"""
Testes de Persistência MySQL
Testa operações CRUD completas de todas as entidades
"""
import pytest

from functions.dao_mysql import ApoliceDAO, ClienteDAO, SeguroDAO, SinistroDAO, UsuarioDAO


class TestClienteDAO:
    """Testes CRUD para ClienteDAO"""

    def test_criar_cliente(self, dao_factories, cliente_teste):
        """Deve criar cliente e retornar ID"""
        cliente_dao = dao_factories["cliente"]

        cliente_id = cliente_dao.criar(cliente_teste)

        assert cliente_id is not None
        assert cliente_id > 0

    def test_ler_cliente(self, dao_factories, cliente_teste):
        """Deve ler cliente criado"""
        cliente_dao = dao_factories["cliente"]

        cliente_id = cliente_dao.criar(cliente_teste)
        cliente = cliente_dao.ler(cliente_id)

        assert cliente is not None
        assert cliente["id"] == cliente_id
        assert cliente["nome"] == cliente_teste["nome"]
        assert cliente["cpf"] == cliente_teste["cpf"]
        assert cliente["email"] == cliente_teste["email"]

    def test_atualizar_cliente(self, dao_factories, cliente_teste):
        """Deve atualizar dados do cliente"""
        cliente_dao = dao_factories["cliente"]

        cliente_id = cliente_dao.criar(cliente_teste)

        # Atualiza telefone e email
        cliente_dao.atualizar(
            cliente_id, {"telefone": "11888888888", "email": "novo.email@email.com"}
        )

        cliente = cliente_dao.ler(cliente_id)
        assert cliente["telefone"] == "11888888888"
        assert cliente["email"] == "novo.email@email.com"
        assert cliente["nome"] == cliente_teste["nome"]  # Nome não mudou

    def test_deletar_cliente(self, dao_factories, cliente_teste):
        """Deve deletar cliente"""
        cliente_dao = dao_factories["cliente"]

        cliente_id = cliente_dao.criar(cliente_teste)

        # Deleta cliente
        resultado = cliente_dao.deletar(cliente_id)
        assert resultado is True

        # Verifica que foi deletado
        cliente = cliente_dao.ler(cliente_id)
        assert cliente is None

    def test_listar_clientes(self, dao_factories, cliente_teste):
        """Deve listar todos os clientes"""
        cliente_dao = dao_factories["cliente"]

        # Cria 3 clientes
        for i in range(3):
            cliente = cliente_teste.copy()
            cliente["cpf"] = f"1234567890{i}"
            cliente["email"] = f"cliente{i}@email.com"
            cliente_dao.criar(cliente)

        clientes = cliente_dao.listar()

        assert len(clientes) == 3

    def test_buscar_cliente_por_cpf(self, dao_factories, cliente_teste):
        """Deve buscar cliente por CPF"""
        cliente_dao = dao_factories["cliente"]

        cliente_id = cliente_dao.criar(cliente_teste)

        # Busca por CPF
        clientes = cliente_dao.listar()
        cliente_encontrado = next((c for c in clientes if c["cpf"] == cliente_teste["cpf"]), None)

        assert cliente_encontrado is not None
        assert cliente_encontrado["id"] == cliente_id


class TestSeguroDAO:
    """Testes CRUD para SeguroDAO"""

    def test_criar_seguro(self, dao_factories, seguro_teste, cliente_teste_id):
        """Deve criar seguro com detalhes JSON"""
        seguro_dao = dao_factories["seguro"]
        
        # Adiciona cliente_id ao seguro_teste
        seguro_teste["cliente_id"] = cliente_teste_id
        seguro_id = seguro_dao.criar(seguro_teste)

        assert seguro_id is not None
        assert seguro_id > 0

    def test_ler_seguro(self, dao_factories, seguro_teste_id):
        """Deve ler seguro com detalhes deserializados"""
        seguro_dao = dao_factories["seguro"]

        seguro = seguro_dao.ler(seguro_teste_id)

        assert seguro is not None
        assert seguro["tipo"] == "AUTO"
        assert isinstance(seguro["detalhes"], dict)
        assert seguro["detalhes"]["cobertura"] == "Completa"

    def test_atualizar_seguro(self, dao_factories, seguro_teste_id):
        """Deve atualizar seguro incluindo detalhes JSON"""
        seguro_dao = dao_factories["seguro"]

        # Atualiza valor e detalhes
        novos_detalhes = {"cobertura": "Completa", "franquia": 3000.00, "assistencia_24h": True}

        seguro_dao.atualizar(seguro_teste_id, {"valor": 1500.00, "detalhes": novos_detalhes})

        seguro = seguro_dao.ler(seguro_teste_id)
        assert float(seguro["valor"]) == 1500.00
        assert seguro["detalhes"]["franquia"] == 3000.00

    def test_deletar_seguro(self, dao_factories, seguro_teste_id):
        """Deve deletar seguro"""
        seguro_dao = dao_factories["seguro"]

        resultado = seguro_dao.deletar(seguro_teste_id)

        assert resultado is True
        assert seguro_dao.ler(seguro_teste_id) is None

    def test_listar_seguros(self, dao_factories, cliente_teste_id):
        """Deve listar todos os seguros"""
        seguro_dao = dao_factories["seguro"]

        # Cria 3 seguros
        tipos = ["AUTO", "RESIDENCIAL", "VIDA"]
        for tipo in tipos:
            seguro_dao.criar(
                {
                    "tipo": tipo,
                    "descricao": f"Seguro {tipo}",
                    "valor": 1000.00,
                    "cliente_id": cliente_teste_id,
                    "detalhes": {"tipo": tipo},
                }
            )

        seguros = seguro_dao.listar()

        assert len(seguros) >= 3


