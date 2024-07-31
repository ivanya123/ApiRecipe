from typing import Optional

from pydantic import BaseModel

from sql_model.models import TypeProduct


class ProdPy(BaseModel):
    name: str
    types: TypeProduct
    calories_per_100: Optional[float] = None


class RecipePy(BaseModel):
    title: str
    description: Optional[str] = None


class PrInProdPy(BaseModel):
    products: list[tuple[int, float]] = [(1,23)]