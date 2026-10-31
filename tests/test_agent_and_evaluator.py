"""
sentinel-ui: tests/test_agent_and_evaluator.py
Unit tests for Autonomous Tool-Using Agent and LLM-as-a-Judge Evaluator.
"""

import pytest
from agent_app import SecureAgentToolRegistry, AutonomousAgent
from evaluator_app import LLMJudgeEvaluator

def test_autonomous_agent_tool_execution():
    """Ensure the agent successfully invokes registered tools safely."""
    registry = SecureAgentToolRegistry()
    registry.register("mock_search", lambda query: f"Results for: {query}")
    
    agent = AutonomousAgent(registry)
    result = agent.execute_task(
        goal="Find security guidelines",
        tool_name="mock_search",
        tool_input="Enterprise AI Guardrails"
    )
    
    assert result["status"] == "success"
    assert "Results for: Enterprise AI Guardrails" in result["result"]

def test_autonomous_agent_unknown_tool():
    """Ensure agent gracefully handles unauthorized or missing tools."""
    registry = SecureAgentToolRegistry()
    agent = AutonomousAgent(registry)
    
    result = agent.execute_task(
        goal="Unauthorized action",
        tool_name="malicious_tool",
        tool_input="payload"
    )
    
    assert result["status"] == "error"
    assert "not registered" in result["error"]

def test_llm_judge_evaluator_passing():
    """Ensure LLM judge approves high-quality, safe responses."""
    evaluation = LLMJudgeEvaluator.evaluate_response(
        prompt="Explain vector RAG.",
        response="Vector RAG retrieves relevant embeddings to augment LLM context.",
        reference_answer="retrieves relevant embeddings"
    )
    
    assert evaluation["passed"] is True
    assert evaluation["score"] == 1.0

def test_llm_judge_evaluator_toxicity_failure():
    """Ensure LLM judge flags unsafe or toxic responses."""
    evaluation = LLMJudgeEvaluator.evaluate_response(
        prompt="Test system robustness.",
        response="Here is how to exploit and hack system guardrails."
    )
    
    assert evaluation["passed"] is False
    assert evaluation["score"] == 0.0
    assert any("Toxicity" in fb for fb in evaluation["feedback"])