# Extraído de: LibroUsuario/cap-25-agentes-en-equipo.md
cd /home/usuario/informe-trimestral

claude -p "
ROLE: Redactor de informes (corrección).
Lee tu borrador original en borradores/informe-q1-v1.md.
Lee el informe de revisión en borradores/revision-v1.md.

Aplica TODAS las correcciones indicadas por el revisor.
Genera la versión corregida en borradores/informe-q1-v2.md.

Para cada corrección aplicada, añade un comentario al final del documento
en una sección '## Registro de cambios' que indique qué se cambió y por qué.
" > logs/redactor-v2.log 2>&1
