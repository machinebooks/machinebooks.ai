# Capitulo 27 — Privacidad y datos sensibles

Ejercicios practicos para aprender a usar Claude con datos que contienen informacion personal, financiera o confidencial. El objetivo es que desarrolles un flujo de trabajo seguro: anonimizar primero, procesar despues, y nunca exponer datos sensibles innecesariamente.

---

## Caso practico 1: Analisis salarial sin exponer datos personales

**Contexto:** Recursos Humanos te pide un analisis de la estructura salarial por departamento. Te dan un CSV con nombres, DNIs, salarios y antigueedad de 200 empleados. Necesitas las estadisticas, pero no necesitas (ni debes) que Claude vea los datos personales.

### Paso A — Preparar los datos de prueba

Crea un archivo `salarios-ejemplo.csv` con datos ficticios para practicar:

```csv
nombre,dni,departamento,puesto,salario_bruto,antiguedad_anos,fecha_nacimiento
Maria Garcia Lopez,12345678A,Tecnologia,Desarrolladora Senior,48000,7,1988-03-15
Carlos Ruiz Fernandez,23456789B,Tecnologia,Arquitecto Software,62000,12,1982-07-22
Ana Martinez Diaz,34567890C,Comercial,Directora de Ventas,55000,9,1985-11-03
Pedro Sanchez Gomez,45678901D,Comercial,Ejecutivo de Cuentas,35000,3,1992-06-18
Laura Jimenez Torres,56789012E,RRHH,Responsable de Seleccion,42000,5,1990-01-25
```

Anade al menos 15-20 filas mas para que el analisis sea significativo.

### Paso B — Anonimizar ANTES de analizar

No le pases el CSV completo a Claude. Primero, anonimiza:

```
Necesito que anonimices el archivo salarios-ejemplo.csv para analisis estadistico.

COLUMNAS A ELIMINAR (no las necesito para el analisis):
- nombre
- dni
- fecha_nacimiento

COLUMNAS A MANTENER:
- departamento
- puesto
- salario_bruto
- antiguedad_anos

PROCESO:
1. Lee el archivo original
2. Crea un archivo nuevo llamado salarios-anonimo.csv con SOLO las columnas a mantener
3. Anade una columna "id" con numeros secuenciales (1, 2, 3...) para poder referenciar filas
4. Muestrame las 5 primeras filas del archivo anonimizado para verificar
5. NO muestres ni almacenes las columnas eliminadas en ningun momento

Confirma cuando el archivo anonimizado este listo.
```

### Paso C — Analizar los datos anonimizados

Ahora si, trabaja con el archivo limpio:

```
Analiza el archivo salarios-anonimo.csv y genera:

1. ESTADISTICAS POR DEPARTAMENTO:
   - Salario medio, mediana, minimo y maximo
   - Numero de empleados
   - Antiguedad media

2. DISTRIBUCION SALARIAL:
   - Rangos: <30K, 30-40K, 40-50K, 50-60K, >60K
   - Porcentaje de empleados en cada rango

3. CORRELACION:
   - Relacion entre antiguedad y salario (hay correlacion?)
   - Diferencias salariales entre puestos similares en distintos departamentos

4. ANOMALIAS:
   - Empleados con salario significativamente por encima o por debajo de su grupo
   - Referencia por "id" (no por nombre, que ya no tenemos)

Formato: tablas Markdown. No inventes datos que no esten en el archivo.
```

### Paso D — Verificar que no hay fuga de datos

```
Revisa tu historial de esta sesion y confirma:
1. En algun momento has mostrado nombres o DNIs de empleados?
2. El archivo salarios-anonimo.csv contiene alguna columna con datos personales?
3. Si alguien leyera esta conversacion completa, podria identificar a algun empleado?
```

**Preguntas de reflexion:**
1. Si hubieras pasado el CSV completo, Claude habria incluido nombres en el analisis?
2. El campo "puesto" podria ser identificador en departamentos pequenos (ej: un solo "Director de Ventas")?
3. Como mejorarias la anonimizacion si los departamentos tuvieran menos de 5 personas?
4. Guardarias el archivo anonimizado o lo eliminarias despues del analisis?

> **Leccion clave:** La anonimizacion no es un paso extra, es el primer paso. Si los datos personales nunca llegan a Claude, no pueden filtrarse. Ademas, el analisis estadistico no necesita saber *quien* cobra cada salario.

---

## Caso practico 2: Facturas de proveedores sin exponer datos bancarios

