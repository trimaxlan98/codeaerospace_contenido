# Plan de contenido: de la Academia a los cursos de video

Fecha: 2026-08-06 (ultima actualizacion: 2026-08-14). Responsable de
arquitectura: Fable (guiones, diseño de curso); agentes sonnet/opus escriben
el codigo de los clips y librerias.

## Idea central

Hay dos formatos vivos. El original (cursos 1-13) desmenuza la Academy en
cursos de 8 clips; el nuevo (familia "Aerodinamica", desde 2026-08-14) parte
de un documento maestro de curso autogestivo y hace **un proyecto por
leccion**, con un clip por subtema. Lo que NO cambia entre los dos: el tema
oficial `code_brand`, la libreria por familia, el rango de 28-45 s por clip y
la validacion visual de frames.

`code-academy-platform` tiene 14 cursos y ~124 lecciones de texto. **No** se
traduce un curso de la Academia a un curso de video: se **desmenuza** — cada
curso de video toma un hilo conceptual (3-6 lecciones, a veces cruzando
cursos) y lo cuenta en 8 clips animados de 25-45 s con el tema oficial
CO.DE Academy (`code_brand.py`).

## Cursos de video existentes (ya en produccion)

Los cuatro primeros son anteriores al plan (sus scripts solo viven en la DB
de produccion). Del 5 al 12 son la cola original del desmenuzado, cerrada el
2026-08-07: los 8 estan versionados en git, renderizados en `qh` en el VPS,
narrados con TTS y con su video final en `exports/<slug>/curso_narrado.mp4`.

