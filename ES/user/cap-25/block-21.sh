# Extraído de: LibroUsuario/cap-25-agentes-en-equipo.md
cd /home/usuario/informe-trimestral

claude -p "
ROLE: Revisor de calidad.
Lee borradores/informe-q1-v1.md (el borrador del informe).
Lee también datos/resultados-q1.csv y datos/objetivos-q1.csv
para verificar que las cifras del informe coinciden con los datos originales.

Genera un informe de revisión en borradores/revision-v1.md con:

1. CIFRAS: ¿Todos los números del informe coinciden con los CSV?
   Si hay discrepancias, indica cuál es el valor en el informe y cuál
   debería ser según los datos.

2. COHERENCIA: ¿Las conclusiones se sostienen con los datos presentados?
   ¿Hay afirmaciones sin respaldo numérico?

3. CLARIDAD: ¿El texto es claro para un directivo que no conoce los detalles?
   ¿Hay párrafos confusos o ambiguos?

4. COMPLETITUD: ¿Falta alguna sección o dato relevante?

5. FORMATO: ¿Las tablas están bien formateadas? ¿Los importes siguen
   el formato del glosario?

6. VEREDICTO: Aprobado / Aprobado con cambios menores / Requiere revisión mayor

Para cada observación, indica la sección afectada y sugiere la corrección concreta.
" > logs/revisor-v1.log 2>&1
