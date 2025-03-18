import flet as ft
from controler import *

class TablesPage(ft.Container):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.expand = True
        self.content = self.build()

    def build(self):
        return ft.Container(
            bgcolor="#F0F8FF",
            expand=True,
            content=ft.Column(
                [
                    ft.Container(
                        expand=True,
                        content=ft.Column(
                            controls=[
                                ft.Icon(
                                    ft.Icons.CONSTRUCTION,
                                    size=100,
                                    color=ft.Colors.INDIGO_400
                                ),
                                ft.Text(
                                    "Em Desenvolvimento",
                                    size=32,
                                    weight="bold",
                                    color=ft.Colors.INDIGO_400
                                ),
                                ft.Text(
                                    "O módulo de Mesas estará disponível em breve!",
                                    size=16,
                                    color=ft.Colors.INDIGO_400
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER
                        )
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )

# Função de compatibilidade para o código existente
def tablesPage(pagex):
    return TablesPage(pagex)