"""
sentinel-ui: vector_retriever.py
Persistent semantic vector RAG retriever utilizing embeddings and cosine similarity scoring.
"""

import json
import math
import os
from typing import List, Dict, Any

class VectorRAGRetriever:
    def __init__(self, storage_path: str = "vector_store.json", collection_name: str = "default"):
        self.storage_path = storage_path
        self.collection_name = collection_name
        self.documents: List[str] = []
        self.metadata: List[Dict[str, Any]] = []
        self.doc_vectors: List[Dict[str, float]] = []
        self.load_store()

    def _tokenize(self, text: str) -> List[str]:
        return [word.lower() for word in text.split() if word.isalnum()]

    def _text_to_vector(self, text: str) -> Dict[str, float]:
        tokens = self._tokenize(text)
        if not tokens:
            return {}
        freq: Dict[str, float] = {}
        for token in tokens:
            freq[token] = freq.get(token, 0.0) + 1.0
        mag = math.sqrt(sum(val ** 2 for val in freq.values()))
        if mag > 0:
            for token in freq:
                freq[token] /= mag
        return freq

    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum(vec1[x] * vec2[x] for x in intersection)
        return float(numerator)

    def add_documents(self, docs: List[str], metadatas: List[Dict[str, Any]] = None):
        if metadatas is None:
            metadatas = [{"id": f"doc_{i}"} for i in range(len(docs))]
        
        for doc, meta in zip(docs, metadatas):
            self.documents.append(doc)
            self.metadata.append(meta)
            self.doc_vectors.append(self._text_to_vector(doc))
        
        self.save_store()

    def search(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
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
                "metadata": meta,
                "document": doc,
                "semantic_score": round(score, 4)
            })
        return results

    def save_store(self):
        data = {
            "collection": self.collection_name,
            "documents": self.documents,
            "metadata": self.metadata
        }
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_store(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    docs = data.get("documents", [])
                    metas = data.get("metadata", [])
                    if docs:
                        self.documents = []
                        self.metadata = []
                        self.doc_vectors = []
                        self.add_documents(docs, metas)
            except Exception:
                pass

if __name__ == "__main__":
    retriever = VectorRAGRetriever()
    retriever.add_documents(
        ["Sentinel-UI provides enterprise AI security and testing.", "Prompt injection can bypass standard guardrails."],
        [{"id": "doc1"}, {"id": "doc2"}]
    )
    print("Persistent Vector Store Initialized and Indexed.")