import flet as ft
from controler import *

class MoneyPage(ft.Container):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.expand = True
        self.content = self.build()
        
    def build(self):
        # Buscar todos os produtos usando a função verProdutos()
        produtos = verProdutos()  # Usando a função verProdutos() para obter os produtos
        
        # Transformar em dicionário agrupado por categoria
        produtos_por_categoria = {}
        total_produtos = 0
        valor_total = 0
        
        for produto in produtos:
            categoria = produto.categoria
            if categoria not in produtos_por_categoria:
                produtos_por_categoria[categoria] = {
                    'quantidade': 0,
                    'valor_total': 0,
                    'produtos': []
                }
            
            produtos_por_categoria[categoria]['quantidade'] += produto.estoque
            produtos_por_categoria[categoria]['valor_total'] += produto.preco * produto.estoque
            produtos_por_categoria[categoria]['produtos'].append(produto)
            
            total_produtos += produto.estoque
            valor_total += produto.preco * produto.estoque
        
        # Obter valores específicos para cada categoria
        cafetaria_info = produtos_por_categoria.get('Cafetaria', {'quantidade': 0, 'valor_total': 0})
        cozinha_info = produtos_por_categoria.get('Cozinha', {'quantidade': 0, 'valor_total': 0})
        loja_info = produtos_por_categoria.get('Loja', {'quantidade': 0, 'valor_total': 0})
        
        # Criar cards
        card_empresa = self.criar_card(
            "Saldo Total da Empresa",
            f"{formatToMoney(valor_total)} MZN",
            f"Total de Produtos: {total_produtos}",
            ft.Colors.INDIGO_300  # Cor de fundo uniforme
        )
        
        card_cafetaria = self.criar_card(
            "Saldo da Cafetaria",
            f"{formatToMoney(cafetaria_info['valor_total'])} MZN",
            f"Produtos: {cafetaria_info['quantidade']}",
            ft.Colors.INDIGO_300  # Cor de fundo uniforme
        )
        
        card_cozinha = self.criar_card(
            "Saldo da Cozinha",
            f"{formatToMoney(cozinha_info['valor_total'])} MZN",
            f"Produtos: {cozinha_info['quantidade']}",
            ft.Colors.INDIGO_300  # Cor de fundo uniforme
        )
        
        card_loja = self.criar_card(
            "Saldo da Loja",
            f"{formatToMoney(loja_info['valor_total'])} MZN",
            f"Produtos: {loja_info['quantidade']}",
            ft.Colors.INDIGO_300  # Cor de fundo uniforme
        )
        
        card_outros = self.criar_card(
            "Resumo de Categorias",
            f"{len(produtos_por_categoria)} Categorias",
            f"Valor Médio: {formatToMoney(valor_total/max(1, len(produtos_por_categoria)))} MZN",
            ft.Colors.INDIGO_300  # Cor de fundo uniforme
        )
        
        return ft.Container(
            bgcolor="#F0F8FF",
            expand=True,
            padding=20,
            content=ft.Column(
                [
                    ft.Text("Visão Financeira", size=32, weight="bold", color=ft.Colors.INDIGO_900),
                    ft.Divider(height=1, color=ft.Colors.INDIGO_200),
                    ft.Container(height=20),
                    
                    # Usando ft.ResponsiveRow para cards responsivos
                    ft.ResponsiveRow(
                        [
                            ft.Column([card_empresa], col=2.4),  # Cada card ocupa 2.4 colunas
                            ft.Column([card_cafetaria], col=2.4),
                            ft.Column([card_cozinha], col=2.4),
                            ft.Column([card_loja], col=2.4),
                            ft.Column([card_outros], col=2.4)
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
    
    def criar_card(self, titulo, valor, subtitulo, cor):
        return ft.Card(
            elevation=0,  # Removido a sombra
            margin=5,
            content=ft.Container(
                width=220,
                height=170,
                padding=10,
                bgcolor=cor,  # Definindo a cor de fundo do card
                border_radius=10,
                content=ft.Column(
                    [
                        ft.Text(titulo, size=18, weight="bold", color=ft.colors.WHITE),
                        ft.Container(height=5),
                        ft.Text(valor, size=24, weight="bold", color=ft.colors.WHITE),
                        ft.Container(height=5),
                        ft.Text(subtitulo, size=14, color=ft.colors.WHITE),
                        ft.Container(
                            alignment=ft.alignment.bottom_right,
                            content=ft.Icon(ft.icons.EQUALIZER, color=ft.colors.with_opacity(0.3, ft.colors.WHITE), size=30)
                        )
                    ],
                    spacing=5,
                )
            )
        )

# Função de compatibilidade para o código existente
def moneyPage(pagex):
    return MoneyPage(pagex)
