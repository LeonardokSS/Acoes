import requests
import time

# ========================================================
# CONFIG"URAÇÕES
# ========================================================
TELEGRAM_TOKEN = "7974684858:AAFeU_cb0_kyijadOBMPSZKamALFoyBPQXg"
CHAT_ID = "6632450212"
ALPHAVANTAGE_KEY = "AZGZNM5OXWQIHOCG"

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})


# ========================================================
# FUNÇÃO: PEGAR PREÇO NO YAHOO FINANCE
# ========================================================
def pegar_yahoo(simbolo):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{simbolo}?interval=1m"

    try:
        resp = session.get(url, timeout=8)
        resp.raise_for_status()
        data = resp.json()

        result = data["chart"]["result"]
        if not result:
            return None

        meta = result[0]["meta"]

        preco_atual = meta.get("regularMarketPrice")
        preco_anterior = meta.get("chartPreviousClose")

        if preco_atual is None or preco_anterior is None:
            return None

        variacao = preco_atual - preco_anterior
        variacao_percent = (variacao / preco_anterior) * 100

        return {
            "simbolo": simbolo,
            "preco_atual": preco_atual,
            "preco_anterior": preco_anterior,
            "variacao": variacao,
            "variacao_percent": variacao_percent,
            "moeda": meta.get("currency", "N/A"),
            "exchange": meta.get("exchangeName", "N/A")
        }

    except:
        return None


# ========================================================
# FUNÇÃO: PEGAR PREÇO NO ALPHAVANTAGE
# ========================================================
def pegar_alpha(simbolo):
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={simbolo}&apikey={ALPHAVANTAGE_KEY}"

    try:
        resp = session.get(url, timeout=8)
        resp.raise_for_status()
        data = resp.json()

        q = data.get("Global Quote")
        if not q:
            return None

        preco_atual = float(q.get("05. price", 0))
        preco_anterior = float(q.get("08. previous close", 0))

        variacao = preco_atual - preco_anterior
        variacao_percent = (variacao / preco_anterior) * 100 if preco_anterior else 0

        return {
            "simbolo": simbolo,
            "preco_atual": preco_atual,
            "preco_anterior": preco_anterior,
            "variacao": variacao,
            "variacao_percent": variacao_percent
        }

    except:
        return None


# ========================================================
# ENVIAR TEXTO PARA TELEGRAM
# ========================================================
def telegram_enviar(texto):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": texto})


# ========================================================
# FUNÇÃO PRINCIPAL
# ========================================================
def enviar_relatorio(simbolos_yahoo, simbolos_alpha):

    linhas = []

    linhas.append("📊 *Relatório de Ações*\n")

    # Yahoo
    for s in simbolos_yahoo:
        d = pegar_yahoo(s)
        if d:
            linhas.append(
                f"▶ {d['simbolo']} ({d['moeda']})\n"
                f"Preço atual: {d['preco_atual']}\n"
                f"Anterior: {d['preco_anterior']}\n"
                f"Variação: {d['variacao']:.2f} ({d['variacao_percent']:.2f}%)\n"
            )
        else:
            linhas.append(f"▶ {s}: erro ao buscar no Yahoo.\n")

    # AlphaVantage
    for s in simbolos_alpha:
        d = pegar_alpha(s)
        if d:
            linhas.append(
                f"◆ {d['simbolo']} (Alpha)\n"
                f"Preço atual: {d['preco_atual']}\n"
                f"Anterior: {d['preco_anterior']}\n"
                f"Variação: {d['variacao']:.2f} ({d['variacao_percent']:.2f}%)\n"
            )
        else:
            linhas.append(f"◆ {s}: erro ao buscar no AlphaVantage.\n")

    texto = "\n".join(linhas)
    telegram_enviar(texto)


# ========================================================
# EXEMPLO DE USO
# ========================================================
if __name__ == "__main__":
    enviar_relatorio(
        simbolos_yahoo=["ITUB4.SA", "BBAS3.SA", "BBSE3.SA","WEGE3"],
        simbolos_alpha=["IBM", "AMD","NVDA","MSFT"]
    )
