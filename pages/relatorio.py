import flet as ft 
from controler import *
from pdv2pdf import *

class RelatorioPage(ft.Container):
    def __init__(self, pagex):
        super().__init__()
        self.pagex = pagex
        self.expand = True
        self.current_date = datetime.now()
        self.day = self.current_date.strftime("%d-%m-%Y")
        self.banco = isDataBase()
        self.hora = ""
        self.data_view = "00-00-0000"
        self.vendas_view = 0
        self.total_view = 0.00
        self.iva_p = 0.16
        self.total_valor = 0
        self.selected_item_id = None
        
        # Componentes da UI
        self.lista_relatorio = ft.ListView(width=200, height=700)
        self.alert_delete = ft.AlertDialog(title=ft.Text("Aviso"))
        self.relatorios = ft.Column(controls=[
            ft.Text(f"Data: {self.data_view}"),
            ft.Text(f"Vendas: {self.vendas_view}"),
            ft.Text(f"Total: {self.total_view} MT")
        ])
        self.vendas = ft.ListView(height=500)
        
        # Dialogs
        self.lista = ft.Column()
        self.dal = ft.AlertDialog(title=ft.Text("Produtos Da Venda:"), content=ft.Container(content=self.lista))
        
        self.relatorio_alert = ft.AlertDialog(
            title=ft.Text("Sem Relatorio"),
            content=ft.Text("Nao tem um Relatorio diario para Hoje! Voce deseja criar?"),
            actions=[
                ft.TextButton('Cancelar', on_click=self.close_modal),
                ft.ElevatedButton("Criar Relatorio", on_click=self.novo_relatorio)
            ])
            
        self.dialogo = ft.AlertDialog(
            title=ft.Text("PDV LITE"),
            content=ft.Text("So pode criar um Relatorios por dia"),
            actions=[
                ft.TextButton('intendi', on_click=self.fecha)
            ])
            
        # Configurar o conteúdo da página no construtor
        self.content = self.build()
        
        # Carregar a lista de relatórios quando a página é inicializada
        self.did_mount()

    def deletar_relatorio(self, e):
        id = e.control.key
        relatorio = db.query(RelatorioVenda).filter_by(id=id).first()
        db.delete(relatorio)
        db.commit()

        self.pagex.close(self.alert_delete)
        # Atualiza a lista após a exclusão
        self.did_mount()
        
    def dialog_delete_relatorio(self, e):
        if(get_logged_user()['cargo']) == 'admin':
            self.alert_delete.content = ft.Row([ft.Icon(ft.Icons.INFO, color=ft.Colors.RED_500), ft.Text("Confirma a exclussao do \n Relatorio?")])
            self.alert_delete.actions = [
                ft.ElevatedButton("DELETAR", bgcolor="red", color="white", on_click=self.deletar_relatorio, key=e.control.key)
            ]
            self.pagex.open(self.alert_delete)
        else:
            self.pagex.open(ft.AlertDialog(title=ft.Text("Aviso"), content=ft.Row([
                ft.Icon(ft.Icons.INFO, color=ft.Colors.RED_600),
                ft.Text("Nao tens permicao para \n deletar um relatorio", weight="bold")
            ])))
            
    def close_modal(self, e):
        self.pagex.close(self.relatorio_alert)

    def fecha(self, e):
        self.dialogo.open = False
        self.pagex.update()

    def fechar_relatorio(self, e):
        # Tente recuperar o relatório do dia especificado
        relatorio = db.query(RelatorioVenda).filter_by(nome=f"relatorio{self.day}").first()

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
            
    def relatorio_pdf(self, e):
        id = e.control.key
        relatorio = getRelatorioUnicoByID(id)
        total_view = totalVendaMoneyRelatorio(relatorio.data)
        vendas_view = len(relatorio.vendas)
        vendas = []
        
        for i in relatorio.vendas:
            # Calcular o total dos produtos para cada venda
            produto_total = sum(float(p['total']) for p in i.produtos)
            
            vendas.append({
                'id': i.id,
                'data': i.data,
                'hora': i.hora,
                'total_item': i.total_item,
                'cliente': f"{i.cliente}",
                'caixa': f"{i.funcionario}",
                'metodo': i.metodo,
                'produtos': i.produtos,
                'total': str(totalVendaMoney(i.id)),
                'produto_total': str(produto_total),  # Adiciona o total dos produtos
                'quantidade': str(i.total_item)  # Adiciona a quantidade total de itens
            })
            
        relatorio_dict = {
            'nome': relatorio.nome,
            'data': relatorio.data,
            'total_vendas': vendas_view,
            'total': total_view,
            'vendas': vendas,
            'entrada': relatorio.entrada,
            'saida': relatorio.saida,
        }
        
        res = gerar_relatorio_pdf(relatorio_dict, id)
        if res:
            self.pagex.open(ft.AlertDialog(title=ft.Text("Relatório"), content=ft.Text("O PDF foi gerado com sucesso")))
        else:
            self.pagex.open(ft.AlertDialog(
                title=ft.Text("Relatório"), 
                content=ft.Text("O PDF será guardado nos documentos/jp"),
                actions=[ft.ElevatedButton("Imprimir PDF", on_click=self.relatorio_pdf, key=id)]
            ))
            
    def novo_relatorio(self, e):
        self.relatorio_alert.open = False
        self.pagex.update()
        rlt = db.query(RelatorioVenda).filter_by(nome=f"relatorio{self.day}").count()
        
        if rlt > 0:
            self.pagex.open(self.dialogo)
        else:
            estoque_hoje = db.query(Produto).all()
            entrada = []
            
            for i in estoque_hoje:
                entrada.append({
                    "nome": i.titulo,
                    "estoque": i.estoque
                })
            
            addRelatorio(self.day, entrada)
            
    def verMaisProdutos(self, e):
        self.lista.controls.clear()
        venda = db.query(ProdutoVenda).filter_by(id=e.control.key).first()

        for p in venda.produtos:
            
            #print(p)
            self.lista.controls.append(
                ft.Row(
                    controls=[
                        ft.Text(f"Nome: "), ft.Text(p['nome'], weight="bold"),
                        ft.Text(f"Preco: "), ft.Text(f"{p['preco']}0 MT"),
                        ft.Text(f"Quantidade: "), ft.Text(p['quantidade'], weight="bold"),
                        ft.Text(f"Total: "), ft.Text(f"{p['total']}0 MT", weight="bold")
                    ]
                )
            )
        self.pagex.open(self.dal)
        
    def print_fatura_pdf(self, e):
        id = e.control.key
        venda = getOneSale(id)
        def to_dict(obj):
            return {column.name: getattr(obj, column.name) for column in obj.__table__.columns}

        # Exemplo de uso
        produto_venda_dict = to_dict(venda)  # produto_venda é o objeto do modelo
        gerar_pdf(produto_venda_dict)
        
    def see_more(self, e):
        self.vendas.controls.clear()
        
        rel = getRelatorioUnicoByID(e.control.bgcolor)
        self.total_view = totalVendaMoneyRelatorio(rel.data)
        self.vendas_view = len(rel.vendas)
        self.data_view = rel.data
        self.relatorios.controls.clear()
        self.relatorios.controls.append(ft.Text(f"Data: {self.data_view}", size=18, weight="bold"))
        self.relatorios.controls.append(ft.Text(f"Vendas: {self.vendas_view}", size=16))
        self.relatorios.controls.append(ft.Text(f"Total: {self.total_view} MT", size=16, color=ft.Colors.RED_500))
        
        for m in rel.vendas:
            total = totalVendaMoney(m.id)
            
            self.vendas.controls.append(
                ft.Card(
                    content=ft.Container(
                        padding=10,
                        content=ft.Column([
                            ft.Row([
                                ft.Column([
                                    ft.Row([
                                        ft.Text("Hora: "), ft.Text(f"{m.hora}", weight="bold")
                                    ]),
                                    ft.Row([
                                        ft.Text("Caixa: "), ft.Text(f"{m.funcionario}", weight="bold")
                                    ]),
                                    ft.Row([
                                        ft.Text("Cliente: "), ft.Text(f"{m.cliente}", weight="bold")
                                    ]),
                                ]),
                                ft.Column([
                                    ft.Row([
                                        ft.Text("Items: "), ft.Text(f"{m.total_item}", weight="bold")
                                    ]),
                                    ft.Row([
                                        ft.Text("Total: "), ft.Text(f"{total}0 MT", weight="bold", color=ft.Colors.RED_500)
                                    ]),
                                    ft.Row([
                                        ft.Text("Metodo: "), ft.Text(f"{m.metodo}", weight="bold")
                                    ]),
                                ])
                            ]),
                            ft.Row([
                                ft.ElevatedButton(
                                    "Imprimir", 
                                    icon=ft.Icons.PRINT,
                                    bgcolor=ft.Colors.ORANGE_600, 
                                    color=ft.Colors.WHITE,
                                    on_click=self.print_fatura_pdf, 
                                    key=m.id
                                ),
                                ft.TextButton(
                                    "Ver Produtos", 
                                    icon=ft.Icons.LIST,
                                    on_click=self.verMaisProdutos, 
                                    key=m.id
                                ),
                            ], alignment=ft.MainAxisAlignment.CENTER)
                        ])
                    )
                )
            )
        self.pagex.update()
        
    def did_mount(self):
        self.lista_relatorio.controls.clear()
        if is_logged():
            try:
                relatorios = db.query(RelatorioVenda).order_by(RelatorioVenda.id.desc()).all()
                for rel in relatorios:
                    total = totalVendaMoneyRelatorio(rel.data)
                    self.lista_relatorio.controls.append(
                        ft.Container(
                            content=ft.Card(
                                content=ft.Container(
                                    padding=10,        
                                    content=ft.Column([
                                        ft.Row([
                                            ft.Text(rel.data, size=18, weight="bold"),
                                        ], alignment=ft.MainAxisAlignment.CENTER),
                                        ft.Text(f"Total: {total} MT", weight="bold", size=17),
                                        ft.Row(
                                            controls=[
                                                ft.IconButton(
                                                    icon=ft.Icons.MORE,
                                                    on_click=self.see_more,
                                                    bgcolor=rel.id
                                                ),
                                                ft.IconButton(
                                                    icon=ft.Icons.PRINT,
                                                    on_click=self.relatorio_pdf,
                                                    key=rel.id
                                                ),
                                                ft.IconButton(
                                                    icon=ft.Icons.DELETE,
                                                    on_click=self.dialog_delete_relatorio,
                                                    key=rel.id
                                                )
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER
                                        ),
                                    ], alignment=ft.MainAxisAlignment.CENTER)
                                )
                            )
                        )
                    )
            except Exception as e:
                print(f"Erro ao carregar relatórios: {e}")
        
    def build(self):
        return ft.Container(
            padding=10,
            content=ft.Column([
                ft.Row([
                    ft.Text("Relatorios", size=30, weight="bold"),
                    ft.ElevatedButton(
                        "Criar Novo Relatório", 
                        on_click=self.novo_relatorio, 
                        bgcolor=ft.Colors.GREEN, 
                        color=ft.Colors.WHITE
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([
                    ft.Container(
                        width=230,
                        height=700,
                        content=self.lista_relatorio
                    ),
                    ft.Column([
                        self.relatorios,
                        ft.Container(
                            height=600,
                            content=self.vendas
                        )
                    ])
                ])
            ])
        )

# Função de compatibilidade para o código existente
def relatorioPage(pagex):
    return RelatorioPage(pagex)