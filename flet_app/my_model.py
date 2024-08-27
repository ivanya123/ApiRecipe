import flet as ft


class TextInfo(ft.Text):
    def __init__(self, value):
        super().__init__(value=value,
                         size=30)


class TextChange(TextInfo):
    def __init__(self, value):
        super().__init__(value=value)
        self.color = ft.colors.RED_400


class Container(ft.Container):
    def __init__(self, content: ft.Control):
        super().__init__(content=content,
                         expand=1,
                         alignment=ft.alignment.center)


class ContainerProduct(Container):
    def __init__(self, content, product):
        super().__init__(content=content)
        self.product = product
