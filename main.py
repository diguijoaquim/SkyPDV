#Criado por Ghost04 - Diqui Joaquim 
import os
import shutil
import flet as ft
from controler import *
from models.modelos import ProdutoVenda,Mesa
from datetime import datetime
from pdv2pdf import*
from time import sleep
from contasToVenda import Venda
from controler import ContaInfoToVenda
from sqlalchemy import asc
from local import *
import win32print

# Corrigir importações para usar apenas as classes
from pages.settings import SettingsPage
from pages.products import ProductsPage
from pages.estoque import EstoquePage
from pages.tables import TablesPage
from pages.money import MoneyPage
from pages.relatorio import RelatorioPage


os.environ["FLET_WS_MAX_MSG_SIZE"] = "8000000"

selected_file_path = None
banco=isDataBase()
current_date = datetime.now()
quantidade_item=0
preco_total=0.00
carrinho = []
carrinho_s=[]
day = current_date.strftime("%d-%m-%Y")
hora=""
iva_p = 0.16
total_valor=0
codigo_barras=''
iva_label="Sem IVA"
desconto_label="Sem Desconto"
produtos_em_json=[]
ultima_venda={}
username=''
caixa=''
selected_item_id=None

dlg_edit = ft.AlertDialog(
        title=ft.Text("Atualizar o Produto", size=24))
settingBody=ft.Container(content=ft.Row([]))
horas=ft.Container(content=ft.Row([
    ft.Text("Hora:", size=15),
    ft.Text(current_date.strftime("%H:%M:%S"), size=15)
]))

def CheckIsLoged():
    return is_logged()

def initialize_app(page: ft.Page, body_config: ft.Container, login_page: ft.Container):
    # Sistema de verificação de requisitos
    requirements_container = ft.Container(
        width=400,
        height=300,
        bgcolor="white",
        border_radius=10,
        padding=20,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("Verificando requisitos do sistema", size=20, weight="bold", color=ft.Colors.INDIGO_400),
                ft.ProgressBar(width=300, color=ft.Colors.INDIGO_400),
                ft.Text("", size=16, color=ft.Colors.GREY_700),  # Status text
                ft.ProgressRing(color=ft.Colors.INDIGO_400, width=20, height=20, stroke_width=2)
            ]
        )
    )

    loading_screen = ft.Container(
        expand=True,
        bgcolor="#F0F8FF",
        alignment=ft.alignment.center,
        content=requirements_container
    )

    page.clean()
    page.add(loading_screen)
    page.update()

    status_text = requirements_container.content.controls[2]
    progress_bar = requirements_container.content.controls[1]
    loading_ring = requirements_container.content.controls[3]

    # Check database
    status_text.value = "Verificando banco de dados..."
    progress_bar.value = 0.3
    page.update()
    sleep(1)

    # Check storage
    status_text.value = "Verificando armazenamento..."
    progress_bar.value = 0.6
    page.update()
    sleep(1)

    # Check dependencies
    status_text.value = "Verificando dependências..."
    progress_bar.value = 0.9
    page.update()
    sleep(1)

    # All checks passed
    status_text.value = "Sistema pronto!"
    progress_bar.value = 1
    loading_ring.visible = False
    page.update()
    sleep(0.5)

    # Clear page and proceed to login
    page.clean()
    if(is_logged()):
        page.add(body_config)
    else:
        page.add(login_page)
    page.update()

