import uuid
import time
import os
from app.embeddings import get_embedding
from app.chroma_store import add_chunks
from app.csv_store import add_paper
from app.config import PDF_DIR
from concurrent.futures import ThreadPoolExecutor


def chunk_text(text, chunk_size=800, overlap=100):

    chunks = []
    i = 0

    while i < len(text):

        chunks.append(text[i:i+chunk_size])
        i += chunk_size - overlap

    return chunks

from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def embed_chunks(chunks):

    embeddings = [None] * len(chunks)

    t0 = time.time()

    with ThreadPoolExecutor(max_workers=4) as ex:

        futures = {
            ex.submit(get_embedding, chunk): i
            for i, chunk in enumerate(chunks)
        }

        done = 0

        for f in as_completed(futures):

            i = futures[f]
            embeddings[i] = f.result()

            done += 1

            if done % 10 == 0 or done == len(chunks):
                print(f"[embedding] {done}/{len(chunks)}")

    t1 = time.time()

    print(f"[DONE] {t1 - t0:.2f}s")

    return embeddings


def ingest_pdf(file_path, pubmed_id=None, title=None, authors=None):

    os.makedirs(PDF_DIR, exist_ok=True)

    paper_id = str(uuid.uuid4())

    # ----------------------------
    # 1. LOAD TEXT
    # ----------------------------
    t0 = time.time()

    with open(file_path, "r", errors="ignore") as f:
        text = f.read()

    t1 = time.time()
    print(f"[TIME] load text: {t1 - t0:.2f}s")

    # ----------------------------
    # 2. CHUNKING
    # ----------------------------
    chunks = chunk_text(text)

    t2 = time.time()
    print(f"[TIME] chunking: {t2 - t1:.2f}s | chunks={len(chunks)}")

    # ----------------------------
    # 3. EMBEDDING
    # ----------------------------
    embeddings = embed_chunks(chunks)

    # ----------------------------
    # 4. CHROMA INSERT
    # ----------------------------
    t3 = time.time()

    print("[INFO] add chunks to chroma...")

    add_chunks(
        chunks,
        embeddings,
        {"paper_id": paper_id}
    )

    t4 = time.time()
    print(f"[TIME] chroma insert: {t4 - t3:.2f}s")

    # ----------------------------
    # 5. CSV UPDATE
    # ----------------------------
    t5 = time.time()

    print("[INFO] add paper metadata...")

    add_paper({
        "paper_id": paper_id,
        "pubmed_id": pubmed_id,
        "title": title or "unknown",
        "authors": authors or [],
        "pub_date": "unknown",
        "source_file": file_path
    })

    t6 = time.time()
    print(f"[TIME] csv write: {t6 - t5:.2f}s")

    # ----------------------------
    # FINAL
    # ----------------------------
    total = t6 - t0
    print(f"\n[TOTAL TIME]: {total:.2f}s\n")

    return {
        "paper_id": paper_id,
        "chunks": len(chunks),
        "time_sec": total
    }
