import sqlalchemy
from sqlalchemy.orm import sessionmaker
from models.modelos import Base,Produto,Categoria,Usuario,ProdutoVenda,RelatorioVenda,ContasAbertas,ProdutosConta,SaidaEstoque,EntradaEstoque,RelatorioEstoque
from datetime import datetime
import re
import win32print
import logging
import os
from sqlalchemy import or_,asc,desc
from sqlalchemy.sql import func
from collections import defaultdict
from local import *

info= {
    "app":"JP Invest",
    "data":{
        "nome":"JP Invest",
        "localizacao":"",
        "cidade":"Lichinga",
        "nuit":1667287375365,
        "valor":30000,
        "validade":"17-05-2020",
        "pago":True,
        "tipo":"Farmacia",
        "contacto":877136613,
        "codigo_fatura":"0786",
        "logo":"/assets/logo.png",
        "email":"admin@gmail.com"
    },
    "admin":{
        "nome":"Miguel",
        "apelido":"Araujo",
        "email":"admin@gmail.com",
        "contacto":877136613,
        "username":"admin",
        "password":"1234"
    }

}
# Verifica se está congelado (executável) ou rodando como script


# Altere a string de conexão para MySQL
db_user = 'root'  # usuário do MySQL
db_password = ''  # senha do MySQL (deixe vazio se não houver)
db_host = '127.0.0.1'  # endereço do servidor MySQL
db_name = 'skypdv'  # substitua pelo nome do seu banco de dados

# Cria a engine do SQLAlchemy
engine = sqlalchemy.create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}", echo=False)
ano=datetime.now().year
mes=datetime.now().month
date=datetime.now().day

_validade_software=info['data']['validade']

#vamos verificar se a validade so software e menor que o ano atual
def AnoValido():
    #vamos dividir a string da data
    validade_software=re.split("-",_validade_software)
    print(mes)
    print(int(validade_software[1]))


    if(ano>int(validade_software[2])):
        print("ja expirou ")
        return False
    elif(ano==int(validade_software[2]) and mes<int(validade_software[1])):
        print("vai expirar este ano")
        return True
    elif(ano==int(validade_software[2]) and mes>int(validade_software[1])):
        print("Ja espirou")
        return False
    else:
        print("Ainda Nao espirou ")
        return True

#vamos criar as tabelas dos segintes modelos,"Produto e Usuario"
def CriarTabelas():
    Base.metadata.create_all(engine) 

#criar uma sessao  db
Session=sessionmaker(bind=engine)

db=Session()
def isDataBase():
    try:
        db.query(Usuario).all()
        return True
    except:
        CriarTabelas()
        CadastrarUsuario(n=info['admin']['nome'], 
                         c="admin",
                         u=info['admin']['username'],
                         s_=info['admin']['password']
                         )
        return False
#essas funcoes podem ser importadas em quarquer class

def CadastrarUsuario(n,c,u,s_):
    novoUsuario=Usuario(nome=n,cargo=c,username=u,senha=s_)
    db.add(novoUsuario)
    db.commit()
    print(f"O usuario {n} Foi Cadastrado com sucesso")

def CadastrarProduto(titulo,barcode,categoria, preco, estoque, image,relatorio_id):
    if titulo != "" and preco is not None and estoque != "" and image != "":
        produto = Produto(titulo=titulo,barcode=barcode,categoria=categoria, preco=preco,estoque=estoque, image=image)
        db.add(produto)
        db.commit()
        produto=db.query(Produto).filter_by(titulo=titulo,estoque=estoque,preco=preco).first()
        entrada=EntradaEstoque(nome=produto.titulo,produto_id=produto.id,quantidade=estoque,relatorio_id=relatorio_id)
        db.add(entrada)
        db.commit()
        print(f"O Produto {titulo} foi cadastrado com sucesso")
    else:
        print("Complete todos os campos")

def AtualisarProduto(id,data):
    produto=db.query(Produto).filter_by(id=data.id).first()
    produto.titulo=data.titulo
    produto.preco=data.preco
    produto.estoque=data.estoque
    db.commit()
    print(f"O produto {data.titulo} foi atualizado com sucesso")
#funcoes para estoque

def addConta(c):
    """
    adicionar contas clente/mesa
    """
    conta=ContasAbertas(cliente=c)
    db.add(conta)
    db.commit()

