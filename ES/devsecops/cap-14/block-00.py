# Extraído de: LibroDevSecOps/cap-14-supply-chain-modelos.md
import hashlib
import json
from pathlib import Path
from huggingface_hub import hf_hub_download, model_info

def verify_model_integrity(
    repo_id: str,
    filename: str,
    local_dir: str = "./models"
) -> dict:
    """Descarga un modelo y verifica su integridad con SHA-256.

    Compara el hash del fichero descargado con el hash
    registrado en los metadatos del repositorio de Hugging Face.
    """
    # Obtener metadatos del modelo antes de descargar
    info = model_info(repo_id)
    expected_hash = None
    for sibling in info.siblings:
        if sibling.rfilename == filename:
            expected_hash = sibling.lfs.sha256 if sibling.lfs else None
            break

    if not expected_hash:
        return {
            "status": "warning",
            "message": f"No se encontró hash para {filename}",
            "recommendation": "Verificar manualmente o rechazar"
        }

    # Descargar el fichero
    local_path = hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        local_dir=local_dir
    )

    # Calcular hash del fichero descargado
    sha256 = hashlib.sha256()
    with open(local_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    actual_hash = sha256.hexdigest()

    # Comparar hashes
    if actual_hash == expected_hash:
        return {
            "status": "verified",
            "file": filename,
            "sha256": actual_hash,
            "repo": repo_id
        }
    else:
        # Eliminar fichero comprometido
        Path(local_path).unlink()
        return {
            "status": "rejected",
            "file": filename,
            "expected": expected_hash,
            "actual": actual_hash,
            "action": "Fichero eliminado — posible manipulación"
        }
