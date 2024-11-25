import enum
from datetime import date
from typing import Optional

from sqlalchemy import Integer, ForeignKey
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

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

    products = relationship("ProductsRecipe", back_populates="recipe", cascade="all, delete-orphan")
    changes = relationship("ChangeRecipe", back_populates="recipe", cascade="all, delete-orphan")


class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)

    products = relationship(
        "Products",
        secondary="products_categories",  # Указываем промежуточную таблицу
        back_populates="categories"
    )


class Products(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    types: Mapped[TypeProduct] = mapped_column(nullable=False)
    calories_per_100: Mapped[Optional[float]]
    shelf_life_close: Mapped[Optional[int]]
    shelf_life_open: Mapped[Optional[int]]

    recipe = relationship("ProductsRecipe", back_populates="product", cascade="all, delete-orphan")
    fridge = relationship("Fridge", back_populates="product", cascade="all, delete-orphan")
    categories = relationship(
        "Category",
        secondary="products_categories",  # Указываем промежуточную таблицу
        back_populates="products"
    )


class ProductsCategories(Base):
    __tablename__ = "products_categories"

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id", ondelete="CASCADE"), primary_key=True)


class ProductsRecipe(Base):
    __tablename__ = "product_recipe"

    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipe.id"), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), primary_key=True)
    quantity: Mapped[float] = mapped_column(nullable=False)

    recipe = relationship("Recipe", back_populates="products")
    product = relationship("Products", back_populates="recipe")


class ChangeRecipe(Base):
    __tablename__ = "change_recipe"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipe.id", ondelete="CASCADE"), nullable=False)

    recipe = relationship("Recipe", back_populates="changes")


class Fridge(Base):
    __tablename__ = "fridge"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[float] = mapped_column(nullable=False)
    start_open: Mapped[Optional[date]] = mapped_column(default=None)
    shelf_life_close: Mapped[Optional[date]]
    shelf_life_open: Mapped[Optional[date]]
    close: Mapped[bool] = mapped_column(default=True)

    product = relationship("Products", back_populates="fridge")
