# Source: The Consultant and the Machine -- Chapter 23
# Pattern: Confidentiality: classification, sanitization, routing
import anthropic
import re
from dataclasses import dataclass
from enum import Enum

class SensitivityLevel(Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

@dataclass
class ClassificationResult:
    level: SensitivityLevel
    reasons: list[str]
    entities_found: list[str]
    recommendation: str  # "api_direct", "api_sanitized", "local_only"

# Deterministic patterns for fast detection
RESTRICTED_PATTERNS = {
    "dni_nie": r"\b\d{8}[A-Z]\b|\b[XYZ]\d{7}[A-Z]\b",
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "ip_address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "credit_card": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
    "iban": r"\b[A-Z]{2}\d{2}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}\b",
    "phone_spain": r"\b(?:\+34|0034)?\s?[6-9]\d{8}\b",
}

CONFIDENTIAL_KEYWORDS = [
    "vulnerabilidad", "hallazgo", "brecha", "incidente",
    "contraseña", "credencial", "organigrama", "nómina",
    "expediente", "sanción", "despido", "reclamación",
]

def classify_deterministic(text: str) -> tuple[SensitivityLevel, list[str]]:
    """Fast classification based on regex patterns."""
    entities = []
    for name, pattern in RESTRICTED_PATTERNS.items():
        matches = re.findall(pattern, text)
        if matches:
            entities.extend([f"{name}: {m[:4]}***" for m in matches])

    if entities:
        return SensitivityLevel.RESTRICTED, entities

    for keyword in CONFIDENTIAL_KEYWORDS:
        if keyword.lower() in text.lower():
            return SensitivityLevel.CONFIDENTIAL, [keyword]

    return SensitivityLevel.PUBLIC, []

# --- Block 2 ---

def classify_semantic(text: str) -> ClassificationResult:
    """Semantic classification with Claude for ambiguous cases."""
    client = anthropic.Anthropic()

    response = client.messages.create(
        model="claude-haiku-4-5",  # Lightweight model for classification
        max_tokens=512,
        system="""You are a data sensitivity classifier for consulting.
Evaluate the fragment and respond in JSON with:
- level: "public", "internal", "confidential", "restricted"
- reasons: list of classification reasons
- entities_found: sensitive entities detected

Criteria:
- RESTRICTED: personal data, credentials, critical vulnerabilities
- CONFIDENTIAL: identifiable client information, audit findings
- INTERNAL: methodology, generic patterns, templates
- PUBLIC: regulations, standards, published information""",
        messages=[{"role": "user", "content": f"Classify:\n\n{text[:2000]}"}]
    )

    import json
    data = json.loads(response.content[0].text)
    level = SensitivityLevel(data["level"])
    route = {
        SensitivityLevel.PUBLIC: "api_direct",
        SensitivityLevel.INTERNAL: "api_direct",
        SensitivityLevel.CONFIDENTIAL: "api_sanitized",
        SensitivityLevel.RESTRICTED: "local_only",
    }
    return ClassificationResult(
        level=level,
        reasons=data.get("reasons", []),
        entities_found=data.get("entities_found", []),
        recommendation=route[level],
    )

# --- Block 3 ---

from dataclasses import field

@dataclass
class SanitizationMap:
    """Reversible sanitization map to restore original data."""
    replacements: dict[str, str] = field(default_factory=dict)
    _counter: dict[str, int] = field(default_factory=dict)

    def replace(self, original: str, category: str) -> str:
        if original in self.replacements:
            return self.replacements[original]
        self._counter[category] = self._counter.get(category, 0) + 1
        placeholder = f"[{category.upper()}_{self._counter[category]}]"
        self.replacements[original] = placeholder
        return placeholder

    def restore(self, sanitized_text: str) -> str:
        """Restores original text after receiving API response."""
        result = sanitized_text
        for original, placeholder in self.replacements.items():
            result = result.replace(placeholder, original)
        return result

def sanitize_text(text: str, san_map: SanitizationMap) -> str:
    """Sanitizes text by replacing entities with generic markers."""
    result = text

    # Replace deterministic patterns
    for category, pattern in RESTRICTED_PATTERNS.items():
        for match in re.finditer(pattern, result):
            original = match.group()
            placeholder = san_map.replace(original, category)
            result = result.replace(original, placeholder)

    # Replace known project organization names
    # (loaded from project configuration)
    project_entities = load_project_entities()  # {"Central Bank": "org", ...}
    for entity, category in project_entities.items():
        if entity in result:
            placeholder = san_map.replace(entity, category)
            result = result.replace(entity, placeholder)

    return result

# --- Block 4 ---

import subprocess

def route_request(
    text: str,
    task: str,
    project_config: dict,
) -> str:
    """Routes the request based on sensitivity classification."""

    # Step 1: deterministic classification
    level, entities = classify_deterministic(text)

    # Step 2: if nothing detected, semantic classification
    if level == SensitivityLevel.PUBLIC and len(text) > 200:
        result = classify_semantic(text)
        level = result.level

    # Step 3: route based on level
    if level == SensitivityLevel.RESTRICTED:
        # Local processing only with Ollama
        return process_local(text, task)

    elif level == SensitivityLevel.CONFIDENTIAL:
        # Sanitize and send to API
        san_map = SanitizationMap()
        clean_text = sanitize_text(text, san_map)
        response = process_api(clean_text, task)
        return san_map.restore(response)

    else:
        # Public or internal: direct API
        return process_api(text, task)

def process_local(text: str, task: str) -> str:
    """Processes with local model via Ollama."""
    import requests
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3:70b",
            "prompt": f"Task: {task}\n\nText:\n{text}",
            "stream": False,
        },
        timeout=120,
    )
    return response.json()["response"]

def process_api(text: str, task: str) -> str:
    """Processes with Claude API."""
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": f"Task: {task}\n\nText:\n{text}",
        }],
    )
    return response.content[0].text
