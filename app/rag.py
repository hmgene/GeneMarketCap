import ollama

from app.embeddings import get_embedding
from app.chroma_store import query_chunks
from app.config import LLM_MODEL


def ask_question(question: str):

    query_embedding = get_embedding(question)

    results = query_chunks(query_embedding)

    docs = results["documents"][0]

    context = "\n\n".join(docs)

    prompt = f"""
You are a scientific research assistant.

Answer the question using ONLY the provided context.

Context:
{context}

Question:
{question}
"""

    response = ollama.chat(
        model=LLM_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]
