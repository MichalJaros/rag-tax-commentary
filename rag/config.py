# config.py

from dotenv import load_dotenv
import os

load_dotenv()

WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8081")
WEAVIATE_CLASS = os.getenv("WEAVIATE_CLASS", "Wyszukiwarka_v1")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "ipipan/silver-retriever-base-v1")

BIELIK_MODEL = os.getenv("BIELIK_MODEL", "speakleash/Bielik-11B-v2.3-Instruct-FP8")
BIELIK_SERVER_URL = os.getenv("BIELIK_SERVER_URL", "http://localhost:8000")

TOP_K = int(os.getenv("TOP_K", "2"))
ENV = os.getenv("ENV", "dev")

def is_production():
    return ENV.lower() == "prod"

print("WEAVIATE_URL =", WEAVIATE_URL)
print("BIELIK_SERVER_URL =", BIELIK_SERVER_URL)
