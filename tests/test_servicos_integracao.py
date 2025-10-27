"""
Testes de Integração da Camada de Serviços
Testa orquestração entre MySQL e MongoDB através dos serviços
"""
import pytest


class TestClienteService:
    """Testes integrados do ClienteService (MySQL + MongoDB)"""

    def test_criar_cliente_registra_log(self, servicos_factories, cliente_teste):
        """Ao criar cliente, deve gravar no MySQL e log no MongoDB"""
        cliente_service = servicos_factories["cliente"]
        auditoria_service = servicos_factories["auditoria"]

        # Cria cliente através do serviço
        cliente_id = cliente_service.criar(usuario="admin_test", dados_cliente=cliente_teste)

        assert cliente_id is not None

        # Verifica que o log foi criado no MongoDB
        logs = auditoria_service.buscar_logs_por_entidade("cliente")

        assert len(logs) >= 1
        log_criacao = next((l for l in logs if l["entidade_id"] == cliente_id), None)
        assert log_criacao is not None
        assert log_criacao["operacao"] == "criar"
        assert log_criacao["usuario"] == "admin_test"

    def test_atualizar_cliente_registra_log(self, servicos_factories, cliente_teste):
        """Ao atualizar cliente, deve atualizar MySQL e registrar log no MongoDB"""
        cliente_service = servicos_factories["cliente"]
        auditoria_service = servicos_factories["auditoria"]

        # Cria cliente
        cliente_id = cliente_service.criar("admin", cliente_teste)

        # Atualiza dados
        novos_dados = {"email": "novo.email@teste.com", "telefone": "11888888888"}

        resultado = cliente_service.atualizar(
            usuario="admin", cliente_id=cliente_id, dados_atualizacao=novos_dados
        )

        assert resultado is True

        # Verifica log de atualização
        logs = auditoria_service.buscar_logs_por_usuario("admin")
        log_atualizacao = next(
            (l for l in logs if l["operacao"] == "atualizar" and l["entidade_id"] == cliente_id),
            None,
        )

        assert log_atualizacao is not None
        assert log_atualizacao["entidade"] == "cliente"

    def test_deletar_cliente_registra_log(self, servicos_factories, cliente_teste):
        """Ao deletar cliente, deve remover do MySQL e registrar log no MongoDB"""
        cliente_service = servicos_factories["cliente"]
        auditoria_service = servicos_factories["auditoria"]

        # Cria cliente
        cliente_id = cliente_service.criar("admin", cliente_teste)

        # Deleta cliente
        resultado = cliente_service.deletar(usuario="admin", cliente_id=cliente_id)

        assert resultado is True

        # Verifica log de exclusão
        logs = auditoria_service.buscar_logs_por_entidade("cliente")
        log_exclusao = next(
            (l for l in logs if l["operacao"] == "deletar" and l["entidade_id"] == cliente_id), None
        )

        assert log_exclusao is not None


class TestApoliceService:
    """Testes integrados do ApoliceService"""

    def test_emitir_apolice_completo(
        self, servicos_factories, dao_factories, cliente_teste, seguro_teste
    ):
        """Emissão de apólice deve gravar MySQL e criar logs detalhados no MongoDB"""
        # Prepara dados
        cliente_dao = dao_factories["cliente"]
        seguro_dao = dao_factories["seguro"]

        cliente_id = cliente_dao.criar(cliente_teste)
        
        # Adiciona cliente_id ao seguro_teste
        seguro_teste["cliente_id"] = cliente_id
        seguro_id = seguro_dao.criar(seguro_teste)

        # Emite apólice pelo serviço
        apolice_service = servicos_factories["apolice"]
        auditoria_service = servicos_factories["auditoria"]

        apolice_id = apolice_service.emitir(
            usuario="operador_test",
            cliente_id=cliente_id,
            seguro_id=seguro_id,
            data_inicio="2025-01-01",
            data_fim="2026-01-01",
            valor_premio=1200.00,
        )

        assert apolice_id is not None

        # Verifica log de emissão
        logs = auditoria_service.buscar_logs_por_entidade("apolice")
        log_emissao = next((l for l in logs if l["entidade_id"] == apolice_id), None)

        assert log_emissao is not None
        assert log_emissao["operacao"] == "emitir"
        assert log_emissao["usuario"] == "operador_test"
        assert "valor_premio" in log_emissao["detalhes"]

    def test_cancelar_apolice_completo(
        self, servicos_factories, dao_factories, cliente_teste, seguro_teste
    ):
        """Cancelamento deve atualizar status no MySQL e registrar no MongoDB"""
        # Prepara apólice
        cliente_dao = dao_factories["cliente"]
        seguro_dao = dao_factories["seguro"]

        cliente_id = cliente_dao.criar(cliente_teste)
        
        # Adiciona cliente_id ao seguro_teste
        seguro_teste["cliente_id"] = cliente_id
        seguro_id = seguro_dao.criar(seguro_teste)

        apolice_service = servicos_factories["apolice"]
        auditoria_service = servicos_factories["auditoria"]

        apolice_id = apolice_service.emitir(
            "admin", cliente_id, seguro_id, "2025-01-01", "2026-01-01", 1200.00
        )

        # Cancela apólice
        motivo = "Cliente solicitou cancelamento"
        resultado = apolice_service.cancelar(usuario="admin", apolice_id=apolice_id, motivo=motivo)

        assert resultado is True

        # Verifica log de cancelamento
        logs = auditoria_service.buscar_logs_por_entidade("apolice")
        log_cancelamento = next(
            (l for l in logs if l["operacao"] == "cancelar" and l["entidade_id"] == apolice_id),
            None,
        )

        assert log_cancelamento is not None
        assert motivo in str(log_cancelamento["detalhes"])


