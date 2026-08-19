# Catálogo de cursos — cómo se agrupan en el índice de Proyectos

Fecha: 2026-08-15 · Herramienta que lo aplica: `studio/tools/ordenar_cursos.py`

## La regla que impone el índice

La vista Proyectos no tiene campo de "área": deduce la **familia** partiendo el
nombre por el primer `·` y quedándose con lo de delante (`Projects.jsx:splitName`).
Dos consecuencias que mandan sobre todo lo demás:

1. **Un prefijo con un solo proyecto no forma grupo** — cae en *Cursos sueltos*.
   Por eso ninguna área tiene menos de dos cursos.
2. **Dentro de una familia se ordena por la etiqueta**, no por fecha
   (`localeCompare`). Por eso cada curso monográfico lleva un número delante: es
   lo único que fija el orden de lectura.

El nombre es, además, la **clave de emparejamiento** de `subir_curso.py:86`. Ver
"Cómo se aplica" antes de tocar un nombre a mano.

## Antes

58 proyectos: tres familias numeradas (Aerodinámica 1.1–4.5, Electromagnetismo
1.1–4.3, Metrología óptica 1.1–3.3; desde 2026-08-19 también Álgebra lineal 1.1–4.3) y **16 cursos monográficos de 8 clips en un
montón plano**, ordenados por actividad — es decir, por el azar de qué se tocó
la última vez.

## Después — 5 áreas

Cada área es una secuencia de lectura, no una etiqueta suelta: el número dice
por dónde se empieza.

### Comunicaciones — del espectro a apuntar la antena
| # | Curso |
|---|-------|
| 1 | El espectro: la guerra invisible por las ondas |
| 2 | SDR: la radio hecha software |
| 3 | Cerrar el enlace: la cuenta en decibelios |
| 4 | Apuntar a un satélite: el arte del seguimiento |

Primero qué es el recurso que se disputa, luego cómo se fabrica la radio que lo
usa, luego si el enlace cierra, y por último cómo se mantiene apuntado. Es la
continuación aplicada del módulo 4 de Electromagnetismo (ionosfera, enlace con
el satélite, clima y margen), que se queda en la física.

### Información y cómputo — medir la información, guardarla, repartirla
| # | Curso |
|---|-------|
| 1 | Teoría de la información: los bits de Shannon |
| 2 | Criptografía: el arte de guardar secretos |
| 3 | Sistemas distribuidos: la nube por dentro |

Shannon define qué es un bit y cuánto cabe; la criptografía decide quién puede
leerlo; los sistemas distribuidos, cómo sobrevive repartido entre máquinas que
fallan.

### Inteligencia artificial — la red, el lenguaje, el agente
| # | Curso |
|---|-------|
| 1 | Redes neuronales: la máquina que aprende |
| 2 | De la palabra al vector: embeddings y atención |
| 3 | Agentes de IA: máquinas que operan el mundo |

Progresión literal del campo: aprender una función, representar lenguaje, actuar
sobre el mundo.

### Sistemas dinámicos — el patrón, su ruptura, su control
| # | Curso |
|---|-------|
| 1 | Matemáticas en la naturaleza |
| 2 | Caos: el orden escondido |
| 3 | Control: domar sistemas que se resisten |

Los tres tratan la misma pregunta desde tres ángulos: qué patrón produce una
regla iterada (Fibonacci, fractales, Turing, Gray-Scott), cuándo esa misma
iteración deja de ser predecible (mapa logístico, Lorenz, Lyapunov) y cómo se
sujeta un sistema que se resiste (realimentación, estabilidad).

### Astronáutica — subir, sobrevivir allá arriba, medir el tiempo
| # | Curso |
|---|-------|
| 1 | Tsiolkovsky: la tiranía del cohete |
| 2 | Materiales que van al espacio |
| 3 | Relatividad y el GPS |

El coste de llegar, lo que aguanta el que llega, y la física fina que hace útil
al que ya está arriba.

### Lo que sigue suelto, a propósito
**Marca · Intro y cierre** (2 clips) no es un curso: son los clips de identidad
para posproducción. Su prefijo `Marca ·` no forma grupo porque está solo, y así
se queda — inventarle compañía sería peor que dejarlo en *Cursos sueltos*.

## Cómo se aplica

El nombre vive en **tres** sitios que tienen que ir a la par:

1. `studio/content/cursos/<slug>/curso.json` → campo `name` (la fuente en git).
2. `guiones/<slugify(nombre)>/` → las narraciones ya generadas.
3. La tabla `projects` de `manimstudio.db` (lo que ve la app).

**(1)** porque `subir_curso.py` empareja el proyecto **por nombre exacto**: si
solo se cambiara la base, la siguiente subida de ese curso no reconocería su
proyecto y **crearía un duplicado con todos sus clips**.

**(2)** porque el directorio de narración **no se guarda en ninguna parte: se
deriva del nombre** (`narracion.destino` → `guiones_dir / slugify(name)`).
Renombrar el proyecto sin mover su carpeta deja las narraciones huérfanas: los
16 cursos aparecerían como *sin narración*, su zip saldría sin `.wav` ni
`.txt`, y regenerarlas costaría ~128 llamadas a Vertex y su TTS — aunque los
archivos siguieran intactos en disco. Este punto se descubrió auditando el
script antes de correrlo en producción y por eso lo hace él mismo, en el mismo
paso y antes de tocar la base (así, cuando la app ve el nombre nuevo, su
carpeta ya está donde la va a buscar).

Por eso el renombrado se hace con una sola herramienta, idempotente y con
dry-run por defecto:

```bash
# plan, sin escribir nada
studio/backend/venv/bin/python studio/tools/ordenar_cursos.py

# aplicar en el VPS (repo + base de producción)
studio/backend/venv/bin/python studio/tools/ordenar_cursos.py --aplicar
```

Estado: **aplicado en el repo y en producción** (2026-08-15). Verificado sobre
un banco de pruebas con los nombres viejos antes de tocar el VPS: 16/16
proyectos renombrados, **cero narraciones huérfanas**, contenido preservado y
segunda pasada sin cambios (idempotente).

**El prefijo de área no entra en el video.** Los `style_block.py` y las librerías de
`manim_extensions/` siguen rotulando en pantalla "Relatividad y el GPS", no
"Astronáutica · 3 Relatividad y el GPS": el área ordena el índice de trabajo, no es
parte del título que ve el espectador. No hay que re-renderizar nada.

Renombrar toca `updated_at`, así que con el orden *por actividad* los 16 suben
al principio una vez. Con el orden *por nombre* el índice queda como se diseñó.
No toca clips, jobs ni renders: los videos ya renderizados siguen vigentes.
