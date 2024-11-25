import asyncio

from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload, joinedload

from shemas import ProdPy, RecipePy, PrInProdPy, UpdateFridgePy
from sql_model.models import Base, Recipe, ProductsRecipe, Products, engine, as_session, ChangeRecipe, Category, \
    ProductsCategories, Fridge


async def get_by_id(model, id, session):
    result = await session.execute(select(model).where(model.id == id))
    return result.scalars().first()


async def create_table():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_table():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def add_category(name: str) -> Category:
    async with as_session() as session:
        new_category = Category(name=name)
        session.add(new_category)
        await session.commit()
        return new_category


async def delete_category(id: int) -> None:
    async with as_session() as session:
        category = await session.execute(select(Category).where(Category.id == id))
        if not category:
            raise ValueError(f'Отсутствует категория {id}')
        category = category.scalars().first()
        session.delete(category)
        await session.commit()


async def update_category(id: int, name: str) -> Category:
    async with as_session() as session:
        category = await get_by_id(Category, id, session)
        category = category.scalars().first()
        category.name = name
        await session.commit()
        return category


async def add_product(prod_py: ProdPy):
    async with as_session() as session:
        prod_dict = prod_py.model_dump()
        categories = prod_dict.pop('categories')
        categories = await session.execute(select(Category).where(Category.id.in_(categories)))

        categories = categories.scalars().all()
        product = Products(**prod_dict)
        session.add(product)
        await session.flush()
        products_categories = [ProductsCategories(product_id=product.id, category_id=category.id) for category in
                               categories]
        session.add_all(products_categories)
        await session.commit()
        return product


async def add_new_recipe(recipe: RecipePy, products_tuple: PrInProdPy) -> Recipe:
    async with as_session() as session:
        recipe_dict = recipe.model_dump()
        recipe = Recipe(**recipe_dict)

        products_dict = products_tuple.model_dump()
        prod_id = [prod_id['product_id'] for prod_id in products_dict["products"]]

        result = await session.execute(select(Products).where(Products.id.in_(prod_id)))
        products = result.scalars().all()

        list_prod_quantity = []
        for product in products:
            for prinprod in products_dict["products"]:
                if product.id == prinprod['product_id']:
                    list_prod_quantity.append((product, prinprod['quantity']))
        prod_recipe = [ProductsRecipe(recipe=recipe, product=product, quantity=quantity) for product, quantity in
                       list_prod_quantity]
        session.add(recipe)
        session.add_all(
            prod_recipe
        )
        await session.flush()
        await session.commit()
        return recipe


async def get_all_products():
    async with as_session() as session:
        result = await session.execute(select(Products).options(
            joinedload(Products.categories)
        ))
        products = result.scalars().unique().all()
        return products


async def get_all_product_category(id: int) -> list[Products]:
    async with as_session() as session:
        result = await session.execute(
            select(Products)
            .join(ProductsCategories)
            .where(ProductsCategories.category_id == id)
            .options(selectinload(Products.categories))
        )
        if not result:
            raise ValueError(f'Отсутствует продукты в категории {id} или сама категория.')
        products: list[Products] = result.scalars().all()
        return products


async def get_all_recipe():
    async with as_session() as session:
        result = await session.execute(
            select(Recipe).options(joinedload(Recipe.products).joinedload(ProductsRecipe.product))
        )
        recipes = result.scalars().unique().all()
        print(recipes)
        return recipes


async def delete_product(id: int):
    async with as_session() as session:
        result = await session.execute(
            select(Products)
            .options(selectinload(Products.recipe).selectinload(ProductsRecipe.recipe))
            .where(Products.id == id)
        )
        if not result:
            raise ValueError(f'Отсутствует продукт {id}')

        res_wait_change_recipe: list[ChangeRecipe] = await session.execute(
            select(ChangeRecipe)
        )
        print(type(res_wait_change_recipe))
        product = result.scalars().first()
        wait_change_recipe_id = [rec.recipe_id for rec in res_wait_change_recipe.scalars().all()]

        list_recipes = [pr.recipe for pr in product.recipe]
        await session.delete(product)

        list_recipe_db = [ChangeRecipe(recipe_id=recipe.id) for recipe in list_recipes if
                          recipe.id not in wait_change_recipe_id]

        session.add_all(list_recipe_db)
        await session.commit()
        return list_recipes


