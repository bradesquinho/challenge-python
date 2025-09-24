import json
import re
from datetime import datetime

def validar_cpf(cpf):
    # Implementação do algoritmo de validação de CPF
    cpf = ''.join(filter(str.isdigit, cpf))
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    def calcular_digito(cpf, peso):
        soma = sum(int(digito) * peso for digito, peso in zip(cpf, range(peso, 1, -1)))
        resto = soma % 11
        return '0' if resto < 2 else str(11 - resto)

    digito1 = calcular_digito(cpf[:9], 10)
    digito2 = calcular_digito(cpf[:9] + digito1, 11)

    return cpf[-2:] == digito1 + digito2

def validar_placa(placa):
    placa = placa.upper()
    return bool(
        re.match(r'^[A-Z]{3}[0-9]{4}$', placa) or
        re.match(r'^[A-Z]{3}[0-9][A-Z][0-9]{2}$', placa)
    )

def salvar_dados(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

def carregar_dados(arquivo):
    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
