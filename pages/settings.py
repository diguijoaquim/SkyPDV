import flet as ft
from controler import *
page:ft.Page=None
tabela=None


def deletar(e):
    if(int(e.control.key)==1):
        def f(e):
            page.close(d)
        d=ft.AlertDialog(title=ft.Text("Aviso"),content=ft.Text("O Admin Nao pode ser eliminado"),actions=[ft.TextButton('fechar',on_click=f)])
        page.open(d)
    else:
        excluir_funcionario(e.control.key)
        funcionarios=[]
        for i in getFuncionarios():
            funcionarios.append(ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(i.nome)),
                        ft.DataCell(ft.Text(i.username)),
                        ft.DataCell(ft.IconButton(icon=ft.Icons.DELETE,key=i.id,on_click=deletar)),
                    ],
                ),)
        tabela.rows=funcionarios
        page.update()
            

funcionarios=[]
tabela=ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Nome")),
            ft.DataColumn(ft.Text("Nome do usuario")),
            ft.DataColumn(ft.Text("accoes"), numeric=True),
        ],
        )
if is_logged():
    
    for i in getFuncionarios():
        funcionarios.append(ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(i.nome)),
                    ft.DataCell(ft.Text(i.username)),
                    ft.DataCell(ft.IconButton(icon=ft.Icons.DELETE,key=i.id,on_click=deletar)),
                ],
            ),)
        tabela.rows=funcionarios
    ft.Text(get_logged_user()['username'],weight="bold")

def confirm_change_password(e):
        
        if(userLoged().senha==cng_old.value):
            cng_old.label="Digite a senha anterior"
            cng_old.border_color=None
            page.update()
            changePassword(userLoged(),cng_new.value)
            cng.open=False
            page.update()
        else:
            cng_old.label="por favor tente novamente"
            cng_old.border_color="red"
            page.update()

cng_old=ft.TextField(label='Digite a senha anterior')
cng_new=ft.TextField(label='Digite a nova senha ')
cng=ft.AlertDialog(title=ft.Text('Mudar a senha do usuario'), content=ft.Column(controls=[
cng_old,cng_new,ft.FilledButton("mudar a senha",on_click=confirm_change_password)
]))
def chang_password(e):
    page.open(cng)

name=ft.TextField(label='Nome do funcionario')
username_input=ft.TextField(label='username')
senha=ft.TextField(label='senha')

def cadastrar(e):
    if name.value != '' and senha.value !="":
        CadastrarUsuario(name.value,'simples',u=username_input.value,s_=senha.value)
        name.value=""
        senha.value=""
        username_input.value=""
        funcionarios=[]
        for i in getFuncionarios():
            funcionarios.append(ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(i.nome)),
                        ft.DataCell(ft.Text(i.username)),
                        ft.DataCell(ft.IconButton(icon=ft.Icons.DELETE,key=i.id,on_click=deletar)),
                    ],
                ),)
        tabela.rows=funcionarios
        page.update()
userDialog=ft.AlertDialog(title=ft.Text("Adicionar Usuario"),
                              content=ft.Column(height=250,controls=[
                                  name,
                                  username_input,
                                  senha,
                                  ft.ElevatedButton("Cadastar Funcionario",on_click=cadastrar)
                              ]))
def addUser(e):
    page.open(userDialog)

def setting(pagex:ft.Page):
    global page
    funcionarios.clear()
    for i in getFuncionarios():
        funcionarios.append(ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(i.nome)),
                    ft.DataCell(ft.Text(i.username)),
                    ft.DataCell(ft.IconButton(icon=ft.Icons.DELETE,key=i.id,on_click=deletar)),
                ],
            ),)
        tabela.rows=funcionarios
    page=pagex
    return ft.Container(content=ft.Column(controls=[
                    ft.Text("Configuracoes",size=34,weight="bold"),
                        ft.Row(controls=[
                            ft.Card(content=ft.Container(padding=10,content=ft.Column(controls=[
                            ft.Row(controls=[
                                ft.Text("Username: "),ft.Text(get_logged_user()['username'],weight="bold")
                            ]),
                            ft.Row(controls=[
                                ft.Text("Nome: "),ft.Text(get_logged_user()['nome'],weight="bold")
                            ]),
                            ft.Row(controls=[
                                ft.Text("Papel: "),ft.Text(get_logged_user()['cargo'],weight="bold")
                            ]),
                            
                        ]))),
                
                ft.Card(content=ft.Container(padding=40,content=ft.Column(controls=[
                    ft.FilledButton(f"mudar a senha",on_click=chang_password),
                    
                    ft.FilledButton(f"adicionar user",on_click=addUser)      
                ])))
                

                ]),
                tabela
                
                
                ]))