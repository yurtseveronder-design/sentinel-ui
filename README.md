\# 🛡️ Sentinel-UI: Enterprise AI Security \& Testing Framework



`sentinel-ui` is a robust, production-ready framework designed for automated API testing, deterministic AI guardrail enforcement, and persistent semantic vector RAG validation.



\## 🚀 Key Architectural Features



\- \*\*Deterministic Security Guardrails\*\*: Multi-layered regex and pattern matching to intercept prompt injections, system overrides, and jailbreaks before they reach downstream models.

\- \*\*Resilient Multi-Provider Client\*\*: Automated error recovery, exponential backoff retries, and seamless failover between primary and secondary LLM providers.

\- \*\*Persistent Vector Retrieval Pipeline\*\*: Disk-backed semantic vector store utilizing custom cosine similarity scoring for high-fidelity RAG evaluation.

\- \*\*SQLite Audit Logging\*\*: Complete traceability and logging of all agent interactions and security block events.

\- \*\*Comprehensive Test Suite\*\*: Automated unit and integration testing via `pytest`.



\## 📦 Installation



Clone the repository and install in editable mode:

```bash

git clone \[https://github.com/yurtseveronder-design/sentinel-ui.git](https://github.com/yurtseveronder-design/sentinel-ui.git)

cd sentinel-ui

pip install -e .

