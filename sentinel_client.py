"""Client for the ai-sentinel gateway (the detection engine behind this front gateway).

Enabled by AI_SENTINEL_URL (for example http://localhost:8000). Credentials come from
AI_SENTINEL_API_KEY. Standard library only. Returns None when the service is not
configured or cannot be reached, in which case the caller falls back to its local check.
"""

import json
import logging
import os
import urllib.request
from typing import Any, Dict, Optional

log = logging.getLogger("sentinel-ui")


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
            return json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        log.warning("ai-sentinel unavailable, using local guardrail: %s", exc)
        return None