**Contexto:** Contabilidad te pide que proceses 50 facturas de proveedores para generar un informe de gastos. Las facturas incluyen datos bancarios (IBAN, CIF) que no necesitas para el informe.

### Paso A — Definir la lista de inclusion/exclusion

Antes de procesar cualquier factura, establece las reglas:

```
Voy a pasarte facturas de proveedores para generar un informe de gastos.

LISTA DE DATOS A EXTRAER (inclusion):
- Nombre del proveedor
- Numero de factura
- Fecha de emision
- Concepto o descripcion del servicio
- Importe base
- IVA
- Importe total
- Categoria de gasto (material, servicios, licencias, etc.)

LISTA DE DATOS A IGNORAR (exclusion):
- IBAN o numero de cuenta bancaria
- CIF/NIF del proveedor
- Direccion postal completa
- Datos de contacto (telefono, email del proveedor)
- Firma o sello
- Condiciones de pago detalladas

Si en alguna factura encuentras datos de la lista de exclusion mezclados
con datos de inclusion (por ejemplo, el IBAN dentro del concepto),
SUSTITUYE el dato sensible por "[DATO BANCARIO OMITIDO]".

Confirma que has entendido ambas listas antes de que te pase la primera factura.
```

### Paso B — Procesar las facturas

Para cada factura (o lote de facturas):

```
Procesa estas facturas siguiendo las reglas de inclusion/exclusion anteriores.

Para cada factura genera una fila con:
| Proveedor | N Factura | Fecha | Concepto | Base | IVA | Total | Categoria |

Al terminar el lote, anade un resumen:
- Total facturado en este lote
- Desglose por categoria de gasto
- Numero de facturas procesadas vs recibidas

Si alguna factura es ilegible o ambigua, marcala como "[REVISAR MANUALMENTE]"
en lugar de inventar datos.
```

### Paso C — Validacion cruzada

```
Revisa el informe generado y verifica:

1. El total de todas las facturas individuales suma lo mismo que el total del resumen?
2. Hay alguna factura donde hayas incluido datos de la lista de exclusion por error?
3. Cuantas facturas has marcado para revision manual?
4. Hay algun proveedor con facturas que parezcan duplicadas (mismo importe y fecha)?

Si detectas errores, corrigelos y muestrame la version corregida.
```

### Paso D — Generar informe final limpio

```
Genera el informe final en formato Markdown con estas secciones:

1. RESUMEN EJECUTIVO
   - Periodo analizado
   - Numero de facturas
   - Gasto total

2. DESGLOSE POR CATEGORIA
   - Tabla con: Categoria | Num facturas | Total | Porcentaje del gasto

3. TOP 10 PROVEEDORES POR VOLUMEN
   - Tabla con: Proveedor | Num facturas | Total facturado

4. ALERTAS
   - Facturas marcadas para revision manual
   - Posibles duplicados
   - Variaciones significativas respecto a periodos anteriores (si aplica)

El informe NO debe contener ningun IBAN, CIF, direccion postal ni dato bancario.
Guardalo como informe-gastos-[MES].md
```

**Preguntas de reflexion:**
1. Si una factura tiene el IBAN en la linea de concepto, tu filtro lo detectaria?
2. El nombre del proveedor es dato sensible? En que contexto podria serlo?
3. Como adaptarias este flujo si las facturas fueran PDFs escaneados en lugar de texto?
4. Guardarias las facturas originales en la misma carpeta que el informe final?

> **Leccion clave:** La lista explicita de inclusion/exclusion es mas segura que confiar en que Claude "sabe" que datos son sensibles. Define lo que quieres, define lo que no quieres, y verifica el resultado.

---

## Caso practico 3: Analisis de contratos sin enviar el texto completo

**Contexto:** El departamento legal te pide que analices 10 contratos con proveedores para identificar clausulas problematicas (penalizaciones, exclusividad, renovacion automatica). Los contratos son confidenciales y no quieres enviar el texto completo a una IA.

### Paso A — Enfoque clausula por clausula

En lugar de pasar el contrato entero, trabaja por secciones anonimizadas:

