import streamlit as st
import json
import csv
import io
from sentinel_core import SentinelEngine

st.set_page_config(page_title="SentinelUI", page_icon="🛡️", layout="centered")
st.title("SentinelUI")
st.markdown("*A calm, human-centric telemetry and guardrail evaluation dashboard.*")
st.markdown("---")

engine = SentinelEngine()
tab1, tab2, tab3 = st.tabs(["Interactive Evaluator", "CI/CD Security Test Suite", "Audit History"])

with tab1:
    with st.form("eval_form"):
        st.subheader("Prompt Evaluation Input")
        prompt = st.text_area("Enter a prompt:", value="What is the status of the automated testing pipeline?")
        submitted = st.form_submit_button("Run Sentinel Audit", type="primary")
    if submitted:
        res = engine.simulate_llm_call(prompt)
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        c1.metric("Latency", f"{res.latency_seconds}s")
        c1.metric("Faithfulness", res.faithfulness_score)
        c2.metric("Tokens", res.token_count)
        c2.metric("Cost", f"${res.estimated_cost}")
        c3.metric("Status", "PASS" if res.is_safe else "FLAGGED")
        st.info(res.response)

with tab2:
    st.subheader("CI/CD Security Test Suite")
    st.markdown("Run a predefined batch of security edge-cases and prompt-injection tests.")
    if st.button("Execute Full Test Suite", type="primary"):
        suite_results = engine.run_test_suite()
        passed_count = sum(1 for r in suite_results if r.is_safe)
        st.success(f"Test Suite Complete: {passed_count}/{len(suite_results)} security checks passed successfully.")
        for i, r in enumerate(suite_results, 1):
            label = "PASS" if r.is_safe else "FLAGGED"
            with st.expander(f"Test #{i} - {label}: {r.prompt[:35]}..."):
                st.text(r.response)
                st.caption(f"Latency: {r.latency_seconds}s | Tokens: {r.token_count} | Faithfulness: {r.faithfulness_score}")

with tab3:
    st.subheader("Persistent Audit Log & Export")
    st.markdown("Review past evaluations and export compliance reports.")
    history = engine.get_history(limit=50)
    
    if not history:
        st.info("No audit history found yet. Run an evaluation or test suite!")
    else:
        col_exp1, col_exp2 = st.columns(2)
        
        # JSON export
        json_data = json.dumps(history, indent=4)
        col_exp1.download_button(
            label="📥 Download JSON Report",
            data=json_data,
            file_name="sentinel_audit_report.json",
            mime="application/json"
        )
        
        # CSV export
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=history[0].keys())
        writer.writeheader()
        writer.writerows(history)
        csv_data = output.getvalue()
        
        col_exp2.download_button(
            label="📥 Download CSV Report",
            data=csv_data,
            file_name="sentinel_audit_report.csv",
            mime="text/csv"
        )
        
        st.markdown("---")
        for row in history:
            status_label = "✅ PASS" if row['is_safe'] else "🚨 FLAGGED"
            with st.expander(f"[{row['timestamp']}] {status_label} - Prompt: {row['prompt'][:40]}..."):
                st.write(f"**Response:** {row['response']}")
                col_a, col_b, col_c, col_d = st.columns(4)
                col_a.metric("Latency", f"{row['latency']}s")
                col_b.metric("Faithfulness", row['faithfulness'])
                col_c.metric("Tokens", row['tokens'])
                col_d.metric("Cost", f"${row['cost']}")
