# ManimStudio v3 — el estudio de investigación

Encargo del **2026-09-03**: revisión exhaustiva de áreas de oportunidad y un plan
para llevar ManimStudio a **estándar de investigación y rigurosidad**: mejores
librerías, mejor UX/UI, más tipos de proyecto (verticales y horizontales), más
sonido y música, voz sin depender de la facturación de Gemini (con subida de
narraciones propias), y —la deficiencia central— **la misma capacidad desde la
plataforma que desde Claude Code en la terminal**. Todo hasta producción
(coderesearch.space) y GitHub, documentado. Corrida autónoma.

Este archivo es el **tablero vivo**. `ESTUDIO-V2.md` (2026-08-28) es la etapa
anterior; `UX-REDISENO.md` y `DESIGN-SYSTEM.md` siguen mandando en lo visual.

---

## 1. Para quién es esto (auditoría del nivel de arriba, `../codeaerospace.com`)

Co.De Aerospace es una startup mexicana de ingeniería aeroespacial con **fondeo
cruzado**: el trabajo comercial (Strategy) financia la investigación (NGSO,
espectro, WRC-2027). Tres divisiones —Aero, Strategy, Academy— y tres cuentas de
Instagram (**@co.de_aero**, **@co.de_strategy**, **@co.de_academy**). No hay
YouTube declarado en ningún repo: el canal de vídeo largo es una intención,
no un activo todavía.

Lo que el estudio tiene que servir, con demanda ya escrita en los repos hermanos:

| Público | Producto | Dónde está la demanda |
|---|---|---|
| Academy (alumnos) | clips de curso horizontal 16:9 y películas montadas | 33 cursos ya producidos aquí; `code-academy-platform/docs/cursos-*.md` |
| Instagram (tres cuentas) | piezas verticales 9:16 de 30–45 s que funcionan solas | cursos 26–33; `promos-redes-sociales` |
| Tesis doctoral 6G/NTN (IPN) | figuras **citables con proveniencia** (commit + semilla + fecha), Gantt de disponibilidad, series RTT, CDF de recuperación, curva de margen adaptativo, geometría de pase LEO-600 (AOS/TCA/LOS), quórum PBFT | `tesis-6g-command-center/docs/09_ROADMAP_VALIDACION_TESIS.md` §Fase 5, `pada-ntn-testbed/tools/plots.py` |
| Paper IEEE Network (deadline 2026-09-30) | «captura + video demo», DOI Zenodo | `tesis-6g-command-center/docs/SPRINTS.md:139` |
| Defensas y conferencias | animaciones por pasos en `.pptx` | ya en la app (`PRESENTACIONES.md`) |
| Divulgación general | vídeos con voz, música y marca | todo lo anterior |

La matemática de la casa, que las librerías tienen que hablar con rigor:
mecánica orbital (Kepler, SGP4, J2), presupuesto de enlace (`FSPL = 92.45 +
20log d + 20log f`, `C/N0 = EIRP + G/T − FSPL − L + 228.6`, `Eb/N0`), control
ATP (Bode, Nyquist, Lyapunov, LQR, H∞), DSP (FFT, ventanas, FIR/IIR) y
aprendizaje por refuerzo multiagente (QMIX, margen adaptativo `MA`, gates
G0–G4 con IC95 %).

## 2. De dónde se parte (auditoría del 2026-09-03)

Cuatro informes, resumidos en lo que duele:

**La app produce piezas y las une, pero un curso NUEVO nace en la terminal.**
No hay import de curso-como-archivos (`subir_curso.py`), ni render en lote a
una calidad elegida (`render_local.py --todos --calidad qh`), ni hoja de
contactos de fotogramas, ni pipeline vertical de N piezas
(`render_vertical` / `verifica_vertical` / `unir_vertical` /
`sellar_duraciones`), ni sondas de invariantes (`sonda_*.py`), ni costuras
entre piezas, ni pico dBFS por pieza, ni manera de ejecutar Python de
validación en el sandbox. Diez brechas, ordenadas, en §5 del informe de
paridad (reproducido abajo en R3/R4).

