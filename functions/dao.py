import sqlite3
from typing import List, Dict, Any, Optional

DB_NAME = 'sistema_seguros.db'

class UsuarioDAO:
    @staticmethod
    def criar(usuario: Dict[str, Any]) -> int:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO usuarios (username, senha, tipo) VALUES (?, ?, ?)''',
                       (usuario['username'], usuario['senha'], usuario['tipo']))
        conn.commit()
        id_ = cursor.lastrowid
        conn.close()
        return id_

    @staticmethod
    def ler_por_username(username: str) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE username = ?', (username,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(zip(['id', 'username', 'senha', 'tipo'], row))
        return None

    @staticmethod
    def listar() -> List[Dict[str, Any]]:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM usuarios')
        rows = cursor.fetchall()
        conn.close()
        return [dict(zip(['id', 'username', 'senha', 'tipo'], row)) for row in rows]

class ClienteDAO:
    @staticmethod
    def criar(cliente: Dict[str, Any]) -> int:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO clientes (nome, cpf, telefone, email, data_nasc, endereco) VALUES (?, ?, ?, ?, ?, ?)''',
                       (cliente['nome'], cliente['cpf'], cliente.get('telefone'), cliente.get('email'), cliente['data_nasc'], cliente['endereco']))
        conn.commit()
        id_ = cursor.lastrowid
        conn.close()
        return id_

    @staticmethod
    def ler_por_id(cliente_id: int) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM clientes WHERE id = ?', (cliente_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(zip(['id', 'nome', 'cpf', 'telefone', 'email', 'data_nasc', 'endereco'], row))
        return None

    @staticmethod
    def atualizar(cliente_id: int, dados: Dict[str, Any]) -> bool:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''UPDATE clientes SET nome=?, cpf=?, telefone=?, email=?, data_nasc=?, endereco=? WHERE id=?''',
                       (dados['nome'], dados['cpf'], dados.get('telefone'), dados.get('email'), dados['data_nasc'], dados['endereco'], cliente_id))
        conn.commit()
        atualizado = cursor.rowcount > 0
        conn.close()
        return atualizado

    @staticmethod
    def deletar(cliente_id: int) -> bool:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM clientes WHERE id=?', (cliente_id,))
        conn.commit()
        deletado = cursor.rowcount > 0
        conn.close()
        return deletado

    @staticmethod
    def listar() -> List[Dict[str, Any]]:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM clientes')
        rows = cursor.fetchall()
        conn.close()
        return [dict(zip(['id', 'nome', 'cpf', 'telefone', 'email', 'data_nasc', 'endereco'], row)) for row in rows]


class SeguroDAO:
    @staticmethod
    def criar(seguro: Dict[str, Any]) -> int:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO seguros (tipo, descricao, valor, detalhes, cliente_id) VALUES (?, ?, ?, ?, ?)''',
                       (seguro['tipo'], seguro.get('descricao'), seguro.get('valor'), seguro.get('detalhes'), seguro['cliente_id']))
        conn.commit()
        id_ = cursor.lastrowid
        conn.close()
        return id_

    @staticmethod
    def ler_por_id(seguro_id: int) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM seguros WHERE id = ?', (seguro_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(zip(['id', 'tipo', 'descricao', 'valor', 'detalhes', 'cliente_id'], row))
        return None

    @staticmethod
    def atualizar(seguro_id: int, dados: Dict[str, Any]) -> bool:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''UPDATE seguros SET tipo=?, descricao=?, valor=?, detalhes=?, cliente_id=? WHERE id=?''',
                       (dados['tipo'], dados.get('descricao'), dados.get('valor'), dados.get('detalhes'), dados['cliente_id'], seguro_id))
        conn.commit()
        atualizado = cursor.rowcount > 0
        conn.close()
        return atualizado

    @staticmethod
    def deletar(seguro_id: int) -> bool:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM seguros WHERE id=?', (seguro_id,))
        conn.commit()
        deletado = cursor.rowcount > 0
        conn.close()
        return deletado

    @staticmethod
    def listar() -> List[Dict[str, Any]]:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM seguros')
        rows = cursor.fetchall()
        conn.close()
        return [dict(zip(['id', 'tipo', 'descricao', 'valor', 'detalhes', 'cliente_id'], row)) for row in rows]

class ApoliceDAO:
    @staticmethod
    def criar(apolice: Dict[str, Any]) -> int:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO apolices (cliente_id, seguro_id, data_emissao, status) VALUES (?, ?, ?, ?)''',
                       (apolice['cliente_id'], apolice['seguro_id'], apolice.get('data_emissao'), apolice.get('status')))
        conn.commit()
        id_ = cursor.lastrowid
        conn.close()
        return id_

    @staticmethod
    def ler_por_id(apolice_id: int) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM apolices WHERE id = ?', (apolice_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(zip(['id', 'cliente_id', 'seguro_id', 'data_emissao', 'status'], row))
        return None

    @staticmethod
    def atualizar(apolice_id: int, dados: Dict[str, Any]) -> bool:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''UPDATE apolices SET cliente_id=?, seguro_id=?, data_emissao=?, status=? WHERE id=?''',
                       (dados['cliente_id'], dados['seguro_id'], dados.get('data_emissao'), dados.get('status'), apolice_id))
        conn.commit()
        atualizado = cursor.rowcount > 0
        conn.close()
        return atualizado

    @staticmethod
    def deletar(apolice_id: int) -> bool:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM apolices WHERE id=?', (apolice_id,))
        conn.commit()
        deletado = cursor.rowcount > 0
        conn.close()
        return deletado

    @staticmethod
    def listar() -> List[Dict[str, Any]]:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM apolices')
        rows = cursor.fetchall()
        conn.close()
        return [dict(zip(['id', 'cliente_id', 'seguro_id', 'data_emissao', 'status'], row)) for row in rows]

class SinistroDAO:
    @staticmethod
    def criar(sinistro: Dict[str, Any]) -> int:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO sinistros (apolice_id, data_ocorrencia, descricao, status) VALUES (?, ?, ?, ?)''',
                       (sinistro['apolice_id'], sinistro.get('data_ocorrencia'), sinistro.get('descricao'), sinistro.get('status')))
        conn.commit()
        id_ = cursor.lastrowid
        conn.close()
        return id_

    @staticmethod
    def ler_por_id(sinistro_id: int) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM sinistros WHERE id = ?', (sinistro_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(zip(['id', 'apolice_id', 'data_ocorrencia', 'descricao', 'status'], row))
        return None

    @staticmethod
    def atualizar(sinistro_id: int, dados: Dict[str, Any]) -> bool:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''UPDATE sinistros SET apolice_id=?, data_ocorrencia=?, descricao=?, status=? WHERE id=?''',
                       (dados['apolice_id'], dados.get('data_ocorrencia'), dados.get('descricao'), dados.get('status'), sinistro_id))
        conn.commit()
        atualizado = cursor.rowcount > 0
        conn.close()
        return atualizado

    @staticmethod
    def deletar(sinistro_id: int) -> bool:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM sinistros WHERE id=?', (sinistro_id,))
        conn.commit()
        deletado = cursor.rowcount > 0
        conn.close()
        return deletado

    @staticmethod
    def listar() -> List[Dict[str, Any]]:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM sinistros')
        rows = cursor.fetchall()
        conn.close()
        return [dict(zip(['id', 'apolice_id', 'data_ocorrencia', 'descricao', 'status'], row)) for row in rows]
