from typing import Annotated

from fastapi import APIRouter, Depends

from shemas import ProdPy, RecipePy, PrInProdPy
from sql_model.models import Recipe
from sql_model.orm import get_all_products, add_product, add_new_recipe, get_all_recipe, delete_recipe, \
    update_recipe, delete_product, update_product, get_change_recipe, delete_wait_change_recipe

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
async def add_r(recipe: RecipePy, prod: PrInProdPy):
    recipe = await add_new_recipe(recipe, prod)
    return recipe.id

@router.get('/all_recipe')
async def get_recipe():
    my_recipes = await get_all_recipe()
    return my_recipes


@router.get("/delete_product/{id}")
async def delete_product_(id: int):
    list_recipes: list[Recipe] = await delete_product(id)
    return list_recipes


@router.get("/delete_recipe/{id}")
async def delete_recipe_(id: int):
    await delete_recipe(id)
    return {"message": "Успешно удалено"}


@router.get("/get_change_recipe")
async def wait_change_recipe():
    result = await get_change_recipe()
    return result


@router.get("/delete_change_recipe/{id}")
async def delete_change_recipe(id: int):
    await delete_wait_change_recipe(id)
    return {"message": "Успешно удалено"}



