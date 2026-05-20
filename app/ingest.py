import os
import uuid

from app.pdf_parser import extract_text
from app.chunker import chunk_text
from app.embeddings import get_embedding
from app.chroma_store import add_chunks


def ingest_pdf(file_path):

    paper_id = str(uuid.uuid4())

    print("Extracting text...")
    text = extract_text(file_path)

    print("Chunking...")
    chunks = chunk_text(text)

    print(f"Total chunks: {len(chunks)}")

    print("Embedding...")
    embeddings = []

    for chunk in chunks:
        embeddings.append(get_embedding(chunk))

    print("Saving to ChromaDB...")

    add_chunks(
        chunks=chunks,
        embeddings=embeddings,
        metadata={
            "paper_id": paper_id,
            "source": os.path.basename(file_path)
        }
    )

    return {
        "paper_id": paper_id,
        "chunks": len(chunks)
    }
