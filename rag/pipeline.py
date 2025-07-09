"""Pipeline for Tax Law Question Answering."""

import argparse
from retriever import WeaviatePassageRetriever
from weaviate_ingest import init_weaviate_client
from llms import build_messages, query_bielik
from config import WEAVIATE_URL, WEAVIATE_CLASS, EMBEDDING_MODEL, TOP_K

def answer_question(question: str, top_k: int = TOP_K):
    client = init_weaviate_client(WEAVIATE_URL)
    retriever = WeaviatePassageRetriever(
        client=client,
        class_name=WEAVIATE_CLASS,
        embedding_model=EMBEDDING_MODEL,
        k=top_k
    )
    retrieved = retriever.retrieve(question, top_k=top_k)
    msgs = build_messages(question, retrieved)
    return query_bielik(msgs)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ask a tax law question.")
    parser.add_argument(
        "-q", "--query",
        required=True,
        help="The tax law question for the model to answer"
    )
    args = parser.parse_args()

    ans = answer_question(args.query)
    print(f"[RESULT] {ans}")

with open("qa_history_log.csv", "a", encoding="utf-8") as f:
    import datetime
    f.write(f'"{datetime.datetime.now().isoformat()}","{args.query}","{ans}"\n')
