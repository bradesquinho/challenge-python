class Seguro:
    def __init__(self, tipo, dados):
        self.tipo = tipo
        self.dados = dados

class Automovel(Seguro):
    def __init__(self, modelo, ano, placa):
        modelo = modelo.title()  # Formata o modelo para ter a primeira letra de cada palavra em maiúscula
        placa = placa.upper()     # Converte a placa para letras maiúsculas
        super().__init__("Automóvel", {"modelo": modelo, "ano": ano, "placa": placa})

class Residencial(Seguro):
    def __init__(self, endereco, valor):
        endereco = endereco.title()  # Formata o endereço para ter a primeira letra de cada palavra em maiúscula
        super().__init__("Residencial", {"endereco": endereco, "valor": valor})

class Vida(Seguro):
    def __init__(self, valor_segurado, beneficiarios):
        beneficiarios = [b.title() for b in beneficiarios]  # Formata cada beneficiário para ter a primeira letra em maiúscula
        super().__init__("Vida", {"valor_segurado": valor_segurado, "beneficiarios": beneficiarios})
