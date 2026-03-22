# Capitulo 26 — Que NO delegar: limites practicos de la automatizacion

Ejercicios practicos para aprender a identificar tareas que requieren supervision humana, corregir prompts peligrosos y configurar barreras de seguridad en Claude Code. El objetivo es que desarrolles el criterio para distinguir entre delegacion productiva y delegacion irresponsable.

---

## Caso practico 1: El informe que salio mal

**Contexto:** Tu jefe te pide un informe trimestral de ventas para la reunion de direccion de manana. Tienes los datos en un CSV y decides pedirle a Claude que lo genere.

### Paso A — El prompt INCORRECTO

Este es el tipo de prompt que parece razonable pero genera problemas. Leelo y analiza que puede salir mal:

```
Genera un informe trimestral de ventas con los datos del archivo ventas-Q3.csv.
Hazlo bonito y profesional. Incluye graficos y conclusiones.
```

**Problemas de este prompt:**
1. **"Hazlo bonito"** — es subjetivo. Claude interpretara "bonito" a su manera
2. **"Incluye conclusiones"** — Claude inventara interpretaciones de negocio que pueden ser incorrectas
3. **No hay verificacion** — no le pides que muestre los datos antes de interpretarlos
4. **No hay formato especifico** — no sabes que vas a obtener hasta que lo tienes
5. **No hay limites** — Claude podria extrapolar tendencias o hacer predicciones sin base

### Paso B — El prompt CORREGIDO con verificacion

Ahora usa este prompt mejorado. Copialo tal cual y adaptalo a tu situacion:

```
Necesito preparar un informe trimestral de ventas. Vamos a hacerlo paso a paso.

PASO 1 - VERIFICACION DE DATOS:
Lee el archivo ventas-Q3.csv y muestrame:
- Numero total de filas
- Nombres de las columnas
- Rango de fechas que cubre
- 5 primeras filas como muestra

NO interpretes los datos todavia. Solo muestramelos para que yo los valide.
```

Cuando Claude te muestre los datos, revisalos. Confirma que:
- El numero de filas coincide con lo que esperas
- Las columnas son las correctas
- No hay datos corruptos o faltantes en la muestra
- El rango de fechas es el trimestre correcto

Solo despues de validar, continua con:

```
Los datos son correctos. Ahora genera el informe con estas reglas:

FORMATO: Markdown con tablas
CONTENIDO:
- Tabla resumen: ventas totales por mes
- Tabla detalle: top 10 productos por facturacion
- Tabla comparativa: este trimestre vs anterior (si hay datos)

REGLAS:
- Usa SOLO los datos del archivo. No inventes ni extrapoles.
- Si algun dato falta o es ambiguo, indicalo con "[DATO PENDIENTE]"
- No incluyas conclusiones ni recomendaciones. Eso lo hago yo.
- Al final, lista cualquier anomalia que detectes en los datos (valores atipicos, huecos, etc.)
```

### Paso C — Compara los resultados

Ejecuta ambos prompts (el incorrecto y el corregido) con el mismo archivo de datos.

**Preguntas de reflexion:**
1. Que diferencias observas entre ambos informes?
2. El primer informe incluyo datos inventados o interpretaciones no solicitadas?
3. Cuanto tiempo te ahorro la verificacion previa vs corregir un informe incorrecto?
4. Te fiarias del primer informe para presentarlo a direccion sin revisarlo linea por linea?

> **Leccion clave:** Delegar la generacion de datos es seguro. Delegar la *interpretacion* de datos de negocio es peligroso. Tu jefe espera tu criterio profesional, no el de una IA.

---

## Caso practico 2: Reorganizacion de archivos

**Contexto:** Tienes una carpeta con 500+ archivos acumulados durante dos anos: documentos de proyectos, plantillas, borradores, archivos temporales. Quieres reorganizarla con Claude Code.

### Paso A — Planificar ANTES de mover

No le pidas a Claude que reorganice directamente. Primero, pide un inventario:

```
Analiza la carpeta ~/Documentos/Proyectos y dame un inventario:

1. Numero total de archivos y tamano total
2. Distribucion por tipo de archivo (.docx, .pdf, .xlsx, etc.)
3. Distribucion por fecha de ultima modificacion (ultimo mes, ultimo trimestre, ultimo ano, mas antiguo)
4. Lista de archivos mayores de 50MB
5. Lista de archivos duplicados (mismo nombre en diferentes subcarpetas)

NO muevas, renombres ni elimines nada. Solo analiza.
```

### Paso B — Definir la estructura destino

Con el inventario en mano, define tu la estructura. No dejes que Claude decida como organizar tu trabajo:

