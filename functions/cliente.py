class Cliente:
    def __init__(self, nome, cpf, data_nasc, endereco, telefone, email):
        self.nome = nome.title()  # Formata o nome para ter a primeira letra de cada palavra em maiúscula
        self.cpf = cpf
        self.data_nasc = data_nasc
        self.endereco = endereco.title()  # Formata o endereço para ter a primeira letra de cada palavra em maiúscula
        self.telefone = telefone
        self.email = email.lower()  # Converte o e-mail para letras minúsculas

    def to_dict(self):
        return {
            "nome": self.nome,
            "cpf": self.cpf,
            "data_nascimento": self.data_nasc.strftime("%d/%m/%Y"),
            "endereco": self.endereco,
            "telefone": self.telefone,
            "email": self.email
        }
