# Extraído de: LibroPQC/cap-01-el-reloj-corre.md
"""
Pseudocódigo: escáner básico de criptografía quantum-vulnerable.
Detecta usos de algoritmos vulnerables al algoritmo de Shor
mediante análisis de patrones en código fuente.
"""

# 1. Definir patrones de algoritmos vulnerables con nivel de riesgo
PATRONES = {
    "RSA":     (r"\b(RSA|rsa_key|PKCS1|PKCS8)\b",          "critical"),
    "ECDSA":   (r"\b(ECDSA|ec_key|secp256r1|P-256)\b",     "critical"),
    "ECDH":    (r"\b(ECDH|X25519|Curve25519)\b",            "critical"),
    "DH":      (r"\b(DiffieHellman|dh_parameters)\b",       "critical"),
    "DES":     (r"\b(DES|3DES|TripleDES)\b",                "critical"),
    "MD5":     (r"\b(MD5|hashlib\.md5)\b",                  "critical"),
    "SHA-1":   (r"\b(SHA1|hashlib\.sha1)\b",                "high"),
    "AES-128": (r"\b(AES128|key_size=128)\b",               "medium"),
}

# 2. Recorrer ficheros de código fuente (.py, .js, .ts, .java, .go...)
#    excluyendo directorios irrelevantes (.git, node_modules, __pycache__)

# 3. Para cada línea de cada fichero, buscar coincidencias con los patrones
#    y registrar: fichero, línea, algoritmo detectado y nivel de riesgo

# 4. Consolidar resultados: total de ficheros analizados,
#    ficheros con hallazgos, conteo por nivel de riesgo (critical/high/medium)

# 5. Generar informe ordenado por severidad
