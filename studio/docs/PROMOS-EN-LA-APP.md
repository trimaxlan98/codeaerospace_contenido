# Promos de redes dentro de ManimStudio — propuesta de implementación

Escrita el 2026-08-27, después de producir a mano los 10 primeros promos (rama
`exp/promos-redes`, ver `docs/plan_contenido/promos-redes-sociales.md`).

Estado: **P1 hecho** (el lienzo). P2 (sonido) y P3 (verificación), propuestos.

---

## 1. La pregunta

> «¿Agregamos una nueva configuración en donde se editan los videos?»

**Sí, una: el formato del lienzo, al nivel del proyecto, hermana de la calidad.** Es un
`select` con tres valores y una regla de bloqueo. Se implementa en una tarde.

Pero esa configuración es la parte pequeña. Lo que hoy hace que un promo **no** se pueda
producir dentro de la app no es el lienzo — es que la app **no pone sonido en el video** y
**no sabe si el bucle cierra**. Un promo sin audio no es un promo (el encargo fue explícito:
sin subtítulos, solo audio), y la costura del bucle no se juzga a ojo: uno de los diez marcó
0.184 % de píxeles distintos y resultó ser el suelo del códec, no una costura.

Esta propuesta ordena las tres cosas por dependencia: **lienzo → sonido → verificación**.

---

## 2. Qué es un promo en el modelo que ya existe

| Pieza del promo | Equivalente en la app hoy | ¿Sirve? |
|---|---|---|
| `style_block.py` (imports, paleta, piezas) | `projects.style_block` | Sí, tal cual |
| `escena.py` (`class Promo(Scene)`) | `clips.script` + `clips.scene` | Sí, tal cual |
| Un promo = una escena | Proyecto de **un solo clip** | Sí, aunque el índice hoy lo mezcla con los 25 cursos |
| Lienzo 1080×1920 | — | **No.** `QUALITY_SPECS` es 16:9 fijo (`projects.py:21`) |
| `promo.json` → bloque `audio` (cama de sfx) | — | **No.** Nada en la app mezcla audio |
| `promo.json` → bloque `voz` (texto a mano + `t_inicio`) | «Generar narración» | **No.** Ese camino escribe el guion con Gemini a partir del código y apunta a 2.2 palabras/s sobre clips de 28-45 s (`narracion.py:27`). El promo lleva texto escrito a mano, de 11-13 s, y Charon va a 2.3-2.6 **sílabas**/s |
| Costura del bucle, duración, picos, extremos en silencio | — | **No.** `render_promo.py` lo mide fuera de la app |
| Continuidad entre clips, `concat`, zip del curso, regla 28-45 s | Proyectos | **Sobra** para un promo |

Lo bueno: **el runner no necesita saber nada de formatos**. El lienzo lo fija la escena
(`promo.formato()` escribe `config.pixel_width/height` y `frame_height` antes que
`frame_width`), y eso ocurre *después* de que manim parsee el `-qh` de la línea de comandos.
El `docker compose run` de `manim_runner.py:115` ya renderiza un promo vertical sin tocar una
línea — lo único que hoy no puede es *elegir* el formato, porque no le llega el dato.

---

## 3. Propuesta: el promo es un **tipo de proyecto**, no una sección nueva

`projects.tipo = 'curso' | 'promo'`. Un promo reusa entero: la cola de un job a la vez, el
SSE, la Biblioteca, el catálogo, la cuota de disco, el asistente, el editor del Estudio, la
plantilla de estilo, el hash de `stale`. Lo que cambia es lo que la UI **muestra** y lo que
el backend **hace después de renderizar**.

**Alternativa descartada — pestaña «Promos» con entidad propia.** Duplicaría cola, editor,
biblioteca y catálogo para ganar solo una portada distinta. El rediseño del sprint 7 fue en
la dirección contraria (fusionar secciones, no abrirlas); una entidad paralela reabre la
costura que se acaba de cerrar.

---

## 4. Sprint P1 — El lienzo · **HECHO** (2026-08-27)

**Entregable:** desde la app se crea un promo, se elige «vertical», se renderiza y sale un
mp4 de 1080×1920 que la interfaz muestra vertical.

**Verificado de punta a punta**, componiendo el script como lo compone el backend y
renderizando con las mismas variables de entorno y el mismo flag `-q` que manda el runner:

| Formato · calidad | La app anuncia | El archivo es |
|---|---|---|
| vertical · qh | 1080×1920 @ 60 | **1080×1920 @ 60**, 10.70 s |
| vertical · ql | 480×852 @ 15 | **480×852 @ 15** |
| horizontal · ql | 854×480 @ 15 | **854×480 @ 15** |
| cuadrado · ql | 480×480 @ 15 | **480×480 @ 15** |

