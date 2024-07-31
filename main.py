from typing import Optional, Annotated

from fastapi import FastAPI, Depends

from router import router
from shemas import ProdPy
from sql_model.models import TypeProduct
from sql_model.orm import get_recipe_with_products, add_product, get_all_products
from pydantic import BaseModel

app = FastAPI()
app.include_router(router=router)
