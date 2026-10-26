"""Embeddings + FAISS search. Owner: Reena."""
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


class Retriever:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", model=None):
        self.model = model or SentenceTransformer(model_name)
        self.index = None
        self.chunks = []

    def build(self, chunks):
        self.chunks = chunks
        emb = self.model.encode([c["text"] for c in chunks],
                                normalize_embeddings=True)
        emb = np.asarray(emb, dtype="float32")
        self.index = faiss.IndexFlatIP(emb.shape[1])
        self.index.add(emb)

    def search(self, question: str, k: int = 3):
        if self.index is None or not self.chunks:
            return []
        q = np.asarray(self.model.encode([question], normalize_embeddings=True),
                       dtype="float32")
        scores, ids = self.index.search(q, min(k, len(self.chunks)))
        return [{**self.chunks[i], "score": float(s)}
                for s, i in zip(scores[0], ids[0]) if i != -1]
