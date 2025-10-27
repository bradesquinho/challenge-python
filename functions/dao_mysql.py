"""
Data Access Objects (DAOs) para MySQL - REFATORADO
Sprint 4 - Persistência Híbrida com Injeção de Dependência
Suporta injeção de conexão para testes isolados
"""
import json
import os
import sys
from typing import Any, Optional

import mysql.connector
from mysql.connector import Error

# Adiciona o diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MYSQL_CONFIG


def get_connection():
    """Cria e retorna uma conexão com o MySQL"""
    try:
        return mysql.connector.connect(
            host=MYSQL_CONFIG["host"],
            port=MYSQL_CONFIG["port"],
            user=MYSQL_CONFIG["user"],
            password=MYSQL_CONFIG["password"],
            database=MYSQL_CONFIG["database"],
            charset=MYSQL_CONFIG["charset"],
            collation=MYSQL_CONFIG["collation"],
        )
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None


class UsuarioDAO:
    """DAO para gerenciar usuários - Suporta injeção de dependência"""

    def __init__(self, connection=None):
        """Inicializa o DAO. Args: connection: Conexão MySQL opcional. Se None, cria uma nova."""
        self._external_conn = connection

    def _get_conn(self):
        """Retorna conexão externa ou cria nova"""
        return self._external_conn if self._external_conn else get_connection()

    def _should_close(self):
        """Retorna True se deve fechar conexão (quando não é externa)"""
        return self._external_conn is None

    def criar(self, usuario: dict[str, Any]) -> int:
        conn = self._get_conn()
        if not conn:
            return 0
        try:
            cursor = conn.cursor()
            # Aceita tanto senha quanto senha
            senha = usuario.get("senha") or usuario.get("senha")
            cursor.execute(
                "INSERT INTO usuarios (username, senha, tipo) VALUES (%s, %s, %s)",
                (usuario["username"], senha, usuario["tipo"]),
            )
            conn.commit()
            id_ = cursor.lastrowid
            cursor.close()
            if self._should_close():
                conn.close()
            return id_
        except Error as e:
            print(f"Erro ao criar usuário: {e}")
            return 0

    def ler_por_username(self, username: str) -> Optional[dict[str, Any]]:
        conn = self._get_conn()
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, senha, tipo FROM usuarios WHERE username = %s",
                (username,),
            )
            row = cursor.fetchone()
            cursor.close()
            if self._should_close():
                conn.close()
            if row:
                return dict(zip(["id", "username", "senha", "tipo"], row))
            return None
        except Error as e:
            print(f"Erro ao ler usuário: {e}")
            return None

    def ler_por_id(self, usuario_id: int) -> Optional[dict[str, Any]]:
        """Busca usuário por ID"""
        conn = self._get_conn()
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, senha, tipo FROM usuarios WHERE id = %s", (usuario_id,)
            )
            row = cursor.fetchone()
            cursor.close()
            if self._should_close():
                conn.close()
            if row:
                return dict(zip(["id", "username", "senha", "tipo"], row))
            return None
        except Error as e:
            print(f"Erro ao ler usuário por ID: {e}")
            return None

    def ler(self, usuario_id: int) -> Optional[dict[str, Any]]:
        """Alias para ler_por_id - compatibilidade com testes"""
        return self.ler_por_id(usuario_id)

    def listar(self) -> list[dict[str, Any]]:
        conn = self._get_conn()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, senha, tipo FROM usuarios")
            rows = cursor.fetchall()
            cursor.close()
            if self._should_close():
                conn.close()
            return [dict(zip(["id", "username", "senha", "tipo"], row)) for row in rows]
        except Error as e:
            print(f"Erro ao listar usuários: {e}")
            return []


