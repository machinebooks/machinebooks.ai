# Extraído de: LibroUsuario/cap-25-agentes-en-equipo.md
cd /home/usuario/propuesta-cliente
claude -p "
ROLE: Director de propuesta.
Lee los tres archivos en partes/ y el glosario.md.
Integra todo en resultado/propuesta-final.md:
1. Inserta analisis-cliente.md donde dice [INSERTAR_ANALISIS]
2. Inserta estimacion-economica.md donde dice [INSERTAR_PRESUPUESTO]
3. Verifica coherencia: cifras, fechas, nombres, tono
4. Corrige cualquier inconsistencia
5. El documento final debe leerse como si lo hubiera escrito una sola persona
"
