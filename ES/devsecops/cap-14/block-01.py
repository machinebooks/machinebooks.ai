# Extraído de: LibroDevSecOps/cap-14-supply-chain-modelos.md
import struct
from pathlib import Path
from typing import Literal

# Firmas mágicas de formatos de serialización
FORMAT_SIGNATURES = {
    b"\x80\x02": "pickle",        # Protocolo pickle v2
    b"\x80\x03": "pickle",        # Protocolo pickle v3
    b"\x80\x04": "pickle",        # Protocolo pickle v4
    b"\x80\x05": "pickle",        # Protocolo pickle v5
    b"PK\x03\x04": "zip",         # ZIP (usado por PyTorch .pt)
    b"{\n": "safetensors_json",    # SafeTensors header (JSON)
}

RISK_LEVELS = {
    "pickle": "critical",
    "zip": "high",                  # .pt files son ZIP con pickle dentro
    "safetensors_json": "safe",
    "onnx": "low",
    "unknown": "high",
}

def analyze_model_format(filepath: str) -> dict:
    """Inspecciona el formato de un fichero de modelo.

    Detecta formatos de serialización inseguros (pickle)
    y recomienda alternativas seguras (SafeTensors, ONNX).
    """
    path = Path(filepath)
    suffix = path.suffix.lower()

    # Leer bytes iniciales para detectar formato
    with open(filepath, "rb") as f:
        header = f.read(8)

    detected_format = "unknown"
    for signature, fmt in FORMAT_SIGNATURES.items():
        if header[:len(signature)] == signature:
            detected_format = fmt
            break

    # SafeTensors: verificación adicional del header
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

    # Recomendaciones por nivel de riesgo
    if risk == "critical":
        result["action"] = "BLOQUEAR — formato pickle permite ejecución"
        result["recommendation"] = "Convertir a SafeTensors o ONNX"
    elif risk == "high":
        result["action"] = "REVISAR — formato potencialmente inseguro"
        result["recommendation"] = "Inspeccionar contenido del ZIP"
    elif risk == "low":
        result["action"] = "ACEPTAR con verificación de integridad"
    else:
        result["action"] = "ACEPTAR — formato seguro por diseño"

    return result
