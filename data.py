import asyncio

from sql_model.orm import create_table, get_all_products, drop_table, get_all_recipe, update_recipe, add_category, \
    add_product, add_new_recipe, get_all_product_category, update_product, update_fridge, get_fridge
from shemas import RecipePy, PrInProdPy, ProdPy, ProductQuantity, UpdateFridgePy, FridgePy


async def main():
    result = await get_fridge()
    print(result[0].quantity)


if __name__ == '__main__':
    asyncio.run(drop_table())
    asyncio.run(create_table())
    category_1 = 'Молочные продукты'
    category_2 = 'Напитки'
    product = {
        'name': 'Молоко',
        'types': 'liquid',
        'calories_per_100': 21.3,
        'shelf_life_close': 14,
        'shelf_life_open': 2,
        'categories': [1, 2]
    }
    recipe = {
        'title': 'Молочный напиток',
        'description': 'Налить молока'
    }
    prod_recipe = {
        'products': [ProductQuantity(product_id=1, quantity=200)]
    }
    product_new = {
        'name': 'Молокосос',
        'types': 'liquid',
        'calories_per_100': 32,
        'shelf_life_close': 23,
        'shelf_life_open': 5,
        'categories': [1]
    }
    new_product_fridge = {
        'id': None,
        'product_id': 1,
        'quantity': 1000,
        'start_open': None,
        'shelf_life_close': None,
        'shelf_life_open': None,
        'close': True
    }
    asyncio.run(add_category(category_1))
    asyncio.run(add_category(category_2))
    asyncio.run(add_product(ProdPy(**product)))
    asyncio.run(add_new_recipe(RecipePy(**recipe), PrInProdPy(**prod_recipe)))
    asyncio.run(update_product(1, ProdPy(**product_new)))
    asyncio.run(update_fridge(UpdateFridgePy(products=[FridgePy(**new_product_fridge)])))
    asyncio.run(main())



