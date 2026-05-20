from app.embeddings import get_embedding

vec = get_embedding("test sentence")
print(len(vec))
