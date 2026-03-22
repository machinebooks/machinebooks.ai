# Extraído de: LibroUsuario/cap-25-agentes-en-equipo.md
cd /home/usuario/propuesta-cliente
claude -p "
ROLE: Controller financiero
Tu tarea es preparar la estimación económica.
Lee datos/tarifas-2025.csv y datos/servicios-catalogo.csv.
La necesidad del cliente está en datos/cliente-tech-solutions.md (solo la sección 'Necesidad identificada').
Genera un presupuesto detallado en partes/estimacion-economica.md que incluya:
- Desglose por fases
- Perfiles y dedicación
- Importes por línea
- Total sin IVA, IVA y total con IVA
"
