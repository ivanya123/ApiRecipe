import flet as ft


def main(page: ft.Page):
    def handle_change(e: ft.ControlEvent):
        print(f"change on panel with index {e.data}")

    def handle_delete(e: ft.ControlEvent):
        panel.controls.remove(e.control.data)
        page.update()

    panel = ft.ExpansionPanelList(
        expand_icon_color=ft.colors.BLUE_800,
        elevation=8,
        divider_color=ft.colors.RED_800,
        on_change=handle_change,
        controls=[
            ft.ExpansionPanel(
                # has no header and content - placeholders will be used
                bgcolor=ft.colors.BLUE_400,
                expanded=True,
            )
        ]
    )

    colors = [
        ft.colors.GREEN_500,
        ft.colors.BLUE_800,
        ft.colors.RED_800,
    ]

    for i in range(3):
        exp = ft.ExpansionPanel(
            bgcolor=colors[i % len(colors)],
            header=ft.ListTile(title=ft.Text(f"Panel {i}")),
        )

        exp.content = ft.ListTile(
            title=ft.Text(f"This is in Panel {i}"),
            subtitle=ft.Text(f"Press the icon to delete panel {i}"),
            trailing=ft.IconButton(ft.icons.DELETE, on_click=handle_delete, data=exp),
        )

        panel.controls.append(exp)

    page.add(panel)


ft.app(target=main)