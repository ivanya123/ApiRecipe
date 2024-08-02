from typing import Annotated

from fastapi import APIRouter, Depends

from shemas import ProdPy, RecipePy, PrInProdPy
from sql_model.orm import get_all_products, add_product, add_new_recipe, get_all_recipe

router = APIRouter(
    prefix="/list_recipes",
    tags=["АПИ РЕЦЕПТОВ"]
)

@router.get('/all_product')
async def root():
    result = await get_all_products()
    return result


@router.post("/add_product")
async def add_product_(product: ProdPy):
    my_product = await add_product(product)
    return my_product


@router.post("/add_recipe")
async def add_r(recipe: Annotated[RecipePy, Depends()], prod: Annotated[PrInProdPy, Depends()]):
    recipe = await add_new_recipe(recipe, prod)
    return recipe.id

@router.get('/all_recipe')
async def get_recipe():
    my_recipes = await get_all_recipe()
    return my_recipes


