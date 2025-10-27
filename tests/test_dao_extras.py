"""
Testes adicionais para aumentar cobertura dos DAOs
Foco em métodos específicos e edge cases
"""
import pytest
from datetime import date, datetime
from functions.dao_mysql import ClienteDAO, SeguroDAO, ApoliceDAO, SinistroDAO


class TestClienteDAOExtras:
    """Testes adicionais para ClienteDAO"""

    def test_ler_por_id_inexistente(self, mysql_db):
        """Busca cliente com ID inexistente"""
        cliente_dao = ClienteDAO(mysql_db)
        cliente = cliente_dao.ler_por_id(999999)
        assert cliente is None

    def test_ler_por_cpf_inexistente(self, mysql_db):
        """Busca cliente por CPF inexistente"""
        cliente_dao = ClienteDAO(mysql_db)
        cliente = cliente_dao.ler_por_cpf("00000000000")
        assert cliente is None

    def test_atualizar_cliente_inexistente(self, mysql_db):
        """Tenta atualizar cliente inexistente"""
        cliente_dao = ClienteDAO(mysql_db)
        dados = {"nome": "Teste"}
        sucesso = cliente_dao.atualizar(999999, dados)
        assert not sucesso

    def test_deletar_cliente_inexistente(self, mysql_db):
        """Tenta deletar cliente inexistente"""
        cliente_dao = ClienteDAO(mysql_db)
        sucesso = cliente_dao.deletar(999999)
        assert not sucesso


class TestSeguroDAOExtras:
    """Testes adicionais para SeguroDAO"""

    def test_ler_por_id_inexistente(self, mysql_db):
        """Busca seguro com ID inexistente"""
        seguro_dao = SeguroDAO(mysql_db)
        seguro = seguro_dao.ler_por_id(999999)
        assert seguro is None

    def test_atualizar_seguro_inexistente(self, mysql_db):
        """Tenta atualizar seguro inexistente"""
        seguro_dao = SeguroDAO(mysql_db)
        dados = {"valor": 5000.00}
        sucesso = seguro_dao.atualizar(999999, dados)
        assert not sucesso

    def test_deletar_seguro_inexistente(self, mysql_db):
        """Tenta deletar seguro inexistente"""
        seguro_dao = SeguroDAO(mysql_db)
        sucesso = seguro_dao.deletar(999999)
        assert not sucesso


class TestApoliceDAOExtras:
    """Testes adicionais para ApoliceDAO"""

    def test_ler_por_id_inexistente(self, mysql_db):
        """Busca apólice com ID inexistente"""
        apolice_dao = ApoliceDAO(mysql_db)
        apolice = apolice_dao.ler_por_id(999999)
        assert apolice is None

    def test_atualizar_apolice_inexistente(self, mysql_db):
        """Tenta atualizar apólice inexistente"""
        apolice_dao = ApoliceDAO(mysql_db)
        dados = {"status": "cancelada"}
        sucesso = apolice_dao.atualizar(999999, dados)
        assert not sucesso

    def test_deletar_apolice_inexistente(self, mysql_db):
        """Tenta deletar apólice inexistente"""
        apolice_dao = ApoliceDAO(mysql_db)
        sucesso = apolice_dao.deletar(999999)
        assert not sucesso


class TestSinistroDAOExtras:
    """Testes adicionais para SinistroDAO"""

    def test_ler_por_id_inexistente(self, mysql_db):
        """Busca sinistro com ID inexistente"""
        sinistro_dao = SinistroDAO(mysql_db)
        sinistro = sinistro_dao.ler_por_id(999999)
        assert sinistro is None

    def test_atualizar_sinistro_inexistente(self, mysql_db):
        """Tenta atualizar sinistro inexistente"""
        sinistro_dao = SinistroDAO(mysql_db)
        dados = {"status": "pago"}
        sucesso = sinistro_dao.atualizar(999999, dados)
        assert not sucesso