**La voz depende de una sola clase con dos métodos.** `VertexNarrador.guion()`
y `.tts()` (`narracion.py:129-188`); todo lo demás —recorte de silencio,
alineado por secciones, ajuste al límite, WAV— es aritmética de bytes agnóstica
del motor. GCP está en **mora** (403 *dunning*, curso 31): hoy no hay voz. No
existe subida de narración propia. Y el guion lo escribe Gemini, así que sin
Gemini tampoco hay guion editable.

**No existe música.** `unir_vertical.py --mudo` existe *precisamente* porque
el dueño se pone la música fuera. La paleta de SFX tiene 18 efectos; los
temas más «musicales» (`pad`, `nebulosa`) son ambientes, no armonía.

**UX**: un editor, un contexto de clip global; el `style_block` compartido se
edita en un `<textarea>` de 14 filas; sin previsualización ni fotogramas; lote
sin progreso agregado; sin duplicar proyecto/clip; sin salida estática (PNG/
SVG) para una figura de tesis; sin ayuda matemática en el editor; sin historial.
`Projects.jsx` tiene 1 585 líneas y 13 subcomponentes inline.

**Lo que ya funciona y NO se toca**: sandbox (runner root + contenedor sin red
y read-only), cola de un render, película con transiciones, presentaciones
`.pptx`, banco de SFX audible, verificación de promos, paleta de comandos,
cuatro temas AA, 275 tests verdes.

## 3. Alternativas de voz, verificadas hoy

| Proveedor | Coste | Red | Dónde corre | Medido el 2026-09-03 |
|---|---|---|---|---|
| **edge-tts** 7.2.8 | gratis | sí, desde el backend | backend | **45 voces en español** (es-MX Jorge/Dalia, es-ES Álvaro/Elvira…), 6.4 s de audio en ~2 s |
| **Piper** 1.7.0 | gratis, offline | no | backend (subproceso) | voz `es_MX-claude-high` (63 MB), **0.56 s por 5.2 s de audio** a 22 050 Hz |
| Vertex / Gemini TTS | de pago (en mora) | sí | backend | el de siempre; queda como proveedor |
| **Archivo** (narración propia) | — | no | — | el dueño graba y sube; la app recorta, alinea y muxea |

El guion, sin Gemini, lo escribe el dueño (o Claude desde aquí) en un editor
de secciones con `t_inicio`; el proveedor de voz solo lo habla.

## 4. Principios (lo que hace «de investigación» a un estudio)

1. **Toda cifra en pantalla se calcula** (regla vigente) y **toda figura sale
   con proveniencia**: commit, semilla, fecha y versión de la librería,
   estampados en el margen o en los metadatos.
2. **Lo que se mide en la terminal se mide en la app**: costuras, picos,
   duraciones, fotogramas, invariantes. Medir lo que se pinta, no lo que se
   declara.
3. **Un proyecto es un directorio**: importable y exportable como archivos
   (`curso.json` + `style_block.py` + `clips/`), para que git y la app sean el
   mismo estado.
4. **Los datos entran, no se transcriben**: un CSV/JSON adjunto al proyecto
   que el clip lee en el contenedor. Las figuras de la tesis se dibujan desde
   el JSONL del banco de pruebas, no desde números copiados.
5. **Nada nuevo corre fuera del sandbox**: cualquier capacidad que necesite
   ffmpeg/numpy entra como comando del runner, como `ensamblar`.

## 5. Tablero

| # | Sprint | Qué cierra | Estado |
|---|---|---|---|
| R0 | Plan | este documento, rama `estudio/v3-investigacion` | **hecho** |
| R1 | Voz sin GCP | proveedores edge/piper/vertex/archivo, guion editable, **subida de narración propia**, normalización en el contenedor | **hecho** |
| R2 | Música | `musica.py` procedural (temas, bpm, tonalidad), banco audible, `audio.musica` en el manifiesto, cama bajo la película con *ducking* | en curso (agente) |
| R3 | Paridad con la terminal | import/export de curso como archivos, render en lote con calidad, hoja de contactos + fotograma PNG, costuras y picos en la película, **Laboratorio** (ejecutar Python en el sandbox: sondas) | **R3b hecho** (fotogramas + Laboratorio); import/export, lote y costuras pendientes |
| R4 | Rigor de investigación | `figura.py` (estilo paper, proveniencia, PNG/SVG), datos adjuntos por proyecto, `ntn.py` para la tesis (pase LEO, Doppler, handover, PBFT, MA) | en curso (agente, librerías) |
| R5 | UX | Estudio con fotogramas, `style_block` en CodeMirror, duplicar proyecto/clip, panel de audio unificado (voz + música + SFX), pestaña Laboratorio, `Projects.jsx` descompuesto | pendiente |
| R6 | Producción y cierre | VPS, nginx (`client_max_body_size`), unit (`MemoryMax`), README, skills, catálogo, memoria | pendiente |

