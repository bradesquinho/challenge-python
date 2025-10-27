"""
Testes para aumentar cobertura de código - Foco em DAOs e Services
Testa workflows completos usando Dependency Injection
"""
import pytest
from datetime import datetime, date
from functions.dao_mysql import ClienteDAO, SeguroDAO, ApoliceDAO, SinistroDAO
from functions.servicos import ClienteService, SeguroService, ApoliceService, SinistroService


class TestClienteWorkflows:
    """Testa workflows completos de cliente"""

    def test_criar_e_listar_cliente(self, mysql_db, mongodb_db, cliente_teste):
        """Cria cliente via service e lista via DAO"""
        cliente_service = ClienteService(mysql_db, mongodb_db)
        cliente_dao = ClienteDAO(mysql_db)

        # Cria cliente
        cliente_id = cliente_service.criar_cliente(cliente_teste, usuario="admin")
        assert cliente_id > 0

        # Lista e verifica
        clientes = cliente_dao.listar()
        assert len(clientes) > 0
        cliente_criado = next((c for c in clientes if c["id"] == cliente_id), None)
        assert cliente_criado is not None
        assert cliente_criado["nome"] == cliente_teste["nome"]
        assert cliente_criado["cpf"] == cliente_teste["cpf"]

    def test_buscar_cliente_por_cpf(self, mysql_db, mongodb_db, cliente_teste):
        """Cria cliente e busca por CPF"""
        cliente_service = ClienteService(mysql_db, mongodb_db)
        cliente_dao = ClienteDAO(mysql_db)

        # Cria cliente
        cliente_id = cliente_service.criar_cliente(cliente_teste, usuario="admin")

        # Busca por CPF
        cliente_encontrado = cliente_dao.ler_por_cpf(cliente_teste["cpf"])
        assert cliente_encontrado is not None
        assert cliente_encontrado["id"] == cliente_id
        assert cliente_encontrado["cpf"] == cliente_teste["cpf"]

    def test_atualizar_cliente(self, mysql_db, mongodb_db, cliente_teste_id):
        """Atualiza dados de cliente"""
        cliente_dao = ClienteDAO(mysql_db)

        # Busca cliente original
        cliente = cliente_dao.ler_por_id(cliente_teste_id)
        assert cliente is not None

        # Atualiza dados
        cliente["nome"] = "Nome Atualizado Test"
        cliente["email"] = "atualizado@test.com"
        sucesso = cliente_dao.atualizar(cliente_teste_id, cliente)
        assert sucesso

        # Verifica atualização
        cliente_atualizado = cliente_dao.ler_por_id(cliente_teste_id)
        assert cliente_atualizado["nome"] == "Nome Atualizado Test"
        assert cliente_atualizado["email"] == "atualizado@test.com"

    def test_deletar_cliente(self, mysql_db, mongodb_db, cliente_teste):
        """Cria e deleta cliente"""
        cliente_service = ClienteService(mysql_db, mongodb_db)
        cliente_dao = ClienteDAO(mysql_db)

        # Cria cliente
        cliente_id = cliente_service.criar_cliente(cliente_teste, usuario="admin")
        assert cliente_id > 0

        # Deleta cliente
        sucesso = cliente_dao.deletar(cliente_id)
        assert sucesso

        # Verifica que foi deletado
        cliente_deletado = cliente_dao.ler_por_id(cliente_id)
        assert cliente_deletado is None


class TestSeguroWorkflows:
    """Testa workflows completos de seguro"""

    def test_criar_e_listar_seguro(self, mysql_db, mongodb_db, cliente_teste_id, seguro_teste):
        """Cria seguro via service e lista via DAO"""
        seguro_service = SeguroService(mysql_db, mongodb_db)
        seguro_dao = SeguroDAO(mysql_db)

        # Adiciona cliente_id
        seguro_teste["cliente_id"] = cliente_teste_id

        # Cria seguro
        seguro_id = seguro_service.criar_seguro(seguro_teste, usuario="admin")
        assert seguro_id > 0

        # Lista e verifica
        seguros = seguro_dao.listar()
        assert len(seguros) > 0
        seguro_criado = next((s for s in seguros if s["id"] == seguro_id), None)
        assert seguro_criado is not None
        assert seguro_criado["tipo"] == seguro_teste["tipo"]
        assert seguro_criado["cliente_id"] == cliente_teste_id

    def test_atualizar_seguro(self, mysql_db, mongodb_db, seguro_teste_id):
        """Atualiza dados de seguro"""
        seguro_dao = SeguroDAO(mysql_db)

        # Busca seguro original
        seguro = seguro_dao.ler_por_id(seguro_teste_id)
        assert seguro is not None

        # Atualiza dados
        seguro["valor"] = 3000.00
        seguro["descricao"] = "Descrição Atualizada"
        sucesso = seguro_dao.atualizar(seguro_teste_id, seguro)
        assert sucesso

        # Verifica atualização
        seguro_atualizado = seguro_dao.ler_por_id(seguro_teste_id)
        assert float(seguro_atualizado["valor"]) == 3000.00
        assert seguro_atualizado["descricao"] == "Descrição Atualizada"


