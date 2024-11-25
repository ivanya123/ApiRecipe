from typing import Optional, List

from pydantic import BaseModel

from sql_model.models import TypeProduct, Category, Products, Recipe, Fridge


class CategoryPy(BaseModel):
    name: str

    def to_orm(self):
        return Category(name=self.name)


# Модель для продукта
class ProdPy(BaseModel):
    name: str
    types: TypeProduct
    calories_per_100: Optional[float] = None
    shelf_life_close: Optional[int] = None
    shelf_life_open: Optional[int] = None
    categories: List[int] = []

    def to_orm(self):
        return Products(
            name=self.name,
            types=self.types,
            calories_per_100=self.calories_per,
            shelf_life_close=self.shelf_life_close,
            shelf_life_open=self.shelf_life_open
        )


# Модель для рецепта
class RecipePy(BaseModel):
    title: str
    description: Optional[str] = None

    def to_orm(self):
        return Recipe(
            title=self.title,
            description=self.description
        )


# Модель для указания количества продуктов в рецепте
class ProductQuantity(BaseModel):
    product_id: int
    quantity: float


class PrInProdPy(BaseModel):
    products: List[ProductQuantity] = []


# Модель для данных холодильника
class FridgePy(BaseModel):
    id: Optional[int]
    product_id: int
    quantity: float
    start_open: Optional[str] = None
    shelf_life_close: Optional[str] = None
    shelf_life_open: Optional[str] = None
    close: bool = True

    def to_orm(self):
        return Fridge(
            product_id=self.product_id,
            quantity=self.quantity,
            start_open=self.start_open,
            shelf_life_close=self.shelf_life_close,
            shelf_life_open=self.shelf_life_open,
            close=self.close
        )


class UpdateFridgePy(BaseModel):
    products: List[FridgePy]


if __name__ == '__main__':
    print(type(UpdateFridgePy))
