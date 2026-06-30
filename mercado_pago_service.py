import os
import requests
import urllib3
from dotenv import load_dotenv

load_dotenv()

MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")
SITE_URL = os.getenv("SITE_URL", "http://127.0.0.1:5000")

APP_ENV = os.getenv("APP_ENV", "development")
VERIFY_SSL = os.getenv("VERIFY_SSL", "true").lower() == "true"

# Segurança: não permitir produção com SSL desligado
if APP_ENV == "production" and VERIFY_SSL is False:
    raise RuntimeError(
        "Configuração insegura: VERIFY_SSL=false não pode ser usado em produção."
    )

# Apenas para ambiente local, por causa do erro SSL no Windows
if VERIFY_SSL is False:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def criar_preferencia_pagamento(
    id_inscricao,
    nome_completo,
    email,
    valor_inscricao,
    valor_camisa,
    valor_total,
    quer_camisa,
    tamanho_camisa
):
    if not MP_ACCESS_TOKEN:
        raise RuntimeError("MP_ACCESS_TOKEN não configurado no .env")

    itens = [
        {
            "title": "Inscrição EMEERJ 2026",
            "quantity": 1,
            "currency_id": "BRL",
            "unit_price": float(valor_inscricao)
        }
    ]

    if quer_camisa == "Sim":
        itens.append({
            "title": f"Camisa EMEERJ 2026 - Tamanho {tamanho_camisa}",
            "quantity": 1,
            "currency_id": "BRL",
            "unit_price": float(valor_camisa)
        })

    dados = {
        "items": itens,

        "payer": {
            "name": nome_completo,
            "email": email
        },

        # Esse campo liga o pagamento ao ID da inscrição no SQLite
        "external_reference": str(id_inscricao)
    }

    # O Mercado Pago exige HTTPS em back_urls.
    # Em desenvolvimento local, com http://127.0.0.1:5000, não enviamos back_urls.
    if SITE_URL.startswith("https://"):
        dados["back_urls"] = {
            "success": f"{SITE_URL}/pagamento/sucesso",
            "failure": f"{SITE_URL}/pagamento/falha",
            "pending": f"{SITE_URL}/pagamento/pendente"
        }

        dados["auto_return"] = "approved"

    resposta = requests.post(
        "https://api.mercadopago.com/checkout/preferences",
        headers={
            "Authorization": f"Bearer {MP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        },
        json=dados,
        timeout=20,
        verify=VERIFY_SSL
    )

    if not resposta.ok:
        print("Erro Mercado Pago:")
        print("Status:", resposta.status_code)
        print("Resposta:", resposta.text)

    resposta.raise_for_status()

    resposta_json = resposta.json()

    if MP_ACCESS_TOKEN.startswith("TEST-"):
        link_pagamento = resposta_json.get("sandbox_init_point")
    else:
        link_pagamento = resposta_json.get("init_point")

    if not link_pagamento:
        raise RuntimeError("Mercado Pago não retornou link de pagamento.")

        if not link_pagamento:
            raise RuntimeError("Mercado Pago não retornou link de pagamento.")

    return {
        "id_preferencia": resposta_json.get("id"),
        "link_pagamento": link_pagamento
    }