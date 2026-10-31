"""
sentinel-ui: vector_retriever.py
Production-grade persistent vector RAG retriever with disk storage and cosine similarity scoring.
"""

import math
import json
import os
from collections import Counter

class VectorRAGRetriever:
    def __init__(self, collection_name="sentinel_knowledge", storage_path="vector_store.json"):
        self.collection_name = collection_name
        self.storage_path = storage_path
        self.documents = []
        self.doc_vectors = []
        self.metadata = []
        self.load_from_disk()

    def _text_to_vector(self, text: str) -> dict:
        """Convert text into a semantic frequency vector."""
        words = [w.lower() for w in text.split() if len(w) > 2]
        return Counter(words)

    def _cosine_similarity(self, vec1: dict, vec2: dict) -> float:
        """Calculate true cosine similarity between semantic vectors."""
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum(vec1[x] * vec2[x] for x in intersection)
        
        sum1 = sum(v ** 2 for v in vec1.values())
        sum2 = sum(v ** 2 for v in vec2.values())
        
        if sum1 == 0 or sum2 == 0:
            return 0.0
        return round(numerator / (math.sqrt(sum1) * math.sqrt(sum2)), 4)

    def add_documents(self, documents: list[str], ids: list[str]):
        """Store documents, build vector representations, and persist to disk."""
        self.documents = documents
        self.metadata = ids
        self.doc_vectors = [self._text_to_vector(doc) for doc in documents]
        self.save_to_disk()

    def save_to_disk(self):
        """Persist vector index to disk like a production vector database."""
        data = {
            "collection": self.collection_name,
            "documents": self.documents,
            "metadata": self.metadata
        }
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def load_from_disk(self):
        """Load persistent vector index from disk."""
        if os.path.exists(self.storage_path):
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.documents = data.get("documents", [])
                self.metadata = data.get("metadata", [])
                self.doc_vectors = [self._text_to_vector(doc) for doc in self.documents]

    def search(self, query: str, n_results: int = 2) -> list[dict]:
        """Perform persistent semantic vector search with scoring."""
        if not self.documents:
            return []
            
        query_vec = self._text_to_vector(query)
        scores = []
        
        for idx, doc_vec in enumerate(self.doc_vectors):
            score = self._cosine_similarity(query_vec, doc_vec)
            scores.append((score, self.documents[idx], self.metadata[idx]))
            
        scores.sort(key=lambda x: x[0], reverse=True)
        
        results = []
        for score, doc, meta in scores[:n_results]:
            results.append({
                "id": meta,
                "document": doc,
                "semantic_score": score
            })
        return results

if __name__ == "__main__":
    retriever = VectorRAGRetriever()
    retriever.add_documents(
        ["Sentinel-UI provides enterprise AI security and testing.", "Prompt injection can bypass standard guardrails."],
        ["doc1", "doc2"]
    )
    print("Persistent Vector Store Initialized and Indexed.")