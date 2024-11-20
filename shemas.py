from typing import Optional, List

from pydantic import BaseModel

from sql_model.models import TypeProduct


class CategoryPy(BaseModel):
    name: str


# Модель для продукта
class ProdPy(BaseModel):
    name: str
    types: TypeProduct
    calories_per_100: Optional[float] = None
    shelf_life_close: Optional[int] = None
    shelf_life_open: Optional[int] = None
    categories: List[int] = []


# Модель для рецепта
class RecipePy(BaseModel):
    title: str
    description: Optional[str] = None


# Модель для указания количества продуктов в рецепте
class ProductQuantity(BaseModel):
    product_id: int
    quantity: float


class PrInProdPy(BaseModel):
    products: List[ProductQuantity] = []


# Модель для данных холодильника
class FridgePy(BaseModel):
    product_id: int
    quantity: float
    start_open: Optional[str] = None
    shelf_life_close: Optional[str] = None
    shelf_life_open: Optional[str] = None
    close: bool = True
