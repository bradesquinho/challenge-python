from functions.exporta_relatorios import receita_mensal_prevista_cli_export, top_clientes_valor_segurado_cli_export, sinistros_status_periodo_cli_export
from functions.cliente import Cliente
from functions.seguro import Automovel, Residencial, Vida
from functions.apolice import Apolice
from functions.sinistro import Sinistro
from utils.utils import validar_cpf, validar_placa
from datetime import datetime
import getpass  # Para ocultar a senha

from functions.dao import ClienteDAO, SeguroDAO, ApoliceDAO, SinistroDAO, UsuarioDAO
from functions.logger import registrar_log
from functions.exceptions import (
    CpfInvalido, ApoliceInexistente, OperacaoNaoPermitida, SinistroInexistente,
    ClienteInexistente, UsuarioInvalido, SeguroInexistente, DadosInvalidos, DataInvalida, ValorInvalido, PermissaoNegada
)

class SistemaSeguros:
    def __init__(self):
        """
        Inicializa o sistema, carregando dados do banco SQLite via DAOs.
        Usuários continuam sendo carregados de usuarios.json.
        """
        self.clientes = ClienteDAO.listar()
        self.seguros = SeguroDAO.listar()
        self.apolices = ApoliceDAO.listar()
        self.sinistros = SinistroDAO.listar()
        # Usuários agora no banco SQLite
        if not UsuarioDAO.listar():
            UsuarioDAO.criar({'username': 'admin', 'senha': 'senha123', 'tipo': 'admin'})

    def atualizar_status_sinistro(self):
        """
        Permite atualizar o status de um sinistro (ex: de 'aberto' para 'fechado').
        """
        print("=== Atualizar Status de Sinistro ===")
        try:
            sinistro_id = input("ID do sinistro a atualizar: ").strip()
            sinistro = SinistroDAO.ler_por_id(int(sinistro_id))
            if not sinistro:
                raise SinistroInexistente("Sinistro não encontrado.")
            print(f"Status atual: {sinistro['status']}")
            novo_status = input("Novo status (aberto/fechado): ").strip().lower()
            if novo_status not in ["aberto", "fechado"]:
                raise OperacaoNaoPermitida("Status inválido. Use 'aberto' ou 'fechado'.")
            if sinistro['status'] != novo_status:
                print(f"Tem certeza que deseja alterar o status do sinistro {sinistro_id} para '{novo_status}'?")
                confirm = input("Digite 'CONFIRMAR' para prosseguir: ").strip()
                if confirm != 'CONFIRMAR':
                    print("Operação abortada pelo usuário.")
                    return
            sinistro['status'] = novo_status
            SinistroDAO.atualizar(int(sinistro_id), sinistro)
            self.sinistros = SinistroDAO.listar()
            print("Status do sinistro atualizado com sucesso!")
            usuario = getattr(self, 'usuario_atual', 'desconhecido')
            registrar_log('INFO', usuario, f"atualizar_status_sinistro", id_obj=sinistro_id)
        except (SinistroInexistente, OperacaoNaoPermitida) as e:
            print(f"[ERRO] {e}")

    def cancelar_apolice(self):
        """
        Permite cancelar uma apólice existente, alterando seu status para 'cancelada'.
        """
        print("=== Cancelar Apólice ===")
        try:
            apolice_id = input("ID da apólice a cancelar: ").strip()
            apolice = ApoliceDAO.ler_por_id(int(apolice_id))
            if not apolice:
                raise ApoliceInexistente("Apólice não encontrada.")
            if apolice.get('status', '').lower() == 'cancelada':
                raise OperacaoNaoPermitida("Esta apólice já está cancelada.")
            print(f"Tem certeza que deseja cancelar a apólice {apolice_id}? Esta ação não pode ser desfeita.")
            confirm = input("Digite 'CONFIRMAR' para cancelar: ").strip()
            if confirm != 'CONFIRMAR':
                print("Cancelamento abortado pelo usuário.")
                return
            apolice['status'] = 'cancelada'
            ApoliceDAO.atualizar(int(apolice_id), apolice)
            self.apolices = ApoliceDAO.listar()
            print("Apólice cancelada com sucesso!")
            usuario = getattr(self, 'usuario_atual', 'desconhecido')
            registrar_log('INFO', usuario, f"cancelar_apolice", id_obj=apolice_id)
        except (ApoliceInexistente, OperacaoNaoPermitida) as e:
            print(f"[ERRO] {e}")

    def alterar_dados_cliente(self):
        """
        Permite alterar os dados de um cliente já cadastrado.
        """
        print("=== Alterar Dados do Cliente ===")
        try:
            cliente_id = input("ID do cliente a alterar: ").strip()
            cliente = ClienteDAO.ler_por_id(int(cliente_id))
            if not cliente:
                raise OperacaoNaoPermitida("Cliente não encontrado.")
            print(f"Dados atuais: Nome: {cliente['nome']}, CPF: {cliente['cpf']}, Telefone: {cliente.get('telefone','')}, Email: {cliente.get('email','')}, Data Nasc: {cliente['data_nasc']}, Endereço: {cliente['endereco']}")
            nome = input(f"Novo nome [{cliente['nome']}]: ").strip() or cliente['nome']
            cpf = input(f"Novo CPF [{cliente['cpf']}]: ").strip() or cliente['cpf']
            telefone = input(f"Novo telefone [{cliente.get('telefone','')}]: ").strip() or cliente.get('telefone','')
            email = input(f"Novo email [{cliente.get('email','')}]: ").strip() or cliente.get('email','')
            data_nasc = input(f"Nova data de nascimento [{cliente['data_nasc']}]: ").strip() or cliente['data_nasc']
            endereco = input(f"Novo endereço [{cliente['endereco']}]: ").strip() or cliente['endereco']
            print(f"Tem certeza que deseja alterar os dados do cliente {cliente_id} ({cliente['nome']})?")
            confirm = input("Digite 'CONFIRMAR' para prosseguir: ").strip()
            if confirm != 'CONFIRMAR':
                print("Operação abortada pelo usuário.")
                return
            novos_dados = {
                'nome': nome,
                'cpf': cpf,
                'telefone': telefone,
                'email': email,
                'data_nasc': data_nasc,
                'endereco': endereco
            }
            ClienteDAO.atualizar(int(cliente_id), novos_dados)
            self.clientes = ClienteDAO.listar()
            print("Dados do cliente atualizados com sucesso!")
            usuario = getattr(self, 'usuario_atual', 'desconhecido')
            registrar_log('INFO', usuario, f"alterar_dados_cliente", id_obj=cliente_id)
        except OperacaoNaoPermitida as e:
            print(f"[ERRO] {e}")

    def cadastrar_cliente(self):
        """
        Cadastra um novo cliente e persiste no banco SQLite via ClienteDAO.
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
                if any(c['cpf'] == cpf for c in ClienteDAO.listar()):
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
            cliente = {
                "nome": nome,
                "cpf": cpf,
                "telefone": telefone,
                "email": email,
                "endereco": endereco,
                "data_nasc": data_nasc.strftime("%d/%m/%Y")
            }
            cliente_id = ClienteDAO.criar(cliente)
            self.clientes = ClienteDAO.listar()
            print(f"Cliente cadastrado com sucesso! ID: {cliente_id}")
            usuario = getattr(self, 'usuario_atual', 'desconhecido')
            registrar_log('INFO', usuario, f"cadastrar_cliente", id_obj=cliente_id)
        except (CpfInvalido, OperacaoNaoPermitida) as e:
            print(f"[ERRO] {e}")



    def autenticar_usuario(self):
        """
        Realiza autenticação do usuário, permitindo login ou cadastro.
        Utiliza dados do banco SQLite.
        """
        print("Você já possui usuário e senha? (s/n)")
        while True:
            possui = input().strip().lower()
            if possui == 's':
                return self.login()
            elif possui == 'n':
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
            if UsuarioDAO.ler_por_username(usuario):
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
            UsuarioDAO.criar({'username': usuario, 'senha': senha, 'tipo': tipo})
            print("Usuário cadastrado com sucesso! Faça login agora.")
            return self.login()

    def login(self):
        while True:
            print("=== Login ===")
            usuario = input("Usuário: ").strip()
            senha = input("Senha: ").strip()
            user = UsuarioDAO.ler_por_username(usuario)
            if user and user['senha'] == senha:
                self.usuario_atual = usuario
                self.tipo_usuario = user['tipo']
                print(f"Login bem-sucedido! Tipo de usuário: {self.tipo_usuario}")
                return True
            else:
                print("Usuário ou senha inválidos. Tente novamente.")

    def cadastrar_seguro(self, cliente=None):
        """
        Cadastra um novo seguro (Automóvel, Residencial ou Vida) e persiste no banco SQLite via SeguroDAO.
        Se cliente for fornecido, pode usar dados do cliente.
        """
        try:
            print("=== Cadastro de Seguro ===")
            if not cliente:
                cliente_id = input("ID do cliente: ").strip()
                cliente = ClienteDAO.ler_por_id(int(cliente_id))
                if not cliente:
                    raise ClienteInexistente("Cliente não encontrado.")
            data_nasc = cliente.get('data_nasc')
            if not data_nasc:
                raise DadosInvalidos("O cliente não possui data de nascimento cadastrada. Verifique os dados do cliente.")
            try:
                idade_cliente = (datetime.now() - datetime.strptime(data_nasc, "%d/%m/%Y")).days // 365
            except Exception:
                raise DadosInvalidos(f"Data de nascimento inconsistente para o cliente (ID {cliente.get('id')}): '{data_nasc}'. Corrija o cadastro do cliente.")
            tipo = None
            while True:
                tipo_input = input("Tipo de Seguro (Automóvel, Residencial, Vida): ").strip().capitalize()
                if tipo_input in ["Automóvel", "Residencial", "Vida"]:
                    tipo = tipo_input
                    break
                else:
                    print("Tipo de seguro inválido. Escolha Automóvel, Residencial ou Vida.")
            if tipo == "Automóvel" and idade_cliente < 18:
                raise PermissaoNegada("É necessário ser maior de idade para contratar um seguro de automóvel.")
            if tipo == "Vida" and idade_cliente < 18:
                print("Menores de 18 anos podem contratar seguro de vida apenas com a assistência de um responsável.")
                responsavel = input("O responsável está presente? (s/n): ").strip().lower()
                if responsavel != 's':
                    raise PermissaoNegada("Cadastro de seguro de vida não permitido sem responsável.")
            dados = {}
            if tipo == "Residencial":
                usar_endereco_cliente = input("Usar o endereço do cliente? (s/n): ").strip().lower()
                if usar_endereco_cliente == "s":
                    endereco = cliente.get('endereco')
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
                    valor_str = input("Valor do imóvel (ex: 150000.00): ").strip().replace(',', '.')
                    try:
                        valor = float(valor_str)
                        valor = round(valor, 2)
                        break
                    except ValueError:
                        raise ValorInvalido("Valor inválido. Digite um número válido com até 2 casas decimais.")
                seguro_obj = Residencial(endereco, valor)
                dados = seguro_obj.dados
            elif tipo == "Vida":
                while True:
                    valor_segurado_str = input("Valor Segurado (ex: 100000.00): ").strip().replace(',', '.')
                    try:
                        valor_segurado = float(valor_segurado_str)
                        valor_segurado = round(valor_segurado, 2)
                        break
                    except ValueError:
                        raise ValorInvalido("Valor inválido. Digite um número válido com até 2 casas decimais.")
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
                "valor": dados.get('valor', dados.get('valor_segurado', 0)),
                "detalhes": str(dados),
                "cliente_id": int(cliente['id']) if cliente and 'id' in cliente else None
            }
            seguro_id = SeguroDAO.criar(seguro_dict)
            self.seguros = SeguroDAO.listar()
            print(f"Seguro cadastrado com sucesso! ID: {seguro_id}")
            usuario = getattr(self, 'usuario_atual', 'desconhecido')
            registrar_log('INFO', usuario, f"cadastrar_seguro", id_obj=seguro_id)
        except (ClienteInexistente, DadosInvalidos, PermissaoNegada, ValorInvalido) as e:
            print(f"[ERRO] {e}")

    def emitir_apolice(self):
        """
        Emite uma nova apólice vinculada a um cliente e seguro.
        Persiste os dados no banco SQLite via ApoliceDAO.
        """        
        print("=== Emissão de Apólice ===")
        while True:
            cliente_id = input("ID do cliente: ").strip()
            cliente = ClienteDAO.ler_por_id(int(cliente_id))
            if not cliente:
                print("Cliente não encontrado. Tente novamente.")
                continue
            break

        print("Seguros disponíveis:")
        seguros = SeguroDAO.listar()
        seguros_cliente = [s for s in seguros if s.get('cliente_id') == cliente['id']]
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
        tipo = seguro['tipo']
        valor = seguro.get('valor', 0)
        if tipo == "Automóvel":
            valor_mensal = 200.0
        elif tipo == "Residencial":
            valor_mensal = valor * 0.005
        elif tipo == "Vida":
            valor_mensal = valor * 0.01
        apolice = {
            "cliente_id": cliente['id'],
            "seguro_id": seguro['id'],
            "data_emissao": datetime.now().strftime("%d/%m/%Y"),
            "status": "ativa"
        }
        apolice_id = ApoliceDAO.criar(apolice)
        self.apolices = ApoliceDAO.listar()
        print(f"Apolice emitida com sucesso! ID: {apolice_id}")
        usuario = getattr(self, 'usuario_atual', 'desconhecido')
        registrar_log('INFO', usuario, f"emitir_apolice", id_obj=apolice_id)

    def registrar_sinistro(self):
        """
        Registra um novo sinistro vinculado a uma apólice.
        Persiste os dados no banco SQLite via SinistroDAO.
        """
        print("=== Registro de Sinistro ===")
        while True:
            apolice_id = input("ID da Apólice: ").strip()
            apolice = ApoliceDAO.ler_por_id(int(apolice_id))
            if not apolice:
                print("Apólice não encontrada.")
                continue
            if apolice.get('status', '').lower() != 'ativa':
                print(f"Não é possível registrar sinistro: apólice com status '{apolice.get('status')}'.")
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
        if confirm != 'CONFIRMAR':
            print("Operação abortada pelo usuário.")
            return
        sinistro = {
            "apolice_id": apolice['id'],
            "data_ocorrencia": data,
            "descricao": descricao,
            "status": "aberto"
        }
        sinistro_id = SinistroDAO.criar(sinistro)
        self.sinistros = SinistroDAO.listar()
        print(f"Sinistro registrado com sucesso! ID: {sinistro_id}")
        usuario = getattr(self, 'usuario_atual', 'desconhecido')
        registrar_log('INFO', usuario, f"registrar_sinistro", id_obj=sinistro_id)


    def relatorios(self):
        """
        Gera relatórios diversos (valor segurado, apólices por tipo, sinistros por status).
        Consulta dados diretamente do banco via DAOs.
        """
        from functions.exporta_relatorios import (
            receita_mensal_prevista_cli_export, top_clientes_valor_segurado_cli_export, sinistros_status_periodo_cli_export,
            exportar_clientes_csv, exportar_clientes_json, exportar_seguros_csv, exportar_seguros_json,
            exportar_apolices_csv, exportar_apolices_json, exportar_sinistros_csv, exportar_sinistros_json
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

            if opcao == '1':
                # Valor total segurado por cliente (CLI)
                clientes = ClienteDAO.listar()
                apolices = ApoliceDAO.listar()
                seguros = SeguroDAO.listar()
                print("\n--- Valor total segurado por cliente ---")
                print(f"{'ID':<6} {'Nome':<20} {'Valor Segurado':<15}")
                for cliente in clientes:
                    valor = 0
                    for apolice in apolices:
                        if apolice['cliente_id'] == cliente['id']:
                            seguro = next((s for s in seguros if s['id'] == apolice['seguro_id']), None)
                            if seguro:
                                valor += seguro.get('valor', 0) or 0
                    print(f"{cliente['id']:<6} {cliente['nome']:<20} R$ {valor:<12.2f}")
            elif opcao == '2':
                # Apólices emitidas por tipo de seguro (CLI)
                apolices = ApoliceDAO.listar()
                seguros = SeguroDAO.listar()
                contagem = {"Automóvel": 0, "Residencial": 0, "Vida": 0}
                for apolice in apolices:
                    seguro = next((s for s in seguros if s['id'] == apolice.get('seguro_id')), None)
                    tipo = seguro['tipo'] if seguro else None
                    if tipo in contagem:
                        contagem[tipo] += 1
                print("\n--- Apólices por tipo de seguro ---")
                for tipo, qtd in contagem.items():
                    print(f"{tipo}: {qtd} apólices")
            elif opcao == '3':
                # Quantidade de sinistros abertos/fechados (CLI)
                sinistros = SinistroDAO.listar()
                abertos = sum(1 for s in sinistros if s['status'] == 'aberto')
                fechados = sum(1 for s in sinistros if s['status'] == 'fechado')
                print("\n--- Sinistros por status ---")
                print(f"Abertos: {abertos}")
                print(f"Fechados: {fechados}")
            elif opcao == '4':
                receita_mensal_prevista_cli_export()
            elif opcao == '5':
                top_clientes_valor_segurado_cli_export()
            elif opcao == '6':
                print("Informe o período (pressione Enter para ignorar):")
                data_ini = input("Data inicial (DD/MM/AAAA): ").strip()
                data_fim = input("Data final (DD/MM/AAAA): ").strip()
                from datetime import datetime
                dt_ini = datetime.strptime(data_ini, "%d/%m/%Y") if data_ini else None
                dt_fim = datetime.strptime(data_fim, "%d/%m/%Y") if data_fim else None
                sinistros_status_periodo_cli_export(dt_ini, dt_fim)
            elif opcao == '7':
                exportar_clientes_csv()
                print("Clientes exportados para CSV.")
            elif opcao == '8':
                exportar_seguros_csv()
                print("Seguros exportados para CSV.")
            elif opcao == '9':
                exportar_apolices_csv()
                print("Apólices exportadas para CSV.")
            elif opcao == '10':
                exportar_sinistros_csv()
                print("Sinistros exportados para CSV.")
            elif opcao == '0':
                break
            else:
                print("Opção inválida. Tente novamente.")

