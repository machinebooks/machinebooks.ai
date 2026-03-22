# Extraído de: LibroUsuario/cap-25-agentes-en-equipo.md
cd /home/usuario/propuesta-cliente
claude -p "
ROLE: Director de propuesta
En la carpeta partes/ hay tres documentos:
- analisis-cliente.md (análisis del cliente)
- estimacion-economica.md (presupuesto detallado)
- documento-propuesta.md (estructura de la propuesta con marcadores)

Tu tarea:
1. Lee los tres documentos
2. Integra el análisis y el presupuesto en el documento de propuesta,
   reemplazando los marcadores
3. Revisa la coherencia: que los datos del análisis coincidan con lo que
   dice la propuesta, que los números del presupuesto estén reflejados
   correctamente en el texto
4. Ajusta el tono para que todo el documento suene como si lo hubiera
   escrito una sola persona
5. Genera el resultado final en resultado/propuesta-tech-solutions.md
"
