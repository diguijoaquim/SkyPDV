import flet as ft
from controler import *

class SettingsPage(ft.Container):
    def __init__(self, pagex):
        super().__init__()
        self.page = pagex
        self.expand = True
        self.bgcolor = "#F0F8FF"  # Light blue-white background
        self.tabela = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nome")),
                ft.DataColumn(ft.Text("Nome do usuario")),
                ft.DataColumn(ft.Text("accoes"), numeric=True),
            ],
        )
        self.funcionarios = []
        self.cng_old = ft.TextField(label='Digite a senha anterior')
        self.cng_new = ft.TextField(label='Digite a nova senha ')
        self.cng = ft.AlertDialog(title=ft.Text('Mudar a senha do usuario'), content=ft.Column(controls=[
            self.cng_old, self.cng_new, ft.FilledButton("mudar a senha", on_click=self.confirm_change_password, bgcolor=ft.Colors.INDIGO_400)
        ]))
        self.name = ft.TextField(label='Nome do funcionario')
        self.username_input = ft.TextField(label='username')
        self.senha = ft.TextField(label='senha')
        self.userDialog = ft.AlertDialog(title=ft.Text("Adicionar Usuario"),
                                content=ft.Column(height=250, controls=[
                                    self.name,
                                    self.username_input,
                                    self.senha,
                                    ft.ElevatedButton("Cadastar Funcionario", on_click=self.cadastrar, bgcolor=ft.Colors.INDIGO_400)
                                ]))
        # Inicializa a página configurando o content com o resultado do método build
        self.content = self.build()

    def deletar(self, e):
        if(int(e.control.key) == 1):
            def f(e):
                self.page.close(d)
            d = ft.AlertDialog(title=ft.Text("Aviso"), content=ft.Text("O Admin Nao pode ser eliminado"), actions=[ft.TextButton('fechar', on_click=f)])
            self.page.open(d)
        else:
            excluir_funcionario(e.control.key)
            self.funcionarios = []
            for i in getFuncionarios():
                self.funcionarios.append(ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(i.nome)),
                            ft.DataCell(ft.Text(i.username)),
                            ft.DataCell(ft.IconButton(icon=ft.Icons.DELETE, key=i.id, on_click=self.deletar)),
                        ],
                    ),)
            self.tabela.rows = self.funcionarios
            self.page.update()

    def confirm_change_password(self, e):
        if(userLoged().senha == self.cng_old.value):
            self.cng_old.label = "Digite a senha anterior"
            self.cng_old.border_color = None
            self.page.update()
            changePassword(userLoged(), self.cng_new.value)
            self.cng.open = False
            self.page.update()
        else:
            self.cng_old.label = "por favor tente novamente"
            self.cng_old.border_color = "red"
            self.page.update()

    def chang_password(self, e):
        self.page.open(self.cng)

    def cadastrar(self, e):
        if self.name.value != '' and self.senha.value != "":
            CadastrarUsuario(self.name.value, 'simples', u=self.username_input.value, s_=self.senha.value)
            self.name.value = ""
            self.senha.value = ""
            self.username_input.value = ""
            self.funcionarios = []
            for i in getFuncionarios():
                self.funcionarios.append(ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(i.nome)),
                            ft.DataCell(ft.Text(i.username)),
                            ft.DataCell(ft.IconButton(icon=ft.Icons.DELETE, key=i.id, on_click=self.deletar)),
                        ],
                    ),)
            self.tabela.rows = self.funcionarios
            self.page.update()

    def addUser(self, e):
        self.page.open(self.userDialog)

    def did_mount(self):
        self.funcionarios.clear()
        for i in getFuncionarios():
            self.funcionarios.append(ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(i.nome)),
                        ft.DataCell(ft.Text(i.username)),
                        ft.DataCell(ft.IconButton(icon=ft.Icons.DELETE, key=i.id, on_click=self.deletar)),
                    ],
                ),)
        self.tabela.rows = self.funcionarios
        self.page.update()

    def build(self):
        return ft.Container(
            bgcolor="#F0F8FF",  # Light blue-white background
            content=ft.Column([
                ft.Container(
                    padding=10,
                    border_radius=10,
                    bgcolor="white",
                    content=ft.Row([
                        ft.Text("Configurações", size=30, weight="bold", color=ft.Colors.INDIGO_400),
                        ft.FilledButton("Mudar senha", on_click=self.chang_password, bgcolor=ft.Colors.INDIGO_400)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ),
                ft.Container(
                    padding=20,
                    content=ft.Column([
                        ft.ElevatedButton(
                            "Gerenciar Usuários",
                            icon=ft.icons.PEOPLE,
                            bgcolor=ft.Colors.INDIGO_400,
                            color="white",
                            on_click=self.manage_users
                        ),
                        ft.ElevatedButton(
                            "Configurações do Sistema",
                            icon=ft.icons.SETTINGS,
                            bgcolor=ft.Colors.INDIGO_400,
                            color="white",
                            on_click=self.system_settings
                        ),
                        ft.ElevatedButton(
                            "Backup e Restauração",
                            icon=ft.icons.BACKUP,
                            bgcolor=ft.Colors.INDIGO_400,
                            color="white",
                            on_click=self.backup_restore
                        )
                    ])
                )
            ])
        )

    def manage_users(self, e):
        """Handle user management"""
        self.addUser(e)  # Reuse existing user management dialog

    def system_settings(self, e):
        """Handle system settings"""
        # TODO: Implement system settings functionality
        def close_dialog(e):
            dialog.open = False
            self.page.update()
            
        dialog = ft.AlertDialog(
            title=ft.Text("Sistema"),
            content=ft.Text("Configurações do sistema em desenvolvimento"),
            actions=[ft.TextButton("OK", on_click=close_dialog)]
        )
        self.page.open(dialog)

    def backup_restore(self, e):
        """Handle backup and restore"""
        # TODO: Implement backup/restore functionality
        def close_dialog(e):
            dialog.open = False
            self.page.update()
            
        dialog = ft.AlertDialog(
            title=ft.Text("Backup"),
            content=ft.Text("Funcionalidade de backup em desenvolvimento"),
            actions=[ft.TextButton("OK", on_click=close_dialog)]
        )
        self.page.open(dialog)

# Função de compatibilidade para o código existente
def setting(pagex: ft.Page):
    return SettingsPage(pagex)