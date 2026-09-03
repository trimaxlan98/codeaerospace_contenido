---
name: curso-de-video
description: Use when creating, extending, or publishing a CO.DE Academy video course in this repo — planning the arc of a course family, writing its manim_extensions library, producing lesson clips (alone or with subagents), validating frames, rendering qh locally, publishing to the VPS, narrating with TTS, and muxing with the brand intro/outro. Courses are MUTE by default (no narrative subtitles on screen: only titles, short labels and measured figures); subtitles are opt-in and only if the owner asks for them. Covers both FORMATS (horizontal familia of 4-clip lessons, and vertical 9:16 pieces for Instagram) and both visual STYLES (CONSOLA, the flight-console look of courses 1-30; and LIENZO, the flat navy 'one thing, one figure' look of course 31 — ask for it by name). Default style is CONSOLA.
---

# Curso de video CO.DE Academy

Cómo se produce un curso completo de punta a punta. Es el proceso destilado
de 31 cursos publicados; el más extenso es el 27, Procesamiento de señales:
30 lecciones, 120 clips y 74 minutos de vídeo. Complementa la skill
`manimstudio` (esa explica la app; ésta, el contenido).

El proceso es **el mismo para los dos formatos y los dos estilos**: cambia el
lienzo y el lenguaje visual, no los 10 pasos ni las herramientas. Por eso no
hay una skill por estilo — habría que mantener dos copias de todo y se
desincronizarían. Ver "Los dos ejes" más abajo.

**Lo primero que hay que saber**: desde el curso 27 los cursos se hacen **sin
subtítulos** salvo que el dueño los pida (ver "Formato mudo" más abajo).

**Antes de tocar nada**: invoca la skill `manimstudio`, lee las memorias
`manimstudio-pipeline-cursos`, `plan-contenido-academy` y la de la familia
vecina más parecida, y `docs/plan_contenido/PLAN.md` (numeración correlativa
de la colección).

## Vocabulario y formato

```
familia            ManimStudio                       DB
---------------    ------------------------------    -----------------
módulo   (K)   →   —  agrupación editorial            no existe
lección  (N)   →   proyecto "Familia · N.M Título"    projects
idea     (4N)  →   clip, HUD "MODULO 0K"              clips
```

- **Formato vigente (familias, desde 2026-08-14)**: un proyecto = una
  **lección de 4 clips**, un clip = una idea. Tamaños ya usados: 9, 12, 18,
  24 y **30** lecciones (el 27 es el mayor: 30 lecciones en 5 lotes de 6). Slugs `<familia>-N-M-<tema>`, nombre `Familia · N.M <título>`
  (el nombre es la clave de emparejamiento de `subir_curso.py`: no lo cambies
  después de subir).
- **Formato antiguo (cursos 1–21)**: un proyecto = un curso de 8 clips. Solo
  para temas que no dan para una familia.
- Fuente del temario: un hilo conceptual propio, un documento maestro, o el
  desmenuzado de `code-academy-platform`. Un curso nuevo **no re-explica** lo
  que ya cubrió otro: declara explícitamente qué capa ocupa y qué asume.

## Los dos ejes: FORMATO y ESTILO

No son lo mismo y se piden por separado.

**Formato** es la forma del lienzo y el tamaño de la pieza:

| Formato | Qué es | Cursos |
|---|---|---|
| **horizontal** | 16:9, familias de lecciones de 4 clips | 1–25, 27, 30 |
| **vertical** | 9:16 real (`promo.formato()`), piezas de 30–45 s sueltas, para Instagram | 26, 28, 29, 31, 32 |

**Estilo** es el lenguaje visual dentro del formato. Hay **dos**, y se elige
por curso, no por clip:

| Estilo | Qué se ve | Módulo | Cursos |
|---|---|---|---|
| **CONSOLA** | Estética de consola de vuelo de la marca: fondo casi negro `#05070a`, escuadras HUD en las esquinas, telemetría en Space Mono repartida por el frame, cifra con pie de tres renglones. **Denso a propósito.** | `code_brand.py` + `promo.py` | todos hasta el 30 |
| **LIENZO** | Superficie lisa azul marino `#0B1B33` con **una cosa y un dato**, cuatro carriles de un solo ocupante, paleta de cuatro colores con un acento, y nada más que la marca de agua (el número de pieza es opcional). **Vacío a propósito.** | `lienzo.py` | 31, 32 |

Para pedir uno u otro basta con nombrarlo: *«un curso vertical en estilo
LIENZO sobre X»*. Si no se dice nada, **el estilo por defecto es CONSOLA**
(es el de 30 de los 31 cursos y el que arrastra la identidad del canal).

El estilo se declara en `curso.json` con `"estilo": "lienzo"`, y la guía
completa de LIENZO —medidas del lienzo, guardianes, convención de color,
tabla de anchos tipográficos medidos— está en **`studio/docs/LIENZO.md`**.
Léela ENTERA antes de escribir el primer clip de un curso LIENZO; no
intentes deducir el estilo mirando un clip.

### El tercer eje: SONIDO (desde el curso 32)

| Sonido | Qué lleva | Cursos |
|---|---|---|
| **narrado** | voz TTS alineada a mano + cama de SFX | todos hasta el 31 |
| **mudo** | ninguna pista de audio: el dueño le pone música al publicar | 32 |

Se declara en `curso.json` con `"sonido": "mudo"` y se entrega con
`unir_vertical.py <curso> --mudo`.

**Un curso mudo NO es un curso narrado al que se le quita la voz.** Sin
narrador, la pantalla es lo único que explica, y este estilo no admite
subtítulos: si no se compensa, el clip se llena de texto y deja de ser
LIENZO. Se compensa con tres cosas y ninguna más:

1. **Una portada de ~3.7 s** (`L.portada(nombre, tesis)`) con el nombre de
   la pieza y **qué vuelve fácil**, en 5 palabras como mucho (tope duro).
   Es el único sitio del clip donde se explica con palabras.
2. **Un solo verbo visual** por pieza. Si para entenderlo hiciera falta una
   frase en pantalla, el verbo está mal elegido: se cambia el dibujo.
3. **Una cifra** al final.

Y cambia el ritmo: el hueco entre planos ya no lo llena una frase hablada,
así que es el único momento en que se puede entender lo que acaba de pasar.
`Pieza.leer(t)` sostiene el estado y **no admite menos de 1.8 s**.

**Cuándo elegir cuál.** CONSOLA sostiene bien la densidad: muchas cifras a la
vez, mobiliario de figura, varias señales conviviendo. LIENZO se rompe con la
densidad y brilla cuando cada clip tiene UNA idea con UN número — que es
justo lo que hace que cada pieza funcione sola como reel. Si el temario pide
tres cifras simultáneas en pantalla, el estilo equivocado es LIENZO.

## Formato mudo: SIN SUBTÍTULOS por defecto

**Desde el curso 27 (Procesamiento de señales), un curso nuevo se hace sin pie
narrativo salvo que el dueño pida lo contrario.** La palabra la pone la voz;
la pantalla pone la **cosa** y su **cifra**. Razón del dueño, con sus palabras
al ver el curso terminado: *"me gustó mucho más sin subtítulos, así no me
pierdo tanto"* — leer y mirar a la vez reparte la atención. El vertical
(curso 26) ya nacía así; desde el 27 el horizontal también.

Lo que puede haber en pantalla:

| Elemento | Helper | Límite |
|---|---|---|
| Título del clip (arriba) | `titulo_curso()` | ≤ 6 palabras |
| Etiqueta del módulo (UL) | `hud_modulo("Modulo 0N")` | fija |
| Rótulo de mobiliario (ejes, `x[n]`, `dB`) | `tag_junto()` | ≤ 4 palabras |
| **Cifra medida** (carril inferior) | `cifra_pie()` | ≤ 5 palabras |
| Cifra flotante | `tag_hud()` | ≤ 5 palabras |
| Columna de cifras (UR) | `panel_cifras()` | ≤ 5 por línea |
| Fórmula | `formula_pie()` | una línea |
| Dato NO calculado aquí | `dato_pie()` | ≤ 5 palabras, gris |
| Cierre del clip 4 | `cierre_leccion()` | 2 líneas |