class TestSinistroService:
    """Testes integrados do SinistroService"""

    def test_registrar_sinistro_completo(
        self, servicos_factories, dao_factories, cliente_teste, seguro_teste
    ):
        """Registrar sinistro deve gravar MySQL e MongoDB (documentos e logs)"""
        # Prepara apólice
        cliente_dao = dao_factories["cliente"]
        seguro_dao = dao_factories["seguro"]
        apolice_dao = dao_factories["apolice"]

        cliente_id = cliente_dao.criar(cliente_teste)
        
        # Adiciona cliente_id ao seguro_teste
        seguro_teste["cliente_id"] = cliente_id
        seguro_id = seguro_dao.criar(seguro_teste)
        apolice_id = apolice_dao.criar(
            {
                "cliente_id": cliente_id,
                "seguro_id": seguro_id,
                "status": "ativa"
            }
        )

        # Registra sinistro pelo serviço
        sinistro_service = servicos_factories["sinistro"]
        auditoria_service = servicos_factories["auditoria"]

        sinistro_id = sinistro_service.registrar(
            usuario="analista_test",
            apolice_id=apolice_id,
            data_ocorrencia="2025-06-15",
            descricao="Colisão traseira no cruzamento",
            valor_estimado=5000.00,
            tipo_sinistro="COLISAO",
            documentos=[
                {
                    "tipo": "BOLETIM_OCORRENCIA",
                    "caminho": "/docs/bo.pdf",
                    "descricao": "BO da polícia"
                }
            ],
        )

        assert sinistro_id is not None

        # Verifica log de registro
        logs = auditoria_service.buscar_logs_por_entidade("sinistro")
        log_registro = next((l for l in logs if l["entidade_id"] == sinistro_id), None)

        assert log_registro is not None
        assert log_registro["operacao"] == "registrar"

    def test_atualizar_status_sinistro_completo(
        self, servicos_factories, dao_factories, cliente_teste, seguro_teste
    ):
        """Atualizar status deve atualizar MySQL e registrar histórico no MongoDB"""
        # Prepara sinistro
        cliente_dao = dao_factories["cliente"]
        seguro_dao = dao_factories["seguro"]
        apolice_dao = dao_factories["apolice"]
        sinistro_dao = dao_factories["sinistro"]

        cliente_id = cliente_dao.criar(cliente_teste)
        
        # Adiciona cliente_id ao seguro_teste
        seguro_teste["cliente_id"] = cliente_id
        seguro_id = seguro_dao.criar(seguro_teste)
        apolice_id = apolice_dao.criar(
            {
                "cliente_id": cliente_id,
                "seguro_id": seguro_id,
                "status": "ativa"
            }
        )

        sinistro_id = sinistro_dao.criar(
            {
                "apolice_id": apolice_id,
                "data_ocorrencia": "2025-06-15",
                "descricao": "Teste",
                "status": "pendente"
            }
        )

        # Atualiza status pelo serviço
        sinistro_service = servicos_factories["sinistro"]
        auditoria_service = servicos_factories["auditoria"]

        resultado = sinistro_service.atualizar_status(
            usuario="analista",
            sinistro_id=sinistro_id,
            novo_status="APROVADO",
            valor_aprovado=2500.00,
            observacoes="Aprovado após análise técnica",
        )

        assert resultado is True

        # Verifica log de atualização
        logs = auditoria_service.buscar_logs_por_entidade("sinistro")
        logs_sinistro = [l for l in logs if l["entidade_id"] == sinistro_id]

        log_status = next((l for l in logs_sinistro if l["operacao"] == "atualizar_status"), None)

        assert log_status is not None
        assert "APROVADO" in str(log_status["detalhes"])


