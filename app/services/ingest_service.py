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