Cada sprint termina con `pytest -q` verde, `vite build`, commit atómico y
despliegue verificado desde fuera.

---

## R1 — Voz sin GCP

### Diseño

`app/tts.py` — un `Protocol Narrador` con `tts(texto, voz) -> bytes` (PCM
s16le mono a `TTS_RATE` = 24 000 Hz) y `guion(system, user) -> dict | None`.
Implementaciones:

- `VertexNarrador` (la de siempre, movida sin cambios).
- `EdgeNarrador`: `edge_tts.Communicate(texto, voz).stream()` → MP3 → PCM. El
  backend no tiene ffmpeg, así que la decodificación se hace con
  `edge-tts` pidiendo `audio-24khz-48kbitrate-mono-mp3` y decodificando con
  `minimp3`/`pyav`… **no**: la decisión es pedirle a edge-tts el formato y
  **decodificar en el contenedor** sería lento por llamada. Se usa el
  decodificador puro Python `pymp3`? Demasiado frágil. **Decisión**: el
  backend guarda el MP3 y el runner lo convierte con ffmpeg en el comando
  `normalizar_voz` (uno por clip, ~1 s). El alineado por secciones se hace
  después sobre el WAV, en el backend (aritmética de bytes existente).
- `PiperNarrador`: subproceso `piper` del venv, WAV a 22 050 Hz →
  remuestreo lineal a 24 000 en Python puro (o por el mismo `normalizar_voz`).
- `ArchivoNarrador`: no sintetiza; la narración la sube el dueño.

Selector `MS_TTS_PROVIDER` (defecto: `edge` si está instalado, si no
`vertex`), `MS_TTS_VOICE` por proveedor, `MS_PIPER_VOICES_DIR`.

### API nueva

- `GET /api/narracion/voces` — proveedores disponibles y sus voces.
- `PUT /api/projects/{pid}/narracion/{cid}/guion` — secciones
  `[{t_inicio, t_fin, momento, texto}]` escritas a mano (o por Claude).
- `POST /api/projects/{pid}/narracion` acepta `{provider, voz, solo_audio}`:
  con guion guardado y `solo_audio` no llama a ningún LLM.
- `POST /api/projects/{pid}/narracion/{cid}/audio` (multipart, wav/mp3/m4a,
  ≤ 25 MB): guarda la subida, el runner la normaliza (mono, 24 kHz, recorte
  de silencio, pico medido) y la deja en la ruta canónica
  `guiones/<slug>/NN-<slug>.wav` con `origen: "subido"` en `estado.json`.
  Con eso `pelicula.plan` la recoge sin cambios.
- nginx: `client_max_body_size 25M` solo en `/api/projects/`.

### Runner

Comando `normalizar_voz {job_dir, entrada}` calcado de `postproceso`:
`ffmpeg -i entrada -ac 1 -ar 24000 -af silenceremove=... -f wav` +
`volumedetect`, devuelve `{duracion_s, pico_db}`.

## R2 — Música (agente Opus, `studio/tools/musica.py`)

Síntesis con numpy, semillas fijas, sin assets, en el contenedor. `TEMAS`
espejo de `PALETA`: raíz, progresión de grados, bpm, carácter. Tres capas:
drone (pad aditivo por nota del acorde), arpegio (Karplus-Strong en
subdivisiones del bpm), sub-bajo senoidal; todo bajo ~950 Hz («espacial pero
tranquilo», criterio verificado en la marca). Manifiesto: `audio.musica =
{tema, db, bpm}` validado contra una tupla cerrada. Se suma dentro de
`sfx.promo()` antes del `_norm` a `pico_db`; en la película, `ensamblar.py`
acepta `musica` global con *sidechain* simple (−9 dB bajo la voz).

## R3 — Paridad con la terminal

