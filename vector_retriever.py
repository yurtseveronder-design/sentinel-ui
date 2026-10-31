import math
import re

class VectorRetriever:
    def __init__(self, documents=None):
        # Sample structured knowledge base for AI security and guardrails
        self.documents = documents or [
            {"id": "doc1", "text": "AI guardrails prevent prompt injection and unauthorized data exfiltration."},
            {"id": "doc2", "text": "RAG systems retrieve relevant context from a vector database before generation."},
            {"id": "doc3", "text": "LLM evaluation requires systematic testing of toxicity, latency, and accuracy."},
            {"id": "doc4", "text": "Test automation frameworks validate API endpoints and response schemas efficiently."}
        ]

    def _text_to_vector(self, text):
        # Convert text into a simple term-frequency vector dictionary
        words = re.findall(r'\w+', text.lower())
        vector = {}
        for word in words:
            vector[word] = vector.get(word, 0) + 1
        return vector

    def _cosine_similarity(self, vec1, vec2):
        # Calculate true cosine similarity between two text vectors
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in intersection])
        
        sum1 = sum([vec1[x] ** 2 for x in vec1.keys()])
        sum2 = sum([vec2[x] ** 2 for x in vec2.keys()])
        
        denominator = math.sqrt(sum1) * math.sqrt(sum2)
        if not denominator:
            return 0.0
        return float(numerator) / denominator

    def search(self, query, top_k=2):
        if not query.strip() or not self.documents:
            return []

        query_vec = self._text_to_vector(query)
        scored_docs = []

        for doc in self.documents:
            doc_vec = self._text_to_vector(doc.get("text", ""))
            score = self._cosine_similarity(query_vec, doc_vec)
            if score > 0.0:
                scored_docs.append((score, doc))

        # Sort by cosine similarity score descending
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored_docs[:top_k]]

if __name__ == "__main__":
    retriever = VectorRetriever()
    results = retriever.search("How do guardrails stop prompt injection?")
    print("Vector Search Results:", results)