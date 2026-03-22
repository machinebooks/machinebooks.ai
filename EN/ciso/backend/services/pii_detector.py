# Chapter 6 — PII Detector with Spanish document patterns
#
# Detects personal data in free text: DNI, NIE, IBAN, credit cards,
# emails, phone numbers, Social Security numbers.
# Operates in "warn-only" mode by default: logs alerts but does not
# block operations. 60-70% initial false positive rate that decreases
# as patterns are refined.

import re
import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class PIIMatch:
    """A single PII detection with type, position, and masked value."""
    pii_type: str
    start: int
    end: int
    original: str
    masked: str


@dataclass
class PIIResult:
    """Result of a PII scan on a text input."""
    has_pii: bool
    matches: list[PIIMatch] = field(default_factory=list)
    types_found: list[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        if not self.has_pii:
            return "No PII detected"
        types = ", ".join(sorted(set(self.types_found)))
        return f"PII detected: {types} ({len(self.matches)} matches)"


class PIIDetector:
    """Detects personal data patterns in text.

    Focused on Spanish/European document formats:
    - DNI: 8 digits + letter (e.g., 12345678A)
    - NIE: X/Y/Z + 7 digits + letter (e.g., X1234567A)
    - IBAN: 2 letters + 2 digits + up to 30 alphanumeric (e.g., ES12 3456 7890 1234 5678 90)
    - Credit card: 4 groups of 4 digits
    - Email addresses
    - Spanish phone numbers (+34 or 0034 prefix)
    - Social Security number (12 digits)

    Usage:
        detector = PIIDetector()
        result = detector.scan("El DNI del cliente es 12345678A y su IBAN ES1234567890123456789012")
        if result.has_pii:
            print(result.summary)
            cleaned = detector.mask(text, result)
    """

    # Patterns ordered by specificity (most specific first to avoid partial matches)
    PATTERNS: dict[str, re.Pattern] = {
        "iban": re.compile(
            r"\b[A-Z]{2}\d{2}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{0,4}\b"
        ),
        "credit_card": re.compile(
            r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b"
        ),
        "social_security": re.compile(
            r"\b\d{2}/?\d{10}\b"
        ),
        "dni": re.compile(
            r"\b\d{8}[A-Z]\b"
        ),
        "nie": re.compile(
            r"\b[XYZ]\d{7}[A-Z]\b"
        ),
        "email": re.compile(
            r"\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}\b"
        ),
        "phone_es": re.compile(
            r"\b(?:\+34|0034)?\s?\d{3}\s?\d{3}\s?\d{3}\b"
        ),
    }

    # DNI letter validation table (Spanish algorithm)
    _DNI_LETTERS = "TRWAGMYFPDXBNJZSQVHLCKE"

    def scan(self, text: str) -> PIIResult:
        """Scan text for PII patterns. Returns all matches found."""
        matches: list[PIIMatch] = []
        types_found: set[str] = set()

        for pii_type, pattern in self.PATTERNS.items():
            for match in pattern.finditer(text):
                value = match.group()

                # Extra validation for DNI: check the letter matches the number
                if pii_type == "dni" and not self._validate_dni(value):
                    continue

                # Extra validation for NIE: check format
                if pii_type == "nie" and not self._validate_nie(value):
                    continue

                masked = self._mask_value(value, pii_type)
                matches.append(PIIMatch(
                    pii_type=pii_type,
                    start=match.start(),
                    end=match.end(),
                    original=value,
                    masked=masked,
                ))
                types_found.add(pii_type)

        return PIIResult(
            has_pii=len(matches) > 0,
            matches=matches,
            types_found=sorted(types_found),
        )

    def mask(self, text: str, result: Optional[PIIResult] = None) -> str:
        """Replace detected PII in text with masked versions.

        Processes matches in reverse order to preserve string positions.
        """
        if result is None:
            result = self.scan(text)

        if not result.has_pii:
            return text

        # Sort by position (reverse) to replace from end to start
        sorted_matches = sorted(result.matches, key=lambda m: m.start, reverse=True)
        masked_text = text
        for match in sorted_matches:
            masked_text = masked_text[:match.start] + match.masked + masked_text[match.end:]

        return masked_text

    def _validate_dni(self, value: str) -> bool:
        """Validate Spanish DNI using the modulo-23 algorithm."""
        try:
            number = int(value[:8])
            letter = value[8]
            expected = self._DNI_LETTERS[number % 23]
            return letter == expected
        except (ValueError, IndexError):
            return False

    def _validate_nie(self, value: str) -> bool:
        """Validate Spanish NIE format."""
        prefix_map = {"X": "0", "Y": "1", "Z": "2"}
        try:
            prefix = prefix_map.get(value[0])
            if prefix is None:
                return False
            number = int(prefix + value[1:8])
            letter = value[8]
            expected = self._DNI_LETTERS[number % 23]
            return letter == expected
        except (ValueError, IndexError):
            return False

    @staticmethod
    def _mask_value(value: str, pii_type: str) -> str:
        """Mask a PII value, keeping enough for identification."""
        if pii_type in ("dni", "nie"):
            return value[:2] + "***" + value[-1]
        elif pii_type == "iban":
            return value[:4] + " **** **** " + value[-4:]
        elif pii_type == "credit_card":
            return "****-****-****-" + value[-4:]
        elif pii_type == "email":
            parts = value.split("@")
            return parts[0][:2] + "***@" + parts[1]
        elif pii_type == "phone_es":
            return value[:3] + " *** ***"
        else:
            return "***"
