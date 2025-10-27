"""
Camada de Serviço Híbrida - REFATORADA
Sprint 4 - Orquestra operações entre MySQL (dados principais) e MongoDB (logs/documentos)
Suporta injeção de dependência para testes isolados
"""
import os
import sys
from datetime import date, datetime
from typing import Any, Optional

# Adiciona o diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from functions.auditoria_service import (
    AuditoriaService,
    ClientePerfilService,
    SinistroDocumentosService,
)
from functions.dao_mysql import ApoliceDAO, ClienteDAO, SeguroDAO, SinistroDAO


def _serializar_para_mongo(obj):
    """Converte objetos Python para formatos compatíveis com MongoDB"""
    if isinstance(obj, dict):
        return {k: _serializar_para_mongo(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_serializar_para_mongo(item) for item in obj]
    elif isinstance(obj, (date, datetime)):
        return obj.isoformat() if hasattr(obj, "isoformat") else str(obj)
    else:
        return obj


class ClienteService:
    """Serviço para operações com clientes (MySQL + MongoDB) - Suporta injeção de dependência"""

    def __init__(self, mysql_connection=None, mongo_database=None):
        """Inicializa o serviço com DAOs e Services configurados"""
        self.cliente_dao = ClienteDAO(mysql_connection)
        self.auditoria = AuditoriaService(mongo_database)
        self.perfil = ClientePerfilService(mongo_database)

    def criar_cliente(self, dados: dict[str, Any], usuario: str) -> int:
        """Cria cliente no MySQL e registra log no MongoDB"""
        cliente_id = self.cliente_dao.criar(dados)

        if cliente_id:
            # Registra auditoria no MongoDB
            self.auditoria.registrar_log(
                usuario=usuario,
                operacao="criar",
                entidade="cliente",
                entidade_id=cliente_id,
                detalhes={"nome": dados["nome"], "cpf": dados["cpf"]},
                status="sucesso",
            )

            # Inicializa perfil do cliente no MongoDB
            self.perfil.atualizar_perfil(
                cliente_id=cliente_id, preferencias={}, historico_contato=[]
            )
        else:
            self.auditoria.registrar_log(
                usuario=usuario,
                operacao="criar",
                entidade="cliente",
                detalhes={"erro": "Falha ao criar cliente"},
                status="erro",
            )

        return cliente_id

    def criar(
        self, usuario: str, dados: Optional[dict[str, Any]] = None, dados_cliente: Optional[dict[str, Any]] = None
    ) -> int:
        """Alias para criar_cliente - compatibilidade com testes

        Aceita tanto criar(usuario, dados) quanto criar(usuario=x, dados_cliente=y)
        """
        dados_finais = dados_cliente if dados_cliente is not None else dados
        return self.criar_cliente(dados_finais, usuario)

    def atualizar_cliente(self, cliente_id: int, dados: dict[str, Any], usuario: str) -> bool:
        """Atualiza cliente no MySQL e registra log no MongoDB"""
        sucesso = self.cliente_dao.atualizar(cliente_id, dados)

        self.auditoria.registrar_log(
            usuario=usuario,
            operacao="atualizar",
            entidade="cliente",
            entidade_id=cliente_id,
            detalhes={"campos_alterados": list(dados.keys())},
            status="sucesso" if sucesso else "erro",
        )

        if sucesso:
            # Atualiza última modificação no perfil
            self.perfil.atualizar_perfil(cliente_id=cliente_id)

        return sucesso

    def atualizar(self, usuario: str, cliente_id: int, dados_atualizacao: dict[str, Any]) -> bool:
        """Alias para atualizar_cliente - compatibilidade com testes"""
        return self.atualizar_cliente(cliente_id, dados_atualizacao, usuario)

    def deletar_cliente(self, cliente_id: int, usuario: str) -> bool:
        """Deleta cliente do MySQL e registra log no MongoDB"""
        # Busca dados antes de deletar para o log
        cliente = self.cliente_dao.ler_por_id(cliente_id)
        sucesso = self.cliente_dao.deletar(cliente_id)

        # Serializa cliente para MongoDB (converte dates para strings)
        cliente_serializado = _serializar_para_mongo(cliente) if cliente else {}

        self.auditoria.registrar_log(
            usuario=usuario,
            operacao="deletar",
            entidade="cliente",
            entidade_id=cliente_id,
            detalhes={"cliente_deletado": cliente_serializado},
            status="sucesso" if sucesso else "erro",
        )

        return sucesso

    def deletar(self, usuario: str, cliente_id: int) -> bool:
        """Alias para deletar_cliente - compatibilidade com testes"""
        return self.deletar_cliente(cliente_id, usuario)

    def buscar_cliente(self, cliente_id: int, usuario: str) -> Optional[dict[str, Any]]:
        """Busca cliente e registra consulta"""
        cliente = self.cliente_dao.ler_por_id(cliente_id)

        # Registra consulta (pode ser útil para análise de comportamento)
        if cliente:
            self.auditoria.registrar_log(
                usuario=usuario,
                operacao="consultar",
                entidade="cliente",
                entidade_id=cliente_id,
                status="sucesso",
            )

        return cliente

    def listar_clientes(self, usuario: str) -> list[dict[str, Any]]:
        """Lista todos os clientes"""
        clientes = self.cliente_dao.listar()

        self.auditoria.registrar_log(
            usuario=usuario,
            operacao="listar",
            entidade="cliente",
            detalhes={"total": len(clientes)},
            status="sucesso",
        )

        return clientes


class ApoliceService:
    """Serviço para operações com apólices (MySQL + MongoDB) - Suporta injeção de dependência"""

    def __init__(self, mysql_connection=None, mongo_database=None):
        """Inicializa o serviço com DAOs e Services configurados"""
        self.apolice_dao = ApoliceDAO(mysql_connection)
        self.cliente_dao = ClienteDAO(mysql_connection)
        self.seguro_dao = SeguroDAO(mysql_connection)
        self.auditoria = AuditoriaService(mongo_database)
        self.perfil = ClientePerfilService(mongo_database)

    def emitir_apolice(self, dados: dict[str, Any], usuario: str) -> int:
        """Emite apólice no MySQL e registra log detalhado no MongoDB"""
        # Define data de emissão se não fornecida
        if "data_emissao" not in dados:
            dados["data_emissao"] = datetime.now().date()

        if "status" not in dados:
            dados["status"] = "ativa"

        apolice_id = self.apolice_dao.criar(dados)

        if apolice_id:
            # Busca dados completos para log detalhado
            cliente = self.cliente_dao.ler_por_id(dados["cliente_id"])
            seguro = self.seguro_dao.ler_por_id(dados["seguro_id"])

            self.auditoria.registrar_log(
                usuario=usuario,
                operacao="emitir",
                entidade="apolice",
                entidade_id=apolice_id,
                detalhes={
                    "cliente_nome": cliente["nome"] if cliente else "Desconhecido",
                    "cliente_cpf": cliente["cpf"] if cliente else "Desconhecido",
                    "seguro_tipo": seguro["tipo"] if seguro else "Desconhecido",
                    "data_emissao": str(dados["data_emissao"]),
                    "valor_premio": dados.get("valor_premio"),
                    "data_inicio": str(dados.get("data_inicio", "")),
                    "data_fim": str(dados.get("data_fim", "")),
                },
                status="sucesso",
            )

            # Registra no histórico de contato do cliente
            if cliente:
                self.perfil.adicionar_contato(
                    dados["cliente_id"],
                    "emissao_apolice",
                    f"Apólice {apolice_id} emitida",
                    {"apolice_id": apolice_id, "seguro_tipo": seguro["tipo"] if seguro else None},
                )
        else:
            self.auditoria.registrar_log(
                usuario=usuario,
                operacao="emitir",
                entidade="apolice",
                detalhes={"erro": "Falha ao emitir apólice"},
                status="erro",
            )

        return apolice_id

    def emitir(
        self,
        usuario: str,
        cliente_id: int,
        seguro_id: int,
        data_inicio: str,
        data_fim: str,
        valor_premio: float,
    ) -> int:
        """Alias para emitir_apolice - compatibilidade com testes"""
        dados = {
            "cliente_id": cliente_id,
            "seguro_id": seguro_id,
            "numero": f"AP{datetime.now().year}{cliente_id:04d}",
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "data_emissao": datetime.now().date(),
            "valor_premio": valor_premio,
            "status": "ativa",
        }
        return self.emitir_apolice(dados, usuario)

    def cancelar_apolice(self, apolice_id: int, usuario: str, motivo: Optional[str] = None) -> bool:
        """Cancela apólice e registra log detalhado"""
        apolice = self.apolice_dao.ler_por_id(apolice_id)

        if not apolice:
            return False

        # Atualiza status para cancelada
        dados_atualizados = apolice.copy()
        dados_atualizados["status"] = "cancelada"

        sucesso = self.apolice_dao.atualizar(apolice_id, dados_atualizados)

        if sucesso:
            self.auditoria.registrar_log(
                usuario=usuario,
                operacao="cancelar",
                entidade="apolice",
                entidade_id=apolice_id,
                detalhes={
                    "motivo": motivo or "Não informado",
                    "data_cancelamento": str(datetime.now()),
                },
                status="sucesso",
            )

            # Registra no histórico do cliente
            self.perfil.adicionar_contato(
                apolice["cliente_id"],
                "cancelamento_apolice",
                f"Apólice {apolice_id} cancelada",
                {"apolice_id": apolice_id, "motivo": motivo},
            )

        return sucesso

    def cancelar(self, usuario: str, apolice_id: int, motivo: Optional[str] = None) -> bool:
        """Alias para cancelar_apolice - compatibilidade com testes"""
        return self.cancelar_apolice(apolice_id, usuario, motivo)

    def listar_apolices(self, usuario: str) -> list[dict[str, Any]]:
        """Lista todas as apólices"""
        apolices = self.apolice_dao.listar()

        self.auditoria.registrar_log(
            usuario=usuario,
            operacao="listar",
            entidade="apolice",
            detalhes={"total": len(apolices)},
            status="sucesso",
        )

        return apolices


class SinistroService:
    """Serviço para operações com sinistros (MySQL + MongoDB) - Suporta injeção de dependência"""

    def __init__(self, mysql_connection=None, mongo_database=None):
        """Inicializa o serviço com DAOs e Services configurados"""
        self.sinistro_dao = SinistroDAO(mysql_connection)
        self.apolice_dao = ApoliceDAO(mysql_connection)
        self.auditoria = AuditoriaService(mongo_database)
        self.documentos = SinistroDocumentosService(mongo_database)
        self.perfil = ClientePerfilService(mongo_database)

    def registrar_sinistro(
        self, dados: dict[str, Any], usuario: str, observacoes: Optional[str] = None
    ) -> int:
        """Registra sinistro no MySQL e documentos no MongoDB"""
        if "data_ocorrencia" not in dados:
            dados["data_ocorrencia"] = datetime.now().date()

        if "status" not in dados:
            dados["status"] = "aberto"

        sinistro_id = self.sinistro_dao.criar(dados)

        if sinistro_id:
            # Busca dados da apólice para log detalhado
            apolice = self.apolice_dao.ler_por_id(dados["apolice_id"])

            self.auditoria.registrar_log(
                usuario=usuario,
                operacao="registrar",
                entidade="sinistro",
                entidade_id=sinistro_id,
                detalhes={
                    "apolice_id": dados["apolice_id"],
                    "descricao_resumida": dados.get("descricao", "")[:100],
                    "data_ocorrencia": str(dados["data_ocorrencia"]),
                },
                status="sucesso",
            )

            # Adiciona documentos/observações detalhadas no MongoDB
            if observacoes:
                self.documentos.adicionar_documento(
                    sinistro_id=sinistro_id,
                    apolice_id=dados["apolice_id"],
                    tipo_documento="observacao_inicial",
                    conteudo=observacoes,
                    metadados={"registrado_por": usuario, "data_registro": str(datetime.now())},
                )

            # Registra no histórico do cliente
            if apolice:
                self.perfil.adicionar_contato(
                    apolice["cliente_id"],
                    "registro_sinistro",
                    f"Sinistro {sinistro_id} registrado",
                    {"sinistro_id": sinistro_id, "apolice_id": dados["apolice_id"]},
                )
        else:
            self.auditoria.registrar_log(
                usuario=usuario,
                operacao="registrar",
                entidade="sinistro",
                detalhes={"erro": "Falha ao registrar sinistro"},
                status="erro",
            )

        return sinistro_id

    def registrar(
        self,
        usuario: str,
        apolice_id: int,
        data_ocorrencia: str,
        descricao: str,
        valor_estimado: float,
        tipo_sinistro: str,
        documentos: Optional[list[dict[str, Any]]] = None,
    ) -> int:
        """Alias para registrar_sinistro - compatibilidade com testes"""
        dados = {
            "apolice_id": apolice_id,
            "data_ocorrencia": data_ocorrencia,
            "descricao": descricao,
            "valor_estimado": valor_estimado,
            "tipo_sinistro": tipo_sinistro,
            "status": "aberto",
        }

        sinistro_id = self.registrar_sinistro(dados, usuario)

        # Adiciona documentos se fornecidos
        if documentos and sinistro_id:
            for doc in documentos:
                self.documentos.adicionar_documento(
                    sinistro_id=sinistro_id,
                    tipo_documento=doc.get("tipo", "OUTROS"),
                    caminho_arquivo=doc.get("caminho", ""),
                    descricao=doc.get("descricao", ""),
                    metadados={"registrado_por": usuario},
                )

        return sinistro_id

    def atualizar_sinistro(
        self,
        sinistro_id: int,
        dados: dict[str, Any],
        usuario: str,
        observacoes: Optional[str] = None,
        operacao: str = "atualizar_sinistro",
    ) -> bool:
        """Atualiza sinistro e adiciona observações no MongoDB"""
        sucesso = self.sinistro_dao.atualizar(sinistro_id, dados)

        if sucesso:
            self.auditoria.registrar_log(
                usuario=usuario,
                operacao=operacao,
                entidade="sinistro",
                entidade_id=sinistro_id,
                detalhes={
                    "campos_alterados": list(dados.keys()),
                    "novo_status": dados.get("status"),
                    "valor_aprovado": dados.get("valor_aprovado"),
                    "observacoes": observacoes,
                },
                status="sucesso",
            )

            # Adiciona observações da atualização no MongoDB
            if observacoes:
                self.documentos.adicionar_documento(
                    sinistro_id=sinistro_id,
                    apolice_id=dados["apolice_id"],
                    tipo_documento="observacao_atualizacao",
                    conteudo=observacoes,
                    metadados={
                        "atualizado_por": usuario,
                        "data_atualizacao": str(datetime.now()),
                        "status_anterior": dados.get("status_anterior"),
                        "status_novo": dados.get("status"),
                    },
                )

        return sucesso

    def atualizar_status(
        self,
        usuario: str,
        sinistro_id: int,
        novo_status: str,
        valor_aprovado: Optional[float] = None,
        observacoes: Optional[str] = None,
    ) -> bool:
        """Alias para atualizar status do sinistro - compatibilidade com testes"""
        # Busca sinistro para ter os dados completos
        sinistro = self.sinistro_dao.ler_por_id(sinistro_id)
        if not sinistro:
            return False

        # Atualiza status e valor_aprovado se fornecido
        dados = {"status": novo_status}
        if valor_aprovado is not None:
            dados["valor_aprovado"] = valor_aprovado
        if sinistro.get("apolice_id"):
            dados["apolice_id"] = sinistro["apolice_id"]  # Necessário para registro de documento

        return self.atualizar_sinistro(
            sinistro_id, dados, usuario, observacoes, operacao="atualizar_status"
        )

    def listar_sinistros(self, usuario: str) -> list[dict[str, Any]]:
        """Lista todos os sinistros"""
        sinistros = self.sinistro_dao.listar()

        self.auditoria.registrar_log(
            usuario=usuario,
            operacao="listar",
            entidade="sinistro",
            detalhes={"total": len(sinistros)},
            status="sucesso",
        )

        return sinistros

    def obter_documentos_sinistro(self, sinistro_id: int) -> list[dict[str, Any]]:
        """Obtém todos os documentos/observações de um sinistro do MongoDB"""
        return self.documentos.listar_documentos(sinistro_id)


class SeguroService:
    """Serviço para operações com seguros (MySQL + MongoDB) - Suporta injeção de dependência"""

    def __init__(self, mysql_connection=None, mongo_database=None):
        """Inicializa o serviço com DAOs e Services configurados"""
        self.seguro_dao = SeguroDAO(mysql_connection)
        self.auditoria = AuditoriaService(mongo_database)

    def criar_seguro(self, dados: dict[str, Any], usuario: str) -> int:
        """Cria seguro no MySQL e registra log no MongoDB"""
        seguro_id = self.seguro_dao.criar(dados)

        if seguro_id:
            self.auditoria.registrar_log(
                usuario=usuario,
                operacao="criar",
                entidade="seguro",
                entidade_id=seguro_id,
                detalhes={"tipo": dados["tipo"], "cliente_id": dados["cliente_id"]},
                status="sucesso",
            )
        else:
            self.auditoria.registrar_log(
                usuario=usuario,
                operacao="criar",
                entidade="seguro",
                detalhes={"erro": "Falha ao criar seguro"},
                status="erro",
            )

        return seguro_id

    def listar_seguros(self, usuario: str) -> list[dict[str, Any]]:
        """Lista todos os seguros"""
        seguros = self.seguro_dao.listar()

        self.auditoria.registrar_log(
            usuario=usuario,
            operacao="listar",
            entidade="seguro",
            detalhes={"total": len(seguros)},
            status="sucesso",
        )

        return seguros
