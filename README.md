# Sentinel UI

The front gateway of the Sentinel stack: it authenticates requests (API key or JWT) and passes every prompt to
[ai-sentinel](https://github.com/yurtseveronder-design/ai-sentinel) for a block-or-allow decision. The repository also
holds small experimental helpers (a vector retriever, an agent loop, a Streamlit-style app) that are not part of the gateway.

```
client -> sentinel-ui (/api/v1/secure-inference) -> ai-sentinel (/v1/scan) -> sentinel-semantic
```

## What is here

* `gateway.py`, `auth.py`, `sentinel_client.py`, `logger.py`: the gateway (tested; see `tests/`).
* `vector_retriever.py`, `agent.py`, `config.py`, `schemas.py`, `utils/`: experimental helpers with their own tests.
* Install with `pip install .` (installs the modules above); run with `uvicorn gateway:app`.

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
