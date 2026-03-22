# Extraído de: LibroPQC/cap-25-mercado.md
# Mapeo de marcos regulatorios a controles de compliance verificables
# Cada regulación se descompone en requisitos que la plataforma evalúa automáticamente

REGULATORY_FRAMEWORKS = {
    "DORA": {
        "nombre_completo": "Digital Operational Resilience Act",
        "jurisdiccion": "UE",
        "fecha_vigor": "2025-01-17",
        "sectores": ["banca", "seguros", "mercados", "pagos", "cripto_activos"],
        "controles_pqc": [
            {
                "id": "DORA-ICT-5.1",
                "descripcion": "Identificación de dependencias criptográficas",
                "modulo_plataforma": "crypto_inventory",
                "evidencia": "Inventario completo de algoritmos en uso",
                "fecha_limite": "2026-12-31",
            },
            {
                "id": "DORA-ICT-5.3",
                "descripcion": "Evaluación de riesgo de tecnologías ICT",
                "modulo_plataforma": "risk_assessment",
                "evidencia": "Clasificación de riesgo por hallazgo criptográfico",
                "fecha_limite": "2025-12-31",
            },
            {
                "id": "DORA-RES-11.2",
                "descripcion": "Pruebas de resiliencia operativa digital",
                "modulo_plataforma": "migration_roadmap",
                "evidencia": "Hoja de ruta de migración con escenarios PQC",
                "fecha_limite": "2026-06-30",
            },
        ],
    },
    "NIS2": {
        "nombre_completo": "Directiva de Seguridad de Redes e Información 2",
        "jurisdiccion": "UE",
        "fecha_vigor": "2024-10-18",
        "sectores": [
            "energia", "transporte", "salud", "agua",
            "infraestructura_digital", "telecomunicaciones",
            "administracion_publica", "espacio",
        ],
        "controles_pqc": [
            {
                "id": "NIS2-ART21-2h",
                "descripcion": "Políticas de criptografía y cifrado",
                "modulo_plataforma": "crypto_inventory",
                "evidencia": "Inventario de algoritmos y evaluación PQC",
                "fecha_limite": "2026-12-31",
            },
            {
                "id": "NIS2-ART21-2d",
                "descripcion": "Seguridad de la cadena de suministro",
                "modulo_plataforma": "dependency_scanner",
                "evidencia": "Análisis de dependencias con crypto vulnerable",
                "fecha_limite": "2026-12-31",
            },
        ],
    },
    "CNSA_2_0": {
        "nombre_completo": "Commercial National Security Algorithm Suite 2.0",
        "jurisdiccion": "EE.UU.",
        "fecha_vigor": "2022-09-01",  # Publicación inicial
        "sectores": ["defensa", "seguridad_nacional", "contratistas_federales"],
        "controles_pqc": [
            {
                "id": "CNSA2-ACQ-2027",
                "descripcion": "Nuevas adquisiciones con algoritmos CNSA 2.0",
                "modulo_plataforma": "algorithm_compliance",
                "evidencia": "Verificación de uso exclusivo de ML-KEM/ML-DSA",
                "fecha_limite": "2027-01-01",
            },
            {
                "id": "CNSA2-MIG-2031",
                "descripcion": "Migración completa de sistemas existentes",
                "modulo_plataforma": "migration_roadmap",
                "evidencia": "Hoja de ruta completada con verificación",
                "fecha_limite": "2031-01-01",
            },
            {
                "id": "CNSA2-PURE-2035",
                "descripcion": "PQC puro, sin esquemas híbridos",
                "modulo_plataforma": "hybrid_detector",
                "evidencia": "Cero dependencias de algoritmos clásicos",
                "fecha_limite": "2035-01-01",
            },
        ],
    },
    "EU_PQC_ROADMAP": {
        "nombre_completo": "Hoja de ruta de la Comisión Europea para migración PQC",
        "jurisdiccion": "UE",
        "fecha_vigor": "2024-04-01",  # Recomendación publicada
        "sectores": ["todos_los_regulados"],
        "controles_pqc": [
            {
                "id": "EU-PQC-INV-2026",
                "descripcion": "Inventario criptográfico completo",
                "modulo_plataforma": "crypto_inventory",
                "evidencia": "Informe de inventario con cobertura >95%",
                "fecha_limite": "2026-12-31",
            },
            {
                "id": "EU-PQC-CRIT-2030",
                "descripcion": "Infraestructuras críticas migradas",
                "modulo_plataforma": "migration_tracker",
                "evidencia": "Estado de migración de sistemas críticos",
                "fecha_limite": "2030-12-31",
            },
            {
                "id": "EU-PQC-FULL-2035",
                "descripcion": "Transición completa",
                "modulo_plataforma": "migration_tracker",
                "evidencia": "Cero algoritmos quantum-vulnerables en uso",
                "fecha_limite": "2035-12-31",
            },
        ],
    },
}
