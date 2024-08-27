from typing import Any

import flet as ft
import requests
from flet_core import MainAxisAlignment


def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT

    data = requests.get("http://127.0.0.1:8000/list_recipes/all_recipe")
    info_recipe = data.json()

    data_products = requests.get("http://127.0.0.1:8000/list_recipes/all_product")
    info_products = data_products.json()

    data_wait_change = requests.get("http://127.0.0.1:8000/list_recipes/get_change_recipe")
    info_wait_change = data_wait_change.json()

    def delete_wait_change(e):
        pass

    # Создание вкладки "Все рецепты"


    container_change_wait = [
        ft.Container(
            content=ft.Text(f"{change_recipe['id']}: {change_recipe['recipe']["title"]}",
                            size=10,
                            color=ft.colors.RED_400),
            margin=5,
            padding=1,
            alignment=ft.alignment.top_left,
            height=15,
            border_radius=5,
            ink=True,
            on_long_press=lambda e: delete_wait_change(e))
        for change_recipe in info_wait_change
    ]

    row_change_wait = ft.Row(controls=container_change_wait)

    def recipe_expansion_tile(recipe_dict: dict[str, Any]) -> ft.ExpansionTile:
        title = recipe_dict["title"]
        description = recipe_dict["description"]

        text_title = ft.TextField(f"{title}", disabled=True, expand=1, color=ft.colors.BLACK)
        text_description = ft.TextField(f"{description}", disabled=True, expand=2, multiline=True,
                                        label="Рецепт", color=ft.colors.BLACK, )

        def product_listtile(product, count: int) -> ft.ListTile:
            def delete_pr(e):
                pass

            if product["product"]["types"] == "liquid":
                unit_of_measurement = "мл"
            elif product["product"]["types"] == "weight":
                unit_of_measurement = "г"
            else:
                unit_of_measurement = "шт"

            name = product["product"]["name"]
            quantity = product["quantity"]

            listtile = ft.ListTile(
                title=ft.Text(f"{count}: {name}-{quantity} {unit_of_measurement}", color=ft.colors.BLACK),
                trailing=ft.IconButton(ft.icons.DELETE, disabled=True, on_click=delete_pr),
                data=product,
                disabled=True,
                bgcolor=ft.colors.BLUE_200,
                content_padding=1
            )
            return listtile

        list_prod_listtile = [product_listtile(product, count+1) for count, product in enumerate(recipe_dict["products"])]
        column_prod_listtile = ft.Column(controls=list_prod_listtile, spacing=5, expand=1)

        expansion_tile = ft.ExpansionTile(
            title=text_title,
            expanded_alignment=ft.alignment.center,
            controls=[
                column_prod_listtile,
                ft.Divider(height=5, color=ft.colors.BLACK),
                text_description
            ]
        )
        return expansion_tile

    list_expansion_tile = [recipe_expansion_tile(recipe) for recipe in info_recipe]
    list_expansion_tile.insert(0, row_change_wait)

    final_column = ft.Column(controls=list_expansion_tile, scroll=ft.ScrollMode.ALWAYS)

    recipe_tab = ft.Tab(text="Рецепты", content=final_column)

    def update_recipe_tab():
        info_recipe = requests.get("http://127.0.0.1:8000/list_recipes/all_recipe").json()
        list_expansion_tile = [recipe_expansion_tile(recipe) for recipe in info_recipe]
        list_expansion_tile.insert(0, row_change_wait)
        final_column.controls = list_expansion_tile
        page.update()
    ####################################################################################################################

    # Создание вкладки добавление рецептов с функционалом
    # Функция доабвления продукта в базу данных через post запрос,
    # и обновление списка продуктов

    # Функция добавления продукта в рецепт.
    def add_product(e, product: dict[str, Any]) -> None:
        if product["types"] == "liquid":
            unit_of_measure = "мл."
        elif product["types"] == "weight":
            unit_of_measure = "г."
        else:
            unit_of_measure = "шт."
        name = product["name"]
        id = product["id"]

        text_describe = ft.Text(f"{name}", width=300)
        field_quantity = ft.TextField(label="Количество", hint_text=f"Введи количество в {unit_of_measure}", width=230)
        text_types = ft.Text(f"{unit_of_measure}")

        list_view_products_recipe.list_products_id.append(id)  # добавляем номер список продуктов

        row = ft.Row([text_describe, field_quantity, text_types])

        def delete_product_recipe(e, id):
            list_view_products_recipe.list_products_id.remove(id)
            text_id.value = f"Ингредиенты в рецепте {list_view_products_recipe.list_products_id}"
            list_view_products_recipe.controls.remove(e.control)
            page.update()

        container = ft.Container(content=row, width=600, padding=5, margin=5,
                                 on_tap_down=lambda e, index=id: delete_product_recipe(e, index), ink=True)
        container.info_for_post = (id, field_quantity)
        list_view_products_recipe.controls.append(container)
        text_id.value = f"Ингредиенты в рецепте {list_view_products_recipe.list_products_id}"
        page.update()

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

        button = ft.FilledButton("Добавить в рецепт", icon="add", on_click=lambda e, prod=product: add_product(e, prod),
                                 width=150)

        def delete_product(e, index: int):
            """Удаление продукта из базы данных."""
            result = requests.get(f"http://127.0.0.1:8000/list_recipes/delete_product/{index}")
            dlg = ft.AlertDialog(title=ft.Text("Не удачное удаление"))
            if result.status_code == 200:
                update_container_product()
            else:
                page.open(dlg)

        container = ft.Container(content=ft.Row([text_name, button],
                                                alignment=ft.MainAxisAlignment.START), padding=7, margin=5,
                                 ink=True, ink_color=ft.colors.RED_400, bgcolor=ft.colors.BLUE_200,
                                 border_radius=10,
                                 on_long_press=lambda e, index=product["id"]: delete_product(e, index))
        container.info_product = product
        container.info_text = text_name
        return container

    # Функция для обновления контейнера с продуктами.
    def update_container_product() -> None:
        nonlocal info_products
        info_products = requests.get("http://127.0.0.1:8000/list_recipes/all_product").json()
        list_container_product = [
            products_text(product) for product in info_products
        ]
        list_container_product.append(container_add_product)
        list_view.controls.clear()
        list_view.controls.extend(list_container_product)
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
    list_view = ft.ListView(auto_scroll=False,
                            height=850, width=500, expand=1)
    # Добавление в список контенеры с продуктами и ряд с полями для добавления нового продукта в базу данных.
    list_view.controls.extend(list_container_product)

    # Запаковывем все в контейнер для дальнейшего использвания
    # Создание кнопки поиска по продуктам.
    def search_product(e):
        # products_info = requests.get("http://127.0.0.1:8000/list_recipes/all_product").json()
        list_container_product = [
            products_text(product) for product in info_products
        ]
        list_container_product = [container for container in list_container_product if
                                  field_search.value.lower() in container.info_text.value.lower()]
        list_container_product.append(container_add_product)
        list_view.controls.clear()
        list_view.controls.extend(list_container_product)
        # container_product.content = ft.ListView(controls=list_container_product, auto_scroll=True,
        #                                         height=550, width=700)
        page.update()

    field_search = ft.TextField(label="Поиск", hint_text="Введите название продукта", width=150,
                                on_change=search_product)
    button_search = ft.FilledButton("Поиск", icon="search", on_click=lambda e: search_product(e))
    row_search = ft.Row(spacing=5, controls=[field_search, button_search], wrap=True)

    container_product = ft.Container(content=ft.Column([row_search, list_view], expand=1))

    # Создание контейнера с полями для ввода названия, описания рецепта с последующем добавлением в базу данных.

    def add_new_recipe(e):
        """
        Функция для добавления нового рецепта в базу данных.
        :param e:
        :return:
        """
        recipe = {
            "title": recipe_tittle_field.value,
            "description": recipe_description_field.value
        }
        list_tuple_index_quantity = [(control.info_for_post[0], control.info_for_post[1].value) for control in
                                     list_view_products_recipe.controls if not isinstance(control, ft.Text)]



        data = {
            "recipe": recipe,
            "prod": {
                "products": list_tuple_index_quantity
            }
        }

        result = requests.post("http://127.0.0.1:8000/list_recipes/add_recipe", json=data)

        if result.status_code == 200:
            update_recipe_tab()
            recipe_tittle_field.value = ""
            recipe_description_field.value = ""
            list_view_products_recipe.controls.clear()
            page.update()





    # Функция для обновления контейнера с рецептами.

    # Создание кнопки для добавления рецепта в базу данных.
    button_add_recipe = ft.FilledButton("Добавить", icon="add", on_click=lambda e: add_new_recipe(e))

    # Cоздание поля для ввода названия рецепта.
    recipe_tittle_field = ft.TextField(label="Название рецепта", hint_text="Введите название рецепта",
                                       multiline=False, expand=1)

    # Создание поля для ввода описания рецепта.
    recipe_description_field = ft.TextField(
        label="Описание рецепта",
        hint_text="Введите описание рецепта",
        multiline=True,
        min_lines=1, max_lines=10,
        expand=4
    )

    list_view_products_recipe = ft.ListView(height=450, expand=5)
    list_view_products_recipe.list_products_id = []
    text_id = ft.Text(f"Ингредиенты а рецепте {list_view_products_recipe.list_products_id}")
    list_view_products_recipe.controls.append(text_id)

    # Создание контейнера с созданными полями для ввода.
    column_field_recipe = ft.Container(content=ft.Column([button_add_recipe,
                                                          recipe_tittle_field,
                                                          recipe_description_field,
                                                          list_view_products_recipe],
                                                         expand=False,
                                                         alignment=ft.alignment.center),
                                       padding=10,
                                       height=900,
                                       width=700,
                                       expand=2,
                                       alignment=ft.alignment.center
                                       )

    # Создание финалльного ряда а затем и вкладки для добавления рецепта в базу данных.
    row_field_recipe_and_product = ft.Row(spacing=10, controls=[column_field_recipe, container_product],
                                          alignment=MainAxisAlignment.CENTER,
                                          expand=True)

    recipe_post_tab = ft.Tab(text="Добавить рецeпты", content=row_field_recipe_and_product)

    t = ft.Tabs(
        tabs=[recipe_tab, recipe_post_tab], expand=True
    )
    page.add(t)


if __name__ == '__main__':
    ft.app(target=main)
