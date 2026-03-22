"""
PQC-Day and the Machine — Chapter 18
Pattern: Priority scoring based on Europol framework
         (shelf life, exposure, severity, migration complexity)

This is a didactic example from the book, not production code.
See chapter 18 for full context and explanation.
"""

from dataclasses import dataclass
from enum import IntEnum
from typing import List


class ShelfLife(IntEnum):
    """How long data must remain protected."""
    DAYS = 1        # Session tokens, ephemeral data
    MONTHS = 2      # Operational communications
    YEARS = 3       # Contracts, intellectual property
    DECADES = 4     # Health, financial data
    PERMANENT = 5   # State secrets, defense


class Exposure(IntEnum):
    """Degree of system exposure to interception."""
    INTERNAL_ONLY = 1     # Isolated network, no external access
    VPN_PROTECTED = 2     # External access via corporate VPN
    AUTHENTICATED = 3     # Public API with authentication
    PUBLIC_FACING = 4     # Public service with sensitive data
    BROADCAST = 5         # Data transmitted without channel control


class Severity(IntEnum):
    """Impact of algorithm compromise."""
    INFORMATIONAL = 1  # Metadata, non-sensitive data
    LOW = 2            # Low-sensitivity internal data
    MEDIUM = 3         # Operational data, basic PII
    HIGH = 4           # Financial data, sensitive PII
    CRITICAL = 5       # Critical infrastructure, health, defense


class MigrationComplexity(IntEnum):
    """Effort required to migrate."""
    TRIVIAL = 1       # Change configuration, no code
    LOW = 2           # Change library, unit tests
    MEDIUM = 3        # Refactor service, coordinate team
    HIGH = 4          # Change protocol, negotiate with third parties
    EXTREME = 5       # Architectural redesign, multiple systems


@dataclass
class PriorityScore:
    """Result of priority calculation."""
    shelf_life: int
    exposure: int
    severity: int
    migration_complexity: int
    composite_score: float
    priority_label: str
    recommended_timeline: str

    @property
    def risk_score(self) -> float:
        """Risk score without considering migration complexity."""
        return self.shelf_life * self.exposure * self.severity

    @property
    def urgency_ratio(self) -> float:
        """Risk / complexity ratio — higher means more urgent."""
        if self.migration_complexity == 0:
            return float('inf')
        return self.risk_score / self.migration_complexity


def calculate_priority(
    shelf_life: int,
    exposure: int,
    severity: int,
    migration_complexity: int
) -> PriorityScore:
    """Calculate migration priority using the Europol framework.

    The composite score weights risk (shelf_life x exposure x severity)
    against effort (migration_complexity). Findings with high risk
    and low complexity are migrated first — they are "quick wins".
    """
    # Raw risk score (1 to 125)
    risk = shelf_life * exposure * severity

    # Composite score: risk weighted by inverse complexity
    # High complexity reduces urgency, not risk
    composite = risk * (6 - migration_complexity) / 5

    # Classification by thresholds
    if composite >= 50:
        label = "critical"
        timeline = "Immediate — next 2 weeks"
    elif composite >= 25:
        label = "high"
        timeline = "Short term — next quarter"
    elif composite >= 10:
        label = "medium"
        timeline = "Medium term — next 6 months"
    else:
        label = "low"
        timeline = "Long term — next year"

    return PriorityScore(
        shelf_life=shelf_life,
        exposure=exposure,
        severity=severity,
        migration_complexity=migration_complexity,
        composite_score=round(composite, 2),
        priority_label=label,
        recommended_timeline=timeline
    )


def prioritize_findings(findings: List[dict]) -> List[dict]:
    """Sort a list of findings by migration priority.

    Each finding should include: shelf_life, exposure,
    severity_score, migration_complexity. Missing values
    default to conservative assumptions (worst case).
    """
    scored = []
    for finding in findings:
        score = calculate_priority(
            shelf_life=finding.get('shelf_life', 3),
            exposure=finding.get('exposure', 3),
            severity=finding.get('severity_score', 3),
            migration_complexity=finding.get('migration_complexity', 3)
        )
        finding['priority_score'] = score.composite_score
        finding['priority_label'] = score.priority_label
        finding['recommended_timeline'] = score.recommended_timeline
        finding['urgency_ratio'] = score.urgency_ratio
        scored.append(finding)

    # Sort by composite score descending
    scored.sort(key=lambda f: f['priority_score'], reverse=True)
    return scored


# --- Main ---
if __name__ == '__main__':
    # Example findings with different risk profiles
    findings = [
        {
            'name': 'RSA-2048 in JWT signing (auth service)',
            'algorithm': 'RSA-2048',
            'shelf_life': ShelfLife.YEARS,          # Tokens protect long-lived sessions
            'exposure': Exposure.PUBLIC_FACING,       # Public API
            'severity_score': Severity.HIGH,          # Financial data
            'migration_complexity': MigrationComplexity.MEDIUM,
        },
        {
            'name': 'MD5 for log file integrity',
            'algorithm': 'MD5',
            'shelf_life': ShelfLife.DAYS,            # Ephemeral logs
            'exposure': Exposure.INTERNAL_ONLY,       # Internal only
            'severity_score': Severity.LOW,           # Non-sensitive
            'migration_complexity': MigrationComplexity.TRIVIAL,
        },
        {
            'name': 'ECDSA P-256 for contract signing',
            'algorithm': 'ECDSA-P256',
            'shelf_life': ShelfLife.DECADES,          # Contracts valid 20+ years
            'exposure': Exposure.AUTHENTICATED,       # Authenticated API
            'severity_score': Severity.CRITICAL,      # Legal documents
            'migration_complexity': MigrationComplexity.HIGH,
        },
        {
            'name': 'AES-128 for data at rest',
            'algorithm': 'AES-128',
            'shelf_life': ShelfLife.YEARS,
            'exposure': Exposure.VPN_PROTECTED,
            'severity_score': Severity.MEDIUM,
            'migration_complexity': MigrationComplexity.LOW,
        },
        {
            'name': 'ECDH X25519 in TLS (CDN)',
            'algorithm': 'X25519',
            'shelf_life': ShelfLife.DAYS,             # TLS session keys
            'exposure': Exposure.BROADCAST,           # Public internet
            'severity_score': Severity.HIGH,
            'migration_complexity': MigrationComplexity.TRIVIAL,
        },
    ]

    prioritized = prioritize_findings(findings)

    print("=== PQC Migration Priority (Europol Framework) ===\n")
    print(f"{'Priority':10s} {'Score':>6s} {'Urgency':>8s} {'Finding'}")
    print(f"{'-'*10} {'-'*6} {'-'*8} {'-'*50}")

    for f in prioritized:
        print(f"{f['priority_label']:10s} {f['priority_score']:6.1f} "
              f"{f['urgency_ratio']:8.1f} {f['name']}")
        print(f"{'':10s} {'':6s} {'':8s} -> {f['recommended_timeline']}")
        print()
