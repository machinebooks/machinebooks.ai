# Extraído de: LibroBugBounty/cap-08-analisis-drivers.md
# Imports peligrosos que indican primitivas de kernel r/w
DANGEROUS_IMPORTS = {
    "MmMapIoSpace":     "Mapea memoria física a virtual — r/w arbitrario",
    "MmMapLockedPages": "Mapea páginas bloqueadas — mapeo arbitrario",
    "ZwMapViewOfSection": "Mapea sección en proceso — mapeo arbitrario",
    "MmCopyMemory":     "Copia de memoria física/virtual — primitiva de lectura",
    "IoAllocateMdl":    "Aloca MDL — usado en cadenas de mapeo",
    "MmBuildMdlForNonPagedPool": "MDL para non-paged pool — primitiva de mapeo",
    "KeStackAttachProcess": "Attach a proceso — acceso cross-process",
}

# Funciones de verificación de privilegios — su AUSENCIA es la señal
PRIVILEGE_CHECKS = {
    "SePrivilegeCheck":        "Verificación de privilegios general",
    "SeSinglePrivilegeCheck":  "Verificación de privilegio específico",
    "SeAccessCheck":           "Verificación de acceso por descriptor de seguridad",
}