class ClienteDAO:
    """DAO para gerenciar clientes - Suporta injeção de dependência"""

    def __init__(self, connection=None):
        """Inicializa o DAO. Args: connection: Conexão MySQL opcional. Se None, cria uma nova."""
        self._external_conn = connection

    def _get_conn(self):
        return self._external_conn if self._external_conn else get_connection()

    def _should_close(self):
        return self._external_conn is None

    def criar(self, cliente: dict[str, Any]) -> int:
        conn = self._get_conn()
        if not conn:
            raise Exception("Erro: Conexão com banco de dados não disponível")
        try:
            cursor = conn.cursor()
            # Aceita tanto data_nasc quanto data_nasc
            data_nasc = cliente.get("data_nasc") or cliente.get("data_nasc")
            cursor.execute(
                "INSERT INTO clientes (nome, cpf, telefone, email, data_nasc, endereco) VALUES (%s, %s, %s, %s, %s, %s)",
                (
                    cliente["nome"],
                    cliente["cpf"],
                    cliente.get("telefone"),
                    cliente.get("email"),
                    data_nasc,
                    cliente["endereco"],
                ),
            )
            conn.commit()
            id_ = cursor.lastrowid
            cursor.close()
            if self._should_close():
                conn.close()
            return id_
        except Error as e:
            print(f"Erro ao criar cliente: {e}")
            raise Exception(f"Erro ao criar cliente: {e}")

    def ler_por_id(self, cliente_id: int) -> Optional[dict[str, Any]]:
        conn = self._get_conn()
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, nome, cpf, telefone, email, data_nasc, endereco FROM clientes WHERE id = %s",
                (cliente_id,),
            )
            row = cursor.fetchone()
            cursor.close()
            if self._should_close():
                conn.close()
            if row:
                return dict(
                    zip(
                        ["id", "nome", "cpf", "telefone", "email", "data_nasc", "endereco"],
                        row,
                    )
                )
            return None
        except Error as e:
            print(f"Erro ao ler cliente: {e}")
            return None

    def ler(self, cliente_id: int) -> Optional[dict[str, Any]]:
        """Alias para ler_por_id - compatibilidade com testes"""
        return self.ler_por_id(cliente_id)

    def ler_por_cpf(self, cpf: str) -> Optional[dict[str, Any]]:
        conn = self._get_conn()
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, nome, cpf, telefone, email, data_nasc, endereco FROM clientes WHERE cpf = %s",
                (cpf,),
            )
            row = cursor.fetchone()
            cursor.close()
            if self._should_close():
                conn.close()
            if row:
                return dict(
                    zip(
                        ["id", "nome", "cpf", "telefone", "email", "data_nasc", "endereco"],
                        row,
                    )
                )
            return None
        except Error as e:
            print(f"Erro ao ler cliente por CPF: {e}")
            return None

    def atualizar(self, cliente_id: int, dados: dict[str, Any]) -> bool:
        conn = self._get_conn()
        if not conn:
            return False
        try:
            # Constrói UPDATE dinâmico apenas com campos fornecidos
            campos = []
            valores = []

            # Mapeamento de campos (aceita both variantes)
            if "nome" in dados:
                campos.append("nome=%s")
                valores.append(dados["nome"])
            if "cpf" in dados:
                campos.append("cpf=%s")
                valores.append(dados["cpf"])
            if "telefone" in dados:
                campos.append("telefone=%s")
                valores.append(dados["telefone"])
            if "email" in dados:
                campos.append("email=%s")
                valores.append(dados["email"])
            if "data_nasc" in dados:
                campos.append("data_nasc=%s")
                valores.append(dados["data_nasc"])
            elif "data_nasc" in dados:
                campos.append("data_nasc=%s")
                valores.append(dados["data_nasc"])
            if "endereco" in dados:
                campos.append("endereco=%s")
                valores.append(dados["endereco"])

            if not campos:
                return False  # Nada para atualizar

            valores.append(cliente_id)
            query = f"UPDATE clientes SET {', '.join(campos)} WHERE id=%s"

            cursor = conn.cursor()
            cursor.execute(query, tuple(valores))
            conn.commit()
            atualizado = cursor.rowcount > 0
            cursor.close()
            if self._should_close():
                conn.close()
            return atualizado
        except Error as e:
            print(f"Erro ao atualizar cliente: {e}")
            return False

    def deletar(self, cliente_id: int) -> bool:
        conn = self._get_conn()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clientes WHERE id=%s", (cliente_id,))
            conn.commit()
            deletado = cursor.rowcount > 0
            cursor.close()
            if self._should_close():
                conn.close()
            return deletado
        except Error as e:
            print(f"Erro ao deletar cliente: {e}")
            return False

    def listar(self) -> list[dict[str, Any]]:
        conn = self._get_conn()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, nome, cpf, telefone, email, data_nasc, endereco FROM clientes"
            )
            rows = cursor.fetchall()
            cursor.close()
            if self._should_close():
                conn.close()
            return [
                dict(
                    zip(
                        ["id", "nome", "cpf", "telefone", "email", "data_nasc", "endereco"],
                        row,
                    )
                )
                for row in rows
            ]
        except Error as e:
            print(f"Erro ao listar clientes: {e}")
            return []


