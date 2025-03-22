import flet as ft
from controler import *
from sqlalchemy import asc
from models.modelos import Produto
from pdv2pdf import gerar_pdf_produtos
import os
from local import get_logged_user
import shutil
from datetime import datetime

class ProductsPage(ft.Container):
    def __init__(self, page:ft.Page, update_menu_callback):
        super().__init__()
        self.page = page
        self.update_menu = update_menu_callback
        self.expand = True
        self.padding=8
        self.height=page.window.height
        self.bgcolor = "#F0F8FF"  # Light blue-white background
        self.banco = isDataBase()
        self.current_date = datetime.now()
        self.day = self.current_date.strftime("%d-%m-%Y")
        self.categoria_lista = getCategorias()
        self.imagens = os.path.join(os.getenv("LOCALAPPDATA"), ".jpInvest/img")
        self.selected_file_path = None
        
        # Componentes
        self.file_picker = ft.FilePicker(on_result=self.file_picker_result)
        self.page.overlay.append(self.file_picker)
        
        # Componentes para gestão de categorias
        self.nova_categoria_input = ft.TextField(label="Nome da Categoria", width=400)
        
        # Tabela de categorias
        self.categorias_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nome")),
                ft.DataColumn(ft.Text("Ações"), numeric=True)
            ],
            rows=[]
        )
        
        # Atualizar tabela de categorias
        self.atualizar_tabela_categorias()
        
        # Dialog para gestão de categorias
        self.dlg_categoria = ft.AlertDialog(
            title=ft.Text("Gestão de Categorias", size=24),
            content=ft.Column([
                ft.Row([
                    ft.CupertinoButton(
                        "Adicionar Nova Categoria",
                        icon=ft.Icons.ADD,
                        bgcolor=ft.Colors.INDIGO_400,
                        color="white",
                        on_click=self.abrir_add_categoria_dialog
                    )
                ]),
                self.categorias_table
            ], scroll=True, spacing=10),
            actions=[
                ft.TextButton("Fechar", on_click=self.cancel_categoria_dlg)
            ]
        )
        
        # Dialog para adicionar/editar categoria
        self.dlg_add_categoria = ft.AlertDialog(
            title=ft.Text("Adicionar Nova Categoria", size=24),
            content=self.nova_categoria_input,
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.close(self.dlg_add_categoria)),
                ft.CupertinoButton(
                    text="Salvar",
                    bgcolor=ft.Colors.INDIGO_400,
                    on_click=self.salvar_categoria
                )
            ]
        )
        
        self.status_text = ft.Text()
        self.select_button = ft.ElevatedButton(text="Selecionar Foto", on_click=lambda _: self.file_picker.pick_files(allow_multiple=False))
        
        # TextField para cadastro
        self.nome_input = ft.TextField(label="Nome", width=400)
        self.preco_input = ft.TextField(label="Preço", width=400)
        self.barcode = ft.TextField(label="barcode Scanneado")
        self.estoque = ft.TextField(label="estoque", multiline=True, width=400)
        self.categoria = ft.Dropdown(
                label="Categoria",width=300,
                options=[ft.dropdown.Option(categoria.nome) for categoria in self.categoria_lista]
            )
            
        # TextField para edição
        self.e_nome_input = ft.TextField(label="Nome", width=400)
        self.e_preco_input = ft.TextField(label="Preço", width=400)
        self.e_barcode_input = ft.TextField(label="Barcode Scanneado")
        self.e_estoque = ft.TextField(label="Estoque", multiline=True, width=400)
        self.input_categoria = ft.Dropdown(
                label="Categoria",
                width=400,
                options=[ft.dropdown.Option(categoria.nome) for categoria in self.categoria_lista])
                
        # Dialogs
        self.dlg = ft.AlertDialog(
            title=ft.Text("Cadastrar Novo Produto", size=24),
            content=ft.Column([
                self.nome_input,
                self.barcode,
                self.preco_input,
                self.categoria,
                self.estoque,
                self.select_button,
                self.status_text
            ], scroll=True),
            actions=[
                ft.TextButton("Cancelar", on_click=self.cancel_dlg),
                ft.ElevatedButton("Salvar", on_click=self.add)
            ])
            
        self.dlg_edit = ft.AlertDialog(
            title=ft.Text("Atualizar o Produto", size=24),
        )
        
        self.quant_estoque = ft.TextField(label="Digite a quantidade")
        
        self.fornecer_dialog = ft.AlertDialog(
            title=ft.Text("Fornecer Produto"),
            content=self.quant_estoque,
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.close(self.fornecer_dialog)),
                ft.ElevatedButton("Fornecer", on_click=self.fornecer)
            ])
            
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
            
        # Inicializa os componentes que serão usados no build
        self.search = ft.TextField(
            label="Pesquisar", 
            on_change=self.submit2,
            prefix_icon=ft.Icons.SEARCH,
            suffix_icon=ft.Icons.CLEAR
        )
        
        self.search_categoria = ft.Dropdown(
            label="Filtrar por categoria",
            options=[ft.dropdown.Option("todas")] + [ft.dropdown.Option(categoria.nome) for categoria in self.categoria_lista],
            width=200,
            on_change=self.submit2
        )
        
        # Inicializa a tabela de produtos
        self.produtos_table = ft.DataTable(
            expand=True,
            columns=[
                ft.DataColumn(ft.Text("Imagem")),
                ft.DataColumn(ft.Text("Nome")),
                ft.DataColumn(ft.Text("Preço")),
                ft.DataColumn(ft.Text("Categoria")),
                ft.DataColumn(ft.Text("Estoque")),
                ft.DataColumn(ft.Text("Ações"))
            ],
            column_spacing=50,
            rows=[]
        )
        
        # Container para a tabela com scroll
        self.produtos_list = ft.Container(
            content=ft.ListView(
                expand=True,
                spacing=10,
                padding=10,
                auto_scroll=True,
                controls=[self.produtos_table]
            ),
            expand=True,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=10
        )
        
        # Inicializa os produtos
        self.update_produtos()
            
        # Inicializa os produtos e configura o content com o resultado do método build
        self.content = self.build()
    
    def file_picker_result(self, e: ft.FilePickerResultEvent):
        if e.files:
            self.selected_file_path = e.files[0].path
            self.status_text.value = f"Arquivo selecionado: {self.selected_file_path}"
        else:
            self.selected_file_path = None
            self.status_text.value = "Nenhum arquivo selecionado"
        self.page.update()
    
    def imprimir_todos(self, e):
        produtos = db.query(Produto).order_by(asc(Produto.titulo)).all()
        gerar_pdf_produtos(produtos)
    
    def atualizar(self, id):
        if(get_logged_user()['cargo'])=='admin':
            produto = acharUmProduto(id) 
            self.e_nome_input.value = produto.titulo
            self.e_barcode_input.value = produto.barcode
            self.e_preco_input.value = produto.preco
            self.e_estoque.value = produto.estoque
            self.input_categoria.value = produto.categoria
            
            self.dlg_edit = ft.AlertDialog(
                title=ft.Text("Atualizar o Produto", size=24),
                content=ft.Column([
                    self.e_nome_input,
                    self.e_barcode_input,
                    self.e_preco_input,
                    self.e_estoque,
                    self.input_categoria,
                    self.status_text,
                    self.select_button
                ], scroll=True),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda e: self.page.close(self.dlg_edit)),
                    ft.ElevatedButton("Atualizar", on_click=self.update_produto, key=id)
                ])

            self.page.open(self.dlg_edit)
        else:
            self.page.open(ft.AlertDialog(title=ft.Text("Aviso"), content=ft.Row([
                ft.Icon(ft.Icons.INFO, color=ft.Colors.RED_600),
                ft.Text("Nao tens permicao para \n editar produtos", weight="bold")
            ])))
    
    def cancel_dlg(self, event):
        self.dlg.open = False
        self.page.update()
    
    def update_produto(self, e):
        destination_dir = os.path.join(os.getenv("LOCALAPPDATA"), ".jpInvest/img")
        filename = None
        
        if self.selected_file_path:
            if not os.path.exists(destination_dir):
                os.makedirs(destination_dir)
            filename = os.path.basename(self.selected_file_path)
            destination_path = os.path.join(destination_dir, filename)
            try:
                shutil.copy(self.selected_file_path, destination_path)
                self.status_text.value = "Foto copiada com sucesso!"
            except Exception as ex:
                self.status_text.value = f"Erro ao copiar a foto: {ex}"
            self.page.update()

        pdt = acharUmProduto(e.control.key)
        pdt.titulo = self.e_nome_input.value
        pdt.preco = self.e_preco_input.value
        pdt.estoque = self.e_estoque.value
        pdt.categoria = self.input_categoria.value

        if self.e_barcode_input.value != "" and self.e_barcode_input.value != None:
            pdt.barcode = self.e_barcode_input.value
        if self.selected_file_path:
            pdt.image = filename
            
        self.selected_file_path = None
        AtualisarProduto(int(e.control.key), pdt)
        self.dlg_edit.open = False
        self.page.update()
        self.update_menu()
        self.update_produtos()
        self.page.update()
    
    def close_modal(self, e):
        self.page.close(self.relatorio_alert)
        
    def fecha(self, e):
        self.dialogo.open = False
        self.page.update()
    
    def novo_relatorio(self, e):
        self.relatorio_alert.open = False
        self.page.update()
        rlt = db.query(RelatorioVenda).filter_by(nome=f"relatorio{self.day}").count()
        
        if rlt > 0:
            self.page.open(self.dialogo)
        else:
            estoque_hoje = db.query(Produto).all()
            entrada = []
            
            for i in estoque_hoje:
                entrada.append({
                    "nome": i.titulo,
                    "estoque": i.estoque
                })
            addRelatorio(self.day, entrada)
    
    def add(self, e):
        filename = None
        destination_dir = os.path.join(os.getenv("LOCALAPPDATA"), ".jpInvest/img")
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)
        if self.selected_file_path:
            filename = os.path.basename(self.selected_file_path)
            destination_path = os.path.join(destination_dir, filename)
            try:
                shutil.copy(self.selected_file_path, destination_path)
                self.status_text.value = "Foto copiada com sucesso!"
            except Exception as ex:
                self.status_text.value = f"Erro ao copiar a foto: {ex}"
        self.page.update()
        try:
            CadastrarProduto(
                self.nome_input.value, 
                self.barcode.value, 
                self.categoria.value, 
                self.preco_input.value, 
                self.estoque.value, 
                filename, 
                getRelatorioUnico(self.day).id
            )
        except:
            self.novo_relatorio(e)
            CadastrarProduto(
                self.nome_input.value, 
                self.barcode.value, 
                self.categoria.value, 
                self.preco_input.value, 
                self.estoque.value, 
                filename, 
                getRelatorioUnico(self.day).id
            )
        self.dlg.open = False
        self.page.update()
        self.update_menu()
        self.update_produtos()
        self.selected_file_path = None
    
    def add_item(self, event):
        self.page.open(self.dlg)
    
    def fornecer(self, e):
        updateEstoque(self.fornecer_dialog.data, int(self.quant_estoque.value))
        self.quant_estoque.value = "0"
        self.page.close(self.fornecer_dialog)
        self.update_produtos()
    
    def open_estoque(self, id):
        self.fornecer_dialog.data = id
        self.page.open(self.fornecer_dialog)
    
    def eliminarProoduto(self, id):
        deletarProduto(id)
        self.update_produtos()
        self.update_menu()
    
    def update_produtos(self):
        self.produtos_table.rows = []
        produtos = db.query(Produto).all()
        for produto in produtos:
            imagem_path = os.path.join(self.imagens, produto.image) if produto.image else None
            is_img = os.path.exists(imagem_path) if imagem_path else False
            
            img = ft.Image(
                src=f"{imagem_path}" if is_img else "assets/imagem.png",
                width=100,
                height=45,
                fit=ft.ImageFit.CONTAIN
            )
            
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Container(content=img, alignment=ft.alignment.center)),
                    ft.DataCell(ft.Container(content=ft.Text(produto.titulo, overflow=ft.TextOverflow.ELLIPSIS), expand=True)),
                    ft.DataCell(ft.Container(content=ft.Text(f"{produto.preco} MZN", overflow=ft.TextOverflow.ELLIPSIS), expand=True)),
                    ft.DataCell(ft.Container(content=ft.Text(produto.categoria, overflow=ft.TextOverflow.ELLIPSIS), expand=True)),
                    ft.DataCell(ft.Container(
                        content=ft.Text(
                            f"Estoque: {produto.estoque}",
                            color="green" if int(produto.estoque) > 20 else "red",
                            overflow=ft.TextOverflow.ELLIPSIS
                        ),
                        expand=True
                    )),
                    ft.DataCell(ft.Container(
                        content=ft.Row(
                            [
                                ft.FilledButton("Editar", on_click=lambda e, produto_id=produto.id: self.atualizar(produto_id)),
                                ft.ElevatedButton("Fornecer", on_click=lambda e, produto_id=produto.id: self.open_estoque(produto_id)),
                                ft.OutlinedButton("Excluir", on_click=lambda e, produto_id=produto.id: self.eliminarProoduto(produto_id))
                            ],
                            spacing=5,
                            wrap=True
                        ),
                        expand=True
                    ))
                ]
            )
            self.produtos_table.rows.append(row)
        self.page.update()
    
    def submit2(self, e):
        keyword = self.search.value.lower() if self.search.value else ""
        cat = self.search_categoria.value
        
        self.produtos_table.rows = []
        produtos = db.query(Produto).all()
        
        for produto in produtos:
            if (keyword in produto.titulo.lower() or keyword in (produto.barcode or "").lower() or keyword == "") and (cat == produto.categoria or cat == None or cat == "todas"):
                imagem_path = os.path.join(self.imagens, produto.image) if produto.image else None
                is_img = os.path.exists(imagem_path) if imagem_path else False
                
                img = ft.Image(
                    src=f"{imagem_path}" if is_img else "imagem.png",
                    width=100,
                    height=100,
                    fit=ft.ImageFit.CONTAIN
                )
                
                row = ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Container(content=img, alignment=ft.alignment.center)),
                        ft.DataCell(ft.Container(content=ft.Text(produto.titulo, overflow=ft.TextOverflow.ELLIPSIS), expand=True)),
                        ft.DataCell(ft.Container(content=ft.Text(f"{produto.preco} MZN", overflow=ft.TextOverflow.ELLIPSIS), expand=True)),
                        ft.DataCell(ft.Container(content=ft.Text(produto.categoria, overflow=ft.TextOverflow.ELLIPSIS), expand=True)),
                        ft.DataCell(ft.Container(
                            content=ft.Text(
                                f"Estoque: {produto.estoque}",
                                color="green" if int(produto.estoque) > 20 else "red",
                                overflow=ft.TextOverflow.ELLIPSIS
                            ),
                            expand=True
                        )),
                        ft.DataCell(ft.Container(
                            content=ft.Row(
                                [
                                    ft.FilledButton("Editar", on_click=lambda e, produto_id=produto.id: self.atualizar(produto_id)),
                                    ft.ElevatedButton("Fornecer", on_click=lambda e, produto_id=produto.id: self.open_estoque(produto_id)),
                                    ft.OutlinedButton("Excluir", on_click=lambda e, produto_id=produto.id: self.eliminarProoduto(produto_id))
                                ],
                                spacing=5,
                                wrap=True
                            ),
                            expand=True
                        ))
                    ]
                )
                self.produtos_table.rows.append(row)
        self.page.update()
    
    def build(self):
        return ft.Container(
            expand=True,
            bgcolor="#F0F8FF",
            padding=8,
            content=ft.Column(
                [
                    ft.Container(
                        padding=10,
                        border_radius=10,
                        bgcolor="white",
                        content=ft.Row([
                            ft.Text("Produtos", size=30, weight="bold", color=ft.Colors.INDIGO_400),
                            ft.CupertinoButton(
                                "Adicionar Produto",
                                icon=ft.Icons.ADD,
                                bgcolor=ft.Colors.INDIGO_400,
                                color="white",
                                on_click=self.add_item
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    ),
                    ft.Row([
                        self.search,
                        self.search_categoria,
                        ft.CupertinoButton(
                            "Gestão de Categorias",
                            icon=ft.Icons.CATEGORY,
                            bgcolor=ft.Colors.INDIGO_400,
                            color="white",
                            on_click=self.abrir_add_categoria
                        ),
                        ft.CupertinoButton(
                            "Imprimir Lista",
                            icon=ft.Icons.PRINT,
                            bgcolor=ft.Colors.INDIGO_400,
                            color="white",
                            on_click=self.imprimir_todos
                        )
                    ]),
                    ft.Container(content=self.produtos_list,expand=1)
                ],
                spacing=10,
                expand=True
            )
        )

    def atualizar_tabela_categorias(self):
        self.categorias_table.rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(categoria.nome)),
                    ft.DataCell(
                        ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_color=ft.Colors.INDIGO_400,
                                tooltip="Editar",
                                on_click=lambda e, cat=categoria: self.editar_categoria(cat)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color=ft.Colors.RED,
                                tooltip="Excluir",
                                on_click=lambda e, cat=categoria: self.excluir_categoria(cat)
                            )
                        ], alignment=ft.MainAxisAlignment.END)
                    )
                ]
            ) for categoria in self.categoria_lista
        ]
        self.page.update()
    
    def cancel_categoria_dlg(self, e):
        self.dlg_categoria.open = False
        self.page.update()
    
    def abrir_add_categoria(self, e):
        self.page.open(self.dlg_categoria)
    
    def abrir_add_categoria_dialog(self, e):
        self.nova_categoria_input.value = ""
        self.page.open(self.dlg_add_categoria)
    
    def editar_categoria(self, categoria):
        self.nova_categoria_input.value = categoria.nome
        self.categoria_em_edicao = categoria
        self.dlg_add_categoria.title = ft.Text("Editar Categoria", size=24)
        self.page.open(self.dlg_add_categoria)
    
    def excluir_categoria(self, categoria):
        def confirmar_exclusao(e):
            deleteCategory(categoria.id)
            self.categoria_lista = getCategorias()
            # Atualizar os dropdowns de categorias
            self.categoria.options = [ft.dropdown.Option(categoria.nome) for categoria in self.categoria_lista]
            self.input_categoria.options = [ft.dropdown.Option(categoria.nome) for categoria in self.categoria_lista]
            self.search_categoria.options = [ft.dropdown.Option("todas")] + [ft.dropdown.Option(categoria.nome) for categoria in self.categoria_lista]
            self.page.close(dlg_confirmar)
            self.atualizar_tabela_categorias()
            self.page.show_snack_bar(ft.SnackBar(content=ft.Text(f"Categoria {categoria.nome} excluída com sucesso!")))
        
        dlg_confirmar = ft.AlertDialog(
            title=ft.Text("Confirmar Exclusão"),
            content=ft.Text(f"Deseja realmente excluir a categoria {categoria.nome}?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.close(dlg_confirmar)),
                ft.ElevatedButton("Excluir", on_click=confirmar_exclusao, color=ft.Colors.RED)
            ]
        )
        self.page.open(dlg_confirmar)
    
    def salvar_categoria(self, e):
        if self.nova_categoria_input.value.strip() != "":
            addCategories(self.nova_categoria_input.value.strip())
            self.categoria_lista = getCategorias()
            
            # Atualizar os dropdowns de categorias
            self.categoria.options = [ft.dropdown.Option(categoria.nome) for categoria in self.categoria_lista]
            self.input_categoria.options = [ft.dropdown.Option(categoria.nome) for categoria in self.categoria_lista]
            self.search_categoria.options = [ft.dropdown.Option("todas")] + [ft.dropdown.Option(categoria.nome) for categoria in self.categoria_lista]
            
            # Atualizar a tabela de categorias
            self.atualizar_tabela_categorias()
            
            self.page.close(self.dlg_add_categoria)
            self.page.update()
        else:
            self.page.open(ft.AlertDialog(
                title=ft.Text("Erro"),
                content=ft.Text("O nome da categoria não pode estar vazio."),
                actions=[ft.TextButton("OK", on_click=lambda e: self.page.close())]
            ))

# Função de compatibilidade para o código existente
def produtoBody(page_param, menu):
    return ProductsPage(page_param, menu)