def addItemConta(items,conta_id):
    """
    Adicionar produto à conta
    """
    produto = ProdutosConta(items=items,conta_id=conta_id)
    db.add(produto)
    db.commit()

def serialize(obj):
    """Converte objetos que não são serializáveis em JSON para strings."""
    if isinstance(obj, datetime):
        return obj.isoformat()  # Converte datetime para string no formato ISO 8601
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

def default_serializer(obj):
    """Função para serializar objetos que não são diretamente serializáveis para JSON."""
    if isinstance(obj, datetime):
        return obj.isoformat()  # Converte datetime para string no formato ISO 8601
    raise TypeError(f"Tipo {type(obj)} não é serializável para JSON")

def ContaInfoToVenda(id=1):
    banco=sessionmaker(bind=engine)
    bb=banco()
    
    pedidos = bb.query(ProdutosConta).filter_by(conta_id=id).all()
    
    # Converte a lista de pedidos em dicionários
    pedidos_json = [pedido.__dict__ for pedido in pedidos]
    
    # Calcule os totais diretamente dos pedidos
    return pedidos_json
   

def userLoged():
        try:
            user=db.query(Usuario).filter_by(username=get_logged_user()['username']).first()
            return user
        except:
            return None
        
def ContaInfo(id=1):
    banco=sessionmaker(bind=engine)
    bb=banco()
    pedidos = bb.query(ProdutosConta).filter_by(conta_id=id).all()
    
    # Converte a lista de pedidos em dicionários
    pedidos_json = [pedido.__dict__ for pedido in pedidos]
    
    # Remove o campo SQLAlchemy _sa_instance_state
    for pedido in pedidos_json:
        pedido.pop('_sa_instance_state', None)
    print(pedidos)
    # Retorna a lista de pedidos diretamente para calcular os totais
    return calcular_totais(pedidos_json)  # Passa diretamente a lista de pedidos

def calcular_totais(dados):
    # Se 'dados' já for um dicionário de totais, retorne-o diretamente
    if isinstance(dados, dict) and 'total_dinheiro' in dados:
        return dados

    # Caso contrário, continuamos com a lógica padrão para calcular os totais
    total_dinheiro = 0.0
    total_produtos = 0
    total_pedidos = len(dados)  # Total de pedidos é o comprimento da lista

    for pedido in dados:
        # Para cada pedido, somamos o total de dinheiro e total de produtos
        for item in pedido['items']:
            total_dinheiro += item['total']
            total_produtos += item['quantidade']
    
    return {
        "total_dinheiro": total_dinheiro,
        "total_produtos": total_produtos,
        "total_pedidos": total_pedidos
    }


def getContas():
    try:
        contas = db.query(ContasAbertas).all() 
        return contas
    except:
        return [] 
    
def incrementarStoque(id_produto,qtd,relatorio_id):
    produto=db.query(Produto).filter_by(id=id_produto).first()
    if(produto):
        p=produto.estoque
        produto.estoque=produto.estoque+qtd
        entrada=EntradaEstoque(nome=produto.titulo,produto_id=produto.id,quantidade=qtd,relatorio_id=relatorio_id)
        db.add(entrada)
        db.commit()
        return f"Estoque atualizado de {p} para {produto.estoque}"
    else:
        return f"O estoque atual e menor que \n a quantidade inserida"
def decrementarStoque(id_produto,qtd,relatorio_id):
    produto=db.query(Produto).filter_by(id=id_produto).first()
    if(produto):
        p=produto.estoque
        if produto.estoque>=qtd:
            produto.estoque=produto.estoque-qtd
            saida=SaidaEstoque(nome=produto.titulo,produto_id=produto.id,quantidade=qtd,relatorio_id=relatorio_id)
            db.add(saida)
            db.commit()
            return f"Estoque atualizado de {p} para {produto.estoque}"
        else:
            return f"O estoque atual e menor que \n a quantidade inserida"
    else:
        print("O produto nao foi encontrado")
        
def deduceStockCart(carrinho,relatorio_id):
    for i in carrinho:
        #achar o produto no banco
        produto=db.query(Produto).filter_by(titulo=i['nome']).first()
        #reduzir o estoque com a funcao abaixo, para cada item
        decrementarStoque(produto.id,i['quantidade'],relatorio_id)

