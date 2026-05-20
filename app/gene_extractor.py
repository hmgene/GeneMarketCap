import ollama
from app.config import LLM_MODEL


def extract_genes(text):

    prompt = f"""
Extract gene names from the text.

Return ONLY a Python list.

Text:
{text[:8000]}
"""

    res = ollama.chat(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        return eval(res["message"]["content"])
    except:
        return []
