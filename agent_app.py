"""
sentinel-ui: agent_app.py
Core agent execution module with built-in security guardrails and audit logging.
"""

import logging
import sqlite3
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SentinelAgent")

class SentinelAgent:
    def __init__(self, db_path="sentinel_audit.db"):
        self.db_path = db_path
        self._init_db()

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
        Process incoming prompts with basic guardrail validation.
        """
        logger.info(f"Processing prompt: {prompt[:50]}...")
        
        # Simple heuristic check for prompt injection keywords
        jailbreak_triggers = ["ignore previous instructions", "system override", "bypass"]
        if any(trigger in prompt.lower() for trigger in jailbreak_triggers):
            self.log_audit(prompt, "BLOCKED", "Potential prompt injection detected")
            return {
                "status": "blocked",
                "message": "Security Guardrail Triggered: Unsafe prompt pattern detected."
            }

        self.log_audit(prompt, "APPROVED", "Passed safety checks")
        return {
            "status": "success",
            "message": f"Processed successfully: Echo -> {prompt}"
        }

if __name__ == "__main__":
    agent = SentinelAgent()
    print("SentinelAgent initialized successfully.")