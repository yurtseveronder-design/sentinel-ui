"""
sentinel-ui: agent_app.py
Security-hardened agent execution module with deterministic regex guardrails and SQLite audit logging.
"""

import logging
import sqlite3
import re
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SentinelAgent")

class SentinelAgent:
    def __init__(self, db_path="sentinel_audit.db"):
        self.db_path = db_path
        self._init_db()
        # Compile deterministic regex patterns for prompt injection and jailbreaks
        self.jailbreak_patterns = [
            re.compile(r"ignore\s+(previous|all)\s+instructions", re.IGNORECASE),
            re.compile(r"system\s+override", re.IGNORECASE),
            re.compile(r"bypass\s+guardrails", re.IGNORECASE),
            re.compile(r"reveal\s+(system|hidden)\s+prompt", re.IGNORECASE),
            re.compile(r"act\s+as\s+an\s+unrestricted", re.IGNORECASE)
        ]

    def _init_db(self):
        """Ensure audit logging table exists."""
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
        """Log agent interaction and security status to SQLite."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO audit_logs (timestamp, prompt, status, details) VALUES (?, ?, ?, ?)",
            (datetime.utcnow().isoformat(), prompt, status, details)
        )
        conn.commit()
        conn.close()

    def process_prompt(self, prompt: str) -> dict:
        """
        Process incoming prompts with deterministic regex guardrail validation.
        """
        logger.info(f"Processing prompt: {prompt[:50]}...")
        
        # Evaluate against deterministic security rules
        for pattern in self.jailbreak_patterns:
            if pattern.search(prompt):
                self.log_audit(prompt, "BLOCKED", f"Deterministic guardrail matched: {pattern.pattern}")
                return {
                    "status": "blocked",
                    "message": "Security Guardrail Triggered: Malicious prompt pattern detected via deterministic filters."
                }

        self.log_audit(prompt, "APPROVED", "Passed deterministic safety checks")
        return {
            "status": "success",
            "message": f"Processed successfully: Response generated for query."
        }

if __name__ == "__main__":
    agent = SentinelAgent()
    print("SentinelAgent initialized with deterministic guardrails.")