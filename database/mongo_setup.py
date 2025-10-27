"""
Setup e conexão com MongoDB
Sprint 4 - Persistência Híbrida (logs e documentos complementares)
"""
import os
import sys
from datetime import datetime

from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

# Adiciona o diretório pai ao path para importar config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MONGODB_CONFIG, get_mongodb_uri


class MongoDBConnection:
    """Gerenciador de conexão com MongoDB"""

    _client = None
    _db = None

    @classmethod
    def get_client(cls):
        """Retorna o cliente MongoDB (singleton)"""
        if cls._client is None:
            try:
                cls._client = MongoClient(get_mongodb_uri(), serverSelectionTimeoutMS=5000)
                # Testa a conexão
                cls._client.admin.command("ping")
                print(
                    f"✓ Conectado ao MongoDB em {MONGODB_CONFIG['host']}:{MONGODB_CONFIG['port']}"
                )
            except ConnectionFailure as e:
                print(f"✗ Erro ao conectar ao MongoDB: {e}")
                cls._client = None
        return cls._client

    @classmethod
    def get_database(cls):
        """Retorna o banco de dados"""
        if cls._db is None:
            client = cls.get_client()
            if client:
                cls._db = client[MONGODB_CONFIG["database"]]
        return cls._db

    @classmethod
    def close(cls):
        """Fecha a conexão"""
        if cls._client:
            cls._client.close()
            cls._client = None
            cls._db = None


def criar_colecoes():
    """Cria as coleções e índices no MongoDB"""
    try:
        db = MongoDBConnection.get_database()
        if db is None:
            return False

        # Coleção de auditoria/logs
        if "auditoria" not in db.list_collection_names():
            db.create_collection("auditoria")
            print("✓ Coleção 'auditoria' criada")

        # Índices para auditoria
        auditoria = db["auditoria"]
        auditoria.create_index([("timestamp", DESCENDING)])
        auditoria.create_index([("usuario", ASCENDING)])
        auditoria.create_index([("operacao", ASCENDING)])
        auditoria.create_index([("entidade", ASCENDING)])
        print("✓ Índices de 'auditoria' criados")

        # Coleção de documentos de sinistros
        if "sinistros_documentos" not in db.list_collection_names():
            db.create_collection("sinistros_documentos")
            print("✓ Coleção 'sinistros_documentos' criada")

        # Índices para documentos de sinistros
        sinistros_docs = db["sinistros_documentos"]
        sinistros_docs.create_index([("sinistro_id", ASCENDING)])
        sinistros_docs.create_index([("apolice_id", ASCENDING)])
        sinistros_docs.create_index([("timestamp", DESCENDING)])
        print("✓ Índices de 'sinistros_documentos' criados")

        # Coleção de perfil/engajamento de clientes (opcional)
        if "clientes_perfil" not in db.list_collection_names():
            db.create_collection("clientes_perfil")
            print("✓ Coleção 'clientes_perfil' criada")

        # Índices para perfil de clientes
        clientes_perfil = db["clientes_perfil"]
        clientes_perfil.create_index([("cliente_id", ASCENDING)], unique=True)
        clientes_perfil.create_index([("ultima_atualizacao", DESCENDING)])
        print("✓ Índices de 'clientes_perfil' criados")

        # Coleção de relatórios exportados (metadados)
        if "relatorios_exportados" not in db.list_collection_names():
            db.create_collection("relatorios_exportados")
            print("✓ Coleção 'relatorios_exportados' criada")

        # Índices para relatórios
        relatorios = db["relatorios_exportados"]
        relatorios.create_index([("timestamp", DESCENDING)])
        relatorios.create_index([("usuario", ASCENDING)])
        relatorios.create_index([("tipo_relatorio", ASCENDING)])
        print("✓ Índices de 'relatorios_exportados' criados")

        return True

    except OperationFailure as e:
        print(f"✗ Erro ao criar coleções: {e}")
        return False


def inserir_log_exemplo():
    """Insere um log de exemplo para teste"""
    try:
        db = MongoDBConnection.get_database()
        if db is None:
            return False

        log_exemplo = {
            "timestamp": datetime.now(),
            "usuario": "sistema",
            "operacao": "setup_inicial",
            "entidade": "mongodb",
            "detalhes": {
                "mensagem": "Setup inicial do MongoDB concluído com sucesso",
                "versao": "1.0",
            },
        }

        resultado = db["auditoria"].insert_one(log_exemplo)
        print(f"✓ Log de exemplo inserido: {resultado.inserted_id}")
        return True

    except Exception as e:
        print(f"✗ Erro ao inserir log de exemplo: {e}")
        return False


if __name__ == "__main__":
    print("=== Setup do MongoDB ===")
    print(f"Host: {MONGODB_CONFIG['host']}:{MONGODB_CONFIG['port']}")
    print(f"Database: {MONGODB_CONFIG['database']}")
    print()

    if criar_colecoes():
        if inserir_log_exemplo():
            print("\n✓ Setup do MongoDB completo!")
        else:
            print("\n⚠ Setup completo, mas erro ao inserir log de exemplo")
    else:
        print("\n✗ Erro no setup do MongoDB")

    MongoDBConnection.close()