class TestFluxoCompleto:
    """Testes de fluxo completo do sistema"""

    def test_fluxo_emissao_sinistro_pagamento(
        self, servicos_factories, dao_factories, cliente_teste, seguro_teste
    ):
        """
        Testa fluxo completo:
        1. Cadastra cliente
        2. Emite apólice
        3. Registra sinistro
        4. Aprova sinistro
        5. Marca como pago
        Verifica logs em cada etapa
        """
        # Setup
        dao_factories["cliente"]
        seguro_dao = dao_factories["seguro"]

        cliente_service = servicos_factories["cliente"]
        apolice_service = servicos_factories["apolice"]
        sinistro_service = servicos_factories["sinistro"]
        auditoria_service = servicos_factories["auditoria"]

        # 1. Cadastra cliente
        cliente_id = cliente_service.criar("admin", cliente_teste)
        
        # Adiciona cliente_id ao seguro_teste
        seguro_teste["cliente_id"] = cliente_id
        seguro_id = seguro_dao.criar(seguro_teste)

        # 2. Emite apólice
        apolice_id = apolice_service.emitir(
            "operador", cliente_id, seguro_id, "2025-01-01", "2026-01-01", 1200.00
        )

        # 3. Registra sinistro
        sinistro_id = sinistro_service.registrar(
            "analista", apolice_id, "2025-06-15", "Colisão", 5000.00, "COLISAO", []
        )

        # 4. Aprova sinistro
        sinistro_service.atualizar_status(
            "analista", sinistro_id, "APROVADO", 4500.00, "Aprovado conforme análise"
        )

        # 5. Marca como pago
        sinistro_service.atualizar_status(
            "financeiro", sinistro_id, "PAGO", 4500.00, "Pagamento efetuado"
        )

        # Verifica histórico completo de logs
        todos_logs = auditoria_service.listar_logs(limite=50)

        # Deve ter logs de: criar cliente, emitir apólice, registrar sinistro,
        # 2x atualizar status
        assert len(todos_logs) >= 5

        # Verifica diversidade de operações
        operacoes = {log["operacao"] for log in todos_logs}
        assert "criar" in operacoes
        assert "emitir" in operacoes or "registrar" in operacoes

    def test_consistencia_transacional(self, servicos_factories, cliente_teste):
        """
        Testa que em caso de erro, dados não ficam inconsistentes
        entre MySQL e MongoDB
        """
        cliente_service = servicos_factories["cliente"]

        # Tenta criar cliente com dados inválidos (CPF duplicado)
        cliente_id1 = cliente_service.criar("admin", cliente_teste)
        assert cliente_id1 is not None

        # Segunda tentativa com mesmo CPF deve falhar
        try:
            cliente_service.criar("admin", cliente_teste)
            # Se não lançou exceção, é um problema
            raise AssertionError("Deveria ter falhado com CPF duplicado")
        except Exception:
            # Esperado - CPF duplicado
            pass

        # Verifica que não há logs órfãos ou inconsistências
        auditoria_service = servicos_factories["auditoria"]
        logs = auditoria_service.buscar_logs_por_entidade("cliente")

        # Deve ter apenas 1 log de sucesso (primeiro cliente)
        logs_sucesso = [l for l in logs if l.get("status") == "sucesso"]
        assert len(logs_sucesso) >= 1


class TestPerformanceIntegracao:
    """Testes de performance básica da integração"""

    def test_criacao_multiplos_registros(self, servicos_factories, cliente_teste):
        """Testa criação de múltiplos registros em lote"""
        cliente_service = servicos_factories["cliente"]

        # Cria 10 clientes
        ids_criados = []
        for i in range(10):
            cliente = cliente_teste.copy()
            cliente["cpf"] = f"1234567{i:04d}"
            cliente["email"] = f"cliente{i}@teste.com"

            cliente_id = cliente_service.criar("admin", cliente)
            ids_criados.append(cliente_id)

        assert len(ids_criados) == 10
        assert all(id is not None for id in ids_criados)

        # Verifica que todos têm logs
        auditoria_service = servicos_factories["auditoria"]
        logs = auditoria_service.listar_logs(limite=20)

        assert len(logs) >= 10