def checkCartStock(carrinho):
    #ir no banco verificar se o estoque e suficiente para a venda
    for i in carrinho:
        resultado={}
        produto=db.query(Produto).filter_by(titulo=i['nome']).first()
        #print(produto.estoque)
        #se o produto.estoque for maior que quantidade de item retorna True
        if produto.estoque>=i['quantidade']:
            print("estoque e suficiente")
            resultado={"msg":"O estoque e suficiente","resultado":True}
        else:
            resultado={"msg":"O estoque nao e suficiente","resultado":False,"produto":i['nome']}
        return resultado

def verProdutos():
    return db.query(Produto).all()

def pegarporCategoria(categoria: str):
    return db.query(Produto).filter_by(categoria=categoria).all()

def pesquisaProduto(query):
    return db.query(Produto).filter(
    or_(
        Produto.titulo.like(f"%{query}%"),
        Produto.categoria.like(f"%{query}%")
    )
).all()
def todosUsers():
    return db.query(Usuario).all()
def verCaixa():
    return db.query(Usuario).filter_by(cargo="Caixa").all()
def acharUmProduto(id):
    return db.query(Produto).filter_by(id=id).first()

def acharUmProduto_barcode(barcode):
    return db.query(Produto).filter_by(barcode=barcode).first()
    
def deletarProduto(id):
    p=db.query(Produto).filter_by(id=id).first()
    db.delete(p)
    db.commit()
    print(f"O produto {p.titulo} foi deletado com sucesso!")

def addVenda(venda):
    db.add(venda)
    db.commit()
    print("Venda Feita")

def verVendas():
    return db.query(ProdutoVenda).all()

def addRelatorio(day, entrada=None):
    relatorio=RelatorioVenda(nome=f"relatorio{day}",data=day,caixa="admin",funcionario=userLoged().nome if userLoged() else "admin")
    db.add(relatorio)
    db.commit()
    
    if entrada:
        for item in entrada:
            entrada_estoque = EntradaEstoque(
                nome=item['nome'],
                quantidade=item['estoque'],
                produto_id=db.query(Produto).filter_by(titulo=item['nome']).first().id,
                relatorio_id=relatorio.id
            )
            db.add(entrada_estoque)
        db.commit()
    print("Relatorio Cadastrado")
    return relatorio

def RemoveRelatorio(day):
    relatorio=db.query(RelatorioVenda).filter_by(data=day).first()
    db.delete(relatorio)
    db.commit()
    print("Relatorio Deletado")


def getRelatorios():
    return db.query(RelatorioVenda).order_by(desc(RelatorioVenda.id)).all()

def getRelatorioUnico(day):
    return db.query(RelatorioVenda).filter_by(data=day).first()

def getRelatorioUnicoByID(id):
    return db.query(RelatorioVenda).filter_by(id=id).first()

def totalRelatorioMoney(day):
    total=0.00
    for v in getRelatorioUnico(day).vendas:
        total+=v.total_money  
    return total
def deletarRelatorio(id):
    p=db.query(RelatorioVenda).filter_by(id=id).first()
    db.delete(p)
    db.commit()

def deletarVendas(id):
    p=db.query(ProdutoVenda).filter_by(id=id).first()
    db.delete(p)
    db.commit()

def totalVendaMoney(id):
    produto=db.query(ProdutoVenda).filter_by(id=id).first()
    total=0.00
    for i in produto.produtos:
        total+=i['total']   
    return total

def totalVendaMoneyRelatorio(day):
    try:
        relatorio=db.query(RelatorioVenda).filter_by(data=day).first()
        total=0.00
        # Soma apenas o total das vendas
        for venda in relatorio.vendas:
            total+=totalVendaMoney(venda.id)
        money=f"{total:,.2f}".replace(",", " ").replace(".", ",")
        return money
    except:
        return 0

def totalVendaProdutos(id):
    produto=db.query(ProdutoVenda).filter_by(id=id).first()
    total=0
    for i in produto.produtos:
        total+=1   
    return total

def getTotalMoneyCart(carrinho):
    total=0.00
    for i in carrinho:
        total+=i['total']
    return total


def getTotalTipoCart(carinho):
    tipo=0
    for i in carinho:
        tipo+=1
    return tipo

def getTotalQuantCart(carrinho):
    quant=0
    for i in carrinho:
        quant+=i["quantidade"]
    return quant

