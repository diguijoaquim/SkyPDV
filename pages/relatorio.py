import flet as ft 
from controler import *
from pdv2pdf import *
page=None
current_date = datetime.now()
day = current_date.strftime("%d-%m-%Y")
banco=isDataBase()
day = current_date.strftime("%d-%m-%Y")
hora=""
data_view="00-00-0000"
vendas_view=0
total_view=0.00
iva_p = 0.16
total_valor=0
selected_item_id=None
lista_relatorio=ft.ListView(width=200,height=700)
alert_delete=ft.AlertDialog(title=ft.Text("Aviso")) 
relatorios=ft.Column(controls=[
                ft.Text(f"Data: {data_view}"),
                ft.Text(f"Vendas: {vendas_view}"),
                ft.Text(f"Total: {total_view} MT")
                               ]) 
vendas=ft.ListView(height=500)
def deletar_relatorio(e):
    id=e.control.key
    relatorio=db.query(RelatorioVenda).filter_by(id=id).first()
    db.delete(relatorio)
    db.commit()

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
def close_modal(e):
    page.close(relatorio_alert)

def fecha(e):
        dialogo.open=False
        page.update()

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
    
def relatorioPage(pagex):
    global page
    lista_relatorio.controls.clear()
    page=pagex
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
            )))
    return ft.Container(scale=0.9,
        content=ft.Column(controls=[
            ft.Row(controls=[
                ft.Text("Relatorios Diarios",weight="bold"),
                ft.ElevatedButton("Novo Relatorio",on_click=novo_relatorio)
            ]),
            ft.Row(
                controls=[
                    lista_relatorio,
                    ft.Container(expand=True,height=800,padding=10,content=ft.Column(
                    controls=[
                        ft.Text("Detalhes Do Relatorio",weight="bold",size=30),
                        relatorios
                    ]
                    ))

                ]
            )
        ])
    )