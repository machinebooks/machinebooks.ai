# Extraído de: LibroPQC/cap-26-criptografo-futuro.md
from app.extensions import db
from datetime import datetime

class CryptoPolicy(db.Model):
    """Política de migración criptográfica configurable por organización.
    Permite actualizar recomendaciones sin re-analizar activos."""

    __tablename__ = "crypto_policies"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id"))
    name = db.Column(db.String(100), nullable=False)
    version = db.Column(db.String(20), nullable=False)  # "2025.1", "2026.1"
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Mapeo: algoritmo vulnerable -> recomendación de migración
    # Almacenado como JSON para flexibilidad
    migration_map = db.Column(db.JSON, nullable=False)
    # Ejemplo de migration_map:
    # {
    #   "RSA-2048": {
    #     "target": "ML-DSA-65",
    #     "hybrid_target": "RSA-2048 + ML-DSA-65",
    #     "phase": "hybrid",           # "hybrid" | "pure_pqc"
    #     "deadline": "2030-12-31",
    #     "regulatory_refs": ["CNSA-2.0", "NIST-IR-8547"]
    #   },
    #   "ECDSA-P256": {
    #     "target": "ML-DSA-44",
    #     "hybrid_target": "ECDSA-P256 + ML-DSA-44",
    #     "phase": "hybrid",
    #     "deadline": "2030-12-31",
    #     "regulatory_refs": ["CNSA-2.0", "EU-PQC-Roadmap"]
    #   },
    #   "ECDH-P256": {
    #     "target": "ML-KEM-768",
    #     "hybrid_target": "X25519 + ML-KEM-768",
    #     "phase": "hybrid",
    #     "deadline": "2031-12-31",
    #     "regulatory_refs": ["CNSA-2.0"]
    #   }
    # }

    rules = db.relationship("CryptoPolicyRule", backref="policy")


class CryptoPolicyRule(db.Model):
    """Regla individual dentro de una política criptográfica."""

    __tablename__ = "crypto_policy_rules"

    id = db.Column(db.Integer, primary_key=True)
    policy_id = db.Column(db.Integer, db.ForeignKey("crypto_policies.id"))
    source_algorithm = db.Column(db.String(50), nullable=False)
    target_algorithm = db.Column(db.String(50), nullable=False)
    hybrid_target = db.Column(db.String(100))
    phase = db.Column(db.String(20), default="hybrid")  # hybrid | pure_pqc
    deadline = db.Column(db.Date)
    priority_weight = db.Column(db.Float, default=1.0)
    regulatory_references = db.Column(db.JSON)

    # Cuando se actualiza la política, todos los findings que referencian
    # esta regla recalculan automáticamente su recomendación
    def get_current_recommendation(self) -> dict:
        """Devuelve la recomendación vigente según la fase actual."""
        if self.phase == "hybrid" and self.hybrid_target:
            return {
                "algorithm": self.hybrid_target,
                "type": "hybrid",
                "note": "Transición: combina clásico + PQC"
            }
        return {
            "algorithm": self.target_algorithm,
            "type": "pure_pqc",
            "note": "Objetivo final: PQC puro"
        }
