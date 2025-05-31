import pandas as pd
import re
from functools import lru_cache
from openai import OpenAI
import weaviate
from transformers import AutoTokenizer

# === CLIENTS AND MODELS CONFIGURATION ===
CLIENT = OpenAI(base_url="http://localhost:8080/v1", api_key="prototyp_v1")
COLLECTION_NAME = "Wyszukiwarka_v1"

TOKENIZER = AutoTokenizer.from_pretrained(
    "ipipan/silver-retriever-base-v1",
    use_fast=True
)

# Weaviate
WEAVIATE_HOST = "localhost"
WEAVIATE_PORT = 8081
WEAVIATE_GRPC = 50051

# Batch size for embeddings and Weaviate insert
BATCH_SIZE = 32

# === TEXT PROCESSING FUNCTIONS ===
LEGAL_REF_PATTERN = re.compile(
    r"(art\.\s*\d+[A-Za-zĄĆĘŁŃÓŚŹŻ]?"
    r"(?:\s*ust\.\s*\d+[A-Za-zĄĆĘŁŃÓŚŹŻ]?)?"
    r"(?:\s*pkt\s*\d+[A-Za-zĄĆĘŁŃÓŚŹŻ]?)?"
    r"(?:\s*lit\.?\s*[A-Za-zĄĆĘŁŃÓŚŹŻ])?"
    r")",
    flags=re.IGNORECASE
)

def merge_legal_reference(text: str) -> str:
    """
    Usuwa spacje wewnątrz odwołań prawnych typu:
    'art. X', 'art. X ust. Y', 'art. X ust. Y pkt Z', 'art. X ust. Y pkt Z lit. W'.
    """
    def _strip_spaces(match: re.Match) -> str:
        return match.group(1).replace(" ", "")
    return LEGAL_REF_PATTERN.sub(_strip_spaces, text)

@lru_cache(maxsize=10_000)
def get_embedding_cached(text: str) -> tuple:
    """
    Removes spaces inside legal references of the forms:
    'art. X', 'art. X ust. Y', 'art. X ust. Y pkt Z', 'art. X ust. Y pkt Z lit. W'.
    """
    response = CLIENT.embeddings.create(
        input=["</s>" + text],
        model="ipipan/silver-retriever-base-v1"
    )
    return tuple(response.data[0].embedding)

def batch_embeddings(texts: list[str], client: OpenAI, model: str = "ipipan/silver-retriever-base-v1") -> list[tuple]:
    """
    Returns the embedding for a given text, caching the results.
    """
    embeddings = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i: i + BATCH_SIZE]
        response = client.embeddings.create(
            input=batch,
            model=model
        )
        embeddings.extend(tuple(item.embedding) for item in response.data)
    return embeddings

def insert_bulk_weaviate(client, records: list[dict], embeddings: list[tuple], batch_size: int = BATCH_SIZE):
    """
    Sends a list of texts in batches of size BATCH_SIZE and returns the list of embeddings.
    """
    batch = client.batch
    batch.batch_size = batch_size
    for rec, vec in zip(records, embeddings):
        batch.add_data_object(
            data_object=rec,
            class_name=COLLECTION_NAME,
            vector=list(vec)
        )
    batch.flush()

def main():
    # 1) Load CSV and metadata
    path = 'interpretacje_prototyp.csv'
    df = pd.read_csv(path)
    df = (df[['Treść:', 'Sygnatura:']]
          .dropna()
          .rename(columns={'Treść:': 'text', 'Sygnatura:': 'sig'}))

    # 2) Clean text
    df['text_clean'] = df['text'].apply(merge_legal_reference)

    # 3) Chunk into max 500 tokens + overlap 128 – without manual encode/decode
    max_len = 500
    overlap = 128

    def make_passages(text: str) -> list[str]:
        enc = TOKENIZER(
            text,
            add_special_tokens=False,
            truncation=True,
            max_length=max_len,
            stride=overlap,
            return_overflowing_tokens=True
        )
        # now decode each chunk back to text:
        return [
            TOKENIZER.decode(token_ids, skip_special_tokens=True)
            for token_ids in enc['input_ids']
        ]

    df['passages'] = df['text_clean'].apply(make_passages)

    # 4) Prepare list of records for batching
    records = []
    for _, row in df.iterrows():
        for passage_text in row['passages']:
            records.append({
                'sig': row['sig'],
                'text': row['text'],
                'passage': passage_text
            })

    # 5) Batch embedding
    all_passages = [rec['passage'] for rec in records]
    embeddings = batch_embeddings(all_passages, CLIENT)

    # 6) Ingest into Weaviate (v4 client)
    client = weaviate.Client(
        url=f"http://{WEAVIATE_HOST}:{WEAVIATE_PORT}"
    )
    if not client.is_ready():
        raise RuntimeError(f"Weaviate nie jest osiągalny pod {WEAVIATE_HOST}:{WEAVIATE_PORT}")

    # retrieve current schema
    schema = client.schema.get()
    existing = [c["class"] for c in schema.get("classes", [])]

    if COLLECTION_NAME not in existing:
        class_obj = {
            "class": COLLECTION_NAME,
            "vectorIndexConfig": {
                "distance": "cosine",
                "cleanupIntervalSeconds": 300
            },
            "properties": [
                {"name": "sig", "dataType": ["string"]},
                {"name": "text", "dataType": ["text"]},
                {"name": "passage", "dataType": ["text"]}
            ]
        }
        client.schema.create_class(class_obj)

    insert_bulk_weaviate(client, records, embeddings)

    # 7) Summary — aggregation in v4:
    result = (
        client.query
        .aggregate(COLLECTION_NAME)
        .with_meta_count()
        .do()
    )
    count = result["data"]["Aggregate"][COLLECTION_NAME][0]["meta"]["count"]
    print(f"Zaindeksowano fragmentów: {count}")

if __name__ == '__main__':
    main()