class SeguroDAO:
    """DAO para gerenciar seguros - Suporta injeção de dependência"""

    def __init__(self, connection=None):
        """Inicializa o DAO. Args: connection: Conexão MySQL opcional. Se None, cria uma nova."""
        self._external_conn = connection

    def _get_conn(self):
        return self._external_conn if self._external_conn else get_connection()

    def _should_close(self):
        return self._external_conn is None

    def criar(self, seguro: dict[str, Any]) -> int:
        conn = self._get_conn()
        if not conn:
            return 0
        try:
            cursor = conn.cursor()
            # Converte detalhes para JSON se for dict
            detalhes = seguro.get("detalhes")
            if isinstance(detalhes, dict):
                detalhes = json.dumps(detalhes)

            cursor.execute(
                "INSERT INTO seguros (tipo, descricao, valor, detalhes, cliente_id) VALUES (%s, %s, %s, %s, %s)",
                (
                    seguro["tipo"],
                    seguro.get("descricao"),
                    seguro.get("valor", 0.0),
                    detalhes,
                    seguro.get("cliente_id"),
                ),
            )
            conn.commit()
            id_ = cursor.lastrowid
            cursor.close()
            if self._should_close():
                conn.close()
            return id_
        except Error as e:
            print(f"Erro ao criar seguro: {e}")
            return 0

    def ler_por_id(self, seguro_id: int) -> Optional[dict[str, Any]]:
        conn = self._get_conn()
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, tipo, descricao, valor, detalhes, cliente_id FROM seguros WHERE id = %s",
                (seguro_id,),
            )
            row = cursor.fetchone()
            cursor.close()
            if self._should_close():
                conn.close()
            if row:
                resultado = dict(
                    zip(["id", "tipo", "descricao", "valor", "detalhes", "cliente_id"], row)
                )
                # Parse JSON se detalhes for string
                if resultado["detalhes"] and isinstance(resultado["detalhes"], str):
                    try:
                        resultado["detalhes"] = json.loads(resultado["detalhes"])
                    except:
                        pass
                return resultado
            return None
        except Error as e:
            print(f"Erro ao ler seguro: {e}")
            return None

    def ler(self, seguro_id: int) -> Optional[dict[str, Any]]:
        """Alias para ler_por_id - compatibilidade com testes"""
        return self.ler_por_id(seguro_id)

    def atualizar(self, seguro_id: int, dados: dict[str, Any]) -> bool:
        conn = self._get_conn()
        if not conn:
            return False
        try:
            # Constrói UPDATE dinâmico apenas com campos fornecidos
            campos = []
            valores = []

            if "tipo" in dados:
                campos.append("tipo=%s")
                valores.append(dados["tipo"])
            if "descricao" in dados:
                campos.append("descricao=%s")
                valores.append(dados["descricao"])
            if "valor" in dados:
                campos.append("valor=%s")
                valores.append(dados["valor"])
            if "detalhes" in dados:
                campos.append("detalhes=%s")
                detalhes = dados["detalhes"]
                if isinstance(detalhes, dict):
                    detalhes = json.dumps(detalhes)
                valores.append(detalhes)
            if "cliente_id" in dados:
                campos.append("cliente_id=%s")
                valores.append(dados["cliente_id"])

            if not campos:
                return False  # Nada para atualizar

            valores.append(seguro_id)
            query = f"UPDATE seguros SET {', '.join(campos)} WHERE id=%s"

            cursor = conn.cursor()
            cursor.execute(query, tuple(valores))
            conn.commit()
            atualizado = cursor.rowcount > 0
            cursor.close()
            if self._should_close():
                conn.close()
            return atualizado
        except Error as e:
            print(f"Erro ao atualizar seguro: {e}")
            return False

    def deletar(self, seguro_id: int) -> bool:
        conn = self._get_conn()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM seguros WHERE id=%s", (seguro_id,))
            conn.commit()
            deletado = cursor.rowcount > 0
            cursor.close()
            if self._should_close():
                conn.close()
            return deletado
        except Error as e:
            print(f"Erro ao deletar seguro: {e}")
            return False

    def listar(self) -> list[dict[str, Any]]:
        conn = self._get_conn()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, tipo, descricao, valor, detalhes, cliente_id FROM seguros")
            rows = cursor.fetchall()
            cursor.close()
            if self._should_close():
                conn.close()
            resultado = []
            for row in rows:
                item = dict(
                    zip(["id", "tipo", "descricao", "valor", "detalhes", "cliente_id"], row)
                )
                if item["detalhes"] and isinstance(item["detalhes"], str):
                    try:
                        item["detalhes"] = json.loads(item["detalhes"])
                    except:
                        pass
                resultado.append(item)
            return resultado
        except Error as e:
            print(f"Erro ao listar seguros: {e}")
            return []


