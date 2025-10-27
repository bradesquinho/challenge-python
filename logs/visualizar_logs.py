"""
Script para visualizar logs do MongoDB via Python
Sprint 4 - Sistema de Seguros
"""
import sys
import os

# Adiciona o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.mongo_setup import MongoDBConnection
from datetime import datetime, timedelta

def listar_todos_logs(limite=10):
    """Lista os últimos logs do sistema"""
    print("\n" + "="*80)
    print(f"📋 ÚLTIMOS {limite} LOGS DE AUDITORIA")
    print("="*80)
    
    db = MongoDBConnection.get_database()
    if db is None:
        print("❌ Não foi possível conectar ao MongoDB")
        return
    
    logs = list(db['auditoria'].find().sort('timestamp', -1).limit(limite))
    
    for i, log in enumerate(logs, 1):
        print(f"\n{i}. [{log['timestamp'].strftime('%d/%m/%Y %H:%M:%S')}]")
        print(f"   Usuario: {log['usuario']}")
        print(f"   Operação: {log['operacao']} → {log['entidade']}")
        if log.get('entidade_id'):
            print(f"   ID: {log['entidade_id']}")
        print(f"   Status: {log.get('status', 'N/A')}")
        if log.get('detalhes'):
            print(f"   Detalhes: {log['detalhes']}")

def listar_logs_por_usuario(usuario):
    """Lista logs de um usuário específico"""
    print("\n" + "="*80)
    print(f"📋 LOGS DO USUÁRIO: {usuario}")
    print("="*80)
    
    db = MongoDBConnection.get_database()
    if db is None:
        print("❌ Não foi possível conectar ao MongoDB")
        return
    
    logs = list(db['auditoria'].find({'usuario': usuario}).sort('timestamp', -1))
    
    print(f"\nTotal: {len(logs)} operações")
    
    for i, log in enumerate(logs, 1):
        print(f"{i}. {log['operacao']} {log['entidade']} - {log['timestamp'].strftime('%d/%m/%Y %H:%M:%S')}")

def listar_logs_por_entidade(entidade):
    """Lista logs de uma entidade específica (cliente, apolice, etc)"""
    print("\n" + "="*80)
    print(f"📋 LOGS DA ENTIDADE: {entidade}")
    print("="*80)
    
    db = MongoDBConnection.get_database()
    if db is None:
        print("❌ Não foi possível conectar ao MongoDB")
        return
    
    logs = list(db['auditoria'].find({'entidade': entidade}).sort('timestamp', -1))
    
    print(f"\nTotal: {len(logs)} operações")
    
    for i, log in enumerate(logs, 1):
        print(f"{i}. {log['usuario']} → {log['operacao']} - {log['timestamp'].strftime('%d/%m/%Y %H:%M:%S')}")
        if log.get('detalhes'):
            print(f"   Detalhes: {log['detalhes']}")

def estatisticas_logs():
    """Mostra estatísticas gerais dos logs"""
    print("\n" + "="*80)
    print("📊 ESTATÍSTICAS DE LOGS")
    print("="*80)
    
    db = MongoDBConnection.get_database()
    if db is None:
        print("❌ Não foi possível conectar ao MongoDB")
        return
    
    # Total de logs
    total = db['auditoria'].count_documents({})
    print(f"\n✅ Total de logs: {total}")
    
    # Logs por entidade
    print("\n📌 Logs por entidade:")
    pipeline = [
        {'$group': {'_id': '$entidade', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ]
    resultado = list(db['auditoria'].aggregate(pipeline))
    for item in resultado:
        print(f"   {item['_id']}: {item['count']}")
    
    # Logs por usuário
    print("\n👤 Logs por usuário:")
    pipeline = [
        {'$group': {'_id': '$usuario', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ]
    resultado = list(db['auditoria'].aggregate(pipeline))
    for item in resultado:
        print(f"   {item['_id']}: {item['count']}")
    
    # Logs por operação
    print("\n🔧 Logs por operação:")
    pipeline = [
        {'$group': {'_id': '$operacao', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ]
    resultado = list(db['auditoria'].aggregate(pipeline))
    for item in resultado:
        print(f"   {item['_id']}: {item['count']}")

def listar_perfis_clientes():
    """Lista perfis de clientes no MongoDB"""
    print("\n" + "="*80)
    print("👤 PERFIS DE CLIENTES NO MONGODB")
    print("="*80)
    
    db = MongoDBConnection.get_database()
    if db is None:
        print("❌ Não foi possível conectar ao MongoDB")
        return
    
    perfis = list(db['clientes_perfil'].find())
    
    print(f"\nTotal: {len(perfis)} perfis")
    
    for perfil in perfis:
        print(f"\n📋 Cliente ID: {perfil['cliente_id']}")
        print(f"   Última atualização: {perfil.get('ultima_atualizacao', 'N/A')}")
        print(f"   Preferências: {perfil.get('preferencias', {})}")
        historico = perfil.get('historico_contato', [])
        print(f"   Histórico de contatos: {len(historico)} registros")
        for i, contato in enumerate(historico[-3:], 1):  # Últimos 3
            print(f"     {i}. {contato.get('tipo')} - {contato.get('descricao')}")

if __name__ == '__main__':
    import sys
    
    print("\n" + "="*80)
    print("🔍 VISUALIZADOR DE LOGS - MONGODB")
    print("="*80)
    
    while True:
        print("\nOpções:")
        print("1 - Ver últimos logs")
        print("2 - Ver logs por usuário")
        print("3 - Ver logs por entidade (cliente, apolice, etc)")
        print("4 - Ver estatísticas")
        print("5 - Ver perfis de clientes")
        print("0 - Sair")
        
        opcao = input("\nEscolha uma opção: ").strip()
        
        if opcao == '1':
            limite = input("Quantos logs deseja ver? (padrão: 10): ").strip()
            limite = int(limite) if limite else 10
            listar_todos_logs(limite)
        
        elif opcao == '2':
            usuario = input("Nome do usuário: ").strip()
            listar_logs_por_usuario(usuario)
        
        elif opcao == '3':
            entidade = input("Nome da entidade (cliente/apolice/sinistro/seguro): ").strip()
            listar_logs_por_entidade(entidade)
        
        elif opcao == '4':
            estatisticas_logs()
        
        elif opcao == '5':
            listar_perfis_clientes()
        
        elif opcao == '0':
            print("\n👋 Até logo!")
            break
        
        else:
            print("❌ Opção inválida!")
