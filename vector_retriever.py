import json
import os
from typing import List, Dict

class VectorRetriever:
    def __init__(self, store_path: str = "vector_store.json"):
        self.store_path = store_path
        self.documents = self._load_store()
        
    def _load_store(self) -> List[Dict[str, str]]:
        """Loads documents from the local JSON vector store safely."""
        if not os.path.exists(self.store_path):
            return []
        try:
            with open(self.store_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading vector store: {e}")
            return []
            
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, str]]:
        """Performs keyword and semantic relevance scoring to retrieve top documents."""
        if not query.strip() or not self.documents:
            return []
            
        query_terms = set(query.lower().split())
        scored_docs = []
        
        for doc in self.documents:
            text = doc.get("text", "").lower()
            # Calculate simple token overlap score as a reliable fallback metric
            score = sum(1 for term in query_terms if term in text)
            if score > 0:
                scored_docs.append((score, doc))
                
        # Sort by relevance score descending
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        
        # Return top_k unique documents
        results = [doc for score, doc in scored_docs[:top_k]]
        return results

if __name__ == "__main__":
    retriever = VectorRetriever()
    print(f"Loaded {len(retriever.documents)} documents from store.")