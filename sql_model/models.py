from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, ForeignKey
import enum

engine = create_async_engine("sqlite+aiosqlite:///./recipes.db", echo=True)
as_session = async_sessionmaker(engine, expire_on_commit=False)


class TypeProduct(enum.Enum):
    liquid = "liquid"
    weight = "weight"
    piece = "piece"


class Base(DeclarativeBase):
    pass


class Recipe(Base):
    __tablename__ = "recipe"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Optional[str]]
    products = relationship("ProductsRecipe", back_populates="recipe")


class Products(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    types: Mapped[TypeProduct] = mapped_column(nullable=False)
    calories_per_100: Mapped[Optional[float]]
    recipe = relationship("ProductsRecipe", back_populates="product")


class ProductsRecipe(Base):
    __tablename__ = "product_recipe"

    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipe.id"), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), primary_key=True)
    quantity: Mapped[float] = mapped_column(nullable=False)

    recipe = relationship("Recipe", back_populates="products")
    product = relationship("Products", back_populates="recipe")
