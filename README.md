# Projekt RAG (Retriever-Augmented Generation)
**rag-tax-commentary**  
Retrieval-Augmented Generation system do automatycznego tworzenia komentarzy podatkowych na bazie interpretacji indywidualnych, wykorzystujący model Bielik LLM oraz bazę wektorową Weaviate.

## Spis treści
- [Cel projektu](#cel-projektu)
- [Technologie](#technologie)
- [Przykład użycia](#przykład-użycia)
- [Struktura repozytorium](#struktura-repozytorium)
- [Kontakt](#kontakt)

## Cel projektu
Celem projektu jest stworzenie narzędzia, które na podstawie interpretacji podatkowych w przystępny sposób odpowie na pytania dotyczące prawa podatkowego. Organy podatkowe wydały ponad pół miliona interpretacji indywidualnych, w których wyjaśniały wykładnię przepisów. Odnalezienie interpretacji zawierających kluczowe informacje bywa czasochłonne, dlatego istnieje przestrzeń dla systemów przyspieszających ten proces oraz generujących zwięzłe podsumowania jasno odpowiadające na pytanie użytkownika.

## Technologie
- **Python 3.12.3**  
  Główne środowisko wykonawcze i język programowania.
- **requests**  
  Wysyłanie zapytań HTTP (pobieranie danych, komunikacja z API).
- **weaviate**  
  Klient do bazy wektorowej Weaviate (indeksowanie dokumentów, wyszukiwanie semantyczne).
- **pandas**  
  Manipulacja i analiza danych w formie DataFrame (wczytywanie i oczyszczanie danych źródłowych).
- **re (Regular Expressions)**  
  Zaawansowane operacje na tekście (parsowanie, czyszczenie).
- **transformers (AutoTokenizer)**  
  Tokenizacja tekstu przed inferencją modeli językowych.
- **litserve**  
  Serwowanie modelu LLM poprzez endpointy REST, ułatwiające integrację z frontendem.
- **vllm (LLM, SamplingParams)**  
  Wydajna inferencja modeli językowych (równoległe przetwarzanie zapytań, konfiguracja parametrów generowania).

Dzięki temu zestawowi narzędzi aplikacja RAG składa się z trzech głównych warstw:
1. **Moduł Retrievera**  
   - Indeksowanie i wyszukiwanie informacji w Weaviate  
   - Preprocessing danych w Pandas  
   - Caching wyników zapytań
2. **Moduł Generatywny**  
   - Tokenizacja w Transformers  
   - Wydajna inferencja w VLLM  
   - Wysyłanie zapytań do lokalnego modelu Bielik lub do API OpenAI
3. **Warstwa Serwowania**  
   - Litserve do wystawienia API HTTP i obsługi żądań użytkowników

Każda z wymienionych bibliotek pełni określoną rolę w architekturze projektu, co pozwala na skalowalny i elastyczny pipeline RAG.

## Przykład użycia
W wyniku prac powstał prototyp zawierający około 4500 interpretacji indywidualnych. Obecna wersja nie posiada interfejsu webowego; pytania należy zadawać w terminalu.

1. Użytkownik wpisuje pytanie (np. o konkretną kwestię podatkową).  
   ![Wpisywanie pytania w terminalu](images/image1.png)

2. System za pomocą wyszukiwania wektorowego odnajduje fragmenty interpretacji, które odpowiadają na zadane pytanie.  
   ![Wyszukiwanie odpowiednich fragmentów w bazie Weaviate](images/image2.png)

3. Zadane pytanie oraz wybrane fragmenty interpretacji trafiają do promptu i są przesyłane do modelu Bielik. Duży model językowy generuje jasną i zwięzłą odpowiedź.  
   ![Generowanie odpowiedzi przez model Bielik](images/image3.png)

W przykładzie w pytaniu użyto słowa „pensja”, aby sprawdzić, czy wyszukiwanie wektorowe poprawnie skojarzy je z terminem „wynagrodzenie”, stosowanym w ustawie oraz interpretacjach indywidualnych.

## Struktura repozytorium
Ze względu na ograniczenia dotyczące rozmiaru plików na GitHubie, w repozytorium nie zamieszczono wektorowej bazy danych ani pliku CSV z surowymi tekstami interpretacji.

Repozytorium składa się z następujących elementów:
├── bielik_aws_deploy/																																								
│ ├── Requirements.txt																																								
│ ├── Run_bielik.sh																																								
│ └── Server.py																																									
├── Rag/																																									
│ ├── dockerfiles/																																								
│ │ ├── Run_embedding_model.sh																																							
│ │ └── Run_vector_db.sh																																							
│ ├── Ingest_data.py																																								
│ ├── rag.py																																									
│ └── Requirements.txt																																								
└── images/																																									
├── image1.png																																									
├── image2.png																																									
└── image3.png																																									

- **bielik_aws_deploy/**  
  Zawiera pliki potrzebne do uruchomienia modelu Bielik na instancji AWS EC2:
  - `Requirements.txt` – lista zależności Pythona do uruchomienia serwera Bielik.  
  - `Run_bielik.sh` – skrypt Docker do uruchamiania serwera i zbierania logów.  
  - `Server.py` – kod serwera wystawiającego endpointy do inferencji modelu Bielik.

- **Rag/**  
  Implementacja pipeline RAG:
  - `dockerfiles/`  
    - `Run_embedding_model.sh` – skrypt Docker do uruchamiania modelu embeddingowego (silver-retriever-base-v1).  
    - `Run_vector_db.sh` – skrypt Docker do uruchamiania bazy wektorowej Weaviate.  
  - `Ingest_data.py` – skrypt Pythona tworzący wektorową bazę danych, modyfikujący tekst interpretacji, przeprowadzający chunking i tokenizację. W kodzie wykorzystano wiedzę dziedzinową, aby np. „art. 18d ust. 1 pkt 1” był traktowany jako pojedynczy token – skrypt usuwa zbędne spacje, dzięki czemu odniesienia do konkretnych przepisów mają dokładniejsze reprezentacje.  
  - `rag.py` – główny skrypt Pythona uruchamiający pełny pipeline RAG: definiuje prompt systemowy, pobiera informacje z bazy wektorowej, ustala hiperparametry LLM-u i wysyła zapytanie do serwera z modelem Bielik.  
  - `Requirements.txt` – lista zależności Pythona dla modułu RAG.

- **images/**  
  Katalog z plikami graficznymi używanymi w sekcji „Przykład użycia”.

## Kontakt
Projekt udostępniony jest na licencji otwartej. Osoby zainteresowane wspólnym rozwojem narzędzia do usystematyzowanego przeglądu przepisów podatkowych zapraszam do kontaktu:  
- LinkedIn: [michał-jaros-88572821a](https://www.linkedin.com/in/michał-jaros-88572821a/)  
- E-mail: michal.marek.jaros@gmail.com  