```
Quiero reorganizar con esta estructura:

/Proyectos
  /Activos          -> proyectos con archivos modificados en los ultimos 3 meses
  /Archivo-2025     -> proyectos sin actividad desde hace mas de 3 meses
  /Plantillas       -> archivos que contengan "plantilla" o "template" en el nombre
  /Pendiente-revision -> archivos que no encajen en ninguna categoria

Reglas:
- NO mover archivos de proyectos que esten activos (modificados en los ultimos 7 dias)
- NO eliminar nada. Ni siquiera duplicados.
- Generar un log en /Proyectos/reorganizacion-log.csv con: archivo_original, destino, fecha_movimiento, motivo

ANTES de ejecutar, muestrame el plan: cuantos archivos irian a cada carpeta.
Espera mi confirmacion para proceder.
```

### Paso C — Ejecutar con registro

Una vez aprobado el plan:

```
Aprobado. Ejecuta la reorganizacion con estas precauciones:

1. Crea las carpetas destino si no existen
2. MUEVE los archivos (no copies, para no duplicar espacio)
3. Si un movimiento falla, registralo en el log y continua con el siguiente
4. Al terminar, muestrame:
   - Resumen: archivos movidos por carpeta
   - Errores: archivos que no se pudieron mover
   - Verificacion: numero total de archivos ANTES vs DESPUES (debe ser identico)
```

### Paso D — Verificacion final

```
Cuenta el numero total de archivos en /Proyectos (incluyendo subcarpetas).
Compara con el numero del inventario inicial.
Si no coinciden, dime que archivos faltan o sobran.
```

**Preguntas de reflexion:**
1. Que habria pasado si le hubieras dicho simplemente "organiza mi carpeta de proyectos"?
2. Por que es importante excluir los proyectos activos?
3. El log de reorganizacion te permite deshacer la operacion si algo salio mal?
4. Aplicarias este mismo proceso a una carpeta compartida en red? Por que si o por que no?

> **Leccion clave:** La reorganizacion de archivos es reversible si tienes un log. Pero sin log, un error de clasificacion puede costarte horas buscando un archivo critico. El log no es opcional: es tu seguro.

---

## Caso practico 3: Servidor en produccion

**Contexto:** Un servidor de produccion esta respondiendo lento. Tu instinto es pedirle a Claude que investigue y arregle el problema.

### Paso A — El prompt PELIGROSO (NO USAR)

Lee este prompt y entiende por que es inaceptable. **No lo ejecutes nunca en un entorno real:**

```
PELIGROSO - NO EJECUTAR

El servidor de produccion esta lento. Conectate por SSH, investiga que pasa
y arreglalo. Si algun servicio esta consumiendo demasiados recursos, reinicialo.
Si hay procesos zombi, matalos. Si el disco esta lleno, elimina archivos de log
antiguos.
```

**Por que es peligroso:**
1. **"Reinicialo"** — reiniciar un servicio en produccion puede causar una caida visible para los usuarios
2. **"Matalos"** — matar procesos sin entender que hacen puede corromper datos
3. **"Elimina archivos de log"** — los logs pueden ser necesarios para una investigacion forense o auditoria
4. **Sin confirmacion** — Claude ejecutaria todo automaticamente
5. **Sin rollback** — no hay plan para deshacer si algo sale mal

### Paso B — El prompt SEGURO (solo investigacion)

```
Necesito diagnosticar por que un servidor esta lento. Vamos a investigar
SIN HACER CAMBIOS. Solo lectura.

Ejecuta estos comandos y muestrame los resultados:

1. uptime (carga del sistema)
2. free -h (memoria disponible)
3. df -h (espacio en disco)
4. top -bn1 | head -20 (procesos que mas CPU consumen)
5. ps aux --sort=-%mem | head -20 (procesos que mas memoria consumen)
6. tail -50 /var/log/syslog (ultimos eventos del sistema)
7. netstat -tlnp (puertos en escucha)

IMPORTANTE:
- NO reinicies ningun servicio
- NO mates ningun proceso
- NO elimines ningun archivo
- NO modifiques ninguna configuracion
- Si necesitas ejecutar algo que no sea solo lectura, PREGUNTAME PRIMERO
```

### Paso C — Analizar y decidir TU

Con los resultados del diagnostico, analiza:

```
Con los datos anteriores, dame tu analisis:

1. Cual parece ser la causa principal de la lentitud?
2. Que opciones tengo para resolverlo? (lista al menos 3, ordenadas de menor a mayor riesgo)
3. Para cada opcion, indica:
   - Que comando ejecutaria
   - Que impacto tendria en los usuarios
   - Como podria revertirlo si sale mal
   - Que deberia verificar despues de ejecutarlo

NO ejecutes nada. Solo dame el analisis para que yo decida.
```

### Paso D — Ejecutar con supervision

Solo despues de elegir la opcion, y solo si has evaluado el riesgo:

```
Voy a aplicar la opcion 2 (la que describiste como "[descripcion]").
Ejecutala paso a paso, esperando mi confirmacion entre cada paso.

Despues de cada paso:
- Muestrame el resultado
- Confirma que el servicio sigue respondiendo
- Espera mi "OK" para continuar

Si algo falla o produce un resultado inesperado, PARA inmediatamente y muestrame que paso.
```

