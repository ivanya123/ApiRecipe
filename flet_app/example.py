import flet as ft

def main(page: ft.Page):
    page.title = "MyApp"

    def event(e):
        if e.data == "close":
            page.dialog = confirm_dialog
            confirm_dialog.open = True
            page.update()

    page.window.prevent_close = True
    page.window.on_event = event

    def yes_click(e):
        page.window.destroy()

    def no_click(e):
        confirm_dialog.open = False
        page.update()

    confirm_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Please confirm"),
        content=ft.Text("Do you really want to exit this app?"),
        actions=[
            ft.ElevatedButton("Yes", on_click=yes_click),
            ft.OutlinedButton("No", on_click=no_click),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.add(ft.Text('Try exiting this app by clicking window\'s "Close" button!'))

ft.app(main)