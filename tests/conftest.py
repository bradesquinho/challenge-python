"""
Fixtures pytest para configuração de testes
Fornece setup/teardown automático para MySQL e MongoDB
"""
import random
import uuid
from datetime import datetime

import mysql.connector
import pytest
from pymongo import MongoClient

from config_test import MONGODB_TEST_CONFIG, MYSQL_TEST_CONFIG


@pytest.fixture(scope="session")
def mysql_test_connection():
    """
    Cria conexão com MySQL de teste e garante que o banco existe
    Scope session: criado uma vez por sessão de testes
    """
    # Conecta sem especificar database para criar o banco se não existir
    temp_config = MYSQL_TEST_CONFIG.copy()
    database_name = temp_config.pop("database")
    temp_config.pop("raise_on_warnings", None)  # Remove para evitar erro em warnings

    conn = mysql.connector.connect(**temp_config)
    cursor = conn.cursor()

    # Cria banco de teste se não existir (ignora se já existe)
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
    cursor.execute(f"USE {database_name}")

    # Limpa tabelas existentes (DROP IF EXISTS para garantir schema limpo)
    cursor.execute("DROP TABLE IF EXISTS sinistros")
    cursor.execute("DROP TABLE IF EXISTS apolices")
    cursor.execute("DROP TABLE IF EXISTS seguros")
    cursor.execute("DROP TABLE IF EXISTS clientes")
    cursor.execute("DROP TABLE IF EXISTS usuarios")
    # Limpa tabelas existentes (DROP IF EXISTS para garantir schema limpo)
    cursor.execute("DROP TABLE IF EXISTS sinistros")
    cursor.execute("DROP TABLE IF EXISTS apolices")
    cursor.execute("DROP TABLE IF EXISTS seguros")
    cursor.execute("DROP TABLE IF EXISTS clientes")
    cursor.execute("DROP TABLE IF EXISTS usuarios")

    # Cria tabelas diretamente via SQL (SCHEMA ATUALIZADO - Sprint 4)
    cursor.execute(
        """
        CREATE TABLE usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            senha VARCHAR(255) NOT NULL,
            tipo ENUM('admin', 'comum') NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_username (username)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    )

    cursor.execute(
        """
        CREATE TABLE clientes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(200) NOT NULL,
            cpf VARCHAR(14) UNIQUE NOT NULL,
            telefone VARCHAR(20),
            email VARCHAR(100),
            data_nasc DATE,
            endereco TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_cpf (cpf),
            INDEX idx_nome (nome)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    )

    cursor.execute(
        """
        CREATE TABLE seguros (
            id INT AUTO_INCREMENT PRIMARY KEY,
            tipo VARCHAR(50) NOT NULL,
            descricao TEXT,
            valor DECIMAL(10, 2),
            detalhes JSON,
            cliente_id INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
            INDEX idx_cliente (cliente_id),
            INDEX idx_tipo (tipo)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    )

    cursor.execute(
        """
        CREATE TABLE apolices (
            id INT AUTO_INCREMENT PRIMARY KEY,
            cliente_id INT NOT NULL,
            seguro_id INT NOT NULL,
            data_emissao DATE,
            status VARCHAR(50) DEFAULT 'ativa',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
            FOREIGN KEY (seguro_id) REFERENCES seguros(id) ON DELETE CASCADE,
            INDEX idx_cliente (cliente_id),
            INDEX idx_seguro (seguro_id),
            INDEX idx_status (status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    )

    cursor.execute(
        """
        CREATE TABLE sinistros (
            id INT AUTO_INCREMENT PRIMARY KEY,
            apolice_id INT NOT NULL,
            data_ocorrencia DATE,
            descricao TEXT,
            status VARCHAR(50) DEFAULT 'aberto',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (apolice_id) REFERENCES apolices(id) ON DELETE CASCADE,
            INDEX idx_apolice (apolice_id),
            INDEX idx_status (status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    )

    conn.commit()
    cursor.close()
    conn.close()

    # Agora conecta ao banco de teste
    test_config = MYSQL_TEST_CONFIG.copy()
    test_config.pop("raise_on_warnings", None)
    conn = mysql.connector.connect(**test_config)

    yield conn

    # Teardown: limpa e fecha conexão
    cursor = conn.cursor()
    cursor.execute(f"DROP DATABASE IF EXISTS {database_name}")
    cursor.close()
    conn.close()


@pytest.fixture(scope="function")
def mysql_db(mysql_test_connection):
    """
    Fornece conexão MySQL limpa para cada teste
    Scope function: reset antes de cada teste
    """
    conn = mysql_test_connection
    cursor = conn.cursor()

    # Limpa todas as tabelas antes de cada teste
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    cursor.execute("TRUNCATE TABLE sinistros")
    cursor.execute("TRUNCATE TABLE apolices")
    cursor.execute("TRUNCATE TABLE seguros")
    cursor.execute("TRUNCATE TABLE clientes")
    cursor.execute("TRUNCATE TABLE usuarios")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    conn.commit()
    cursor.close()

    yield conn

    # Rollback após cada teste para garantir isolamento
    conn.rollback()


@pytest.fixture(scope="session")
def mongodb_test_connection():
    """
    Cria conexão com MongoDB de teste
    Scope session: criado uma vez por sessão de testes
    """
    client = MongoClient(MONGODB_TEST_CONFIG["uri"])
    db = client[MONGODB_TEST_CONFIG["database"]]

    # Cria coleções e índices diretamente
    # Coleção de auditoria
    if "auditoria" not in db.list_collection_names():
        db.create_collection("auditoria")
    db.auditoria.create_index([("timestamp", -1)])
    db.auditoria.create_index([("usuario", 1)])
    db.auditoria.create_index([("entidade", 1), ("entidade_id", 1)])

    # Coleção de documentos de sinistros
    if "sinistros_documentos" not in db.list_collection_names():
        db.create_collection("sinistros_documentos")
    db.sinistros_documentos.create_index([("sinistro_id", 1)])
    db.sinistros_documentos.create_index([("tipo_documento", 1)])

    # Coleção de perfis de clientes
    if "clientes_perfil" not in db.list_collection_names():
        db.create_collection("clientes_perfil")
    db.clientes_perfil.create_index([("cliente_id", 1)], unique=True)

    # Coleção de metadados de relatórios
    if "relatorios_exportados" not in db.list_collection_names():
        db.create_collection("relatorios_exportados")
    db.relatorios_exportados.create_index([("data_exportacao", -1)])
    db.relatorios_exportados.create_index([("usuario", 1)])

    yield db

    # Teardown: remove database de teste
    client.drop_database(MONGODB_TEST_CONFIG["database"])
    client.close()


@pytest.fixture(scope="function")
def mongodb_db(mongodb_test_connection):
    """
    Fornece MongoDB limpo para cada teste
    Scope function: reset antes de cada teste
    """
    db = mongodb_test_connection

    # Limpa todas as coleções antes de cada teste
    db.auditoria.delete_many({})
    db.sinistros_documentos.delete_many({})
    db.clientes_perfil.delete_many({})
    db.relatorios_exportados.delete_many({})

    yield db


@pytest.fixture
def dao_factories(mysql_db):
    """
    Fornece factory de DAOs para testes
    """
    from functions.dao_mysql import ApoliceDAO, ClienteDAO, SeguroDAO, SinistroDAO, UsuarioDAO

    return {
        "cliente": ClienteDAO(mysql_db),
        "seguro": SeguroDAO(mysql_db),
        "apolice": ApoliceDAO(mysql_db),
        "sinistro": SinistroDAO(mysql_db),
        "usuario": UsuarioDAO(mysql_db),
    }


@pytest.fixture
def servicos_factories(mysql_db, mongodb_db):
    """
    Fornece factory de serviços para testes de integração
    """
    from functions.auditoria_service import AuditoriaService
    from functions.servicos import ApoliceService, ClienteService, SeguroService, SinistroService

    # Configura serviços para usar bancos de teste
    return {
        "cliente": ClienteService(mysql_db, mongodb_db),
        "seguro": SeguroService(mysql_db, mongodb_db),
        "apolice": ApoliceService(mysql_db, mongodb_db),
        "sinistro": SinistroService(mysql_db, mongodb_db),
        "auditoria": AuditoriaService(mongodb_db),
    }


# ==================== GERADORES DE DADOS ÚNICOS ====================


def gerar_cpf_unico():
    """Gera CPF único baseado em UUID para garantir unicidade absoluta"""
    # Usa UUID + timestamp para garantir que nunca repete
    unique_str = f"{uuid.uuid4().hex}{datetime.now().timestamp()}"
    # Extrai apenas dígitos e pega os primeiros 11
    digits = ''.join(filter(str.isdigit, unique_str))[:11]
    # Se não tiver 11 dígitos, completa com zeros
    cpf = digits.ljust(11, '0')
    return cpf


def gerar_email_unico():
    """Gera email único para testes"""
    return f"test_{uuid.uuid4().hex}@example.com"


def gerar_telefone_unico():
    """Gera telefone único para testes"""
    unique_digits = ''.join(filter(str.isdigit, uuid.uuid4().hex))[:9]
    return f"11{unique_digits.ljust(9, '0')}"


# ==================== FIXTURES DE DADOS ====================


@pytest.fixture
def cliente_teste():
    """Dados de cliente para testes com CPF único por execução"""
    return {
        "nome": "João da Silva",
        "cpf": gerar_cpf_unico(),  # CPF único por teste
        "data_nasc": "1990-01-15",
        "email": gerar_email_unico(),  # Email único por teste
        "telefone": gerar_telefone_unico(),  # Telefone único por teste
        "endereco": "Rua Teste, 123",
    }


@pytest.fixture
def usuario_teste():
    """Dados de usuário para testes com username único"""
    unique_id = uuid.uuid4().hex[:8]
    return {
        "username": f"user_{unique_id}",  # Username único por teste
        "senha": "senha_hash_teste_123",
        "tipo": "admin",
    }


@pytest.fixture
def cliente_teste_id(dao_factories, cliente_teste):
    """Cria cliente no banco e retorna ID"""
    cliente_dao = dao_factories["cliente"]
    cliente_id = cliente_dao.criar(cliente_teste)
    return cliente_id


@pytest.fixture
def seguro_teste_id(dao_factories, cliente_teste_id):
    """Cria seguro no banco e retorna ID"""
    seguro_dao = dao_factories["seguro"]
    seguro_dados = {
        "tipo": "AUTO",
        "descricao": "Cobertura completa para veículos",
        "valor": 1200.00,
        "cliente_id": cliente_teste_id,
        "detalhes": {"cobertura": "Completa", "franquia": 2000.00, "assistencia_24h": True},
    }
    seguro_id = seguro_dao.criar(seguro_dados)
    return seguro_id


@pytest.fixture
def seguro_teste():
    """Dados de seguro para testes - schema novo (sem nome/premio_base)
    
    NOTA: cliente_id precisa ser preenchido pelo teste
    """
    return {
        "tipo": "AUTO",
        "descricao": "Cobertura completa para veículos",
        "valor": 1200.00,
        # cliente_id será preenchido pelo teste após criar o cliente
        "detalhes": {"cobertura": "Completa", "franquia": 2000.00, "assistencia_24h": True},
    }


@pytest.fixture
def apolice_teste(cliente_teste_id, seguro_teste_id):
    """Dados de apólice para testes - schema novo (sem data_inicio/data_fim/valor_premio)"""
    return {
        "cliente_id": cliente_teste_id,
        "seguro_id": seguro_teste_id,
        "status": "ativa",
    }


@pytest.fixture
def sinistro_teste(apolice_teste_id):
    """Dados de sinistro para testes - schema novo (sem numero/valor_estimado/valor_aprovado)"""
    return {
        "apolice_id": apolice_teste_id,
        "data_ocorrencia": "2025-06-15",
        "descricao": "Colisão traseira em cruzamento",
        "status": "pendente",
    }


@pytest.fixture
def apolice_teste_id(dao_factories, cliente_teste_id, seguro_teste_id):
    """Cria apólice no banco e retorna ID"""
    apolice_dao = dao_factories["apolice"]
    apolice_dados = {
        "cliente_id": cliente_teste_id,
        "seguro_id": seguro_teste_id,
        "status": "ativa",
    }
    apolice_id = apolice_dao.criar(apolice_dados)
    return apolice_id

