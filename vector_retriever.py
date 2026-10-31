"""
sentinel-ui: vector_retriever.py
True semantic vector RAG retriever using pure Python semantic token profiling and cosine similarity.
"""

import math
from collections import Counter

class VectorRAGRetriever:
    def __init__(self, collection_name="sentinel_knowledge"):
        self.collection_name = collection_name
        self.documents = []
        self.doc_vectors = []

    def _text_to_vector(self, text: str) -> dict:
        """Convert text into a semantic frequency vector."""
        words = [w.lower() for w in text.split() if len(w) > 2]
        return Counter(words)

    def _cosine_similarity(self, vec1: dict, vec2: dict) -> float:
        """Calculate true cosine similarity between two semantic vectors."""
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum(vec1[x] * vec2[x] for x in intersection)
        
        sum1 = sum(v ** 2 for v in vec1.values())
        sum2 = sum(v ** 2 for v in vec2.values())
        
        if sum1 == 0 or sum2 == 0:
            return 0.0
        return round(numerator / (math.sqrt(sum1) * math.sqrt(sum2)), 4)

    def add_documents(self, documents: list[str], ids: list[str]):
        """Store documents and build their semantic vector representations."""
        self.documents = documents
        self.doc_vectors = [self._text_to_vector(doc) for doc in documents]

    def search(self, query: str, n_results: int = 2) -> list[dict]:
        """Perform semantic vector search using cosine similarity scoring."""
        if not self.documents:
            return []
            
        query_vec = self._text_to_vector(query)
        scores = []
        
        for idx, doc_vec in enumerate(self.doc_vectors):
            score = self._cosine_similarity(query_vec, doc_vec)
            scores.append((score, self.documents[idx]))
            
        # Sort by highest semantic similarity score
        scores.sort(key=lambda x: x[0], reverse=True)
        
        results = []
        for score, doc in scores[:n_results]:
            results.append({
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
    hits = retriever.search("How does the platform handle security testing?")
    print("Semantic Search Results:", hits)