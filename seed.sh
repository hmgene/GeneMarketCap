#!/bin/bash

set -e

echo "[INFO] creating project structure..."

mkdir -p app/api/routes
mkdir -p app/core
mkdir -p app/services
mkdir -p app/db
mkdir -p app/utils

mkdir -p data/chroma
mkdir -p data/meta
mkdir -p data/pdfs
mkdir -p data/obsidian

touch app/__init__.py

########################################
# requirements.txt
########################################

cat > requirements.txt << 'EOF'
fastapi
uvicorn
python-multipart
ollama
chromadb
pymupdf
EOF

########################################
# core/config.py
########################################

cat > app/core/config.py << 'EOF'
CHROMA_DIR = "./data/chroma"
PDF_DIR = "./data/pdfs"
META_DIR = "./data/meta"

EMBED_MODEL = "nomic-embed-text"
LLM_MODEL = "qwen3:14b"

EMBED_WORKERS = 6

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
EOF

########################################
# services/pdf_service.py
########################################

cat > app/services/pdf_service.py << 'EOF'
import fitz


def parse_pdf(pdf_path):

    doc = fitz.open(pdf_path)

    text = ""

    for page in doc:
        text += page.get_text()

    return text
EOF

########################################
# services/chunk_service.py
########################################

cat > app/services/chunk_service.py << 'EOF'
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
EOF

########################################
# services/embedding_service.py
########################################

cat > app/services/embedding_service.py << 'EOF'
import ollama

from app.core.config import EMBED_MODEL


def get_embedding(text):

    res = ollama.embeddings(
        model=EMBED_MODEL,
        prompt=text
    )

    return res["embedding"]
EOF

########################################
# utils/parallel.py
########################################

cat > app/utils/parallel.py << 'EOF'
from concurrent.futures import ThreadPoolExecutor


def parallel_map(fn, items, workers=6):

    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(fn, items))
EOF

########################################
# db/chroma_store.py
########################################

cat > app/db/chroma_store.py << 'EOF'
import chromadb

from app.core.config import CHROMA_DIR

client = chromadb.PersistentClient(path=CHROMA_DIR)

collection = client.get_or_create_collection("papers")


def add_chunks(
    chunks,
    embeddings,
    metadatas,
    batch_size=100
):

    for start in range(0, len(chunks), batch_size):

        end = start + batch_size

        batch_chunks = chunks[start:end]
        batch_embeddings = embeddings[start:end]

        batch_ids = [
            f"{metadatas['paper_id']}_{i}"
            for i in range(start, end)
            if i < len(chunks)
        ]

        batch_metadatas = [
            metadatas for _ in batch_chunks
        ]

        collection.add(
            documents=batch_chunks,
            embeddings=batch_embeddings,
            metadatas=batch_metadatas,
            ids=batch_ids
        )


def query_chunks(
    query_embedding,
    pubmed_id=None,
    n_results=5
):

    if pubmed_id:

        return collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where={
                "pubmed_id": str(pubmed_id)
            }
        )

    return collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
EOF

########################################
# db/csv_store.py
########################################

cat > app/db/csv_store.py << 'EOF'
import csv
import os

from app.core.config import META_DIR

CSV_PATH = f"{META_DIR}/papers.csv"

FIELDS = [
    "paper_id",
    "pubmed_id",
    "title",
    "source_file"
]

os.makedirs(META_DIR, exist_ok=True)


def add_paper(row):

    exists = os.path.exists(CSV_PATH)

    with open(CSV_PATH, "a", newline="") as f:

        writer = csv.DictWriter(
            f,
            fieldnames=FIELDS
        )

        if not exists:
            writer.writeheader()

        writer.writerow(row)
EOF

########################################
# services/ingest_service.py
########################################

cat > app/services/ingest_service.py << 'EOF'
import uuid

from app.services.pdf_service import parse_pdf
from app.services.chunk_service import chunk_text
from app.services.embedding_service import get_embedding

from app.db.chroma_store import add_chunks
from app.db.csv_store import add_paper

from app.utils.parallel import parallel_map

from app.core.config import EMBED_WORKERS


def ingest_pdf(
    file_path,
    pubmed_id=None,
    title=None
):

    paper_id = str(uuid.uuid4())

    print("[INFO] parsing pdf...")
    text = parse_pdf(file_path)

    print("[INFO] chunking...")
    chunks = chunk_text(text)

    print(f"[INFO] chunks: {len(chunks)}")

    print("[INFO] embedding...")

    embeddings = parallel_map(
        get_embedding,
        chunks,
        workers=EMBED_WORKERS
    )

    print("[INFO] inserting chroma...")

    add_chunks(
        chunks,
        embeddings,
        {
            "paper_id": paper_id,
            "pubmed_id": str(pubmed_id)
        }
    )

    print("[INFO] updating metadata...")

    add_paper({
        "paper_id": paper_id,
        "pubmed_id": pubmed_id,
        "title": title or "unknown",
        "source_file": file_path
    })

    return {
        "paper_id": paper_id,
        "chunks": len(chunks)
    }
EOF

########################################
# services/rag_service.py
########################################

cat > app/services/rag_service.py << 'EOF'
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
EOF

########################################
# api/routes/upload.py
########################################

cat > app/api/routes/upload.py << 'EOF'
from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File

import os

from app.services.ingest_service import ingest_pdf

router = APIRouter()


@router.post("/upload")
async def upload(
    file: UploadFile = File(...),
    pubmed_id: str = None,
    title: str = None
):

    os.makedirs("./data/pdfs", exist_ok=True)

    path = f"./data/pdfs/{file.filename}"

    with open(path, "wb") as f:
        f.write(await file.read())

    return ingest_pdf(
        path,
        pubmed_id,
        title
    )
EOF

########################################
# api/routes/ask.py
########################################

cat > app/api/routes/ask.py << 'EOF'
from fastapi import APIRouter

from app.services.rag_service import ask_question

router = APIRouter()


@router.post("/ask")
async def ask(payload: dict):

    answer = ask_question(
        payload["question"],
        payload.get("pubmed_id")
    )

    return {
        "answer": answer
    }
EOF

########################################
# main.py
########################################

cat > app/main.py << 'EOF'
from fastapi import FastAPI

from app.api.routes.upload import router as upload_router
from app.api.routes.ask import router as ask_router

app = FastAPI()

app.include_router(upload_router)
app.include_router(ask_router)
EOF

########################################
# run.sh
########################################

cat > run.sh << 'EOF'
#!/bin/bash

export OLLAMA_KEEP_ALIVE=24h
export OMP_NUM_THREADS=4

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
EOF

chmod +x run.sh

########################################
# final
########################################

echo ""
echo "[DONE]"
echo ""
echo "Next:"
echo "1. python -m venv venv"
echo "2. source venv/bin/activate"
echo "3. pip install -r requirements.txt"
echo "4. ollama pull nomic-embed-text"
echo "5. ollama pull qwen3:14b"
echo "6. ./run.sh"
echo ""
echo "Upload endpoint:"
echo "POST /upload"
echo ""
echo "Ask endpoint:"
echo "POST /ask"
echo ""
