import flet as ft
from controler import *
from sqlalchemy import asc
from models.modelos import Produto
from pdv2pdf import gerar_pdf_produtos
import os
from local import get_logged_user
import shutil

page=None #we need update this var to page off our app
imagens=os.path.join(os.getenv("LOCALAPPDATA"), ".jpInvest/img") # path off imagens
update_menu=None
update_produtos=None
banco=isDataBase()
current_date = datetime.now()
day = current_date.strftime("%d-%m-%Y")
categoria_lista = getCategorias()


def file_picker_result(e: ft.FilePickerResultEvent):
    global selected_file_path
    if e.files:
        selected_file_path = e.files[0].path
        status_text.value = f"Arquivo selecionado: {selected_file_path}"
    else:
        selected_file_path = None
        status_text.value = "Nenhum arquivo selecionado"
    page.update()

status_text = ft.Text()
file_picker = ft.FilePicker(on_result=file_picker_result)

select_button = ft.ElevatedButton(text="Selecionar Foto", on_click=lambda _: file_picker.pick_files(allow_multiple=False))
selected_file_path = None
def imprimir_todos(e):
    produtos = db.query(Produto).order_by(asc(Produto.titulo)).all()
    gerar_pdf_produtos(produtos)

def atualizar(id):
    if(get_logged_user()['cargo'])=='admin':
        produto=acharUmProduto(id) 
        global dlg_edit
        e_nome_input.value=produto.titulo
        e_barcode_input.value=produto.barcode
        e_preco_input.value=produto.preco
        e_estoque.value=produto.estoque
        input_categoria.value=produto.categoria
        dlg_edit=ft.AlertDialog(
        title=ft.Text("Atualizar o Produto", size=24),
        content=ft.Column([
            e_nome_input,
            e_barcode_input,
            e_preco_input,
            e_estoque,
            input_categoria,
            status_text,
            select_button
        ], scroll=True),  # Permite rolagem se o conteúdo for maior que o espaço disponível
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: page.close(dlg_edit)),
            ft.ElevatedButton("Atualizar", on_click=update_produto,key=id)
        ])

        page.open(dlg_edit)
    else:
        page.open(ft.AlertDialog(title=ft.Text("Aviso"),content=ft.Row([
            ft.Icon(ft.Icons.INFO,color=ft.Colors.RED_600),
            ft.Text("Nao tens permicao para \n editar produtos",weight="bold")
        ])))

nome_input = ft.TextField(label="Nome", width=400)
preco_input = ft.TextField(label="Preço", width=400)
barcode=ft.TextField(label="barcode Scanneado")
select_button = ft.ElevatedButton(text="Selecionar Foto", on_click=lambda _: file_picker.pick_files(allow_multiple=False))
estoque = ft.TextField(label="estoque", multiline=True, width=400,)
categoria = ft.Dropdown(
        label="Categoria",
        options=[ft.dropdown.Option(categoria.nome) for categoria in categoria_lista]
    )
e_nome_input = ft.TextField(label="Nome", width=400)
e_preco_input = ft.TextField(label="Preço", width=400)
e_barcode_input=ft.TextField(label="Barcode Scanneado")
e_estoque = ft.TextField(label="Estoque", multiline=True, width=400)


def cancel_dlg(event):
    dlg.open=False
    page.update()
def update_produto(e):
    global dlg_edit,selected_file_path
    destination_dir = os.path.join(os.getenv("LOCALAPPDATA"), ".jpInvest/img")

    if  not selected_file_path:
        pass
    else:
    
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)
        filename = os.path.basename(selected_file_path)
        destination_path = os.path.join(destination_dir, filename)
        try:
            shutil.copy(selected_file_path, destination_path)
            status_text.value = "Foto copiada com sucesso!"
        except Exception as ex:
            status_text.value = f"Erro ao copiar a foto: {ex}"
        page.update()
        


    pdt=acharUmProduto(e.control.key)
    pdt.titulo=e_nome_input.value
    pdt.preco=e_preco_input.value
    pdt.estoque=e_estoque.value
    pdt.categoria=input_categoria.value

    if e_barcode_input.value !="" and e_barcode_input.value!=None:
        pdt.barcode=e_barcode_input.value
    if  not selected_file_path:
        pass
    else:
        pdt.image=filename
    selected_file_path=None
    AtualisarProduto(int(e.control.key),pdt)
    dlg_edit.open=False
    page.update()
    update_menu()
    update_produtos()
    page.update()

def close_modal(e):
        page.close(relatorio_alert)

def fecha(e):
    dialogo.open=False
    page.update()
dialogo=ft.AlertDialog(title=ft.Text("PDV LITE"),
                           content=ft.Text("So pode criar um Relatorios por dia"),
                           actions=[
                               ft.TextButton('intendi',on_click=fecha)
                           ] )