```
Voy a analizarte clausulas individuales de contratos con proveedores.
Necesito que identifiques riesgos legales en cada clausula.

REGLAS:
- Te pasare clausulas una a una, ya anonimizadas
- Donde aparezca el nombre de una empresa, lo sustituire por [EMPRESA_A] o [EMPRESA_B]
- Donde aparezcan importes, los mantendre (son necesarios para el analisis)
- Donde aparezcan fechas, las mantendre (son necesarias para plazos)
- NO me pidas el contrato completo ni el contexto de negocio
- Analiza SOLO lo que te paso

Para cada clausula, responde:
1. Tipo de clausula (penalizacion, exclusividad, confidencialidad, etc.)
2. Riesgo para [EMPRESA_A] (alto/medio/bajo)
3. Por que es riesgosa (o por que no)
4. Sugerencia de mejora o negociacion (si aplica)

Confirma que has entendido el formato.
```

### Paso B — Enviar clausulas anonimizadas

Ejemplo de como anonimizar una clausula antes de enviarla:

**Texto original del contrato:**
```
Cláusula 7.3 - Penalización por incumplimiento
En caso de que Servicios Tecnológicos Avanzados S.L. no entregue el proyecto
en el plazo acordado de 90 días desde la firma, abonará a Distribuciones
García e Hijos S.A. una penalización del 2% del importe total del contrato
(185.000 EUR) por cada semana de retraso, hasta un máximo del 15%.
```

**Texto anonimizado para Claude:**
```
Clausula 7.3 - Penalizacion por incumplimiento
En caso de que [PROVEEDOR_B] no entregue el proyecto en el plazo acordado
de 90 dias desde la firma, abonara a [EMPRESA_A] una penalizacion del 2%
del importe total del contrato (185.000 EUR) por cada semana de retraso,
hasta un maximo del 15%.

Analiza esta clausula segun el formato acordado.
```

### Paso C — Compilar el analisis

Despues de analizar todas las clausulas relevantes:

```
Con todas las clausulas analizadas, genera un informe de riesgos:

1. RESUMEN DE RIESGOS
   | Contrato | Clausula | Tipo | Riesgo | Resumen |

2. CLAUSULAS QUE REQUIEREN RENEGOCIACION (riesgo alto)
   - Detalle de cada una y sugerencia concreta

3. CLAUSULAS ACEPTABLES PERO MEJORABLES (riesgo medio)
   - Detalle y sugerencia

4. PATRONES DETECTADOS
   - Clausulas similares entre distintos contratos
   - Proveedores con condiciones mas agresivas que otros

El informe debe usar SOLO los identificadores anonimizados ([PROVEEDOR_A], etc.)
Yo mantendre la tabla de correspondencia por separado.
```

### Paso D — Tabla de correspondencia (solo local, NUNCA en Claude)

Crea manualmente (sin usar Claude) un archivo local con la correspondencia:

```
ARCHIVO: correspondencia-contratos.xlsx (NO compartir con Claude)

[EMPRESA_A]    = Tu empresa
[PROVEEDOR_A]  = Nombre real del proveedor 1
[PROVEEDOR_B]  = Nombre real del proveedor 2
[PROVEEDOR_C]  = Nombre real del proveedor 3
...
```

> **Importante:** Este archivo nunca debe estar en una carpeta accesible por Claude. Guardalo en la carpeta `confidencial/` que configuraremos en el siguiente ejercicio.

**Preguntas de reflexion:**
1. Si Claude tuviera acceso al contrato completo, que datos podria memorizar entre sesiones?
2. La anonimizacion clausula a clausula pierde contexto importante?
3. Como verificarias que no has dejado un nombre real por error en una clausula anonimizada?
4. El departamento legal aceptaria un analisis hecho por IA? Con que condiciones?

> **Leccion clave:** El analisis clausula a clausula con anonimizacion previa te da el 90% del valor con el 10% del riesgo. Claude no necesita saber *quien* firma para detectar una clausula de exclusividad abusiva.

---

## Ejercicio 4: Configuracion del entorno para proteger datos

**Contexto:** Vas a configurar tu entorno de trabajo para que Claude Code no pueda acceder a datos confidenciales, ni siquiera por accidente.

### Paso A — Crear el archivo .claudeignore

En la raiz de tu carpeta de trabajo, crea un archivo `.claudeignore` (funciona como `.gitignore` pero para Claude Code):

```
# Archivos con credenciales
.env
.env.*
*.key
*.pem
*.p12
*.pfx
credentials.json
service-account.json

# Carpetas confidenciales
confidencial/
privado/
personal/
rrhh/
legal/contratos-originales/

# Archivos con datos sensibles
*password*
*secret*
*credential*
salarios*.csv
nominas*.pdf
contratos-originales/

# Copias de seguridad (pueden contener datos antiguos)
backup/
*.bak
*.old

# Archivos temporales de Office (pueden contener metadatos)
~$*
*.tmp
```

