import asyncio

from sql_model.orm import create_table, drop_table, get_all_recipe, update_recipe
from shemas import RecipePy, PrInProdPy, ProdPy

if __name__ == '__main__':
    # asyncio.run(drop_table())
    # asyncio.run(create_table())
    asyncio.run(get_all_recipe())
    # recipe = {
    #     "title": "test",
    #     "description": "testing"
    # }
    # products = {
    #     "products": [[1, 1.2], [2, 2.3]]
    # }
    # product = {
    #     "name": "test",
    #     "types": "liquid",
    #     "calories_per_100g": 100
    # }
    #
    # asyncio.run(update_recipe(1, RecipePy(**recipe), PrInProdPy(**products)))

