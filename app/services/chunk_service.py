from app.core.config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP
)


def chunk_text(
    text,
    chunk_size=CHUNK_SIZE,
    overlap=CHUNK_OVERLAP
):

    chunks = []

    i = 0

    while i < len(text):

        chunk = text[i:i+chunk_size]

        if len(chunk.strip()) > 50:
            chunks.append(chunk)

        i += chunk_size - overlap

    return chunks
