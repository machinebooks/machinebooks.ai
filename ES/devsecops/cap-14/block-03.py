# Extraído de: LibroDevSecOps/cap-14-supply-chain-modelos.md
import anthropic
import yaml
from datetime import datetime, timedelta

client = anthropic.Anthropic()

def load_ml_bom(path: str = "ml-bom.yaml") -> dict:
    """Carga el inventario ML-BOM desde fichero."""
    with open(path) as f:
        return yaml.safe_load(f)

def audit_model_compliance(bom: dict) -> list[dict]:
    """Audita cada modelo contra la política definida en el BOM."""
    policy = bom.get("policy", {})
    max_age = policy.get("max_age_days", 90)
    allowed = set(policy.get("allowed_formats", []))
    blocked = set(policy.get("blocked_formats", []))
    findings = []

    for model in bom.get("models", []):
        model_id = model["id"]

        # Verificar formato
        fmt = model.get("format", "unknown")
        if fmt in blocked:
            findings.append({
                "model": model_id,
                "severity": "critical",
                "finding": f"Formato bloqueado: {fmt}",
                "recommendation": "Migrar a SafeTensors o ONNX"
            })
        elif fmt not in allowed and fmt != "api":
            findings.append({
                "model": model_id,
                "severity": "high",
                "finding": f"Formato no aprobado: {fmt}",
                "recommendation": "Revisar formato y añadir a lista"
            })

        # Verificar antigüedad
        verified = model.get("verified_date")
        if verified:
            age = (datetime.now() - datetime.fromisoformat(verified)).days
            if age > max_age:
                findings.append({
                    "model": model_id,
                    "severity": "medium",
                    "finding": f"Verificación caducada ({age} días)",
                    "recommendation": "Reverificar integridad y modelo"
                })

        # Verificar model card
        if policy.get("require_model_card") and not model.get("model_card_reviewed"):
            findings.append({
                "model": model_id,
                "severity": "medium",
                "finding": "Model card no revisada",
                "recommendation": "Revisar model card antes de producción"
            })

        # Verificar hash
        if policy.get("require_hash_verification"):
            if model.get("format") != "api" and not model.get("sha256"):
                findings.append({
                    "model": model_id,
                    "severity": "high",
                    "finding": "Sin verificación de hash",
                    "recommendation": "Calcular y registrar SHA-256"
                })

    return findings

def generate_audit_report(findings: list[dict], bom: dict) -> str:
    """Genera informe narrativo con agente Claude."""
    findings_text = yaml.dump(findings, default_flow_style=False)
    model_count = len(bom.get("models", []))
    critical = sum(1 for f in findings if f["severity"] == "critical")
    high = sum(1 for f in findings if f["severity"] == "high")

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=(
            "Eres un auditor de seguridad especializado en supply chain "
            "de modelos de IA. Genera informes concisos en español técnico. "
            "Prioriza hallazgos críticos y ofrece recomendaciones accionables."
        ),
        messages=[{
            "role": "user",
            "content": (
                f"Genera un informe de auditoría de supply chain de modelos.\n\n"
                f"Total modelos inventariados: {model_count}\n"
                f"Hallazgos críticos: {critical}\n"
                f"Hallazgos altos: {high}\n\n"
                f"Detalle de hallazgos:\n{findings_text}\n\n"
                f"Incluye: resumen ejecutivo, hallazgos priorizados, "
                f"acciones inmediatas y recomendaciones a medio plazo."
            )
        }]
    )
    return response.content[0].text

# Ejecución del pipeline de auditoría
bom = load_ml_bom()
findings = audit_model_compliance(bom)
report = generate_audit_report(findings, bom)
print(report)
