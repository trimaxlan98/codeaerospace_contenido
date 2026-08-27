---
name: curso-de-video
description: Use when creating, extending, or publishing a CO.DE Academy video course in this repo — planning the arc of a course family, writing its manim_extensions library, producing lesson clips (alone or with subagents), validating frames, rendering qh locally, publishing to the VPS, narrating with TTS, and muxing with the brand intro/outro. Covers both formats (familia = one project per lesson, and the old 8-clip single course).
---

# Curso de video CO.DE Academy

Cómo se produce un curso completo de punta a punta. Es el proceso destilado
de 25 cursos publicados (el 25, Protocolos de Internet, son 24 lecciones y
96 clips). Complementa la skill `manimstudio` (esa explica la app; ésta, el
contenido).

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
  **lección de 4 clips**, un clip = una idea. Tamaños ya usados: 9, 12, 18 y
  24 lecciones. Slugs `<familia>-N-M-<tema>`, nombre `Familia · N.M <título>`
  (el nombre es la clave de emparejamiento de `subir_curso.py`: no lo cambies
  después de subir).
- **Formato antiguo (cursos 1–21)**: un proyecto = un curso de 8 clips. Solo
  para temas que no dan para una familia.
- Fuente del temario: un hilo conceptual propio, un documento maestro, o el
  desmenuzado de `code-academy-platform`. Un curso nuevo **no re-explica** lo
  que ya cubrió otro: declara explícitamente qué capa ocupa y qué asume.

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
- Pies de ≥ 5 s legibles; **el pie cambia ANTES** de la animación que
  ilustra; los rótulos del momento anterior se apagan antes del pie nuevo.
- Un solo cierre a pantalla limpia por lección (clip 4), dos líneas, la
  segunda en cian.
- **Todo número en pantalla se calcula** en la librería con numpy y semilla
  fija. Cero cifras inventadas. Si se dibuja una ventana de una simulación
  más larga, la estadística se mide **sobre la ventana dibujada**. Lo que la
  librería no calcula (datos públicos) se declara como tal en el pie y en
  otro color, para que el cian siga significando "medido aquí".
- Si algo se exagera de escala, se declara en el pie.

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