def novo_relatorio(e):
        relatorio_alert.open = False
        page.update()
        rlt = db.query(RelatorioVenda).filter_by(nome=f"relatorio{day}").count()
        
        if rlt > 0:
            page.open(dialogo)
        else:
            estoque_hoje = db.query(Produto).all()
            entrada = []
            
            for i in estoque_hoje:
                entrada.append({
                    "nome": i.titulo,
                    "estoque": i.estoque
                })
            addRelatorio(day, entrada)  

relatorio_alert=ft.AlertDialog(title=ft.Text("Sem Relatorio"),content=ft.Text("Nao tem um Relatorio diario para Hoje! Voce deseja criar?"),actions=[
        ft.TextButton('Cancelar',on_click=close_modal),
        ft.ElevatedButton("Criar Relatorio",on_click=novo_relatorio)
    ])
  
def add(e):
    global selected_file_path
    filename=None
    destination_dir = os.path.join(os.getenv("LOCALAPPDATA"), ".jpInvest/img")
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    if selected_file_path:
        filename = os.path.basename(selected_file_path)
        destination_path = os.path.join(destination_dir, filename)
        try:
            shutil.copy(selected_file_path, destination_path)
            status_text.value = "Foto copiada com sucesso!"
        except Exception as ex:
            status_text.value = f"Erro ao copiar a foto: {ex}"
    page.update()
    try:
        CadastrarProduto(nome_input.value,barcode.value, categoria.value,preco_input.value, estoque.value, filename,getRelatorioUnico(day).id)
    except:
        novo_relatorio(e)
        CadastrarProduto(nome_input.value,barcode.value, categoria.value,preco_input.value, estoque.value, filename,getRelatorioUnico(day).id)
    dlg.open=False
    page.update()
    update_menu()
    update_produtos()
    selected_file_path=None
    

dlg = ft.AlertDialog(
    title=ft.Text("Cadastrar Novo Produto", size=24),
    content=ft.Column([
        nome_input,
        barcode,
        preco_input,
        categoria,
        estoque,
        select_button,
        status_text
        
    ], scroll=True),  # Permite rolagem se o conteúdo for maior que o espaço disponível
    actions=[
        ft.TextButton("Cancelar", on_click=cancel_dlg),
        ft.TextButton("Cadastrar", on_click=add),  # Fechar o diálogo sem ação adicional
    ],

)
# Diálogo de cadastro
    

def add_item(event):
    if(get_logged_user()['cargo'])=='admin':
        page.open(dlg)
    else:
        page.open(ft.AlertDialog(title=ft.Text("Nao Autorizado"),content=ft.Row([
            ft.Icon(ft.Icons.INFO,color='red'),
            ft.Text("Nao pode adicionar\n produtos")
        ])))
quant_estoque=ft.TextField(label="Digite a quantidade")

def fornecer(e):
    global selected_item_id
    resposta=incrementarStoque(selected_item_id,int(quant_estoque.value),getRelatorioUnico(day).id)
    if "Estoque atualizado" in resposta:
        update_produtos()
        page.open(ft.AlertDialog(title=ft.Text("PDV Lite"),content=ft.Row([ft.Icon(ft.Icons.INFO,color=ft.Colors.GREEN_500),ft.Text(resposta,weight='bold')])))
    else:
        page.open(ft.AlertDialog(title=ft.Text("PDV Lite"),content=ft.Row([ft.Icon(ft.Icons.INFO,color='red'),ft.Text(resposta,weight='bold')])))

fornecer_dialog=ft.AlertDialog(title=ft.Text("Fornecer Produto"),
                                    content=quant_estoque,
                                    actions=[
                                        ft.TextButton("Cancelar",on_click=lambda e:page.close(fornecer_dialog) ),
                                        ft.ElevatedButton("Guardar",bgcolor=ft.Colors.ORANGE_600,color=ft.Colors.WHITE,on_click=fornecer)
                                    ])
def open_estoque(id):
    global selected_item_id
    selected_item_id=id
    page.open(fornecer_dialog)

def eliminarProoduto(id):
    deletarProduto(id)
    update_menu()
    update_produtos()

def update_produtos():
    page.update()
    produtos.rows.clear()
    for i in verProdutos():
        
        produto_id = i.id  # Captura o ID do produto atual
        produtos.rows.append(
                ft.DataRow(
                cells=[
                    ft.DataCell(ft.Row([ft.Image(f'{imagens}/{i.image}',width=80,height=40),ft.Text(i.titulo, weight="bold", size=14)])),
                    ft.DataCell(ft.Text(f'{i.preco} MZN', weight="bold", size=13, color=ft.Colors.RED_700)),
                    ft.DataCell(ft.Text(i.barcode)),
                    ft.DataCell(ft.Text(i.categoria)),
                    ft.DataCell(ft.Text(i.estoque,size=18,weight='bold')),
                    
                    ft.DataCell(ft.PopupMenuButton(
                                items=[
                                    ft.PopupMenuItem(text="Editar", on_click=lambda e, produto_id=produto_id: atualizar(produto_id)),
                                    ft.PopupMenuItem(text="Fornecer Produto",  on_click=lambda e, produto_id=produto_id: open_estoque(produto_id)),
                                    ft.PopupMenuItem(text="Deletar", on_click=lambda e, produto_id=produto_id: eliminarProoduto(produto_id)),

                                ]
                            ),),
                ],
            ),
            )
        
        page.update()
