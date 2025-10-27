"""
Configuração para ambiente de testes
Usa bancos de dados separados para não interferir com dados de produção
"""
import os

from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configuração MySQL para testes (banco separado)
MYSQL_TEST_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": "sistema_seguros_test",  # Banco separado para testes
    "raise_on_warnings": True,
}


# Configuração MongoDB para testes (database separado)
def get_mongodb_test_uri():
    """Retorna URI de conexão do MongoDB para testes"""
    host = os.getenv("MONGODB_HOST", "localhost")
    port = os.getenv("MONGODB_PORT", "27017")
    return f"mongodb://{host}:{port}/"


MONGODB_TEST_CONFIG = {
    "uri": get_mongodb_test_uri(),
    "database": "sistema_seguros_test_logs",  # Database separado para testes
}
