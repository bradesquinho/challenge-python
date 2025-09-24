
import os
import json
from dao import ClienteDAO, SeguroDAO, ApoliceDAO, SinistroDAO

BASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'json')

def importar_json(nome):
    path = os.path.join(BASE_PATH, nome)
    if not os.path.exists(path):
        print(f"Arquivo não encontrado: {path}")
        return []
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def migrar_clientes():
    print('Migrando clientes...')
    clientes = importar_json('clientes.json')
    cpf_to_id = {}
    for c in clientes:
        try:
            cliente_db = {
                'nome': c['nome'],
                'cpf': c['cpf'],
                'telefone': c.get('telefone', ''),
                'email': c.get('email', ''),
                'data_nasc': c.get('data_nascimento', ''),
                'endereco': c.get('endereco', '')
            }
            cliente_id = ClienteDAO.criar(cliente_db)
            cpf_to_id[c['cpf']] = cliente_id
            print(f"Cliente {c['cpf']} migrado com id {cliente_id}")
        except Exception as e:
            print(f"Erro ao migrar cliente {c}: {e}")
    return cpf_to_id

def migrar_seguros(cpf_to_id):
    print('Migrando seguros...')
    seguros = importar_json('seguros.json')
    seguro_key_to_id = {}
    for idx, s in enumerate(seguros):
        try:
            cliente_id = cpf_to_id.get(s['cpf_cliente'])
            if not cliente_id:
                print(f"Cliente não encontrado para seguro: {s}")
                continue
            tipo = s['tipo']
            dados = s.get('dados', {})
            # Mapeamento dos campos para o banco
            descricao = None
            valor = None
            detalhes = json.dumps(dados, ensure_ascii=False)
            if tipo == 'Vida':
                valor = dados.get('valor_segurado')
            elif tipo == 'Residencial':
                valor = dados.get('valor')
                descricao = dados.get('endereco')
            seguro_db = {
                'tipo': tipo,
                'descricao': descricao,
                'valor': valor,
                'detalhes': detalhes,
                'cliente_id': cliente_id
            }
            seguro_id = SeguroDAO.criar(seguro_db)
            seguro_key_to_id[(s['cpf_cliente'], tipo, idx)] = seguro_id
            print(f"Seguro {tipo} do cliente {s['cpf_cliente']} migrado com id {seguro_id}")
        except Exception as e:
            print(f"Erro ao migrar seguro {s}: {e}")
    return seguro_key_to_id

def migrar_apolices(cpf_to_id, seguro_key_to_id):
    print('Migrando apólices...')
    apolices = importar_json('apolices.json')
    numero_to_id = {}
    for a in apolices:
        try:
            cliente_id = cpf_to_id.get(a['cliente_cpf'])
            if not cliente_id:
                print(f"Cliente não encontrado para apólice: {a}")
                continue
            tipo = a['tipo_seguro']
            # Encontrar o seguro correspondente
            seguro_id = None
            for (cpf, t, idx), sid in seguro_key_to_id.items():
                if cpf == a['cliente_cpf'] and t == tipo:
                    seguro_id = sid
                    break
            if not seguro_id:
                print(f"Seguro não encontrado para apólice: {a}")
                continue
            apolice_db = {
                'cliente_id': cliente_id,
                'seguro_id': seguro_id,
                'data_emissao': a.get('data_emissao', ''),
                'status': 'ativa'
            }
            apolice_id = ApoliceDAO.criar(apolice_db)
            numero_to_id[a['numero']] = apolice_id
            print(f"Apólice {a['numero']} migrada com id {apolice_id}")
        except Exception as e:
            print(f"Erro ao migrar apólice {a}: {e}")
    return numero_to_id

def migrar_sinistros(numero_to_id):
    print('Migrando sinistros...')
    sinistros = importar_json('sinistros.json')
    for s in sinistros:
        try:
            apolice_id = numero_to_id.get(s['numero_apolice'])
            if not apolice_id:
                print(f"Apólice não encontrada para sinistro: {s}")
                continue
            sinistro_db = {
                'apolice_id': apolice_id,
                'data_ocorrencia': s.get('data', ''),
                'descricao': s.get('descricao', ''),
                'status': s.get('status', '')
            }
            sid = SinistroDAO.criar(sinistro_db)
            print(f"Sinistro da apólice {s['numero_apolice']} migrado com id {sid}")
        except Exception as e:
            print(f"Erro ao migrar sinistro {s}: {e}")

def main():
    print('--- Migração de JSON para SQLite ---')
    cpf_to_id = migrar_clientes()
    seguro_key_to_id = migrar_seguros(cpf_to_id)
    numero_to_id = migrar_apolices(cpf_to_id, seguro_key_to_id)
    migrar_sinistros(numero_to_id)
    print('Migração concluída!')

if __name__ == '__main__':
    main()