| Brecha | Entra como |
|---|---|
| curso como archivos | `POST /api/projects/importar` (zip o `{slug}` del repo) y `GET /{pid}/fuentes.zip` |
| lote con calidad | `POST /{pid}/render-lote {clips, calidad, force}` + progreso agregado en `GET /{pid}` |
| hoja de contactos ✅ | comando `frames` del runner → `POST /api/jobs/{id}/frames` + `GET …/frames/NN.png` (N PNG + último real) |
| fotograma / figura ✅ | comando `fotograma` → `POST /api/jobs/{id}/fotograma {t, ancho}` a la resolución pedida |
| costuras y picos | `pelicula/verificar` mide además la unión pieza a pieza (PIL) y el pico por pieza |
| sondas / Laboratorio ✅ | comando `ejecutar` del runner: script Python en el sandbox, stdout + archivos producidos → `POST /api/laboratorio` y vista `#/laboratorio` |

## R4 — Rigor de investigación (agente Opus, librerías)

- `manim_extensions/figura.py`: figura de paper (fondo blanco o marca),
  anchos de columna IEEE (3.5 in / 7.16 in), tipografía serif para eje,
  **sello de proveniencia** (`figura.sello(commit, semilla)`), exportación a
  PNG/SVG con `-s`.
- `manim_extensions/ntn.py`: geometría de pase LEO (AOS/TCA/LOS, elevación,
  distancia oblicua), Doppler y retardo, cascada de handover, quórum PBFT
  (`n ≥ 3f+1`), margen adaptativo y gates con IC95 %. Determinista, con sonda.
- Datos adjuntos: `POST /{pid}/datos` (CSV/JSON/JSONL ≤ 10 MB) montados en
  el directorio del job como `datos/`; `figura.leer_csv()` los lee.

## R5 — UX

Panel de **Audio** por clip que unifica voz (proveedor, voz, guion editable,
subir grabación, escuchar), música (tema, nivel, escuchar) y SFX (banco).
Estudio: hoja de contactos bajo el vídeo, «Fotograma como PNG». Proyecto:
`style_block` en CodeMirror, duplicar proyecto y clip, importar/exportar
fuentes, progreso del lote. Pestaña **Laboratorio**. `Projects.jsx` partido
en `components/proyectos/*`.

---

## R3b — Fotogramas y Laboratorio (2026-09-03)

Lo que cierra: **ver lo que se pinta y ejecutar lo que se mide**. Hasta hoy el
único resultado de un render en la app era el mp4, y el único Python que la
consola sabía ejecutar era una escena de manim.

### Diseño

**Un solo contenedor por hoja, no uno por fotograma.** Arrancar
`docker compose run` cuesta ~1,5 s; doce arranques serían veinte segundos para
doce PNG de un cuarto de segundo. Por eso hay una herramienta nueva,
`studio/tools/hoja_contactos.py`, con el mismo patrón que `promo_verifica.py`:
ruta fija del script, todo el trabajo en un contenedor, informe JSON en la
última línea de stdout. Dos modos:

- `tira VIDEO DESTINO --n N --ancho 480` — N fotogramas en `t = dur·(i+½)/N`
  (el mismo reparto que `render_local.py`, que evita los fundidos de los
  extremos) más `final.png`, el último fotograma **real**. Deja `indice.json`
  al lado con el instante y el tamaño medido de cada uno.
- `figura VIDEO SALIDA --t T --ancho W` — un PNG a la resolución pedida.

**Idempotencia por el índice, no por una tabla.** El mp4 de un job es
inmutable: pedir la misma hoja dos veces no puede costar dos contenedores. El
backend lee `frames/indice.json`, comprueba que el `n` coincide y que **todos**
sus PNG siguen en disco, y devuelve `recalculada: false` sin tocar el runner.
Medido: 2,2 s la primera vez, 0,00 s la segunda.

**El Laboratorio no entra en la cola de renders.** `JobManager._run_job` está
construido alrededor de `runner.render()` —transmite el log de manim línea a
línea por SSE, busca un mp4 al terminar, saca miniatura y resolución, y guarda
en columnas (`scene`, `quality`, `video_path`…) que un script no tiene—; meterlo
ahí obligaría a partir el worker en dos caminos y a inventar valores para media
docena de columnas. Se hace lo que ya hacen `mezclar_audio` y `verificar_promo`,
que tampoco pasan por la cola: **son segundos, no minutos**. Pero **sólo una
ejecución a la vez**, con el turno apartado de forma síncrona (`crear()` fija
`_corriendo` sin ningún `await` entre la comprobación y la reserva; hacerlo
dentro de la corrutina deja una ventana por la que se cuelan dos). Así lo peor
que puede coincidir en 2 vCPU es un render largo y una sonda corta, y el tope
de 1.5 vCPU de compose sigue mandando.

