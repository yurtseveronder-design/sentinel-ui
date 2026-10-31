# Sentinel-UI

A lightweight AI security guardrail and semantic retrieval interface built with Python and Streamlit.

## 🛠️ Current Architecture & Features
* **Semantic Vector Retrieval:** Uses custom Python-based term frequency vectors and mathematical cosine similarity scoring to match user queries against knowledge bases.
* **Local Data Store:** Implements a transparent, file-based local JSON store (`vector_store.json`) for data persistence rather than an external vector database.
* **Security & Guardrails:** Validates inputs against common prompt injection and unauthorized data exfiltration patterns.
* **Testing:** Includes Pytest units for deterministic guardrail checks.

---

## 🚧 Scope & Limitations
* Designed as a focused portfolio project demonstrating practical AI security concepts and custom math implementation.
* Not built for massive enterprise-scale embedding clusters; optimized for local development and transparency.

## Getting Started
1. Install dependencies:
   ```bash
   pip install -r requirements.txt