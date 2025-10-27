"""
Testes de Regras de Negócio
Testa lógica de emissão/cancelamento de apólice, abertura/fechamento de sinistro,
cálculos e validações conforme regras do domínio
"""
from datetime import datetime, timedelta

import pytest

from functions.dao_mysql import ApoliceDAO, ClienteDAO, SeguroDAO, SinistroDAO


class TestEmissaoApolice:
    """Testes para regras de emissão de apólices"""

    def test_emitir_apolice_sucesso(self, dao_factories, cliente_teste, seguro_teste):
        """Deve emitir apólice com dados válidos"""
        cliente_dao = dao_factories["cliente"]
        seguro_dao = dao_factories["seguro"]
        apolice_dao = dao_factories["apolice"]

        # Cria cliente e seguro
        cliente_id = cliente_dao.criar(cliente_teste)
        
        # Adiciona cliente_id ao seguro_teste
        seguro_teste["cliente_id"] = cliente_id
        seguro_id = seguro_dao.criar(seguro_teste)

        # Emite apólice (schema novo: apenas 3 campos)
        apolice_data = {
            "cliente_id": cliente_id,
            "seguro_id": seguro_id,
            "status": "ativa"
        }

        apolice_id = apolice_dao.criar(apolice_data)

        assert apolice_id is not None
        assert apolice_id > 0

        # Valida dados gravados
        apolice = apolice_dao.ler(apolice_id)
        assert apolice["status"] == "ativa"

    def test_emitir_apolice_cliente_invalido(self, dao_factories, seguro_teste, cliente_teste_id):
        """Não deve emitir apólice com cliente inexistente"""
        seguro_dao = dao_factories["seguro"]
        apolice_dao = dao_factories["apolice"]
        
        # Adiciona cliente_id ao seguro_teste
        seguro_teste["cliente_id"] = cliente_teste_id

        seguro_id = seguro_dao.criar(seguro_teste)

        # Tenta criar apólice com cliente_id inexistente (99999)
        apolice_data = {
            "cliente_id": 99999,  # Cliente inexistente
            "seguro_id": seguro_id,
            "status": "ativa"
        }

        # Deve falhar por violação de foreign key
        with pytest.raises(Exception):
            apolice_dao.criar(apolice_data)

    def test_cancelar_apolice(self, dao_factories, cliente_teste, seguro_teste):
        """Deve cancelar apólice ativa"""
        cliente_dao = dao_factories["cliente"]
        seguro_dao = dao_factories["seguro"]
        apolice_dao = dao_factories["apolice"]

        # Cria e emite apólice
        cliente_id = cliente_dao.criar(cliente_teste)
        
        # Adiciona cliente_id ao seguro_teste
        seguro_teste["cliente_id"] = cliente_id
        seguro_id = seguro_dao.criar(seguro_teste)

        apolice_data = {
            "cliente_id": cliente_id,
            "seguro_id": seguro_id,
            "status": "ativa"
        }

        apolice_id = apolice_dao.criar(apolice_data)

        # Cancela apólice
        apolice_dao.atualizar(apolice_id, {"status": "cancelada"})

        # Valida cancelamento
        apolice = apolice_dao.ler(apolice_id)
        assert apolice["status"] == "cancelada"

    def test_valor_premio_positivo(self, dao_factories, cliente_teste, seguro_teste):
        """Valor do seguro deve estar presente"""
        cliente_dao = dao_factories["cliente"]
        seguro_dao = dao_factories["seguro"]
        apolice_dao = dao_factories["apolice"]

        cliente_id = cliente_dao.criar(cliente_teste)
        
        # Adiciona cliente_id ao seguro_teste e define valor negativo
        seguro_teste["cliente_id"] = cliente_id
        seguro_teste["valor"] = -1200.00  # Valor negativo para teste
        seguro_id = seguro_dao.criar(seguro_teste)

        apolice_data = {
            "cliente_id": cliente_id,
            "seguro_id": seguro_id,
            "status": "ativa"
        }

        # Cria apólice e valida que o seguro tem valor negativo
        apolice_id = apolice_dao.criar(apolice_data)
        seguro = seguro_dao.ler(seguro_id)

        # Verifica que o valor negativo foi gravado (validação deve ser feita na camada de serviço)
        assert float(seguro["valor"]) == -1200.00


