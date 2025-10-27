"""
Serviço de Auditoria com MongoDB - REFATORADO
Sprint 4 - Logs enriquecidos e persistência híbrida com injeção de dependência
Suporta injeção de database para testes isolados
"""
import os
import sys
from datetime import datetime
from typing import Any, Optional

# Adiciona o diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from database.mongo_setup import MongoDBConnection

    MONGODB_DISPONIVEL = True
except ImportError:
    MONGODB_DISPONIVEL = False
    print("⚠ MongoDB não disponível - logs serão salvos apenas em arquivo")


class AuditoriaService:
    """Serviço de auditoria que grava logs no MongoDB e arquivo - Suporta injeção de dependência"""

    def __init__(self, database=None):
        """Inicializa o serviço. Args: database: MongoDB database opcional. Se None, obtém do MongoDBConnection."""
        self._external_db = database

    def _get_db(self):
        """Retorna database externo ou obtém do MongoDBConnection"""
        if self._external_db is not None:
            return self._external_db
        if MONGODB_DISPONIVEL:
            return MongoDBConnection.get_database()
        return None

    def registrar_log(
        self,
        usuario: str,
        operacao: str,
        entidade: str,
        entidade_id: Optional[int] = None,
        detalhes: Optional[dict[str, Any]] = None,
        status: str = "sucesso",
    ):
        """
        Registra um log de auditoria no MongoDB e arquivo

        Args:
            usuario: Nome do usuário que realizou a operação
            operacao: Tipo de operação (criar, atualizar, deletar, consultar, etc)
            entidade: Tipo de entidade (cliente, apolice, sinistro, etc)
            entidade_id: ID da entidade afetada
            detalhes: Detalhes adicionais da operação
            status: Status da operação (sucesso, erro, warning)

        Returns:
            str: ID do log inserido no MongoDB, ou None se falhou
        """
        timestamp = datetime.now()

        log_documento = {
            "timestamp": timestamp,
            "usuario": usuario,
            "operacao": operacao,
            "entidade": entidade,
            "entidade_id": entidade_id,
            "status": status,
            "detalhes": detalhes or {},
        }

        # Grava no MongoDB se disponível
        log_id = None
        try:
            db = self._get_db()
            if db is not None:
                resultado = db["auditoria"].insert_one(log_documento)
                log_id = str(resultado.inserted_id)
        except Exception as e:
            print(f"Erro ao gravar log no MongoDB: {e}")

        # Também grava em arquivo (backup)
        _gravar_log_arquivo(log_documento)

        return log_id

    def consultar_logs(
        self,
        usuario: Optional[str] = None,
        operacao: Optional[str] = None,
        entidade: Optional[str] = None,
        limite: int = 100,
    ):
        """Consulta logs de auditoria no MongoDB"""
        try:
            db = self._get_db()
            if db is None:
                return []

            filtro = {}
            if usuario:
                filtro["usuario"] = usuario
            if operacao:
                filtro["operacao"] = operacao
            if entidade:
                filtro["entidade"] = entidade

            logs = list(db["auditoria"].find(filtro).sort("timestamp", -1).limit(limite))

            # Converte ObjectId para string
            for log in logs:
                log["_id"] = str(log["_id"])

            return logs
        except Exception as e:
            print(f"Erro ao consultar logs: {e}")
            return []

    # Métodos alias para compatibilidade com testes
    def listar_logs(self, limite: int = 100):
        """Alias para consultar_logs sem filtros"""
        return self.consultar_logs(limite=limite)

    def buscar_logs_por_usuario(self, usuario: str, limite: int = 100):
        """Alias para consultar_logs filtrado por usuário"""
        return self.consultar_logs(usuario=usuario, limite=limite)

    def buscar_logs_por_entidade(self, entidade: str, limite: int = 100):
        """Alias para consultar_logs filtrado por entidade"""
        return self.consultar_logs(entidade=entidade, limite=limite)


