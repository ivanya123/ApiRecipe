from typing import Any

import flet as ft
import requests
from flet_core import MainAxisAlignment

from shemas import TypeProduct, RecipePy, ProdPy, PrInProdPy


def main(page: ft.Page):
    data = requests.get("http://127.0.0.1:8000/list_recipes/all_recipe")
    info = data.json()

    data_products = requests.get("http://127.0.0.1:8000/list_recipes/all_product")
    info_products = data_products.json()

    def add_new_product(e):
        global recipe_post_tab
        data = {}
        name = product_add_name_field.value
        types = product_type_dropdown.value
        calories_per_100: str = product_calories_per_100_field.value
        data["name"] = name
        data["types"] = types
        if calories_per_100:
            data["calories_per_100"] = float(calories_per_100)
        else:
            data["calories_per_100"] = None

        result = requests.post("http://127.0.0.1:8000/list_recipes/add_product", json=data)
        recipe_post_tab = update_recipe_post_tab()
        page.update()

    def add_product(e):
        print("Ничего не придумал")

    def products_text(product: dict[str, Any]) -> ft.Container:
        if product["types"] == "liquid":
            unit_of_measure = "мл."
        elif product["types"] == "weight":
            unit_of_measure = "г."
        else:
            unit_of_measure = "шт."

        text_name = ft.Text(f"{product['id']}: {product['name']}({unit_of_measure})\n"
                            f"Калории на 100 {unit_of_measure}: {product['calories_per_100']}")

        button = ft.FilledButton("Добавить в рецепт", icon="add", on_click=lambda e: add_product(e))
        container = ft.Container(content=ft.Row([text_name, button]))
        container.info_product = product
        return container

    product_add_name_field = ft.TextField(label="Название продукта", hint_text="Введите название продукта",
                                          multiline=False, width=150)
    product_type_dropdown = ft.Dropdown(label="Тип", options=[ft.dropdown.Option("liquid"),
                                                              ft.dropdown.Option("weight"),
                                                              ft.dropdown.Option("piece")],
                                        hint_text="Тип",
                                        width=70)
    product_calories_per_100_field = ft.TextField(label="Калории",
                                                  hint_text="Калории",
                                                  width=80)
    button_add_product = ft.FilledButton("Добавить", icon="add", on_click=lambda e: add_new_product(e))
    row_add_product = ft.Row(
        controls=[product_add_name_field, product_type_dropdown, product_calories_per_100_field, button_add_product],
        wrap=True)

    container_add_product = ft.Container(content=row_add_product)

    page.theme_mode = ft.ThemeMode.LIGHT

    def add_clicked(e, description: str):
        new_list = container_list.copy()
        new_list.append(ft.Text(f"{description}"))
        recipe_tab.content = ft.Column(new_list)
        page.update()

    def update_recipe_post_tab():
        new_info_product = requests.get("http://127.0.0.1:8000/list_recipes/all_product").json()
        recipe_tittle_field = ft.TextField(label="Название рецепта", hint_text="Введите название рецепта",
                                           multiline=False
                                           , width=600)
        recipe_description_field = ft.TextField(
            label="Описание рецепта",
            hint_text="Введите описание рецепта",
            multiline=True,
            min_lines=1, max_lines=10, width=600,
        )
        column_field_recipe = ft.Container(content=ft.Column([recipe_tittle_field, recipe_description_field]),
                                           padding=10,
                                           width=600)
        list_container_product = [
            products_text(product) for product in new_info_product
        ]
        list_container_product.append(container_add_product)
        container_product = ft.Container(content=ft.Column(list_container_product), width=500)

        row_field_recipe_and_product = ft.Row(spacing=10, controls=[column_field_recipe, container_product], wrap=True,
                                              alignment=MainAxisAlignment.START)

        recipe_post_tab = ft.Tab(text="Добавить рецпты", content=row_field_recipe_and_product)
        return recipe_post_tab

    container_list = [
        ft.Container(content=ft.Text(f"{recipe['title']}"),
                     margin=5,
                     padding=1,
                     alignment=ft.alignment.top_left,
                     width=100,
                     height=30,
                     border_radius=8,
                     ink=True,
                     on_click=lambda e, k=recipe["description"]: add_clicked(e, k)) for recipe in info
    ]

    recipe_post_tab = update_recipe_post_tab()
    recipe_tab = ft.Tab(text="Рецепты", content=ft.Column(container_list))

    t = ft.Tabs(
        tabs=[recipe_tab, recipe_post_tab]
    )
    page.add(t)


if __name__ == '__main__':
    ft.app(target=main)
