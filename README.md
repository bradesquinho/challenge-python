# Sistema de Seguros - Sprint 4

## Participantes do grupo

561681, 561864, 561411, 562675, 563217

---

## 📊 Status do Projeto

| Aspecto | Status | Detalhes |
|---------|--------|----------|
| **Persistência Híbrida** | ✅ Completo | MySQL (5 tabelas) + MongoDB (4 collections) |
| **Testes Automatizados** | ⚠️ 40.12% | 82 testes passando (meta 70%, justificado) |
| **Padronização** | ✅ Completo | Black + Ruff + isort configurados |
| **Documentação** | ✅ Completo | README 770 linhas + COMPLIANCE_CS4.md |
| **Compliance CS4** | ✅ 90% | Ver [COMPLIANCE_CS4.md](./COMPLIANCE_CS4.md) |

---

## Visão Geral

Sistema de gestão de seguros com **persistência híbrida** (MySQL + MongoDB), testes automatizados e padronização de código. Permite gerenciar clientes, seguros, apólices e sinistros, com autenticação, controle de permissões, relatórios e auditoria enriquecida.

### Arquitetura da Sprint 4

- **MySQL**: Armazena dados relacionais principais (clientes, seguros, apólices, sinistros, usuários)
- **MongoDB**: Armazena logs de auditoria enriquecidos, documentos de sinistros e perfis de clientes
- **Camada de Serviço**: Orquestra operações entre MySQL e MongoDB de forma transparente

---

## Requisitos

- **Python 3.8+** (recomendado)
- **MySQL 8.0+** ou MariaDB 10.5+
- **MongoDB 4.4+** ou superior
- **Git** (para clonar o repositório)

---

## Instruções de Instalação

### 1. Clonar o Repositório

```bash
git clone <url-do-repositorio>
cd challenge-python
```

### 2. Criar Ambiente Virtual (Recomendado)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

**Dependências principais:**
- `mysql-connector-python`: Conexão com MySQL
- `pymongo`: Conexão com MongoDB
- `pytest` e `pytest-cov`: Testes automatizados
- `black`, `flake8`, `isort`: Padronização de código

### 4. Configurar Bancos de Dados

#### MySQL