El clip de arranque de la plantilla además **cierra el bucle**: 0.0007 % de subpíxeles
distintos entre el primer frame y el último, al nivel del suelo del códec.

**Una trampa que apareció al hacerlo.** `854x480` (el «16:9» de manim) no sale de ninguna
proporción exacta: 480 × 16/9 = 853.33, y con lados pares eso es 852. Como la app anuncia la
resolución *antes* de renderizar, anunciaba 854 y habría producido 852. Se resolvió dándole a
`promo.formato()` un parámetro `largo_px` (y su `PROMO_LARGO`): quien encarga el render fija
los **dos** lados, así que la cifra de la interfaz y la del archivo salen del mismo número.
La resolución medida con ffprobe queda como comprobación, no como parche.

**Lo que se hizo:**

- **DB** — migraciones aditivas por tabla (`db.py`): `projects.tipo`, `projects.formato`,
  `jobs.formato` (el **pedido**) y `jobs.resolution` (la **medida**). Una base existente pasa
  por el mismo camino que una nueva.
- **`projects.py`** — `specs(quality, formato)`: la calidad fija el lado corto y los fps, el
  formato la proporción. En horizontal devuelve la tabla de manim tal cual, porque es la que
  produce el flag `-q`. Se publica en `GET /api/projects/{pid}` como `specs`.
- **Runner** — `PROMO_FORMATO`, `PROMO_CALIDAD`, `PROMO_CORTO`, `PROMO_LARGO` y `PROMO_FPS`
  al `docker compose run`, validados contra un conjunto y rangos cerrados igual que la
  calidad. El runner no interpreta el lienzo: lo aplica la escena. Un curso 16:9 ignora esas
  variables y renderiza como siempre.
- **Plantilla «Promo de redes»** (`plantillas.js`) — estilo con `FMT = _promo.formato()`,
  fondo seguro, la marca donde la app no la tapa, y un clip de arranque que renderiza y
  cierra el bucle. Un promo nuevo sale funcionando sin escribir una línea.
- **Resolución medida** — el comando de miniatura del runner corre además `ffprobe` y guarda
  `WxH`. La interfaz muestra lo que el archivo *es*, no lo que se pidió.
- **UI** — `formatos.js` centraliza la proporción (medida si hay video, pedida si no) y los
  tres `aspect-video` escritos a mano pasan a `style={{ aspectRatio }}`; el reproductor se
  acota por alto; el select de formato vive en la cabecera del proyecto, deshabilitado en
  cuanto hay un render vigente (el backend responde 409 igual).
- **Rango de duración por tipo** — 28-45 s en un curso, 8-15 s en un promo. Con la vara del
  curso, los diez promos salían marcados en ámbar por «cortos».
- **11 pruebas nuevas** (`tests/test_formato.py`), 162 en total en verde.

---

## 5. Sprint P2 — El sonido

**Entregable:** el mp4 que sirve `/api/jobs/{id}/video` (`main.py:282`) ya viene con cama de
sonido y, si hay voz, con voz. Hoy sale mudo y el `mux.sh` vive fuera de la app.

- **Manifiesto por clip**: `clips.audio_json TEXT` (aditivo) con los bloques `audio` y `voz`
  de `promo.json` tal cual. La UI lo edita con un formulario, no con un editor de JSON:
  - *Cama*: filas `(sonido, t, dB)`. El catálogo de sonidos es cerrado y ya existe —
    los 19 nombres de `PALETA` en `sfx.py:225` (`barrido`, `aire`, `blip_grave`, `pulso`,
    `nebulosa`, `sting`…). Un `select`, no texto libre.
  - *Voz*: filas `(t_inicio, texto)`. Con dos avisos calculados, no decorativos: **cuántas
    sílabas caben** a 2.3-2.6 síl/s desde ese `t_inicio` hasta el siguiente, y si la voz
    termina **a menos de 0.6 s del final** (el bucle chasquea). Los dos son errores que ya se
    cometieron a mano.
- **Runner, comando nuevo `postproceso`**: corre `sfx.py promo` dentro de la imagen
  `manim-render`, con el directorio del job montado rw y la ruta del script fija dentro del
  repo montado ro. Es el mismo patrón, casi línea por línea, que `handle_thumbnail`
  (`manim_runner.py:158`): superficie mínima, sin rutas arbitrarias.
- **Voz**: reusa `narracion.sintetizar()` (`narracion.py:358`) con las secciones escritas a
  mano — **sin** pasar por el generador de guion de Gemini. Mismo feature-flag que hoy (sin
  `gcp-key.json`, no hay voz), misma service account.
- **Dos archivos por render**: se conserva el mudo y se escribe el sonorizado al lado.
  Cambiar el manifiesto **no** obliga a re-renderizar el video: re-mezcla. Eso es importante
  — el render en `qh` vertical es la parte cara, la mezcla cuesta segundos.
