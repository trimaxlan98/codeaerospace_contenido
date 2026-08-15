# Marca · Intro y cierre

Proyecto especial de identidad (NO es una lección): dos clips cortos que se
unen en **posproducción** al principio y al final de cada curso nuevo. Los
cursos ya publicados no se tocan (no se re-renderiza nada viejo).

- Proyecto: `studio/content/cursos/marca-intro-y-cierre/`
- Calidad: qh · 2 clips · **sin narración** (la música/voz se decide en post)
- Duración objetivo: **9–12 s por clip**. El aviso de `render_local.py` de
  "clip fuera de 28–45 s" es esperado aquí y se ignora: ese rango es para
  lecciones.
- Regla de empalme: cada clip **arranca y termina en fondo limpio**
  (`#05070a`, sin mobjects visibles) con ≥ 0.5 s de quietud en cada extremo,
  para que el corte en post sea invisible.
- Identidad manual: el style_block del proyecto solo fija el fondo; la
  intro dibuja las esquinas HUD como parte de su coreografía y **ninguno de
  los dos clips lleva `marca_agua()`** (el wordmark grande ES la marca).

## Clip 1 — Intro «Encendido» (~10 s)

Estética de consola de vuelo que despierta:

1. (0–2 s) Fondo limpio; una **línea de escaneo ámbar** barre la pantalla
   y a su paso enciende una **retícula HUD tenue** (gris azulado `#31414f`,
   opacidad muy baja).
2. (2–5 s) Las **escuadras de esquina** (`esquinas_hud`) se dibujan mientras
   el wordmark **CO.DE** grande se ensambla en el centro: «CO» y «DE» en
   tinta, el **punto en ámbar** llega al final como un cursor que parpadea.
3. (5–7.5 s) Debajo aparece **ACADEMY** en muted con tracking amplio
   (letras espaciadas), y arriba una etiqueta HUD pequeña en Space Mono
   (p. ej. `CIENCIA · INGENIERIA · ESPACIO` — solo ASCII).
4. (7.5–10 s) Respiro: leve pulso del punto ámbar; la retícula se apaga; el
   wordmark queda estable ~1 s y **todo funde a fondo limpio**.

## Clip 2 — Cierre «Despedida» (~9 s)

Sobrio y quieto; despide y suelta al espectador:

1. (0–2 s) Fondo limpio; el wordmark **CO.DE ACADEMY** centrado entra con
   un FadeIn suave (leve escala).
2. (2–4.5 s) Un **subrayado con degradado ámbar→naranja**
   (`CODE_ACCENT`→`CODE_ACCENT_2`) se dibuja bajo el wordmark; debajo, un
   pie en muted: «Sigue explorando.»
3. (4.5–7 s) Quietud; el pie desvanece; el punto del wordmark queda
   **parpadeando dos veces como cursor** (la firma del canal).
4. (7–9 s) Fundido a negro total; último frame en fondo limpio.

## Producción

- Patrón de subagentes por clip: **Opus** la intro (coreografía fina),
  **Sonnet** el cierre (mecánica simple); contratos en el scratchpad,
  validación con `render_local.py --clip N --frames 12` iterada por cada
  agente y revisión final de frames por el orquestador.
- En post: `intro.mp4 + clips narrados + cierre.mp4` con el `concat` del
  `mux.sh` (mismo códec/parámetros al salir del mismo pipeline qh).
