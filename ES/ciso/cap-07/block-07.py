# Extraído de: LibroCISO/cap-07-gestion-riesgos.md
# Configuración de escalas — cada metodología define sus propios valores
# Almacenado en base de datos, no hardcodeado en el código

METHODOLOGY_CONFIGS = {
    "magerit_v3": {
        "name": "MAGERIT v3",
        "source": "CCN — Consejo Superior de Administración Electrónica",
        "impact_dimensions": ["disponibilidad", "integridad",
                              "confidencialidad", "autenticidad",
                              "trazabilidad"],
        "probability_scale": {
            1: {"label": "Muy baja", "description": "Casi imposible, < 1 vez/10 años"},
            2: {"label": "Baja", "description": "Improbable, ~ 1 vez/5 años"},
            3: {"label": "Media", "description": "Posible, ~ 1 vez/año"},
            4: {"label": "Alta", "description": "Probable, ~ 1 vez/trimestre"},
            5: {"label": "Muy alta", "description": "Casi seguro, ~ 1 vez/mes"},
        },
        "impact_scale": {
            0: {"label": "Despreciable", "description": "Sin impacto apreciable"},
            1: {"label": "Bajo", "description": "Daño menor, recuperable"},
            2: {"label": "Medio", "description": "Daño significativo"},
            3: {"label": "Alto", "description": "Daño grave"},
            4: {"label": "Muy alto", "description": "Daño muy grave o irreversible"},
        },
        "asset_types": [
            "service", "data", "software", "hardware",
            "network", "auxiliary", "facility", "personnel"
        ],
        "risk_calculation": "qualitative",
    },
    "fair": {
        "name": "FAIR — Factor Analysis of Information Risk",
        "source": "The Open Group",
        "impact_dimensions": ["primary_loss", "secondary_loss"],
        "probability_scale": None,  # FAIR usa frecuencia, no escala ordinal
        "impact_scale": None,        # FAIR usa magnitud en EUR
        "lef_ranges": {
            "rare": {"min": 0.01, "max": 0.1, "label": "< 1 vez/10 años"},
            "unlikely": {"min": 0.1, "max": 0.5, "label": "~ 1 vez/2-10 años"},
            "possible": {"min": 0.5, "max": 2.0, "label": "~ 1-2 veces/año"},
            "likely": {"min": 2.0, "max": 10.0, "label": "~ 2-10 veces/año"},
            "frequent": {"min": 10.0, "max": 100.0, "label": "> 10 veces/año"},
        },
        "risk_calculation": "quantitative",
    },
    # Las demás metodologías (ISO 27005, NIST SP 800-30, OCTAVE, EBIOS, etc.)
    # siguen el mismo patrón de configuración: nombre, fuente, dimensiones de
    # impacto, escalas de probabilidad e impacto, tipos de activo y tipo de
    # cálculo (qualitative o quantitative). Se omiten por brevedad.
}
