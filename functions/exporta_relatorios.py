import csv
import json
import os
from datetime import datetime

# Sprint 4 - Usa DAOs do MySQL (não mais SQLite)
from functions.dao_mysql import ApoliceDAO, ClienteDAO, SeguroDAO, SinistroDAO

EXPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "export")


def receita_mensal_prevista_cli_export():
    # Instancia os DAOs
    apolice_dao = ApoliceDAO()
    seguro_dao = SeguroDAO()
    
    apolices = apolice_dao.listar()
    seguros = seguro_dao.listar()
    total = 0
    rows = []
    for apolice in apolices:
        if apolice.get("status", "").lower() == "ativa":
            seguro = next((s for s in seguros if s["id"] == apolice.get("seguro_id")), None)
            valor = seguro.get("valor", 0) if seguro else 0
            # Converte Decimal para float
            if valor:
                valor = float(valor)
            tipo = seguro.get("tipo", "") if seguro else ""
            if tipo == "Automóvel":
                mensal = 200.0
            elif tipo == "Residencial":
                mensal = valor * 0.005
            elif tipo == "Vida":
                mensal = valor * 0.01
            else:
                mensal = 0
            total += mensal
            rows.append(
                {
                    "apolice_id": apolice["id"],
                    "cliente_id": apolice["cliente_id"],
                    "seguro_id": apolice["seguro_id"],
                    "tipo": tipo,
                    "mensalidade": round(mensal, 2),
                }
            )
    print("\n--- Receita Mensal Prevista (Apolices Ativas) ---")
    if not rows:
        print("Nenhuma apólice ativa encontrada.")
        return
    print(f"{'Apolice':<8} {'Cliente':<8} {'Seguro':<8} {'Tipo':<12} {'Mensalidade':<12}")
    for r in rows:
        print(
            f"{r['apolice_id']:<8} {r['cliente_id']:<8} {r['seguro_id']:<8} {r['tipo']:<12} R$ {r['mensalidade']:<10.2f}"
        )
    print(f"Total previsto: R$ {total:.2f}")
    # Exporta CSV
    path = os.path.join(EXPORT_DIR, "receita_mensal_prevista.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"CSV exportado para {path}")


def top_clientes_valor_segurado_cli_export(top_n=5):
    # Instancia os DAOs
    cliente_dao = ClienteDAO()
    apolice_dao = ApoliceDAO()
    seguro_dao = SeguroDAO()
    
    clientes = cliente_dao.listar()
    apolices = apolice_dao.listar()
    seguros = seguro_dao.listar()
    ranking = []
    for cliente in clientes:
        valor = 0
        for apolice in apolices:
            if apolice["cliente_id"] == cliente["id"]:
                seguro = next((s for s in seguros if s["id"] == apolice["seguro_id"]), None)
                if seguro:
                    valor_seguro = seguro.get("valor", 0) or 0
                    # Converte Decimal para float
                    if valor_seguro:
                        valor_seguro = float(valor_seguro)
                    valor += valor_seguro
        ranking.append(
            {"cliente_id": cliente["id"], "nome": cliente["nome"], "valor_segurado": valor}
        )
    ranking.sort(key=lambda x: x["valor_segurado"], reverse=True)
    print(f"\n--- Top {top_n} Clientes por Valor Segurado ---")
    if not ranking:
        print("Nenhum cliente encontrado.")
        return
    print(f"{'ID':<6} {'Nome':<20} {'Valor Segurado':<15}")
    for r in ranking[:top_n]:
        print(f"{r['cliente_id']:<6} {r['nome']:<20} R$ {r['valor_segurado']:<12.2f}")
    # Exporta CSV
    path = os.path.join(EXPORT_DIR, "top_clientes_valor_segurado.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ranking[0].keys())
        writer.writeheader()
        writer.writerows(ranking[:top_n])
    print(f"CSV exportado para {path}")


def sinistros_status_periodo_cli_export(data_ini=None, data_fim=None):
    # Instancia o DAO
    sinistro_dao = SinistroDAO()
    
    sinistros = sinistro_dao.listar()
    rows = []
    for s in sinistros:
        data = s.get("data_ocorrencia")
        if data:
            try:
                # Tenta formato MySQL (YYYY-MM-DD) ou objeto date
                if isinstance(data, str):
                    try:
                        data_dt = datetime.strptime(data, "%Y-%m-%d")
                    except ValueError:
                        data_dt = datetime.strptime(data, "%d/%m/%Y")
                else:
                    # Objeto date
                    data_dt = datetime.combine(data, datetime.min.time())
            except Exception:
                continue
            if data_ini and data_dt < data_ini:
                continue
            if data_fim and data_dt > data_fim:
                continue
        rows.append(
            {
                "id": s["id"],
                "apolice_id": s["apolice_id"],
                "data_ocorrencia": str(s["data_ocorrencia"]),
                "descricao": s["descricao"],
                "status": s["status"],
            }
        )
    # Agrupa por status
    status_count = {}
    for r in rows:
        status_count[r["status"]] = status_count.get(r["status"], 0) + 1
    print("\n--- Sinistros por Status e Período ---")
    if not rows:
        print("Nenhum sinistro encontrado.")
        return
    print(f"{'ID':<6} {'Apolice':<8} {'Data':<12} {'Status':<10} {'Descricao'}")
    for r in rows:
        print(
            f"{r['id']:<6} {r['apolice_id']:<8} {r['data_ocorrencia']:<12} {r['status']:<10} {r['descricao']}"
        )
    print("\nResumo por status:")
    for k, v in status_count.items():
        print(f"{k}: {v}")
    # Exporta CSV
    path = os.path.join(EXPORT_DIR, "sinistros_status_periodo.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"CSV exportado para {path}")


def exportar_clientes_csv(path="clientes_export.csv"):
    cliente_dao = ClienteDAO()
    clientes = cliente_dao.listar()
    if not clientes:
        print("Nenhum cliente para exportar.")
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=clientes[0].keys())
        writer.writeheader()
        writer.writerows(clientes)


def exportar_clientes_json(path="clientes_export.json"):
    cliente_dao = ClienteDAO()
    clientes = cliente_dao.listar()
    # Converte date objects para string
    for c in clientes:
        if "data_nasc" in c and c["data_nasc"]:
            c["data_nasc"] = str(c["data_nasc"])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(clientes, f, ensure_ascii=False, indent=2, default=str)


def exportar_seguros_csv(path="seguros_export.csv"):
    seguro_dao = SeguroDAO()
    seguros = seguro_dao.listar()
    if not seguros:
        print("Nenhum seguro para exportar.")
        return
    # Converte Decimal e outros tipos para string
    for s in seguros:
        if "valor" in s and s["valor"]:
            s["valor"] = float(s["valor"])
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=seguros[0].keys())
        writer.writeheader()
        writer.writerows(seguros)


def exportar_seguros_json(path="seguros_export.json"):
    seguro_dao = SeguroDAO()
    seguros = seguro_dao.listar()
    # Converte Decimal para float
    for s in seguros:
        if "valor" in s and s["valor"]:
            s["valor"] = float(s["valor"])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(seguros, f, ensure_ascii=False, indent=2, default=str)


def exportar_apolices_csv(path="apolices_export.csv"):
    apolice_dao = ApoliceDAO()
    apolices = apolice_dao.listar()
    if not apolices:
        print("Nenhuma apólice para exportar.")
        return
    # Converte date objects para string
    for a in apolices:
        if "data_emissao" in a and a["data_emissao"]:
            a["data_emissao"] = str(a["data_emissao"])
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=apolices[0].keys())
        writer.writeheader()
        writer.writerows(apolices)