**No se deja a la disciplina**: `pie_curso` **no se define** en el
`style_block`, y los helpers pasan por un `_vigilar()` que **aborta el render**
si un rótulo se convierte en frase. Con 30 lecciones y ~25 subagentes fue la
única forma de que la regla llegara viva al final; un agente que copie
`pie_curso` de otra familia revienta en el primer render, que es justo lo que
tiene que pasar.

**Consecuencia de ritmo**: el tiempo que antes sostenía la lectura del pie
(≥ 5 s) ahora lo sostiene la **animación**. Más `Create`/`Transform`/updaters y
menos `wait` largo y vacío. La duración sigue en 28–45 s.

**Implementación de referencia**, para copiar tal cual:
`studio/content/cursos/procesamiento-senales-1-1-muestreo/style_block.py`
(helpers, guardián y suelos tipográficos) y sus cuatro clips.

### Si el dueño SÍ pide subtítulos

Entonces vuelve la regla clásica, que sigue siendo válida: `pie_curso()` en la
zona `abajo`, **pies de ≥ 5 s legibles**, **el pie cambia ANTES** de la
animación que ilustra y los rótulos del momento anterior se apagan antes del
pie nuevo. Los cursos 1–26 son el modelo (p. ej.
`studio/content/cursos/comunicaciones-digitales-1-1-muestreo/`). En ese caso
se quita el guardián o se le sube el límite, y se declara en el §2 del plan
para que los subagentes lo sepan.

## Los 10 pasos

Para un curso grande, se parte en **lotes de ~6 lecciones** y cada lote
recorre los 10 pasos ENTERO antes de empezar el siguiente. Así se puede parar
en cualquier frontera de lote sin dejar nada a medias.

1. **Plan maestro** → `docs/plan_contenido/curso-NN-<tema>.md`. Ángulo
   editorial, mapa de lecciones, paleta por ROL, contrato de la librería,
   storyboard clip a clip, lotes y **tablero de estado**. Es el único estado
   que sobrevive a la sesión: todo lo necesario para reanudar vive ahí, no en
   la conversación. Plantilla: `references/plantilla-plan.md`.
2. **Librería** → `studio/content/manim_extensions/<tema>.py`. Piezas de
   dibujo + funciones numéricas, deterministas (`default_rng(semilla)`),
   reutilizando el sustrato de familias vecinas. **Se valida en el contenedor
   (cifras impresas + PNGs con PIL) ANTES de escribir un solo clip.**
3. **Molde**: la primera lección del lote la escribes TÚ entera (curso.json +
   style_block.py + 4 clips), la validas y la corriges. Es el molde que
   copian las demás.
4. **Esqueletos**: `curso.json` + stubs `class ClipN(Scene): self.wait(1)` de
   todas las lecciones del lote — `render_local.py` aborta si falta cualquier
   clip declarado, y sin stubs no se puede paralelizar.
5. **Producción**: una lección por subagente (Sonnet las mecánicas, Opus las
   conceptualmente delicadas), contrato en el scratchpad. Los agentes NO
   tocan la librería ni git. Ver `references/contrato-agente.md`.
6. **Revisión tuya** de los frames de todas las lecciones + `pytest -q` del
   Studio. Si un agente encontró un bug de la librería, corrígelo y **revisa
   los rodeos que otros clips hicieron para compensarlo** (y los `final_state`,
   que también citan cifras).
7. **PR y merge**: commit atómico con rutas explícitas, PR a `main`,
   `gh pr merge`.
8. **Producción en el VPS**: `git pull` + `subir_curso.py` por lección; los
   **`qh` se renderizan LOCAL** (3 en paralelo), se suben al staging y se
   adoptan con `adoptar_renders.py`.
