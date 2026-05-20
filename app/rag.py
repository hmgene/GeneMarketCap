import ollama

from app.embeddings import get_embedding
from app.chroma_store import query_chunks
from app.csv_store import update_genes
from app.gene_extractor import extract_genes
from app.config import LLM_MODEL


def ask_question(question, paper_id=None):

    query_embedding = get_embedding(question)

    results = query_chunks(query_embedding)

    docs = results["documents"][0]

    context = "\n\n".join(docs)

    prompt = f"""
You are a scientific research assistant.

Extract:
- genes
- pathways
- mechanism

Context:
{context}

Question:
{question}
"""

    res = ollama.chat(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

    answer = res["message"]["content"]

    genes = extract_genes(context)

    if paper_id:
        update_genes(paper_id, genes)

    return {
        "answer": answer,
        "genes": genes
    }
