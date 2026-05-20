import ollama

from app.services.embedding_service import get_embedding
from app.db.chroma_store import query_chunks

from app.core.config import LLM_MODEL


def ask_question(
    question,
    pubmed_id=None
):

    query_embedding = get_embedding(question)

    results = query_chunks(
        query_embedding,
        pubmed_id=pubmed_id
    )

    docs = results["documents"][0]

    context = "\n\n".join(docs)

    prompt = f"""
You are a scientific research assistant.

Use ONLY the provided context.

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
