from sqlalchemy.orm import declarative_base,relationship
from sqlalchemy import Column, String, Integer, Float, DateTime,JSON,ForeignKey
#Criado por Ghost 04- Diqui Joaquim
from datetime import datetime

Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    nome = Column(String(32))
    cargo = Column(String(100))
    username=Column(String(20))
    senha= Column(String(100))

class Produto(Base):
    __tablename__ = "produtos"
    id = Column(Integer, primary_key=True)
    titulo = Column(String(100))
    preco = Column(Float)
    barcode=Column(String(30))
    estoque = Column(Integer)
    image=Column(String(100))
    quantidade_venda=Column(Integer,nullable=True)
    categoria_id=Column(Integer, ForeignKey("categorias.id"))
    categoria=Column(String(50))

class Categoria(Base):
    __tablename__="categorias"
    id=Column(Integer,primary_key=True)
    nome=Column(String(30))
    produtos=relationship("Produto", backref="produtos", cascade="all, delete")

class EntradaEstoque(Base):
    __tablename__ = "entradas_estoque"
    id = Column(Integer, primary_key=True)
    nome=Column(String(50),nullable=True)
    produto_id = Column(Integer, ForeignKey('produtos.id'), nullable=False)
    quantidade = Column(Integer, nullable=False)
    data_entrada = Column(DateTime, default=datetime.now)
    # Relacionamento com o Produto
    produto = relationship("Produto", backref="entradas", cascade="all, delete")
    relatorio_id = Column(Integer, ForeignKey("relatorios.id"), nullable=True)
   
# Tabela de Saída no Estoque
class SaidaEstoque(Base):
    __tablename__ = "saidas_estoque"
    id = Column(Integer, primary_key=True)
    nome=Column(String(50))
    produto_id = Column(Integer, ForeignKey('produtos.id'), nullable=False)
    quantidade = Column(Integer, nullable=False)
    data_saida = Column(DateTime, default=datetime.now)
    # Relacionamento com o Produto
    produto = relationship("Produto", backref="saidas", cascade="all, delete")
    relatorio_id = Column(Integer, ForeignKey("relatorios.id"), nullable=True)

    
class RelatorioVenda(Base):
    __tablename__="relatorios"
    id=Column(Integer,primary_key=True)
    nome=Column(String(20))
    data=Column(String(22))
    caixa=Column(String(50))
    vendas=relationship("ProdutoVenda", backref="relatorios",cascade="all, delete")
    funcionario=Column(String(40))
    entrada = Column(JSON)
    saida = Column(JSON,nullable=True)
    entrada_estoque = relationship("EntradaEstoque", backref="relatorio",cascade="all, delete")
    saida_estoque = relationship("SaidaEstoque", backref="relatorio",cascade="all, delete")

class ProdutoVenda(Base):
    __tablename__="vendas"
    id=Column(Integer,primary_key=True)
    data=Column(DateTime)
    hora=Column(String(10),default="08:00")
    produtos = Column(JSON, nullable=False)
    total_item=Column(Integer)
    total_money=Column(Float)
    relatorio_id=Column(Integer, ForeignKey("relatorios.id"))
    cliente=Column(String(50))
    funcionario=Column(String(40))
    metodo=Column(String(40))

class ProdutosConta(Base):
    __tablename__ = "produtos_conta"
    
    id = Column(Integer, primary_key=True)
    data = Column(DateTime, default=datetime.now)
    items = Column(JSON, nullable=False)  # Lista de itens (JSON)
    conta_id = Column(Integer, ForeignKey('contas.id'), nullable=False)  # Chave estrangeira para ContasAbertas
    
    # Relacionamento com a tabela ContasAbertas (muitos para um)
    conta = relationship("ContasAbertas", back_populates="produtos")


class ContasAbertas(Base):
    __tablename__ = "contas"
    
    id = Column(Integer, primary_key=True)
    cliente = Column(String(100), nullable=False, unique=True)
    
    # Relacionamento com ProdutosConta (um para muitos)
    produtos = relationship("ProdutosConta", back_populates="conta", cascade="all, delete")

class RelatorioEstoque(Base):
    __tablename__ = 'relatorio_estoque'

    id = Column(Integer, primary_key=True, autoincrement=True)
    relatorio_id = Column(Integer, nullable=False, unique=True)  # ID único para o relatório
    historico = Column(JSON, nullable=False)  # Coluna para armazenar a lista completa como JSON
    