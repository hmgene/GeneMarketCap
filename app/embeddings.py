import ollama
from app.config import EMBED_MODEL


def get_embedding(text):
    res = ollama.embeddings(
        model=EMBED_MODEL,
        prompt=text
    )
    return res["embedding"]