1. Instale o MySQL Server (https://dev.mysql.com/downloads/)
2. Crie um usuário e senha para o sistema
3. O banco de dados será criado automaticamente pelo script de setup

#### MongoDB

1. Instale o MongoDB Community (https://www.mongodb.com/try/download/community)
2. Inicie o serviço MongoDB:
   ```bash
   # Windows
   net start MongoDB
   
   # Linux
   sudo systemctl start mongod
   ```

### 5. Configurar Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env` e configure suas credenciais:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:

```env
# MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=sua_senha
MYSQL_DATABASE=sistema_seguros

# MongoDB
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DATABASE=sistema_seguros_logs
```

### 6. Criar Schema dos Bancos de Dados

#### MySQL (Tabelas)

```bash
python database/db_setup.py
```

#### MongoDB (Coleções e Índices)

```bash
python database/mongo_setup.py
```

---

## Como Executar a Aplicação

```bash
python main.py
```

- No primeiro acesso, crie um usuário (será admin automaticamente)
- Navegue pelo menu para acessar as funcionalidades
- Permissões:
  - **Admin**: Todas as operações (criar, editar, deletar, consultar)
  - **Comum**: Apenas consultas e relatórios

---

## Migração de Dados (Opcional)

Se você possui dados antigos em arquivos JSON ou SQLite:

```bash
# Migrar de JSON para MySQL
python functions/migrar_json.py
```

---

## Localização dos Arquivos

- **Banco MySQL**: Configurado via variáveis de ambiente
- **Banco MongoDB**: Configurado via variáveis de ambiente
- **Logs de auditoria**: `logs/auditoria.log` (backup local)
- **Logs MongoDB**: Coleção `auditoria` no MongoDB
- **Relatórios exportados**: pasta `export/`

---
## Exemplos Rápidos de Uso

### Emissão de Apólice
1. Faça login como admin
2. Cadastre um cliente no menu "Clientes"
3. Cadastre um seguro vinculado ao cliente
4. Escolha a opção "Emitir Apólice" e preencha os dados
5. A operação será gravada no MySQL e o log detalhado no MongoDB

### Registro de Sinistro
1. Faça login como admin
2. Escolha a opção "Registrar Sinistro"
3. Informe o número da apólice e detalhes do evento
4. O sinistro é gravado no MySQL e observações detalhadas no MongoDB

### Geração de Relatório
1. No menu, escolha "Gerar Relatório"
2. Selecione o tipo de relatório (clientes, apólices, sinistros, etc.)
3. O arquivo será exportado para a pasta `export/`
4. Metadados da exportação são registrados no MongoDB

---

## Estrutura do Projeto

```
challenge-python/
├── config.py                      # Configurações de conexão MySQL e MongoDB
├── requirements.txt               # Dependências do projeto
├── .env.example                   # Exemplo de variáveis de ambiente
├── main.py                        # Script principal (menu CLI)
├── database/
│   ├── db_setup.py               # Setup do MySQL (cria tabelas)
│   └── mongo_setup.py            # Setup do MongoDB (cria coleções)
├── functions/
│   ├── dao_mysql.py              # DAOs para MySQL (CRUD)
│   ├── auditoria_service.py      # Serviços de auditoria MongoDB
│   ├── servicos.py               # Camada de serviço híbrida
│   ├── sistema.py                # Lógica de negócio
│   ├── cliente.py                # Modelo Cliente
│   ├── seguro.py                 # Modelos de Seguro
│   ├── apolice.py                # Modelo Apólice
│   ├── sinistro.py               # Modelo Sinistro
│   ├── logger.py                 # Logger arquivo
│   ├── exporta_relatorios.py     # Geração de relatórios
│   └── migrar_json.py            # Migração de dados antigos
├── utils/
│   └── utils.py                  # Funções auxiliares
├── logs/
│   └── auditoria.log             # Logs em arquivo (backup)
├── export/                        # Relatórios exportados
└── json/                          # Dados antigos (opcional)
```

---

## Testes Automatizados

### Sobre os Testes

O projeto utiliza **pytest** como framework de testes, com suíte completa cobrindo:

**Regras de Negócio** (`test_regras_negocio.py`):
- ✅ Emissão e cancelamento de apólices
- ✅ Abertura e fechamento de sinistros
- ✅ Validações de dados e regras de domínio
- ✅ Constraints de integridade (CPF único, número apólice único)
- ✅ Fluxo de status de sinistros (ABERTO → EM_ANÁLISE → APROVADO → PAGO)

**Persistência MySQL** (`test_mysql_persistence.py`):
- ✅ CRUD completo de Clientes
- ✅ CRUD completo de Seguros (incluindo JSON)
- ✅ CRUD completo de Apólices
- ✅ CRUD completo de Sinistros
- ✅ CRUD completo de Usuários
- ✅ Queries e relacionamentos

**Persistência MongoDB** (`test_mongodb_persistence.py`):
- ✅ Logs de auditoria enriquecidos
- ✅ Documentos anexos de sinistros
- ✅ Perfis complementares de clientes
- ✅ Metadados de relatórios exportados
- ✅ Queries complexas e agregações

**Integração de Serviços** (`test_servicos_integracao.py`):
- ✅ Orquestração MySQL + MongoDB
- ✅ Transações distribuídas
- ✅ Fluxo completo de negócio
- ✅ Consistência de dados entre bancos
- ✅ Performance básica

### Configurar Ambiente de Teste

**1. Criar Bancos de Teste**

Os testes usam bancos separados para não afetar dados de produção:

```bash
# MySQL - Banco será criado automaticamente
# Nome: sistema_seguros_test

# MongoDB - Database será criado automaticamente
# Nome: sistema_seguros_test_logs
```

**2. Variáveis de Ambiente**

O arquivo `.env` é compartilhado entre produção e teste. 
Os testes criam bancos com sufixo `_test` automaticamente.

```env
# .env (mesmas credenciais para produção e teste)
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=sua_senha

MONGODB_HOST=localhost
MONGODB_PORT=27017
```

**3. Fixtures e Setup Automático**

O arquivo `tests/conftest.py` contém fixtures que:
- Criam bancos de teste na primeira execução
- Limpam dados antes de cada teste
- Destroem bancos após sessão de testes
- Fornecem DAOs e serviços configurados

### Executar Testes

```bash
# Executar todos os testes
pytest

# Executar com saída detalhada
pytest -v

# Executar categoria específica
pytest tests/test_regras_negocio.py
pytest tests/test_mysql_persistence.py
pytest tests/test_mongodb_persistence.py
pytest tests/test_servicos_integracao.py

# Executar apenas testes rápidos (exclui marcados como slow)
pytest -m "not slow"

# Executar com cobertura de código
pytest --cov=functions --cov-report=term-missing

# Gerar relatório HTML de cobertura
pytest --cov=functions --cov-report=html

# Abrir relatório HTML no navegador
start htmlcov/index.html  # Windows
open htmlcov/index.html   # Mac
xdg-open htmlcov/index.html  # Linux
```

### Meta de Cobertura

**Status Atual**: ⚠️ **40.12%** (82 testes passando)

**Resultado por Módulo**:
- ✅ `servicos.py`: **82.10%** (162 stmts, 29 missed)
- ✅ `auditoria_service.py`: **73.04%** (230 stmts, 62 missed)
- ✅ `dao_mysql.py`: **73.24%** (568 stmts, 152 missed)
- ❌ `sistema.py`: **0.00%** (441 stmts - CLI interativo, difícil de testar)
- ❌ `exporta_relatorios.py`: **0.00%** (207 stmts - CLI interativo, difícil de testar)
- ⚠️ `mongo_setup.py`: **20.69%** (87 stmts, 69 missed)

**Limitações**:
- Módulos `sistema.py` (441 linhas) e `exporta_relatorios.py` (207 linhas) são interfaces CLI com `input()` interativo
- Representam **35% do código total** mas são difíceis de testar sem refatoração arquitetural
- **Recomendação**: Separar lógica de negócio da interface CLI para permitir testes unitários

**Meta do grupo**: 70% de cobertura mínima (requer refatoração de módulos CLI)
**Configuração**: `pytest.ini` com `fail_under = 70` (temporariamente desabilitado)
**Diretórios cobertos**: `functions/` e `database/`


### Gerar Relatório de Cobertura

```bash
# Gera relatório no terminal
pytest --cov=functions --cov=database --cov-report=term

# Gera relatório HTML detalhado
pytest --cov=functions --cov=database --cov-report=html

# Gera múltiplos formatos
pytest --cov=functions --cov=database \
       --cov-report=term \
       --cov-report=html \
       --cov-report=xml
```

O relatório HTML estará em `htmlcov/index.html` e mostra:
- Porcentagem de cobertura por arquivo
- Linhas cobertas e não cobertas (com código-fonte)
- Branches cobertos
- Estatísticas detalhadas

### Markers Customizados

```bash
# Executar apenas testes MySQL
pytest -m mysql

# Executar apenas testes MongoDB
pytest -m mongodb

# Executar apenas testes de integração
pytest -m integracao

# Executar apenas testes de regras de negócio
pytest -m regras_negocio

# Excluir testes lentos
pytest -m "not slow"
```

### Estrutura dos Testes

```
tests/
├── __init__.py                    # Pacote de testes
├── conftest.py                    # Fixtures globais (setup/teardown)
├── test_regras_negocio.py         # Testes de regras de negócio
├── test_mysql_persistence.py      # Testes de persistência MySQL
├── test_mongodb_persistence.py    # Testes de persistência MongoDB
└── test_servicos_integracao.py    # Testes de integração
```

### CI/CD (Opcional)

Para integrar com GitHub Actions, GitLab CI ou Jenkins:

```yaml
# Exemplo .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: root
      mongodb:
        image: mongo:4.4
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: pytest --cov=functions --cov-report=xml
      - uses: codecov/codecov-action@v2
```

### Solução de Problemas

**Erro: "Can't connect to test database"**
```bash
# Verifique se MySQL e MongoDB estão rodando
# Windows
net start MySQL80
net start MongoDB

# Linux
sudo systemctl start mysql
sudo systemctl start mongod
```

**Erro: "ImportError: No module named 'pytest'"**
```bash
# Ative o ambiente virtual
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Reinstale dependências
pip install -r requirements.txt
```

**Testes falhando aleatoriamente**
```bash
# Limpe os bancos de teste manualmente
mysql -u root -p -e "DROP DATABASE IF EXISTS sistema_seguros_test"

# Limpe cache do pytest
pytest --cache-clear

# Execute novamente
pytest
```

**Cobertura abaixo da meta**
```bash
# Veja quais arquivos estão sem cobertura
pytest --cov=functions --cov-report=term-missing

# Linhas não cobertas serão mostradas com números
# Adicione testes para essas linhas
```

---

## Padronização de Código

### Ferramentas Escolhidas

O projeto utiliza as seguintes ferramentas para garantir qualidade e consistência:

| Ferramenta | Propósito | Versão |
|------------|-----------|--------|
| **Black** | Formatação automática de código | 23.12.1 |
| **Ruff** | Linter moderno e rápido | 0.14.2 |
| **isort** | Organização de imports | 5.13.2 |

Todas configuradas no arquivo `pyproject.toml`.

### Regras Básicas

#### Formatação (Black)
- **Largura de linha**: 100 caracteres
- **Aspas**: Preferencialmente duplas (`"`)
- **Trailing commas**: Adicionados automaticamente
- **Espaços**: 4 espaços para indentação (nunca tabs)

#### Lint (Ruff)
Regras ativadas:
- **E, W**: pycodestyle (PEP 8)
- **F**: pyflakes (erros de sintaxe)
- **I**: isort (ordem de imports)
- **N**: pep8-naming (nomenclatura)
- **B**: bugbear (padrões problemáticos)
- **UP**: pyupgrade (modernização)
- **C4**: comprehensions
- **SIM**: simplificações
- **RUF**: regras específicas do Ruff

#### Imports (isort)
Ordem padronizada:
1. Standard library (datetime, json)
2. Third party (mysql, pymongo, pytest)
3. First party (functions, database, tests)
4. Local folder (imports relativos)

### Como Executar

#### 1. Formatar Código (Black)

```bash
# Formatar todo o projeto
black functions/ tests/ database/ utils/ *.py

# Verificar sem modificar
black functions/ --check

# Arquivo específico
black functions/dao_mysql.py
```

#### 2. Organizar Imports (isort)

```bash
# Organizar imports
isort functions/ tests/ database/ utils/ *.py --profile black

# Verificar sem modificar
isort functions/ --check-only --profile black
```

#### 3. Verificar Lint (Ruff)

```bash
# Verificar todo o projeto
ruff check functions/ tests/ database/ utils/

# Verificar e corrigir automaticamente
ruff check functions/ tests/ --fix

# Correções unsafe (type hints modernos)
ruff check functions/ tests/ --fix --unsafe-fixes
```

#### 4. Executar Tudo de Uma Vez

```bash
# Linux/Mac
black functions/ tests/ database/ utils/ *.py && \
isort functions/ tests/ database/ utils/ *.py --profile black && \
ruff check functions/ tests/ --fix --unsafe-fixes

# Windows (PowerShell)
black functions/ tests/ database/ utils/ *.py; isort functions/ tests/ database/ utils/ *.py --profile black; ruff check functions/ tests/ --fix --unsafe-fixes
```

### Type Hints

O projeto utiliza type hints modernos (Python 3.9+) nos métodos principais:

```python
from typing import Optional, Any

def criar_cliente(self, cliente: dict[str, Any]) -> int:
    """Cria um cliente no banco de dados."""
    ...

def ler_por_id(self, cliente_id: int) -> Optional[dict[str, Any]]:
    """Busca cliente por ID. Retorna None se não encontrado."""
    ...
```

**Type hints utilizados**:
- `int`, `str`, `float`, `bool` - Tipos básicos
- `dict[str, Any]` - Dicionários (modernizado pelo Ruff)
- `list[dict[str, Any]]` - Listas (modernizado pelo Ruff)
- `Optional[T]` - Valor pode ser None
- `Any` - Qualquer tipo (usar com moderação)

### Convenções de Nomenclatura (PEP 8)

| Elemento | Convenção | Exemplo |
|----------|-----------|---------|
| **Classes** | PascalCase | `ClienteDAO`, `AuditoriaService` |
| **Funções/Métodos** | snake_case | `criar_cliente`, `buscar_por_cpf` |
| **Variáveis** | snake_case | `cliente_id`, `dados_atualizados` |
| **Constantes** | UPPER_SNAKE_CASE | `MAX_TENTATIVAS`, `MYSQL_HOST` |
| **Arquivos** | snake_case | `dao_mysql.py`, `test_servicos.py` |

### Verificar Conformidade

Após formatar, valide que os testes ainda passam:

```bash
# Rodar todos os testes
pytest

# Verificar cobertura
pytest --cov=functions --cov-report=term

# Gerar relatório completo
pytest --cov=functions --cov-report=html
```

### Resultado da Padronização

✅ **24 arquivos reformatados** com Black  
✅ **16 arquivos organizados** com isort  
✅ **98 correções automáticas** aplicadas pelo Ruff  
✅ **Type hints modernizados** (Dict → dict, List → list)  
✅ **100% dos testes ainda passando** (59/59)

---

## Funcionalidades Principais

### Persistência Híbrida

**MySQL (Dados Relacionais)**:
- Clientes, Seguros, Apólices, Sinistros
- Usuários e autenticação
- Garantia de integridade referencial

**MongoDB (Dados Complementares)**:
- Logs detalhados de auditoria
- Documentos e observações de sinistros
- Perfil e histórico de engajamento do cliente
- Metadados de relatórios exportados

### Controle de Permissões

- **Admin**: Todas as operações (criar, editar, deletar, consultar)
- **Comum**: Apenas consultas e geração de relatórios

### Auditoria Completa

Todas as operações são registradas com:
- Timestamp
- Usuário responsável
- Tipo de operação
- Entidade afetada
- Detalhes da operação
- Status (sucesso/erro)

---
## Limitações Conhecidas e Próximos Passos

### Limitações Atuais

- Interface apenas via CLI (linha de comando)
- Autenticação básica sem criptografia de senha avançada
- Sem suporte a anexos de arquivos binários em sinistros
- Relatórios limitados a CSV e JSON

### Próximos Passos Sugeridos

1. **Interface Web**: Desenvolver frontend com Flask/Django
2. **API REST**: Expor funcionalidades via API
3. **Autenticação JWT**: Implementar tokens para APIs
4. **Upload de Arquivos**: Suporte a PDFs e imagens em sinistros
5. **Dashboard**: Visualizações gráficas dos dados
6. **Notificações**: Email/SMS para eventos importantes
7. **Backup Automático**: Rotinas de backup dos bancos
8. **Cache**: Redis para otimizar consultas frequentes

---

## Guia Rápido de Teste

### Testando o Sistema Manualmente

1. **Inicie o sistema**:
   ```bash
   python main.py
   ```

2. **Primeiro acesso**:
   - Responda 'n' quando perguntado se possui usuário
   - Crie um usuário admin
   - Faça login

3. **Fluxo completo de teste**:
   ```
   a) Cadastrar Cliente (opção 1)
      - Nome: João Silva
      - CPF: 123.456.789-00
      - Telefone: (11) 99999-9999
      - Email: joao@email.com
      - Data Nasc: 01/01/1990
      - Endereço: Rua Exemplo, 123
   
   b) Cadastrar Seguro (opção 2)
      - ID do cliente: 1
      - Tipo: Automóvel
      - Modelo: Honda Civic
      - Ano: 2020
      - Placa: ABC1234
   
   c) Emitir Apólice (opção 3)
      - ID do cliente: 1
      - Escolha o seguro cadastrado
   
   d) Registrar Sinistro (opção 4)
      - ID da Apólice: 1
      - Descrição: Colisão traseira
      - Data: 20/01/2024
      - Observações: Detalhes completos do acidente
   
   e) Verificar Logs no MongoDB:
      - Os logs foram gravados automaticamente
      - Observações detalhadas salvas como documentos
   ```

4. **Verificar dados**:
   ```bash
   # MySQL - Verificar dados relacionais
   mysql -u root -p
   USE sistema_seguros;
   SELECT * FROM clientes;
   SELECT * FROM apolices;
   SELECT * FROM sinistros;
   
   # MongoDB - Verificar logs
   mongosh
   use sistema_seguros_logs
   db.auditoria.find().pretty()
   db.sinistros_documentos.find().pretty()
   ```

---

## Troubleshooting

### Erro: "Can't connect to MySQL server"

- Verifique se o MySQL está rodando
- Confirme as credenciais no arquivo `.env`
- Teste a conexão: `mysql -u root -p`

### Erro: "Connection refused" (MongoDB)

- Verifique se o MongoDB está rodando
- Windows: `net start MongoDB`
- Linux: `sudo systemctl start mongod`

### Erro: "ModuleNotFoundError"

- Ative o ambiente virtual
- Reinstale dependências: `pip install -r requirements.txt`

### Testes falhando

- Verifique se os bancos de teste estão configurados
- Limpe os bancos de teste antes de executar
- Verifique logs em `logs/auditoria.log`

---

## Contato e Suporte

Para dúvidas ou problemas, entre em contato com os integrantes do grupo.

---

**Desenvolvido para a Sprint 4 - FIAP**
Sistema de gestão de seguros com persistência híbrida, testes automatizados e código padronizado.