def itensListsimple(id):
    venda=db.query(ProdutoVenda).filter_by(id=id).first()
    
    produtos=[]
    for i in venda.produtos:
        produtos.append(f"{i['nome']}-{i['quantidade']}")
    novas_string=", ".join(produtos)
    return novas_string
def formatToMoney(data):
    money=f"{data:,.2f}".replace(",", " ").replace(".", ",")
    return money
def getOneSale(id):
    return db.query(ProdutoVenda).filter_by(id=id).first()

def StartLogin(username,senha):
    user=db.query(Usuario).filter_by(username=username,senha=senha).first()
    if user != None:

        return user
    else:
        return False
    

def loged():
    return ''
def changePassword(user,nova):
    user.senha=nova
    db.commit()
    print("senha foi modificada com sucesso")
def getFuncionarios():
    funcionarios=db.query(Usuario).all()
    return funcionarios

def excluir_funcionario(id):
    session = Session()
    try:
        funcionario = session.query(Usuario).filter_by(id=id).first()
        session.delete(funcionario)
        session.commit()
    except:
        print("erro ao excluir funcionario")
    finally:
        session.close()

def cadastrar_metodo_pagamento(nome, descricao):
    session = Session()
    try:
        metodo = MetodoPagamento(nome=nome, descricao=descricao)
        session.add(metodo)
        session.commit()
    except:
        print("erro ao cadastrar método de pagamento")
    finally:
        session.close()

def excluir_metodo_pagamento(id):
    session = Session()
    try:
        metodo = session.query(MetodoPagamento).filter_by(id=id).first()
        session.delete(metodo)
        session.commit()
    except:
        print("erro ao excluir método de pagamento")
    finally:
        session.close()

def get_metodos_pagamento():
    session = Session()
    try:
        metodos = session.query(MetodoPagamento).all()
        return metodos
    except:
        print("erro ao buscar métodos de pagamento")
        return []
    finally:
        session.close()
def userUpdate(data):
    user=loged()
    can=False
    if data['nome'] != "":
        user.nome=data['nome']
        can=True
    if data['apelido'] != "":    
        user.apelido=data['apelido']
        can=True
    if data['telefone'] != "":
        user.telefone=data["telefone"]
        can=True
    if data['email'] != "":
        user.email=data['email']
        can=True
    if data['username'] != "":
        user.username=data['username']
        can=True
    if can:
        db.commit()
        print("dados atualizados")
    else:
        print("Formaulario esta")


def formatar_dados(dados):
    import json

    # Verifica se 'dados' é uma string e precisa ser convertido
    if isinstance(dados, str):
        print(dados)
        dados = json.loads(dados)

    
    # Cria uma lista para armazenar as linhas da string de retorno
    linhas = []
    
    # Adiciona os dados formatados à lista
    linhas.append("-------JP INVEST------")
    linhas.append(f"Data: ")
    linhas.append("--------------------------")
    linhas.append("Produtos:")
    
    for produto in dados['produtos']:
        linhas.append(f"  Nome: {produto['nome']}")
        linhas.append(f"  Preço: {produto['preco']:.2f} MT")
        linhas.append(f"  Quantidade: {produto['quantidade']}")
        linhas.append("--------------------------")
        
    linhas.append(f"Subtotal: {dados['subtotal']:.2f} MT")
    linhas.append(f"IVA: {dados['iva']:.2f} MT")
    linhas.append(f"Total: {dados['total']:.2f} MT")
    linhas.append("-------BlueSpark MZ-------")
    
    # Junta todas as linhas em uma única string
    return "\n".join(linhas)
def calcular_totais_por_metodo(relatorio):
    # Inicializar um dicionário para armazenar o total por método de pagamento
    totais_por_metodo = {
        'Cash': 0.0,
        'MPesa': 0.0,
        'E-mola': 0.0,
        'Izi': 0.0,
        'Paga Facil': 0.0,
        'Ponto 24': 0.0,
        'POS BIM': 0.0,
        'POS BCI': 0.0,
        'POS ABSA': 0.0,
        'POS MOZA BANCO': 0.0,
        'POS StanderBank': 0.0,
        'M-Cash': 0.0
    }
    
    # Iterar sobre as vendas no relatório
    for venda in relatorio['vendas']:
        metodo = venda['metodo']
        total = float(venda['total'].replace(',', '.'))  # Converter o total para numérico
        
        # Somar o total para o método de pagamento existente
        if metodo in totais_por_metodo:
            totais_por_metodo[metodo] += total
        else:
            totais_por_metodo[metodo] = total  # Adiciona novos métodos, caso apareçam
    
    return totais_por_metodo
