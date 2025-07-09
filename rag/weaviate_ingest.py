"""Utility functions for Weaviate vectorstore ingest and management."""

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Weaviate
import weaviate

def init_weaviate_client(weaviate_url: str) -> weaviate.Client:
    """
    Creates and returns a Weaviate client (compatible with langchain).
    """
    client = weaviate.Client(weaviate_url)
    if not client.is_ready():
        raise RuntimeError(f"Weaviate is not responding at {weaviate_url}")
    return client

def ensure_weaviate_class(client, class_name: str):
    """
    Checks if a class exists in Weaviate; if not, creates it.
    """
    schema = client.schema.get()
    existing_classes = [c["class"] for c in schema.get("classes", [])]
    if class_name not in existing_classes:
        class_obj = {
            "class": class_name,
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

def get_embeddings(model_name: str = "ipipan/silver-retriever-base-v1"):
    """
    Returns a HuggingFace embedding object (using GPU if available).
    """
    return HuggingFaceEmbeddings(model_name=model_name, model_kwargs={"device": "cuda"})

def ingest_documents_to_weaviate(
    client,
    class_name: str,
    split_docs: list,
    embeddings
):
    """
    Indexes documents in Weaviate (using LangChain Vectorstore).
    """
    vectorstore = Weaviate(
        client=client,
        index_name=class_name,
        text_key="passage",
        embedding=embeddings
    )
    vectorstore.add_documents(split_docs)

def count_indexed_chunks(client, class_name: str) -> int:
    """
    Returns the number of indexed chunks in the specified Weaviate class.
    """
    result = (
        client.query
        .aggregate(class_name)
        .with_meta_count()
        .do()
    )
    try:
        agg = result["data"]["Aggregate"][class_name]
        if agg:
            return agg[0]["meta"]["count"]
        else:
            return 0
    except Exception:
        return 0
