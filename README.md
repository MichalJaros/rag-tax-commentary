[English version below](#english-version-below)

# Projekt RAG (Retriever-Augmented Generation)
**rag-tax-commentary**

Zaawansowany system Retrieval-Augmented Generation do automatycznego generowania komentarzy podatkowych na podstawie interpretacji indywidualnych, wykorzystujący **LangChain**, model **Bielik LLM** oraz bazę wektorową **Weaviate**.

---

## Spis treści
- [Cel projektu](#cel-projektu)
- [Technologie](#technologie)
- [Przykład użycia](#przykład-użycia)
- [Automatyczna analiza statystyk i raportowanie](#automatyczna-analiza-statystyk-i-raportowanie)
- [Struktura repozytorium](#struktura-repozytorium)
- [Kontakt](#kontakt)

---

## Cel projektu

Celem projektu jest stworzenie narzędzia, które na podstawie interpretacji podatkowych potrafi w zrozumiały sposób odpowiadać na pytania dotyczące prawa podatkowego. System automatycznie wyszukuje najtrafniejsze fragmenty interpretacji (retrieval), a następnie generuje precyzyjne komentarze podatkowe z użyciem dużego modelu językowego (Bielik LLM). Pipeline korzysta z nowoczesnych frameworków **LangChain** oraz **Weaviate**.

---

## Technologie

- **Python 3.12+**
- **[LangChain](https://python.langchain.com/)** — framework do budowy pipeline’ów RAG, zarządzania przepływem danych (retriever, LLM, monitoring, analizy)
- **[Weaviate](https://weaviate.io/)** — baza danych wektorowych (przechowuje zakodowane fragmenty interpretacji, umożliwia wyszukiwanie semantyczne)
- **[HuggingFace Transformers](https://huggingface.co/docs/transformers/)** — embeddingi tekstów do przestrzeni wektorowej
- **Bielik LLM** — polskojęzyczny model generatywny (REST API)
- **pandas** — przetwarzanie i czyszczenie danych
- **numpy** — operacje matematyczne/statystyczne
- **matplotlib** — generowanie wykresów (histogramy, itp.)
- **requests** — komunikacja HTTP z serwerem Bielik
- **re** — zaawansowane operacje tekstowe (regex)
- **dotenv** — obsługa zmiennych środowiskowych
- **Docker** — uruchamianie serwera embeddingowego i bazy Weaviate

**Pliki:**
- [csv_document_loader.py](rag/csv_document_loader.py) — ładowanie i chunkowanie danych CSV
- [weaviate_ingest.py](rag/weaviate_ingest.py) — indeksowanie dokumentów, zarządzanie schematem i połączenie z bazą Weaviate
- [retriever.py](rag/retriever.py) — retriever oparty na LangChain (wyszukiwanie najbardziej relewantnych fragmentów)
- [llms.py](rag/llms.py) — komunikacja i budowa promptów dla Bielik LLM
- [pipeline.py](rag/pipeline.py) — główny pipeline RAG (terminal)
- [generate_stats.py](rag/generate_stats.py) — automatyczna analiza, zbieranie statystyk i generowanie raportów/wykresów na podstawie realnych pytań

---

## Przykład użycia

Prototyp systemu obejmuje ~4500 interpretacji podatkowych.  
Obecna wersja **nie posiada interfejsu webowego** – pytania zadawane są w terminalu.

1. **Uruchom wymagane serwery** (Weaviate, Bielik LLM, embedding server) – zgodnie z dokumentacją lub dockerami.
2. **Dodaj dane (CSV)** i zaindeksuj je do bazy Weaviate (jeśli nie masz jeszcze bazy).
3. **Zadaj pytanie w terminalu** (przykład):

    ```bash
    python pipeline.py -q "Czy można zaliczyć pensje inżynierów do ulgi na działalność badawczo-rozwojową?"
    ```

![Przykład](images/image1.png)

Odpowiedź pojawi się w terminalu oraz zostanie zapisana do logu (`qa_history_log.csv`).

4. **Po zadaniu serii pytań** możesz wygenerować statystyki, ranking chunków i automatyczne raporty do README:

    ```bash
    python generate_stats.py
    ```

    W katalogu pojawią się m.in.: `retrieval_report.md`, `chunk_ranking.csv`, `chunk_length_hist.png`, `retrieval_stats_summary.md`.

---

## Automatyczna analiza statystyk i raportowanie

- **System loguje każde pytanie i odpowiedź** do pliku `qa_history_log.csv`
- **[generate_stats.py](rag/generate_stats.py)** analizuje rzeczywistą historię zapytań:
    - Liczbę i długość chunków
    - Ranking najczęściej przywoływanych fragmentów
    - Czasy odpowiedzi
    - Histogramy, rozkład embeddingów, itp.
    - Gotowe raporty Markdown do README lub prezentacji

**Przykładowe raporty/statystyki znajdziesz w plikach:**
- [retrieval_report.md](rag/retrieval_report.md)
- [retrieval_stats_summary.md](rag/retrieval_stats_summary.md)
- [chunk_ranking.csv](rRg/chunk_ranking.csv)

---

## Struktura repozytorium

Ze względu na ograniczenia dotyczące rozmiaru plików na GitHub, repozytorium nie zawiera bazy wektorowej ani pliku CSV z tekstami interpretacji.

```
repo_root/
│
├── bielik_aws_deploy/
│   ├── Requirements.txt
│   ├── Run_bielik.sh
│   └── Server.py
│
├── Rag/
│   ├── dockerfiles/
│   │   └── Run_vector_db.sh
│   ├── csv_document_loader.py
│   ├── weaviate_ingest.py
│   ├── retriever.py
│   ├── llms.py
│   ├── pipeline.py
│   ├── generate_stats.py
│   ├── config.py
│   ├── retrieval_report.md
│   └── retrieval_stats_summary.md
│├── images/
│   └── image1.png
└── README.md
```
## Kontakt

Projekt na licencji otwartej.  
Zapraszam do współpracy:  
- [LinkedIn: Michał Jaros](https://www.linkedin.com/in/michał-jaros-88572821a/)  
- E-mail: michal.marek.jaros@gmail.com

[English version below](#english-version-below)

# RAG Project (Retriever-Augmented Generation)
**rag-tax-commentary**

An advanced Retrieval-Augmented Generation system for automatic tax commentary generation based on individual tax rulings, utilizing **LangChain**, the **Bielik LLM** model, and the **Weaviate** vector database.

---

## Table of Contents
- [Project Goal](#project-goal)
- [Technologies](#technologies)
- [Usage Example](#usage-example)
- [Automatic Statistics Analysis and Reporting](#automatic-statistics-analysis-and-reporting)
- [Repository Structure](#repository-structure)
- [Contact](#contact)

---

## Project Goal

The aim of this project is to create a tool that, based on tax interpretations, can answer questions regarding tax law in an understandable way. The system automatically retrieves the most relevant fragments (retrieval) and then generates precise tax commentaries using a large language model (Bielik LLM). The pipeline uses modern frameworks such as **LangChain** and **Weaviate**.

---

## Technologies

- **Python 3.12+**
- **[LangChain](https://python.langchain.com/)** — framework for building RAG pipelines, managing data flow (retriever, LLM, monitoring, analytics)
- **[Weaviate](https://weaviate.io/)** — vector database (stores encoded document fragments, enables semantic search)
- **[HuggingFace Transformers](https://huggingface.co/docs/transformers/)** — for text embeddings into vector space
- **Bielik LLM** — Polish-language generative model (REST API)
- **pandas** — data processing and cleaning
- **numpy** — mathematical/statistical operations
- **matplotlib** — generating plots (histograms, etc.)
- **requests** — HTTP communication with Bielik server
- **re** — advanced text operations (regex)
- **dotenv** — environment variable handling
- **Docker** — for running the embedding server and Weaviate database

**Files:**
- [csv_document_loader.py](Rag/csv_document_loader.py) — CSV data loading and chunking
- [weaviate_ingest.py](Rag/weaviate_ingest.py) — document indexing, schema management, and Weaviate connection
- [retriever.py](Rag/retriever.py) — LangChain-based retriever (searching for most relevant fragments)
- [llms.py](Rag/llms.py) — prompt building and Bielik LLM communication
- [pipeline.py](Rag/pipeline.py) — main RAG pipeline (terminal)
- [generate_stats.py](Rag/generate_stats.py) — automatic analysis, statistics gathering, and report/plot generation based on real user questions

---

## Usage Example

The system prototype includes ~4500 tax rulings.  
The current version **does not have a web interface** – questions are asked in the terminal.

1. **Start the required servers** (Weaviate, Bielik LLM, embedding server) — as described in documentation or Docker scripts.
2. **Add data (CSV)** and index it into Weaviate (if you do not have a vector DB yet).
3. **Ask a question in the terminal** (example):

    ```bash
    python pipeline.py -q "Can engineer salaries be included in the R&D tax relief?"
    ```

![Example](images/image1.png)

The answer will appear in the terminal and will also be saved to the log (`qa_history_log.csv`).

4. **After asking a series of questions**, you can generate statistics, chunk rankings, and automatic reports for the README:

    ```bash
    python generate_stats.py
    ```

    The following files will appear in the directory: `retrieval_report.md`, `chunk_ranking.csv`, `chunk_length_hist.png`, `retrieval_stats_summary.md`, etc.

---

## Automatic Statistics Analysis and Reporting

- **The system logs every question and answer** to `qa_history_log.csv`
- **[generate_stats.py](Rag/generate_stats.py)** analyzes the actual query history:
    - Number and length of chunks
    - Ranking of the most frequently retrieved fragments
    - Response times
    - Histograms, embedding distribution, etc.
    - Ready-made Markdown reports for the README or presentations

**Sample reports/statistics can be found in:**
- [retrieval_report.md](Rag/retrieval_report.md)
- [retrieval_stats_summary.md](Rag/retrieval_stats_summary.md)
- [chunk_ranking.csv](Rag/chunk_ranking.csv)

---

## Repository Structure

Due to GitHub's file size limitations, the repository does **not** include the vector database or the CSV file with raw text interpretations.

```
repo_root/
│
├── bielik_aws_deploy/
│   ├── Requirements.txt
│   ├── Run_bielik.sh
│   └── Server.py
│
├── Rag/
│   ├── dockerfiles/
│   │   └── Run_vector_db.sh
│   ├── csv_document_loader.py
│   ├── weaviate_ingest.py
│   ├── retriever.py
│   ├── llms.py
│   ├── pipeline.py
│   ├── generate_stats.py
│   ├── config.py
│   ├── retrieval_report.md
│   └── retrieval_stats_summary.md
│├── images/
│   └── image1.png
└── README.md
```
---

## Contact

Open source project.  
Feel free to collaborate:  
- [LinkedIn: Michał Jaros](https://www.linkedin.com/in/michał-jaros-88572821a/)  
- E-mail: michal.marek.jaros@gmail.com  
