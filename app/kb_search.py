from __future__ import annotations
from typing import List, Dict
import numpy as np
from data_loader import ChunkedKnowledgeBase


class EmbeddingRetriever:
    """Vector-based search over per-HMO chunks."""

    def __init__(self, kb: ChunkedKnowledgeBase, client, top_k: int = 3):
        self.client = client
        self.top_k  = top_k

        # Build index once
        docs  = [c["text"] for c in kb.chunks]
        metas = [{"hmo": c["hmo"], "text": c["text"]} for c in kb.chunks]

        embeddings = self.client.embed(docs)
        self.index: List[Dict] = []
        for vec, meta in zip(embeddings, metas):
            v = np.asarray(vec, dtype=np.float32)
            v = v / (np.linalg.norm(v) + 1e-8)
            self.index.append({**meta, "vec": v})

    # ────────────────── search ──────────────────
    def search(self, allowed_hmos: List[str], query: str) -> List[str]:
        q_vec = np.asarray(self.client.embed([query])[0], dtype=np.float32)
        q_vec = q_vec / (np.linalg.norm(q_vec) + 1e-8)

        scored = [
            (item["text"], float(np.dot(q_vec, item["vec"])))
            for item in self.index
            if item["hmo"] in allowed_hmos
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [text for text, _ in scored[: self.top_k]]

# ----------------------------------------------------------------------
# Helper for the RAG chain
class Retriever:
    def __init__(self, kb: ChunkedKnowledgeBase, client):
        self.emb = EmbeddingRetriever(kb, client)

    def build_context(self, hmos: List[str], user_query: str) -> str:
        snippets = self.emb.search(hmos, user_query)
        return "\n\n".join(snippets)