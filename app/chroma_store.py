import chromadb
from app.config import CHROMA_DIR

client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = client.get_or_create_collection("papers")


def add_chunks(chunks, embeddings, metadatas, batch_size=100):

    assert len(chunks) == len(embeddings)

    for start in range(0, len(chunks), batch_size):

        end = start + batch_size

        batch_chunks = chunks[start:end]
        batch_embeddings = embeddings[start:end]

        batch_ids = [
            f"chunk_{start + i}"
            for i in range(len(batch_chunks))
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


def query_chunks(query_embedding, k=5):

    return collection.query(
        query_embeddings=[query_embedding],
        n_results=k
    )
