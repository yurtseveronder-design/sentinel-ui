# Sentinel UI

An agentic interface and utility toolkit designed for vector retrieval, local model management, and interactive AI experimentation.

## What It Solves
When building with local or agentic AI models, you need a straightforward command center to handle vector lookups, prompt toolkits, and autonomous loops without getting bogged down in heavy, complex UI frameworks.

## Core Features
* **Agentic Workflows (`agentic-flow/`):** Implements autonomous loops and task handling.
* **Prompt Engineering Toolkit (`PromptEngineering-toolkit/`):** Modular templates and utilities for managing prompts.
* **Vector Retrieval Utilities (`utils/`):** Custom embedding and retrieval functions built for local performance.
* **Automated Testing & CI/CD:** Verified and tested continuously via GitHub Actions workflows.

## Project Structure
* `agentic-flow/`: Core autonomous agent logic and execution loops.
* `PromptEngineering-toolkit/`: Reusable prompt templates and formatting tools.
* `utils/`: Helper scripts for vector processing and environment handling.
* `tests/`: Automated test suite for local validation.
* `.github/workflows/`: CI pipeline configuration.

## Gateway authentication
`gateway.py` protects `/api/v1/secure-inference` with an API key (`x-api-key` header) or an HS256 JWT (`Authorization: Bearer ...`). Credentials are never stored in the code; set them as environment variables (see `.env.example`):

* `SENTINEL_API_KEYS`: comma-separated accepted API keys.
* `SENTINEL_JWT_SECRET`: signing secret for JWTs.

If a variable is unset, that method rejects every request. `SecurityManager.create_jwt_token()` issues tokens for local use and tests.

## Delegating to ai-sentinel

By default `gateway.py` uses a small built-in prompt-injection check. Point it at the detection engine and it delegates instead:

* `AI_SENTINEL_URL`: base URL of [ai-sentinel](https://github.com/yurtseveronder-design/ai-sentinel), for example `http://localhost:8000`.
* `AI_SENTINEL_API_KEY`: key sent to ai-sentinel as `X-API-Key`.
* `AI_SENTINEL_TIMEOUT`: seconds to wait (default `3`).

The response's `guardrail` field says which engine decided (`ai-sentinel` or `local`) and includes the semantic analysis when ai-sentinel is running with [sentinel-semantic](https://github.com/yurtseveronder-design/sentinel-semantic). **Fail closed:** once `AI_SENTINEL_URL` is set, ai-sentinel is the only authority. If it is unreachable, times out, or answers 401, 429 or 5xx, the gateway answers `503` and refuses the request. The small local check runs only when `AI_SENTINEL_URL` is unset (standalone mode) and is far weaker than ai-sentinel; do not rely on it. Request bodies over `SENTINEL_UI_MAX_BODY_BYTES` (default 65536) get `413`. Logs record prompts as length and a short hash only.

## Quick Start
1. Clone the repository and configure your `.env` file using `.env.example`.
2. Install dependencies and run the test suite:
   ```bash
   python -m pytest -v
