import json

class Venda:
    def __init__(self, cont_data, day, hora, cliente,pagamento):
        self.cont_data = cont_data  # Dados das vendas
        self.day = day              # Data da venda
        self.hora = hora            # Hora da venda
        self.cliente = cliente      # Nome do cliente
        self.pagamento = pagamento  # Método de pagamento
        self.ultima_venda = {}      # Dicionário para armazenar a última venda
        self.produto_id = 1         # Iniciar o ID dos produtos
        
    def pedidos_para_venda(self):
        # Agrupar itens iguais e somar as quantidades
        produtos_agrupados = {}
        for venda in self.cont_data:
            for item in venda["items"]:
                # Verificar se as chaves necessárias estão presentes
                if "nome" in item and "quantidade" in item and "preco" in item and "total" in item:
                    nome = item["nome"]
                    if nome in produtos_agrupados:
                        # Se o item já estiver no dicionário, aumenta a quantidade e o total
                        produtos_agrupados[nome]["quantidade"] += item["quantidade"]
                        produtos_agrupados[nome]["total"] += item["total"]
                    else:
                        # Caso contrário, adiciona o item ao dicionário com um ID único
                        produtos_agrupados[nome] = {
                            "id": self.produto_id,
                            "nome": nome,
                            "preco": item["preco"],
                            "quantidade": item["quantidade"],
                            "total": item["total"],
                            'image':item['image']
                        }
                        self.produto_id += 1  # Incrementar o ID para o próximo produto
                else:
                    print(f"Item inválido: {item}")  # Exibir item que não contém as chaves necessárias

        # Converter o dicionário de produtos agrupados de volta para uma lista
        carrinho_s = list(produtos_agrupados.values())

        # Cálculos
        subtotal = sum(item["total"] for item in carrinho_s)  # Total sem IVA
        iva = subtotal * 0.15  # Exemplo: 15% de IVA
        total = subtotal + iva  # Total com IVA

        # Criando o dicionário da última venda
        self.ultima_venda = {
            'data': f"{self.day} - {self.hora}",
            'produtos': carrinho_s,
            'subtotal': subtotal,
            'iva': iva,
            'total': total,
            'cliente': f"{self.cliente}",
            'troco': 0.0,  # Troco a ser calculado conforme o pagamento
            'metodo': self.pagamento,
            'entregue': f"{total}"
        }

        return self.ultima_venda

    def venda_em_json(self):
        # Retorna a última venda em formato JSON
        return json.dumps(self.ultima_venda, indent=4)
