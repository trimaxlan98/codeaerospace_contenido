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
| R3 | Paridad con la terminal | import/export de curso como archivos, render en lote con calidad, hoja de contactos + fotograma PNG, costuras y picos en la película, **Laboratorio** (ejecutar Python en el sandbox: sondas) | **R3a hecho** (import/export, lote, duplicar); R3b pendiente |
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

| Brecha | Entra como | Estado |
|---|---|---|
| curso como archivos | `POST /api/projects/importar` (zip o `{slug}` del repo) y `GET /{pid}/fuentes.zip` | **R3a** |
| lote con calidad | `POST /{pid}/render-lote {clips, calidad, force}` + progreso en `GET /{pid}/lote` | **R3a** |
| duplicar proyecto/clip | `POST /{pid}/duplicar`, `POST /{pid}/clips/{cid}/duplicar` (venía de R5) | **R3a** |
| hoja de contactos | comando `frames` del runner → `GET /api/jobs/{id}/frames` (N PNG + último) | R3b |
| fotograma / figura | `POST /api/jobs/{id}/fotograma {t, formato: png／svg}` a resolución del job | R3b |
| costuras y picos | `pelicula/verificar` mide además la unión pieza a pieza (PIL) y el pico por pieza | R3b |
| sondas / Laboratorio | comando `ejecutar` del runner: script Python + argumentos en el sandbox, stdout + archivos producidos → `POST /api/laboratorio` | R3b |

### R3a — un proyecto es un directorio (diseño)

**El módulo compartido.** `subir_curso.py` tenía dentro toda la lectura de un
curso-como-archivos. Se mueve entera a **`app/importar.py`** (puro: sin
FastAPI, sin `sys.exit`) y los dos CLI pasan a ser envoltorios que traducen
`ErrorImportacion` a `sys.exit`. La terminal y la app ejecutan literalmente el
mismo código, que es la única forma de que no diverjan. `subir_promo.py`
también: su `cargar_promo` aplana el manifiesto genérico a la forma
`clip` + `audio` que espera su `sincronizar` (que sigue siendo suyo, porque
sus mensajes de reporte son de promo).

Tres cargadores, un solo manifiesto en memoria:

| Función | Lee | Particularidad |
|---|---|---|
| `cargar_curso` | `curso.json` con `clips` | el de siempre, más `formato`, `tipo` y `estilo` |
| `cargar_vertical` | `curso.json` con `piezas` + una `clip.json`/`escena.py` por pieza | cada pieza es un clip; `audio`/`voz` → `audio_json`; `modulo` y `duracion_objetivo` → `notes` |
| `cargar_promo` | `promo.json` | un proyecto de un clip, `tipo='promo'`, prefijo `Promo · ` |

`aplicar(service, db, curso, dry_run)` escribe: idempotente por **nombre
exacto**, clips por **posición**, y nunca borra. Devuelve un `Resultado`
(`project_id`, `creado`, `clips`, `creados`, `actualizados`, `stale`,
`reporte`), del que el CLI toma solo `reporte` para no cambiar su salida.

**El zip de fuentes es determinista.** `GET /{pid}/fuentes.zip` produce
`curso.json` + `style_block.py` + `clips/NN-<slug>.py` + `guiones/NN-<slug>.*`,
sin compresión, con la fecha de cada miembro fijada a 1980-01-01 y en orden
fijo. Sin eso, dos exportaciones del mismo proyecto salen con bytes distintos
(la hora va en cada cabecera local) y el round-trip deja de ser verificable.
El test hace exportar → borrar el proyecto → importar → exportar y compara
**los bytes**.

**Los guiones no se reescriben al exportar** (se copian tal cual) y **sí** al
importar: entran por `narracion.guardar_guion`, el mismo camino que el editor,
para que `estado.json` quede coherente y la narración se marque
`desactualizada` — que es la verdad: hay guion, no hay audio.

**El lote** (`app/lotes.py`) no es una cola nueva: es *una lista de job_ids con
nombre* sobre la cola de siempre (un render a la vez). Doble vía: en memoria
mientras el backend viva, y **derivado de la tabla de jobs** si se reinició
(los que siguen activos, más todo lo encolado desde el primero de ellos).
`GET /{pid}/lote` da `total/hechos/fallidos/en_curso/pendientes`, la media de
duración de los `done` **de ese proyecto** y la ETA, que descuenta lo que
lleva corriendo el job en curso.

**Duplicar** copia lo que define cómo se ve y cómo suena; **nunca el render**:
un vídeo es de UN clip, y dos clips apuntando al mismo `job_id` harían que
borrarlo dejase sin vídeo a un proyecto que nadie estaba tocando.

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

### R3a — Paridad con la terminal: import/export, lote y duplicar (2026-09-03)

Lo que quedó: `app/importar.py` (tres cargadores + `aplicar` + el zip de
fuentes + la apertura validada del zip), `app/lotes.py`, seis rutas nuevas en
`projects_api.py`, `components/ImportarDialog.jsx` y `components/RenderLote.jsx`,
y los dos CLI convertidos en envoltorios. Medido sobre el contenido real del
repo: **169 cursos, 6 verticales y 10 promos** cargan sin un solo fallo, y el
primer curso vuelve **idéntico** tras exportar → zip → importar.

Trampas:

- **Un zip no es determinista por defecto.** `zipfile` escribe la hora actual
  en la cabecera local de cada miembro: dos exportaciones seguidas del mismo
  proyecto daban bytes distintos y el round-trip byte a byte era imposible de
  afirmar. Se construye cada entrada con un `ZipInfo` de fecha fija
  (1980-01-01), `ZIP_STORED` y orden fijo.
- **La calidad no entra en el hash de contenido.** Cambiarla no vuelve `stale`
  a ningún clip (el hash es `style_block + script + scene`), así que un lote a
  otra calidad se habría saltado los treinta clips por estar «al día» con un
  vídeo del tamaño viejo. El lote implica `force` cuando cambia la calidad.
- **Y el guardián de `update_project` habría bloqueado ese cambio**: existe
  para que un curso a medio renderizar no acabe con vídeos de dos tamaños. El
  lote lo salta a propósito —es el acto deliberado de rehacer el curso
  entero— y por eso **rechaza con 409 el cambio de calidad con `clips`
  elegidos a dedo**: eso sí dejaría el proyecto mezclado.
- **El nombre del clip decide el nombre del archivo del guion.**
  `narracion.slugify` quita acentos; `projects._slugify` no. Si el importador
  hubiera usado el segundo, el zip habría exportado los guiones con un nombre
  y la app los habría buscado con otro, en silencio. `importar.slug` replica
  el primero y un test compara las dos funciones sobre siete títulos.
- **`módulo` y `duración objetivo` de un vertical no tienen columna.** Van a
  `notes` en un formato fijo (mismas líneas, mismo orden) para que reimportar
  dos veces no genere un cambio. Una migración por dos campos que solo usan
  seis proyectos habría sido peor negocio; `estilo` sí la tuvo, porque
  `lienzo` no se puede deducir del `style_block` sin adivinar.
- **La `voz` de un vertical se guarda aunque el diálogo de audio de un curso
  la rechace.** `audio_promo.validar(..., tipo="curso")` prohíbe frases (la
  narración de un curso va por «Generar narración»), pero los clip.json de
  fractales, satélites y emergencia traen voz alineada a mano: perderla al
  importar habría sido peor que no poder editarla desde ahí.
- **Un lote terminado y limpio no se pinta.** La barra solo aparece mientras
  corre o si dejó fallos: un `30/30` en verde no dice nada que no diga ya el
  contador «Render N/N» de la cabecera.