class SinistroDocumentosService:
    """Serviço para gerenciar documentos e anexos de sinistros no MongoDB - Suporta injeção de dependência"""

    def __init__(self, database=None):
        """Inicializa o serviço. Args: database: MongoDB database opcional. Se None, obtém do MongoDBConnection."""
        self._external_db = database

    def _get_db(self):
        if self._external_db is not None:
            return self._external_db
        if MONGODB_DISPONIVEL:
            return MongoDBConnection.get_database()
        return None

    def adicionar_documento(
        self,
        sinistro_id: int,
        tipo_documento: str,
        caminho_arquivo: Optional[str] = None,
        descricao: Optional[str] = None,
        apolice_id: Optional[int] = None,
        conteudo: Optional[str] = None,
        metadados: Optional[dict[str, Any]] = None,
    ):
        """
        Adiciona um documento/observação ao sinistro

        Args:
            sinistro_id: ID do sinistro
            tipo_documento: Tipo do documento (BOLETIM_OCORRENCIA, FOTOS, etc)
            caminho_arquivo: Caminho do arquivo (para documentos físicos)
            descricao: Descrição do documento
            apolice_id: ID da apólice (opcional, para compatibilidade)
            conteudo: Conteúdo textual (para observações)
            metadados: Metadados adicionais
        """
        try:
            db = self._get_db()
            if db is None:
                print("MongoDB não disponível")
                return None

            documento = {
                "sinistro_id": sinistro_id,
                "tipo_documento": tipo_documento,
                "metadados": metadados or {},
                "timestamp": datetime.now(),
            }

            # Adiciona campos opcionais
            if apolice_id:
                documento["apolice_id"] = apolice_id
            if caminho_arquivo:
                documento["caminho_arquivo"] = caminho_arquivo
            if descricao:
                documento["descricao"] = descricao
            if conteudo:
                documento["conteudo"] = conteudo

            resultado = db["sinistros_documentos"].insert_one(documento)
            return str(resultado.inserted_id)
        except Exception as e:
            print(f"Erro ao adicionar documento: {e}")
            return None

    def listar_documentos(self, sinistro_id: int):
        """Lista todos os documentos de um sinistro"""
        try:
            db = self._get_db()
            if db is None:
                return []

            documentos = list(
                db["sinistros_documentos"].find({"sinistro_id": sinistro_id}).sort("timestamp", -1)
            )

            # Converte ObjectId para string
            for doc in documentos:
                doc["_id"] = str(doc["_id"])

            return documentos
        except Exception as e:
            print(f"Erro ao listar documentos: {e}")
            return []

    # Métodos alias para compatibilidade com testes
    def listar_documentos_sinistro(self, sinistro_id: int):
        """Alias para listar_documentos"""
        return self.listar_documentos(sinistro_id)

    def buscar_por_tipo(self, sinistro_id: int, tipo_documento: str):
        """Busca documentos de um sinistro por tipo"""
        try:
            db = self._get_db()
            if db is None:
                return []

            documentos = list(
                db["sinistros_documentos"]
                .find({"sinistro_id": sinistro_id, "tipo_documento": tipo_documento})
                .sort("timestamp", -1)
            )

            # Converte ObjectId para string
            for doc in documentos:
                doc["_id"] = str(doc["_id"])

            return documentos
        except Exception as e:
            print(f"Erro ao buscar documentos por tipo: {e}")
            return []


class ClientePerfilService:
    """Serviço para gerenciar perfil e histórico de engajamento do cliente - Suporta injeção de dependência"""

    def __init__(self, database=None):
        """Inicializa o serviço. Args: database: MongoDB database opcional. Se None, obtém do MongoDBConnection."""
        self._external_db = database

    def _get_db(self):
        if self._external_db is not None:
            return self._external_db
        if MONGODB_DISPONIVEL:
            return MongoDBConnection.get_database()
        return None

    def atualizar_perfil(
        self,
        cliente_id: int,
        preferencias: Optional[dict[str, Any]] = None,
        historico_contato: Optional[list] = None,
    ):
        """Atualiza ou cria o perfil de engajamento do cliente"""
        try:
            db = self._get_db()
            if db is None:
                return False

            perfil = {
                "cliente_id": cliente_id,
                "preferencias": preferencias or {},
                "historico_contato": historico_contato or [],
                "ultima_atualizacao": datetime.now(),
            }

            db["clientes_perfil"].update_one(
                {"cliente_id": cliente_id}, {"$set": perfil}, upsert=True
            )
            return True
        except Exception as e:
            print(f"Erro ao atualizar perfil: {e}")
            return False

    def adicionar_contato(
        self,
        cliente_id: int,
        tipo_contato_ou_dict: any,
        descricao: Optional[str] = None,
        metadados: Optional[dict[str, Any]] = None,
    ):
        """
        Adiciona registro de contato ao histórico do cliente

        Aceita dois formatos:
        1. adicionar_contato(cliente_id, dict_contato) - dict com todos os campos
        2. adicionar_contato(cliente_id, tipo, descricao, metadados) - campos separados
        """
        try:
            db = self._get_db()
            if db is None:
                return False

            # Se segundo parâmetro é dict, usa ele diretamente
            if isinstance(tipo_contato_ou_dict, dict):
                contato_dict = tipo_contato_ou_dict.copy()
                contato = {
                    "timestamp": datetime.now(),
                    "tipo": contato_dict.get("tipo", "OUTROS"),
                    "descricao": contato_dict.get("descricao", ""),
                }
                # Preserva 'assunto' e outros campos como estão
                for key in ["assunto", "data", "observacoes"]:
                    if key in contato_dict:
                        contato[key] = contato_dict[key]

                # Adiciona campos não-especiais em metadados
                metadados_extra = {
                    k: v
                    for k, v in contato_dict.items()
                    if k not in ["tipo", "assunto", "descricao", "data", "observacoes"]
                }
                if metadados_extra:
                    contato["metadados"] = metadados_extra
            else:
                # Formato antigo: parâmetros separados
                contato = {
                    "timestamp": datetime.now(),
                    "tipo": tipo_contato_ou_dict,
                    "descricao": descricao or "",
                    "metadados": metadados or {},
                }

            db["clientes_perfil"].update_one(
                {"cliente_id": cliente_id},
                {
                    "$push": {"historico_contato": contato},
                    "$set": {"ultima_atualizacao": datetime.now()},
                },
                upsert=True,
            )
            return True
        except Exception as e:
            print(f"Erro ao adicionar contato: {e}")
            return False

    def obter_perfil(self, cliente_id: int):
        """Obtém o perfil completo do cliente"""
        try:
            db = self._get_db()
            if db is None:
                return None

            perfil = db["clientes_perfil"].find_one({"cliente_id": cliente_id})
            if perfil:
                perfil["_id"] = str(perfil["_id"])
            return perfil
        except Exception as e:
            print(f"Erro ao obter perfil: {e}")
            return None

    # Métodos alias para compatibilidade com testes
    def criar_perfil(
        self,
        cliente_id: int,
        preferencias: Optional[dict[str, Any]] = None,
        historico_contato: Optional[list] = None,
    ):
        """Alias para atualizar_perfil (que faz upsert)"""
        return self.atualizar_perfil(cliente_id, preferencias, historico_contato)


