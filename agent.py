"""
PromptEngineering-toolkit: agent.py
Implements a true ReAct (Reasoning-Acting-Observing) loop with dynamic tool calling and memory.
"""

import json
from typing import List, Dict, Any, Callable

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.descriptions: Dict[str, str] = {}

    def register(self, name: str, func: Callable, description: str):
        self.tools[name] = func
        self.descriptions[name] = description

    def execute(self, name: str, argument: str) -> str:
        if name not in self.tools:
            return f"Error: Tool '{name}' not found."
        try:
            return str(self.tools[name](argument))
        except Exception as e:
            return f"Error executing tool '{name}': {str(e)}"

class ReActAgent:
    def __init__(self, registry: ToolRegistry, max_steps: int = 3):
        self.registry = registry
        self.max_steps = max_steps
        self.memory: List[Dict[str, str]] = []

    def run(self, goal: str) -> Dict[str, Any]:
        self.memory.append({"role": "user", "content": goal})
        steps_log = []
        
        current_step = 0
        current_thought = f"Analyze goal: {goal}"
        
        while current_step < self.max_steps:
            current_step += 1
            
            # Simple heuristic matching for demonstration/robust local execution
            chosen_tool = None
            tool_arg = goal
            
            for tool_name in self.registry.tools.keys():
                if tool_name in goal.lower() or tool_name in current_thought.lower():
                    chosen_tool = tool_name
                    break
            
            # Default fallback tool if none matched explicitly
            if not chosen_tool and self.registry.tools:
                chosen_tool = list(self.registry.tools.keys())[0]

            observation = ""
            if chosen_tool:
                observation = self.registry.execute(chosen_tool, tool_arg)

            step_record = {
                "step": current_step,
                "thought": current_thought,
                "action": chosen_tool,
                "action_input": tool_arg,
                "observation": observation
            }
            steps_log.append(step_record)
            
            # Reflect on observation
            if "Error" not in observation:
                final_answer = f"Successfully completed goal via {chosen_tool}. Result: {observation}"
                self.memory.append({"role": "assistant", "content": final_answer})
                return {
                    "status": "success",
                    "goal": goal,
                    "steps": steps_log,
                    "final_answer": final_answer
                }
            
            current_thought = f"Refining approach after observation: {observation}"

        return {
            "status": "max_steps_exceeded",
            "goal": goal,
            "steps": steps_log,
            "final_answer": "Agent reached max execution steps without clear convergence."
        }

if __name__ == "__main__":
    registry = ToolRegistry()
    registry.register("calculator", lambda x: eval(x, {"__builtins__": {}}, {}), "Evaluates mathematical expressions.")
    registry.register("search", lambda q: f"Simulated web results for: {q}", "Performs keyword search.")

    agent = ReActAgent(registry)
    res = agent.run("calculator 15 * 4")
    print(json.dumps(res, indent=2))