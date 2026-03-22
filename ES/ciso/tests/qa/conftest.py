# Extraído de: LibroCISO/cap-23-testing-grc.md
# tests/qa/conftest.py
"""Registro de actualizaciones regulatorias conocidas."""

REGULATORY_VERSIONS = {
    "rgpd": {"version": "2016/679", "ultima_guia_aepd": "2024-06"},
    "ens": {"version": "RD 311/2022", "ultima_actualizacion": "2022-05"},
    "nis2": {"version": "2022/2555", "transposicion_es": "2024-10"},
    "dora": {"version": "2022/2554", "aplicable_desde": "2025-01"},
    "ai_act": {"version": "2024/1689", "aplicable_desde": "2026-08"},
}


def test_regulatory_freshness():
    """Verificar que los tests QA están actualizados respecto
    a las versiones regulatorias vigentes. Si este test falla,
    significa que hay una actualización regulatoria que los tests
    QA aún no reflejan."""
    import importlib
    for modulo, info in REGULATORY_VERSIONS.items():
        qa_module = importlib.import_module(f"tests.qa.qa_{modulo}")
        version_en_tests = getattr(qa_module, "REGULATORY_VERSION", None)
        assert version_en_tests == info["version"], (
            f"El módulo qa_{modulo}.py verifica la versión "
            f"'{version_en_tests}' pero la versión vigente es "
            f"'{info['version']}'. Revisar y actualizar tests."
        )