class TestApoliceWorkflows:
    """Testa workflows completos de apólice"""

    def test_emitir_e_listar_apolice(self, mysql_db, mongodb_db, cliente_teste_id, seguro_teste_id):
        """Emite apólice via service e lista via DAO"""
        apolice_service = ApoliceService(mysql_db, mongodb_db)
        apolice_dao = ApoliceDAO(mysql_db)

        # Prepara dados da apólice
        dados_apolice = {
            "seguro_id": seguro_teste_id,
            "cliente_id": cliente_teste_id,
            "data_emissao": date.today(),
            "status": "ativa"
        }

        # Emite apólice
        apolice_id = apolice_service.emitir_apolice(dados_apolice, usuario="admin")
        assert apolice_id > 0

        # Lista e verifica
        apolices = apolice_dao.listar()
        assert len(apolices) > 0
        apolice_criada = next((a for a in apolices if a["id"] == apolice_id), None)
        assert apolice_criada is not None
        assert apolice_criada["seguro_id"] == seguro_teste_id
        assert apolice_criada["cliente_id"] == cliente_teste_id
        assert apolice_criada["status"] == "ativa"

    def test_cancelar_apolice(self, mysql_db, mongodb_db, cliente_teste_id, seguro_teste_id):
        """Emite e cancela apólice"""
        apolice_service = ApoliceService(mysql_db, mongodb_db)
        apolice_dao = ApoliceDAO(mysql_db)

        # Prepara dados da apólice
        dados_apolice = {
            "seguro_id": seguro_teste_id,
            "cliente_id": cliente_teste_id,
            "data_emissao": date.today(),
            "status": "ativa"
        }

        # Emite apólice
        apolice_id = apolice_service.emitir_apolice(dados_apolice, usuario="admin")

        # Cancela apólice
        sucesso = apolice_service.cancelar_apolice(apolice_id, usuario="admin")
        assert sucesso

        # Verifica cancelamento
        apolice = apolice_dao.ler_por_id(apolice_id)
        assert apolice["status"] == "cancelada"


class TestSinistroWorkflows:
    """Testa workflows completos de sinistro"""

    def test_registrar_e_listar_sinistro(
        self, mysql_db, mongodb_db, cliente_teste_id, seguro_teste_id, sinistro_teste
    ):
        """Registra sinistro via service e lista via DAO"""
        sinistro_service = SinistroService(mysql_db, mongodb_db)
        sinistro_dao = SinistroDAO(mysql_db)
        apolice_service = ApoliceService(mysql_db, mongodb_db)

        # Prepara dados da apólice
        dados_apolice = {
            "seguro_id": seguro_teste_id,
            "cliente_id": cliente_teste_id,
            "data_emissao": date.today(),
            "status": "ativa"
        }

        # Primeiro emite apólice
        apolice_id = apolice_service.emitir_apolice(dados_apolice, usuario="admin")

        # Prepara dados do sinistro
        sinistro_teste["apolice_id"] = apolice_id

        # Registra sinistro
        sinistro_id = sinistro_service.registrar_sinistro(sinistro_teste, usuario="admin")
        assert sinistro_id > 0

        # Lista e verifica
        sinistros = sinistro_dao.listar()
        assert len(sinistros) > 0
        sinistro_criado = next((s for s in sinistros if s["id"] == sinistro_id), None)
        assert sinistro_criado is not None
        assert sinistro_criado["apolice_id"] == apolice_id
        assert sinistro_criado["status"] == "pendente"

    def test_atualizar_sinistro(
        self, mysql_db, mongodb_db, cliente_teste_id, seguro_teste_id, sinistro_teste
    ):
        """Registra e atualiza sinistro"""
        sinistro_service = SinistroService(mysql_db, mongodb_db)
        sinistro_dao = SinistroDAO(mysql_db)
        apolice_service = ApoliceService(mysql_db, mongodb_db)

        # Prepara dados da apólice
        dados_apolice = {
            "seguro_id": seguro_teste_id,
            "cliente_id": cliente_teste_id,
            "data_emissao": date.today(),
            "status": "ativa"
        }

        # Primeiro emite apólice
        apolice_id = apolice_service.emitir_apolice(dados_apolice, usuario="admin")

        # Registra sinistro
        sinistro_teste["apolice_id"] = apolice_id
        sinistro_id = sinistro_service.registrar_sinistro(sinistro_teste, usuario="admin")

        # Atualiza status
        sinistro = sinistro_dao.ler_por_id(sinistro_id)
        sinistro["status"] = "em_analise"
        sinistro["status_anterior"] = "pendente"
        
        sucesso = sinistro_service.atualizar_sinistro(
            sinistro_id, sinistro, usuario="admin", observacoes="Análise iniciada"
        )
        assert sucesso

        # Verifica atualização
        sinistro_atualizado = sinistro_dao.ler_por_id(sinistro_id)
        assert sinistro_atualizado["status"] == "em_analise"


class TestValidacoesNegocio:
    """Testa validações de regras de negócio"""

    def test_cpf_duplicado_retorna_zero(self, mysql_db, mongodb_db, cliente_teste):
        """Verifica que CPF duplicado lança exceção"""
        cliente_service = ClienteService(mysql_db, mongodb_db)

        # Cria primeiro cliente
        cliente_id1 = cliente_service.criar_cliente(cliente_teste, usuario="admin")
        assert cliente_id1 > 0

        # Tenta criar segundo cliente com mesmo CPF (deve lançar exceção)
        with pytest.raises(Exception) as exc_info:
            cliente_service.criar_cliente(cliente_teste, usuario="admin")
        
        # Verifica que a exceção é sobre CPF duplicado
        assert "Duplicate entry" in str(exc_info.value) or "cpf" in str(exc_info.value).lower()