**Preguntas de reflexion:**
1. Cuantas cosas podrian haber salido mal con el prompt peligroso?
2. El prompt seguro te llevo mas tiempo, pero cuanto tiempo habrias perdido si Claude hubiera reiniciado el servicio equivocado?
3. En tu empresa, quien deberia autorizar cambios en servidores de produccion?
4. Usarias Claude para diagnosticar un problema de seguridad (una intrusion)? Por que no?

> **Leccion clave:** En produccion, Claude es un excelente diagnosticador pero un ejecutor peligroso. La regla de oro: Claude investiga, tu decides, Claude ejecuta bajo tu supervision paso a paso.

---

## Ejercicio 4: Configuracion de seguridad en CLAUDE.md

**Contexto:** Vas a configurar reglas de seguridad para que Claude Code respete limites automaticamente en tus proyectos.

### Paso A — Reglas de seguridad en CLAUDE.md

Crea un archivo `CLAUDE.md` en la raiz de tu carpeta de trabajo con estas reglas de seguridad:

```markdown
# Reglas de seguridad

## Operaciones prohibidas
- NUNCA eliminar archivos sin confirmacion explicita
- NUNCA ejecutar comandos con sudo o como administrador
- NUNCA modificar archivos fuera de la carpeta del proyecto
- NUNCA enviar datos a URLs externas
- NUNCA ejecutar scripts descargados de internet sin revision previa

## Operaciones que requieren confirmacion
- Mover o renombrar mas de 5 archivos a la vez
- Modificar archivos de configuracion (.env, config.json, etc.)
- Instalar paquetes o dependencias nuevas
- Ejecutar comandos que accedan a red (curl, wget, ssh)

## Datos sensibles
- No leer ni procesar archivos en la carpeta /confidencial
- No incluir passwords, tokens ni claves API en las respuestas
- Si un archivo contiene datos personales, avisar antes de procesarlo

## Formato de respuesta para operaciones de riesgo
Antes de cualquier operacion que modifique el sistema, mostrar:
1. Que voy a hacer (descripcion en lenguaje natural)
2. Que comando exacto voy a ejecutar
3. Que podria salir mal
4. Como revertirlo
Esperar confirmacion del usuario.
```

### Paso B — Prompt para registro de operaciones

Anade este prompt a tu flujo de trabajo cuando uses Claude para tareas administrativas:

```
A partir de ahora, para cada operacion que ejecutes en esta sesion,
registra en el archivo operaciones-log.md:

- Fecha y hora
- Descripcion de la operacion
- Comando ejecutado
- Resultado (exito/error)
- Archivos afectados

Actualiza el log ANTES de ejecutar cada operacion.
Si el log no existe, crealo al inicio de la sesion.
```

### Paso C — Prompt para copias de seguridad

Usa este prompt antes de cualquier operacion masiva sobre archivos:

```
Antes de hacer cambios, crea una copia de seguridad:

1. Crea la carpeta backup-[FECHA] dentro del directorio actual
2. Copia (no muevas) todos los archivos que vas a modificar a esa carpeta
3. Genera un archivo backup-manifest.txt con la lista de archivos copiados
4. Muestrame el manifest para que lo verifique

Solo despues de mi confirmacion, procede con los cambios.
```

### Paso D — Prompt para exclusion de datos confidenciales

Cuando trabajes con carpetas que mezclan datos publicos y privados:

```
En esta carpeta hay archivos confidenciales y no confidenciales.

REGLAS DE EXCLUSION:
- Ignorar completamente cualquier archivo en subcarpetas llamadas "privado", "confidencial" o "personal"
- Ignorar archivos con extension .key, .pem, .p12, .pfx
- Ignorar archivos que contengan "password", "secret" o "credential" en el nombre
- Si encuentras un archivo .env, NO leas su contenido

Si durante el analisis necesitas acceder a un archivo que podria ser sensible,
preguntame antes de abrirlo.

Confirma que has entendido estas reglas antes de empezar.
```

**Preguntas de reflexion:**
1. Has revisado que tu CLAUDE.md cubre los riesgos especificos de tu entorno de trabajo?
2. El log de operaciones te serviria para auditar que hizo Claude en una sesion anterior?
3. La copia de seguridad es suficiente si Claude modifica un archivo de base de datos?
4. Que otras exclusiones anadiras segun el tipo de datos que manejas en tu trabajo?

> **Leccion clave:** La seguridad en Claude Code no depende de que Claude "sepa" que algo es peligroso. Depende de que tu configures barreras explicitas. CLAUDE.md es tu primera linea de defensa.

---

## Resumen de aprendizajes

| Leccion | Regla practica |
|---------|---------------|
| Informes y datos | Claude genera; tu interpretas y decides |
| Archivos y carpetas | Inventario primero, plan despues, log siempre |
| Servidores y produccion | Diagnostico si, ejecucion solo paso a paso con supervision |
| Seguridad | Configurar limites ANTES de empezar a trabajar |

**Criterio general:** si una accion es irreversible, o si afecta a personas, dinero o sistemas en produccion, Claude te ayuda a preparar pero **tu** ejecutas la decision final.
