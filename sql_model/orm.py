import asyncio

from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload

from shemas import ProdPy, RecipePy, PrInProdPy
from sql_model.models import Base, Recipe, ProductsRecipe, Products, engine, as_session, ChangeRecipe, Category, \
    ProductsCategories


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
        category = category.scalars().first()
        session.delete(category)
        await session.commit()


async def update_category(id: int, name: str) -> Category:
    async with as_session() as session:
        category = await session.execute(select(Category).where(Category.id == id))
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
        result = await session.execute(select(Products))
        products = result.scalars().all()
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
        result = await session.execute(select(ChangeRecipe).where(ChangeRecipe.id == id))
        recipe = result.scalars().first()
        await session.delete(recipe)
        await session.commit()


async def delete_recipe(id: int):
    async with as_session() as session:
        result = await session.execute(select(Recipe).where(Recipe.id == id))
        recipe = result.scalars().first()
        await session.delete(recipe)
        await session.commit()


async def update_product(id, prod_py: ProdPy):
    async with as_session() as session:
        result = await session.execute(select(Products).where(Products.id == id))
        product = result.scalars().first()
        prod_dict = prod_py.model_dump()
        product.name = prod_dict["name"]
        product.types = prod_dict["types"]
        product.calories_per_100g = prod_dict["calories_per_100g"]
        await session.flush()
        await session.commit()
        return product


async def update_recipe(id, recipe_py: RecipePy, products_tuple: PrInProdPy):
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

        current_products = {pr.product_id: pr for pr in recipe.products}

        for prod_id, quantity in products_tuple.products:
            if prod_id in current_products:
                current_products[prod_id].quantity = quantity
                del current_products[prod_id]
            else:
                new_product = ProductsRecipe(recipe_id=id, product_id=prod_id, quantity=quantity)
                session.add(new_product)

        for prod_id in current_products:
            await session.delete(current_products[prod_id])

        res_change = await session.execute(select(ChangeRecipe).where(ChangeRecipe.recipe_id == id))
        change_recipe = res_change.scalars().first()
        await session.delete(change_recipe)

        await session.commit()


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
