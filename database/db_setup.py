"""
Setup do banco de dados MySQL
Sprint 4 - Persistência Híbrida
"""
import os
import sys

import mysql.connector
from mysql.connector import Error

# Adiciona o diretório pai ao path para importar config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MYSQL_CONFIG


def get_connection():
    """Cria e retorna uma conexão com o MySQL"""
    try:
        conn = mysql.connector.connect(
            host=MYSQL_CONFIG["host"],
            port=MYSQL_CONFIG["port"],
            user=MYSQL_CONFIG["user"],
            password=MYSQL_CONFIG["password"],
            charset=MYSQL_CONFIG["charset"],
            collation=MYSQL_CONFIG["collation"],
        )
        return conn
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None


def criar_database():
    """Cria o banco de dados se não existir"""
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {MYSQL_CONFIG['database']} CHARACTER SET {MYSQL_CONFIG['charset']} COLLATE {MYSQL_CONFIG['collation']}"
        )
        print(f"Database '{MYSQL_CONFIG['database']}' criado/verificado com sucesso!")
        cursor.close()
        conn.close()
        return True
    except Error as e:
        print(f"Erro ao criar database: {e}")
        return False


def criar_tabelas():
    """Cria as tabelas no MySQL"""
    try:
        conn = mysql.connector.connect(
            host=MYSQL_CONFIG["host"],
            port=MYSQL_CONFIG["port"],
            user=MYSQL_CONFIG["user"],
            password=MYSQL_CONFIG["password"],
            database=MYSQL_CONFIG["database"],
            charset=MYSQL_CONFIG["charset"],
            collation=MYSQL_CONFIG["collation"],
        )
        cursor = conn.cursor()

        # Tabela de usuários
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            senha VARCHAR(255) NOT NULL,
            tipo ENUM('admin', 'comum') NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_username (username)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        )

        # Tabela de clientes
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS clientes (
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

        # Tabela de seguros
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS seguros (
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

        # Tabela de apólices
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS apolices (
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

        # Tabela de sinistros
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS sinistros (
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
        print("Tabelas criadas com sucesso no MySQL!")
        cursor.close()
        conn.close()
        return True

    except Error as e:
        print(f"Erro ao criar tabelas: {e}")
        return False


def atualizar_schema():
    """Executa comandos de atualização do schema, se necessário."""
    try:
        conn = mysql.connector.connect(
            host=MYSQL_CONFIG["host"],
            port=MYSQL_CONFIG["port"],
            user=MYSQL_CONFIG["user"],
            password=MYSQL_CONFIG["password"],
            database=MYSQL_CONFIG["database"],
        )
        cursor = conn.cursor()

        # Exemplo: adicionar uma coluna se não existir
        # Descomente e adapte conforme necessário
        # try:
        #     cursor.execute("ALTER TABLE clientes ADD COLUMN novo_campo VARCHAR(100)")
        #     print("Coluna 'novo_campo' adicionada com sucesso!")
        # except Error as e:
        #     if e.errno == 1060:  # Duplicate column name
        #         print("Coluna já existe, pulando...")
        #     else:
        #         raise

        conn.commit()
        cursor.close()
        conn.close()
        print("Schema atualizado com sucesso!")
        return True

    except Error as e:
        print(f"Erro ao atualizar schema: {e}")
        return False


if __name__ == "__main__":
    print("=== Setup do Banco de Dados MySQL ===")
    print(f"Host: {MYSQL_CONFIG['host']}")
    print(f"Database: {MYSQL_CONFIG['database']}")
    print()

    if criar_database():
        if criar_tabelas():
            print("\n✓ Setup completo!")
        else:
            print("\n✗ Erro ao criar tabelas")
    else:
        print("\n✗ Erro ao criar database")
