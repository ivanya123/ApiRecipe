import asyncio

from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload, joinedload

from shemas import ProdPy, RecipePy, PrInProdPy
from sql_model.models import Base, Recipe, ProductsRecipe, Products, engine, as_session, TypeProduct


async def create_table():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_table():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def add_product(prod_py: ProdPy):
    async with as_session() as session:
        prod_dict = prod_py.model_dump()
        product = Products(**prod_dict)
        session.add(product)
        await session.flush()
        await session.commit()
        return product


async def add_new_recipe(recipe: RecipePy, products_tuple: PrInProdPy) -> Recipe:
    async with as_session() as session:
        recipe_dict = recipe.model_dump()
        recipe = Recipe(**recipe_dict)

        products_dict = products_tuple.model_dump()
        prod_id = [prod_id for prod_id, _ in products_dict["products"]]

        result = await session.execute(select(Products).where(Products.id.in_(prod_id)))
        products = result.scalars().all()

        list_prod_quantity = []
        for product in products:
            for index, quantity in products_dict["products"]:
                if product.id == index:
                    list_prod_quantity.append((product, quantity))
        prod_recipe = [ProductsRecipe(recipe=recipe, product=product, quantity=quantity) for product, quantity in
                       list_prod_quantity]
        session.add_all(
            prod_recipe
        )
        await session.flush()
        await session.commit()
        return recipe


async def add():
    async with as_session() as session:
        async with session.begin():
            recipe1 = Recipe(title="Salad", description="Vkussnii salad")
            recipe2 = Recipe(title="Sup", description="Vkusnii sup")

            prod1 = Products(name="Pomidor", types="weight", calories_per_100=133)
            prod2 = Products(name="Ogurecc", types="piece", calories_per_100=231)
            prod3 = Products(name="Water", types="liquid", calories_per_100=32)
            prod4 = Products(name="Solen Ogurci", types="weight", calories_per_100=13)
            prod5 = Products(name="Kolbasa", types="weight", calories_per_100=21)
            prod6 = Products(name="smetana", types="liquid", calories_per_100=321)
            prod7 = Products(name="slivki", types="liquid", calories_per_100=41)

            session.add_all([
                ProductsRecipe(recipe=recipe1, product=prod1, quantity=50),
                ProductsRecipe(recipe=recipe1, product=prod2, quantity=200),
                ProductsRecipe(recipe=recipe1, product=prod3, quantity=40),
                ProductsRecipe(recipe=recipe1, product=prod4, quantity=60),
                ProductsRecipe(recipe=recipe2, product=prod1, quantity=20),
                ProductsRecipe(recipe=recipe2, product=prod2, quantity=142),
                ProductsRecipe(recipe=recipe2, product=prod3, quantity=23),
                ProductsRecipe(recipe=recipe2, product=prod4, quantity=3123),
                ProductsRecipe(recipe=recipe2, product=prod5, quantity=42),
                ProductsRecipe(recipe=recipe2, product=prod6, quantity=312),
                ProductsRecipe(recipe=recipe2, product=prod7, quantity=132),
            ])


async def add_2():
    async with as_session() as session:
        async with session.begin():
            prod = Products(name="Pomidor", types="weight")
            session.add(prod)
            await session.commit()


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
        return recipes

async def get_recipe_with_products(recipe_id: int):
    async with as_session() as session:
        result = await session.execute(
            select(Recipe).options(selectinload(Recipe.products)).where(Recipe.id == recipe_id)
        )
        recipe = result.scalars().first()

        if recipe:
            print(f"Recipe: {recipe.title}, Description: {recipe.description}")
            for product_recipe in recipe.products:
                product_result = await session.execute(
                    select(Products).where(Products.id == product_recipe.product_id)
                )
                product = product_result.scalars().first()
                print(
                    f"Product: {product.name}, Type: {product.types}, Quantity: {product_recipe.quantity}")
        else:
            print("Recipe not found")
    print(recipe)
    return recipe


async def main():
    await drop_table()
    await create_table()
    products = await get_all_products()
    for prod in products:
        print(prod.name)


if __name__ == '__main__':
    asyncio.run(main())