| # | Curso | Origen | Libreria | Estado |
|---|-------|--------|----------|--------|
| 1 | Fractales: la belleza de los numeros complejos | original | — (solo en DB) | publicado |
| 2 | Satelites e IA: la red que aprende a gobernarse | original | — (solo en DB) | publicado |
| 3 | Mecanica orbital: el ballet de la gravedad | Academy: Mecanica Orbital L1-L9 | — (solo en DB) | publicado |
| 4 | Señales y espectro: de Fourier al enlace satelital | Academy: Señales y sistemas + SDR | — (solo en DB) | publicado |
| 5 | Redes neuronales: la maquina que aprende | IA L2-L6 (gradiente, regresion, logistica, redes, backprop, sobreajuste) | `aprendizaje.py` | publicado (PR #2) |
| 6 | De la palabra al vector: embeddings y atencion | IA L8-L9 (NLP, embeddings, transformers) | `atencion.py` | publicado (PR #2) |
| 7 | Agentes de IA: maquinas que operan el mundo | IA L10 + IA Agentica L1, L2, L5-L7 | `agentes.py` | publicado (PR #3) |
| 8 | SDR: la radio hecha software | SDR L3-L6 (IQ, FFT, waterfall, demodulacion) | `radio.py` | publicado (PR #4) |
| 9 | Apuntar a un satelite: el arte del seguimiento | APT L1-L4, L6 (Az/El, Doppler, PID) | `apuntado.py` (+ reusa `satelites.py`) | publicado (PR #5) |
| 10 | El espectro: la guerra invisible por las ondas | Espectro L1-L4, L6 (bandas, lluvia, UIT, NGSO-GSO) | `espectro.py` | publicado (PR #6) |
| 11 | Control: domar sistemas que se resisten | Señales y sistemas L10-L12, L16 + APT L6-L7 | `control.py` | publicado (PR #7) |
| 12 | Materiales que van al espacio | Materiales M1-M5 + Elasticidad M1 | `materia.py` | publicado (PR #8) |
| 13 | Cerrar el enlace: la cuenta en decibelios | Redes satelitales M2 (FSPL, PIRE, C/N0, G/T) + M7 (Shannon, MODCOD, ACM) | `enlace.py` | publicado (PR #9) |
| 14 | Matematicas en la naturaleza | original (divulgacion pura, heredero visual de Fractales) | `naturaleza.py` | publicado (PR #11) |
| 15 | Caos: el orden escondido | original (divulgacion pura, tercer titulo de la linea visual) | `caos.py` | publicado (PR #12) |
| 16 | Relatividad y el GPS | original (divulgacion pura, fisica aplicada a ingenieria) | `relatividad.py` | publicado (PR #13) |
| 17 | Tsiolkovsky: la tirania del cohete | original (divulgacion pura, astronautica) | `cohete.py` | publicado (PR #15) |
| 18 | Sistemas distribuidos: la nube por dentro | original (divulgacion, computo distribuido) | `distribuido.py` | publicado (PR #16) |

Los storyboards de los cursos 5-12 estan en `curso-01-*.md` .. `curso-08-*.md`
(la numeracion del archivo es la prioridad en la cola original, no el # de
esta tabla); del 13 en adelante, el numero de archivo ya es correlativo
(`curso-09-enlace.md` es el curso 13; `curso-11-matematicas-naturaleza.md`
es el curso 14, `curso-12-caos.md` el 15, `curso-13-relatividad-gps.md`
el 16, `curso-14-tsiolkovsky.md` el 17 y `curso-15-distribuidos.md` el
18 — el `curso-10` lo ocupa la familia Aerodinamica, que corre en su
propia rama con otro formato).

## Familia "Aerodinamica" (2026-08-14, formato nuevo)

Encargo distinto a todo lo anterior: la fuente no es la Academy sino un
**documento maestro de curso autogestivo** (Aerodinamica II, 4 modulos, 20
lecciones, 83 subtemas), y el cliente pide reciclarlo, asi que la familia se
titula **Aerodinamica** a secas, sin el "II".

Cambia la granularidad: **un proyecto de ManimStudio = una LECCION**, y cada
clip = un subtema. Son 4 clips de 33-45 s por proyecto (~2.5-3 min), no los 8
de los cursos 1-13. Los 20 proyectos comparten una sola libreria
(`aerodinamica.py`) y un solo `style_block` (el molde: entre dos lecciones
solo cambia su bloque `# --- Numeros de la leccion ---`).

Storyboard y contrato de la libreria: `curso-10-aerodinamica.md`.

| Leccion | Proyecto | Clips | Estado |
|---------|----------|-------|--------|
| 1.1 | El numero de Mach y los regimenes de vuelo | 4 | versionado, validado en local |
| 1.2 | Repaso de termodinamica aplicada | 4 | versionado, validado en local |
| 1.3 | La velocidad del sonido | 4 | versionado, validado en local |
| 1.4 | Ecuaciones de conservacion | 4 | versionado, validado en local |
| 1.5 | Propiedades de estancamiento e isentropicas | 4 | versionado, validado en local |
| 2.1 | Naturaleza fisica de la onda de choque | 4 | versionado, validado en local |
| 2.2 | Relaciones de la onda de choque normal | 4 | versionado, validado en local |
| 2.3 | Medicion de velocidad en flujo compresible | 4 | versionado, validado en local |
| 2.4 | Flujo cuasi-unidimensional en conductos | 4 | versionado, validado en local |
| 2.5 | Toberas convergentes y De Laval | 5 | versionado, validado en local |
| 3.1 | Ondas de choque oblicuas | 4 | versionado, validado en local |
| 3.2 | La relacion theta-beta-M | 4 | versionado, validado en local |
| 3.3 | Reflexion e interaccion de ondas | 4 | versionado, validado en local |
| 3.4 | Expansion de Prandtl-Meyer | 4 | versionado, validado en local |
| 3.5 | Teoria de choque-expansion | 5 | versionado, validado en local |
| 4.1 | Potencial de perturbacion linealizado | 4 | versionado, validado en local |
| 4.2 | Correcciones de compresibilidad subsonica | 4 | versionado, validado en local |
| 4.3 | Mach critico y divergencia del arrastre | 4 | versionado, validado en local |
| 4.4 | El regimen transonico | 4 | versionado, validado en local |
| 4.5 | Teoria linealizada y panorama hipersonico | 5 | versionado, validado en local |

**EL CURSO ESTA COMPLETO**: 20 lecciones y 83 clips, uno por subtema del
documento maestro. Pendiente: `subir_curso.py` contra produccion, renders
`qh`, narracion TTS y mux de los 20 proyectos.

## Familia "Electromagnetismo" (2026-08-14, mismo formato que Aerodinamica)

Segunda familia con el formato de lecciones: **un proyecto = una leccion de
4 clips**. Original (no viene de un documento maestro): 4 modulos x 3
lecciones = 12 proyectos, 48 clips, con TODOS los ejemplos apuntando a
telecomunicaciones y satelites. El arco: *de la carga de Coulomb al bit que
baja del satelite*. Una sola libreria (`electromagnetismo.py`, numeros
validados contra CODATA / ITU-R P.838-3 / WR-90 / orbita de Clarke) y un
solo style_block molde.

Storyboard y contrato de la libreria: `curso-16-electromagnetismo.md`.

| Leccion | Proyecto | Clips | Estado |
|---------|----------|-------|--------|
| 1.1 | La carga y el campo electrico | 4 | versionado, validado en local |
| 1.2 | La corriente y el campo magnetico | 4 | versionado, validado en local |
| 1.3 | La fuerza de Lorentz | 4 | versionado, validado en local |
| 2.1 | La induccion de Faraday | 4 | versionado, validado en local |
| 2.2 | Las ecuaciones de Maxwell | 4 | versionado, validado en local |
| 2.3 | La onda electromagnetica | 4 | versionado, validado en local |
| 3.1 | Las lineas de transmision | 4 | versionado, validado en local |
| 3.2 | La reflexion y la onda estacionaria | 4 | versionado, validado en local |
| 3.3 | Las antenas | 4 | versionado, validado en local |
| 4.1 | La ionosfera | 4 | versionado, validado en local |
| 4.2 | El enlace con el satelite | 4 | versionado, validado en local |
| 4.3 | El clima, el ruido y el margen | 4 | versionado, validado en local |

## Cola de cursos nuevos (desmenuzado de la Academy)

La cola original esta agotada. Los proximos cursos se eligen tema a tema.

| Prio | Curso de video (8 clips) | Lecciones fuente (Academy) | Libreria nueva | Estado |
|------|--------------------------|----------------------------|----------------|--------|
| — | _(por definir)_ | | | |

Criterio de prioridad: (1) riqueza visual con primitivas existentes o
factibles, (2) tamaño de audiencia, (3) actualidad del tema, (4) no
canibalizar cursos de video ya publicados.

## Pipeline por curso

1. **Diseño (Fable)**: storyboard clip a clip + `style_block` + contrato de
   la libreria nueva → `docs/plan_contenido/curso-NN-*.md`.
2. **Codigo (agentes)**: libreria en `studio/content/manim_extensions/`
   (opus) y clips en `studio/content/cursos/<slug>/clips/` (sonnet), todo
   **versionado en git** — a diferencia de los 4 cursos previos, cuyos
   scripts solo viven en la DB de produccion.
3. **Validacion local**: `studio/tools/render_local.py <curso> --todos`
   compone el script igual que el runner (style_block + clip + identidad) y
   lo renderiza en `ql` en Docker, dejando video y frames PNG en
   `render_jobs/validacion/<slug>/`. Revision visual obligatoria de esos
   frames (regla dura: **nada encimado**; los textos se relevan con
   `Rotulos`) y dos revisores de vision por curso antes de dar por bueno.
4. **Subida**: `studio/tools/subir_curso.py` sincroniza el directorio del
   curso con la DB del backend (proyecto + clips) usando los modulos de
   `app/` — mismas validaciones que la API.
5. **Produccion (VPS)**: pull, subir_curso, renders `qh` por la cola del
   Studio, narracion TTS (`studio/tools/guiones.py`), export + mux.

### Restricciones operativas (aprendidas en los 8 cursos de la cola)

- **Duracion de clip: 28-45 s**, tope duro. `render_local.py` avisa cuando
  un clip se sale del rango.
- **Pies de al menos 5 s**, y el pie cambia **antes** del transform que
  ilustra — nunca despues.
- **El VPS no tiene `ffmpeg`**: el mux final (clips + voz →
  `exports/<slug>/curso_narrado.mp4`) se hace en local, con los renders `qh`
  bajados del VPS.
- Imagen Docker local: `codeaerospace_contenido-manim` (no
  `manimstudio-render`, que es otra cosa).
- Render `qh` ≈ frames/2.5 s (Cairo single-thread); el timeout del VPS es
  1200 s por job.

## Arrancar un curso nuevo

1. Elegir el hilo conceptual y las lecciones fuente; anotarlo en la cola de
   arriba con su libreria nueva.
2. Escribir el storyboard en `docs/plan_contenido/curso-NN-<tema>.md`
   siguiendo el formato de los ocho existentes (paleta con nombres `C_*`,
   clip a clip: intencion, visual, rotulos y pies literales, final_state).
3. Rama `curso/<tema>`, libreria en `manim_extensions/`, curso en
   `studio/content/cursos/<slug>/` (`curso.json` + `style_block.py` +
   `clips/NN-*.py`, una clase `ClipN(Scene)` por archivo).
4. `render_local.py --todos --frames 8` → revision visual → fixes.
5. `cd studio/backend && venv/bin/pytest -q` (los tests del Studio deben
   seguir en verde) → PR → merge → deploy y narracion en el VPS.

## Estructura versionada de un curso

```
studio/content/cursos/<slug>/
  curso.json        # name, description, quality, lista de clips (titulo,
                    # escena, archivo, final_state)
  style_block.py    # el bloque de estilo completo del proyecto
  clips/NN-slug.py  # un archivo por clip: SOLO la clase ClipN(Scene)
```

## Reglas anti-encimamiento (prioridad: el espectador)

- Todo texto narrativo pasa por `Rotulos` (zonas `arriba`/`abajo`): el
  rotulo nuevo desvanece al anterior de su zona; jamas coexisten dos.
- `pie_curso` y `formula_pie` comparten zona — nunca se suman.
- Titulos y pies se auto-encogen si exceden el ancho util del frame.
- Mobiliario de figura (tags de eje, llaves) se coloca respecto a los ejes
  con `buff` explicito y se retira antes de introducir el siguiente.
- Validacion visual obligatoria de frames antes de dar un clip por bueno.