async def get_change_recipe():
    async with as_session() as session:
        result = await session.execute(select(ChangeRecipe).options(joinedload(ChangeRecipe.recipe)))
        recipes = result.scalars().all()
        return recipes


async def delete_wait_change_recipe(id: int):
    async with as_session() as session:
        recipe = await get_by_id(ChangeRecipe, id, session)
        await session.delete(recipe)
        await session.commit()


async def delete_recipe(id: int):
    async with as_session() as session:
        recipe = await get_by_id(Recipe, id, session)
        await session.delete(recipe)
        await session.commit()


async def update_product(id: int, prod_py: ProdPy):
    async with as_session() as session:
        # Получение продукта
        result = await session.execute(
            select(Products).options(joinedload(Products.categories)).where(Products.id == id)
        )
        product = result.scalars().first()
        if not product:
            raise ValueError(f"Продукт с id {id} не найден.")

        # Удаление текущих категорий
        await session.execute(
            delete(ProductsCategories).where(ProductsCategories.product_id == id)
        )

        # Обновление данных продукта
        dict_product = prod_py.model_dump()
        new_categories = dict_product.pop("categories")
        await session.execute(
            update(Products).where(Products.id == id).values(**dict_product)
        )

        # Добавление новых категорий
        if new_categories:
            new_categories_data = [
                ProductsCategories(product_id=id, category_id=category_id)
                for category_id in new_categories
            ]
            session.add_all(new_categories_data)

        # Сохранение изменений
        await session.commit()
        return product



async def update_recipe(id, recipe_py: RecipePy, list_products: PrInProdPy):
    async with as_session() as session:
        result = await session.execute(
            select(Recipe).options(
                joinedload(Recipe.products).joinedload(ProductsRecipe.product)
            ).where(Recipe.id == id)
        )
        recipe = result.scalars().first()
        recipe_dict = recipe_py.model_dump()
        for key, value in recipe_dict.items():
            setattr(recipe, key, value)

        old_products = {pr.product_id: pr for pr in recipe.products}

        for product_dict in list_products['products']:
            if product_dict['product_id'] in old_products:
                old_products[product_dict['product_id']].quantity = product_dict['quantity']
                del old_products[product_dict['product_id']]
            else:
                new_product = ProductsRecipe(recipe_id=id, product_id=product_dict['product_id'],
                                             quantity=product_dict['quantity'])
                session.add(new_product)

        for prod_id in old_products:
            await session.delete(old_products[prod_id])

        res_change = await session.execute(select(ChangeRecipe).where(ChangeRecipe.recipe_id == id))
        change_recipe = res_change.scalars().first()
        await session.delete(change_recipe)

        await session.commit()


async def update_fridge(list_products: UpdateFridgePy) -> None:
    change_id = [fridge_product.id for fridge_product in list_products.products if fridge_product.id]
    async with as_session() as session:
        change_product = await session.execute(select(Fridge).where(Fridge.id.in_(change_id)))
        change_product = change_product.scalars().all()

        for product in change_product:
            for update_product in list_products.products:
                if update_product.id == product.id:
                    dict_product = update_product.model_dump()
                    for key, value in dict_product.items():
                        setattr(product, key, value)

        new_products: list[dict] = [fridge_product.model_dump() for fridge_product in list_products.products if
                                    not fridge_product.id]
        for product in new_products:
            del product['id']

        list_new_products = [Fridge(**product) for product in new_products]
        session.add_all(list_new_products)

        await session.flush()
        await session.commit()


async def get_fridge():
    async with as_session() as session:
        result = await session.execute(select(Fridge).options(joinedload(Fridge.product)))
        result = result.scalars().all()
        return result


async def main():
    await drop_table()
    await create_table()
    product = {
        "name": "test",
        "types": "liquid",
        "calories_per_100g": 100
    }
    products = await add_product(ProdPy(**product))
    # products = await get_all_products()
    # for prod in products:
    #     print(prod.name)


if __name__ == '__main__':
    recipe = {
        "title": "test",
        "description": "testing"
    }
    products = {
        "products": [[1, 1.2], [2, 2.3]]
    }
    products = {
        "name": "test",
        "types": "liquid",
        "calories_per_100g": 100
    }

    asyncio.run(main())
    asyncio.run(get_all_recipe())
    # asyncio.run(update_recipe(1, recipe, products))
