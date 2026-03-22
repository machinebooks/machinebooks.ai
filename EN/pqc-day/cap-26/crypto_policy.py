"""
PQC-Day and the Machine — Chapter 26
Pattern: CryptoPolicy data model for crypto-agility

This is a didactic example from the book, not production code.
See chapter 26 for full context and explanation.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Dict, List, Optional


@dataclass
class CryptoPolicyRule:
    """Individual rule within a cryptographic policy."""
    id: int = 0
    source_algorithm: str = ""
    target_algorithm: str = ""
    hybrid_target: str = ""
    phase: str = "hybrid"           # hybrid | pure_pqc
    deadline: Optional[date] = None
    priority_weight: float = 1.0
    regulatory_references: List[str] = field(default_factory=list)

    def get_current_recommendation(self) -> dict:
        """Return the current recommendation based on the active phase."""
        if self.phase == "hybrid" and self.hybrid_target:
            return {
                "algorithm": self.hybrid_target,
                "type": "hybrid",
                "note": "Transition: combines classical + PQC"
            }
        return {
            "algorithm": self.target_algorithm,
            "type": "pure_pqc",
            "note": "Final target: pure PQC"
        }


@dataclass
class CryptoPolicy:
    """Configurable cryptographic migration policy per organization.

    Allows updating recommendations without re-analyzing assets.
    The key pattern is indirection: findings reference a policy,
    not a target algorithm. When NIST updates FIPS 203, the admin
    updates the policy and all recommendations recalculate.
    """
    id: int = 0
    organization_id: int = 0
    name: str = ""
    version: str = ""               # "2025.1", "2026.1"
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    rules: List[CryptoPolicyRule] = field(default_factory=list)

    # Migration map as JSON for flexibility
    # Example:
    # {
    #   "RSA-2048": {
    #     "target": "ML-DSA-65",
    #     "hybrid_target": "RSA-2048 + ML-DSA-65",
    #     "phase": "hybrid",
    #     "deadline": "2030-12-31",
    #     "regulatory_refs": ["CNSA-2.0", "NIST-IR-8547"]
    #   }
    # }
    migration_map: Dict = field(default_factory=dict)


def evaluate_against_policy(
    algorithm: str,
    use_case: str,
    context: str,
    policy: CryptoPolicy
) -> dict:
    """Evaluate an algorithm against the organization's active policy.

    Typical CI/CD usage: before merging a PR that introduces
    cryptographic usage, the pipeline queries whether the algorithm
    is acceptable per the organization's PQC policy.
    """
    # Look up in migration map
    algo_upper = algorithm.upper().replace(' ', '-')
    recommendation = None

    for algo_key, mapping in policy.migration_map.items():
        if algo_key.upper() in algo_upper or algo_upper in algo_key.upper():
            recommendation = mapping
            break

    if not recommendation:
        # Check rules
        for rule in policy.rules:
            if rule.source_algorithm.upper() in algo_upper:
                rec = rule.get_current_recommendation()
                return {
                    "algorithm": algorithm,
                    "pqc_compliant": False,
                    "recommendation": rec["algorithm"],
                    "type": rec["type"],
                    "deadline": rule.deadline.isoformat() if rule.deadline else None,
                    "regulatory_refs": rule.regulatory_references,
                    "severity": "high",
                }

        # Algorithm not in policy — assume acceptable
        return {
            "algorithm": algorithm,
            "pqc_compliant": True,
            "recommendation": None,
            "severity": "info",
            "note": "Algorithm not listed in migration policy"
        }

    return {
        "algorithm": algorithm,
        "pqc_compliant": False,
        "recommendation": recommendation.get("target"),
        "hybrid_option": recommendation.get("hybrid_target"),
        "phase": recommendation.get("phase", "hybrid"),
        "deadline": recommendation.get("deadline"),
        "severity": "high" if recommendation.get("phase") == "hybrid" else "critical",
        "regulatory_refs": recommendation.get("regulatory_refs", []),
    }


def create_default_policy(organization_id: int) -> CryptoPolicy:
    """Create a default PQC migration policy based on CNSA 2.0 and NIST."""
    policy = CryptoPolicy(
        id=1,
        organization_id=organization_id,
        name="Default PQC Migration Policy",
        version="2025.1",
        is_active=True,
        migration_map={
            "RSA-2048": {
                "target": "ML-DSA-65",
                "hybrid_target": "RSA-2048 + ML-DSA-65",
                "phase": "hybrid",
                "deadline": "2030-12-31",
                "regulatory_refs": ["CNSA-2.0", "NIST-IR-8547"]
            },
            "RSA-4096": {
                "target": "ML-DSA-87",
                "hybrid_target": "RSA-4096 + ML-DSA-87",
                "phase": "hybrid",
                "deadline": "2030-12-31",
                "regulatory_refs": ["CNSA-2.0"]
            },
            "ECDSA-P256": {
                "target": "ML-DSA-44",
                "hybrid_target": "ECDSA-P256 + ML-DSA-44",
                "phase": "hybrid",
                "deadline": "2030-12-31",
                "regulatory_refs": ["CNSA-2.0", "EU-PQC-Roadmap"]
            },
            "ECDH-P256": {
                "target": "ML-KEM-768",
                "hybrid_target": "X25519 + ML-KEM-768",
                "phase": "hybrid",
                "deadline": "2031-12-31",
                "regulatory_refs": ["CNSA-2.0"]
            },
            "X25519": {
                "target": "ML-KEM-768",
                "hybrid_target": "X25519 + ML-KEM-768",
                "phase": "hybrid",
                "deadline": "2031-12-31",
                "regulatory_refs": ["CNSA-2.0"]
            },
            "DH": {
                "target": "ML-KEM-768",
                "hybrid_target": None,
                "phase": "pure_pqc",
                "deadline": "2028-12-31",
                "regulatory_refs": ["NIST-IR-8547"]
            },
        },
        rules=[
            CryptoPolicyRule(
                source_algorithm="MD5",
                target_algorithm="SHA-384",
                phase="pure_pqc",
                deadline=date(2025, 12, 31),
                regulatory_references=["NIST-SP-800-131A"]
            ),
            CryptoPolicyRule(
                source_algorithm="SHA-1",
                target_algorithm="SHA-384",
                phase="pure_pqc",
                deadline=date(2025, 12, 31),
                regulatory_references=["NIST-SP-800-131A"]
            ),
            CryptoPolicyRule(
                source_algorithm="DES",
                target_algorithm="AES-256-GCM",
                phase="pure_pqc",
                deadline=date(2025, 6, 30),
                regulatory_references=["NIST-SP-800-131A"]
            ),
            CryptoPolicyRule(
                source_algorithm="AES-128",
                target_algorithm="AES-256",
                phase="pure_pqc",
                deadline=date(2027, 12, 31),
                priority_weight=0.5,
                regulatory_references=["CNSA-2.0"]
            ),
        ]
    )
    return policy


# --- Main ---
if __name__ == '__main__':
    policy = create_default_policy(organization_id=1)

    print(f"Policy: {policy.name} v{policy.version}")
    print(f"Migration map entries: {len(policy.migration_map)}")
    print(f"Additional rules: {len(policy.rules)}\n")

    # Evaluate sample algorithms
    test_algorithms = [
        ("RSA-2048", "jwt_signing", "production"),
        ("ECDSA-P256", "document_signing", "production"),
        ("AES-256-GCM", "data_encryption", "production"),
        ("MD5", "file_integrity", "internal"),
        ("X25519", "tls_key_exchange", "production"),
        ("AES-128", "cache_encryption", "internal"),
    ]

    print("=== Algorithm Evaluation Against Policy ===\n")
    for algo, use_case, ctx in test_algorithms:
        result = evaluate_against_policy(algo, use_case, ctx, policy)
        compliant = "OK" if result['pqc_compliant'] else "MIGRATE"
        print(f"  [{compliant:7s}] {algo:15s} ({use_case})")
        if not result['pqc_compliant']:
            rec = result.get('recommendation') or result.get('hybrid_option', 'N/A')
            print(f"           -> {rec}")
            if result.get('deadline'):
                print(f"           Deadline: {result['deadline']}")
            if result.get('regulatory_refs'):
                print(f"           Refs: {', '.join(result['regulatory_refs'])}")
        print()
