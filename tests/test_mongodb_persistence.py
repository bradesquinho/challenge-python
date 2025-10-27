"""
Testes de Persistência MongoDB
Testa inserção e consulta de documentos, logs e dados não estruturados
"""
from datetime import datetime

import pytest


class TestAuditoriaService:
    """Testes para logs de auditoria no MongoDB"""

    def test_registrar_log_auditoria(self, mongodb_db):
        """Deve registrar log de auditoria no MongoDB"""
        from functions.auditoria_service import AuditoriaService

        auditoria = AuditoriaService(mongodb_db)

        log_id = auditoria.registrar_log(
            usuario="admin_test",
            operacao="criar",
            entidade="cliente",
            entidade_id=1,
            detalhes={"nome": "João Silva", "cpf": "12345678901"},
            status="sucesso",
        )

        assert log_id is not None

    def test_listar_logs_auditoria(self, mongodb_db):
        """Deve listar logs de auditoria"""
        from functions.auditoria_service import AuditoriaService

        auditoria = AuditoriaService(mongodb_db)

        # Registra 3 logs
        for i in range(3):
            auditoria.registrar_log(
                usuario=f"user{i}",
                operacao="criar",
                entidade="cliente",
                entidade_id=i + 1,
                detalhes={"teste": f"log {i}"},
                status="sucesso",
            )

        logs = auditoria.listar_logs(limite=10)

        assert len(logs) >= 3
        assert all("usuario" in log for log in logs)
        assert all("operacao" in log for log in logs)

    def test_buscar_logs_por_usuario(self, mongodb_db):
        """Deve buscar logs de um usuário específico"""
        from functions.auditoria_service import AuditoriaService

        auditoria = AuditoriaService(mongodb_db)

        # Registra logs de diferentes usuários
        auditoria.registrar_log("admin1", "criar", "cliente", 1, {}, "sucesso")
        auditoria.registrar_log("admin1", "atualizar", "cliente", 1, {}, "sucesso")
        auditoria.registrar_log("admin2", "deletar", "cliente", 2, {}, "sucesso")

        logs_admin1 = auditoria.buscar_logs_por_usuario("admin1")

        assert len(logs_admin1) == 2
        assert all(log["usuario"] == "admin1" for log in logs_admin1)

    def test_buscar_logs_por_entidade(self, mongodb_db):
        """Deve buscar logs por tipo de entidade"""
        from functions.auditoria_service import AuditoriaService

        auditoria = AuditoriaService(mongodb_db)

        # Registra logs de diferentes entidades
        auditoria.registrar_log("admin", "criar", "cliente", 1, {}, "sucesso")
        auditoria.registrar_log("admin", "criar", "apolice", 1, {}, "sucesso")
        auditoria.registrar_log("admin", "criar", "apolice", 2, {}, "sucesso")

        logs_apolice = auditoria.buscar_logs_por_entidade("apolice")

        assert len(logs_apolice) == 2
        assert all(log["entidade"] == "apolice" for log in logs_apolice)

    def test_log_com_status_erro(self, mongodb_db):
        """Deve registrar log com status de erro"""
        from functions.auditoria_service import AuditoriaService

        auditoria = AuditoriaService(mongodb_db)

        log_id = auditoria.registrar_log(
            usuario="admin",
            operacao="criar",
            entidade="cliente",
            entidade_id=None,
            detalhes={"erro": "CPF já cadastrado"},
            status="erro",
        )

        assert log_id is not None

        logs = auditoria.listar_logs(limite=1)
        assert logs[0]["status"] == "erro"
        assert "erro" in logs[0]["detalhes"]


