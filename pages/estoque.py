import flet as ft
from controler import *

page=None #we need update this var to page off our app
imagens=os.path.join(os.getenv("LOCALAPPDATA"), ".jpInvest/img") # path off imagens
update_menu=None
update_produtos=None
banco=isDataBase()
current_date = datetime.now()
day = current_date.strftime("%d-%m-%Y")


def Entradas(e):
    entradas=getEntradas(getRelatorioUnico(day).id)
    content=ft.Column(height=500)
    for nome, quantidade in entradas.items():
        content.controls.append(ft.Text(f"{nome}---{quantidade}"))

    entrada_dialog=ft.AlertDialog(title=ft.Text('Entradas'),content=content)
    entrada_dialog.actions=[ft.ElevatedButton("fechar",on_click=lambda e: page.close(entrada_dialog))]
    page.open(entrada_dialog)

def Saidas(e):
    saidas=getSaidas(getRelatorioUnico(day).id)
    content=ft.Column(height=500)
    saida_dialog=ft.AlertDialog(title=ft.Text('Saidas'),content=content,actions=[
        ft.ElevatedButton("fechar",bgcolor=ft.Colors.RED_400)])
    saida_dialog.actions=[ft.ElevatedButton("fechar",on_click=lambda e: page.close(saida_dialog))]


    for nome, quantidade in saidas.items():
        content.controls.append(ft.Text(f"{nome}---{quantidade}"))
        

    page.open(saida_dialog)
def estoquePage(pagex):
    global page
    page=pagex
    historico=ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Nome")),
            ft.DataColumn(ft.Text("Estoque Inicial"),numeric=True),
            ft.DataColumn(ft.Text("Entradas"), numeric=True),
            ft.DataColumn(ft.Text("saidas"), numeric=True),
            ft.DataColumn(ft.Text("Estoque Atual"), numeric=True),
        ],height=800)
    try:
        for estoque in getHistoricoEstoque(getRelatorioUnico(day).id):
            historico.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(estoque['nome'])),
                    ft.DataCell(ft.Text(estoque['estoque_inicial'])),
                    ft.DataCell(ft.Text(estoque['entrada'])),
                    ft.DataCell(ft.Text(estoque['saida'])),
                    ft.DataCell(ft.Text(estoque['estoque_atual']))
                    ])
        )
    except:
        pass
    return ft.Container(padding=10,content=ft.Column([
            ft.Row([
                ft.CupertinoButton("Ver Entradas",bgcolor=ft.Colors.ORANGE_600,on_click=Entradas),
                ft.CupertinoButton("Ver Saidas",bgcolor=ft.Colors.ORANGE_600,on_click=Saidas),
            ]),ft.Card(content=historico)
        ]))
    