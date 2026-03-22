# Extraído de: LibroBugBounty/cap-01-primera-vuln-agente.md
# Fragmento del análisis de PE ejecutado en el contenedor Docker
# Claude identifica importaciones peligrosas en el driver

DANGEROUS_IMPORTS = {
    "MmMapIoSpace":
        "Mapea memoria física a virtual — lectura/escritura arbitraria",
    "ZwMapViewOfSection":
        "Mapea sección en proceso — mapeo arbitrario potencial",
    "MmCopyMemory":
        "Copia desde memoria física/virtual — primitiva de lectura",
    "IoCreateDevice":
        "Crea objeto de dispositivo — verificar DACL",
}

# Resultado del análisis: AsIO3.sys
# - MmMapIoSpace: PRESENTE (sin SeSinglePrivilegeCheck)
# - ZwMapViewOfSection: PRESENTE
# - IoCreateDevice: PRESENTE (con DACL permisiva)
# - Risk Score: 14/15 - CRITICAL
# - Razón: "Operaciones de memoria SIN verificación de privilegios"
