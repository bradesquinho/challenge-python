1) Persistência Híbrida (MySQL + MongoDB)

MySQL (relacional – núcleo do negócio):

Persistir Cliente, Seguro, Apólice, Sinistro e Usuário/Autenticação.
Garantir integridade nas operações principais (emissão/cancelamento de apólice, abertura/fechamento de sinistro, consultas e relatórios).

MongoDB (documentos – dados complementares):

Armazenar logs detalhados de operações (auditoria enriquecida), anexos e documentos desestruturados de sinistros (relatórios, observações extensas, metadados).
Opcionalmente manter perfil/engajamento do cliente (preferências, histórico de contato).

Serviços de aplicação:

Implementar uma camada de serviço que orquestre gravações: ação principal no MySQL e enriquecimento/log no MongoDB quando aplicável.
As operações do menu/CLI devem funcionar de ponta a ponta usando essa camada híbrida.

2) Testes Automatizados (biblioteca à escolha do grupo)

Criar suíte de testes automatizados que cubra:

Regras de negócio centrais (emissão/cancelamento de apólice, abertura/fechamento de sinistro, cálculos/validações).
Persistência em MySQL (CRUD e consultas principais).
Persistência em MongoDB (inserção/consulta de documentos/logs).

Lib livre: pytest, unittest, nose2 ou similar (à escolha do grupo).

Cobertura mínima: definir uma meta do grupo (recomendação: = 70%). Registrar no README a meta e como gerar o relatório.

Permite-se usar bancos temporários (por exemplo, schemas separados para teste, containers locais, ou mocks/fakes quando fizer sentido). Descrever no README como rodar os testes localmente.

3) Padronização de Código

Adotar um padrão de formatação e lint (livre a escolha do grupo), por exemplo:

Formatação: black ou yapf.
Lint: ruff, flake8 ou pylint.
Imports: isort (opcional).

Definir e documentar no README:

As ferramentas escolhidas.
Como executar (comandos).
Regras básicas (ex.: largura de linha, convenções de nome, docstrings).

Recomenda-se uso moderado de type hints nas principais classes/métodos (opcional, mas desejável).



Entregáveis da Sprint 4 (via GitHub)

O grupo deverá entregar um repositório no GitHub contendo:

Código do Sistema (atualizado)

Integração funcional com MySQL para entidades de negócio.
Integração funcional com MongoDB para logs/anexos/dados desestruturados.
Camada de serviços realizando a orquestração entre MySQL e MongoDB.

Testes Automatizados

Pasta de testes com casos cobrindo regras de negócio e persistência (MySQL e Mongo).
Instruções no README para preparar o ambiente de teste (por exemplo, subir containers locais, configurar variáveis, criar schema de teste) e para executar os testes.
Indicação clara da meta de cobertura e como gerar o relatório.

Padronização de Código

Arquivos de configuração das ferramentas escolhidas (ex.: pyproject.toml, .flake8, .pylintrc, ruff.toml, etc., conforme a escolha do grupo).
Comandos documentados no README para formatar e verificar o código.

README.md (completo)

Nomes e RMs de todos os integrantes do grupo no topo do arquivo.
Visão geral do projeto e desta Sprint (o que foi implementado).
Requisitos e preparação do ambiente (MySQL, MongoDB, variáveis de ambiente, strings de conexão).
Como executar a aplicação (passo a passo).
Como rodar os testes e gerar cobertura.
Como rodar as ferramentas de padronização (lint/format).
Estrutura resumida do repositório.
Limitações conhecidas e próximos passos sugeridos.