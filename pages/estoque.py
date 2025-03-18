import flet as ft
from controler import *

class EstoquePage(ft.Container):
    def __init__(self, pagex):
        super().__init__()
        self.pagex = pagex
        self.expand = True
        self.imagens = os.path.join(os.getenv("LOCALAPPDATA"), ".jpInvest/img")
        self.banco = isDataBase()
        self.current_date = datetime.now()
        self.day = self.current_date.strftime("%d-%m-%Y")
        
        self.historico = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nome")),
                ft.DataColumn(ft.Text("Estoque Inicial"), numeric=True),
                ft.DataColumn(ft.Text("Entradas"), numeric=True),
                ft.DataColumn(ft.Text("saidas"), numeric=True),
                ft.DataColumn(ft.Text("Estoque Atual"), numeric=True),
            ], height=800)
            
        # Inicializa a tabela de histórico
        try:
            self.update_table()
        except:
            pass
            
        # Configura o content com o resultado do método build
        self.content = self.build()
    
    def Entradas(self, e):
        entradas = getEntradas(getRelatorioUnico(self.day).id)
        content = ft.Column(height=500)
        for nome, quantidade in entradas.items():
            content.controls.append(ft.Text(f"{nome}---{quantidade}"))

        entrada_dialog = ft.AlertDialog(title=ft.Text('Entradas'), content=content)
        entrada_dialog.actions = [ft.ElevatedButton("fechar", on_click=lambda e: self.pagex.close(entrada_dialog))]
        self.pagex.open(entrada_dialog)

    def Saidas(self, e):
        saidas = getSaidas(getRelatorioUnico(self.day).id)
        content = ft.Column(height=500)
        saida_dialog = ft.AlertDialog(title=ft.Text('Saidas'), content=content, actions=[
            ft.ElevatedButton("fechar", bgcolor=ft.Colors.RED_400)])
        saida_dialog.actions = [ft.ElevatedButton("fechar", on_click=lambda e: self.pagex.close(saida_dialog))]

        for nome, quantidade in saidas.items():
            content.controls.append(ft.Text(f"{nome}---{quantidade}"))
            
        self.pagex.open(saida_dialog)
    
    def update_table(self):
        try:
            for estoque in getHistoricoEstoque(getRelatorioUnico(self.day).id):
                self.historico.rows.append(
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
    
    def build(self):
        return ft.Column([
            ft.Container(padding=8, content=ft.Row([
                ft.FilledButton("Ver Entradas", bgcolor=ft.Colors.INDIGO_400, on_click=self.Entradas),
                ft.FilledButton("Ver Saidas", bgcolor=ft.Colors.INDIGO_400, on_click=self.Saidas),
            ])),
              ft.Card(content=self.historico)
        ])

# Função de compatibilidade para o código existente
def estoquePage(pagex):
    return EstoquePage(pagex)