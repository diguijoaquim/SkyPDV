import flet as ft
from controler import *

class EstoquePage(ft.Container):
    def __init__(self, pagex:ft.Page):
        super().__init__()
        self.pagex = pagex
        self.expand = True
        self.padding = 8
        self.height=pagex.window.height
        self.bgcolor = "#F0F8FF"  # Light blue-white background
        self.imagens = os.path.join(os.getenv("LOCALAPPDATA"), ".jpInvest/img")
        self.banco = isDataBase()
        self.current_date = datetime.now()
        self.day = self.current_date.strftime("%d-%m-%Y")
        self.selected_relatorio_id = None
        
        # Dropdown para selecionar relatórios
        self.relatorio_dropdown = ft.Dropdown(
            label="Selecione um relatório",
            width=300,
            on_change=self.on_relatorio_change
        )
        
        # Carrega os relatórios disponíveis
        self.load_relatorios()
        
        # Diálogo para quando não há relatório disponível
        self.no_relatorio_dialog = ft.AlertDialog(
            title=ft.Text("Relatório não encontrado"),
            content=ft.Text("Não há relatório para a data atual. Deseja criar um novo?"),
            actions=[
                ft.TextButton("Cancelar", on_click=self.close_no_relatorio_dialog),
                ft.ElevatedButton("Criar Relatório", on_click=self.criar_novo_relatorio)
            ]
        )
        
        self.historico = ft.DataTable(
            expand=True,
            columns=[
                ft.DataColumn(ft.Text("Nome", size=16, weight="bold")),
                ft.DataColumn(ft.Text("Estoque Inicial", size=16, weight="bold")),
                ft.DataColumn(ft.Text("Entradas", size=16, weight="bold")),
                ft.DataColumn(ft.Text("Saídas", size=16, weight="bold")),
                ft.DataColumn(ft.Text("Estoque Atual", size=16, weight="bold"))
            ],
            column_spacing=30,
            horizontal_lines=ft.border.BorderSide(1, "#EEEEEE"),
            vertical_lines=ft.border.BorderSide(1, "#EEEEEE")
        )
        
        # Container para a tabela com scroll
        self.historico_container = ft.Container(
            content=ft.ListView(
                expand=True,
                spacing=10,
                padding=10,
                auto_scroll=True,
                controls=[self.historico]
            ),
            expand=True,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=10
        )
            
        # Inicializa a tabela de histórico
        self.check_and_load_relatorio()
            
        # Configura o content com o resultado do método build
        self.content = self.build()
    
    def load_relatorios(self):
        """Carrega todos os relatórios disponíveis no dropdown"""
        relatorios = getRelatorios()
        
        # Limpa as opções atuais
        self.relatorio_dropdown.options = []
        
        # Adiciona opção para cada relatório
        for relatorio in relatorios:
            self.relatorio_dropdown.options.append(
                ft.dropdown.Option(relatorio.data, data=relatorio.id)
            )
        
        # Define a data atual como padrão, se disponível
        for option in self.relatorio_dropdown.options:
            if option.key == self.day:
                self.relatorio_dropdown.value = option.key
                self.selected_relatorio_id = option.data
                break
    
    def on_relatorio_change(self, e):
        """Chamado quando um relatório é selecionado no dropdown"""
        for option in self.relatorio_dropdown.options:
            if option.key == self.relatorio_dropdown.value:
                self.selected_relatorio_id = option.data
                break
        
        # Atualiza a tabela com o relatório selecionado
        self.update_table()
        self.pagex.update()
    
    def check_and_load_relatorio(self):
        """Verifica se existe um relatório para hoje e carrega ou mostra diálogo"""
        relatorio = getRelatorioUnico(self.day)
        if relatorio:
            self.selected_relatorio_id = relatorio.id
            self.update_table()
        else:
            # Programa a abertura do diálogo após a atualização inicial da página
            self.pagex.after_build_complete = lambda: self.pagex.open(self.no_relatorio_dialog)
    
    def close_no_relatorio_dialog(self, e):
        self.pagex.close(self.no_relatorio_dialog)
    
    def criar_novo_relatorio(self, e):
        db=get_db()
        """Cria um novo relatório para o dia atual"""
        self.pagex.close(self.no_relatorio_dialog)
        
        # Verifica se já existe um relatório para hoje (dupla verificação)
        if db.query(RelatorioVenda).filter_by(nome=f"relatorio{self.day}").count() > 0:
            aviso_dialog = ft.AlertDialog(
                title=ft.Text("Aviso"),
                content=ft.Text("Já existe um relatório para hoje."),
                actions=[ft.TextButton("OK", on_click=lambda e: self.pagex.close(aviso_dialog))]
            )
            self.pagex.open(aviso_dialog)
            return
        
        # Obtém os produtos em estoque
        estoque_hoje = db.query(Produto).all()
        entrada = []
        
        for i in estoque_hoje:
            entrada.append({
                "nome": i.titulo,
                "estoque": i.estoque
            })
        
        # Adiciona o relatório
        addRelatorio(self.day, entrada)
        
        # Recarrega os relatórios e atualiza a tabela
        self.load_relatorios()
        self.check_and_load_relatorio()
        self.pagex.update()
    
    def Entradas(self, e):
        if not self.selected_relatorio_id:
            aviso_dialog = ft.AlertDialog(
                title=ft.Text("Aviso"),
                content=ft.Text("Selecione um relatório primeiro."),
                actions=[ft.TextButton("OK", on_click=lambda e: self.pagex.close(aviso_dialog))]
            )
            self.pagex.open(aviso_dialog)
            return
            
        entradas = getEntradas(self.selected_relatorio_id)
        content = ft.Column(height=500)
        for nome, quantidade in entradas.items():
            content.controls.append(ft.Text(f"{nome}---{quantidade}"))

        entrada_dialog = ft.AlertDialog(title=ft.Text('Entradas'), content=content)
        entrada_dialog.actions = [ft.ElevatedButton("fechar", on_click=lambda e: self.pagex.close(entrada_dialog))]
        self.pagex.open(entrada_dialog)

    def Saidas(self, e):
        if not self.selected_relatorio_id:
            aviso_dialog = ft.AlertDialog(
                title=ft.Text("Aviso"),
                content=ft.Text("Selecione um relatório primeiro."),
                actions=[ft.TextButton("OK", on_click=lambda e: self.pagex.close(aviso_dialog))]
            )
            self.pagex.open(aviso_dialog)
            return
            
        saidas = getSaidas(self.selected_relatorio_id)
        content = ft.Column(height=500)
        saida_dialog = ft.AlertDialog(title=ft.Text('Saidas'), content=content, actions=[
            ft.ElevatedButton("fechar", bgcolor=ft.Colors.RED_400)])
        saida_dialog.actions = [ft.ElevatedButton("fechar", on_click=lambda e: self.pagex.close(saida_dialog))]

        for nome, quantidade in saidas.items():
            content.controls.append(ft.Text(f"{nome}---{quantidade}"))
            
        self.pagex.open(saida_dialog)
    
    def update_table(self):
        """Atualiza a tabela com os dados do relatório selecionado"""
        if not self.selected_relatorio_id:
            return
            
        # Limpa as linhas existentes
        self.historico.rows = []
        
        try:
            for estoque in getHistoricoEstoque(self.selected_relatorio_id):
                self.historico.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Container(
                            content=ft.Text(estoque['nome'], size=14),
                            padding=ft.padding.symmetric(horizontal=10)
                        )),
                        ft.DataCell(ft.Text(estoque['estoque_inicial'], size=14)),
                        ft.DataCell(ft.Container(
                            content=ft.Text(
                                estoque['entrada'],
                                color="green",
                                weight="bold",
                                size=14
                            ),
                            padding=5,
                            border_radius=5,
                            bgcolor=ft.Colors.with_opacity(0.1, "green")
                        )),
                        ft.DataCell(ft.Container(
                            content=ft.Text(
                                estoque['saida'],
                                color="red",
                                weight="bold",
                                size=14
                            ),
                            padding=5,
                            border_radius=5,
                            bgcolor=ft.Colors.with_opacity(0.1, "red")
                        )),
                        ft.DataCell(ft.Text(estoque['estoque_atual'], weight="bold", size=14))
                    ])
                )
        except Exception as e:
            print(f"Erro ao carregar histórico: {e}")
    
    def gerar_relatorio(self, e):
        if not self.selected_relatorio_id:
            aviso_dialog = ft.AlertDialog(
                title=ft.Text("Aviso"),
                content=ft.Text("Selecione um relatório primeiro."),
                actions=[ft.TextButton("OK", on_click=lambda e: self.pagex.close(aviso_dialog))]
            )
            self.pagex.open(aviso_dialog)
            return
            
        from pdv2pdf import gerar_relatorio_estoque_pdf
        gerar_relatorio_estoque_pdf(self.selected_relatorio_id)

    def build(self):
        return ft.Column([
            ft.Container(
                padding=20,
                border_radius=10,
                bgcolor="white",
                content=ft.Row(
                    [
                        ft.Text("Histórico de Estoque", size=30, weight="bold", color=ft.Colors.INDIGO_400),
                        ft.Row([
                            ft.CupertinoButton(
                                text="Ver Entradas", 
                                bgcolor=ft.Colors.INDIGO_400,
                                color="white",
                                on_click=self.Entradas
                            ),
                            ft.CupertinoButton(
                                text="Ver Saidas", 
                                bgcolor=ft.Colors.INDIGO_400,
                                color="white",
                                on_click=self.Saidas
                            ),
                            ft.CupertinoButton(
                                text="Gerar PDF", 
                                bgcolor=ft.Colors.INDIGO_400,
                                color="white",
                                on_click=self.gerar_relatorio
                            ),
                        ], spacing=10),
                        self.relatorio_dropdown
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
            ),
            ft.Container(
                content=self.historico_container,
                expand=1,
                padding=10
            )
        ])

# Função de compatibilidade para o código existente
def estoquePage(pagex):
    return EstoquePage(pagex)