# Plan de contenido: de la Academia a los cursos de video

Fecha: 2026-08-06. Responsable de arquitectura: Fable (guiones, diseño de
curso); agentes sonnet/opus escriben el codigo de los clips y librerias.

## Idea central

`code-academy-platform` tiene 14 cursos y ~124 lecciones de texto. **No** se
traduce un curso de la Academia a un curso de video: se **desmenuza** — cada
curso de video toma un hilo conceptual (3-6 lecciones, a veces cruzando
cursos) y lo cuenta en 8 clips animados de 25-45 s con el tema oficial
CO.DE Academy (`code_brand.py`).

## Cursos de video existentes (ya en produccion)

| # | Curso | Origen | Estado |
|---|-------|--------|--------|
| 1 | Fractales: la belleza de los numeros complejos | original | publicado |
| 2 | Satelites e IA: la red que aprende a gobernarse | original | publicado |
| 3 | Mecanica orbital: el ballet de la gravedad | Academy: Mecanica Orbital L1-L9 | publicado |
| 4 | Señales y espectro: de Fourier al enlace satelital | Academy: Señales y sistemas + SDR | publicado |

## Cola de cursos nuevos (desmenuzado)

| Prio | Curso de video (8 clips) | Lecciones fuente (Academy) | Libreria nueva | Estado |
|------|--------------------------|----------------------------|----------------|--------|
| 1 | **Redes neuronales: la maquina que aprende** | IA L2-L6 (gradiente, regresion, logistica, redes, backprop, sobreajuste) | `aprendizaje.py` | **validado en local** (8 clips ql revisados frame a frame; falta qh + narracion en prod) |
| 2 | De la palabra al vector: embeddings y atencion | IA L8-L9 (NLP, embeddings, transformers) | `atencion.py` | **validado en local** (8 clips ql revisados frame a frame; falta qh + narracion en prod) |
| 3 | Agentes de IA: maquinas que operan el mundo | IA L10 + IA Agentica L1, L2, L5-L7 | `agentes.py` | **validado en local** (8 clips ql revisados frame a frame; falta qh + narracion en prod) |
| 4 | SDR: la radio hecha software | SDR L3-L6 (IQ, FFT, waterfall, demodulacion) | `radio.py` | **validado en local** (8 clips ql revisados frame a frame; falta qh + narracion en prod) |
| 5 | Apuntar a un satelite: el arte del seguimiento | APT L1-L4, L6 (Az/El, Doppler, PID) | `apuntado.py` (+ reusa `satelites.py`) | **validado en local** (8 clips ql revisados frame a frame; falta qh + narracion en prod) |
| 6 | El espectro: la guerra invisible por las ondas | Espectro L1-L4, L6 (bandas, lluvia, UIT, NGSO-GSO) | `espectro.py` | **validado en local** (8 clips ql revisados frame a frame; falta qh + narracion en prod) |
| 7 | Control: domar sistemas que se resisten | Señales y sistemas L10-L12, L16 + APT L6-L7 | `control.py` | **validado en local** (8 clips ql revisados frame a frame; falta qh + narracion en prod) |
| 8 | Materiales que van al espacio | Materiales M1-M5 + Elasticidad M1 | `materia.py` | pendiente |

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
3. **Validacion local**: render `ql` en Docker + revision visual de frames
   (regla dura: **nada encimado**; los textos se relevan con `Rotulos`).
4. **Subida**: `studio/tools/subir_curso.py` sincroniza el directorio del
   curso con la DB del backend (proyecto + clips) usando los modulos de
   `app/` — mismas validaciones que la API.
5. **Produccion (VPS)**: pull, subir_curso, renders `qh` por la cola del
   Studio, narracion TTS, export + mux.

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
