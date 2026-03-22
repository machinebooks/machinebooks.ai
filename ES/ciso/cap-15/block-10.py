# Extraído de: LibroCISO/cap-15-autenticacion-capas.md
# Prompt de contexto para Claude Code al diseñar el módulo PKI:
#
# "Necesito implementar autenticación mTLS en FastAPI con Nginx como
# terminador TLS. Requisitos: verificación de cadena X.509, OCSP check
# en tiempo real con fallback a CRL, fail-closed si no se puede verificar
# revocación. El certificado del cliente llega como header de Nginx.
# La biblioteca es cryptography (pyca). Muéstrame el flujo completo."
#
# Claude Code generó la estructura base y el flujo OCSP.
# El refinamiento manual fue:
# - Añadir timeout al cliente OCSP (5s) para no bloquear si el responder cae
# - Implementar caché de respuestas OCSP (5 minutos) para reducir latencia
# - Manejar el caso de CAs intermedias en la cadena de verificación
