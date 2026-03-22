# Extraído de: LibroCISO/cap-23-testing-grc.md
# conftest.py (raíz)
"""Configuración de pytest con metadatos regulatorios para auditoría."""
import pytest
import json
from datetime import datetime


def pytest_collection_modifyitems(items):
    """Añadir metadatos regulatorios a cada test para el informe."""
    for item in items:
        markers = [m.name for m in item.iter_markers()]
        if "regulatory" in markers:
            # Extraer el artículo/control del docstring
            doc = item.function.__doc__ or ""
            item.user_properties.append(("regulatory_ref", doc.split(":")[0]))
            item.user_properties.append(("timestamp", datetime.utcnow().isoformat()))


def pytest_sessionfinish(session, exitstatus):
    """Generar informe de auditoría al finalizar la sesión."""
    resultados = []
    for item in session.items:
        props = dict(item.user_properties)
        resultados.append({
            "test": item.nodeid,
            "regulatory_ref": props.get("regulatory_ref", "N/A"),
            "resultado": "PASS" if item.session.exitstatus == 0 else "FAIL",
            "timestamp": props.get("timestamp"),
        })

    with open("reports/qa_audit_report.json", "w") as f:
        json.dump({
            "fecha_ejecucion": datetime.utcnow().isoformat(),
            "total_tests": len(resultados),
            "resultados": resultados,
        }, f, indent=2, ensure_ascii=False)
