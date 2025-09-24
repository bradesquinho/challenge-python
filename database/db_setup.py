import sqlite3

DB_NAME = 'sistema_seguros.db'

def criar_tabelas():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        tipo TEXT NOT NULL CHECK(tipo IN ('admin', 'comum'))
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        cpf TEXT UNIQUE NOT NULL,
        telefone TEXT,
        email TEXT,
        data_nasc TEXT,
        endereco TEXT
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS seguros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT NOT NULL,
        descricao TEXT,
        valor REAL,
        detalhes TEXT,
        cliente_id INTEGER NOT NULL,
        FOREIGN KEY(cliente_id) REFERENCES clientes(id)
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS apolices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER NOT NULL,
        seguro_id INTEGER NOT NULL,
        data_emissao TEXT,
        status TEXT,
        FOREIGN KEY(cliente_id) REFERENCES clientes(id),
        FOREIGN KEY(seguro_id) REFERENCES seguros(id)
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sinistros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        apolice_id INTEGER NOT NULL,
        data_ocorrencia TEXT,
        descricao TEXT,
        status TEXT,
        FOREIGN KEY(apolice_id) REFERENCES apolices(id)
    )''')

    conn.commit()
    conn.close()

def atualizar_schema():
    """Executa comandos de atualização do schema, se necessário."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Exemplo: adicionar uma coluna se não existir
    try:
        cursor.execute("ALTER TABLE clientes ADD COLUMN novo_campo TEXT")
    except sqlite3.OperationalError:
        # Coluna já existe, ignora o erro
        pass
    # Adicione outros comandos de migração aqui
    conn.commit()
    conn.close()

if __name__ == '__main__':
    criar_tabelas()
    # atualizar_schema()  # Descomente se/quando precisar atualizar o schema