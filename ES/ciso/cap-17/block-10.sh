# Extraído de: LibroCISO/cap-17-hardening-siem.md
# Ejemplo didáctico: scripts/verify_hardening.sh

#!/bin/bash
# Verificación básica de hardening post-despliegue

BASE_URL="https://grc.ejemplo.com"
ERRORS=0

echo "=== Verificación de headers de seguridad ==="

# Comprobar CSP
CSP=$(curl -sI "$BASE_URL" | grep -i "content-security-policy")
if echo "$CSP" | grep -q "nonce-"; then
    echo "[OK] CSP con nonce detectado"
else
    echo "[FAIL] CSP sin nonce o ausente"
    ERRORS=$((ERRORS + 1))
fi

# Comprobar HSTS
HSTS=$(curl -sI "$BASE_URL" | grep -i "strict-transport-security")
if echo "$HSTS" | grep -q "max-age=31536000"; then
    echo "[OK] HSTS con max-age de 1 año"
else
    echo "[FAIL] HSTS ausente o con max-age insuficiente"
    ERRORS=$((ERRORS + 1))
fi

# Comprobar X-Frame-Options
XFO=$(curl -sI "$BASE_URL" | grep -i "x-frame-options")
if echo "$XFO" | grep -qi "deny"; then
    echo "[OK] X-Frame-Options: DENY"
else
    echo "[FAIL] X-Frame-Options ausente o permisivo"
    ERRORS=$((ERRORS + 1))
fi

# Comprobar rate limiting en auth
echo ""
echo "=== Verificación de rate limiting ==="
for i in $(seq 1 15); do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
        -X POST "$BASE_URL/api/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"email":"test@test.com","password":"wrong"}')
    if [ "$STATUS" = "429" ]; then
        echo "[OK] Rate limit activado en petición $i (HTTP 429)"
        break
    fi
done

echo ""
echo "=== Resultado: $ERRORS errores ==="
exit $ERRORS
