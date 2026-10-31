"""
sentinel-ui: agent_app.py
Autonomous Tool-Using Agent implementation with secure tool dispatch and guardrails.
"""

import json
import logging
from typing import Dict, Any, Callable, Optional

logger = logging.getLogger("sentinel-ui.agent")

class SecureAgentToolRegistry:
    """Registry of safe, sandboxed tools available to the autonomous agent."""
    
    def __init__(self):
        self._tools: Dict[str, Callable[[Any], str]] = {}

    def register(self, name: str, func: Callable[[Any], str]) -> None:
        self._tools[name] = func

    def get(self, name: str) -> Optional[Callable[[Any], str]]:
        return self._tools.get(name)

    def list_tools(self) -> list:
        return list(self._tools.keys())


class AutonomousAgent:
    """Autonomous agent capable of reasoning, tool selection, and secure execution."""

    def __init__(self, registry: SecureAgentToolRegistry):
        self.registry = registry

    def execute_task(self, goal: str, tool_name: str, tool_input: Any) -> Dict[str, Any]:
        """Execute a reasoned task by safely invoking a registered tool."""
        logger.info(f"Agent received goal: '{goal}' utilizing tool: '{tool_name}'")
        
        tool = self.registry.get(tool_name)
        if not tool:
            logger.error(f"Tool not found or unauthorized: {tool_name}")
            return {
                "status": "error",
                "goal": goal,
                "error": f"Tool '{tool_name}' is not registered or authorized."
            }

        try:
            result = tool(tool_input)
            return {
                "status": "success",
                "goal": goal,
                "tool_used": tool_name,
                "result": result
            }
        except Exception as e:
            logger.error(f"Tool execution failed: {str(e)}")
            return {
                "status": "error",
                "goal": goal,
                "error": str(e)
            }