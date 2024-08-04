from typing import Any

import flet as ft
import requests
from flet_core import MainAxisAlignment


def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT

    data = requests.get("http://127.0.0.1:8000/list_recipes/all_recipe")
    info = data.json()

    data_products = requests.get("http://127.0.0.1:8000/list_recipes/all_product")
    info_products = data_products.json()

    # Создание вкладки "Все рецепты"

    def add_clicked(e, description: str):
        """
        Функция для кнопки которая выводит описание рецепта.
        :param e:
        :param description:
        :return:
        """
        new_list = container_list.copy()
        new_list.append(ft.Text(f"{description}"))
        recipe_tab.content = ft.Column(new_list)
        page.update()

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

    recipe_tab = ft.Tab(text="Рецепты", content=ft.Column(container_list))



    # Создание вкладки добавление рецептов с функционалом
    # Функция доабвления продукта в базу данных через post запрос,
    # и обновление списка продуктов

    # Функция добавления продукта в рецепт.
    def add_product(e):
        print("Ничего не придумал")
    def add_new_product(e):
        """
        Функция доабвления продукта в базу данных через post запрос,
        и обновление списка продуктов
        :param e: необазательный парраметр event, не используется в данное функции
        :return: None
        """
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

        requests.post("http://127.0.0.1:8000/list_recipes/add_product", json=data)
        update_container_product()

    # Функция создания контейнера с описанием
    # продукта и кнопки, которая добаляет продукт в рецепт.
    def products_text(product: dict[str, Any]) -> ft.Container:
        """
        Функция создания контейнера с описанием
        продукта и кнопки, которая добаляет продукт в рецепт.
        :param product: dict[str, Any] - словарь с описанием продукта.
        Пример product:
        product = {
                    "name": "Соленые огурцы",
                    "id": 1,
                    "calories_per_100": 100,
                    "types": "liquid"
                  }
        :return:
        """
        if product["types"] == "liquid":
            unit_of_measure = "мл."
        elif product["types"] == "weight":
            unit_of_measure = "г."
        else:
            unit_of_measure = "шт."

        text_name = ft.Text(f"{product['id']}: {product['name']}({unit_of_measure})\n"
                            f"Калории на 100 {unit_of_measure}: {product['calories_per_100']}",
                            overflow=ft.TextOverflow.ELLIPSIS,
                            width=250)

        button = ft.FilledButton("Добавить в рецепт", icon="add", on_click=lambda e: add_product(e),
                                 width=150)
        container = ft.Container(content=ft.Row([text_name, button],
                                                alignment=ft.MainAxisAlignment.START), padding=7, margin=5,
                                 ink=True, ink_color=ft.colors.RED_400, bgcolor=ft.colors.BLUE_200,
                                 border_radius=10)
        container.info_product = product
        return container

    # Функция для обновления контейнера с продуктами.
    def update_container_product() -> None:
        products_info = requests.get("http://127.0.0.1:8000/list_recipes/all_product").json()
        list_container_product = [
            products_text(product) for product in products_info
        ]
        list_container_product.append(container_add_product)
        container_product.content = ft.ListView(controls=list_container_product, auto_scroll=True,
                                                height=550, width=700)
        page.update()


    # Изначальное создание контейнера с продуктами при запуске приложения
    # Создания поля для ввода названия приложения
    product_add_name_field = ft.TextField(label="Название продукта", hint_text="Введите название продукта",
                                          multiline=False, width=190)
    # Создание поля для выбора типа продукта.
    product_type_dropdown = ft.Dropdown(label="Тип", options=[ft.dropdown.Option("liquid", "Жидкость"),
                                                              ft.dropdown.Option("weight", "Весовой товар"),
                                                              ft.dropdown.Option("piece", "Штучный")],
                                        hint_text="Тип",
                                        width=150)
    # Создание поля для ввода калорий на 100 грамм.
    product_calories_per_100_field = ft.TextField(label="Калории",
                                                  hint_text="Калории",
                                                  width=80)
    # Создание кнопки для добавления продукта в базу данных.
    button_add_product = ft.FilledButton("Добавить", icon="add", on_click=lambda e: add_new_product(e))
    # Объединения полей ввода и кнопки в один ряд
    row_add_product = ft.Row(
        controls=[product_add_name_field, product_type_dropdown, product_calories_per_100_field, button_add_product],
        wrap=True)
    # Создание контейнера с описанием продукта.
    container_add_product = ft.Container(content=row_add_product)

    # Создание списка контейнеров с описанием продуктов и кнопки для добавления продукта в рецепт.
    list_container_product = [
        products_text(product) for product in info_products
    ]
    # Добавление в конец списка ряда с полями для добавления нового продукта в базу данных.
    list_container_product.append(container_add_product)
    # Создание прокручиваемого списка продуктов.
    list_view = ft.ListView(auto_scroll=True,
                            height=550, width=500)
    # Добавление в список контенеры с продуктами и ряд с полями для добавления нового продукта в базу данных.
    list_view.controls.extend(list_container_product)
    # Запаковывем все в контейнер для дальнейшего использвания
    container_product = ft.Container(content=list_view, width=450)




    recipe_tittle_field = ft.TextField(label="Название рецепта", hint_text="Введите название рецепта",
                                       multiline=False, width=600)
    recipe_description_field = ft.TextField(
        label="Описание рецепта",
        hint_text="Введите описание рецепта",
        multiline=True,
        min_lines=1, max_lines=10, width=600,
        height=500
    )
    column_field_recipe = ft.Container(content=ft.Column([recipe_tittle_field, recipe_description_field]),
                                       padding=10,
                                       width=600,
                                       alignment=ft.alignment.top_left)





    row_field_recipe_and_product = ft.Row(spacing=10, controls=[column_field_recipe, container_product], wrap=True,
                                          alignment=MainAxisAlignment.START)

    recipe_post_tab = ft.Tab(text="Добавить рецпты", content=row_field_recipe_and_product)

    t = ft.Tabs(
        tabs=[recipe_tab, recipe_post_tab]
    )
    page.add(t)


if __name__ == '__main__':
    ft.app(target=main)
