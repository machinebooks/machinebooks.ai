# Source: The FinOps Engineer and the Machine -- Chapter 21
# Pattern: GDPR content handler for LLM responses

# services/gdpr_content_handler.py
import re


class GDPRContentHandler:
    """
    Detects probable presence of personal data in prompts.
    Adjusts retention policy based on PII risk level.
    """

    PII_INDICATORS = [
        r"\b[A-Z][a-z]+ [A-Z][a-z]+\b",     # Proper names
        r"\b[\w.+-]+@[\w-]+\.[a-zA-Z]+\b",   # Emails
        r"\b\d{8}[A-Z]\b",                    # Spanish national ID
        r"\b\d{4}\s\d{4}\s\d{4}\s\d{4}\b",   # Card numbers
    ]

    def assess_pii_risk(self, content: str) -> dict:
        detected = []
        for pattern in self.PII_INDICATORS:
            matches = re.findall(pattern, content)
            if matches:
                detected.append({"pattern": pattern, "count": len(matches)})

        risk = "high" if len(detected) >= 2 else "medium" if detected else "low"
        return {
            "risk_level": risk,
            "detected_patterns": detected,
            "retention_days": 30 if risk == "high" else 90,
        }
