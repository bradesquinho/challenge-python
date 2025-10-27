"""
Configurações de conexão para MySQL e MongoDB
Utilize variáveis de ambiente para configurar em produção
"""
import os

from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações MySQL
MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "sistema_seguros"),
    "charset": "utf8mb4",
    "collation": "utf8mb4_unicode_ci",
}

# Configurações MongoDB
MONGODB_CONFIG = {
    "host": os.getenv("MONGODB_HOST", "localhost"),
    "port": int(os.getenv("MONGODB_PORT", 27017)),
    "database": os.getenv("MONGODB_DATABASE", "sistema_seguros_logs"),
    "username": os.getenv("MONGODB_USER", ""),
    "password": os.getenv("MONGODB_PASSWORD", ""),
}


# String de conexão MongoDB
def get_mongodb_uri():
    """Retorna a URI de conexão do MongoDB"""
    if MONGODB_CONFIG["username"] and MONGODB_CONFIG["password"]:
        return f"mongodb://{MONGODB_CONFIG['username']}:{MONGODB_CONFIG['password']}@{MONGODB_CONFIG['host']}:{MONGODB_CONFIG['port']}"
    return f"mongodb://{MONGODB_CONFIG['host']}:{MONGODB_CONFIG['port']}"