**El registro del Laboratorio es el disco.** Cada ejecución es
`render_jobs/lab/<id>/` con `script.py`, `meta.json` y lo que el script deje.
Sin migración de esquema y sin dos fuentes de verdad que sincronizar; borrar una
ejecución es borrar su directorio.

**La ejecución va en segundo plano y la vista pregunta.** El tope es de 900 s y
nginx corta una petición mucho antes: `POST` devuelve 202 con el id y
`Laboratorio.jsx` consulta cada 1,2 s mientras dura. No se añade un evento SSE
por una tarea que dura segundos.

### Superficie nueva

| Runner | Backend | Frontend |
|---|---|---|
| `frames {job_id, n}` | `POST /api/jobs/{id}/frames` · `GET …/frames/{NN.png\|final.png}` | «Hoja de contactos» bajo el vídeo (Estudio y modal de Renders) |
| `fotograma {job_id, t, ancho, formato}` | `POST /api/jobs/{id}/fotograma` · `GET …/figuras/{archivo}` | «Fotograma → PNG» con el `currentTime` del `<video>` y 1920/2560/3840 |
| `ejecutar {lab_id, sonda?, timeout}` | `POST /api/laboratorio` · `GET /api/laboratorio[/{id}]` · `GET …/{id}/archivos/{n}` · `DELETE` · `GET /api/laboratorio/sondas` · `POST /api/laboratorio/sondas/{nombre}` | vista `#/laboratorio` (`g l`): editor CodeMirror, salida, galería de archivos, sondas del repo e historial |

### Medido (runner y backend reales, Docker de verdad, 2026-09-03)

| Qué | Resultado |
|---|---|
| hoja de 6 fotogramas de un clip de 4,0 s (`ql`) | 2,2 s · 7 PNG de 480×270 · segunda petición 0,00 s |
| figura a 1920 px | 1080 de alto, 72 KB, 0,8 s |
| figura a 3840 px | **2158** de alto (no 2160), 229 KB, 1,7 s |
| `sonda_sistemas.py` en el sandbox | **73 invariantes ok, 0 fallos** en 2,6 s (3,1 s por HTTP) |
| script con numpy + PIL + `import code_brand` | 2,4 s, `figura.png` de 480×240 devuelta y pintada en la vista |
| timeout (script que duerme 600 s, `timeout: 30`) | `code 124`, `timed_out: true` a los 60,1 s, **sin contenedor huérfano** |
| garantías del sandbox, medidas DESDE DENTRO | red bloqueada · repo read-only · otro job no escribible · sólo el directorio propio escribible · uid:gid 1000:1000 |

### Trampas

- **Un `-ss` al filo de la duración sale con éxito SIN escribir nada.** Y el
  instante de la figura lo manda el `<video>` del navegador, que al terminar
  marca `currentTime == duration`: el caso más probable era justo el roto.
  Cualquier `t` dentro de los últimos 0,4 s se atiende con `-sseof -0.4
  -update 1`, que es como sacan el último fotograma `promo_verifica.py` y
  `verifica_vertical.py`. Verificado pidiendo `t = 4.0` de un vídeo de 4,0 s.
- **`scale=3840:-2` sobre un 854×480 da 2158, no 2160.** La resolución que
  enseña la interfaz es la **medida sobre el PNG escrito** (`ffprobe`), no la
  que se pidió: una figura de tesis que dice 2160 y mide 2158 es una cifra
  falsa, del mismo tipo que las que caza la regla de la casa.
- **`docker compose run` escribe su progreso en stderr.** En los demás comandos
  da igual (se lee el JSON de stdout); en el Laboratorio **no**, porque ese
  stderr se le enseña al usuario tal cual y las dos líneas de «Container …
  Creating/Created» dejaban un traceback de Python enterrado bajo ruido del
  orquestador. El runner las filtra con un regex anclado.