### Paso B — Estructura de directorios recomendada

Organiza tu carpeta de trabajo con dos zonas claramente separadas:

```
Mi-Proyecto/
├── trabajo/                    <- Claude PUEDE acceder aqui
│   ├── CLAUDE.md              <- reglas del proyecto
│   ├── .claudeignore          <- exclusiones
│   ├── datos-anonimizados/    <- CSVs limpios para analisis
│   ├── informes/              <- resultados generados
│   ├── scripts/               <- automatizaciones
│   └── plantillas/            <- templates reutilizables
│
├── confidencial/               <- Claude NO puede acceder aqui
│   ├── datos-originales/      <- CSVs con datos personales
│   ├── contratos-originales/  <- contratos sin anonimizar
│   ├── credenciales/          <- .env, tokens, certificados
│   ├── correspondencia/       <- tabla de anonimizacion
│   └── README.md              <- "Esta carpeta NO se comparte con IA"
```

Crea esta estructura:

```
mkdir -p trabajo/datos-anonimizados trabajo/informes trabajo/scripts trabajo/plantillas
mkdir -p confidencial/datos-originales confidencial/contratos-originales confidencial/credenciales confidencial/correspondencia
```

### Paso C — Reglas de privacidad en CLAUDE.md

Anade estas reglas al archivo `CLAUDE.md` de tu carpeta de trabajo:

```markdown
# Reglas de privacidad

## Datos personales
- NUNCA procesar archivos que contengan DNI, NIF o numero de seguridad social
- NUNCA procesar archivos con nombres asociados a salarios, evaluaciones o datos medicos
- Si un archivo contiene datos personales por error, avisar y NO procesarlo
- Los datos siempre se anonimizan ANTES de ser procesados

## Flujo obligatorio para datos sensibles
1. El usuario anonimiza los datos fuera de Claude
2. Claude recibe SOLO los datos anonimizados
3. Claude procesa y genera resultados
4. El usuario re-identifica los resultados si es necesario (fuera de Claude)

## Carpetas restringidas
- /confidencial — NUNCA acceder, leer ni listar archivos
- Cualquier carpeta llamada "privado", "personal" o "rrhh" — NUNCA acceder

## Verificacion post-proceso
Al terminar cualquier tarea con datos, confirmar:
- No se han mostrado datos personales en la conversacion
- Los archivos generados no contienen datos de la lista de exclusion
- Los archivos temporales se han eliminado
```

### Paso D — Test de verificacion

Prueba que tu configuracion funciona:

```
Intenta listar los archivos en la carpeta confidencial/.
Que resultado obtienes?

Ahora intenta leer el archivo confidencial/datos-originales/salarios.csv.
Que resultado obtienes?

Finalmente, lista los archivos en trabajo/datos-anonimizados/.
Este si deberia funcionar.
```

**Preguntas de reflexion:**
1. El `.claudeignore` impide que Claude *acceda* a los archivos, pero impide que *sepa que existen*?
2. Si copias un archivo de `confidencial/` a `trabajo/` por error, el `.claudeignore` te protege?
3. Como explicarias esta configuracion a un companero que no conoce Claude Code?
4. Revisarias periodicamente el `.claudeignore` para anadir nuevos patrones?

> **Leccion clave:** La proteccion de datos no es un prompt: es una configuracion de entorno. `.claudeignore`, estructura de carpetas y reglas en `CLAUDE.md` trabajan juntos para crear un perimetro seguro. Configuralo una vez y olvidate de recordarlo en cada conversacion.

---

## Resumen de aprendizajes

| Situacion | Estrategia | Herramienta |
|-----------|-----------|-------------|
| Datos personales (RRHH, salarios) | Anonimizar antes de analizar | Script de eliminacion de columnas |
| Datos financieros (facturas, IBAN) | Lista explicita de inclusion/exclusion | Prompt con reglas claras |
| Documentos legales (contratos) | Clausula a clausula, con anonimizacion | Tabla de correspondencia local |
| Configuracion general | Separar zonas accesibles y restringidas | .claudeignore + estructura de carpetas |

**Principio fundamental:** Los datos sensibles nunca deberian llegar a Claude. No se trata de confiar en que Claude los proteja — se trata de que nunca los vea. La anonimizacion previa es siempre mas segura que la confianza posterior.
