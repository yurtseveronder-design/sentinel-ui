"""
sentinel-ui: evaluator_app.py
Evaluation engine for scoring guardrail compliance and hallucination thresholds.
"""

class SecurityEvaluator:
    @staticmethod
    def evaluate_hallucination(response_text: str, expected_keywords: list) -> float:
        """
        Evaluate response against required domain keywords to calculate hallucination risk score.
        Returns a score between 0.0 (high hallucination/off-topic) and 1.0 (fully grounded).
        """
        if not response_text or not expected_keywords:
            return 0.0
        
        text_lower = response_text.lower()
        matches = sum(1 for kw in expected_keywords if kw.lower() in text_lower)
        score = matches / len(expected_keywords)
        return round(score, 2)

    @staticmethod
    def evaluate_guardrail(prompt: str) -> bool:
        """
        Returns True if safe, False if prompt injection is suspected.
        """
        blocked_phrases = ["ignore previous instructions", "override"]
        return not any(phrase in prompt.lower() for phrase in blocked_phrases)

if __name__ == "__main__":
    evaluator = SecurityEvaluator()
    score = evaluator.evaluate_hallucination("The user lifecycle API passed all tests.", ["user", "API"])
    print(f"Sample Hallucination Score: {score}")