def garantir_inteiro(valor):
    try:
        return int(valor)
    except (ValueError, TypeError):
        return 20

def calcular_quantidade_saida(estoque_inicial, estoque_final):
    # Garante que os valores são inteiros, mesmo que sejam strings ou tipos inválidos
    estoque_inicial = garantir_inteiro(estoque_inicial)
    estoque_final = garantir_inteiro(estoque_final)

    # Calcula a quantidade saída e garante que não seja negativa
    quantidade_saida = estoque_inicial - estoque_final

    return quantidade_saida

def calcular_estoque_restante(estoque_inicial, quantidade_saida):
    # Garante que estoque_inicial é um inteiro
    estoque_inicial = garantir_inteiro(estoque_inicial)
    
    # Calcula o estoque restante e garante que não seja negativo
    estoque_restante = estoque_inicial - quantidade_saida
    if estoque_restante < 0:
        estoque_restante = 0

    return estoque_restante



def getSaidas(relatorio_id): 
    relatorio = db.query(RelatorioVenda).filter_by(id=relatorio_id).first()
    if not relatorio:
        return {}
    
    # Usa o relacionamento direto saida_estoque
    produtos_dict = defaultdict(int)
    for saida in relatorio.saida_estoque:
        produtos_dict[saida.nome] += saida.quantidade

    return produtos_dict

def getEntradas(relatorio_id):
    relatorio = db.query(RelatorioVenda).filter_by(id=relatorio_id).first()
    if not relatorio:
        return {}
    
    # Usa o relacionamento direto entrada_estoque
    produtos_dict = defaultdict(int)
    for entrada in relatorio.entrada_estoque:
        produtos_dict[entrada.nome] += entrada.quantidade

    return produtos_dict

def getHistoricoEstoque(relatorio_id):
    """
    Esta função retorna uma lista de produtos movimentados no estoque usando os relacionamentos
    entrada_estoque e saida_estoque do RelatorioVenda.
    """
    relatorio = db.query(RelatorioVenda).filter_by(id=relatorio_id).first()
    if not relatorio:
        return []

    # Usa os relacionamentos diretos do RelatorioVenda
    entradas = relatorio.entrada_estoque
    saidas = relatorio.saida_estoque

    # Mapeia entradas e saídas por produto
    entradas_por_produto = {}
    for entrada in entradas:
        entradas_por_produto[entrada.produto_id] = entradas_por_produto.get(entrada.produto_id, 0) + entrada.quantidade

    saidas_por_produto = {}
    for saida in saidas:
        saidas_por_produto[saida.produto_id] = saidas_por_produto.get(saida.produto_id, 0) + saida.quantidade

    # Lista para armazenar os dados do histórico
    historico = []

    # Obtém produtos únicos das movimentações
    produtos_ids = set(list(entradas_por_produto.keys()) + list(saidas_por_produto.keys()))
    produtos = db.query(Produto).filter(Produto.id.in_(produtos_ids)).all()

    # Calcula os dados para cada produto
    for produto in produtos:
        entrada = entradas_por_produto.get(produto.id, 0)
        saida = saidas_por_produto.get(produto.id, 0)
        
        estoque_inicial = produto.estoque + saida - entrada
        historico.append({
            "nome": produto.titulo,
            "estoque_inicial": estoque_inicial,
            "entrada": entrada,
            "saida": saida,
            "estoque_atual": produto.estoque,
        })

    return historico

def getRelatorioEstoque(relatorio_id):
    relatorio = db.query(RelatorioEstoque).filter_by(relatorio_id=relatorio_id).first()
    if relatorio:
        return relatorio.historico
    else:
        return []  # Se não encontrar o relatório, retorna uma lista vazia

#get all categories
def getCategorias():
    return db.query(Categoria).all()

def addCategories(category:str):
    cat=Categoria(nome=category)
    db.add(cat)
    db.commit()

def deleteCategory(id):
    cat=db.query(Categoria).filter_by(id=id).first()
    db.delete(cat)
    db.commit()

