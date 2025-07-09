"""Utility functions for CSV document loading and chunking."""

import pandas as pd
import re
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# REGEX for cleaning legal references (e.g. 'art. 123 ust. 2' -> 'art.123ust.2')
LEGAL_REF_PATTERN = re.compile(
    r"(art\.\s*\d+[A-Za-zĄĆĘŁŃÓŚŹŻ]?"
    r"(?:\s*ust\.\s*\d+[A-Za-zĄĆĘŁŃÓŚŹŻ]?)?"
    r"(?:\s*pkt\s*\d+[A-Za-zĄĆĘŁŃÓŚŹŻ]?)?"
    r"(?:\s*lit\.?\s*[A-Za-zĄĆĘŁŃÓŚŹŻ])?"
    r")",
    flags=re.IGNORECASE
)

def merge_legal_reference(text: str) -> str:
    """Removes spaces from legal references."""
    def _strip_spaces(match: re.Match) -> str:
        return match.group(1).replace(" ", "")
    return LEGAL_REF_PATTERN.sub(_strip_spaces, text)

def load_csv_to_dataframe(csv_path_or_buffer) -> pd.DataFrame:
    """
    Loads data from a CSV file or buffer and returns a cleaned DataFrame.
    The CSV file must contain columns: 'Treść:', 'Sygnatura:'.
    """
    df = pd.read_csv(csv_path_or_buffer)
    required_cols = {'Treść:', 'Sygnatura:'}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"The CSV file must contain the following columns: {required_cols}")
    df = df[['Treść:', 'Sygnatura:']].dropna().rename(columns={'Treść:': 'text', 'Sygnatura:': 'sig'})
    df['text_clean'] = df['text'].apply(merge_legal_reference)
    return df

def dataframe_to_documents(df: pd.DataFrame) -> list:
    """
    Converts a DataFrame into a list of LangChain Documents.
    """
    return [
        Document(
            page_content=row['text_clean'],
            metadata={'sig': row['sig'], 'text': row['text']}
        )
        for _, row in df.iterrows()
    ]

def split_documents(
    documents: list,
    chunk_size: int = 500,
    chunk_overlap: int = 128
) -> list:
    """
    Splits documents into chunks of the specified length.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    split_docs = splitter.split_documents(documents)
    for doc in split_docs:
        doc.metadata['passage'] = doc.page_content
    return split_docs
