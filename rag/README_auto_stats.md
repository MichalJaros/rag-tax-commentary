# Statystyki RAG

- **Liczba dokumentów:** 4245
- **Liczba chunków:** 538974
- **Średnia długość chunku:** 382.35483529817765
- **Mediana długości chunku:** 417.0
- **Max długość chunku:** 500
- **Liczba chunków w bazie Weaviate:** 96534

## Rozkład długości chunków
![Histogram chunków](docs_imgs/chunk_length_hist.png)

## Pipeline

```mermaid
flowchart LR
    User([User]) -->|Pytanie| Streamlit(Streamlit/CLI)
    Streamlit -->|Preprocessing| Retriever
    Retriever -->|Query| Weaviate[(Weaviate)]
    Retriever -->|Top-K chunks| BielikLLM[Bielik LLM]
    BielikLLM -->|Odpowiedź| Streamlit
    Streamlit -->|Wynik| User

