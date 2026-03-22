# Source: The DevSecOps and the Machine -- Chapter 14
# Pattern: Model integrity verification and behavioral drift detection

import hashlib
import json
from pathlib import Path
from huggingface_hub import hf_hub_download, model_info

def verify_model_integrity(
    repo_id: str,
    filename: str,
    local_dir: str = "./models"
) -> dict:
    """Downloads a model and verifies its integrity with SHA-256.

    Compares the downloaded file's hash with the hash
    registered in the Hugging Face repository metadata.
    """
    # Get model metadata before downloading
    info = model_info(repo_id)
    expected_hash = None
    for sibling in info.siblings:
        if sibling.rfilename == filename:
            expected_hash = sibling.lfs.sha256 if sibling.lfs else None
            break

    if not expected_hash:
        return {
            "status": "warning",
            "message": f"No hash found for {filename}",
            "recommendation": "Verify manually or reject"
        }

    # Download the file
    local_path = hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        local_dir=local_dir
    )

    # Calculate hash of downloaded file
    sha256 = hashlib.sha256()
    with open(local_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    actual_hash = sha256.hexdigest()

    # Compare hashes
    if actual_hash == expected_hash:
        return {
            "status": "verified",
            "file": filename,
            "sha256": actual_hash,
            "repo": repo_id
        }
    else:
        # Delete compromised file
        Path(local_path).unlink()
        return {
            "status": "rejected",
            "file": filename,
            "expected": expected_hash,
            "actual": actual_hash,
            "action": "File deleted — possible tampering"
        }

import struct
from pathlib import Path
from typing import Literal

# Magic signatures for serialization formats
FORMAT_SIGNATURES = {
    b"\x80\x02": "pickle",        # Pickle protocol v2
    b"\x80\x03": "pickle",        # Pickle protocol v3
    b"\x80\x04": "pickle",        # Pickle protocol v4
    b"\x80\x05": "pickle",        # Pickle protocol v5
    b"PK\x03\x04": "zip",         # ZIP (used by PyTorch .pt)
    b"{\n": "safetensors_json",    # SafeTensors header (JSON)
}

RISK_LEVELS = {
    "pickle": "critical",
    "zip": "high",                  # .pt files are ZIP with pickle inside
    "safetensors_json": "safe",
    "onnx": "low",
    "unknown": "high",
}

def analyze_model_format(filepath: str) -> dict:
    """Inspects a model file's format.

    Detects insecure serialization formats (pickle)
    and recommends safe alternatives (SafeTensors, ONNX).
    """
    path = Path(filepath)
    suffix = path.suffix.lower()

    # Read initial bytes to detect format
    with open(filepath, "rb") as f:
        header = f.read(8)

    detected_format = "unknown"
    for signature, fmt in FORMAT_SIGNATURES.items():
        if header[:len(signature)] == signature:
            detected_format = fmt
            break

    # SafeTensors: additional header verification
    if detected_format == "safetensors_json" or suffix == ".safetensors":
        detected_format = "safetensors"
        risk = "safe"
    elif suffix == ".onnx":
        detected_format = "onnx"
        risk = "low"
    else:
        risk = RISK_LEVELS.get(detected_format, "high")

    result = {
        "file": str(path.name),
        "detected_format": detected_format,
        "risk_level": risk,
        "size_mb": round(path.stat().st_size / (1024 * 1024), 1),
    }

    # Recommendations by risk level
    if risk == "critical":
        result["action"] = "BLOCK — pickle format allows execution"
        result["recommendation"] = "Convert to SafeTensors or ONNX"
    elif risk == "high":
        result["action"] = "REVIEW — potentially insecure format"
        result["recommendation"] = "Inspect ZIP contents"
    elif risk == "low":
        result["action"] = "ACCEPT with integrity verification"
    else:
        result["action"] = "ACCEPT — format safe by design"

    return result

import anthropic
import yaml
from datetime import datetime, timedelta

client = anthropic.Anthropic(api_key="<YOUR_API_KEY>")

def load_ml_bom(path: str = "ml-bom.yaml") -> dict:
    """Loads the ML-BOM inventory from file."""
    with open(path) as f:
        return yaml.safe_load(f)

def audit_model_compliance(bom: dict) -> list[dict]:
    """Audits each model against the policy defined in the BOM."""
    policy = bom.get("policy", {})
    max_age = policy.get("max_age_days", 90)
    allowed = set(policy.get("allowed_formats", []))
    blocked = set(policy.get("blocked_formats", []))
    findings = []

    for model in bom.get("models", []):
        model_id = model["id"]

        # Verify format
        fmt = model.get("format", "unknown")
        if fmt in blocked:
            findings.append({
                "model": model_id,
                "severity": "critical",
                "finding": f"Blocked format: {fmt}",
                "recommendation": "Migrate to SafeTensors or ONNX"
            })
        elif fmt not in allowed and fmt != "api":
            findings.append({
                "model": model_id,
                "severity": "high",
                "finding": f"Unapproved format: {fmt}",
                "recommendation": "Review format and add to list"
            })

        # Verify age
        verified = model.get("verified_date")
        if verified:
            age = (datetime.now() - datetime.fromisoformat(verified)).days
            if age > max_age:
                findings.append({
                    "model": model_id,
                    "severity": "medium",
                    "finding": f"Expired verification ({age} days)",
                    "recommendation": "Reverify integrity and model"
                })

        # Verify model card
        if policy.get("require_model_card") and not model.get("model_card_reviewed"):
            findings.append({
                "model": model_id,
                "severity": "medium",
                "finding": "Model card not reviewed",
                "recommendation": "Review model card before production"
            })

        # Verify hash
        if policy.get("require_hash_verification"):
            if model.get("format") != "api" and not model.get("sha256"):
                findings.append({
                    "model": model_id,
                    "severity": "high",
                    "finding": "No hash verification",
                    "recommendation": "Calculate and register SHA-256"
                })

    return findings

def generate_audit_report(findings: list[dict], bom: dict) -> str:
    """Generates a narrative report with a Claude agent."""
    findings_text = yaml.dump(findings, default_flow_style=False)
    model_count = len(bom.get("models", []))
    critical = sum(1 for f in findings if f["severity"] == "critical")
    high = sum(1 for f in findings if f["severity"] == "high")

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=(
            "You are a security auditor specialized in AI model supply chain. "
            "Generate concise reports in technical English. "
            "Prioritize critical findings and offer actionable recommendations."
        ),
        messages=[{
            "role": "user",
            "content": (
                f"Generate a model supply chain audit report.\n\n"
                f"Total models inventoried: {model_count}\n"
                f"Critical findings: {critical}\n"
                f"High findings: {high}\n\n"
                f"Finding details:\n{findings_text}\n\n"
                f"Include: executive summary, prioritized findings, "
                f"immediate actions, and medium-term recommendations."
            )
        }]
    )
    return response.content[0].text

# Audit pipeline execution
bom = load_ml_bom()
findings = audit_model_compliance(bom)
report = generate_audit_report(findings, bom)
print(report)