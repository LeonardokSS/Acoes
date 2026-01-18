import requests
import time
# ========================================================
# CONFIGURAÇÕES
# ========================================================
TELEGRAM_TOKEN = "7974684858:AAFeU_cb0_kyijadOBMPSZKamALFoyBPQXg"
CHAT_ID = "6632450212"


session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})
TIMEOUT = 8


# ========================================================
# YAHOO FINANCE
# ========================================================
def pegar_yahoo(simbolo):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{simbolo}?interval=1m"

    try:
        r = session.get(url, timeout=TIMEOUT)
        r.raise_for_status()
        result = r.json()["chart"]["result"]

        if not result:
            return None

        meta = result[0]["meta"]
        atual = meta.get("regularMarketPrice")
        anterior = meta.get("chartPreviousClose")

        if atual is None or anterior is None:
            return None

        return montar_dados(
            simbolo,
            atual,
            anterior,
            meta.get("currency", "N/A"),
            meta.get("exchangeName", "N/A")
        )

    except (requests.RequestException, KeyError, ValueError):
        return None





# ========================================================
# FUNÇÃO AUXILIAR
# ========================================================
def montar_dados(simbolo, atual, anterior, moeda="USD", exchange="N/A"):
    variacao = atual - anterior
    variacao_percent = (variacao / anterior) * 100 if anterior else 0

    return {
        "simbolo": simbolo,
        "preco_atual": atual,
        "preco_anterior": anterior,
        "variacao": variacao,
        "variacao_percent": variacao_percent,
        "moeda": moeda,
        "exchange": exchange
    }


# ========================================================
# TELEGRAM
# ========================================================
def telegram_enviar(texto):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    session.post(
        url,
        json={
            "chat_id": CHAT_ID,
            "text": texto,
            "parse_mode": "Markdown"
        },
        timeout=TIMEOUT
    )


# ========================================================
# RELATÓRIO
# ========================================================
def enviar_relatorio(simbolos_yahoo):
    linhas = ["📊 *Relatório de Ações*\n"]

    for s in simbolos_yahoo:
        d = pegar_yahoo(s)
        linhas.append(formatar_linha(d, fonte="Yahoo"))

    telegram_enviar("\n".join(linhas))


def formatar_linha(dados, fonte):
    if not dados:
        return f"❌ Erro ao buscar dados ({fonte})\n"

    return (
        f"▶ *{dados['simbolo']}* ({fonte})\n"
        f"Preço: {dados['preco_atual']}\n"
        f"Anterior: {dados['preco_anterior']}\n"
        f"Variação: {dados['variacao']:.2f} ({dados['variacao_percent']:.2f}%)\n"
    )


# ========================================================
# EXECUÇÃO
# ========================================================
if __name__ == "__main__":
    enviar_relatorio(
        simbolos_yahoo = [
    "ITUB4.SA", "BBAS3.SA", "BBSE3.SA", "WEGE3.SA",
    "AAPL", "MSFT", "NVDA", "AMD", "IBM"]
    )
