import asyncio

from sql_model.orm import create_table, drop_table, get_all_recipe, update_recipe, add_category, add_product
from shemas import RecipePy, PrInProdPy, ProdPy

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
    asyncio.run(add_category(category_1))
    asyncio.run(add_category(category_2))
    asyncio.run(add_product(ProdPy(**product)))