class ApoliceDAO:
    """DAO para gerenciar apólices - Suporta injeção de dependência"""

    def __init__(self, connection=None):
        """Inicializa o DAO. Args: connection: Conexão MySQL opcional. Se None, cria uma nova."""
        self._external_conn = connection

    def _get_conn(self):
        return self._external_conn if self._external_conn else get_connection()

    def _should_close(self):
        return self._external_conn is None

    def criar(self, apolice: dict[str, Any]) -> int:
        conn = self._get_conn()
        if not conn:
            raise Exception("Erro: Conexão com banco de dados não disponível")
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO apolices (cliente_id, seguro_id, data_emissao, status) VALUES (%s, %s, %s, %s)",
                (
                    apolice["cliente_id"],
                    apolice["seguro_id"],
                    apolice.get("data_emissao"),
                    apolice.get("status", "ativa"),
                ),
            )
            conn.commit()
            id_ = cursor.lastrowid
            cursor.close()
            if self._should_close():
                conn.close()
            return id_
        except Error as e:
            print(f"Erro ao criar apólice: {e}")
            raise Exception(f"Erro ao criar apólice: {e}")

    def ler_por_id(self, apolice_id: int) -> Optional[dict[str, Any]]:
        conn = self._get_conn()
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, cliente_id, seguro_id, data_emissao, status FROM apolices WHERE id = %s",
                (apolice_id,),
            )
            row = cursor.fetchone()
            cursor.close()
            if self._should_close():
                conn.close()
            if row:
                return dict(
                    zip(
                        [
                            "id",
                            "cliente_id",
                            "seguro_id",
                            "data_emissao",
                            "status",
                        ],
                        row,
                    )
                )
            return None
        except Error as e:
            print(f"Erro ao ler apólice: {e}")
            return None

    def ler(self, apolice_id: int) -> Optional[dict[str, Any]]:
        """Alias para ler_por_id - compatibilidade com testes"""
        return self.ler_por_id(apolice_id)

    def atualizar(self, apolice_id: int, dados: dict[str, Any]) -> bool:
        conn = self._get_conn()
        if not conn:
            return False
        try:
            # Constrói UPDATE dinâmico apenas com campos fornecidos
            campos = []
            valores = []

            if "cliente_id" in dados:
                campos.append("cliente_id=%s")
                valores.append(dados["cliente_id"])
            if "seguro_id" in dados:
                campos.append("seguro_id=%s")
                valores.append(dados["seguro_id"])
            if "data_emissao" in dados:
                campos.append("data_emissao=%s")
                valores.append(dados["data_emissao"])
            if "status" in dados:
                campos.append("status=%s")
                valores.append(dados["status"])

            if not campos:
                return False  # Nada para atualizar

            valores.append(apolice_id)
            query = f"UPDATE apolices SET {', '.join(campos)} WHERE id=%s"

            cursor = conn.cursor()
            cursor.execute(query, tuple(valores))
            conn.commit()
            atualizado = cursor.rowcount > 0
            cursor.close()
            if self._should_close():
                conn.close()
            return atualizado
        except Error as e:
            print(f"Erro ao atualizar apólice: {e}")
            return False

    def deletar(self, apolice_id: int) -> bool:
        conn = self._get_conn()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM apolices WHERE id=%s", (apolice_id,))
            conn.commit()
            deletado = cursor.rowcount > 0
            cursor.close()
            if self._should_close():
                conn.close()
            return deletado
        except Error as e:
            print(f"Erro ao deletar apólice: {e}")
            return False

    def listar(self) -> list[dict[str, Any]]:
        conn = self._get_conn()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, cliente_id, seguro_id, data_emissao, status FROM apolices"
            )
            rows = cursor.fetchall()
            cursor.close()
            if self._should_close():
                conn.close()
            return [
                dict(
                    zip(
                        [
                            "id",
                            "cliente_id",
                            "seguro_id",
                            "data_emissao",
                            "status",
                        ],
                        row,
                    )
                )
                for row in rows
            ]
        except Error as e:
            print(f"Erro ao listar apólices: {e}")
            return []


