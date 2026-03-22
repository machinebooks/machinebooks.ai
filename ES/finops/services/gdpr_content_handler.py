# Extraído de: LibroFinOps/cap-21-aiact-auditoria.md
# services/gdpr_content_handler.py
import re


class GDPRContentHandler:
    """
    Detecta presencia probable de datos personales en prompts.
    Ajusta la política de retención según el nivel de riesgo PII.
    """

    PII_INDICATORS = [
        r"\b[A-Z][a-z]+ [A-Z][a-z]+\b",     # Nombres propios
        r"\b[\w.+-]+@[\w-]+\.[a-zA-Z]+\b",   # Emails
        r"\b\d{8}[A-Z]\b",                    # DNI español
        r"\b\d{4}\s\d{4}\s\d{4}\s\d{4}\b",   # Números de tarjeta
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
