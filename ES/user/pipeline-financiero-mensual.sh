# Extraído de: LibroUsuario/cap-24-pipelines-de-datos.md
#!/bin/bash
# pipeline-financiero-mensual.sh

MES=$(date -d "yesterday" +%B | tr '[:upper:]' '[:lower:]')
# Nota: el flag -d es específico de GNU/Linux. En macOS, usa: date -v-1d +%B
ANIO=$(date +%Y)

cd /home/usuario/reporting-mensual

claude -p "
Ejecuta el pipeline de reporting financiero para el mes de $MES de $ANIO.
Sigue las instrucciones del CLAUDE.md del proyecto.
Los datos están en datos/facturacion-$MES.csv, datos/gastos-$MES.csv,
datos/cobros-$MES.csv y datos/presupuesto-q*.csv.
Genera el informe en informes/informe-financiero-$MES-$ANIO.md
" >> /home/usuario/logs/pipeline-financiero-$MES.log 2>&1