class SinistroDAO:
    """DAO para gerenciar sinistros - Suporta injeção de dependência"""

    def __init__(self, connection=None):
        """Inicializa o DAO. Args: connection: Conexão MySQL opcional. Se None, cria uma nova."""
        self._external_conn = connection

    def _get_conn(self):
        return self._external_conn if self._external_conn else get_connection()

    def _should_close(self):
        return self._external_conn is None

    def criar(self, sinistro: dict[str, Any]) -> int:
        conn = self._get_conn()
        if not conn:
            raise Exception("Erro: Conexão com banco de dados não disponível")
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO sinistros (apolice_id, data_ocorrencia, descricao, status) VALUES (%s, %s, %s, %s)",
                (
                    sinistro["apolice_id"],
                    sinistro.get("data_ocorrencia"),
                    sinistro.get("descricao"),
                    sinistro.get("status", "aberto"),
                ),
            )
            conn.commit()
            id_ = cursor.lastrowid
            cursor.close()
            if self._should_close():
                conn.close()
            return id_
        except Error as e:
            print(f"Erro ao criar sinistro: {e}")
            raise Exception(f"Erro ao criar sinistro: {e}")

    def ler_por_id(self, sinistro_id: int) -> Optional[dict[str, Any]]:
        conn = self._get_conn()
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, apolice_id, data_ocorrencia, descricao, status FROM sinistros WHERE id = %s",
                (sinistro_id,),
            )
            row = cursor.fetchone()
            cursor.close()
            if self._should_close():
                conn.close()
            if row:
                return dict(
                    zip(
                        [
                            "id",
                            "apolice_id",
                            "data_ocorrencia",
                            "descricao",
                            "status",
                        ],
                        row,
                    )
                )
            return None
        except Error as e:
            print(f"Erro ao ler sinistro: {e}")
            return None

    def ler(self, sinistro_id: int) -> Optional[dict[str, Any]]:
        """Alias para ler_por_id - compatibilidade com testes"""
        return self.ler_por_id(sinistro_id)

    def atualizar(self, sinistro_id: int, dados: dict[str, Any]) -> bool:
        conn = self._get_conn()
        if not conn:
            return False
        try:
            # Constrói UPDATE dinâmico apenas com campos fornecidos
            campos = []
            valores = []

            if "apolice_id" in dados:
                campos.append("apolice_id=%s")
                valores.append(dados["apolice_id"])
            if "data_ocorrencia" in dados:
                campos.append("data_ocorrencia=%s")
                valores.append(dados["data_ocorrencia"])
            if "descricao" in dados:
                campos.append("descricao=%s")
                valores.append(dados["descricao"])
            if "status" in dados:
                campos.append("status=%s")
                valores.append(dados["status"])

            if not campos:
                return False  # Nada para atualizar

            valores.append(sinistro_id)
            query = f"UPDATE sinistros SET {', '.join(campos)} WHERE id=%s"

            cursor = conn.cursor()
            cursor.execute(query, tuple(valores))
            conn.commit()
            atualizado = cursor.rowcount > 0
            cursor.close()
            if self._should_close():
                conn.close()
            return atualizado
        except Error as e:
            print(f"Erro ao atualizar sinistro: {e}")
            return False

    def deletar(self, sinistro_id: int) -> bool:
        conn = self._get_conn()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sinistros WHERE id=%s", (sinistro_id,))
            conn.commit()
            deletado = cursor.rowcount > 0
            cursor.close()
            if self._should_close():
                conn.close()
            return deletado
        except Error as e:
            print(f"Erro ao deletar sinistro: {e}")
            return False

    def listar(self) -> list[dict[str, Any]]:
        conn = self._get_conn()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, apolice_id, data_ocorrencia, descricao, status FROM sinistros"
            )
            rows = cursor.fetchall()
            cursor.close()
            if self._should_close():
                conn.close()
            return [
                dict(
                    zip(
                        [
                            "id",
                            "apolice_id",
                            "data_ocorrencia",
                            "descricao",
                            "status",
                        ],
                        row,
                    )
                )
                for row in rows
            ]
        except Error as e:
            print(f"Erro ao listar sinistros: {e}")
            return []
