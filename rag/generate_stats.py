# generate_stats.py

import time
import csv
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter, defaultdict
from retriever import WeaviatePassageRetriever
from weaviate_ingest import init_weaviate_client
from llms import build_messages, query_bielik
from config import WEAVIATE_URL, WEAVIATE_CLASS, EMBEDDING_MODEL, TOP_K

LOG_FILE = "qa_history_log.csv"

def read_questions_from_log(logfile=LOG_FILE):
    questions = []
    with open(logfile, encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) > 1:
                questions.append(row[1])
    # return only unique, preserve order
    return list(dict.fromkeys(questions))

def main():
    questions = read_questions_from_log()
    if not questions:
        print("No questions found in the log file. Make sure you've asked some questions via pipeline.py.")
        return

    client = init_weaviate_client(WEAVIATE_URL)
    retriever = WeaviatePassageRetriever(client, WEAVIATE_CLASS, EMBEDDING_MODEL, k=TOP_K)

    qna_history = []
    chunk_counter = Counter()
    chunk_len_hist = []
    retrieval_times = []
    llm_times = []
    chunk_stats = defaultdict(list)
    embedding_distances = []

    for q in questions:
        # --- Retrieval ---
        t0 = time.time()
        docs = retriever.vectorstore.similarity_search(q, k=TOP_K)
        retrieval_time = time.time() - t0
        retrieval_times.append(retrieval_time)

        # --- Prepare for LLM ---
        retrieved_for_llm = [(doc.metadata.get("sig", ""), doc.page_content) for doc in docs]
        msgs = build_messages(q, retrieved_for_llm)

        # --- LLM (Bielik) ---
        t1 = time.time()
        try:
            answer = query_bielik(msgs)
        except Exception as e:
            answer = f"[ERROR calling LLM]: {e}"
        llm_time = time.time() - t1
        llm_times.append(llm_time)

        # --- Collect retrieved chunks info ---
        retrieved_list = []
        for doc in docs:
            sig = doc.metadata.get("sig", "")
            passage = doc.page_content
            chunk_counter[sig] += 1
            chunk_len_hist.append(len(passage))
            chunk_stats[sig].append(len(passage))
            score = doc.metadata.get("score", None)
            retrieved_list.append({
                "sig": sig,
                "passage": passage[:300],  # Only first 300 chars for report
                "score": score,
                "length": len(passage),
            })
            # (Optional) Embedding distance if API available
            try:
                query_emb = retriever.vectorstore.embedding.embed_query(q)
                doc_emb = retriever.vectorstore.embedding.embed_documents([doc.page_content])[0]
                dist = np.linalg.norm(np.array(query_emb) - np.array(doc_emb))
                embedding_distances.append(dist)
            except Exception:
                pass

        qna_history.append({
            "question": q,
            "retrieved": retrieved_list,
            "retrieval_time": retrieval_time,
            "llm_time": llm_time,
            "answer": answer,
        })

    # --- Write Q&A history to markdown ---
    with open("retrieval_report.md", "w", encoding="utf-8") as f:
        f.write("# Q&A History and Retrieval Stats\n\n")
        for entry in qna_history:
            f.write(f"## Q: {entry['question']}\n")
            f.write(f"- Retrieval time: {entry['retrieval_time']:.3f}s\n")
            f.write(f"- LLM answer time: {entry['llm_time']:.3f}s\n")
            for i, doc in enumerate(entry['retrieved'], 1):
                f.write(f"  - Top {i}: Sig: {doc['sig']} | Len: {doc['length']}\n")
                f.write(f"    Passage: {doc['passage']}\n")
                if doc['score'] is not None:
                    f.write(f"    Similarity score: {doc['score']}\n")
            f.write(f"\n### Model answer:\n{entry['answer']}\n\n")

    # --- Write most frequent chunks to CSV ---
    with open("chunk_ranking.csv", "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["sig", "hits", "avg_length"])
        for sig, count in chunk_counter.most_common(20):
            avg_len = np.mean(chunk_stats[sig]) if chunk_stats[sig] else 0
            writer.writerow([sig, count, int(avg_len)])

    # --- Plot histogram of chunk lengths ---
    plt.figure(figsize=(7,4))
    plt.hist(chunk_len_hist, bins=40)
    plt.title("Histogram of Chunk Lengths")
    plt.xlabel("Chunk Length (characters)")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig("chunk_length_hist.png")

    # --- Plot histogram of retrieval times ---
    plt.figure(figsize=(6,3))
    plt.hist(retrieval_times, bins=15)
    plt.title("Histogram of Retrieval Times")
    plt.xlabel("Time [s]")
    plt.ylabel("Number of queries")
    plt.tight_layout()
    plt.savefig("retrieval_times_hist.png")

    # --- Plot histogram of LLM times ---
    plt.figure(figsize=(6,3))
    plt.hist(llm_times, bins=15)
    plt.title("Histogram of LLM Answer Times")
    plt.xlabel("Time [s]")
    plt.ylabel("Number of queries")
    plt.tight_layout()
    plt.savefig("llm_times_hist.png")

    # --- Plot histogram of embedding distances (if available) ---
    if embedding_distances:
        plt.figure(figsize=(7,3))
        plt.hist(embedding_distances, bins=20)
        plt.title("Histogram of Query-Chunk Embedding Distances")
        plt.xlabel("L2 Distance")
        plt.ylabel("Count")
        plt.tight_layout()
        plt.savefig("embedding_distances_hist.png")

    # --- Write summary markdown for README ---
    with open("retrieval_stats_summary.md", "w", encoding="utf-8") as f:
        f.write("# RAG Pipeline Statistics\n\n")
        f.write(f"- Number of questions: {len(questions)}\n")
        f.write(f"- Number of unique chunks retrieved: {len(chunk_counter)}\n")
        f.write(f"- Avg. retrieval time: {np.mean(retrieval_times):.3f}s\n")
        f.write(f"- Avg. LLM answer time: {np.mean(llm_times):.3f}s\n")
        if embedding_distances:
            f.write(f"- Avg. embedding L2 distance: {np.mean(embedding_distances):.3f}\n")
        f.write("\n![Chunk Lengths](chunk_length_hist.png)\n")
        f.write("\n![Retrieval Times](retrieval_times_hist.png)\n")
        f.write("\n![LLM Times](llm_times_hist.png)\n")
        if embedding_distances:
            f.write("\n![Embedding Distances](embedding_distances_hist.png)\n")

        f.write("\n## Top retrieved chunks\n")
        f.write("| Sig | Retrieval count | Avg. length |\n")
        f.write("|-----|----------------|-------------|\n")
        for sig, count in chunk_counter.most_common(20):
            avg_len = np.mean(chunk_stats[sig]) if chunk_stats[sig] else 0
            f.write(f"| {sig} | {count} | {int(avg_len)} |\n")

    print("Stats generated: retrieval_report.md, chunk_ranking.csv, chunk_length_hist.png, retrieval_times_hist.png, llm_times_hist.png, retrieval_stats_summary.md")
    if embedding_distances:
        print("  + embedding_distances_hist.png")

if __name__ == "__main__":
    main()
