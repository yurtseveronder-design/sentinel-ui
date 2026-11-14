"""Client for the ai-sentinel gateway (the detection engine behind this front gateway).

Enabled by AI_SENTINEL_URL (for example http://localhost:8000). Credentials come from
AI_SENTINEL_API_KEY. Standard library only.

scan() returns None only when ai-sentinel is NOT configured (standalone mode). When it is
configured, any failure to obtain a verdict (unreachable, timeout, 401, 429, 5xx, bad JSON)
raises SentinelUnavailable: the caller must refuse the request, never wave it through.
"""

import json
import logging
import os
import urllib.request
from typing import Any, Dict, Optional

log = logging.getLogger("sentinel-ui")


class SentinelUnavailable(RuntimeError):
    """ai-sentinel is configured but did not give a usable verdict."""


def enabled() -> bool:
    return bool(os.environ.get("AI_SENTINEL_URL"))


def scan(prompt: str, request_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    base = os.environ.get("AI_SENTINEL_URL")
    if not base:
        return None
    headers = {"Content-Type": "application/json", "X-API-Key": os.environ.get("AI_SENTINEL_API_KEY", "")}
    if request_id:
        headers["X-Request-ID"] = request_id
    request = urllib.request.Request(
        base.rstrip("/") + "/v1/scan",
        data=json.dumps({"prompt": prompt}).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        timeout = float(os.environ.get("AI_SENTINEL_TIMEOUT", "3"))
        with urllib.request.urlopen(request, timeout=timeout) as response:  # nosec B310 - operator-configured URL
            verdict = json.loads(response.read().decode("utf-8"))
    except Exception as exc:  # HTTPError covers 401/429/5xx: none of them is permission
        raise SentinelUnavailable(f"{type(exc).__name__}: {exc}") from exc
    if not isinstance(verdict, dict) or verdict.get("action") not in ("ALLOW", "BLOCK"):
        raise SentinelUnavailable("ai-sentinel returned a response without a valid action")
    return verdict