def exportar_apolices_json(path="apolices_export.json"):
    apolice_dao = ApoliceDAO()
    apolices = apolice_dao.listar()
    # Converte date objects para string
    for a in apolices:
        if "data_emissao" in a and a["data_emissao"]:
            a["data_emissao"] = str(a["data_emissao"])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(apolices, f, ensure_ascii=False, indent=2, default=str)


def exportar_sinistros_csv(path="sinistros_export.csv"):
    sinistro_dao = SinistroDAO()
    sinistros = sinistro_dao.listar()
    if not sinistros:
        print("Nenhum sinistro para exportar.")
        return
    # Converte date objects para string
    for s in sinistros:
        if "data_ocorrencia" in s and s["data_ocorrencia"]:
            s["data_ocorrencia"] = str(s["data_ocorrencia"])
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=sinistros[0].keys())
        writer.writeheader()
        writer.writerows(sinistros)


def exportar_sinistros_json(path="sinistros_export.json"):
    sinistro_dao = SinistroDAO()
    sinistros = sinistro_dao.listar()
    # Converte date objects para string
    for s in sinistros:
        if "data_ocorrencia" in s and s["data_ocorrencia"]:
            s["data_ocorrencia"] = str(s["data_ocorrencia"])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sinistros, f, ensure_ascii=False, indent=2, default=str)


def exportar_todos():
    exportar_clientes_csv()
    exportar_clientes_json()
    exportar_seguros_csv()
    exportar_seguros_json()
    exportar_apolices_csv()
    exportar_apolices_json()
    exportar_sinistros_csv()
    exportar_sinistros_json()
    print("Exportação concluída!")


if __name__ == "__main__":
    exportar_todos()
