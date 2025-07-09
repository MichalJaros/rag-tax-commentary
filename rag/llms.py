"""LLM and prompt configuration for tax assistant."""

import requests
from config import BIELIK_MODEL, BIELIK_SERVER_URL

SYSTEM_PROMPT = (
    "Jesteś asystentem – ekspertem prawa podatkowego. Masz za zadanie udzielać użytkownikowi wyczerpujących **komentarzy podatkowych** "
    "w oparciu o dostarczony kontekst (fragmenty orzeczeń sądów administracyjnych).\n\n"
)

def build_messages(user_q: str, retrieved):
    msgs = [{"role":"system","content":SYSTEM_PROMPT}]
    for sig, passage in retrieved:
        msgs.append({"role":"system","content":f"W oparciu o orzeczenie {sig}: „{passage}”"})
    msgs.append({"role":"user","content":user_q})
    return msgs

def query_bielik(messages):
    payload = {
        "model": BIELIK_MODEL,
        "messages": messages,
        "temperature": 0.2,
        "top_p": 0.95,
        "max_tokens": 32768,
        "stop": None
    }
    resp = requests.post(
         f"{BIELIK_SERVER_URL}/v1/chat/completions",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]
