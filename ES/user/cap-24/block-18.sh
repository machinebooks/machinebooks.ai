# Extraído de: LibroUsuario/cap-24-pipelines-de-datos.md
claude -p "
PIPELINE DE PREPARACIÓN DE PROPUESTA COMERCIAL
Cliente: Tech Solutions
Fecha: $(date +%Y-%m-%d)

=== FASE 1: RECOPILAR INFORMACIÓN ===
1. Lee la ficha del cliente en datos/cliente-tech-solutions.md
2. Lee el catálogo de servicios en datos/servicios-catalogo.csv
3. Lee el historial de proyectos anteriores en datos/proyectos-anteriores.csv
4. Lee las tarifas vigentes en datos/tarifas-2025.csv
5. Identifica los servicios relevantes para la necesidad del cliente

=== FASE 2: PREPARAR LOS NÚMEROS ===
1. Basándote en la necesidad del cliente (sistema de gestión de incidencias
   con integración, diseño, desarrollo, implantación y formación, 4 meses):

   Estima un desglose realista:
   - Fase de consultoría/diseño: duración y equipo necesario
   - Fase de desarrollo: número de sprints y perfiles
   - Fase de implantación: días estimados
   - Fase de formación: sesiones necesarias
   - Soporte post-implantación: meses recomendados

2. Calcula el presupuesto usando las tarifas de tarifas-2025.csv
3. Aplica un 10% de descuento por ser cliente existente
4. Calcula el total sin IVA, el IVA (21%) y el total con IVA

=== FASE 3: COMPONER LA PROPUESTA ===
Genera resultado/propuesta-tech-solutions.md con esta estructura:

# Propuesta de servicios profesionales
## Para: Tech Solutions
## De: [Nuestra empresa]
## Fecha: [hoy]
## Referencia: PROP-2025-[número secuencial]

### 1. Resumen ejecutivo
[1 párrafo: quién somos, qué proponemos, por qué somos la mejor opción]
[Mencionar nuestra experiencia previa con el cliente y su satisfacción]

### 2. Comprensión de la necesidad
[Reformular la necesidad del cliente en nuestras palabras]
[Mostrar que entendemos su contexto y sus plazos]

### 3. Solución propuesta
[Describir la solución en lenguaje no técnico]
[Fases del proyecto con hitos y entregables]
[Equipo asignado (perfiles, no nombres)]

### 4. Plan de trabajo
[Cronograma de 4 meses con fases y solapamientos]
[Tabla: Mes | Fase | Actividades | Entregables]

### 5. Equipo
[Perfiles profesionales que participarán]
[Experiencia relevante del equipo en proyectos similares]

### 6. Presupuesto
[Tabla desglosada por fase y perfil]
[Subtotal, descuento cliente, total sin IVA, IVA, total con IVA]
[Condiciones de pago sugeridas: 30% inicio, 40% hito intermedio, 30% entrega]

### 7. Garantías y soporte
[Período de garantía incluido]
[Opciones de soporte post-implantación]

### 8. Por qué nosotros
[Referencia a proyectos anteriores con este cliente]
[Puntuación de satisfacción]
[Ventajas competitivas]

### 9. Validez y próximos pasos
[La propuesta es válida 30 días]
[Próximo paso sugerido: reunión de presentación]

=== FASE 4: VERIFICAR ===
1. Revisa que todos los números cuadran (subtotales = suma de líneas)
2. Verifica que el cronograma cabe en 4 meses
3. Comprueba que no hay secciones vacías o incompletas
4. Genera un resumen de 5 líneas de la propuesta en resultado/resumen-propuesta.md
"
