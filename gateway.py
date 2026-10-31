"""
sentinel-ui: gateway.py
Live production API gateway with authentication, security guardrails, and structured error logging.
"""

from fastapi import FastAPI, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse
from auth import SecurityManager
from logger import EnterpriseErrorHandler

app = FastAPI(
    title="sentinel-ui Enterprise API Gateway",
    version="1.0.0",
    description="Live production security gateway and AI guardrail enforcement layer."
)

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
            content={"error": "Internal gateway error", "details": str(exc)}
        )

@app.get("/health")
async def health_check():
    """Public health check endpoint for load balancers and container orchestrators."""
    return {"status": "healthy", "gateway": "operational"}

@app.post("/api/v1/secure-inference")
async def secure_inference(
    payload: dict,
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
        
    # 2. Check for Prompt Injection / Guardrails
    prompt = payload.get("prompt", "")
    if "ignore previous instructions" in prompt.lower() or "system prompt" in prompt.lower():
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
        "processed_prompt": prompt
    }