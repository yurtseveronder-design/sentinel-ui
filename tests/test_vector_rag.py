import pytest
from vector_retriever import VectorRetriever

def test_vector_retriever_initialization():
    retriever = VectorRetriever()
    assert len(retriever.documents) > 0

def test_vector_retriever_search():
    retriever = VectorRetriever()
    results = retriever.retrieve("AI guardrails")
    assert isinstance(results, list)
    if len(results) > 0:
        assert "id" in results[0]
        assert "text" in results[0]

def test_vector_retriever_empty_query():
    retriever = VectorRetriever()
    results = retriever.retrieve("")
    assert results == []