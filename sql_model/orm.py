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
        print(prod_dict)
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


async def main():
    await drop_table()
    await create_table()
    products = await get_all_products()
    for prod in products:
        print(prod.name)


if __name__ == '__main__':
    asyncio.run(main())
