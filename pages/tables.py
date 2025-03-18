import flet as ft
from controler import db
from models.modelos import Mesa

class TablesPage(ft.Container):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.expand = True
        self.padding = 8
        self.bgcolor = "#F0F8FF"  # Light blue-white background
        self.mesas = []  # Lista para armazenar mesas
        self.error_dialog = ft.AlertDialog(
            title=ft.Text("Erro"), 
            content=ft.Text(""), 
            actions=[ft.TextButton("OK", on_click=self.close_error_dialog)]
        )
        
        # Inicializa os componentes
        self.numero_input = ft.TextField(
            label="Número da Mesa", 
            keyboard_type=ft.KeyboardType.NUMBER,
            width=400,
            border_radius=8
        )
        
        self.capacidade_input = ft.TextField(
            label="Capacidade", 
            keyboard_type=ft.KeyboardType.NUMBER,
            width=400,
            border_radius=8
        )
        
        self.status_dropdown = ft.Dropdown(
            label="Status",
            width=400,
            options=[
                ft.dropdown.Option("livre"),
                ft.dropdown.Option("ocupada"),
                ft.dropdown.Option("reservada")
            ],
            value="livre"
        )
        
        # Tabela de mesas
        self.mesas_table = ft.DataTable(
            expand=True,
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Número")),
                ft.DataColumn(ft.Text("Capacidade")),
                ft.DataColumn(ft.Text("Status")),
                ft.DataColumn(ft.Text("Ações"))
            ],
            column_spacing=50,
            rows=[]
        )
        
        # Container para a tabela com scroll
        self.mesas_grid = ft.Container(
            content=ft.ListView(
                expand=True,
                spacing=10,
                padding=10,
                auto_scroll=True,
                controls=[self.mesas_table]
            ),
            expand=True,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=10
        )
        
        # Inicializa as mesas
        self.update_mesas()
        
        # Configura o content com o resultado do método build
        self.content = self.build()

    def build(self):
        return ft.Column(
            [
                ft.Container(
                    padding=10,
                    border_radius=10,
                    bgcolor="white",
                    content=ft.Row([
                        ft.Text("Mesas", size=30, weight="bold", color=ft.Colors.INDIGO_400),
                        ft.CupertinoButton(
                            "Adicionar Mesa",
                            icon=ft.Icons.ADD,
                            bgcolor=ft.Colors.INDIGO_400,
                            color="white",
                            on_click=self.add_mesa_dialog
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ),
                ft.Container(
                    content=self.mesas_grid,
                    expand=1
                )
            ],
            spacing=10,
            expand=True
        )

    def update_mesas(self):
        self.mesas_table.rows = []
        mesas = db.query(Mesa).all()
        
        for mesa in mesas:
            # Define a cor do status
            status_color = "green" if mesa.status == "livre" else "red" if mesa.status == "ocupada" else "orange"
            
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(mesa.id)),
                    ft.DataCell(ft.Text(mesa.numero)),
                    ft.DataCell(ft.Text(mesa.capacidade)),
                    ft.DataCell(ft.Container(
                        content=ft.Text(
                            mesa.status,
                            color=status_color,
                            weight="bold"
                        ),
                        padding=5,
                        border_radius=5,
                        bgcolor=ft.colors.with_opacity(0.1, status_color)
                    )),
                    ft.DataCell(ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.icons.EDIT,
                                icon_color=ft.colors.BLUE,
                                tooltip="Editar",
                                on_click=lambda e, mesa_id=mesa.id: self.editar_mesa(mesa_id)
                            ),
                            ft.IconButton(
                                icon=ft.icons.DELETE,
                                icon_color=ft.colors.RED,
                                tooltip="Excluir",
                                on_click=lambda e, mesa_id=mesa.id: self.confirmar_exclusao(mesa_id)
                            )
                        ],
                        spacing=5
                    ))
                ]
            )
            self.mesas_table.rows.append(row)
        self.page.update()

    def add_mesa_dialog(self, e):
        # Reseta os campos
        self.numero_input.value = ""
        self.capacidade_input.value = ""
        self.status_dropdown.value = "livre"
        
        # Cria o diálogo
        dialog = ft.AlertDialog(
            title=ft.Text("Adicionar Nova Mesa", size=24),
            content=ft.Column([
                self.numero_input,
                self.capacidade_input,
                self.status_dropdown
            ], scroll=True, spacing=10),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.close(dialog)),
                ft.ElevatedButton(
                    "Salvar", 
                    bgcolor=ft.colors.INDIGO_400,
                    color=ft.colors.WHITE,
                    on_click=lambda e: self.salvar_mesa(dialog)
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        # Abre o diálogo
        self.page.open(dialog)

    def salvar_mesa(self, dialog):
        # Verifica se os campos de entrada não estão vazios
        if not self.numero_input.value or not self.capacidade_input.value:
            self.show_error("Por favor, preencha todos os campos.")
            return

        try:
            # Tenta converter os valores para inteiros
            numero = int(self.numero_input.value)
            capacidade = int(self.capacidade_input.value)
            
            # Cria uma nova mesa e salva no banco de dados
            nova_mesa = Mesa(
                numero=numero, 
                capacidade=capacidade, 
                status=self.status_dropdown.value
            )
            db.add(nova_mesa)
            db.commit()
            
            # Fecha o diálogo e atualiza a tabela
            self.page.close(dialog)
            self.update_mesas()
            
        except ValueError:
            self.show_error("Por favor, insira valores numéricos válidos.")

    def editar_mesa(self, mesa_id):
        # Busca a mesa no banco de dados
        mesa = db.query(Mesa).filter_by(id=mesa_id).first()
        
        # Preenche os campos com os valores atuais
        self.numero_input.value = str(mesa.numero)
        self.capacidade_input.value = str(mesa.capacidade)
        self.status_dropdown.value = mesa.status
        
        # Cria o diálogo de edição
        dialog = ft.AlertDialog(
            title=ft.Text(f"Editar Mesa #{mesa.numero}", size=24),
            content=ft.Column([
                self.numero_input,
                self.capacidade_input,
                self.status_dropdown
            ], scroll=True, spacing=10),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.close(dialog)),
                ft.ElevatedButton(
                    "Atualizar", 
                    bgcolor=ft.colors.INDIGO_400,
                    color=ft.colors.WHITE,
                    on_click=lambda e: self.atualizar_mesa(dialog, mesa_id)
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        # Abre o diálogo
        self.page.open(dialog)

    def atualizar_mesa(self, dialog, mesa_id):
        # Verifica se os campos de entrada não estão vazios
        if not self.numero_input.value or not self.capacidade_input.value:
            self.show_error("Por favor, preencha todos os campos.")
            return

        try:
            # Tenta converter os valores para inteiros
            numero = int(self.numero_input.value)
            capacidade = int(self.capacidade_input.value)
            
            # Atualiza a mesa no banco de dados
            mesa = db.query(Mesa).filter_by(id=mesa_id).first()
            mesa.numero = numero
            mesa.capacidade = capacidade
            mesa.status = self.status_dropdown.value
            db.commit()
            
            # Fecha o diálogo e atualiza a tabela
            self.page.close(dialog)
            self.update_mesas()
            
        except ValueError:
            self.show_error("Por favor, insira valores numéricos válidos.")

    def confirmar_exclusao(self, mesa_id):
        # Cria o diálogo de confirmação
        dialog = ft.AlertDialog(
            title=ft.Text("Confirmar Exclusão"),
            content=ft.Text("Tem certeza que deseja excluir esta mesa?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.close(dialog)),
                ft.ElevatedButton(
                    "Excluir", 
                    bgcolor=ft.colors.RED,
                    color=ft.colors.WHITE,
                    on_click=lambda e: self.excluir_mesa(dialog, mesa_id)
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        # Abre o diálogo
        self.page.open(dialog)

    def excluir_mesa(self, dialog, mesa_id):
        # Exclui a mesa do banco de dados
        mesa = db.query(Mesa).filter_by(id=mesa_id).first()
        db.delete(mesa)
        db.commit()
        
        # Fecha o diálogo e atualiza a tabela
        self.page.close(dialog)
        self.update_mesas()

    def show_error(self, message):
        self.error_dialog.content = ft.Text(message)
        self.page.open(self.error_dialog)

    def close_error_dialog(self, e):
        self.page.close(self.error_dialog)

# Função de compatibilidade para o código existente
def tablesPage(pagex):
    return TablesPage(pagex)