- **Botón**: «Mezclar audio» junto a «Renderizar» en la tarjeta del promo, y se dispara solo
  al terminar un render si el clip tiene manifiesto.

**Criterio de aceptación:** editar un evento de sonido en la UI, pulsar «Mezclar», y que el
video que se descarga suene con ese cambio sin haber vuelto a renderizar.

---

## 6. Sprint P3 — La verificación

**Entregable:** la app dice, con números, si el promo está listo para publicar.

- `medir_bucle` sale de `render_promo.py` a un módulo compartido, y lo ejecuta el mismo
  comando `postproceso` (necesita ffmpeg → contenedor). Se guarda en `jobs.verify_json`.
- **La sutileza que hay que conservar**: la costura se juzga **sobre el suelo del códec**.
  Comparar el primer frame con el último a secas acusa de sucio a un bucle perfecto: h264
  sobre fondos planos oscuros da hasta 0.18 % de subpíxeles distintos entre dos frames que en
  la escena son idénticos. La herramienta mide ese suelo comparando dos frames vecinos y lo
  resta. Sin eso, el semáforo miente.
- **Tarjeta de verificación** en la UI, cuatro líneas: bucle (`% sobre el suelo`), duración,
  pico de audio en dBFS, extremos en silencio. Verde/rojo con el número al lado, nunca solo
  el color.
- **Tira de frames** equiespaciados (`render_promo.py` ya los extrae) bajo el reproductor:
  la costumbre de revisar frame a frame es la que cazó el elemento fuera de lienzo, la nariz
  del cohete sobre el rótulo y el «19 2» que se leía «192». Que la UI la ofrezca sola.
- El primer frame y el último, uno al lado del otro, a tamaño real.

**Criterio de aceptación:** un promo con la costura rota se ve rojo en la app antes de que
nadie abra el video.

---

## 7. Índice y galería

- Filtro «Promos» en Proyectos, reusando el agrupador por familia que ya existe
  (`Projects.jsx:130`): los promos se agrupan **por curso**, no sueltos.
- La tarjeta del promo muestra miniatura vertical, duración y el semáforo del bucle en vez de
  la barra de progreso `rendered/stale` (que para un clip único no dice nada).
- Descarga directa del mp4 sonorizado; sin zip ni `concat` (no aplican).

---

## 8. Importar los 10 promos que ya existen

`studio/tools/subir_promo.py`, hermano de `subir_curso.py`: lee
`studio/content/promos/<slug>/{promo.json, style_block.py, escena.py}` y crea el proyecto
(`tipo='promo'`, `formato='vertical'`, `quality='qh'`), su clip y su `audio_json`. El nombre
del promo es la clave de emparejamiento, igual que en los cursos, para que re-subir actualice
en vez de duplicar. Se corre una vez y los diez aparecen en la app con su manifiesto.

---

## 9. Coste, riesgos y lo que no se hace

- **Render**: 1080×1920 son 2.07 Mpx por frame, los mismos que 1920×1080. Un promo de 12 s le
  cuesta al VPS **menos** que un clip de curso de 35 s a la misma calidad. El formato no
  añade coste; la duración lo quita.
- **Riesgo real**: `promo.py` vive en `manim_extensions/` y lo importa el `style_block`. Si
  la plantilla y la librería se desincronizan, el fallo aparece como un error de import en el
  log del render. Mitigación: la plantilla no inventa API, usa `formato()` y `Formato` tal
  como están, y los tests de `test_projects_store.py` cubren `specs(quality, formato)`.
- **No se toca** la narración de cursos: el camino Gemini→TTS de 28-45 s queda como está. El
  promo entra por una puerta distinta al mismo `sintetizar()`.
- **Queda fuera** de esta propuesta: publicar a Instagram desde la app (subida, credenciales,
  calendario). Eso es otro proyecto y otra superficie de riesgo.
- **Queda pendiente del lote anterior**, independiente de la app: mirar los diez en un
  teléfono real y tirar las versiones 16:9 en `qh` (el camino está validado en `ql` 960×540 y
  cada escena tiene su rama horizontal escrita, pero cada composición pide un ajuste).

---

## 10. Orden sugerido

| Sprint | Qué habilita | Tamaño |
|---|---|---|
| ~~**P1 · Lienzo**~~ | ~~Autoría de promos en la app, sin sonido~~ · **hecho** | 1 sesión |
| **P2 · Sonido** | El promo se termina dentro de la app | 2 sesiones |
| **P3 · Verificación** | Publicar sin abrir la terminal | 1 sesión |
| **Importador** | Los 10 promos existentes entran al catálogo | media sesión |

P1 tiene valor por sí solo y no rompe nada: hasta que llegue P2 se descarga el mp4 mudo y se
sonoriza con las herramientas locales, exactamente como ahora.