class RelatorioMetadadosService:
    """Serviço para registrar metadados de relatórios exportados - Suporta injeção de dependência"""

    def __init__(self, database=None):
        """Inicializa o serviço. Args: database: MongoDB database opcional. Se None, obtém do MongoDBConnection."""
        self._external_db = database

    def _get_db(self):
        if self._external_db is not None:
            return self._external_db
        if MONGODB_DISPONIVEL:
            return MongoDBConnection.get_database()
        return None

    def registrar_exportacao(
        self,
        tipo_relatorio: str,
        formato: str,
        usuario: str,
        caminho_arquivo: Optional[str] = None,
        arquivo: Optional[str] = None,
        total_registros: Optional[int] = None,
        registros_total: Optional[int] = None,
        filtros: Optional[dict[str, Any]] = None,
    ):
        """
        Registra metadados de uma exportação de relatório

        Args:
            tipo_relatorio: Tipo do relatório exportado
            formato: Formato do arquivo (PDF, Excel, CSV, etc)
            usuario: Usuário que exportou
            caminho_arquivo: Caminho completo do arquivo (novo formato)
            arquivo: Nome do arquivo (formato antigo, para compatibilidade)
            total_registros: Total de registros no relatório (novo)
            registros_total: Total de registros (antigo, para compatibilidade)
            filtros: Filtros aplicados na exportação
        """
        try:
            db = self._get_db()
            if db is None:
                return None

            # Usa total_registros ou registros_total
            total = total_registros or registros_total or 0

            # Usa caminho_arquivo ou arquivo
            file_path = caminho_arquivo or arquivo or ""

            metadados = {
                "timestamp": datetime.now(),
                "usuario": usuario,
                "tipo_relatorio": tipo_relatorio,
                "formato": formato,
                "arquivo": file_path,
                "registros_total": total,
                "filtros": filtros or {},
            }

            resultado = db["relatorios_exportados"].insert_one(metadados)
            return str(resultado.inserted_id)
        except Exception as e:
            print(f"Erro ao registrar exportação: {e}")
            return None

    def buscar_por_tipo(self, tipo_relatorio: str):
        """Busca relatórios exportados por tipo"""
        try:
            db = self._get_db()
            if db is None:
                return []

            relatorios = list(
                db["relatorios_exportados"]
                .find({"tipo_relatorio": tipo_relatorio})
                .sort("timestamp", -1)
            )

            # Converte ObjectId para string
            for rel in relatorios:
                rel["_id"] = str(rel["_id"])

            return relatorios
        except Exception as e:
            print(f"Erro ao buscar relatórios por tipo: {e}")
            return []

    def listar_por_usuario(self, usuario: str):
        """Lista relatórios exportados por um usuário específico"""
        try:
            db = self._get_db()
            if db is None:
                return []

            relatorios = list(
                db["relatorios_exportados"].find({"usuario": usuario}).sort("timestamp", -1)
            )

            # Converte ObjectId para string
            for rel in relatorios:
                rel["_id"] = str(rel["_id"])

            return relatorios
        except Exception as e:
            print(f"Erro ao listar relatórios por usuário: {e}")
            return []


def _gravar_log_arquivo(log_documento: dict[str, Any]):
    """Grava log em arquivo como backup"""
    try:
        import os

        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
        os.makedirs(log_dir, exist_ok=True)

        log_file = os.path.join(log_dir, "auditoria.log")

        with open(log_file, "a", encoding="utf-8") as f:
            timestamp = log_documento["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            linha = f"{timestamp} | {log_documento['usuario']} | {log_documento['operacao']} | {log_documento['entidade']}"
            if log_documento.get("entidade_id"):
                linha += f" | ID: {log_documento['entidade_id']}"
            linha += f" | Status: {log_documento['status']}"
            if log_documento.get("detalhes"):
                linha += f" | Detalhes: {log_documento['detalhes']}"
            f.write(linha + "\n")
    except Exception as e:
        print(f"Erro ao gravar log em arquivo: {e}")
