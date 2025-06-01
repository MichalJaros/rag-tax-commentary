import requests
import weaviate
import argparse

# Import ready-made functions from ingest_data.py
from ingest_data import get_embedding_cached, TOKENIZER, COLLECTION_NAME, WEAVIATE_HOST, WEAVIATE_PORT


# === CLIENTS AND MODELS CONFIGURATION ===

BIELIK_MODEL = "speakleash/Bielik-11B-v2.3-Instruct-FP8"

# 2) Weaviate – vector database
WV_CLIENT = weaviate.Client(
    url=f"http://{WEAVIATE_HOST}:{WEAVIATE_PORT}"
)
if not WV_CLIENT.is_ready():
    raise RuntimeError(f"Weaviate nieosiągalny pod {WEAVIATE_HOST}:{WEAVIATE_PORT}")

# === BUILDING MESSAGES FOR Bielik ===
SYSTEM_PROMPT = (
    "Jesteś asystentem – ekspertem prawa podatkowego. Masz za zadanie udzielać użytkownikowi wyczerpujących **komentarzy podatkowych** "
    "w oparciu o dostarczony kontekst (fragmenty orzeczeń sądów administracyjnych).\n\n"
    )

def retrieve_passages(question: str, top_k: int = 3):
    emb = get_embedding_cached(question)
    print(f"[DEBUG] embedding vector len: {len(emb)}")  # DEBUG
    res = (
        WV_CLIENT.query
          .get(COLLECTION_NAME, ["sig", "passage"])
          .with_near_vector({"vector": list(emb)})
          .with_limit(top_k)
          .do()
    )
    hits = res["data"]["Get"].get(COLLECTION_NAME, [])
    print(f"[DEBUG] retrieved passages: {hits}")  # DEBUG
    return [(h["sig"], h["passage"]) for h in hits]

def build_messages(user_q: str, retrieved):
    msgs = [{"role":"system","content":SYSTEM_PROMPT}]
    for sig, passage in retrieved:
        msgs.append({"role":"system","content":f"W oparciu o orzeczenie {sig}: „{passage}”"})
    msgs.append({"role":"user","content":user_q})
    print(f"[DEBUG] built messages: {msgs}")  # DEBUG
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
    print(f"[DEBUG] Bielik status_code: {resp.status_code}")  # DEBUG
    print(f"[DEBUG] Bielik raw response: {resp.text}")       # DEBUG
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

def answer_question(q: str):
    retrieved = retrieve_passages(q, top_k=2)
    msgs = build_messages(q, retrieved)
    return query_bielik(msgs)

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Zadaj pytanie")
    parser.add_argument(
        "-q", "--query",
        required=True,
        help="Tekst pytania podatkowego, na które ma odpowiedzieć model"
    )
    args = parser.parse_args()

    ans = answer_question(args.query)
    print(f"[RESULT] {ans}")
