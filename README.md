# Research Agent

Local-first scientific research assistant.

## Structure 
```
data/
├── chroma/
├── obsidian/
├── pdfs/
└── meta/
    └── papers.csv   ← single source of truth

app/
├── main.py             (FastAPI)
├── ingest.py           (PDF upload pipeline)
├── rag.py              (ASK pipeline)
├── csv_store.py        (papers.csv manager)
├── embeddings.py
├── chroma_store.py
├── gene_extractor.py
└── config.py
```

---

# Setup

## 1. Install Python dependencies

```bash
pip install -r requirements.txt


## Examples

**Test**
```
import ollama

def test():
    print("embedding test...")

    e = ollama.embeddings(
        model="nomic-embed-text",
        prompt="gene regulation"
    )

    print("embedding dim:", len(e["embedding"]))

    print("chat test...")

    r = ollama.chat(
        model="qwen3:8b",
        messages=[{"role": "user", "content": "say ok"}]
    )

    print(r["message"]["content"])

test()

curl http://127.0.0.1:11434/api/embeddings \
  -d '{
    "model": "nomic-embed-text",
    "prompt": "TP53 regulates cell cycle"
  }'


```

**Ask Question**

```

curl -X POST \
  -F "file=@data/pdfs/s43018-026-01154-x.pdf" \
  http://127.0.0.1:8000/upload

curl -X POST \
  http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What genes are important?"}'
```