def updateEstoque(produto_id, quantidade):
    """
    Atualiza o estoque de um produto
    
    Args:
        produto_id: ID do produto a ser atualizado
        quantidade: Nova quantidade a ser adicionada ao estoque
    """
    produto = db.query(Produto).filter_by(id=produto_id).first()
    if produto:
        estoque_atual = int(produto.estoque)
        produto.estoque = estoque_atual + quantidade
        db.commit()
        print(f"Estoque do produto {produto.titulo} atualizado para {produto.estoque}")
        return True
    return False

def abrir_gaveta(printer_name="XP-80C", comando=b'\x1b\x70\x00\x19\xfa'):
    try:
        hPrinter = win32print.OpenPrinter(printer_name)
        hJob = win32print.StartDocPrinter(hPrinter, 1, ("Abrir Gaveta", None, "RAW"))
        win32print.StartPagePrinter(hPrinter)

        win32print.WritePrinter(hPrinter, comando)

        win32print.EndPagePrinter(hPrinter)
        win32print.EndDocPrinter(hPrinter)
        logging.info("Gaveta aberta com sucesso.")
        return True, "Sucesso", "Gaveta aberta com sucesso."
    except Exception as e:
        logging.error(f"Erro ao abrir a gaveta: {e}")
        return False, "Erro", f"Erro ao abrir a gaveta: {e}"
    finally:
        win32print.ClosePrinter(hPrinter)

def print_receipt(dados, printer_name="XP-80C"):
    try:
        hPrinter = win32print.OpenPrinter(printer_name)
        hJob = win32print.StartDocPrinter(hPrinter, 1, ("Receipt", None, "RAW"))
        win32print.StartPagePrinter(hPrinter)
        

        esc_pos_commands = b'\x1b\x40'  # Inicia o documento (ESC @)
        esc_pos_commands += b'\x1b\x45\x01'  # Habilita negrito
        esc_pos_commands += b'JP INVEST, LTD!\n'
        esc_pos_commands += b'\x1b\x45\x00'  # Desabilita negrito
        esc_pos_commands += f'Data: {dados['data']}\n'.encode('utf-8')
        esc_pos_commands += b'----------------------------------------------\n'

        esc_pos_commands += b"Qnt   Nome   Total\n"
        esc_pos_commands += b'----------------------------------------------\n'
        for produto in dados['produtos']:
            esc_pos_commands += f"{produto['quantidade']}x {produto['nome']} - {produto['total']:.2f} MZN\n".encode('utf-8')
        esc_pos_commands += b'\x1b\x45\x01'  # Habilita negrito
        esc_pos_commands += f'TOTAL SAO {dados["total"]:.2f} MZN\n'.encode('utf-8')
        esc_pos_commands += b'\x1b\x45\x00'  # Desabilita negrito
        esc_pos_commands += b'---\n'
        esc_pos_commands += f'Subtotal: {dados["subtotal"]:.2f} MZN\n'.encode('utf-8')
        esc_pos_commands += f'Taxa de IVA: {dados["iva"]:.2f} MZN\n'.encode('utf-8')
        esc_pos_commands += f'Total : {dados["total"]:.2f} MZN\n'.encode('utf-8')
        esc_pos_commands += b'------------------------------------------------\n'
        esc_pos_commands += f"Metode de Pagamento: {dados['metodo']}\n".encode('utf-8')
        esc_pos_commands += f'Valor Entrege : {dados["entregue"]}\n'.encode('utf-8')
        if int(dados['troco'])>0:
            esc_pos_commands += f'Troco : {dados["troco"]:.2f}\n'.encode('utf-8')
        esc_pos_commands += b'-----------------------------------------------\n'
        esc_pos_commands += f'Cliente/Mesa: {dados['cliente']}\n'.encode('utf-8')
        esc_pos_commands += b'-----------------Volte-Sempre-------------------\n'
        esc_pos_commands += b'From ElectroGulamo - sistemas\n'

        esc_pos_commands += b'\x1d\x56\x41\x00'
        if dados['metodo'] =='Cash':
            print('cash')
            abrir_gaveta()

        

        win32print.WritePrinter(hPrinter, esc_pos_commands)

        win32print.EndPagePrinter(hPrinter)
        win32print.EndDocPrinter(hPrinter)
        logging.info("Recibo impresso com sucesso.")
        
        return True, "Sucesso", "Recibo impresso com sucesso."
    except Exception as e:
        logging.error(f"Erro ao imprimir recibo: {e}")
        return False, "Erro", f"Erro ao imprimir recibo: {e}"
    finally:
        win32print.ClosePrinter(hPrinter)