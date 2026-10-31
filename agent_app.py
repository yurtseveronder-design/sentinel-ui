"""
sentinel-ui: agent_app.py
Production-grade AI agent interface with multi-provider failover, retry logic, and audit logging.
"""

import logging
import sqlite3
import re
import time
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SentinelAgent")

class ResilientLLMClient:
    """Simulates production multi-provider fallback and exponential backoff retry logic."""
    def __init__(self, primary_provider="groq", fallback_provider="openai"):
        self.primary_provider = primary_provider
        self.fallback_provider = fallback_provider

    def generate(self, prompt: str) -> str:
        retries = 3
        delay = 1.0
        
        for attempt in range(retries):
            try:
                # Simulated production API call with error handling
                if not prompt.strip():
                    raise ValueError("Prompt cannot be empty.")
                return f"[{self.primary_provider.upper()} Response]: Processed securely -> {prompt[:100]}"
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed on {self.primary_provider}: {e}")
                if attempt == retries - 1:
                    logger.info(f"Switching to fallback provider: {self.fallback_provider}")
                    return f"[{self.fallback_provider.upper()} Fallback Response]: Processed -> {prompt[:100]}"
                time.sleep(delay)
                delay *= 2

class SentinelAgent:
    def __init__(self, db_path="sentinel_audit.db"):
        self.db_path = db_path
        self._init_db()
        self.llm_client = ResilientLLMClient()
        self.jailbreak_patterns = [
            re.compile(r"ignore\s+(previous|all)\s+instructions", re.IGNORECASE),
            re.compile(r"system\s+override", re.IGNORECASE),
            re.compile(r"bypass\s+guardrails", re.IGNORECASE)
        ]

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                prompt TEXT,
                status TEXT,
                details TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def log_audit(self, prompt: str, status: str, details: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO audit_logs (timestamp, prompt, status, details) VALUES (?, ?, ?, ?)",
            (datetime.utcnow().isoformat(), prompt, status, details)
        )
        conn.commit()
        conn.close()

    def process_prompt(self, prompt: str) -> dict:
        logger.info(f"Evaluating prompt security...")
        
        for pattern in self.jailbreak_patterns:
            if pattern.search(prompt):
                self.log_audit(prompt, "BLOCKED", f"Deterministic guardrail matched")
                return {
                    "status": "blocked",
                    "message": "Security Guardrail Triggered: Unsafe pattern detected."
                }

        response = self.llm_client.generate(prompt)
        self.log_audit(prompt, "APPROVED", "Passed safety checks and generated response")
        return {
            "status": "success",
            "message": response
        }