def submit2(e):
    produtos.rows.clear()
    page.update()
    if e.control.value=="Todos os Produtos":
        for i in verProdutos():

            produto_id = i.id  # Captura o ID do produto atual
            produtos.rows.append(
                ft.DataRow(
                cells=[
                    ft.DataCell(ft.Row([ft.Image(f'{imagens}/{i.image}', width=80,height=40),ft.Text(i.titulo, weight="bold", size=14)])),
                    ft.DataCell(ft.Text(f'{i.preco} MZN', weight="bold", size=13, color=ft.Colors.RED_700)),
                    ft.DataCell(ft.Text(i.barcode)),
                    ft.DataCell(ft.Text(i.categoria)),
                    ft.DataCell(ft.Text(i.estoque,size=18,weight='bold')),
        
                    ft.DataCell(ft.PopupMenuButton(
                                items=[
                                    ft.PopupMenuItem(text="Editar", on_click=lambda e, produto_id=produto_id: atualizar(produto_id)),
                                    ft.PopupMenuItem(text="Fornecer Produto",  on_click=lambda e, produto_id=produto_id: open_estoque(produto_id)),
                                    ft.PopupMenuItem(text="Deletar", on_click=lambda e, produto_id=produto_id: eliminarProoduto(produto_id)),
                                ]
                            ),),
                ],
            ),
            )
            
    else:
        produtos.rows.clear()
        for i in pesquisaProduto(e.control.value):
            
            produto_id = i.id  # Captura o ID do produto atual
            produtos.rows.append(
                ft.DataRow(
                cells=[
                    ft.DataCell(ft.Row([ft.Image(f'{imagens}/{i.image}', width=80,height=40),ft.Text(i.titulo, weight="bold", size=14)])),
                    ft.DataCell(ft.Text(f'{i.preco} MZN', weight="bold", size=13, color=ft.Colors.RED_700)),
                    ft.DataCell(ft.Text(i.barcode)),
                    ft.DataCell(ft.Text(i.categoria)),
                    ft.DataCell(ft.Text(i.estoque,size=18,weight='bold')),
                    
                    ft.DataCell(ft.PopupMenuButton(
                                items=[
                                    ft.PopupMenuItem(text="Editar", on_click=lambda e, produto_id=produto_id: atualizar(produto_id)),
                                    ft.PopupMenuItem(text="Fornecer Produto",  on_click=lambda e, produto_id=produto_id: open_estoque(produto_id)),
                                    ft.PopupMenuItem(text="Deletar", on_click=lambda e, produto_id=produto_id: eliminarProoduto(produto_id)),
                                ]
                            ),),
                ],
            ),
            )
    page.update()

input_categoria = ft.Dropdown(
        label="Categoria",
        width=400,
        options=[ft.dropdown.Option(categoria.nome) for categoria in categoria_lista])

search_categoria2 = ft.Dropdown(
        label="Categoria",
        options=[ft.dropdown.Option(categoria.nome) for categoria in categoria_lista],
        on_change=submit2
    )
search2=ft.TextField(label="Procurar Produto",border_radius=12,on_change=submit2)

produtos=ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nome do produto")),
                ft.DataColumn(ft.Text("Preco")),
                ft.DataColumn(ft.Text("Codigo de Barra")),
                ft.DataColumn(ft.Text("Categoria")),
                ft.DataColumn(ft.Text("Estoque Atual"), numeric=True),
                ft.DataColumn(ft.Text("accoes")),
            ])



#this is the page or producta
def produtoBody(pagex,menu):
    global page,update_menu
    page=pagex
    update_menu=menu
    update_produtos()
    page.floating_action_button=ft.FloatingActionButton(
                        icon=ft.Icons.ADD, on_click=add_item
                    )

    page.overlay.append(file_picker)
    produtos_table_itens=ft.Container(height=page.window.height-20,padding=10)
    produtos_table_itens.content=ft.Card(content=ft.Container(expand=True,padding=10,
                     content=ft.ResponsiveRow(controls=[
                        ft.Column(controls=[
                           ft.ResponsiveRow(controls=[
                            produtos
                           ])
                        ],scroll=ft.ScrollMode.AUTO,height=page.window.height-10)
                    ],)))

    return ft.Container(
       content=ft.Column([
           ft.Container(padding=10,border_radius=10,bgcolor="white",content=ft.Row(controls=[
                            ft.Text(info['app'],size=30,weight="bold",color=ft.Colors.RED_500),
                            search_categoria2,
                            search2,
                            ft.CupertinoButton(text="Imprimir Tudo",bgcolor=ft.Colors.ORANGE_600,on_click=imprimir_todos)
                        ],alignment=ft.MainAxisAlignment.SPACE_BETWEEN)),
                        produtos_table_itens
       ])
    )