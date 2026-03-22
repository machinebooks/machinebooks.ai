# Extraído de: LibroPQC/cap-25-mercado.md
# Evaluación de preparación PQC de HSMs en la infraestructura del cliente

HSM_PQC_SUPPORT = {
    # Fabricante -> modelo -> soporte PQC
    "futurex": {
        "vectera_plus": {
            "pqc_algorithms": ["ML-KEM-768", "ML-KEM-1024", "ML-DSA-65"],
            "certification": "PCI HSM v4",
            "pqc_ready": True,
            "notes": "Primer HSM certificado PCI con PQC (junio 2025)",
        },
        "hardened_enterprise": {
            "pqc_algorithms": ["ML-KEM-768"],
            "certification": "FIPS 140-2 Level 3",
            "pqc_ready": False,  # FIPS 140-3 con PQC pendiente
            "notes": "Soporte PQC experimental, sin certificación PQC",
        },
    },
    "thales": {
        "luna_network_7": {
            "pqc_algorithms": ["ML-KEM-768", "ML-DSA-65"],
            "certification": "FIPS 140-3 Level 3",
            "pqc_ready": False,  # Soporte PQC en firmware beta
            "notes": "Firmware PQC previsto para 2026-Q3",
        },
    },
    "utimaco": {
        "securityserver_se": {
            "pqc_algorithms": ["ML-KEM-512", "ML-KEM-768"],
            "certification": "FIPS 140-2 Level 4",
            "pqc_ready": False,
            "notes": "SDK PQC disponible, certificación pendiente",
        },
    },
}


def evaluate_hsm_readiness(org_hsm_inventory: list) -> dict:
    """Evalúa la preparación PQC del parque de HSMs del cliente."""
    results = {
        "total_hsms": len(org_hsm_inventory),
        "pqc_ready": 0,
        "upgrade_needed": 0,
        "replacement_needed": 0,
        "recommendations": [],
    }

    for hsm in org_hsm_inventory:
        vendor = hsm.get("vendor", "").lower()
        model = hsm.get("model", "").lower()

        vendor_data = HSM_PQC_SUPPORT.get(vendor, {})
        model_data = vendor_data.get(model)

        if model_data and model_data["pqc_ready"]:
            results["pqc_ready"] += 1
        elif model_data and model_data["pqc_algorithms"]:
            results["upgrade_needed"] += 1
            results["recommendations"].append({
                "hsm": f"{vendor}/{model}",
                "action": "upgrade_firmware",
                "detail": model_data["notes"],
                "urgencia": "alta",
            })
        else:
            results["replacement_needed"] += 1
            results["recommendations"].append({
                "hsm": f"{vendor}/{model}",
                "action": "replace",
                "detail": "Sin roadmap PQC del fabricante",
                "urgencia": "critica",
            })

    return results
