# Extraído de: LibroUsuario/cap-19-tu-terminal-potenciada.md
# URLs más visitadas hoy con tiempo de respuesta
today=$(date +%d/%b/%Y)

# Paso 1: Filtrar logs de hoy y extraer URL + tiempo de respuesta
grep "$today" /var/log/apache2/access.log | \
  awk '{print $7, $NF}' | \
  sort | \
  # Paso 2: Contar visitas por URL
  uniq -c | sort -rn | head -20 > /tmp/top20_urls.txt

# Paso 3: De las top 20, filtrar las lentas (>2000ms)
while read count url time; do
  if (( time > 2000 )); then
    echo "$url $time $count"
  fi
done < /tmp/top20_urls.txt > /tmp/slow_urls.txt

# Paso 4: Distribución por hora para URLs lentas
echo "=== Distribución horaria de URLs lentas ==="
while read url rest; do
  echo "--- $url ---"
  grep "$url" /var/log/apache2/access.log | \
    grep "$today" | \
    awk '{print $4}' | cut -d: -f2 | sort | uniq -c
done < /tmp/slow_urls.txt
