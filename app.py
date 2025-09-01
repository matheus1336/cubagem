from flask import Flask, render_template, request, jsonify
import pandas as pd
import re

app = Flask(__name__)

# Tabela de caixas disponíveis
caixas = [
    {"nome": "Caixa 12TP", "capacidade": 2.0},
    {"nome": "Caixa 15TP", "capacidade": 5.0},
    {"nome": "Caixa 19TP", "capacidade": 10.0},
]

def norm_code(x):
    s = str(x).strip()
    if s.endswith(".0"):
        s = s[:-2]
    return s

def to_float(x):
    if pd.isna(x):
        return 0.0
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).strip().replace(" ", "").replace(",", ".")
    m = re.search(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', s)
    return float(m.group(0)) if m else 0.0

def carregar_dados():
    df = pd.read_excel("produtos.xlsx")
    df = df.rename(columns={
        "Código": "Codigo",
        "C\u00f3digo": "Codigo",
        "M3": "m3_total",
        "m³": "m3_total",
        "m3": "m3_total",
        "Peso (kg)": "Peso",
        "peso": "Peso",
        "PESO": "Peso",
    })
    if "Codigo" not in df.columns:
        raise ValueError("A planilha precisa ter a coluna 'Codigo'.")
    df["Codigo"] = df["Codigo"].apply(norm_code)
    for col in ["Comprimento", "Largura", "Altura", "m3_total", "Peso"]:
        if col in df.columns:
            df[col] = df[col].apply(to_float)
    if "m3_total" not in df.columns:
        df["m3_total"] = (df["Comprimento"] * df["Largura"] * df["Altura"]) / 1_000_000
    if "Peso" not in df.columns:
        df["Peso"] = 0.0
    return df

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/buscar", methods=["GET"])
def buscar():
    termo = request.args.get("q", "").lower()
    df = carregar_dados()
    mask = df.apply(lambda r: termo in str(r.get("Codigo","")).lower() or termo in str(r.get("Nome","")).lower(), axis=1)
    out = df.loc[mask, ["Codigo", "Nome", "m3_total", "Peso", "Comprimento", "Largura", "Altura"]].copy()

    registros = []
    for _, row in out.iterrows():
        registros.append({
            "Codigo": row["Codigo"],
            "Nome": str(row.get("Nome", "")),
            "Comprimento": float(row.get("Comprimento", 0.0)),
            "Largura": float(row.get("Largura", 0.0)),
            "Altura": float(row.get("Altura", 0.0)),
            "m3_total": float(row.get("m3_total", 0.0)),
            "Peso": float(row.get("Peso", 0.0)),
        })
    return jsonify(registros)

@app.route("/cubagem", methods=["POST"])
def cubagem():
    itens = request.json.get("itens", [])
    item_set = {norm_code(x) for x in itens}
    df = carregar_dados()
    selecionados = df[df["Codigo"].isin(item_set)]

    volume_total = float(selecionados["m3_total"].sum())
    peso_total = float(selecionados["Peso"].sum())

    caixas_possiveis = [
        {"nome": c["nome"], "capacidade": float(c["capacidade"])}
        for c in caixas if c["capacidade"] >= volume_total
    ]

    itens_lista = []
    for _, row in selecionados.iterrows():
        itens_lista.append({
            "Codigo": row["Codigo"],
            "Nome": str(row.get("Nome", "")),
            "Comprimento": float(row.get("Comprimento", 0.0)),
            "Largura": float(row.get("Largura", 0.0)),
            "Altura": float(row.get("Altura", 0.0)),
            "m3_total": float(row.get("m3_total", 0.0)),
            "Peso": float(row.get("Peso", 0.0)),
        })

    return jsonify({
        "itens_encontrados": int(selecionados.shape[0]),
        "volume_total": volume_total,
        "peso_total": peso_total,
        "caixas": caixas_possiveis,
        "itens": itens_lista   # <-- corrigido para coincidir com o front
    })

if __name__ == "__main__":
    app.run(debug=True)
