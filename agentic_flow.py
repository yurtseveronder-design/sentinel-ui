"""
sentinel-ui: agentic_flow.py
Interactive Streamlit Dashboard for Prompt Engineering Toolkit, Autonomous Agent, and LLM-as-a-Judge.
"""

import streamlit as st
import sqlite3
import datetime
from agent_app import SecureAgentToolRegistry, AutonomousAgent
from evaluator_app import LLMJudgeEvaluator

# Initialize SQLite Telemetry Database with a fresh unique name
def init_db():
    conn = sqlite3.connect("audit_telemetry.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prompt_telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            mode TEXT,
            prompt TEXT,
            response TEXT,
            score REAL,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def log_telemetry(mode: str, prompt: str, response: str, score: float, status: str):
    conn = sqlite3.connect("audit_telemetry.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO prompt_telemetry (timestamp, mode, prompt, response, score, status) VALUES (?, ?, ?, ?, ?, ?)",
        (str(datetime.datetime.now()), mode, prompt, response, score, status)
    )
    conn.commit()
    conn.close()

st.set_page_config(
    page_title="sentinel-ui: Prompt Engineering & Agent Toolkit",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ sentinel-ui: Prompt Engineering & Agentic Toolkit")
st.markdown("Enterprise-grade prompt chaining, autonomous tool execution, and LLM-as-a-Judge evaluation dashboard.")

# Sidebar Navigation
tab = st.sidebar.radio("Navigation", ["Autonomous Agent", "LLM-as-a-Judge Evaluator", "Prompt Chaining & Telemetry"])

# --- TAB 1: AUTONOMOUS AGENT ---
if tab == "Autonomous Agent":
    st.header("🤖 Autonomous Tool-Using Agent")
    st.markdown("Dispatch goals to sandboxed tools with automated security guardrails.")

    registry = SecureAgentToolRegistry()
    registry.register("mock_search", lambda q: f"Secure web search results for: '{q}' (Verified Source)")
    registry.register("python_calculator", lambda expr: f"Computed Result: {eval(expr, {'__builtins__': {}}, {})}")

    selected_tool = st.selectbox("Select Tool", registry.list_tools())
    goal = st.text_input("Agent Goal", "Research enterprise AI security standards")
    tool_input = st.text_input("Tool Input / Parameter", "AI Guardrails")

    if st.button("Execute Agent Task"):
        agent = AutonomousAgent(registry)
        result = agent.execute_task(goal, selected_tool, tool_input)
        
        if result["status"] == "success":
            st.success(f"Task Completed Successfully using `{result['tool_used']}`!")
            st.json(result)
            log_telemetry("Autonomous Agent", goal, str(result), 1.0, "SUCCESS")
        else:
            st.error(f"Execution Failed: {result['error']}")
            log_telemetry("Autonomous Agent", goal, result['error'], 0.0, "FAILED")

# --- TAB 2: LLM-AS-A-JUDGE EVALUATOR ---
elif tab == "LLM-as-a-Judge Evaluator":
    st.header("⚖️ LLM-as-a-Judge Evaluation Engine")
    st.markdown("Audit AI responses against security rubrics, toxicity thresholds, and reference context.")

    eval_prompt = st.text_input("Original Prompt", "Explain vector RAG architecture.")
    eval_response = st.text_area("AI Response to Evaluate", "Vector RAG retrieves relevant embeddings from a vector store to augment LLM context.")
    reference_answer = st.text_input("Reference Answer (Optional)", "retrieves relevant embeddings")

    if st.button("Run Judge Evaluation"):
        evaluation = LLMJudgeEvaluator.evaluate_response(eval_prompt, eval_response, reference_answer)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Judge Score", f"{evaluation['score'] * 100:.0f}%")
        with col2:
            st.metric("Status", "PASSED" if evaluation["passed"] else "FAILED")

        st.subheader("Evaluator Feedback:")
        for fb in evaluation["feedback"]:
            if evaluation["passed"]:
                st.success(fb)
            else:
                st.error(fb)

        log_telemetry("LLM-as-a-Judge", eval_prompt, eval_response, evaluation["score"], "PASSED" if evaluation["passed"] else "FAILED")

# --- TAB 3: PROMPT CHAINING & TELEMETRY ---
else:
    st.header("⛓️ Prompt Chaining & Audit Telemetry")
    st.markdown("Inspect SQLite telemetry logs of all agent executions and judge evaluations.")

    conn = sqlite3.connect("audit_telemetry.db")
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, mode, prompt, score, status FROM prompt_telemetry ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    if rows:
        st.dataframe(
            [{"Timestamp": r[0], "Mode": r[1], "Prompt": r[2], "Score": r[3], "Status": r[4]} for r in rows],
            use_container_width=True
        )
    else:
        st.info("No telemetry logs recorded yet. Run some tasks or evaluations above!")