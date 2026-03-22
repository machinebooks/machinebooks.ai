# Extraído de: LibroUsuario/cap-19-tu-terminal-potenciada.md
# Buscar errores HTTP 5xx en logs de nginx (últimos 7 días)
# Incluye ficheros comprimidos (.gz) y texto plano

# Paso 1: Obtener errores de ficheros recientes
find /var/log/nginx/ -name "*.log" -o -name "*.log.*.gz" \
  -mtime -7 | while read f; do
  if [[ "$f" == *.gz ]]; then
    zcat "$f"
  else
    cat "$f"
  fi
done | grep -E '" (500|502|503|504) ' > /tmp/nginx_errors_week.txt

# Paso 2: Contar por código de error
echo "=== Errores por código ==="
awk '{for(i=1;i<=NF;i++) if($i ~ /^5[0-9][0-9]$/) print $i}' \
  /tmp/nginx_errors_week.txt | sort | uniq -c | sort -rn

# Paso 3: Top 10 endpoints con más errores
echo "=== Top 10 endpoints ==="
awk '{print $7}' /tmp/nginx_errors_week.txt | sort | uniq -c | sort -rn | head -10

# Paso 4: Distribución por día
echo "=== Errores por día ==="
awk '{print $4}' /tmp/nginx_errors_week.txt | cut -d: -f1 | \
  tr -d '[' | sort | uniq -c | sort -t/ -k3 -n
