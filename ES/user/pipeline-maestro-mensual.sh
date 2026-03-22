# Extraído de: LibroUsuario/cap-24-pipelines-de-datos.md
#!/bin/bash
# pipeline-maestro-mensual.sh
# Ejecuta los tres pipelines en secuencia

MES="enero"
ANIO="2025"
LOG="/home/usuario/logs/pipeline-maestro-$MES.log"

echo "=== Pipeline maestro: $MES $ANIO ===" > "$LOG"

# Pipeline 1: Consolidar datos
echo "[$(date)] Pipeline 1: Consolidación..." >> "$LOG"
cd /home/usuario/consolidacion
claude -p "Consolida los datos de $MES $ANIO según las instrucciones del CLAUDE.md" >> "$LOG" 2>&1

# Verificar que el pipeline 1 generó su salida
if [ ! -f "datos-consolidados-$MES.csv" ]; then
    echo "[ERROR] Pipeline 1 no generó datos consolidados. Abortando." >> "$LOG"
    exit 1
fi

# Pipeline 2: Análisis
echo "[$(date)] Pipeline 2: Análisis financiero..." >> "$LOG"
cp "datos-consolidados-$MES.csv" /home/usuario/reporting-mensual/datos/
cd /home/usuario/reporting-mensual
claude -p "Ejecuta el pipeline de análisis financiero para $MES $ANIO" >> "$LOG" 2>&1

# Verificar que el pipeline 2 generó el informe
if [ ! -f "informes/informe-financiero-$MES-$ANIO.md" ]; then
    echo "[ERROR] Pipeline 2 no generó el informe. Abortando." >> "$LOG"
    exit 1
fi

# Pipeline 3: Distribución
echo "[$(date)] Pipeline 3: Distribución..." >> "$LOG"
claude -p "
Envía el informe informes/informe-financiero-$MES-$ANIO.md por email a:
- directora.financiera@empresa.com (destinatario principal)
- gerencia@empresa.com (copia)

Asunto: Informe financiero $MES $ANIO
Cuerpo: Adjunto el informe financiero mensual. Los puntos clave son:
[incluir las 3 conclusiones principales del informe]
" >> "$LOG" 2>&1

echo "[$(date)] Pipeline maestro completado." >> "$LOG"
