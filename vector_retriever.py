import math
import re
import json
import os

class VectorRetriever:
    def __init__(self, store_path="vector_store.json", *args, **kwargs):
        self.store_path = store_path
        self.documents = self._load_documents()

    def _load_documents(self):
        if os.path.exists(self.store_path):
            try:
                with open(self.store_path, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return [
            {"id": "doc1", "text": "AI guardrails prevent prompt injection and unauthorized data exfiltration."},
            {"id": "doc2", "text": "Cosine similarity measures the angle between two semantic vectors."},
            {"id": "doc3", "text": "Local JSON persistence provides transparency and eliminates heavy database dependencies."}
        ]

    def _text_to_vector(self, text):
        words = re.findall(r'\w+', text.lower())
        vector = {}
        for word in words:
            vector[word] = vector.get(word, 0) + 1
        return vector

    def _cosine_similarity(self, vec1, vec2):
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in intersection])
        
        sum1 = sum([vec1[x] ** 2 for x in vec1.keys()])
        sum2 = sum([vec2[x] ** 2 for x in vec2.keys()])
        
        denominator = math.sqrt(sum1) * math.sqrt(sum2)
        if not denominator:
            return 0.0
        return float(numerator) / denominator

    def retrieve(self, query, top_k=2):
        if not query or not query.strip():
            return []

        query_vec = self._text_to_vector(query)
        scored_docs = []

        for doc in self.documents:
            if isinstance(doc, dict):
                text_val = doc.get("text", "")
                doc_obj = doc
            else:
                text_val = str(doc)
                doc_obj = {"id": "legacy", "text": text_val}

            doc_vec = self._text_to_vector(text_val)
            score = self._cosine_similarity(query_vec, doc_vec)
            if score > 0.0:
                scored_docs.append((score, doc_obj))

        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored_docs[:top_k]]

# Backward compatibility alias
VectorRAGRetriever = VectorRetriever