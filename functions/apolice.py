from datetime import datetime

class Apolice:
    def __init__(self, numero, cliente_cpf, tipo_seguro, dados_seguro, valor_mensal):
        self.numero = numero
        self.cliente_cpf = cliente_cpf
        self.tipo_seguro = tipo_seguro
        self.dados_seguro = dados_seguro
        self.valor_mensal = valor_mensal
        self.data_emissao = datetime.now().strftime("%d/%m/%Y")
