"""Retriever for legal tax Q&A using Weaviate and LangChain."""

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Weaviate
from config import EMBEDDING_MODEL

class WeaviatePassageRetriever:
    """
    Retriever to search for top-k passages in Weaviate using embedding similarity (LangChain).
    """
    def __init__(
        self,
        client,
        class_name,
        embedding_model=EMBEDDING_MODEL,
        k=3
    ):
        self.vectorstore = Weaviate(
            client=client,
            index_name=class_name,
            text_key="passage",
            embedding=HuggingFaceEmbeddings(model_name=embedding_model, model_kwargs={"device": "cuda"}),
            by_text=False
        )
        self.k = k

    def retrieve(self, query: str, top_k: int = None):
        k = top_k or self.k
        docs = self.vectorstore.similarity_search(query, k=k)
        return [
            (doc.metadata.get("sig", ""), doc.page_content)
            for doc in docs
        ]
