import flet as ft
from controler import *

class MoneyPage(ft.Container):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.expand = True
        self.bgcolor = "#F0F8FF"  # Light blue-white background

    def build(self):
        return ft.Container(
            bgcolor="#F0F8FF",  # Light blue-white background
            content=ft.Column([
                ft.Container(
                    padding=10,
                    border_radius=10,
                    bgcolor="white",
                    content=ft.Row([
                        ft.Text("Finanças", size=30, weight="bold", color=ft.Colors.INDIGO_400),
                        ft.ElevatedButton(
                            "Exportar Relatório",
                            icon=ft.icons.DOWNLOAD,
                            bgcolor=ft.Colors.INDIGO_400,
                            color="white",
                        
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ),
                ft.Container(
                    padding=20,
                    content=ft.Column([
                        ft.Row([
                            ft.Container(
                                padding=20,
                                bgcolor="white",
                                border_radius=10,
                                content=ft.Column([
                                    ft.Text("Vendas Hoje", size=20, color=ft.Colors.INDIGO_400),
                                    ft.Text("10,000 MT", size=30, weight="bold")
                                ])
                            ),
                            ft.Container(
                                padding=20,
                                bgcolor="white",
                                border_radius=10,
                                content=ft.Column([
                                    ft.Text("Vendas Mês", size=20, color=ft.Colors.INDIGO_400),
                                    ft.Text("150,000 MT", size=30, weight="bold")
                                ])
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Container(
                            padding=20,
                            content=ft.DataTable(
                                columns=[
                                    ft.DataColumn(ft.Text("Data")),
                                    ft.DataColumn(ft.Text("Descrição")),
                                    ft.DataColumn(ft.Text("Valor")),
                                    ft.DataColumn(ft.Text("Status")),
                                ],
                                rows=[
                                    ft.DataRow(
                                        cells=[
                                            ft.DataCell(ft.Text("2024-01-20")),
                                            ft.DataCell(ft.Text("Venda #1234")),
                                            ft.DataCell(ft.Text("1,000 MT")),
                                            ft.DataCell(ft.Text("Concluído", color=ft.Colors.INDIGO_400))
                                        ]
                                    )
                                ]
                            )
                        )
                    ])
                )
            ])
        )

# Função de compatibilidade para o código existente
def moneyPage(pagex):
    return MoneyPage(pagex)