class TestApoliceDAO:
    """Testes CRUD para ApoliceDAO"""

    def test_criar_apolice(self, dao_factories, apolice_teste):
        """Deve criar apólice vinculada a cliente e seguro"""
        apolice_dao = dao_factories["apolice"]

        apolice_id = apolice_dao.criar(apolice_teste)

        assert apolice_id is not None
        assert apolice_id > 0

    def test_ler_apolice(self, dao_factories, apolice_teste_id):
        """Deve ler apólice com relacionamentos"""
        apolice_dao = dao_factories["apolice"]

        apolice = apolice_dao.ler(apolice_teste_id)

        assert apolice is not None
        assert apolice["status"] == "ativa"

    def test_atualizar_status_apolice(self, dao_factories, apolice_teste_id):
        """Deve atualizar status da apólice"""
        apolice_dao = dao_factories["apolice"]

        # Cancela apólice
        apolice_dao.atualizar(apolice_teste_id, {"status": "cancelada"})

        apolice = apolice_dao.ler(apolice_teste_id)
        assert apolice["status"] == "cancelada"

    def test_deletar_apolice(self, dao_factories, apolice_teste_id):
        """Deve deletar apólice"""
        apolice_dao = dao_factories["apolice"]

        resultado = apolice_dao.deletar(apolice_teste_id)

        assert resultado is True
        assert apolice_dao.ler(apolice_teste_id) is None


class TestSinistroDAO:
    """Testes CRUD para SinistroDAO"""

    def test_criar_sinistro(self, dao_factories, sinistro_teste):
        """Deve criar sinistro vinculado a apólice"""
        sinistro_dao = dao_factories["sinistro"]

        sinistro_id = sinistro_dao.criar(sinistro_teste)

        assert sinistro_id is not None
        assert sinistro_id > 0

    def test_ler_sinistro(self, dao_factories, apolice_teste_id):
        """Deve ler sinistro com relacionamento"""
        sinistro_dao = dao_factories["sinistro"]

        sinistro_id = sinistro_dao.criar(
            {
                "apolice_id": apolice_teste_id,
                "data_ocorrencia": "2025-06-15",
                "descricao": "Teste sinistro",
                "status": "pendente",
            }
        )

        sinistro = sinistro_dao.ler(sinistro_id)

        assert sinistro is not None
        assert sinistro["apolice_id"] == apolice_teste_id
        assert sinistro["status"] == "pendente"

    def test_atualizar_sinistro(self, dao_factories, apolice_teste_id):
        """Deve atualizar status do sinistro"""
        sinistro_dao = dao_factories["sinistro"]

        sinistro_id = sinistro_dao.criar(
            {
                "apolice_id": apolice_teste_id,
                "data_ocorrencia": "2025-06-15",
                "descricao": "Teste sinistro",
                "status": "pendente",
            }
        )

        # Aprova sinistro
        sinistro_dao.atualizar(sinistro_id, {"status": "aprovado"})

        sinistro = sinistro_dao.ler(sinistro_id)
        assert sinistro["status"] == "aprovado"


class TestUsuarioDAO:
    """Testes CRUD para UsuarioDAO"""

    def test_criar_usuario(self, dao_factories, usuario_teste):
        """Deve criar usuário"""
        usuario_dao = dao_factories["usuario"]

        usuario_id = usuario_dao.criar(usuario_teste)

        assert usuario_id is not None
        assert usuario_id > 0

    def test_ler_usuario(self, dao_factories, usuario_teste):
        """Deve ler usuário"""
        usuario_dao = dao_factories["usuario"]

        usuario_id = usuario_dao.criar(usuario_teste)
        usuario = usuario_dao.ler(usuario_id)

        assert usuario is not None
        assert usuario["username"] == usuario_teste["username"]
        assert usuario["tipo"] == usuario_teste["tipo"]

    def test_buscar_usuario_por_username(self, dao_factories, usuario_teste):
        """Deve buscar usuário por username"""
        usuario_dao = dao_factories["usuario"]

        usuario_dao.criar(usuario_teste)
        usuario = usuario_dao.ler_por_username(usuario_teste["username"])  # Corrigido: buscar_por_username → ler_por_username

        assert usuario is not None
        assert usuario["username"] == usuario_teste["username"]
