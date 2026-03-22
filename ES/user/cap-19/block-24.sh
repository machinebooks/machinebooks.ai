# Extraído de: LibroUsuario/cap-19-tu-terminal-potenciada.md
# 1. Total de ventas por región
echo "=== Total por región ==="
awk -F, 'NR>1 {sum[$3]+=$5} END {for(r in sum) printf "%s: %.2f€\n", r, sum[r]}' \
  /tmp/ventas.csv | sort -t: -k2 -rn

# 2. Producto más vendido por región
echo "=== Producto top por región ==="
awk -F, 'NR>1 {sales[$3","$2]+=$4}
  END {
    for(key in sales) {
      split(key,parts,",")
      region=parts[1]; product=parts[2]
      if(sales[key] > max[region]) {
        max[region]=sales[key]; best[region]=product
      }
    }
    for(r in best) print r": "best[r]" ("max[r]" unidades)"
  }' /tmp/ventas.csv

# 3. Promedio de importe por mes
echo "=== Promedio por mes ==="
awk -F, 'NR>1 {
  split($1,d,"-"); month=d[1]"-"d[2]
  sum[month]+=$5; count[month]++
} END {
  for(m in sum) printf "%s: %.2f€ (media de %d ventas)\n", m, sum[m]/count[m], count[m]
}' /tmp/ventas.csv | sort

# 4. Top 5 fechas con más ventas
echo "=== Top 5 fechas ==="
awk -F, 'NR>1 {count[$1]++} END {for(d in count) print count[d], d}' \
  /tmp/ventas.csv | sort -rn | head -5
