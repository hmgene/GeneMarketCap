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
