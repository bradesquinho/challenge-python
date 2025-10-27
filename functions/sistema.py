from datetime import datetime

# Sprint 4 - Persistência Híbrida (MySQL + MongoDB)
from functions.dao_mysql import ApoliceDAO, ClienteDAO, SeguroDAO, SinistroDAO, UsuarioDAO
from functions.exceptions import (
    ApoliceInexistente,
    ClienteInexistente,
    CpfInvalido,
    DadosInvalidos,
    OperacaoNaoPermitida,
    PermissaoNegada,
    SinistroInexistente,
    ValorInvalido,
)
from functions.exporta_relatorios import (
    receita_mensal_prevista_cli_export,
    sinistros_status_periodo_cli_export,
    top_clientes_valor_segurado_cli_export,
)
from functions.logger import registrar_log
from functions.seguro import Automovel, Residencial, Vida
from functions.servicos import ApoliceService, ClienteService, SeguroService, SinistroService
from utils.utils import validar_cpf, validar_placa


class SistemaSeguros:
    def __init__(self, mysql_connection=None, mongo_database=None):
        """
        Inicializa o sistema, carregando dados do banco MySQL via DAOs.
        Sprint 4 - Persistência Híbrida (MySQL + MongoDB)
        
        Args:
            mysql_connection: Conexão MySQL opcional (para testes)
            mongo_database: Database MongoDB opcional (para testes)
        """
        # Instanciar DAOs (com conexões padrão None = usará a conexão padrão)
        self.cliente_dao = ClienteDAO(mysql_connection)
        self.seguro_dao = SeguroDAO(mysql_connection)
        self.apolice_dao = ApoliceDAO(mysql_connection)
        self.sinistro_dao = SinistroDAO(mysql_connection)
        self.usuario_dao = UsuarioDAO(mysql_connection)

        # Carregar dados do banco MySQL
        self.clientes = self.cliente_dao.listar()
        self.seguros = self.seguro_dao.listar()
        self.apolices = self.apolice_dao.listar()
        self.sinistros = self.sinistro_dao.listar()
        self.usuario_atual = None
        self.tipo_usuario = None

        # Instanciar Services (para operações que envolvem MySQL + MongoDB)
        self.cliente_service = ClienteService(mysql_connection, mongo_database)
        self.seguro_service = SeguroService(mysql_connection, mongo_database)
        self.apolice_service = ApoliceService(mysql_connection, mongo_database)
        self.sinistro_service = SinistroService(mysql_connection, mongo_database)

        # Cria usuário admin padrão se não existir
        if not self.usuario_dao.listar():
            self.usuario_dao.criar({"username": "admin", "senha": "senha123", "tipo": "admin"})

    def atualizar_status_sinistro(self):
        """
        Permite atualizar o status de um sinistro (ex: de 'aberto' para 'fechado').
        Sprint 4 - Usa SinistroService para gravar observações no MongoDB.
        """
        print("=== Atualizar Status de Sinistro ===")
        try:
            sinistro_id = input("ID do sinistro a atualizar: ").strip()
            sinistro = self.sinistro_dao.ler_por_id(int(sinistro_id))
            if not sinistro:
                raise SinistroInexistente("Sinistro não encontrado.")

            print(f"Status atual: {sinistro['status']}")
            novo_status = input("Novo status (aberto/fechado): ").strip().lower()
            if novo_status not in ["aberto", "fechado"]:
                raise OperacaoNaoPermitida("Status inválido. Use 'aberto' ou 'fechado'.")

            if sinistro["status"] != novo_status:
                print(
                    f"Tem certeza que deseja alterar o status do sinistro {sinistro_id} para '{novo_status}'?"
                )
                confirm = input("Digite 'CONFIRMAR' para prosseguir: ").strip()
                if confirm != "CONFIRMAR":
                    print("Operação abortada pelo usuário.")
                    return

            observacoes = input("Observações sobre a atualização (opcional): ").strip()

            # Prepara dados para atualização
            dados_atualizados = sinistro.copy()
            dados_atualizados["status"] = novo_status
            dados_atualizados["status_anterior"] = sinistro["status"]

            # Usa SinistroService (grava no MySQL + observações no MongoDB)
            sucesso = self.sinistro_service.atualizar_sinistro(
                int(sinistro_id), dados_atualizados, self.usuario_atual, observacoes or None
            )

            if sucesso:
                self.sinistros = self.sinistro_dao.listar()
                print("Status do sinistro atualizado com sucesso!")
                registrar_log(
                    "INFO", self.usuario_atual, "atualizar_status_sinistro", id_obj=sinistro_id
                )
            else:
                print("Erro ao atualizar sinistro.")
        except (SinistroInexistente, OperacaoNaoPermitida) as e:
            print(f"[ERRO] {e}")

    def cancelar_apolice(self):
        """
        Permite cancelar uma apólice existente, alterando seu status para 'cancelada'.
        Sprint 4 - Usa ApoliceService para gravar logs detalhados no MongoDB.
        """
        print("=== Cancelar Apólice ===")
        try:
            apolice_id = input("ID da apólice a cancelar: ").strip()
            apolice = self.apolice_dao.ler_por_id(int(apolice_id))
            if not apolice:
                raise ApoliceInexistente("Apólice não encontrada.")
            if apolice.get("status", "").lower() == "cancelada":
                raise OperacaoNaoPermitida("Esta apólice já está cancelada.")

            print(
                f"Tem certeza que deseja cancelar a apólice {apolice_id}? Esta ação não pode ser desfeita."
            )
            confirm = input("Digite 'CONFIRMAR' para cancelar: ").strip()
            if confirm != "CONFIRMAR":
                print("Cancelamento abortado pelo usuário.")
                return

            motivo = input("Motivo do cancelamento (opcional): ").strip()

            # Usa ApoliceService (grava no MySQL + log detalhado no MongoDB)
            sucesso = self.apolice_service.cancelar_apolice(
                int(apolice_id), self.usuario_atual, motivo or None
            )

            if sucesso:
                self.apolices = self.apolice_dao.listar()
                print("Apólice cancelada com sucesso!")
                registrar_log("INFO", self.usuario_atual, "cancelar_apolice", id_obj=apolice_id)
            else:
                print("Erro ao cancelar apólice.")
        except (ApoliceInexistente, OperacaoNaoPermitida) as e:
            print(f"[ERRO] {e}")

    def alterar_dados_cliente(self):
        """
        Permite alterar os dados de um cliente já cadastrado.
        Sprint 4 - Usa ClienteService para gravar logs no MongoDB.
        """
        print("=== Alterar Dados do Cliente ===")
        try:
            cliente_id = input("ID do cliente a alterar: ").strip()
            cliente = self.cliente_dao.ler_por_id(int(cliente_id))
            if not cliente:
                raise OperacaoNaoPermitida("Cliente não encontrado.")

            print(
                f"Dados atuais: Nome: {cliente['nome']}, CPF: {cliente['cpf']}, Telefone: {cliente.get('telefone','')}, Email: {cliente.get('email','')}, Data Nasc: {cliente['data_nasc']}, Endereço: {cliente['endereco']}"
            )
            nome = input(f"Novo nome [{cliente['nome']}]: ").strip() or cliente["nome"]
            cpf = input(f"Novo CPF [{cliente['cpf']}]: ").strip() or cliente["cpf"]
            telefone = input(
                f"Novo telefone [{cliente.get('telefone','')}]: "
            ).strip() or cliente.get("telefone", "")
            email = input(f"Novo email [{cliente.get('email','')}]: ").strip() or cliente.get(
                "email", ""
            )
            data_nasc = (
                input(f"Nova data de nascimento [{cliente['data_nasc']}]: ").strip()
                or cliente["data_nasc"]
            )
            endereco = (
                input(f"Novo endereço [{cliente['endereco']}]: ").strip() or cliente["endereco"]
            )

            print(
                f"Tem certeza que deseja alterar os dados do cliente {cliente_id} ({cliente['nome']})?"
            )
            confirm = input("Digite 'CONFIRMAR' para prosseguir: ").strip()
            if confirm != "CONFIRMAR":
                print("Operação abortada pelo usuário.")
                return

            novos_dados = {
                "nome": nome,
                "cpf": cpf,
                "telefone": telefone,
                "email": email,
                "data_nasc": data_nasc,
                "endereco": endereco,
            }

            # Usa ClienteService (grava no MySQL + log no MongoDB)
            sucesso = self.cliente_service.atualizar_cliente(
                int(cliente_id), novos_dados, self.usuario_atual
            )

            if sucesso:
                self.clientes = self.cliente_dao.listar()
                print("Dados do cliente atualizados com sucesso!")
                registrar_log(
                    "INFO", self.usuario_atual, "alterar_dados_cliente", id_obj=cliente_id
                )
            else:
                print("Erro ao atualizar cliente.")
        except OperacaoNaoPermitida as e:
            print(f"[ERRO] {e}")

    def cadastrar_cliente(self):
        """
        Cadastra um novo cliente e persiste no MySQL via ClienteService.
        Sprint 4 - Logs gravados automaticamente no MongoDB.
        """
        print("=== Cadastro de Cliente ===")
        try:
            while True:
                nome = input("Nome: ").strip()
                if not nome:
                    print("Nome não pode ser vazio.")
                    continue
                break
            while True:
                cpf = input("CPF: ").strip()
                if not validar_cpf(cpf):
                    raise CpfInvalido("CPF inválido. Tente novamente.")
                if any(c["cpf"] == cpf for c in self.cliente_dao.listar()):
                    raise OperacaoNaoPermitida("Já existe um cliente com esse CPF.")
                break
            telefone = input("Telefone: ").strip()
            email = input("Email: ").strip()
            endereco = input("Endereço: ").strip()
            data_nasc_str = input("Data de nascimento (DD/MM/AAAA): ").strip()
            try:
                data_nasc = datetime.strptime(data_nasc_str, "%d/%m/%Y")
            except ValueError:
                raise OperacaoNaoPermitida("Data de nascimento inválida.")

            cliente_dados = {
                "nome": nome,
                "cpf": cpf,
                "telefone": telefone,
                "email": email,
                "endereco": endereco,
                "data_nasc": data_nasc.strftime("%Y-%m-%d"),  # Formato MySQL
            }

            # Usa ClienteService (grava no MySQL + log no MongoDB)
            cliente_id = self.cliente_service.criar_cliente(cliente_dados, self.usuario_atual)

            if cliente_id:
                self.clientes = self.cliente_dao.listar()
                print(f"Cliente cadastrado com sucesso! ID: {cliente_id}")
                registrar_log("INFO", self.usuario_atual, "cadastrar_cliente", id_obj=cliente_id)
            else:
                print("Erro ao cadastrar cliente.")
        except (CpfInvalido, OperacaoNaoPermitida) as e:
            print(f"[ERRO] {e}")

    def autenticar_usuario(self):
        """
        Realiza autenticação do usuário, permitindo login ou cadastro.
        Sprint 4 - Utiliza dados do MySQL.
        """
        print("Você já possui usuário e senha? (s/n)")
        while True:
            possui = input().strip().lower()
            if possui == "s":
                return self.login()
            elif possui == "n":
                return self.cadastrar_usuario_e_login()
            else:
                print("Resposta inválida. Digite 's' para sim ou 'n' para não.")

    def cadastrar_usuario_e_login(self):
        """
        Cadastra um novo usuário e realiza o login.
        """
        print("=== Cadastro de novo usuário ===")
        while True:
            usuario = input("Digite o nome de usuário desejado: ").strip()
            if not usuario:
                print("Usuário não pode ser vazio.")
                continue
            if self.usuario_dao.ler_por_username(usuario):
                print("Usuário já existe. Tente outro.")
                continue
            senha = input("Digite a senha: ").strip()
            if not senha:
                print("Senha não pode ser vazia.")
                continue
            tipo = input("Tipo de usuário (admin/comum): ").strip().lower()
            if tipo not in ["admin", "comum"]:
                print("Tipo inválido.")
                continue
            self.usuario_dao.criar({"username": usuario, "senha": senha, "tipo": tipo})
            print("Usuário cadastrado com sucesso! Faça login agora.")
            return self.login()

    def login(self):
        while True:
            print("=== Login ===")
            usuario = input("Usuário: ").strip()
            senha = input("Senha: ").strip()
            user = self.usuario_dao.ler_por_username(usuario)
            if user and user["senha"] == senha:
                self.usuario_atual = usuario
                self.tipo_usuario = user["tipo"]
                print(f"Login bem-sucedido! Tipo de usuário: {self.tipo_usuario}")
                return True
            else:
                print("Usuário ou senha inválidos. Tente novamente.")

    def cadastrar_seguro(self, cliente=None):
        """
        Cadastra um novo seguro (Automóvel, Residencial ou Vida) e persiste no MySQL via SeguroDAO.
        Se cliente for fornecido, pode usar dados do cliente.
        Sprint 4 - Persistência híbrida (MySQL + MongoDB).
        """
        try:
            print("=== Cadastro de Seguro ===")
            if not cliente:
                cliente_id = input("ID do cliente: ").strip()
                cliente = self.cliente_dao.ler_por_id(int(cliente_id))
                if not cliente:
                    raise ClienteInexistente("Cliente não encontrado.")
            data_nasc = cliente.get("data_nasc")
            if not data_nasc:
                raise DadosInvalidos(
                    "O cliente não possui data de nascimento cadastrada. Verifique os dados do cliente."
                )
            try:
                # Tenta converter data_nasc para datetime
                # Pode vir como string "YYYY-MM-DD" do MySQL ou como date object
                if isinstance(data_nasc, str):
                    # Tenta formato MySQL primeiro (YYYY-MM-DD)
                    try:
                        data_nasc_obj = datetime.strptime(data_nasc, "%Y-%m-%d")
                    except ValueError:
                        # Tenta formato brasileiro (DD/MM/YYYY)
                        data_nasc_obj = datetime.strptime(data_nasc, "%d/%m/%Y")
                else:
                    # Já é um objeto date/datetime
                    data_nasc_obj = datetime.combine(data_nasc, datetime.min.time())
                
                idade_cliente = (datetime.now() - data_nasc_obj).days // 365
            except Exception:
                raise DadosInvalidos(
                    f"Data de nascimento inconsistente para o cliente (ID {cliente.get('id')}): '{data_nasc}'. Corrija o cadastro do cliente."
                )
            tipo = None
            while True:
                tipo_input = (
                    input("Tipo de Seguro (Automóvel, Residencial, Vida): ").strip().capitalize()
                )
                if tipo_input in ["Automóvel", "Residencial", "Vida"]:
                    tipo = tipo_input
                    break
                else:
                    print("Tipo de seguro inválido. Escolha Automóvel, Residencial ou Vida.")
            if tipo == "Automóvel" and idade_cliente < 18:
                raise PermissaoNegada(
                    "É necessário ser maior de idade para contratar um seguro de automóvel."
                )
            if tipo == "Vida" and idade_cliente < 18:
                print(
                    "Menores de 18 anos podem contratar seguro de vida apenas com a assistência de um responsável."
                )
                responsavel = input("O responsável está presente? (s/n): ").strip().lower()
                if responsavel != "s":
                    raise PermissaoNegada(
                        "Cadastro de seguro de vida não permitido sem responsável."
                    )
            dados = {}
            if tipo == "Residencial":
                usar_endereco_cliente = input("Usar o endereço do cliente? (s/n): ").strip().lower()
                if usar_endereco_cliente == "s":
                    endereco = cliente.get("endereco")
                    if not endereco:
                        while True:
                            endereco = input("Endereço: ").strip()
                            if endereco:
                                break
                            print("Endereço é obrigatório. Por favor, preencha.")
                else:
                    while True:
                        endereco = input("Endereço: ").strip()
                        if endereco:
                            break
                        print("Endereço é obrigatório. Por favor, preencha.")
                while True:
                    valor_str = input("Valor do imóvel (ex: 150000.00): ").strip().replace(",", ".")
                    try:
                        valor = float(valor_str)
                        valor = round(valor, 2)
                        break
                    except ValueError:
                        raise ValorInvalido(
                            "Valor inválido. Digite um número válido com até 2 casas decimais."
                        )
                seguro_obj = Residencial(endereco, valor)
                dados = seguro_obj.dados
            elif tipo == "Vida":
                while True:
                    valor_segurado_str = (
                        input("Valor Segurado (ex: 100000.00): ").strip().replace(",", ".")
                    )
                    try:
                        valor_segurado = float(valor_segurado_str)
                        valor_segurado = round(valor_segurado, 2)
                        break
                    except ValueError:
                        raise ValorInvalido(
                            "Valor inválido. Digite um número válido com até 2 casas decimais."
                        )
                beneficiarios = input("Beneficiários (separados por vírgula): ").strip()
                lista_benef = [b.strip() for b in beneficiarios.split(",")] if beneficiarios else []
                seguro_obj = Vida(valor_segurado, lista_benef)
                dados = seguro_obj.dados
            elif tipo == "Automóvel":
                while True:
                    modelo = input("Modelo: ").strip()
                    if modelo:
                        break
                    print("Modelo é obrigatório.")
                while True:
                    ano = input("Ano: ").strip()
                    if ano:
                        break
                    print("Ano é obrigatório.")
                while True:
                    placa = input("Placa: ").strip().upper()
                    if validar_placa(placa):
                        break
                    else:
                        raise DadosInvalidos("Placa inválida. Use o formato ABC1234 ou ABC1D23.")
                seguro_obj = Automovel(modelo, ano, placa)
                dados = seguro_obj.dados
            seguro_dict = {
                "tipo": tipo,
                "descricao": str(dados),
                "valor": dados.get("valor", dados.get("valor_segurado", 0)),
                "detalhes": dados,  # Agora passa o dict diretamente (será convertido para JSON)
                "cliente_id": int(cliente["id"]) if cliente and "id" in cliente else None,
            }

            # Usa SeguroService (grava no MySQL + log no MongoDB)
            seguro_id = self.seguro_service.criar_seguro(seguro_dict, self.usuario_atual)

            if seguro_id:
                self.seguros = self.seguro_dao.listar()
                print(f"Seguro cadastrado com sucesso! ID: {seguro_id}")
                registrar_log("INFO", self.usuario_atual, "cadastrar_seguro", id_obj=seguro_id)
            else:
                print("Erro ao cadastrar seguro.")
        except (ClienteInexistente, DadosInvalidos, PermissaoNegada, ValorInvalido) as e:
            print(f"[ERRO] {e}")

    def emitir_apolice(self):
        """
        Emite uma nova apólice vinculada a um cliente e seguro.
        Sprint 4 - Usa ApoliceService para persistência híbrida (MySQL + MongoDB).
        """
        print("=== Emissão de Apólice ===")
        while True:
            cliente_id = input("ID do cliente: ").strip()
            cliente = self.cliente_dao.ler_por_id(int(cliente_id))
            if not cliente:
                print("Cliente não encontrado. Tente novamente.")
                continue
            break

        print("Seguros disponíveis:")
        seguros = self.seguro_dao.listar()
        seguros_cliente = [s for s in seguros if s.get("cliente_id") == cliente["id"]]
        if not seguros_cliente:
            print("Este cliente não possui seguros cadastrados.")
            return
        for i, s in enumerate(seguros_cliente):
            print(f"{i+1}: {s['tipo']} - {s['descricao']}")
        while True:
            try:
                escolha = int(input("Escolha o número do seguro: ").strip())
                if 1 <= escolha <= len(seguros_cliente):
                    break
                else:
                    print("Escolha inválida. Tente novamente.")
            except ValueError:
                print("Entrada inválida. Digite um número.")

        seguro = seguros_cliente[escolha - 1]
        valor_mensal = 0
        tipo = seguro["tipo"]
        valor = seguro.get("valor", 0)
        # Converte Decimal para float se necessário (MySQL retorna Decimal)
        if valor:
            valor = float(valor)
        if tipo == "Automóvel":
            valor_mensal = 200.0
        elif tipo == "Residencial":
            valor_mensal = valor * 0.005
        elif tipo == "Vida":
            valor_mensal = valor * 0.01

        apolice_dados = {
            "cliente_id": cliente["id"],
            "seguro_id": seguro["id"],
            "data_emissao": datetime.now().date(),
            "status": "ativa",
        }

        # Usa ApoliceService (grava no MySQL + log detalhado no MongoDB)
        apolice_id = self.apolice_service.emitir_apolice(apolice_dados, self.usuario_atual)

        if apolice_id:
            self.apolices = self.apolice_dao.listar()
            print(f"Apólice emitida com sucesso! ID: {apolice_id}")
            print(f"Valor mensal estimado: R$ {valor_mensal:.2f}")
            registrar_log("INFO", self.usuario_atual, "emitir_apolice", id_obj=apolice_id)
        else:
            print("Erro ao emitir apólice.")

    def registrar_sinistro(self):
        """
        Registra um novo sinistro vinculado a uma apólice.
        Sprint 4 - Usa SinistroService para persistência híbrida (MySQL + MongoDB).
        """
        print("=== Registro de Sinistro ===")
        while True:
            apolice_id = input("ID da Apólice: ").strip()
            apolice = self.apolice_dao.ler_por_id(int(apolice_id))
            if not apolice:
                print("Apólice não encontrada.")
                continue
            if apolice.get("status", "").lower() != "ativa":
                print(
                    f"Não é possível registrar sinistro: apólice com status '{apolice.get('status')}'."
                )
                return
            break

        descricao = input("Descrição do ocorrido: ").strip()

        while True:
            data = input("Data do sinistro (DD/MM/AAAA): ").strip()
            try:
                data_sinistro = datetime.strptime(data, "%d/%m/%Y")
                if data_sinistro > datetime.now():
                    print("A data do sinistro não pode ser no futuro.")
                else:
                    break
            except ValueError:
                print("Data inválida. Use o formato DD/MM/AAAA.")

        print(f"Tem certeza que deseja registrar o sinistro para a apólice {apolice_id}?")
        confirm = input("Digite 'CONFIRMAR' para prosseguir: ").strip()
        if confirm != "CONFIRMAR":
            print("Operação abortada pelo usuário.")
            return

        # Solicita observações detalhadas (serão salvas no MongoDB)
        observacoes = input("Observações detalhadas (opcional, serão salvas no MongoDB): ").strip()

        sinistro_dados = {
            "apolice_id": apolice["id"],
            "data_ocorrencia": data_sinistro.date(),
            "descricao": descricao,
            "status": "aberto",
        }

        # Usa SinistroService (grava no MySQL + documentos no MongoDB)
        sinistro_id = self.sinistro_service.registrar_sinistro(
            sinistro_dados, self.usuario_atual, observacoes or None
        )

        if sinistro_id:
            self.sinistros = self.sinistro_dao.listar()
            print(f"Sinistro registrado com sucesso! ID: {sinistro_id}")
            if observacoes:
                print("Observações detalhadas salvas no MongoDB.")
            registrar_log("INFO", self.usuario_atual, "registrar_sinistro", id_obj=sinistro_id)
        else:
            print("Erro ao registrar sinistro.")

    def relatorios(self):
        """
        Gera relatórios diversos (valor segurado, apólices por tipo, sinistros por status).
        Consulta dados diretamente do banco via DAOs.
        """
        from functions.exporta_relatorios import (
            exportar_apolices_csv,
            exportar_clientes_csv,
            exportar_seguros_csv,
            exportar_sinistros_csv,
        )

        while True:
            print("\n=== Relatórios ===")
            print("1 - Valor total segurado por cliente")
            print("2 - Apólices emitidas por tipo de seguro")
            print("3 - Quantidade de sinistros abertos/fechados")
            print("4 - Receita mensal prevista (apólices ativas) [CSV]")
            print("5 - Top clientes por valor segurado [CSV]")
            print("6 - Sinistros por status e período [CSV]")
            print("7 - Exportar clientes (CSV)")
            print("8 - Exportar seguros (CSV)")
            print("9 - Exportar apólices (CSV)")
            print("10 - Exportar sinistros (CSV)")
            print("0 - Voltar")
            opcao = input("Escolha uma opção: ").strip()

            if opcao == "1":
                # Valor total segurado por cliente (CLI)
                clientes = self.cliente_dao.listar()
                apolices = self.apolice_dao.listar()
                seguros = self.seguro_dao.listar()
                print("\n--- Valor total segurado por cliente ---")
                print(f"{'ID':<6} {'Nome':<20} {'Valor Segurado':<15}")
                for cliente in clientes:
                    valor = 0
                    for apolice in apolices:
                        if apolice["cliente_id"] == cliente["id"]:
                            seguro = next(
                                (s for s in seguros if s["id"] == apolice["seguro_id"]), None
                            )
                            if seguro:
                                valor += seguro.get("valor", 0) or 0
                    print(f"{cliente['id']:<6} {cliente['nome']:<20} R$ {valor:<12.2f}")
            elif opcao == "2":
                # Apólices emitidas por tipo de seguro (CLI)
                apolices = self.apolice_dao.listar()
                seguros = self.seguro_dao.listar()
                contagem = {"Automóvel": 0, "Residencial": 0, "Vida": 0}
                for apolice in apolices:
                    seguro = next((s for s in seguros if s["id"] == apolice.get("seguro_id")), None)
                    tipo = seguro["tipo"] if seguro else None
                    if tipo in contagem:
                        contagem[tipo] += 1
                print("\n--- Apólices por tipo de seguro ---")
                for tipo, qtd in contagem.items():
                    print(f"{tipo}: {qtd} apólices")
            elif opcao == "3":
                # Quantidade de sinistros abertos/fechados (CLI)
                sinistros = self.sinistro_dao.listar()
                abertos = sum(1 for s in sinistros if s["status"] == "aberto")
                fechados = sum(1 for s in sinistros if s["status"] == "fechado")
                print("\n--- Sinistros por status ---")
                print(f"Abertos: {abertos}")
                print(f"Fechados: {fechados}")
            elif opcao == "4":
                receita_mensal_prevista_cli_export()
            elif opcao == "5":
                top_clientes_valor_segurado_cli_export()
            elif opcao == "6":
                print("Informe o período (pressione Enter para ignorar):")
                data_ini = input("Data inicial (DD/MM/AAAA): ").strip()
                data_fim = input("Data final (DD/MM/AAAA): ").strip()
                from datetime import datetime

                dt_ini = datetime.strptime(data_ini, "%d/%m/%Y") if data_ini else None
                dt_fim = datetime.strptime(data_fim, "%d/%m/%Y") if data_fim else None
                sinistros_status_periodo_cli_export(dt_ini, dt_fim)
            elif opcao == "7":
                exportar_clientes_csv()
                print("Clientes exportados para CSV.")
            elif opcao == "8":
                exportar_seguros_csv()
                print("Seguros exportados para CSV.")
            elif opcao == "9":
                exportar_apolices_csv()
                print("Apólices exportadas para CSV.")
            elif opcao == "10":
                exportar_sinistros_csv()
                print("Sinistros exportados para CSV.")
            elif opcao == "0":
                break
            else:
                print("Opção inválida. Tente novamente.")
