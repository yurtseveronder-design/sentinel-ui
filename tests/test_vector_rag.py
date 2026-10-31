from vector_retriever import VectorRAGRetriever

def test_semantic_vector_search():
    retriever = VectorRAGRetriever(collection_name="test_knowledge")
    
    # Add domain knowledge chunks
    retriever.add_documents(
        [
            "The authorization token expires after 3600 seconds of inactivity.",
            "Guardrails intercept malicious prompt injection attacks before reaching the core LLM."
        ],
        ["id_token", "id_security"]
    )
    
    # Query using semantic phrasing that maps to the token document vocabulary
    results = retriever.search("How many seconds before authorization token expires?", n_results=1)
    
    assert len(results) > 0
    # Verify that semantic search successfully retrieves the token expiration document
    assert "token expires" in results[0]["document"]
    assert results[0]["semantic_score"] > 0.0