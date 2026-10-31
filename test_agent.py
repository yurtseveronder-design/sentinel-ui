"""
PromptEngineering-toolkit: test_agent.py
Unit tests for the ReAct Agent and Tool Registry.
"""

import pytest
from agent import ToolRegistry, ReActAgent

def test_tool_registry_execution():
    registry = ToolRegistry()
    registry.register("add", lambda x: str(int(x) + 5), "Adds 5 to input.")
    
    result = registry.execute("add", "10")
    assert result == "15"

def test_tool_registry_not_found():
    registry = ToolRegistry()
    result = registry.execute("nonexistent", "test")
    assert "Error" in result

def test_react_agent_execution():
    registry = ToolRegistry()
    registry.register("calculator", lambda x: "45", "Performs math.")
    
    agent = ReActAgent(registry)
    response = agent.run("calculator 15 * 3")
    
    assert response["status"] == "success"
    assert len(response["steps"]) > 0
    assert "45" in response["final_answer"]