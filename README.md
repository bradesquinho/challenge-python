# Sistema de Seguros

## Instruções de Uso

Este sistema permite gerenciar clientes, seguros, apólices e sinistros, com autenticação, controle de permissões, relatórios e auditoria. Toda a persistência é feita via banco SQLite, eliminando o uso de arquivos JSON.

### Como executar

1. Certifique-se de ter o Python 3 instalado.
2. Execute o script de criação das tabelas (apenas na primeira vez ou após limpeza do banco):
	```
	python database/db_setup.py
	```
3. Inicie o sistema:
	```
	python main.py
	```
4. No primeiro acesso, será solicitado login ou cadastro. O primeiro usuário criado é admin por padrão.
5. Navegue pelo menu para acessar as funcionalidades conforme seu perfil.

### Funcionalidades principais

- Cadastro e autenticação de usuários (persistência em SQLite, perfis admin/comum).
- Controle de permissões:
  - **Admin:** pode cadastrar, editar, cancelar, emitir apólices, registrar e atualizar sinistros, alterar clientes e acessar relatórios.
  - **Comum:** pode apenas consultar e gerar relatórios.
- Cadastro de clientes com validação de CPF, telefone e e-mail.
- Cadastro de seguros: Automóvel, Residencial e Vida (com validações específicas).
- Emissão de apólices vinculadas a clientes e seguros.
- Registro e atualização de sinistros (restrito a admin).
- Alteração de dados de clientes e cancelamento de apólices (restrito a admin).
- Geração e exportação de relatórios analíticos (CSV/JSON).
- Auditoria completa: todas as operações sensíveis são registradas em log, incluindo o usuário autenticado.

## Estrutura de Arquivos

- `main.py`: Script principal (menu e fluxo do sistema).
- `functions/sistema.py`: Classe `SistemaSeguros` (lógica de negócio, autenticação, permissões).
- `functions/dao.py`: DAOs para acesso/manipulação das entidades no banco SQLite.
- `database/db_setup.py`: Script de criação das tabelas do banco.
- `functions/logger.py`: Módulo de auditoria/logs (arquivo e console).
- `functions/exporta_relatorios.py`: Relatórios analíticos e exportação.
- `cliente.py`, `seguro.py`, `apolice.py`, `sinistro.py`: Definições das entidades.
- `utils.py`: Funções auxiliares de validação.
- Banco de dados: `sistema_seguros.db` (criado automaticamente).

## Requisitos para Execução

- Python 3.x (recomendado Python 3.6+)
- Apenas bibliotecas padrão do Python (nenhuma dependência externa)

O sistema é totalmente operado via terminal/linha de comando.

---
Desenvolvido para facilitar a gestão de seguros com validações, controle de permissões e auditoria robusta, sem dependências externas e com persistência confiável em banco de dados.