9. **Narración**: `guiones.py` en el VPS, **SERIAL** (en paralelo el TTS da
   429), detached. Es idempotente.
10. **Mux local** con intro/cierre de marca, medir picos, re-muxear los que
    pasen de −0.5 dB, y **actualizar el tablero, `PLAN.md` y la memoria de la
    familia** antes de cerrar el lote.

Comandos exactos de los pasos 2 y 8–10: `references/comandos.md`.

## Reglas duras (no se renegocian por clip)

**Contenido**
- Clips de **28–45 s** (tope duro por ambos lados). Un clip de 26 s se
  engorda con `wait`, no metiendo más contenido.
- **Sin pie narrativo** (ver "Formato mudo"): la zona de abajo es el carril de
  la cifra. Si el dueño pidió subtítulos, entonces sí: pies de ≥ 5 s legibles,
  el pie cambia ANTES de la animación que ilustra, y los rótulos del momento
  anterior se apagan antes del pie nuevo.
- Un solo cierre a pantalla limpia por lección (clip 4), dos líneas, la
  segunda en cian.
- **Todo número en pantalla se calcula** en la librería con numpy y semilla
  fija. Cero cifras inventadas. Si se dibuja una ventana de una simulación
  más larga, la estadística se mide **sobre la ventana dibujada**. Lo que la
  librería no calcula (datos públicos) se declara como tal **en gris**
  (`dato_pie`), para que el cian siga significando "medido aquí".
- **Lo que depende de la malla no se rotula.** La profundidad de un nulo, de un
  notch o de los ceros de un CIC cambia con el número de puntos de la rejilla
  (−119 dB con 4096, −141 con 16384). Se rotula lo que NO se mueve al cambiar
  la malla: la posición del nulo, el nivel de los lóbulos, el ancho del hueco.
- Si algo se exagera de escala, se declara con una etiqueta corta.

**Forma**
- Tema oficial `code_brand` en todos los clips (branding automático salvo que
  el script mencione `code_brand`).
- **Sin acentos en el texto renderizado** (Rajdhani/Space Mono); los acentos
  viven en `curso.json`, que no se renderiza. Superíndices, griegas y `≈`
  solo en `MathTex`.
- **Nada encimado**: revisión de frames UNO A UNO, obligatoria, antes de dar
  un clip por bueno. Las piezas densas se dimensionan **midiendo**, nunca a
  ojo.
- `Transform` solo entre gemelas de estructura IDÉNTICA.

**Proceso**
- `qh` **local** (3 procesos en 8 cores, ~1 min/clip); el VPS tarda ~16
  min/clip: nunca encolar `qh` allí.
- Narración **serial**, siempre.
- Mux **local**: el VPS no tiene ffmpeg.
- Commits: asunto **sin acentos**, rutas explícitas, nunca `git add -A`. Los
  mp4 de `exports/` no se versionan.
- Si el checkout principal está ocupado (otra rama, un cron), trabaja en un
  **git worktree** aparte usando el venv del checkout principal.
- Deja el **tablero al día** antes de que se agote la sesión: la siguiente
  corrida debe poder continuar sin rehacer nada.

## Trampas

`references/trampas.md` — catálogo acumulado (librería, composición,
tipografía, honestidad, herramientas). Léelo antes de escribir clips y
páselo a los subagentes: cada familia repite las mismas.

## Cierre de familia

No está terminada hasta que: las lecciones están en prod con sus `qh`
adoptados, narradas y muxeadas; `PLAN.md` y `studio/docs/CATALOGO-CURSOS.md`
actualizados; la cosecha de trampas escrita en el plan; y la memoria
`familia-<tema>.md` (+ línea en `MEMORY.md`) con estado, decisiones y
trampas.

Y **la entrega se comprueba EN EL DISCO**, no en el tablero. `exports/` no
está versionado y vive en el segundo disco: que el plan diga "entregado" no
prueba que los mp4 sigan ahí. Lista el directorio del curso antes de cerrar.
