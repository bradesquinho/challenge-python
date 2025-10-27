from functions.sistema import SistemaSeguros


def main():
    sistema = SistemaSeguros()
    if sistema.autenticar_usuario():
        while True:
            print("\nSistema de Gestão de Apólices - Sompo Seguros")
            print("1 - Cadastrar Cliente")
            print("2 - Cadastrar Seguro")
            print("3 - Emitir Apólice")
            print("4 - Registrar Sinistro")
            print("5 - Gerar Relatórios")
            print("6 - Alterar Dados do Cliente")  # Nova opção
            print("7 - Cancelar Apólice")
            print("8 - Atualizar Status de Sinistro")
            print("9 - Sair")

            opcao = input("Escolha uma opção: ").strip()

            if opcao == "1":
                sistema.cadastrar_cliente()
            elif opcao == "2":
                sistema.cadastrar_seguro()
            elif opcao == "3":
                sistema.emitir_apolice()
            elif opcao == "4":
                sistema.registrar_sinistro()
            elif opcao == "5":
                sistema.relatorios()
            elif opcao == "6":
                sistema.alterar_dados_cliente()  # Chama a função para alterar dados do cliente
            elif opcao == "7":
                sistema.cancelar_apolice()
            elif opcao == "8":
                sistema.atualizar_status_sinistro()
            elif opcao == "9":
                print("Saindo do sistema.")
                break
            else:
                print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()
