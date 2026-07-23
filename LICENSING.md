# Licencias — machinebooks.ai

Este repositorio contiene el **código compañero** (companion code) de la serie de
libros *El Profesional y la Máquina* / *The Professional and the Machine*. No todo
en el proyecto está bajo la misma licencia: el **código compañero** es abierto, pero el
**contenido editorial** y el **pipeline de producción** no lo son. Este documento
explica, capa por capa, qué puedes hacer con cada parte.

En caso de conflicto entre este documento y el fichero [`LICENSE`](LICENSE), para
el código compañero de las carpetas `EN/` y `ES/` prevalece [`LICENSE`](LICENSE).
Para el resto del repositorio se aplican las delimitaciones de este documento.

---

## Resumen

| Capa | Qué es | Licencia | Disponibilidad |
|------|--------|----------|----------------|
| Código compañero (`EN/`, `ES/`) | Ejemplos, scaffolds y ejercicios de los capítulos | **MIT** | Público y reutilizable |
| Texto de los libros | El contenido íntegro de cada libro de la serie | **Copyright editorial — todos los derechos reservados** | No incluido |
| Videocursos | Las formaciones en vídeo derivadas de los libros | **Copyright editorial — todos los derechos reservados** | No incluidos |
| Pipeline de producción (`formaciones/`) | Tooling libro → videocurso | **Propietario — todos los derechos reservados** | Código visible, sin licencia de reutilización |

---

## 1. Código compañero — MIT (abierto a propósito)

Todo el código de las carpetas [`EN/`](EN/) y [`ES/`](ES/) se publica bajo la
licencia **MIT**, cuyo texto íntegro está en [`LICENSE`](LICENSE):

> Copyright (c) 2026 Carlos Pérez González and Juan Carlos Montes Senra

Esta elección es **deliberada**. El objetivo del código compañero es la **máxima
difusión**: que cualquiera pueda clonar, copiar, modificar, integrar en sus
proyectos —comerciales o no— y aprender de los ejemplos sin fricción legal. MIT es
una licencia permisiva con pocas restricciones y sirve bien a ese objetivo.

El código es **didáctico**: son andamiajes de partida y ejemplos comentados con
referencias a los capítulos, no plataformas listas para producción. Liberarlo bajo
MIT no compromete el negocio, porque el valor no está en el software (ver
sección 5).

**Puedes**, sin pedir permiso: usar, copiar, modificar, fusionar, publicar,
distribuir, sublicenciar y vender copias del código, siempre que conserves el aviso
de copyright y de licencia de [`LICENSE`](LICENSE).

---

## 2. Texto de los libros — copyright editorial (todos los derechos reservados)

El **texto íntegro** de cada libro de la serie *El Profesional y la Máquina* es
**obra editorial protegida por copyright, con todos los derechos reservados**. No
forma parte de la licencia MIT y **no** se incluye en este repositorio.

Esto abarca la redacción, estructura, capítulos, ilustraciones, diagramas y
cualquier material narrativo o pedagógico de los libros. Los libros se adquieren a
través de los canales oficiales (Amazon y [machinebooks.ai](https://machinebooks.ai/)).

**No está permitido** sin autorización expresa por escrito: reproducir, redistribuir,
traducir, adaptar, resumir, republicar ni crear obras derivadas del texto de los
libros; ni entrenar modelos ni construir productos a partir de su contenido
editorial.

> El fragmento de código que aparezca *dentro* de un libro se rige por la MIT en su
> versión publicada en este repositorio (carpetas `EN/` y `ES/`). La **prosa que lo
> rodea, lo explica y lo estructura** es copyright editorial.

---

## 3. Videocursos — copyright editorial (todos los derechos reservados)

Los **videocursos** (formaciones en vídeo) derivados de los libros son igualmente
**obra editorial protegida por copyright, con todos los derechos reservados**. Se
distribuyen exclusivamente por los canales oficiales de formación.

**No está permitido** sin autorización expresa por escrito: descargar, reproducir en
público, redistribuir, revender, transcribir, doblar, subtitular ni crear obras
derivadas de los videocursos.

---

## 4. Pipeline de producción — propietario y fuera de MIT

La carpeta [`formaciones/`](formaciones/) contiene tooling del **pipeline de
producción que transforma cada libro en su videocurso**. El código está visible en
este repositorio, pero se mantiene **propietario y fuera de la licencia MIT**:

- No está cubierto por la licencia MIT del código compañero.
- Su visibilidad pública no concede permiso de uso, copia, modificación o
  distribución.
- Todos los derechos sobre esta carpeta están reservados por sus autores.

No está permitido usar, copiar, ejecutar, modificar ni distribuir el contenido de
`formaciones/` sin autorización expresa por escrito de los autores.

---

## 5. El foso legal

Conviene ser explícito sobre la estrategia, porque explica por qué el código es MIT
sin que eso ponga en riesgo el negocio:

**El foso no es la licencia de software. El foso es el copyright editorial + la marca.**

- El **código compañero** se publica bajo MIT porque su valor es de difusión, no de exclusividad.
  Copiarlo no reproduce el producto.
- Lo que **sí** está protegido y constituye el activo defendible es:
  1. El **texto íntegro** de los libros (copyright editorial).
  2. Los **videocursos** (copyright editorial).
  3. El **pipeline de producción** libro → videocurso (propietario y fuera de MIT).
  4. La **marca** *El Profesional y la Máquina* / *The Professional and the Machine*
     y *machinebooks.ai*.

Quien copie el código no obtiene los libros, ni los cursos, ni la capacidad de
producirlos, ni el derecho a usar la marca. Ahí está la defensa.

---

## Marcas

*El Profesional y la Máquina*, *The Professional and the Machine*, los títulos de la
serie y *machinebooks.ai* son marcas de sus autores. La licencia MIT del código **no**
otorga ningún derecho sobre estas marcas.

## Contacto

Para cualquier autorización de uso fuera de lo que permite la licencia MIT del
código, contacta con los autores a través de
[machinebooks.ai](https://machinebooks.ai/).

---

*Autores: Carlos Pérez González y Juan Carlos Montes Senra — © 2026. Todos los
derechos reservados sobre el contenido editorial, los videocursos y el pipeline de
producción. El código compañero se publica bajo licencia MIT (ver [`LICENSE`](LICENSE)).*
