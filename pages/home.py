import flet as ft
from controler import *

class HomePage(ft.Container):
    def __init__(self, page,items_menu,hora,clientes,day):
        super().__init__()
        self.page = page
        self.expand = True
        self.items_menu=items_menu
        self.categoria_lista = getCategorias()
        self.hora=hora
        self.clientes=clientes
        self.day=day
        self.search_categoria=ft.Dropdown(
        label="Categoria",
        width=230,
        options=[ft.dropdown.Option(categoria.nome) for categoria in self.categoria_lista],
        
    )
        self.content = self.build()

    def build(self):
        
        return ft.Container(
            content=ft.Container(
                bgcolor="#F0F8FF",  # Light blue-white background
                content=ft.Column([
                    ft.Row(
                        controls=[
                            ft.Container(
                                expand=True,
                                height=800,
                                padding=14,
                                content=ft.Column(controls=[
                                    ft.Container(
                                        padding=10,
                                        border_radius=10,
                                        bgcolor="white",
                                        content=ft.Row(
                                            controls=[
                                                ft.Text(info['app'],size=30,weight="bold",color=ft.Colors.INDIGO_400),
                                                self.search_categoria,
                                                self.search
                                            ],
                                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                        )
                                    ),
                                    self.items_menu
                                ])
                            ),
                            ft.Container(
                                width=260,
                                padding=10,
                                bgcolor=ft.Colors.WHITE,
                                content=ft.Column(controls=[
                                    ft.Text("Resumo da Veda:",size=20,weight="bold",color=ft.Colors.INDIGO_400),
                                    ft.Container(
                                        padding=10,
                                        margin=10,
                                        content=ft.Column(controls=[
                                            ft.Row(controls=[
                                                ft.Text("Data:",size=15),
                                                ft.Text(day,size=15)
                                            ]),
                                            self.horas,
                                            ft.Row(controls=[
                                                ft.Text("Caixa:",size=15),
                                                ft.Text(userLoged().nome,size=15)
                                            ])
                                        ])
                                    ),
                                    ft.Card(
                                        content=ft.Container(
                                            padding=10,
                                            content=ft.Column([
                                                self.clientes,
                                                self.mesa,
                                                ft.ElevatedButton("Abrir Gaveta",on_click=lambda e:abrir_gaveta())
                                            ])
                                        )
                                    ),
                                    ft.Stack(
                                        width=260,
                                        height=650,
                                        controls=[
                                            self.lista_vendas,
                                            ft.Card(
                                                width=235,
                                                bottom=300,
                                                content=ft.Container(
                                                    padding=10,
                                                    content=ft.Column(controls=[self.total_text])
                                                )
                                            )
                                        ]
                                    )
                                ])
                            )
                        ]
                    )
                ])
            )
        )
# Função de compatibilidade para o código existente
def homePage(pagex):
    return HomePage(pagex)