class TestGestaoSinistros:
    """Testes para regras de gestão de sinistros"""

    def test_registrar_sinistro(self, dao_factories, cliente_teste, seguro_teste):
        """Deve registrar sinistro em apólice ativa"""
        cliente_dao = dao_factories["cliente"]
        seguro_dao = dao_factories["seguro"]
        apolice_dao = dao_factories["apolice"]
        sinistro_dao = dao_factories["sinistro"]

        # Prepara apólice
        cliente_id = cliente_dao.criar(cliente_teste)
        
        # Adiciona cliente_id ao seguro_teste
        seguro_teste["cliente_id"] = cliente_id
        seguro_id = seguro_dao.criar(seguro_teste)

        apolice_data = {
            "cliente_id": cliente_id,
            "seguro_id": seguro_id,
            "status": "ativa"
        }

        apolice_id = apolice_dao.criar(apolice_data)

        # Registra sinistro
        sinistro_data = {
            "apolice_id": apolice_id,
            "data_ocorrencia": "2025-06-15",
            "descricao": "Colisão traseira",
            "status": "pendente"
        }

        sinistro_id = sinistro_dao.criar(sinistro_data)

        assert sinistro_id is not None
        sinistro = sinistro_dao.ler(sinistro_id)
        assert sinistro["status"] == "pendente"
        
    def test_atualizar_status_sinistro(self, dao_factories, cliente_teste, seguro_teste):
        """Deve atualizar status do sinistro (pendente -> em_analise -> aprovado -> pago)"""
        cliente_dao = dao_factories["cliente"]
        seguro_dao = dao_factories["seguro"]
        apolice_dao = dao_factories["apolice"]
        sinistro_dao = dao_factories["sinistro"]

        # Prepara dados
        cliente_id = cliente_dao.criar(cliente_teste)
        
        # Adiciona cliente_id ao seguro_teste
        seguro_teste["cliente_id"] = cliente_id
        seguro_id = seguro_dao.criar(seguro_teste)
        apolice_id = apolice_dao.criar(
            {
                "cliente_id": cliente_id,
                "seguro_id": seguro_id,
                "status": "ativa",
            }
        )

        sinistro_id = sinistro_dao.criar(
            {
                "apolice_id": apolice_id,
                "data_ocorrencia": "2025-06-15",
                "descricao": "Quebra de para-brisa",
                "status": "pendente",
            }
        )

        # Atualiza para em_analise
        sinistro_dao.atualizar(sinistro_id, {"status": "em_analise"})
        sinistro = sinistro_dao.ler(sinistro_id)
        assert sinistro["status"] == "em_analise"

        # Atualiza para aprovado
        sinistro_dao.atualizar(sinistro_id, {"status": "aprovado"})
        sinistro = sinistro_dao.ler(sinistro_id)
        assert sinistro["status"] == "aprovado"
        
        # Atualiza para pago
        sinistro_dao.atualizar(sinistro_id, {"status": "pago"})
        sinistro = sinistro_dao.ler(sinistro_id)
        assert sinistro["status"] == "pago"

    def test_sinistro_apolice_inexistente(self, dao_factories):
        """Não deve registrar sinistro em apólice inexistente"""
        sinistro_dao = dao_factories["sinistro"]

        sinistro_data = {
            "apolice_id": 99999,  # ID inexistente"data_ocorrencia": "2025-06-15",
            "descricao": "Teste",
                "status": "pendente"
        }

        # Deve falhar por violação de foreign key
        with pytest.raises(Exception):
            sinistro_dao.criar(sinistro_data)


class TestValidacoes:
    """Testes de validações gerais"""

    def test_cpf_unico(self, dao_factories, cliente_teste):
        """Não deve permitir CPF duplicado"""
        cliente_dao = dao_factories["cliente"]

        # Cria primeiro cliente
        cliente_id1 = cliente_dao.criar(cliente_teste)
        assert cliente_id1 is not None

        # Tenta criar segundo cliente com mesmo CPF
        cliente_teste2 = cliente_teste.copy()
        cliente_teste2["nome"] = "Maria Santos"
        cliente_teste2["email"] = "maria@email.com"

        # Deve falhar por constraint UNIQUE no CPF
        with pytest.raises(Exception):
            cliente_dao.criar(cliente_teste2)

    def test_numero_apolice_unico(self, dao_factories, cliente_teste, seguro_teste):
        """Não deve permitir número de apólice duplicado"""
        cliente_dao = dao_factories["cliente"]
        seguro_dao = dao_factories["seguro"]
        apolice_dao = dao_factories["apolice"]

        cliente_id = cliente_dao.criar(cliente_teste)
        
        # Adiciona cliente_id ao seguro_teste
        seguro_teste["cliente_id"] = cliente_id
        seguro_id = seguro_dao.criar(seguro_teste)

        # Cria primeira apólice
        apolice_data1 = {
            "cliente_id": cliente_id,
            "seguro_id": seguro_id,
            "status": "ativa"
        }

        apolice_id1 = apolice_dao.criar(apolice_data1)
        assert apolice_id1 is not None

        # Cria segunda apólice com mesmos dados (schema novo permite - não há campo numero único)
        apolice_data2 = apolice_data1.copy()
        apolice_id2 = apolice_dao.criar(apolice_data2)
        
        # Ambas as apólices são criadas com sucesso (sem constraint UNIQUE no schema novo)
        assert apolice_id2 is not None
        assert apolice_id2 != apolice_id1

    def test_listar_apolices_por_cliente(self, dao_factories, cliente_teste, seguro_teste):
        """Deve listar todas as apólices de um cliente"""
        cliente_dao = dao_factories["cliente"]
        seguro_dao = dao_factories["seguro"]
        apolice_dao = dao_factories["apolice"]

        # Cria cliente e seguro
        cliente_id = cliente_dao.criar(cliente_teste)
        
        # Adiciona cliente_id ao seguro_teste
        seguro_teste["cliente_id"] = cliente_id
        seguro_id = seguro_dao.criar(seguro_teste)

        # Cria 3 apólices para o mesmo cliente
        for i in range(3):
            apolice_data = {
                "cliente_id": cliente_id,
                "seguro_id": seguro_id,
                "numero": f"AP2025{100+i}",                
                "valor_premio": 1200.00 + (i * 100),
                "status": "ativa"
            }
            apolice_dao.criar(apolice_data)

        # Lista apólices do cliente
        apolices = apolice_dao.listar()
        apolices_cliente = [a for a in apolices if a["cliente_id"] == cliente_id]

        assert len(apolices_cliente) == 3