def main(page: ft.Page):
    page.title="PDV Niassa"
    page.title="Ponto de venda - JP Invest"
    page.theme_mode=ft.ThemeMode.LIGHT
    page.padding=0
    page.window.full_screen=True
    altura=page.window.height+150
    global hora,banco,selected_item_id

    def chage_nav2(e):
        selected_index=e.control.selected_index
        nav_rail.selected_index=None

        if selected_index == 0:
            if(get_logged_user()['cargo'])=='admin':
                body.content = SettingsPage(pagex=page)
                page.update()
            else:
                page.open(ft.AlertDialog(title=ft.Text("Aviso"),content=ft.Row([
                    ft.Icon(ft.Icons.INFO,color=ft.Colors.RED_600),
                    ft.Text("Nao tens Permicao para acessar nas difinicoes")
                ])))
            page.update()
        
        elif selected_index == 1:
            page.clean()
            page.floating_action_button=None
            clear_logout()
            page.add(login_page)
        
    def chage_nav(e):
        selected_index = e.control.selected_index
        bottom_nav.selected_index = None

        if selected_index == 0:
            update_mesas_dropdown()  # Atualiza as mesas ao voltar para a página principal
            body.content = ft.Container(
                bgcolor="#F0F8FF",  # Light blue-white background
                content=ft.Column(
                    [
                        ft.Row(
                            controls=[
                                ft.Container(
                                    expand=True,
                                    height=altura,
                                    padding=14,
                                    content=ft.Column(controls=[
                                        ft.Container(
                                            padding=10,
                                            border_radius=10,
                                            bgcolor="white",
                                            content=ft.Row(
                                                controls=[
                                                    ft.Text(info['app'],size=30,weight="bold",color=ft.Colors.INDIGO_400),
                                                    search_categoria,
                                                    search
                                                ],
                                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                            )
                                        ),
                                        items_menu
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
                                                horas,
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
                                                    clientes,
                                                    mesa,
                                                    ft.CupertinoButton("Abrir Gaveta",bgcolor=ft.Colors.INDIGO_300,on_click=lambda e:abrir_gaveta())
                                                ])
                                            )
                                        ),
                                        ft.Stack(
                                            width=260,
                                            height=650,
                                            controls=[
                                                lista_vendas,
                                                ft.Card(
                                                    width=235,
                                                    bottom=300,
                                                    content=ft.Container(
                                                        padding=10,
                                                        content=ft.Column(controls=[total_text])
                                                    )
                                                )
                                            ]
                                        )
                                    ])
                                )
                            ]
                        )
                    ]
                )
            )
            update_menu()
            page.update()
        elif selected_index == 1:
            # Página de produtos - usando a classe ProductsPage
            body.content = ProductsPage(page, update_menu)
            page.update()
        elif selected_index == 2:
            # Página de estoque - usando a classe EstoquePage
            body.content = EstoquePage(page)
            page.update()
        elif selected_index == 3:
            # Página de finanças - usando a classe MoneyPage
            body.content = MoneyPage(page)
            page.update()
        elif selected_index == 4:
            # Página de mesas - usando a classe TablesPage
            body.content = TablesPage(page)
            page.update()
        elif selected_index == 5:
            # Página de relatórios - usando a classe RelatorioPage
            body.content = RelatorioPage(page)
            update_mesas_dropdown()  # Atualiza as mesas após possíveis alterações na página de mesas
            page.update()
        else:
            page.clean()
            page.floating_action_button=None
            clear_logout()
            page.add(login_page)
                
    #capturar eventos de scanner
    def on_key(event):
        global codigo_barras 
        if event.key.isdigit():  
            codigo_barras += event.key 
        elif event.key == 'Enter': 
            adicionar_Carinho_barCode(codigo_barras)
            codigo_barras = ""  

    def update_time():
        global hora 
        current_date = datetime.now()
        hora=current_date.strftime("%H:%M:%S")
        horas.content=ft.Row(controls=[
                                ft.Text("Horas:",size=15),
                                ft.Text(hora,size=15),    
                            ])
        page.update()

    categoria_lista = getCategorias()

    categoria = ft.Dropdown(
        label="Categoria",
        options=[ft.dropdown.Option(categoria.nome) for categoria in categoria_lista]
    )
            
    global ultima_venda
  
    def serialize_user(user):
        global caixa
        caixa=user.nome
        return {
            'id': user.id,
            'nome': user.nome,
            'cargo': user.cargo,
            'username': user.username,
            'senha':user.senha   
        }

    imagens=os.path.join(os.getenv("LOCALAPPDATA"), ".jpInvest/img")
    
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
    page.overlay.append(file_picker)
    usname=ft.TextField(label="Nome do usuario")
    uspass=ft.TextField(label="Senha do Usuario")
    
    def entrar(e):
        global username,caixa
        result = StartLogin(username, login_input.value)
        if(result != False):
            update_menu()
            update_mesas_dropdown()
            card.content = choice_perfil
            
            username=e.control.key
            login_perfil.offset = ft.transform.Offset(0, 0)
            login_input.value=''
            
            if not userLoged() or userLoged==None:
                set_logged(True,serialize_user(result))
            else:
                clear_logout()
            

            page.controls.clear()
            page.update()
            body.content=ft.Container(
                bgcolor="#F0F8FF",  # Light blue-white background
                content=ft.Column([
                    ft.Row(
                        controls=[
                            ft.Container(
                                expand=True,
                                height=altura,
                                padding=14,
                                content=ft.Column(controls=[
                                    ft.Container(
                                        padding=10,
                                        border_radius=10,
                                        bgcolor="white",
                                        content=ft.Row(
                                            controls=[
                                                ft.Text(info['app'],size=30,weight="bold",color=ft.Colors.INDIGO_400),
                                                search_categoria,
                                                search
                                            ],
                                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                        )
                                    ),
                                    items_menu
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
                                            horas,
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
                                                clientes,
                                                mesa,
                                                ft.CupertinoButton("Abrir Gaveta",bgcolor=ft.Colors.INDIGO_300,on_click=lambda e:abrir_gaveta())
                                            ])
                                        )
                                    ),
                                    ft.Stack(
                                        width=260,
                                        height=650,
                                        controls=[
                                            lista_vendas,
                                            ft.Card(
                                                width=235,
                                                bottom=300,
                                                content=ft.Container(
                                                    padding=10,
                                                    content=ft.Column(controls=[total_text])
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
        
            page.add(body_config) 
    
        else:
            page.open(ft.AlertDialog(title=ft.Text("Senha errada"),content=ft.Row(controls=[
                ft.Icon(name=ft.Icons.INFO,color=ft.Colors.RED_600),
                ft.Text("A sua senha esta incorreta,\n fale com admin",weight="bold")
            ])))    
        usname.value=""
        uspass.value=""
        page.update()
            

    header=ft.Row(
        [ft.Container(content=ft.Text(info['app'],weight='bold',size=50,color=ft.Colors.INDIGO_400))]
        ,alignment=ft.MainAxisAlignment.CENTER,
        )
    def hovercard(e):
        if e.data == "true":  # mouse entra
            e.control.bgcolor='#fcf9d9'
        else: 
            e.control.bgcolor='#fefce8'
        page.update()
    perfiles=ft.Row(alignment=ft.MainAxisAlignment.CENTER)

    def enter(e):
        global username,caixa
        import re
        
        username=re.split("=",e.control.key)[0]
        caixa=re.split("=",e.control.key)[1]
        
        card.content=login_perfil
        login_perfil.offset = ft.transform.Offset(0, 0)
        page.update()

    choice_perfil=ft.Column(
        [ft.Row([ft.Text("Escolha o seu perfil")]),
         perfiles
        ]
    )

    def clear(e):
        login_input.value=''
        page.update()

    def write(e):
        if(e.control.text!='<'):
            holdtext=login_input.value
            newtext=holdtext+e.control.text
            login_input.value=newtext
        else:
            holdtext=login_input.value
            login_input.value = holdtext[:-1]
            
        page.update()
    
    def write_payment(e):
        global total_valor

        troco=0
        if valor_pagar.disabled:
            pass
        else:
            if(e.control.text!='<'):
                holdtext=valor_pagar.value
                newtext=holdtext+e.control.text
                valor_pagar.value=newtext
            else:
                holdtext=valor_pagar.value
                valor_pagar.value = holdtext[:-1]

            recebido=valor_pagar.value
            total = getTotalMoneyCart(carrinho_s)  
            total_valor=total
            iva = round(total * iva_p)  
            subtotal = subtotal = round(total - iva, 2)
            try:
                if int(recebido)>total:
                    troco=int(recebido)-total
                    trocoView.value=f"O troco e de: {troco},00 MT"
                elif int(recebido)<total:
                    resta=total-int(recebido)
                    trocoView.value=f"falta: {resta},00 MT"
                elif int(recebido)==total:
                    trocoView.value=f"sem troco"
                else:
                    trocoView.value=f"occoreu um erro"
            except:
                print("input is not int")
            global ultima_venda
            ultima_venda={
                'data':f"{day} - {hora}",
                'produtos':carrinho_s,
                'subtotal':subtotal,
                'iva':iva,
                'total':total, 
                'cliente':f"{clientes.value} {mesa.value}",
                'troco':troco,
                'metodo':f"{pagamento.value}",
                'entregue':f"{valor_pagar.value} "
            }
            
            page.update()

    def write_payment2(e):
        global total_valor
        troco=0

        recebido=valor_pagar.value
        total = getTotalMoneyCart(carrinho_s)  
        total_valor=total
        iva = total * 0.16  # 16% do total
        subtotal = total - iva  # Subtotal é o total menos o IVA
        try:
            if int(recebido)>total:
                troco=int(recebido)-total
                trocoView.value=f"O troco e de: {troco},00 MT"
            elif int(recebido)<total:
                resta=total-int(recebido)
                trocoView.value=f"falta: {resta},00 MT"
            elif int(recebido)==total:
                trocoView.value=f"sem troco"
            else:
                trocoView.value=f"occoreu um erro"
        except:
            print("input is not int")
        global ultima_venda
        ultima_venda={
            'data':f"{day} - {hora}",
            'produtos':carrinho_s,
            'subtotal':subtotal,
            'iva':iva,
            'total':total,
            'cliente':f"{clientes.value} {mesa.value}",
            'troco':troco,
            'metodo':f"{pagamento.value}",
            'entregue':f"{valor_pagar.value} "
        }
       
        page.update()
    keyboard=ft.Column([
        ft.Row([
        ft.ElevatedButton(text="1",on_click=write),
        ft.ElevatedButton(text="2",on_click=write),
        ft.ElevatedButton(text="3",on_click=write),
        ]),
        ft.Row([
        ft.ElevatedButton(text="4",on_click=write),
        ft.ElevatedButton(text="5",on_click=write),
        ft.ElevatedButton(text="6",on_click=write),
        ]),
        ft.Row([
        ft.ElevatedButton(text="7",on_click=write),
        ft.ElevatedButton(text="8",on_click=write),
        ft.ElevatedButton(text="9",on_click=write),
        ]),
        ft.Row([
        ft.ElevatedButton(text="<",on_click=write,on_long_press=clear),
        ft.ElevatedButton(text="0",on_click=write),
        ft.ElevatedButton(text="ok",on_click=entrar),
        ])
    ])
    nome_do_cliente = ft.Text(value="",size=30,weight="bold")

    carrinho_show=ft.AlertDialog(title=ft.Text("Produtos escolhidos"))

    def show_carrinho(e):
        carrinho_show.content=ft.Container(width=600,height=400,padding=10,content=lista_vendas)
        page.open(carrinho_show)
    def fechar_contas(e):
        global ultima_venda,carrinho_s,total_valor
        id = e.control.key
        nome_clinte=e.control.bgcolor
        clientes.value=nome_clinte
        venda = Venda(ContaInfoToVenda(id), f"{day} - {hora}", f"{hora}",nome_clinte,"Dinheiro")
        ultima_venda=venda.pedidos_para_venda()
        carrinho_s=ultima_venda['produtos']
        total_text.controls.clear()
        total = getTotalMoneyCart(carrinho_s)  # Exemplo: 1000 MZN
        total_valor=total

        iva = total * 0.16  # 16% do total
        subtotal = total - iva  # Subtotal é o total menos o IVA
        total_text.controls.append(ft.Column(controls=[
            ft.Text(f"Subtotal: {subtotal} MT", size=17),
            ft.Text(f"IVA: {round(iva,2)} MT", size=17), 
            ft.Text(f"Total: {total_valor} MT", size=17),
            ft.Row(controls=[
                ft.IconButton(icon=ft.Icons.DELETE, on_click=limpar,icon_color=ft.Colors.INDIGO_400),
                ft.IconButton(icon=ft.Icons.LIST, on_click=addcontas,),
                ft.IconButton(icon=ft.Icons.CHECK, on_click=guardar),
                ft.IconButton(icon=ft.Icons.VISIBILITY, on_click=show_carrinho),
                
                
            ])
        ]))
        lista_vendas.controls.clear()
        for i, item in enumerate(carrinho_s):
            lista_vendas.controls.append(ft.Container(
                padding=8,
                height=80,
                content=ft.Card(content=ft.Row(
                    controls=[
                        ft.Image(src=f'{imagens}/{item['image']}', width=40, height=40, border_radius=8),
                        ft.Text(item['nome']),
                        ft.Row(controls=[ft.Text(f"{item['preco']} MT", size=8)]),
                        ft.Text(f"Qtd: {item['quantidade']}"),  ft.PopupMenuButton(items=[
                            ft.PopupMenuItem(text="diminuir",on_click=decrement_item, icon=item['id']),
                            ft.PopupMenuItem(text="Deletar",on_click=delete_item, icon=i),

                        ])
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ))
            ))
        page.update()
        guardar()
        #Eliminar a Conta
        user=db.query(ContasAbertas).filter_by(id=id).first()
        db.delete(user)
        db.commit()
        update_contas_list()
        contas.append(ft.dropdown.Option("Sem Nome"))
        contas.clear()
        for conta in getContas():
            contas.append(ft.dropdown.Option(conta.cliente))
        page.update()

    def deletar_contas(e):
        id = e.control.key
        conta = db.query(ContasAbertas).filter_by(id=id).first()
        if conta:
            db.delete(conta)
            db.commit()
            print(f"Conta deletada: {conta.cliente}")
        
        # Atualizando a lista de contas
        update_contas_list()
    def update_contas_list():
        # Limpar as linhas da tabela antes de adicionar novas
        tabela_contas.rows.clear()
        # Adicionar as contas atualizadas na tabela
        for conta in getContas():
            tabela_contas.rows.append(ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(conta.cliente)),
                    ft.DataCell(ft.Text(str(len(conta.produtos)))),
                    ft.DataCell(ft.Row([
                        ft.ElevatedButton("fechar",on_click=fechar_contas,key=conta.id,bgcolor=conta.cliente),
                        ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.INDIGO_400, key=conta.id, on_click=deletar_contas)
                    ])),
                ],
            ))
        
        # Atualizando a página com as mudanças
        page.update()

    def mudar(e=""):
        user = db.query(ContasAbertas).filter_by(cliente=clientes.value).first()
        cliente_row.content=ft.Text()
        cliente_info.content=ft.Text()
        if user:
            userInfo=ContaInfo(user.id)
            cliente_info.content=ft.Column([
                ft.Row([
                    ft.Text("Total de produtos:"),ft.Text(userInfo['total_produtos'],size=16,weight="bold")
                ]),
                ft.Row([
                    ft.Text("Total de pedidos:"),ft.Text(userInfo['total_pedidos'],size=16,weight="bold")
                ]),
                ft.Row([
                    ft.Text("Total em dinheiro:"),ft.Text(userInfo['total_dinheiro'],size=16,weight="bold")
                ])
            ])
        nome_do_cliente.value = f"Cliente/Mesa: {clientes.value}"
        page.update()

    clientes=ft.Dropdown()
    contas=[]
    contas.append(ft.dropdown.Option("Sem Nome"))
    for conta in getContas():
        contas.append(ft.dropdown.Option(conta.cliente))

    clientes = ft.Dropdown(
        label="Escolher o cliente",
        options=contas,
        on_change=mudar  # Usa on_change para capturar a seleção
    )
    

    
    cliente_row=ft.Container()
    def adicionar_contas(e):
        addConta(input_cliente.value)
        clientes.value=input_cliente.value
        mudar(clientes)
        ct=getContas()
        contas.clear()
        input_cliente.value=""
        cliente_row.content=ft.Row([
        ])
        contas.append(ft.dropdown.Option("Sem Nome"))
        page.update()
        for conta in ct:
            contas.append(ft.dropdown.Option(conta.cliente))
        clientes.options=contas
        update_contas_list()
        page.update()

    input_cliente=ft.TextField(label="Nome do cliente/mesa")
    def novo_cliente(e):
        cliente_row.content=ft.Row([
            input_cliente,
            ft.ElevatedButton("adicionar",on_click=adicionar_contas)
        ])
        page.update()
    

    def adicionarItem(e):
        try:
            ms=db.query(ContasAbertas).filter_by(cliente=clientes.value).first()
            if len(carrinho_s)>=1:
                addItemConta(carrinho_s,ms.id)
                mudar()
                update_contas_list()
            else:
                cliente_row.content=ft.Text("O cliente nao tem nenhum pedido",color=ft.Colors.INDIGO_400,weight="bold")        
        except:
            cliente_row.content=ft.Text("Crie um cliente primeiro",color=ft.Colors.INDIGO_400,weight="bold")
        page.update()
    tabela_contas=ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nome")),
                ft.DataColumn(ft.Text("total de pedidos")),
                ft.DataColumn(ft.Text("accoes"), numeric=True),
            ],height=500)
    cliente_info=ft.Container()   
    dialog_contas=ft.AlertDialog(title=ft.Text("Contas"),content=ft.Column(height=400,width=500,controls=[
        ft.Row([clientes,ft.Container(content=ft.FloatingActionButton(icon=ft.Icons.ADD,on_click=novo_cliente))]),
        ft.Tabs(
        selected_index=1,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="inicio",
                content=ft.Container(padding=10,
                    content=ft.Column([
                        cliente_row,
                        nome_do_cliente,
                        cliente_info,
                        ft.Row([ft.ElevatedButton('Adicionar items',on_click=adicionarItem),ft.ElevatedButton('Fechar A Conta')])
                    ])
                ),
            ),
            
            ft.Tab(
                text="Contas Abertas",
                content=ft.Container(height=400,
                    content=ft.Column([tabela_contas],scroll=True,height=400)
                ),
            ),
        ],
        expand=1,
    ),
        
    ]))

    def addcontas(e):
        """
        uma funcao de gestao de contas
        """
        update_contas_list()
        page.open(dialog_contas)
        

    def finalizar(e=''):
        global carrinho
        global preco_total
        global carrinho_s
        
        for p in carrinho:
            preco_total+=p.preco
        
        if(len(carrinho_s)>=1):
            if (float(valor_pagar.value))<getTotalMoneyCart(carrinho_s):
                d=ft.AlertDialog(title=ft.Text("Aviso"),content=ft.Text("Nao pode Concluir o valor e \n menor que o Total"))
                d.actions=[ft.TextButton("Fechar",on_click=lambda e:page.close(d))]
                page.open(d)
                return
            if(getRelatorioUnico(day)):
        
                venda=ProdutoVenda(
                data=datetime.now(),
                hora=current_date.strftime("%H:%M:%S"),
                produtos=carrinho_s,
                total_item=quantidade_item,
                total_money=preco_total,
                relatorio_id=getRelatorioUnico(day).id,
                cliente=clientes.value,
                funcionario=get_logged_user()['nome'],
                metodo=pagamento.value)
                trocoView.value=""
                page.update()
                if(checkCartStock(carrinho_s)['resultado']):
                    addVenda(venda)
                    deduceStockCart(carrinho_s,getRelatorioUnico(day).id)
                    limpar()
                    update_menu()
                    show_resumo()
                else:
                    page.open(ft.AlertDialog(title=ft.Text("Aviso"),content=ft.Row([
                        ft.Icon(ft.Icons.INFO,color=ft.Colors.INDIGO_400),
                        ft.Text(f"O estoque do produto {checkCartStock(carrinho_s)['produto']} \nnao e suficiente para terminar o processo")
                    ])))

            else:
                page.open(relatorio_alert)
                
        
    keyboard2=ft.Column([
        ft.Row([
        ft.ElevatedButton(text="1",on_click=write_payment,scale=1.2),
        ft.ElevatedButton(text="2",on_click=write_payment,scale=1.2),
        ft.ElevatedButton(text="3",on_click=write_payment,scale=1.2),
        ],alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ,ft.Row([
        ft.ElevatedButton(text="4",on_click=write_payment,scale=1.2),
        ft.ElevatedButton(text="5",on_click=write_payment,scale=1.2),
        ft.ElevatedButton(text="6",on_click=write_payment,scale=1.2),
        ],alignment=ft.MainAxisAlignment.SPACE_BETWEEN,spacing=5),
        ft.Row([
        ft.ElevatedButton(text="7",on_click=write_payment,scale=1.2),
        ft.ElevatedButton(text="8",on_click=write_payment,scale=1.2),
        ft.ElevatedButton(text="9",on_click=write_payment,scale=1.2),
        ],alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Row([
        ft.ElevatedButton(text="<",on_click=write_payment,scale=1.2,on_long_press=clear),
        ft.ElevatedButton(text="0",on_click=write_payment,scale=1.2),
        ft.ElevatedButton(text="ok",on_click=finalizar,scale=1.2),
        ],alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    ])

    login_input=ft.TextField(label='Digite a sua senha')
    login=ft.Row(alignment=ft.MainAxisAlignment.CENTER,controls=[
        ft.Image(src='image.png',width=300,height=300,border_radius=10),
        ft.Column([
            login_input
            ,
            keyboard
        ],expand=True)
    ])
    def back_to_perfil(e):
        card.content=choice_perfil
        page.update()
    login_label=ft.Row([ft.IconButton(icon=ft.Icons.ARROW_BACK,on_click=back_to_perfil),ft.Text(f"Dgite o seu pin")])
    login_perfil=ft.Column(
        [login_label,
         login

        ])

    for i in todosUsers():
        user = f"{i.username}={i.nome}"
        perfiles.controls.append(
            ft.Container(height=200,width=200,bgcolor='#fefce8',border_radius=10,
                          content=ft.Column([
                        
                        ft.Row([ft.Image(src='image.png',width=100,height=100)],alignment=ft.MainAxisAlignment.CENTER),
                        ft.Row([ft.Text(i.nome,weight='bold')],alignment=ft.MainAxisAlignment.CENTER)
             ]),alignment=ft.alignment.center,padding=20,on_hover=hovercard,on_click=enter,key=user,)
        )

    card=ft.Container(padding=10,content=choice_perfil,
         bgcolor=ft.Colors.INDIGO_100,border_radius=10
        )
    login_page=ft.Container(
        content=ft.Column(
            controls=[header,
                      ft.Row([card],
                             alignment=ft.MainAxisAlignment.CENTER),
                            ft.Row([ft.CupertinoButton(text="Fechar",bgcolor=ft.Colors.INDIGO_400,on_click=lambda e:page.window.close())],
                        alignment=ft.MainAxisAlignment.CENTER)],
                        expand=1,
                        alignment=ft.MainAxisAlignment.CENTER
                    ),bgcolor='#fefce8',expand=True)

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
            
    def fecha(e):
        dialogo.open=False
        page.update()
    
    def close_modal(e):
        page.close(relatorio_alert)
    relatorio_alert=ft.AlertDialog(title=ft.Text("Sem Relatorio"),content=ft.Text("Nao tem um Relatorio diario para Hoje! Voce deseja criar?"),actions=[
        ft.TextButton('Cancelar',on_click=close_modal),
        ft.ElevatedButton("Criar Relatorio",on_click=novo_relatorio)
    ])
    
    def ch(e):
        global ultima_venda,total_valor
        ultima_venda['metodo']=e.control.value
        if e.control.value !="Cash":
            valor_pagar.value=total_valor
            valor_pagar.disabled=True
        else:
            valor_pagar.disabled=False

    pagamento=ft.Dropdown(label="metodo de pagamento",
                    options=[ft.dropdown.Option("Cash"),
                             ft.dropdown.Option("MPesa"),
                             ft.dropdown.Option("POS BCI"),
                             ft.dropdown.Option("E-mola")
                             ],on_change=ch)

    dialogo=ft.AlertDialog(title=ft.Text("PDV LITE"),
                           content=ft.Text("So pode criar um Relatorios por dia"),
                           actions=[
                               ft.TextButton('intendi',on_click=fecha)
                           ] )

    valor_pagar=ft.TextField(label="valor recebido",on_change=write_payment2)
    trocoView=ft.Text(weight='bold',size=24,col=ft.Colors.INDIGO_400)
    
    def close_show(e):
        page.close(resumo_venda)
    pagament=ft.AlertDialog(title=ft.Text("Pagamento"),content=ft.Container(width=300,height=340,content=ft.Column([
        pagamento,valor_pagar,trocoView,keyboard2
    ])))
    def guardar(e=''):
        pagamento.value="Cash"
        global ultima_venda
        print(ultima_venda)
        valor_pagar.value=''
        page.open(pagament)
    def imprimir_fatuta(e):
        print_receipt(ultima_venda)
        page.close(resumo_venda)

    resumo_venda=ft.AlertDialog(title=ft.Text('Resumo da Venda'),actions=[
        ft.TextButton('Cancelar',on_click=close_show),
        ft.ElevatedButton("imprimir",bgcolor=ft.Colors.INDIGO_400,color='white',on_click=imprimir_fatuta)
    ])
    
    def show_resumo():
        dado=formatar_dados(ultima_venda)
        resumo_venda.content=ft.Text(dado)
        valor_pagar.value=''
        pagamento.value="Cash"
        page.open(resumo_venda)
        
    def limpar(e=''):
        global carrinho
        global quantidade_item
        global carrinho_s
        carrinho_s=[]
        carrinho=[]
        quantidade_item=0
        total_text.controls.clear()
        total_text.controls.append(ft.Column(controls=[
                ft.Text(f"Subtotal: 0.0 MT", size=17),
                ft.Text(f"IVA: 0.0 MT", size=17), 
                ft.Text(f"Total : 0.0 MT", size=17),
                ft.Row(controls=[
                    ft.IconButton(icon=ft.Icons.DELETE, on_click=limpar,icon_color=ft.Colors.INDIGO_400),
                    ft.IconButton(icon=ft.Icons.LIST, on_click=addcontas,),
                    ft.IconButton(icon=ft.Icons.CHECK, on_click=guardar),
                    ft.IconButton(icon=ft.Icons.VISIBILITY, on_click=show_carrinho),
                ])
            ]))
        lista_vendas.controls.clear()
        page.update()

    ####################################################### NAVBAR #############################################################
    if(CheckIsLoged()==True):
        pass
    total_text=ft.Column(controls=[
        ft.Column(controls=[
                ft.Text(f"Subtotal: 0.0 MT", size=17),
                ft.Text(f"IVA: 0.0 MT", size=17), 
                ft.Text(f"Total : 0.0 MT", size=17),

                ft.Row(controls=[
                    ft.IconButton(icon=ft.Icons.DELETE, on_click=limpar,icon_color=ft.Colors.INDIGO_400),
                    ft.IconButton(icon=ft.Icons.LIST, on_click=addcontas,),
                    ft.IconButton(icon=ft.Icons.CHECK, on_click=guardar),
                    ft.IconButton(icon=ft.Icons.VISIBILITY, on_click=show_carrinho),
                ])
            ])
    ])       
    dl_m=ft.AlertDialog(title=ft.Text('Adicionar Mais'),
                    content=ft.Column(controls=[

                    ]))
    quantidade=ft.TextField(label=f"Quantidade")
    def dl_more_carinho(e):
        prod=acharUmProduto(e.control.key)
        sub=ft.ElevatedButton(text="Adicionar",bgcolor=f'{prod.id}',on_click=adicionar_Carinho_m,key=e.control.key)
        dl_m.title=ft.Text(f'Edit Qtd:  {prod.titulo}')
        dl_m.content=ft.Column(height=200,controls=[
            quantidade,sub
        ])
        page.open(dl_m)
    
    def adicionar_Carinho_m(e):
        global quantidade_item
        id = e.control.key
        produto = acharUmProduto(id)
        quantidade_valor = int(quantidade.value)
        Existe = False

        # Verifica se o produto já está no carrinho_s
        for i in range(len(carrinho_s)):
            if str(carrinho_s[i]['id']) == id:
                # Aumenta a quantidade do item existente em carrinho_s
                carrinho_s[i]['quantidade'] += quantidade_valor  # Aumenta a quantidade
                carrinho_s[i]['total'] = carrinho_s[i]['quantidade'] * produto.preco  # Atualiza o total
                Existe = True
                # print("O Produto existe no carrinho, quantidade aumentada.")
                break

        if not Existe:
            # Se não existe, adiciona o novo produto ao carrinho
            carrinho.append(produto)  # Você ainda pode manter a referência ao produto
            carrinho_s.append(
                {
                    "id": produto.id, 
                    "barcode": produto.barcode,
                    "nome": produto.titulo,
                    "preco": produto.preco,
                    "categoria":produto.categoria,
                    "image": produto.image,
                    "quantidade": quantidade_valor,
                    "total": produto.preco * quantidade_valor,
                    
                }
            )

        lista_vendas.controls.clear()
        quantidade_item += quantidade_valor
        quantidade.value = ""
        total_text.controls.clear()

        total = getTotalMoneyCart(carrinho_s)  # Exemplo: 1000 MZN
        iva = total * 0.16  # 16% do total
        subtotal = total - iva  # Subtotal é o total menos o IVA
        global total_valor,ultima_venda
        total_valor=total
        ultima_venda={
            'data':f"{day} - {hora}",
            'produtos':carrinho_s,
            'subtotal':subtotal,
            'iva':iva,
            'total':total,
            'cliente':f"{clientes.value} {mesa.value}",
            'troco':0.0,
            'metodo':f"{pagamento.value}",
            'entregue':f"{valor_pagar.value} "
        }

        total_text.controls.append(ft.Column(controls=[
            ft.Text(f"Subtotal: {subtotal} MT", size=17),
            ft.Text(f"IVA: {round(iva,2)} MT", size=17), 
            ft.Text(f"Total: {total} MT", size=17),
            ft.Row(controls=[
                ft.IconButton(icon=ft.Icons.DELETE, on_click=limpar,icon_color=ft.Colors.INDIGO_400),
                ft.IconButton(icon=ft.Icons.LIST, on_click=addcontas,),
                ft.IconButton(icon=ft.Icons.CHECK, on_click=guardar),
                ft.IconButton(icon=ft.Icons.VISIBILITY, on_click=show_carrinho),
            ])
        ]))

        dl_m.open = False  # Fecha a lista de produtos, se aplicável

        for i, item in enumerate(carrinho_s):
            lista_vendas.controls.append(ft.Container(
                padding=8,
                height=80,
                content=ft.Card(content=ft.Row(
                    controls=[
                        ft.Image(src=f'{imagens}/{item['image']}', width=40, height=40, border_radius=8),
                        ft.Text(item['nome']),
                        ft.Row(controls=[ft.Text(f"{item['preco']} MT", size=8)]),
                        ft.Text(f"Qtd: {item['quantidade']}"),  # Atualiza a quantidade aqui
                        ft.PopupMenuButton(items=[
                            ft.PopupMenuItem(text="diminuir",on_click=decrement_item, icon=item['id']),
                            ft.PopupMenuItem(text="Deletar",on_click=delete_item, icon=i),

                        ])
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ))
            ))

        page.update()

    def delete_item(e):
        index=e.control.icon
        try:
            carrinho.pop(index)
        except:
            pass
        carrinho_s.pop(index)
        global quantidade_item
        quantidade_valor=1
        quantidade.value=1
        e.control.bgcolor="RED"
        lista_vendas.controls.clear()
        page.update()
        quantidade_item+=int(quantidade.value)
        quantidade.value=""
        total_text.controls.clear()
        total = getTotalMoneyCart(carrinho_s)  # Exemplo: 1000 MZN
        iva = total * 0.16  # 16% do total
        subtotal = total - iva  # Subtotal é o total menos o IVA
        total_text.controls.append(
            ft.Column(controls=[
                ft.Text(f"Subtotal: {subtotal} MT", size=17),
                ft.Text(f"IVA: {round(iva, 2)} MT", size=17), 
                ft.Text(f"Total: {total} MT", size=17),
                            ft.Row(controls=[
                ft.IconButton(icon=ft.Icons.DELETE, on_click=limpar, icon_color=ft.Colors.INDIGO_400),
                ft.IconButton(icon=ft.Icons.LIST, on_click=addcontas,),
                ft.IconButton(icon=ft.Icons.CHECK, on_click=guardar),
                ft.IconButton(icon=ft.Icons.VISIBILITY, on_click=show_carrinho),
            ])
        ]))
        for i, item in enumerate(carrinho_s):
            
            lista_vendas.controls.append(ft.Container(padding=8,height=80,
                    content=ft.Card(content=ft.Row(
                    controls=[
                        ft.Image(src=f'{imagens}/{item['image']}',width=40,height=40,border_radius=8),
                            ft.Row(controls=[
                                ft.Text(f"{item['preco']} MT",size=8)]),
                                ft.Text(f"Qtd: {quantidade_valor}"),
                                ft.PopupMenuButton(items=[
                            ft.PopupMenuItem(text="diminuir",on_click=decrement_item, icon=item['id']),
                            ft.PopupMenuItem(text="Deletar",on_click=delete_item, icon=i),

                        ])
                                
                                ],alignment=ft.MainAxisAlignment.SPACE_BETWEEN) 
                                )))
            
        page.update()

    def decrement_item(e):
        global carrinho_s, quantidade_item, total_valor
        id = e.control.icon  # ID do produto a ser decrementado
        Existe = False
        
        for i in range(len(carrinho_s)):
            if carrinho_s[i]['id'] == int(id) or carrinho_s[i]['barcode'] == int(id):
                # Verifica se a quantidade é maior que 1 para diminuir, caso contrário remove o item
                if carrinho_s[i]['quantidade'] > 1:
                    carrinho_s[i]['quantidade'] -= 1
                    carrinho_s[i]['total'] = carrinho_s[i]['quantidade'] * carrinho_s[i]['preco']  # Atualiza o total
                    print("Quantidade do produto no carrinho diminuída.")
                else:
                    carrinho_s.pop(i)  # Remove o item do carrinho se a quantidade for zero
                    print("Produto removido do carrinho.")
                Existe = True
                break

        # Atualiza o front-end após a mudança
        lista_vendas.controls.clear()
        total_text.controls.clear()
        
        # Calcula o subtotal e o total com o IVA
        total = getTotalMoneyCart(carrinho_s)
        iva = total * 0.16
        subtotal = total - iva
        
        # Atualiza os textos do total, subtotal e IVA
        total_text.controls.append(
            ft.Column(controls=[
                ft.Text(f"Subtotal: {subtotal} MT", size=17),
                ft.Text(f"IVA: {round(iva, 2)} MT", size=17), 
                ft.Text(f"Total: {total} MT", size=17),
                ft.Row(controls=[
                    ft.IconButton(icon=ft.Icons.DELETE, on_click=limpar, icon_color=ft.Colors.INDIGO_400),
                    ft.IconButton(icon=ft.Icons.LIST, on_click=addcontas),
                    ft.IconButton(icon=ft.Icons.CHECK, on_click=guardar),
                    ft.IconButton(icon=ft.Icons.VISIBILITY, on_click=show_carrinho),
                ])
            ])
        )

        # Adiciona os itens atualizados ao front-end
        for item in carrinho_s:
            lista_vendas.controls.append(
                ft.Container(
                    padding=8, height=80,
                    content=ft.Card(
                        content=ft.Row(
                            controls=[
                                ft.Image(src=f'{imagens}/{item['image']}', width=40, height=40, border_radius=8),
                                ft.Text(item['nome']),
                                ft.Text(f"{item['preco']} MT", size=8),
                                ft.Text(f"Qtd: {item['quantidade']}"),  # Exibe a quantidade correta
                                ft.PopupMenuButton(
                                    items=[
                                        ft.PopupMenuItem(text="Diminuir", on_click=decrement_item, icon=item['id']),
                                        ft.PopupMenuItem(text="Deletar",on_click=delete_item, icon=i),
                                    ]
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        )
                    )
                )
            )

        page.update()

        if not Existe:
            print("O produto não está no carrinho.")

    
                  
    def adicionar_Carinho(e):
        global quantidade_item,total_valor,ultima_venda
        
        id = e.control.key
        produto = produto = acharUmProduto(id)
        quantidade_valor = 1  # Pode ajustar conforme necessário
        quantidade.value = 1
        Existe = False
        e.control.bgcolor = "RED"


        for i in range(len(carrinho_s)):
            if str(carrinho_s[i]['id']) == id:
                # Aumenta a quantidade do item existente em carrinho_s
                carrinho_s[i]['quantidade'] += quantidade_valor
                carrinho_s[i]['total'] = carrinho_s[i]['quantidade'] * produto.preco  # Atualiza o total
                Existe = True
                # print("O Produto existe no carrinho, quantidade aumentada.")
                break

        if not Existe:
            # Se não existe, adiciona o novo produto ao carrinho
            carrinho.append(produto)  # Você ainda pode manter a referência ao produto
            carrinho_s.append(
                {
                    "id": produto.id, 
                    "barcode": produto.barcode,
                    "nome": produto.titulo,
                    "preco": produto.preco,
                    "categoria":produto.categoria,
                    "image": produto.image,
                    "quantidade": quantidade_valor,
                    "total": produto.preco * quantidade_valor,
                    
                }
            )

        lista_vendas.controls.clear()
        quantidade_item += quantidade_valor
        quantidade.value = ""
        total_text.controls.clear()

        total = getTotalMoneyCart(carrinho_s)  # Exemplo: 1000 MZN
        total_valor=total

        iva = total * 0.16  # 16% do total
        subtotal = total - iva  # Subtotal é o total menos o IVA
        ultima_venda={
            'data':f"{day} - {hora}",
            'produtos':carrinho_s,
            'subtotal':subtotal,
            'iva':iva,
            'total':total,
            'cliente':f"{clientes.value} {mesa.value}",
            'troco':0.0,
            'metodo':f"{pagamento.value}",
            'entregue':f"{valor_pagar.value} "
        }

        total_text.controls.append(ft.Column(controls=[
            ft.Text(f"Subtotal: {subtotal} MT", size=17),
            ft.Text(f"IVA: {round(iva,2)} MT", size=17), 
            ft.Text(f"Total: {total} MT", size=17),
            ft.Row(controls=[
                ft.IconButton(icon=ft.Icons.DELETE, on_click=limpar,icon_color=ft.Colors.INDIGO_400),
                ft.IconButton(icon=ft.Icons.LIST, on_click=addcontas,),
                ft.IconButton(icon=ft.Icons.CHECK, on_click=guardar),
                ft.IconButton(icon=ft.Icons.VISIBILITY, on_click=show_carrinho),
            ])
        ]))

        for i, item in enumerate(carrinho_s):
            lista_vendas.controls.append(ft.Container(
                padding=8,
                height=80,
                content=ft.Card(content=ft.Row(
                    controls=[
                        ft.Image(src=f'{imagens}/{item['image']}', width=40, height=40, border_radius=8),
                        ft.Text(item['nome']),
                        ft.Row(controls=[ft.Text(f"{item['preco']} MT", size=8)]),
                        ft.Text(f"Qtd: {item['quantidade']}"),
                        ft.PopupMenuButton(items=[
                            ft.PopupMenuItem(text="diminuir",on_click=decrement_item, icon=item['id']),
                            ft.PopupMenuItem(text="Deletar",on_click=delete_item, icon=i),

                        ])
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ))
            ))

        page.update()

    def adicionar_Carinho_barCode(barcode):
        global quantidade_item,total_valor,ultima_venda
        
        produto = acharUmProduto_barcode(barcode)
        if produto:
            quantidade_valor = 1  # Pode ajustar conforme necessário
            quantidade.value = 1
            Existe = False

            for i in range(len(carrinho_s)):
                if str(carrinho_s[i]['barcode']) == barcode:
                    # Aumenta a quantidade do item existente em carrinho_s
                    carrinho_s[i]['quantidade'] += quantidade_valor
                    carrinho_s[i]['total'] = carrinho_s[i]['quantidade'] * produto.preco  # Atualiza o total
                    Existe = True
                    # print("O Produto existe no carrinho, quantidade aumentada.")
                    break

            if not Existe:
                # Se não existe, adiciona o novo produto ao carrinho
                carrinho.append(produto)  # Você ainda pode manter a referência ao produto
                carrinho_s.append(
                    {
                        "id": produto.id,  
                        "barcode": produto.barcode,
                        "nome": produto.titulo,
                        "preco": produto.preco,
                        "categoria":produto.categoria,
                        "image": produto.image,
                        "quantidade": quantidade_valor,
                        "total": produto.preco * quantidade_valor,
                        
                    }
                )

            lista_vendas.controls.clear()
            quantidade_item += quantidade_valor
            quantidade.value = ""
            total_text.controls.clear()

            total = getTotalMoneyCart(carrinho_s)  # Exemplo: 1000 MZN
            total_valor=total

            iva = total * 0.16  # 16% do total
            subtotal = total - iva  # Subtotal é o total menos o IVA
            ultima_venda={
                'data':f"{day} - {hora}",
                'produtos':carrinho_s,
                'subtotal':subtotal,
                'iva':iva,
                'total':total,
                'cliente':f"{clientes.value} {mesa.value}",
                'troco':0.0,
                'metodo':f"{pagamento.value}",
                'entregue':f"{valor_pagar.value} "
            }

            total_text.controls.append(ft.Column(controls=[
                ft.Text(f"Subtotal: {subtotal} MT", size=17),
                ft.Text(f"IVA: {round(iva,2)} MT", size=17), 
                ft.Text(f"Total: {total} MT", size=17),
                ft.Row(controls=[
                    ft.IconButton(icon=ft.Icons.DELETE, on_click=limpar,icon_color=ft.Colors.INDIGO_400),
                    ft.IconButton(icon=ft.Icons.LIST, on_click=addcontas,),
                    ft.IconButton(icon=ft.Icons.CHECK, on_click=guardar),
                    ft.IconButton(icon=ft.Icons.VISIBILITY, on_click=show_carrinho),
                ])
            ]))

            for i, item in enumerate(carrinho_s):
                lista_vendas.controls.append(ft.Container(
                    padding=8,
                    height=80,
                    content=ft.Card(content=ft.Row(
                        controls=[
                            ft.Image(src=f'{imagens}/{item['image']}', width=40, height=40, border_radius=8),
                            ft.Text(item['nome']),
                            ft.Row(controls=[ft.Text(f"{item['preco']} MT", size=8)]),
                            ft.Text(f"Qtd: {item['quantidade']}"),  # Atualiza a quantidade aqui
                            ft.PopupMenuButton(items=[
                                ft.PopupMenuItem(text="diminuir",on_click=decrement_item, icon=item['id']),
                                ft.PopupMenuItem(text="Deletar",on_click=delete_item, icon=i),

                            ])
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ))
                ))

            page.update()
            
    def submit(e):
        items_menu.controls.clear()
        page.update()
        if e.control.value=="Todos os Produtos":
            for i in verProdutos():
           
                items_menu.controls.append(
                                ft.Card(width=130,height=180,
                                    content=ft.Container(padding=7,
                                        content=ft.Column([
                                            ft.Image(f'{imagens}/{i.image}',border_radius=10,height=80,fit=ft.ImageFit.COVER,width=page.window.width / 3),
                                            ft.Text(i.titulo,weight="bold",size=13),
                                            ft.Text(f'{i.preco} MZN',weight="bold",size=13,color=ft.Colors.INDIGO_400)
                                        ])
                                        ,on_hover=hovercard,on_click=adicionar_Carinho,on_long_press=dl_more_carinho,key=f'{i.id}')),) 
        else:
            for i in pesquisaProduto(e.control.value):
                items_menu.controls.append(
                                ft.Card(width=130,height=180,
                                    content=ft.Container(padding=7,
                                        content=ft.Column([
                                            ft.Image(f'{imagens}/{i.image}',border_radius=10,height=80,fit=ft.ImageFit.COVER,width=page.window.width / 3),
                                            ft.Text(i.titulo,weight="bold",size=13),
                                            ft.Text(f'{i.preco} MZN',weight="bold",size=13,color=ft.Colors.INDIGO_400)
                                        ])
                                        ,on_hover=hovercard,on_click=adicionar_Carinho,on_long_press=dl_more_carinho,key=f'{i.id}')),) 
        page.update()
    
    def hovercard(e):
        if e.data == "true":  # mouse entra
            e.control.bgcolor='#fcf9d9'
            e.control.border_radius=10

        else: 
            e.control.bgcolor=''
        page.update()
    def update_menu():
        items_menu.controls.clear()
        page.update()
        for i in verProdutos():
           
            items_menu.controls.append(
                            ft.Card(width=130,height=180,
                                content=ft.Container(padding=7,
                                    content=ft.Column([
                                        ft.Image(f'{imagens}/{i.image}',border_radius=10,height=80,fit=ft.ImageFit.COVER,width=page.window.width / 3),
                                        ft.Text(i.titulo,weight="bold",size=13),
                                        ft.Text(f'{i.preco} MZN',weight="bold",size=13,color=ft.Colors.INDIGO_400)
                                    ])
                                    ,on_hover=hovercard,on_click=adicionar_Carinho,on_long_press=dl_more_carinho,key=f'{i.id}')),) 
        page.update()
    lista_vendas=ft.ListView(height=380)

    # items_menu=ft.GridView(max_extent=200,spacing=10,height=600,child_aspect_ratio=0.8)
    items_menu=ft.Row(wrap=True,scroll=True,height=altura-110)
    search_categoria = ft.Dropdown(
        label="Categoria",
        width=230,
        options=[ft.dropdown.Option(categoria.nome) for categoria in categoria_lista],
        on_change=submit
    )
    search=ft.TextField(label="Procurar Produto",border_radius=12,on_change=submit,width=200)
    
    update_menu()
    
    def update_mesas_dropdown():
        # Busca todas as mesas do banco de dados
        mesas_db = db.query(Mesa).order_by(Mesa.numero).all()
        
        # Cria as opções para o dropdown com indicadores visuais de status
        mesas_options = []
        for m in mesas_db:
            # Determina a cor baseada no status
            status_color = "🟢" if m.status == "livre" else "🔴" if m.status == "ocupada" else "🟠"
            mesas_options.append(ft.dropdown.Option(f"{status_color} Mesa {m.numero} ({m.status})"))
        
        # Adiciona a opção "Sem mesa" no início
        mesas_options.insert(0, ft.dropdown.Option("Sem mesa"))
        
        # Atualiza as opções do dropdown
        mesa.options = mesas_options
        page.update()
    
    mesa = ft.Dropdown(label="Mesa", options=[ft.dropdown.Option("Sem mesa")])
    # Carrega as mesas do banco de dados
    update_mesas_dropdown()

    # Criando o NavigationRail
    nav_rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=400,
        group_alignment=-0.9,
        leading=ft.Container(padding=5,
                             content=ft.Text("JP",weight="bold",color=ft.Colors.INDIGO_400,size=35),
    ),
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.HOME_OUTLINED),
                selected_icon=ft.Icon(ft.Icons.HOME,color=ft.Colors.INDIGO_400),
                label="Casa"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.WIDGETS),
                selected_icon=ft.Icon(ft.Icons.WIDGETS,color=ft.Colors.INDIGO_400),
                label="Produtos"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.INVENTORY),
                selected_icon=ft.Icon(ft.Icons.INVENTORY,color=ft.Colors.INDIGO_400),
                label="Estoque"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.MONETIZATION_ON),
                selected_icon=ft.Icon(ft.Icons.MONETIZATION_ON,color=ft.Colors.INDIGO_400),
                label="Saldo"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.TABLE_BAR),
                selected_icon=ft.Icon(ft.Icons.TABLE_BAR,color=ft.Colors.INDIGO_400),
                label="Mesas"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.TIMELINE_OUTLINED),
                selected_icon=ft.Icon(ft.Icons.TIMELINE,color=ft.Colors.INDIGO_400),
                label="Relatorios"
            ),
        ],
        on_change=chage_nav,
    )

    bottom_nav=ft.NavigationRail(height=130,width=100,destinations=[
        ft.NavigationRailDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icon(ft.Icons.SETTINGS,color=ft.Colors.INDIGO_400),
                label="Definicoes"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.LOGOUT_OUTLINED,
                selected_icon=ft.Icon(ft.Icons.LOGOUT,color=ft.Colors.INDIGO_400),
                label="Log out"
            ),

    ],on_change=chage_nav2)
    
    # Conteúdo inicial do corpo da página
    if CheckIsLoged():
        body = ft.Container(
            content=ft.Container(
                bgcolor="#F0F8FF",  # Light blue-white background
                content=ft.Column([
                    ft.Row(
                        controls=[
                            ft.Container(
                                expand=True,
                                height=altura,
                                padding=14,
                                content=ft.Column(controls=[
                                    ft.Container(
                                        padding=10,
                                        border_radius=10,
                                        bgcolor="white",
                                        content=ft.Row(
                                            controls=[
                                                ft.Text(info['app'],size=30,weight="bold",color=ft.Colors.INDIGO_400),
                                                search_categoria,
                                                search
                                            ],
                                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                        )
                                    ),
                                    items_menu
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
                                            horas,
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
                                                clientes,
                                                mesa,
                                                ft.CupertinoButton("Abrir Gaveta",bgcolor=ft.Colors.INDIGO_300,on_click=lambda e:abrir_gaveta())
                                            ])
                                        )
                                    ),
                                    ft.Stack(
                                        width=260,
                                        height=650,
                                        controls=[
                                            lista_vendas,
                                            ft.Card(
                                                width=235,
                                                bottom=300,
                                                content=ft.Container(
                                                    padding=10,
                                                    content=ft.Column(controls=[total_text])
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
    else:
        
        body = ft.Container(content=ft.Container(content=ft.Text("nao tava logado")))
     #bottom_nav,nav_rail
    body_config=ft.ResponsiveRow(
                [
                    ft.Container(col=1,content=ft.Column(controls=[
                        ft.Container(expand=1,content=nav_rail),ft.Container(height=200,padding=ft.padding.only(bottom=50),content=bottom_nav)
                    ])),
                    ft.Column([body], alignment=ft.MainAxisAlignment.START, col=11),
                ],
                expand=True,  
            )
    page.on_keyboard_event = on_key
    # Adicionando o NavigationRail ao layout da página
    if(CheckIsLoged()):
        page.add(body_config) 
    else:
        page.add(login_page)
    initialize_app(page, body_config, login_page)
    while True:
        try:
            update_time()
        except:
            page.window.close()
        sleep(10)
    
ft.app(target=main)