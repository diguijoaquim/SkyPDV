#Criado por Ghost 04- Diqui Joaquim 
import os
import shutil
import flet as ft
from controler import *
from models.modelos import ProdutoVenda
from datetime import datetime
from pdv2pdf import*
import logging
from time import sleep
from contasToVenda import Venda
from controler import ContaInfoToVenda
from sqlalchemy import asc
from local import *

os.environ["FLET_WS_MAX_MSG_SIZE"] = "8000000"

selected_file_path = None
logging.basicConfig(level=logging.INFO)
 

    
banco=isDataBase()

current_date = datetime.now()
quantidade_item=0
preco_total=0.00
carrinho = []
carrinho_s=[]
day = current_date.strftime("%d-%m-%Y")
hora=""
data_view="00-00-0000"
vendas_view=0
total_view=0.00
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


relatorios=ft.Column(controls=[
                ft.Text(f"Data: {data_view}"),
                ft.Text(f"Vendas: {vendas_view}"),
                ft.Text(f"Total: {total_view} MT")
                               ])
dlg_edit = ft.AlertDialog(
        title=ft.Text("Atualizar o Produto", size=24))
settingBody=ft.Container(content=ft.Row([]))
horas=ft.Container()
    
def main(page: ft.Page):
    page.title="PDV Niassa"
    page.title="Ponto de venda - JP Invest"
    page.theme_mode=ft.ThemeMode.LIGHT
    page.padding=0
    page.window.full_screen=True
    altura=page.window.height+150
    global hora,banco,selected_item_id
    def CheckIsLoged():
        return is_logged()
    
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

    def userLoged():
        try:
            user=db.query(Usuario).filter_by(username=get_logged_user()['username']).first()
            return user
        except:
            return None
    estoqueBody=ft.Container()

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

    def updateEstoquePage():
        historico=ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nome")),
                ft.DataColumn(ft.Text("Estoque Inicial"),numeric=True),
                ft.DataColumn(ft.Text("Entradas"), numeric=True),
                ft.DataColumn(ft.Text("saidas"), numeric=True),
                ft.DataColumn(ft.Text("Estoque Atual"), numeric=True),
            ],height=altura-100)
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
        card_historico=ft.Container(padding=10,content=ft.Column([
            ft.Row([
                ft.CupertinoButton("Ver Entradas",bgcolor=ft.Colors.ORANGE_600,on_click=Entradas),
                ft.CupertinoButton("Ver Saidas",bgcolor=ft.Colors.ORANGE_600,on_click=Saidas),
            ]),ft.Card(content=historico)
        ]))
        estoqueBody.content=card_historico
        body.content=estoqueBody
        page.update()
    def chage_nav2(e):
        selected_index=e.control.selected_index

        if selected_index == 1:
            if(get_logged_user()['cargo'])=='admin':
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
                ft.Text(get_logged_user()['username'],weight="bold")
                settingBody=ft.Container(content=ft.Column(controls=[
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
                body.content = settingBody
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
        selected_index=e.control.selected_index
        if selected_index == 0:
            body.content = ft.Container(
            bgcolor="#e1e0e0",
            content=ft.Column(
                [
                    ft.Row(
                        controls=[
                    
                    ft.Container(expand=True,height=altura,
                                padding=14,
                                content=ft.Column(controls=[
                        ft.Container(padding=10,border_radius=10,bgcolor="white",content=ft.Row(controls=[
                            ft.Text(info['app'],size=30,weight="bold",color=ft.Colors.RED_500),
                            search_categoria,
                            search
                        ],alignment=ft.MainAxisAlignment.SPACE_BETWEEN)),
                        items_menu
                    ])),
                    ft.Container(width=260,padding=10,bgcolor=ft.Colors.WHITE,content=ft.Column(controls=[
                        ft.Text("Resumo da Veda:",size=20,weight="bold",color=ft.Colors.RED_500),
                        ft.Container(padding=10,margin=10,content=ft.Column(controls=[
                            ft.Row(controls=[
                                    ft.Text("Data:",size=15),
                                    ft.Text(day,size=15)
                                ]),
                            horas,
                            ft.Row(controls=[
                                    ft.Text("Caixa:",size=15),
                                    ft.Text(userLoged().nome,size=15),    
                                ]),
                            
                        ])),
                        ft.Card(content=ft.Container(padding=10,
                                                    content=ft.Column([
                                                        clientes,mesa,ft.ElevatedButton("Abrir Gaveta",on_click=lambda e:abrir_gaveta()),
                                                        ]),)),
                        ft.Stack(width=260,height=650,controls=[
                        lista_vendas,
                        ft.Card(width=235,
                                bottom=300,
                                content=ft.Container(padding=10,content=ft.Column(controls=[
                                    total_text
                                    ])))
                                    ])
                                    ]))
                
                        ],)]))
            update_menu()
            page.update()
        elif selected_index == 1:
            body.content = relatoriosBody
            relatorio_update()
            page.update()
        elif selected_index == 2:
            update_produtos()


            produtos_table_itens.content=ft.Card(content=ft.Container(expand=True,padding=10,
                     content=ft.ResponsiveRow(controls=[
                        ft.Column(controls=[
                           ft.ResponsiveRow(controls=[
                            produtos
                           ])
                        ],scroll=ft.ScrollMode.AUTO,height=page.window.height-10)
                    ],)))
            
            
            body.content = produtoBody
            page.update()
        elif selected_index == 3:
            updateEstoquePage()
        else:
            page.clean()
            page.floating_action_button=None
            clear_logout()
            page.add(login_page)
            

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
    select_button = ft.ElevatedButton(text="Selecionar Foto", on_click=lambda _: file_picker.pick_files(allow_multiple=False))
    usname=ft.TextField(label="Nome do usuario")
    uspass=ft.TextField(label="Senha do Usuario")
    vendas=ft.ListView(height=500)
    def entrar(e):
        global username,caixa
        result=StartLogin(username,login_input.value)
        if(result != False):
            update_menu()
    
            page.client_storage.set("loged",True)
            card.content=choice_perfil
            page.floating_action_button=ft.FloatingActionButton(
                        icon=ft.Icons.ADD, on_click=add_item
                    )
            username=e.control.key
            login_perfil.offset = ft.transform.Offset(0, 0)
            login_input.value=''
            
            if not userLoged() or userLoged==None:
                set_logged(True,serialize_user(result))
            else:
                clear_logout()
            

            page.controls.clear()
            page.update()
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
        [ft.Container(content=ft.Text(info['app'],weight='bold',size=50,color=ft.Colors.RED_500))]
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

        ])
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
    keyboard=ft.Column([
        ft.Row([
        ft.ElevatedButton(text="1",on_click=write),
        ft.ElevatedButton(text="2",on_click=write),
        ft.ElevatedButton(text="3",on_click=write),
        ])
        ,ft.Row([
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
                ft.IconButton(icon=ft.Icons.DELETE, on_click=limpar,icon_color="red"),
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
                        ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.RED_600, key=conta.id, on_click=deletar_contas)
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
                cliente_row.content=ft.Text("O cliente nao tem nenhum pedido",color=ft.Colors.RED_400,weight="bold")

            
        except:
            cliente_row.content=ft.Text("Crie um cliente primeiro",color=ft.Colors.RED_400,weight="bold")
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
                        ft.Icon(ft.Icons.INFO,color=ft.Colors.RED_500),
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
         bgcolor=ft.Colors.RED_100,border_radius=10
        )
    login_page=ft.Container(
        content=ft.Column(
            controls=[header,
                      ft.Row([card],
                             alignment=ft.MainAxisAlignment.CENTER),
                            ft.Row([ft.CupertinoButton(text="Fechar",bgcolor=ft.Colors.RED_400,on_click=lambda e:page.window.close())],
                        alignment=ft.MainAxisAlignment.CENTER)],
                        expand=1,
                        alignment=ft.MainAxisAlignment.CENTER
                    ),bgcolor='#fefce8',expand=True)
        
    
    

    #CriarTabelas()
    def fechar_relatorio(e):
        # Tente recuperar o relatório do dia especificado
        relatorio = db.query(RelatorioVenda).filter_by(nome=f"relatorio{day}").first()

        if relatorio:
            # Recupera o estoque atual de todos os produtos
            estoque_atual = db.query(Produto).all()
            estoque_dicionario = {produto.titulo: produto.estoque for produto in estoque_atual}

            # Certifique-se de que `entrada` seja uma lista de dicionários
            if isinstance(relatorio.entrada, str):
                try:
                    entrada = json.loads(relatorio.entrada)
                except json.JSONDecodeError:
                    print("Erro ao decodificar a entrada do relatório.")
                    return
            else:
                entrada = relatorio.entrada  # Caso já seja uma lista

            # Inicialize a lista de saídas
            saida = []

            for produto in entrada:
                nome = produto["nome"]
                estoque_inicial = produto["estoque"]
                estoque_final = estoque_dicionario.get(nome, 0)
                quantidade_saida = calcular_quantidade_saida(estoque_inicial, estoque_final)
                if quantidade_saida > 0:
                    saida.append({
                        "nome": nome,
                        "quantidade_saida": quantidade_saida
                    })

            # Atualize o relatório e salve no banco de dados
            relatorio.saida = json.dumps(saida)  # Converter para JSON antes de armazenar
            db.commit()

            print("Relatório fechado com sucesso. Saídas registradas.")
        else:
            print("Relatório não encontrado para o dia especificado.")


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
    def relatorio_pdf(e):
        id=e.control.key
        relatorio=getRelatorioUnicoByID(id)
        total_view=totalVendaMoneyRelatorio(relatorio.data)
        vendas_view=len(relatorio.vendas)
        
        vendas=[]
        for i in relatorio.vendas:
            
            total=totalVendaMoney(i.id)
            # print(total)
            total_tipo=totalVendaProdutos(i.id)
            vendas.append({
                'id':i.id,
                'hora':i.hora,
                'produto_total':total_tipo,
                'quantidade':f"{i.total_item}",
                'total':f"{total}",
                'cliente':f"{i.cliente}",
                'caixa':f"{i.funcionario}",
                'metodo':i.metodo,
                'produtos':i.produtos
            })
        relatorio_dict={
            'nome':relatorio.nome,
            'data':relatorio.data,
            'total_vendas':vendas_view,
            'total':total_view,
            'vendas':vendas,
            'entrada':relatorio.entrada,
            'saida':relatorio.saida,
        }
        if  relatorio.data ==day:
            print("relatorio de hoje")
            getHistoricoEstoque(getRelatorioUnico(day).id)
            fechar_relatorio(e)
        res=gerar_relatorio_pdf(relatorio_dict,getRelatorioUnico(day).id)
        if res:
            page.open(ft.AlertDialog(title=ft.Text("Relatorio"),content=ft.Text("O pdf foi gerado com sucesso")))
        else:
            page.open(ft.AlertDialog(title=ft.Text("Relatorio"),content=ft.Text("O pdf sera quardado\n nos documentos/jp"),
                                     actions=[ft.ElevatedButton("Imprimir PDF",on_click=relatorio_pdf,key=id)]))
        
    lista=ft.Column()
    dal=ft.AlertDialog(title=ft.Text("Produtos Da Venda:"),content=ft.Container(content=lista))
    def verMaisProdutos(e):
        lista.controls.clear()
        venda=db.query(ProdutoVenda).filter_by(id=e.control.key).first()

        for p in venda.produtos:
            
            #print(p)
            lista.controls.append(
                ft.Row(
                    controls=[
                        ft.Text(f"Nome: "),ft.Text(p['nome'],weight="bold"),
                        ft.Text(f"Preco: "),ft.Text(f"{p['preco']}0 MT"),
                        ft.Text(f"Quantidade: "),ft.Text(p['quantidade'],weight="bold"),
                        ft.Text(f"Total: "),ft.Text(f"{p['total']}0 MT",weight="bold")
                    ]
                )
            )
        page.open(dal)
    def close_modal(e):
        page.close(relatorio_alert)
    relatorio_alert=ft.AlertDialog(title=ft.Text("Sem Relatorio"),content=ft.Text("Nao tem um Relatorio diario para Hoje! Voce deseja criar?"),actions=[
        ft.TextButton('Cancelar',on_click=close_modal),
        ft.ElevatedButton("Criar Relatorio",on_click=novo_relatorio)
    ])
    def print_fatura_pdf(e):
        id=e.control.key
        venda =getOneSale(id)
        def to_dict(obj):
            return {column.name: getattr(obj, column.name) for column in obj.__table__.columns}

        # Exemplo de uso
        produto_venda_dict = to_dict(venda)  # produto_venda é o objeto do modelo
        gerar_pdf(produto_venda_dict)

    def ch(e):
        global ultima_venda,total_valor
        ultima_venda['metodo']=e.control.value
        if e.control.value !="Cash":
            valor_pagar.value=total_valor
            valor_pagar.disabled=True
        else:
            valor_pagar.disabled=False


    # ft.dropdown.Option("Paga Facil"),
    #                          ft.dropdown.Option("Ponto 24"),
    #                          ft.dropdown.Option("POS BIM"),
    #                          ft.dropdown.Option("POS BCI"),
    #                          ft.dropdown.Option("POS ABSA"),
    #                          ft.dropdown.Option("POS MOZA BANCO"),
    #                          ft.dropdown.Option("POS StanderBank"),
    #                          ft.dropdown.Option("M-Cash")

    pagamento=ft.Dropdown(label="metodo de pagamento",
                    options=[ft.dropdown.Option("Cash"),
                             ft.dropdown.Option("MPesa"),
                             ft.dropdown.Option("POS BCI"),
                             ft.dropdown.Option("E-mola")
                             ],on_change=ch)

    def see_more(e):
        vendas.controls.clear()
        global total_view
        global vendas_view
        global data_view

        rel=getRelatorioUnicoByID(e.control.bgcolor)
        total_view=totalVendaMoneyRelatorio(rel.data)
        vendas_view=len(rel.vendas)
        data_view=rel.data
        relatorios.controls.clear()
        relatorios.controls.append(ft.Text(f"Data: {data_view}"))
        relatorios.controls.append(ft.Text(f"Vendas: {vendas_view}"))
        relatorios.controls.append(ft.Text(f"Total: {total_view} MT"))
        relatorios.controls.append(vendas)
        for i in rel.vendas:
            total=totalVendaMoney(i.id)
            total_tipo=totalVendaProdutos(i.id)
            vendas.controls.append(ft.Card(content=ft.Container(padding=8,
                content=ft.Column(controls=[
                    ft.Row(controls=[
                    ft.Text(f"Produtos: {total_tipo}"),
                    ft.Text(f"Qtd: {i.total_item}"),
                    ft.IconButton(icon=ft.Icons.VISIBILITY,key=f"{i.id}",on_click=verMaisProdutos),
                    ft.Row(controls=[
                        ft.Text(f"Total:"),
                        ft.Text(f" {total}0 MT",size=18,weight="bold")
                    ]),
                    ft.Row(controls=[
                        ft.Text(f"Cliente/Mesa: "),
                        ft.Text(f"{i.cliente}",size=15,weight="bold")
                    ]),
                    ft.Row(controls=[
                        ft.Text(f"Caixa: "),
                        ft.Text(f"{i.funcionario}",size=15,weight="bold")
                    ]),
                    
                    ft.IconButton(icon=ft.Icons.PRINT,key=f"{i.id}",on_click=print_fatura_pdf)

                ]),
     
               
                ])
            )))


        page.update()


    dialogo=ft.AlertDialog(title=ft.Text("PDV LITE"),
                           content=ft.Text("So pode criar um Relatorios por dia"),
                           actions=[
                               ft.TextButton('intendi',on_click=fecha)
                           ] )

    valor_pagar=ft.TextField(label="valor recebido",on_change=write_payment2)
    trocoView=ft.Text(weight='bold',size=24,col=ft.Colors.RED_500)
    
    def close_show(e):
        page.close(resumo_venda)
    pagament=ft.AlertDialog(title=ft.Text("Pagamento"),content=ft.Container(width=300,height=340,content=ft.Column([
        pagamento,
                    valor_pagar,
                    trocoView,
                    keyboard2
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
        ft.ElevatedButton("imprimir",bgcolor=ft.Colors.RED_500,color='white',on_click=imprimir_fatuta)
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
                    ft.IconButton(icon=ft.Icons.DELETE, on_click=limpar,icon_color="red"),
                    ft.IconButton(icon=ft.Icons.LIST, on_click=addcontas,),
                    ft.IconButton(icon=ft.Icons.CHECK, on_click=guardar),
                    ft.IconButton(icon=ft.Icons.VISIBILITY, on_click=show_carrinho),
                ])
            ]))
        lista_vendas.controls.clear()
        page.update()
    help_dialog=ft.AlertDialog(title=ft.Text("Ajuda"),content=ft.Container(padding=10,width=300,content=ft.Text(
        "O aplicativo PDV LITE e um sistema que facilitas as vendas das lojas, restaurantes e farmacias, o aplicativo tem uma documentacao na web e uma playlist de aulas gratis, clique nas seguintes accoes e aproveite , o novo futura de mocambique"
    )),actions=[
        ft.ElevatedButton("Documentacao",bgcolor="blue"),
        ft.ElevatedButton("YouTube",bgcolor="red")
    ])


    ####################################################### NAVBAR #############################################################
    if(CheckIsLoged()==True):
        pass
    total_text=ft.Column(controls=[
        ft.Column(controls=[
                ft.Text(f"Subtotal: 0.0 MT", size=17),
                ft.Text(f"IVA: 0.0 MT", size=17), 
                ft.Text(f"Total : 0.0 MT", size=17),

                ft.Row(controls=[
                    ft.IconButton(icon=ft.Icons.DELETE, on_click=limpar,icon_color="red"),
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
                    "categoria":produto.categoria,
                    "nome": produto.titulo,
                    "preco": produto.preco,
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
                ft.IconButton(icon=ft.Icons.DELETE, on_click=limpar,icon_color="red"),
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
                        ft.Text(f"Qtd: {item['quantidade']}"),  ft.PopupMenuButton(items=[
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
        total_text.controls.append(ft.Column(controls=[
            ft.Text(f"Subtotal: {subtotal} MT", size=17),
            ft.Text(f"IVA: {round(iva,2)} MT", size=17), 
            ft.Text(f"Total: {total} MT", size=17),
                            ft.Row(controls=[
                ft.IconButton(icon=ft.Icons.DELETE, on_click=limpar,icon_color="red"),
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
                    carrinho_s[i]['total'] = carrinho_s[i]['quantidade'] * carrinho_s[i]['preco']
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
                    ft.IconButton(icon=ft.Icons.DELETE, on_click=limpar, icon_color="red"),
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
                    "categoria":produto.categoria,
                    "preco": produto.preco,
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
                ft.IconButton(icon=ft.Icons.DELETE, on_click=limpar,icon_color="red"),
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
                        ft.Row(controls=[ft.Text(f"{item['preco']} MT", size=12)]),
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
                    ft.IconButton(icon=ft.Icons.DELETE, on_click=limpar,icon_color="red"),
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
                            ft.Row(controls=[ft.Text(f"{item['preco']} MT", size=12)]),
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
                                            ft.Text(f'{i.preco} MZN',weight="bold",size=13,color=ft.Colors.RED_700)
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
                                            ft.Text(f'{i.preco} MZN',weight="bold",size=13,color=ft.Colors.RED_700)
                                        ])
                                        ,on_hover=hovercard,on_click=adicionar_Carinho,on_long_press=dl_more_carinho,key=f'{i.id}')),) 
        page.update()
    
    def hovercard(e):
        if e.data == "true":  # mouse entra
            e.control.bgcolor='#fefce8'
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
                                        ft.Text(f'{i.preco} MZN',weight="bold",size=13,color=ft.Colors.RED_700)
                                    ])
                                    ,on_hover=hovercard,on_click=adicionar_Carinho,on_long_press=dl_more_carinho,key=f'{i.id}')),) 
        page.update()
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
        

    def eliminarProoduto(id):
        deletarProduto(id)
        update_menu()
        update_produtos()
    def open_estoque(id):
        global selected_item_id
        selected_item_id=id
        page.open(fornecer_dialog)
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

    lista_relatorio=ft.ListView(width=200,height=700)  
    alert_delete=ft.AlertDialog(title=ft.Text("Aviso"))  
    def deletar_relatorio(e):
        id=e.control.key
        relatorio=db.query(RelatorioVenda).filter_by(id=id).first()
        db.delete(relatorio)
        db.commit()
        relatorio_update()
        page.close(alert_delete)

    def dialog_delete_relatorio(e):
        if(get_logged_user()['cargo'])=='admin':
            alert_delete.content=ft.Row([ft.Icon(ft.Icons.INFO,color=ft.Colors.RED_500),ft.Text("Confirma a exclussao do \n Relatorio?")])
            alert_delete.actions=[
                ft.ElevatedButton("DELETAR",bgcolor="red",color="white",on_click=deletar_relatorio,key=e.control.key)
            ]
            page.open(alert_delete)
        else:
            page.open(ft.AlertDialog(title=ft.Text("Aviso"),content=ft.Row([
                ft.Icon(ft.Icons.INFO,color=ft.Colors.RED_600),
                ft.Text("Nao tens permicao para \n deletar um relatorio",weight="bold")
            ])))
    def relatorio_update():
        lista_relatorio.controls.clear()
        page.update()
        for i in getRelatorios():
            total=totalVendaMoneyRelatorio(i.data)
            lista_relatorio.controls.append(
                ft.Container(
                    content=ft.Card(
                ft.Container(padding=10,        
                content=ft.Column(  
                [
                    ft.Row(
                    [
                    ft.Text(i.data,size=18,weight="bold"),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                ft.Text(f"Total: {total} MT",weight="bold",size=17),
                    
                ft.Row(controls=[
            ft.IconButton(ft.Icons.MORE,on_click=see_more,bgcolor=f"{i.id}"),
             ft.IconButton(ft.Icons.PRINT,on_click=relatorio_pdf,key=f"{i.id}"),
            ft.IconButton(ft.Icons.DELETE,on_click=dialog_delete_relatorio,key=i.id)
                ],
                alignment=ft.MainAxisAlignment.CENTER
                ),
                
                ],
                alignment=ft.MainAxisAlignment.CENTER
            ) )
            ))
                )
            body.content = relatoriosBody
            
            page.update()
        page.update()

    
    lista_vendas=ft.ListView(height=380)

    # items_menu=ft.GridView(max_extent=200,spacing=10,height=600,child_aspect_ratio=0.8)
    items_menu=ft.Row(wrap=True,scroll=True,height=altura-110)
    search_categoria = ft.Dropdown(
        label="Categoria",
        options=[ft.dropdown.Option(categoria.nome) for categoria in categoria_lista],
        on_change=submit
    )
    input_categoria = ft.Dropdown(
        label="Categoria",
        width=400,
        options=[ft.dropdown.Option(categoria.nome) for categoria in categoria_lista],
        on_change=submit
    )
    search=ft.TextField(label="Procurar Produto",border_radius=12,on_change=submit)

    search_categoria2 = ft.Dropdown(
        label="Categoria",
        options=[ft.dropdown.Option(categoria.nome) for categoria in categoria_lista],
        on_change=submit2
    )
    search2=ft.TextField(label="Procurar Produto",border_radius=12,on_change=submit2)
    produtos_table_itens=ft.Container(height=page.window.height-20,padding=10)
    produtos=ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nome do produto")),
                ft.DataColumn(ft.Text("Preco")),
                ft.DataColumn(ft.Text("Codigo de Barra")),
                ft.DataColumn(ft.Text("Categoria")),
                ft.DataColumn(ft.Text("Estoque Atual"), numeric=True),
                ft.DataColumn(ft.Text("accoes")),
            ])
    update_menu()
    
    relatoriosBody=ft.Container(scale=0.9,
        content=ft.Column(controls=[
            ft.Row(controls=[
                ft.Text("Relatorios Diarios",weight="bold"),
                ft.ElevatedButton("Novo Relatorio",on_click=novo_relatorio)
            ]),
            ft.Row(
                controls=[
                    lista_relatorio,
                    ft.Container(expand=True,height=altura,padding=10,content=ft.Column(
                    controls=[
                        ft.Text("Detalhes Do Relatorio",weight="bold",size=30),
                        relatorios
                    ]
                    ))

                ]
            )
        ])
    )
    def imprimir_todos(e):
        produtos = db.query(Produto).order_by(asc(Produto.titulo)).all()
        gerar_pdf_produtos(produtos)
        
    produtoBody=ft.Container(
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
    mesas = [ft.dropdown.Option(f"Mesa {i}") for i in range(1, 31)]
    mesas.insert(0, ft.dropdown.Option("Sem mesa"))
    mesa=ft.Dropdown(label="Mesa",height=40,
                     options=mesas)
    def addUser(e):
        page.open(userDialog)
        

    name=ft.TextField(label='Nome do funcionario')
    username_input=ft.TextField(label='username')
    senha=ft.TextField(label='senha')

        
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
    if CheckIsLoged():
        
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
        
    nome_input = ft.TextField(label="Nome", width=400)
    preco_input = ft.TextField(label="Preço", width=400)
    barcode=ft.TextField(label="barcode Scanneado")
    select_button = ft.ElevatedButton(text="Selecionar Foto", on_click=lambda _: file_picker.pick_files(allow_multiple=False))
    estoque = ft.TextField(label="estoque", multiline=True, width=400,)
    
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
    
    # Criando o NavigationRail
    nav_rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=400,
        group_alignment=-0.9,
        leading=ft.Container(padding=5,
                             content=ft.Text("JP",weight="bold",color=ft.Colors.RED_600,size=35),
    ),
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.HOME_OUTLINED),
                selected_icon=ft.Icon(ft.Icons.HOME,color=ft.Colors.RED_500),
                label="Casa"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.WIDGETS),
                selected_icon=ft.Icon(ft.Icons.WIDGETS,color=ft.Colors.RED_500),
                label="Produtos"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.INVENTORY),
                selected_icon=ft.Icon(ft.Icons.INVENTORY,color=ft.Colors.RED_500),
                label="Estoque"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.MONETIZATION_ON),
                selected_icon=ft.Icon(ft.Icons.MONETIZATION_ON,color=ft.Colors.RED_500),
                label="Saldo"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.TABLE_BAR),
                selected_icon=ft.Icon(ft.Icons.TABLE_BAR,color=ft.Colors.RED_500),
                label="Mesas"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.TIMELINE_OUTLINED),
                selected_icon=ft.Icon(ft.Icons.TIMELINE,color=ft.Colors.RED_500),
                label="Relatorios"
            ),
        ],
        on_change=chage_nav,
    )

    bottom_nav=ft.NavigationRail(height=130,width=100,destinations=[
        ft.NavigationRailDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icon(ft.Icons.SETTINGS,color=ft.Colors.RED_500),
                label="Definicoes"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.LOGOUT_OUTLINED,
                selected_icon=ft.Icon(ft.Icons.LOGOUT,color=ft.Colors.RED_500),
                label="Log out"
            ),

    ],on_change=chage_nav2)
    def close_about(e):
        about.open=False
        page.update()
    about=ft.AlertDialog(
        title=ft.Text("Sobre PDV Lite v1.0 - Lichinga"),
        content=ft.Container(
            width=300,
            content=ft.Text("""O PDV Lite é um sistema de ponto de venda offline desenvolvido pela equipe BlueSpark da empresa Electro Gulamo. Este sistema tem como objetivo auxiliar a gestão de vendas em lojas e farmácias.
                                                                        Imagine um cenário onde todos os cálculos são realizados automaticamente e um relatório diário é gerado sem a necessidade de utilizar o Excel. O PDV Lite foi criado para oferecer muito mais, proporcionando uma solução completa e eficiente para a gestão de vendas.
        """,no_wrap=False)),actions=[
            ft.TextButton("Intendi!",on_click=close_about)
        ])
    # Conteúdo inicial do corpo da página
    if CheckIsLoged():
        body = ft.Container(content=ft.Container(
        bgcolor="#e1e0e0",
        content=ft.Column(
           controls=[
                ft.Row(
                    controls=[
                
                ft.Container(expand=True,height=altura,
                             padding=14,
                             content=ft.Column(controls=[
                    ft.Container(padding=10,border_radius=10,bgcolor="white",content=ft.Row(controls=[
                        ft.Text(info['app'],size=30,weight="bold",color=ft.Colors.RED_500),
                        search_categoria,
                        search
                    ],alignment=ft.MainAxisAlignment.SPACE_BETWEEN)),
                    items_menu
                ])),
                ft.Container(width=260,padding=10,bgcolor=ft.Colors.WHITE,content=ft.Column(controls=[
                    ft.Text("Resumo da Veda:",size=20,weight="bold",color=ft.Colors.RED_500),
                     ft.Container(padding=10,margin=10,content=ft.Column(controls=[
                        ft.Row(controls=[
                                ft.Text("Data:",size=15),
                                ft.Text(day,size=15)
                            ]),
                        horas,
                        ft.Row(controls=[
                                ft.Text("Caixa:",size=15),
                                ft.Text(userLoged().nome,size=15),    
                            ]),
                        
                    ])),
                    ft.Card(content=ft.Container(padding=10,
                                                 content=ft.Column([
                                                     clientes,mesa,ft.ElevatedButton("Abrir Gaveta",on_click=lambda e:abrir_gaveta()),
                                                    ]),)),
                    ft.Stack(width=260,height=650,controls=[
                    ft.Container(content=lista_vendas,scale=0.8),
                    ft.Card(width=235,
                            bottom=300,
                            content=ft.Container(padding=10,content=ft.Column(controls=[
                                total_text
                                ])))
                                ])
                                ]))
             
                    ],)])))
    else:
        body = ft.Container(content=ft.Container())

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
        page.floating_action_button=ft.FloatingActionButton(
                        icon=ft.Icons.ADD, on_click=add_item
                    )
        page.add(
          body_config  
        ) 
        
        
    else:
        page.add(login_page)
    while True:
        try:
            update_time()
        except:
            page.window.close()
        sleep(10)
    
ft.app(target=main)