class TestSinistroDocumentos:
    """Testes para documentos de sinistros no MongoDB"""

    def test_adicionar_documento_sinistro(self, mongodb_db):
        """Deve adicionar documento anexo a sinistro"""
        from functions.auditoria_service import SinistroDocumentosService

        docs_service = SinistroDocumentosService(mongodb_db)

        doc_id = docs_service.adicionar_documento(
            sinistro_id=1,
            tipo_documento="BOLETIM_OCORRENCIA",
            caminho_arquivo="/docs/bo_12345.pdf",
            descricao="Boletim de ocorrência policial",
            metadados={
                "numero_bo": "12345/2025",
                "delegacia": "1ª DP",
                "data_registro": "2025-06-15",
            },
        )

        assert doc_id is not None

    def test_listar_documentos_sinistro(self, mongodb_db):
        """Deve listar todos os documentos de um sinistro"""
        from functions.auditoria_service import SinistroDocumentosService

        docs_service = SinistroDocumentosService(mongodb_db)

        # Adiciona 3 documentos ao mesmo sinistro
        tipos = ["BOLETIM_OCORRENCIA", "FOTOS", "ORCAMENTO"]
        for tipo in tipos:
            docs_service.adicionar_documento(
                sinistro_id=100,
                tipo_documento=tipo,
                caminho_arquivo=f"/docs/{tipo.lower()}.pdf",
                descricao=f"Documento {tipo}",
            )

        documentos = docs_service.listar_documentos_sinistro(100)

        assert len(documentos) == 3
        assert all(doc["sinistro_id"] == 100 for doc in documentos)

    def test_buscar_documento_por_tipo(self, mongodb_db):
        """Deve buscar documentos por tipo"""
        from functions.auditoria_service import SinistroDocumentosService

        docs_service = SinistroDocumentosService(mongodb_db)

        # Adiciona documentos
        docs_service.adicionar_documento(101, "FOTOS", "/docs/foto1.jpg", "Foto frontal")
        docs_service.adicionar_documento(101, "FOTOS", "/docs/foto2.jpg", "Foto lateral")
        docs_service.adicionar_documento(101, "ORCAMENTO", "/docs/orc.pdf", "Orçamento")

        fotos = docs_service.buscar_por_tipo(101, "FOTOS")

        assert len(fotos) == 2
        assert all(doc["tipo_documento"] == "FOTOS" for doc in fotos)

    def test_documento_com_metadados(self, mongodb_db):
        """Deve armazenar e recuperar metadados do documento"""
        from functions.auditoria_service import SinistroDocumentosService

        docs_service = SinistroDocumentosService(mongodb_db)

        metadados = {
            "tamanho_kb": 1500,
            "resolucao": "1920x1080",
            "formato": "JPEG",
            "timestamp": "2025-06-15T14:30:00",
        }

        docs_service.adicionar_documento(
            sinistro_id=102,
            tipo_documento="FOTOS",
            caminho_arquivo="/docs/foto.jpg",
            descricao="Foto do dano",
            metadados=metadados,
        )

        documentos = docs_service.listar_documentos_sinistro(102)

        assert len(documentos) == 1
        assert documentos[0]["metadados"]["resolucao"] == "1920x1080"
        assert documentos[0]["metadados"]["formato"] == "JPEG"


class TestClientePerfil:
    """Testes para perfis de clientes no MongoDB"""

    def test_criar_perfil_cliente(self, mongodb_db):
        """Deve criar perfil complementar do cliente"""
        from functions.auditoria_service import ClientePerfilService

        perfil_service = ClientePerfilService(mongodb_db)

        perfil_id = perfil_service.criar_perfil(
            cliente_id=1,
            preferencias={
                "canal_contato": "EMAIL",
                "horario_preferencial": "MANHA",
                "idioma": "PT-BR",
            },
            historico_contato=[
                {"data": "2025-01-15", "tipo": "TELEFONE", "assunto": "Dúvida sobre cobertura"}
            ],
        )

        assert perfil_id is not None

    def test_atualizar_perfil_cliente(self, mongodb_db):
        """Deve atualizar perfil do cliente"""
        from functions.auditoria_service import ClientePerfilService

        perfil_service = ClientePerfilService(mongodb_db)

        # Cria perfil
        perfil_service.criar_perfil(
            cliente_id=2, preferencias={"canal_contato": "EMAIL"}, historico_contato=[]
        )

        # Atualiza preferências
        resultado = perfil_service.atualizar_perfil(
            cliente_id=2, preferencias={"canal_contato": "WHATSAPP", "idioma": "PT-BR"}
        )

        assert resultado is True

        # Verifica atualização
        perfil = perfil_service.obter_perfil(2)
        assert perfil["preferencias"]["canal_contato"] == "WHATSAPP"

    def test_adicionar_historico_contato(self, mongodb_db):
        """Deve adicionar registro ao histórico de contato"""
        from functions.auditoria_service import ClientePerfilService

        perfil_service = ClientePerfilService(mongodb_db)

        # Cria perfil
        perfil_service.criar_perfil(cliente_id=3, preferencias={}, historico_contato=[])

        # Adiciona contato
        contato = {
            "data": "2025-06-20",
            "tipo": "EMAIL",
            "assunto": "Renovação de apólice",
            "observacoes": "Cliente solicitou desconto",
        }

        resultado = perfil_service.adicionar_contato(3, contato)
        assert resultado is True

        # Verifica histórico
        perfil = perfil_service.obter_perfil(3)
        assert len(perfil["historico_contato"]) == 1
        assert perfil["historico_contato"][0]["assunto"] == "Renovação de apólice"

    def test_obter_perfil_inexistente(self, mongodb_db):
        """Deve retornar None para perfil inexistente"""
        from functions.auditoria_service import ClientePerfilService

        perfil_service = ClientePerfilService(mongodb_db)

        perfil = perfil_service.obter_perfil(99999)

        assert perfil is None