- **`meta.json` no cae por la lista de extensiones.** La ruta de archivos
  producidos filtra por extensión (`.png`, `.wav`, `.json`…), y `.json` está
  permitido: sin una lista de nombres reservados, `GET …/archivos/meta.json`
  servía el registro interno de la ejecución —con su stdout entero— como si
  fuera un resultado del script. Lo cazó el test antes que nadie.
- **`exit 1` no es una avería.** Una sonda con invariantes rotos sale con 1 **a
  propósito**: pintarlo de rojo como fallo del sistema sería perder justo la
  señal que se buscaba. Estado propio (`salida`, ámbar) distinto de `timeout` y
  de `error` (runner caído).
- **Las sondas se buscan en `<workspace>/studio/tools`, no junto al código.**
  Es la ruta que el runner ejecuta dentro del contenedor
  (`/workspace/studio/tools/sonda_<x>.py`): si el backend mirara a otro sitio,
  la app ofrecería una sonda que el runner no encuentra. En los tests el
  workspace es un `tmp_path`, así que el fixture enlaza las herramientas reales
  —sondas y no-sondas, para que el filtro tenga algo que descartar.
- **El laboratorio cuenta contra la cuota de disco de renders**, porque vive
  bajo `render_jobs/`. Es deliberado: son bytes en el mismo volumen, y
  `storage_usage()` ya los ve sin cambiar nada.
- **Con `render_jobs` enlazado a otro disco, el cwd del laboratorio es la ruta
  REAL, no `/workspace/…`.** En esta máquina `render_jobs` es un enlace al
  segundo disco (`ARTEFACTOS-LOCALES.md`) y dentro del contenedor ese enlace
  cuelga; Docker resuelve el destino del montaje a través de él y lo crea en
  la ruta del host. Los tres comandos **funcionan igual** (verificado con el
  enlace puesto: hoja de 4 fotogramas, figura a 1920 px y un script que
  escribe un `.txt`), pero un `os.getcwd()` o un traceback imprimen
  `/home/…/data/…/render_jobs/lab/<id>` en un clon local y
  `/workspace/render_jobs/lab/<id>` en el VPS, donde el directorio es real.

## Cosecha (se rellena al cerrar cada sprint)

### R1 — Voz sin GCP (2026-09-03)

Lo que quedó: `app/tts.py` (catálogo, fábrica, cuatro proveedores),
`narracion.py` (guion a mano, `exacto`, subida), `narracion_api.py`
(`/api/narracion/proveedores`, `PUT …/guion`, `PUT …/audio`), runner
`normalizar_voz`, `components/GuionDialog.jsx` y `VozSelector.jsx`. Medido:

| Proveedor | Voz | 2 secciones (t=0.5 y t=8.0), 25 palabras | Pico |
|---|---|---|---|
| edge | es-MX-JorgeNeural | 12.79 s de audio en 3.9 s | −2.8 dB |
| piper | es_MX-claude-high | 13.20 s de audio en 3.6 s | 0.0 dB → atenuado a −3 dB |

Trampas:

- **El tope de hueco de 2.5 s es veneno para un guion escrito a mano.** Existía
  para los tiempos *estimados* por Gemini; con tiempos deliberados (verticales
  con huecos de 4–7 s) desplazaba la segunda frase de t=4.5 a t=3.0. El test lo
  cazó (3.5 s donde debían ser 5.0). Ahora `sintetizar(..., exacto=True)` para
  guiones a mano, que es lo que `alinear_voz.py` hacía a mano.
- **Cambiar la voz por defecto habría dejado 397 narraciones «desactualizadas»**:
  el hash de frescura incluía `cfg.tts_voice`. Ahora usa la voz con que se narró
  cada clip; cambiar de voz es un `force` deliberado.
- **El backend no tiene ffmpeg ni numpy**: edge-tts devuelve MP3 y Piper WAV a
  22 050 Hz. `miniaudio` (wheel manylinux, sin dependencias) decodifica y
  remuestrea a 24 kHz en el backend; solo m4a/aac/webm van al contenedor.
- **Piper dentro del backend se cuenta en el cgroup**: `MemoryMax` de 512M a
  1024M. Corre como subproceso para que no quede residente.
- **FastAPI `UploadFile` exige `python-multipart`**, que no está en el venv. La
  subida es el cuerpo crudo con `?nombre=`; no hay dependencia nueva.

