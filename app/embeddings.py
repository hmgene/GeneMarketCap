import ollama

from app.config import EMBED_MODEL


def get_embedding(text: str):

    response = ollama.embeddings(
        model=EMBED_MODEL,
        prompt=text
    )

    return response["embedding"]