class TestRelatorioMetadados:
    """Testes para metadados de relatórios exportados"""

    def test_registrar_exportacao_relatorio(self, mongodb_db):
        """Deve registrar metadados de relatório exportado"""
        from functions.auditoria_service import RelatorioMetadadosService

        relatorio_service = RelatorioMetadadosService(mongodb_db)

        relatorio_id = relatorio_service.registrar_exportacao(
            tipo_relatorio="SINISTROS_MES",
            formato="PDF",
            caminho_arquivo="/export/sinistros_jun2025.pdf",
            usuario="admin",
            filtros={"mes": 6, "ano": 2025, "status": "PAGO"},
            total_registros=45,
        )

        assert relatorio_id is not None

    def test_listar_relatorios_usuario(self, mongodb_db):
        """Deve listar relatórios gerados por usuário"""
        from functions.auditoria_service import RelatorioMetadadosService

        relatorio_service = RelatorioMetadadosService(mongodb_db)

        # Registra 3 relatórios do mesmo usuário
        for i in range(3):
            relatorio_service.registrar_exportacao(
                tipo_relatorio=f"RELATORIO_{i}",
                formato="PDF",
                caminho_arquivo=f"/export/rel_{i}.pdf",
                usuario="analista1",
                filtros={},
                total_registros=10,
            )

        relatorios = relatorio_service.listar_por_usuario("analista1")

        assert len(relatorios) == 3
        assert all(rel["usuario"] == "analista1" for rel in relatorios)

    def test_buscar_relatorio_por_tipo(self, mongodb_db):
        """Deve buscar relatórios por tipo"""
        from functions.auditoria_service import RelatorioMetadadosService

        relatorio_service = RelatorioMetadadosService(mongodb_db)

        # Registra relatórios de diferentes tipos
        relatorio_service.registrar_exportacao("CLIENTES", "PDF", "/r1.pdf", "admin", {}, 100)
        relatorio_service.registrar_exportacao("CLIENTES", "CSV", "/r2.csv", "admin", {}, 100)
        relatorio_service.registrar_exportacao("APOLICES", "PDF", "/r3.pdf", "admin", {}, 50)

        relatorios_clientes = relatorio_service.buscar_por_tipo("CLIENTES")

        assert len(relatorios_clientes) == 2
        assert all(rel["tipo_relatorio"] == "CLIENTES" for rel in relatorios_clientes)


class TestQueriesComplexas:
    """Testes para queries complexas no MongoDB"""

    def test_agregacao_logs_por_periodo(self, mongodb_db):
        """Deve agregar logs por período"""
        from functions.auditoria_service import AuditoriaService

        auditoria = AuditoriaService(mongodb_db)

        # Registra logs
        for i in range(5):
            auditoria.registrar_log(
                usuario="admin",
                operacao="criar" if i % 2 == 0 else "atualizar",
                entidade="cliente",
                entidade_id=i,
                detalhes={},
                status="sucesso",
            )

        # Busca por operação
        logs_criar = [log for log in auditoria.listar_logs(limite=10) if log["operacao"] == "criar"]

        assert len(logs_criar) >= 3

    def test_busca_documentos_com_filtro(self, mongodb_db):
        """Deve buscar documentos com filtros múltiplos"""
        from functions.auditoria_service import SinistroDocumentosService

        docs_service = SinistroDocumentosService(mongodb_db)

        # Adiciona documentos com diferentes metadados
        docs_service.adicionar_documento(
            200, "FOTOS", "/f1.jpg", "Foto 1", metadados={"tamanho_kb": 500, "aprovado": True}
        )
        docs_service.adicionar_documento(
            200, "FOTOS", "/f2.jpg", "Foto 2", metadados={"tamanho_kb": 1500, "aprovado": False}
        )
        docs_service.adicionar_documento(
            200,
            "ORCAMENTO",
            "/o1.pdf",
            "Orçamento",
            metadados={"tamanho_kb": 200, "aprovado": True},
        )

        # Busca todos os documentos do sinistro
        todos = docs_service.listar_documentos_sinistro(200)
        assert len(todos) == 3

        # Busca apenas fotos
        fotos = docs_service.buscar_por_tipo(200, "FOTOS")
        assert len(fotos) == 2
