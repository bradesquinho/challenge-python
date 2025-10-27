# Guia Rápido de Testes

## Executar Testes

### Comando básico
```bash
# Executar todos os testes
pytest

# Executar com saída detalhada
pytest -v

# Executar testes de uma categoria específica
pytest tests/test_regras_negocio.py -v
```

### Testes com Cobertura
```bash
# Executar com relatório de cobertura no terminal
pytest --cov=functions --cov-report=term-missing

# Gerar relatório HTML
pytest --cov=functions --cov-report=html

# Abrir relatório HTML
start htmlcov/index.html  # Windows
```

## Testes Criados

### 59 Testes Totais

**Regras de Negócio** (10 testes):
- ✅ 4 testes de emissão de apólice
- ✅ 3 testes de gestão de sinistros
- ✅ 3 testes de validações

**Persistência MySQL** (21 testes):
- ✅ 6 testes de ClienteDAO (criar, ler, atualizar, deletar, listar, buscar)
- ✅ 5 testes de SeguroDAO
- ✅ 4 testes de ApoliceDAO
- ✅ 3 testes de SinistroDAO
- ✅ 3 testes de UsuarioDAO

**Persistência MongoDB** (18 testes):
- ✅ 5 testes de auditoria
- ✅ 4 testes de documentos de sinistros
- ✅ 4 testes de perfis de clientes
- ✅ 3 testes de metadados de relatórios
- ✅ 2 testes de queries complexas

**Integração** (10 testes):
- ✅ 3 testes de ClienteService
- ✅ 2 testes de ApoliceService
- ✅ 2 testes de SinistroService
- ✅ 2 testes de fluxo completo
- ✅ 1 teste de performance

## Estrutura

```
tests/
├── conftest.py                    # Fixtures (setup/teardown automático)
├── test_regras_negocio.py         # Lógica de negócio
├── test_mysql_persistence.py      # CRUD MySQL
├── test_mongodb_persistence.py    # Documentos MongoDB
└── test_servicos_integracao.py    # Integração MySQL + MongoDB
```

## Pré-requisitos

1. MySQL rodando (localhost:3306)
2. MongoDB rodando (localhost:27017)
3. Variáveis de ambiente configuradas (.env)
4. Dependências instaladas (pip install -r requirements.txt)

## Primeira Execução

Os testes criam automaticamente:
- Banco MySQL: `sistema_seguros_test`
- Database MongoDB: `sistema_seguros_test_logs`

Após a execução, os bancos são limpos automaticamente.

## Meta de Cobertura

**Objetivo: 70% de cobertura mínima**

Para verificar:
```bash
pytest --cov=functions --cov-report=term
```

## Troubleshooting

**Erro de conexão MySQL/MongoDB?**
- Verifique se os serviços estão rodando
- Confirme credenciais no .env

**ImportError?**
- Ative o ambiente virtual
- pip install -r requirements.txt

**Testes falhando?**
- Limpe cache: pytest --cache-clear
- Execute novamente
