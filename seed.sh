#!/usr/bin/env bash

set -e

PROJECT_NAME="./"

echo "Creating project: ${PROJECT_NAME}"

mkdir -p ${PROJECT_NAME}

cd ${PROJECT_NAME}

##################################################
# DIRECTORY STRUCTURE
##################################################

mkdir -p app
mkdir -p data/pdfs
mkdir -p data/chroma
mkdir -p data/obsidian

touch README.md

##################################################
# requirements.txt
##################################################

cat << 'EOF' > requirements.txt
fastapi
uvicorn
python-multipart

pymupdf
chromadb
ollama

langchain-text-splitters
EOF

##################################################
# .gitignore
##################################################

cat << 'EOF' > .gitignore
__pycache__/
*.pyc

.env
venv/

data/chroma/
data/pdfs/

.DS_Store
EOF

##################################################
# app/config.py
##################################################

cat << 'EOF' > app/config.py
CHROMA_PATH = "./data/chroma"
PDF_PATH = "./data/pdfs"
OBSIDIAN_PATH = "./data/obsidian"

EMBED_MODEL = "nomic-embed-text"
LLM_MODEL = "qwen3:14b"

COLLECTION_NAME = "papers"
EOF

##################################################
# app/pdf_parser.py
##################################################

cat << 'EOF' > app/pdf_parser.py
import fitz


def extract_text(pdf_path: str) -> str:

    doc = fitz.open(pdf_path)

    text = []

    for page in doc:
        text.append(page.get_text())

    return "\n".join(text)
EOF

##################################################
# app/chunker.py
##################################################

cat << 'EOF' > app/chunker.py
from langchain_text_splitters import RecursiveCharacterTextSplitter


splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200,
    chunk_overlap=200
)


def chunk_text(text: str):

    return splitter.split_text(text)
EOF

##################################################
# app/embeddings.py
##################################################

cat << 'EOF' > app/embeddings.py
import ollama

from app.config import EMBED_MODEL


def get_embedding(text: str):

    response = ollama.embeddings(
        model=EMBED_MODEL,
        prompt=text
    )

    return response["embedding"]
EOF

##################################################
# app/chroma_store.py
##################################################

cat << 'EOF' > app/chroma_store.py
import chromadb

from app.config import CHROMA_PATH, COLLECTION_NAME


client = chromadb.PersistentClient(path=CHROMA_PATH)

collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)


def add_chunks(chunks, embeddings, metadata):

    ids = [
        f"{metadata['paper_id']}_{i}"
        for i in range(len(chunks))
    ]

    metadatas = []

    for i in range(len(chunks)):

        metadatas.append({
            "paper_id": metadata["paper_id"],
            "source": metadata["source"],
            "chunk_index": i
        })

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )


def query_chunks(query_embedding, n_results=5):

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    return results
EOF

##################################################
# app/ingest.py
##################################################

cat << 'EOF' > app/ingest.py
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
EOF

##################################################
# app/rag.py
##################################################

cat << 'EOF' > app/rag.py
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
EOF

##################################################
# app/main.py
##################################################

cat << 'EOF' > app/main.py
import os
import shutil

from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel

from app.ingest import ingest_pdf
from app.rag import ask_question

from app.config import PDF_PATH


app = FastAPI()


class QuestionRequest(BaseModel):
    question: str


@app.get("/")
async def root():

    return {
        "message": "Research Agent API running"
    }


@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):

    save_path = os.path.join(PDF_PATH, file.filename)

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = ingest_pdf(save_path)

    return result


@app.post("/ask")
async def ask(req: QuestionRequest):

    answer = ask_question(req.question)

    return {
        "question": req.question,
        "answer": answer
    }
EOF

##################################################
# README.md
##################################################

cat << 'EOF' > README.md
# Research Agent

Local-first scientific research assistant.

## Stack

- Ollama
- FastAPI
- ChromaDB
- PyMuPDF
- Open WebUI
- Obsidian

---

# Setup

## 1. Install Python dependencies

```bash
pip install -r requirements.txt
