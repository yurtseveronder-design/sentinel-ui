"""
sentinel-ui: gateway.py
Authentication gateway that delegates prompt scanning to ai-sentinel (or a small local check when
ai-sentinel is not configured), with structured error logging.
"""

import os

from fastapi import FastAPI, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse
import sentinel_client
from auth import SecurityManager
from logger import EnterpriseErrorHandler

MAX_BODY_BYTES = int(os.environ.get("SENTINEL_UI_MAX_BODY_BYTES", "65536"))


class BodyTooLarge(BaseException):
    """Raised inside the receive channel when more than MAX_BODY_BYTES were actually read."""


class BodyLimitMiddleware:
    """Counts the bytes actually received (chunked bodies included), not just Content-Length."""

    def __init__(self, app, max_bytes: int):
        self.app, self.max_bytes = app, max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        total, started = 0, False

        async def counting_receive():
            nonlocal total
            message = await receive()
            if message["type"] == "http.request":
                total += len(message.get("body", b""))
                if total > self.max_bytes:
                    raise BodyTooLarge()
            return message

        async def tracking_send(message):
            nonlocal started
            started = started or message["type"] == "http.response.start"
            await send(message)

        try:
            await self.app(scope, counting_receive, tracking_send)
        except BodyTooLarge:
            if not started:
                await JSONResponse({"error": "Request body too large"}, status_code=413)(scope, receive, send)


app = FastAPI(
    title="sentinel-ui gateway",
    version="1.0.0",
    description="Authentication front gateway for the Sentinel guardrail stack."
)

app.add_middleware(BodyLimitMiddleware, max_bytes=MAX_BODY_BYTES)


@app.middleware("http")
async def security_and_logging_middleware(request: Request, call_next):
    """Interception middleware to log requests and enforce gateway security policies."""
    path = request.url.path
    method = request.method
    
    # Allow health check public endpoint
    if path == "/health":
        return await call_next(request)
        
    try:
        response = await call_next(request)
        return response
    except Exception as exc:
        # Capture unhandled gateway exceptions using our enterprise error handler
        EnterpriseErrorHandler.log_api_failure(
            endpoint=path,
            method=method,
            status_code=500,
            error_message=str(exc)
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Internal gateway error"}
        )

@app.get("/health")
async def health_check():
    """Public health check endpoint for load balancers and container orchestrators."""
    return {"status": "healthy", "gateway": "operational"}

@app.post("/api/v1/secure-inference")
async def secure_inference(
    payload: dict,
    request: Request,
    x_api_key: str = Header(None),
    authorization: str = Header(None)
):
    """Protected AI inference endpoint enforcing API key or JWT token authentication."""
    # 1. Verify API Key or Bearer Token
    authenticated = False
    if x_api_key and SecurityManager.verify_api_key(x_api_key):
        authenticated = True
    elif authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        if SecurityManager.verify_jwt_token(token):
            authenticated = True
            
    if not authenticated:
        EnterpriseErrorHandler.log_api_failure(
            endpoint="/api/v1/secure-inference",
            method="POST",
            status_code=401,
            request_body=payload,
            error_message="Unauthorized access attempt - Invalid or missing credentials"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Valid API Key or JWT token required"
        )
        
    # 2. Prompt-injection guardrail. If ai-sentinel is configured it is the only authority: when it
    #    cannot give a verdict (down, timeout, 401, 429, 5xx) the request is refused, not waved through.
    #    The small local check is used only in standalone mode (AI_SENTINEL_URL unset).
    prompt = payload.get("prompt", "")
    if not isinstance(prompt, str):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="prompt must be a string")
    guardrail = {"source": "local"}
    if sentinel_client.enabled():
        try:
            verdict = sentinel_client.scan(prompt, request_id=request.headers.get("x-request-id"))
        except sentinel_client.SentinelUnavailable as exc:
            EnterpriseErrorHandler.log_api_failure(
                endpoint="/api/v1/secure-inference",
                method="POST",
                status_code=503,
                request_body=payload,
                error_message=f"Guardrail service unavailable, request refused: {exc}",
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Guardrail service unavailable; the request was refused.",
            )
        blocked = verdict.get("action") == "BLOCK"
        guardrail = {
            "source": "ai-sentinel",
            "risk_score": verdict.get("risk_score"),
            "semantic": verdict.get("semantic"),
        }
    else:
        blocked = "ignore previous instructions" in prompt.lower() or "system prompt" in prompt.lower()

    if blocked:
        EnterpriseErrorHandler.log_api_failure(
            endpoint="/api/v1/secure-inference",
            method="POST",
            status_code=400,
            request_body=payload,
            error_message="Prompt injection attack detected"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security Violation: Prompt injection pattern detected and blocked."
        )

    return {
        "status": "success",
        "message": "Inference request passed security guardrails.",
        "processed_prompt": prompt,
        "guardrail": guardrail,
    }
