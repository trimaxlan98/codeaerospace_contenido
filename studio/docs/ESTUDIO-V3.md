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
| R2 | Música | `musica.py` procedural (temas, bpm, tonalidad), banco audible, `audio.musica` en el manifiesto, cama bajo la película con *ducking* | **hecho** |
| R3 | Paridad con la terminal | import/export de curso como archivos, render en lote con calidad, hoja de contactos + fotograma PNG, costuras y picos en la película, **Laboratorio** (ejecutar Python en el sandbox: sondas) | **R3a hecho** (import/export, lote, duplicar); R3b pendiente |
| R4 | Rigor de investigación | `figura.py` (estilo paper, proveniencia, PNG/SVG), datos adjuntos por proyecto, `ntn.py` para la tesis (pase LEO, Doppler, handover, PBFT, MA) | **hecho** (librerías; datos adjuntos pendiente) |
| R5 | UX | Estudio con fotogramas, `style_block` en CodeMirror, duplicar proyecto/clip, panel de audio unificado (voz + música + SFX), pestaña Laboratorio, `Projects.jsx` descompuesto | **R5a hecho** (Proyectos partido, estilo en CodeMirror, audio en una fila, historial de script); Estudio con fotogramas y Laboratorio entraron por R3b |
| R6 | Producción y cierre | VPS, nginx (`client_max_body_size`), unit (`MemoryMax`), README, skills, catálogo, memoria | **hecho** 2026-09-03 (desplegado desde la rama; PR #75 pendiente de merge por el dueño) |

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

## R2 — Música (`studio/tools/musica.py`) · **hecho** 2026-09-03

Hasta hoy la app no tenía música: `unir_vertical.py --mudo` existe
*precisamente* porque el dueño se la ponía fuera. La paleta de SFX da 18
efectos y dos ambientes (`pad`, `nebulosa`), pero un ambiente no es una cama:
no tiene tonalidad, ni pulso, ni progresión.

### Diseño

`TEMAS` es un dict cerrado de **ocho temas**, espejo de `PALETA` y con el mismo
test de AST que impide que la app y la síntesis se separen en silencio. Cada
tema declara raíz (Hz), progresión de acordes por grados (semitonos sobre la
raíz), bpm, compás, subdivisión, el nivel de cada capa y su semilla.

| tema | raíz | bpm | capas (de más fuerte a más floja) |
|---|---|---|---|
| `orbita` | 55,00 | 52 | drone + sub + arpegio — la cama por defecto |
| `deriva` | 49,00 | 44 | drone + sub + arpegio — dos armonías muy lentas |
| `pulso_lento` | 61,74 | 60 | sub + drone + arpegio — un latido por segundo |
| `aurora` | 65,41 | 66 | drone + sub + arpegio — mayor con séptimas, tresillos |
| `telemetria` | 58,27 | 84 | arpegio + sub + drone — datos, órbitas, señales |
| `cuerdas_frias` | 51,91 | 48 | sub + arpegio + drone — cuerdas por delante |
| `amanecer` | 73,42 | 72 | drone + sub + arpegio — mayor ascendente |
| `marcha` | 43,65 | 96 | sub + drone + arpegio — el pulso más rápido |

Tres capas, todas sobre el **reloj absoluto** (eso es lo que hace posible
sintetizar por bloques sin costuras):

- **drone** — pad aditivo, una voz por nota del acorde, con dos capas
  desafinadas un 0,25 % (batido ~0,3 Hz: el colchón respira) y vibrato sumado
  a la **fase** con desviación fija 0,18 rad. Multiplicarlo por `t` —el error
  que ya se corrigió en `sfx.pad`— hace crecer la desviación con los segundos
  y llena el colchón de laterales ásperos.
- **arpegio** — Karplus-Strong en las subdivisiones del bpm, patrón cíclico
  determinista, acento en la cabeza de cada tiempo. Vectorizado por pasadas de
  la tabla de onda (`np.roll`): el bucle muestra a muestra de `sfx.cuerda`
  serían millones de iteraciones de Python por bloque.
- **sub** — senoidal en la fundamental del acorde (`grado % 12`, siempre en
  40–100 Hz), articulado a cada tiempo con envolvente `cos²` **con suelo**: no
  llega a cero (chasquearía) pero baja lo bastante como para que el pulso sea
  *medible* por autocorrelación.

Pasabanda 30–900 Hz para drone y sub; el arpegio va por **90–950 Hz** propios
—recortarle las fundamentales, que viven donde vive el sub, limpió el grave
sin quitarle presencia—. Reverberación única y corta (1,6 s, mezcla 0,22): las
tres capas comparten espacio, como en `sfx.mezclar`.

`tema(nombre, dur, semilla=None, bpm=None)` dura exactamente
`round(dur·24000)` muestras: la progresión se repite y se recorta donde caiga,
y la caída final la pone la envolvente global (entrada ≤ 1,2 s, salida ≤ 1,8 s)
—que es también lo que mantiene mudos los extremos de un promo en bucle—.

### Cifras medidas (contenedor `codeaerospace_contenido-manim`, numpy 2.5.1)

Los ocho temas a 12 s y a 37,3 s, 16 corridas. **Todas pasan**:

| invariante | exigido | medido |
|---|---|---|
| duración | ±1 muestra | **0** de desvío en las 16 |
| determinismo | dos corridas iguales al byte | sha256 idéntico en las 16 |
| pico | ≤ −1 dBFS | −3,00 … −4,31 dBFS |
| recorte | ninguna muestra a fondo de escala | ninguna |
| energía < 300 Hz | ≥ 50 % | **95,4 – 99,8 %** |
| energía < 950 Hz | ≥ 95 % | **99,8 – 100 %** |
| periodicidad del bpm | ±3 % | **0,00 – 2,20 %** (autocorrelación 0,39–0,80) |
| picos espectrales en las notas | ±1 % | 0 notas desplazadas |

Balance por bandas (RMS, ponderación A, tema a 12 s): 40–150 Hz de −33,7 a
−39,7 dB; 150–300 Hz de −31,5 a −41,3; 300–900 Hz de −32,9 a −46,6. Es decir,
grave y medio a la par y la cuerda 8–13 dB por debajo en los temas de colchón,
a la par en `telemetria` y `cuerdas_frias`. «Espacial pero tranquilo», el
criterio verificado del dueño para la marca, aquí es eso.

### El manifiesto y el promo

`audio.musica = {tema, db, bpm?}`, normalizado y validado contra la tupla
`TEMAS` de `audio_promo.py`. `sfx.promo()` suma la cama **antes** del `_norm` a
`pico_db`, así que el pico final sigue siendo el que pide el manifiesto y la
música queda en su sitio relativo a los efectos, no encima. Medido sobre el
promo real de filotaxis (10,73 s, vertical ql) con `volumedetect`:

| mezcla | pico | medio |
|---|---|---|
| sin música (referencia) | **−3,0 dB** | −17,3 dB |
| música `orbita` −24 dB | **−3,0 dB** | −17,3 dB |
| música −24 + voz | −1,7 dB | −20,7 dB |
| música −12 + voz | −1,7 dB | −20,5 dB |

El pico no se mueve: la música entra dentro del presupuesto, no encima de él.

**El umbral del aviso no es un número redondo: sale de medir.** Con una voz a
−1,5 dBFS, la separación voz/música (RMS contra RMS) en el tramo hablado es
**14,98 dB** con la cama en −24, **8,98** en −18 y **2,98** en −12 — o sea
`separación = −9,02 − db`. El mínimo de la casa son 12 dB, y eso se rompe justo
en **−21**: ahí salta el aviso y el defecto son −24, con 3 dB de margen.

> Salvedad honesta: hoy no hay TTS (GCP en mora), así que la voz de la medición
> es de laboratorio — ruido en la banda de la palabra (200–3400 Hz) con
> envolvente silábica a 2,45 sílabas/s, la cadencia medida de Charon, y pico en
> −1,5 dBFS. Mide el **camino de mezcla**, no el timbre.

### La película

`plan.json` acepta `musica: {tema, db}` global. `ensamblar.py` añade un paso 3:
mide la película recién unida, saca su envolvente, construye la curva de
*ducking* y sintetiza la cama de esa duración exacta con la ganancia ya
aplicada. Escalón −9 dB, ataque 0,12 s, liberación 0,60 s, umbral −40 dBFS,
envolvente a 100 Hz sobre un decimado a 4 kHz. Medido sobre una película de
prueba de 21,59 s (una pieza con voz, otra muda):

- cama de **518 160 muestras**, 0 de desvío contra la duración medida;
- pico de la cama **−24,00 dBFS** exacto;
- misma ventana, con y sin *ducking*: **−7,92 dB** en el tramo hablado y
  **0,00 dB** en el mudo. (El escalón pedido son 9; el promedio bajo una voz
  con pausas es 7,9 porque la liberación devuelve la música entre sílabas.)
- película entera: pico **−1,7 dB** con música contra **−1,6 dB** sin ella, y
  el tramo hablado −18,9 contra −18,8. Añadir música no mueve el montaje.

### Trampas

1. **`amix=…:normalize=0` no existe en el ffmpeg de la imagen.** Debian 11 trae
   **4.3.9** y esa opción llegó en 4.4: el filtro aborta con «Option
   'normalize' not found». Y sin la opción, `amix` divide cada entrada por el
   número de entradas, así que la película entera bajaría 6 dB por el hecho de
   añadir una segunda pista. **Era un fallo ya existente**, no de este sprint:
   la rama voz+cama de `args_pieza` (sprint E3) lo usaba, de modo que montar un
   curso cuyos clips llevaran cama de sonido *y* narración fallaba en seco.
   Ahora las dos sumas van por `amerge=inputs=2,pan=mono|c0=c0+c1` con un
   `aformat` explícito delante, que suma a ganancia unidad desde ffmpeg 2.x.
2. **`alimiter` trae el auto-nivel ENCENDIDO.** `level` es `true` por defecto:
   sin `level=disabled`, el limitador —que está ahí como red, no como efecto—
   sube la película entera hasta el techo, exactamente lo contrario de lo que
   se le pide.
3. **La envolvente del *ducking* se mide sobre el montaje SIN música.** Medida
   sobre la película ya mezclada, la propia cama supera el umbral y se agacha a
   sí misma: 96 % del metraje agachado contra el 37 % real.
4. **`_filtra` es una convolución CIRCULAR.** Al sintetizar por bloques, el
   final de cada bloque se contamina con su propio principio. Con sólo la
   entradilla de 3 s (que sí recupera las cuerdas vivas y la cola de reverb),
   el salto entre muestras vecinas en la costura era 0,0089 sobre un pico de
   0,063 — el mayor salto de todo el archivo, es decir, un clic. Con una guarda
   de cola de 1 s baja a 0,0010 y 0,0005, por debajo del salto máximo natural
   de la señal (0,0023).
5. **Una escala por bloque hace saltar el nivel en cada costura**, que es justo
   lo que se oiría. `escribe_cama` hace **dos pasadas**: la primera sólo mide el
   pico de toda la cama, la segunda escribe. Sintetizar 200 s cuesta 17 s en el
   contenedor (las dos pasadas incluidas); un curso de media hora, ~2,5 min.
6. **La música se aparta bajo cualquier sonido del montaje**, no sólo bajo la
   voz: en un curso narrado eso es la voz, y en un clip con cama de SFX también
   la cama. Es lo que se quiere —la música es el fondo de todo lo demás— pero
   hay que saberlo antes de extrañarse.
7. **La sonda de picos espectrales tiene que mirar sólo los acordes que
   SUENAN.** A 12 s de `orbita` (4,6 s por acorde) el cuarto no llega a entrar;
   buscarlo encontraba el vecino y acusaba un desplazamiento del 3 % inexistente.

### Superficie nueva

`studio/tools/musica.py` (`banco` / `tema` / `aplicar`), comando `musica` del
runner (calcado de `paleta`, destino fijo `exports/musica`), `cfg.musica_dir`,
`app/musica_api.py` (`GET/POST /api/musica`, `GET /api/musica/{tema}` con la
misma defensa de ruta que `sfx_api`), `MusicaSelector.jsx` compartido por
`AudioPromoDialog` y `PeliculaPanel`, y 20 tests nuevos en
`tests/test_musica.py` (espejo AST de nombres **y** de bpm, manifiesto, avisos,
banco, plan de película, hash que caduca al cambiar de tema, y la curva de
*ducking* como función pura).

## R3 — Paridad con la terminal

| Brecha | Entra como | Estado |
|---|---|---|
| curso como archivos | `POST /api/projects/importar` (zip o `{slug}` del repo) y `GET /{pid}/fuentes.zip` | **R3a** |
| lote con calidad | `POST /{pid}/render-lote {clips, calidad, force}` + progreso en `GET /{pid}/lote` | **R3a** |
| duplicar proyecto/clip | `POST /{pid}/duplicar`, `POST /{pid}/clips/{cid}/duplicar` (venía de R5) | **R3a** |
| hoja de contactos | comando `frames` del runner → `GET /api/jobs/{id}/frames` (N PNG + último) | **R3b** |
| fotograma / figura | `POST /api/jobs/{id}/fotograma {t, formato: png／svg}` a resolución del job | **R3b** |
| costuras y picos | `pelicula/verificar` mide además la unión pieza a pieza (PIL), el pico por pieza y la cola de silencio de la voz | **R3c** |
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

### R3c — medir la película como se mide en la terminal (2026-09-03)

**Lo que cierra.** `verifica_vertical.py` y `unir_vertical.py` miden de un curso
tres cosas que la app no medía: la **costura** entre piezas, el **pico** por
pieza y la **cola de silencio** de cada narración. Eran justamente las tres que
han cazado defectos reales —el parpadeo de las catorce uniones del curso 28 no
lo vio nadie a ojo— y hasta hoy solo existían en la terminal. Ahora las mide
`ensamblar.py verificar`, se persisten en `pelicula.json` y se pintan en el
panel.

#### La costura, y por qué los umbrales no son números redondos

Costura = diferencia media absoluta por subpíxel (0–255) entre el **último
fotograma real** de una pieza y el **primero** de la siguiente, con PIL
(`ImageChops.difference` + `ImageStat.mean`, en C: la misma cuenta en Python
puro sobre 1920×1080 son 6,2 millones de restas por unión).

Se mide sobre los **vídeos de origen**, no sobre la película: en el montaje esos
dos fotogramas son consecutivos y la diferencia que ve el espectador es la
misma, pero sacarlos de los originales no depende de acertar el instante del
empalme dentro de un archivo de media hora.

Los umbrales salen de los cursos ya entregados:

| medida | valor | qué era |
|---|---|---|
| cursos **31** (esp32) y **33** (señales) | **0,0000** exacto, 15 y 19 uniones | lo mejor de la colección |
| curso **26** (fractales) | 0,003 | |
| curso **28** (satélites), uniones de lección | **0,0048** (13 de máximo) | el peor caso *limpio* medido |
| curso **28**, intro y cierre de marca | 0,055 | **legítimo**: la marca no lleva esquinas HUD ni marca de agua |
| curso **28** antes del arreglo | **0,0552 idéntico en las catorce** | el defecto: un `FadeOut` apagaba la capa fija al final de cada pieza |

De ahí: **≤ 0,01 limpia** (el doble de margen sobre el peor limpio),
**≤ 0,06 a mirar**, **> 0,06 se ve**. Entre 0,01 y 0,06 **no se falla, se
avisa**, porque el mismo 0,055 es un defecto en una unión de lección y lo
correcto en una unión con la marca. Quien las distingue no es el valor: es el
**diagnóstico**.

`firma_capa_fija(valores)` emite el diagnóstico cuando **todas** las costuras
valen lo mismo (±1e-4), no valen cero y hay al menos **tres** (dos iguales son
una coincidencia). Si además el valor compartido pasa de 0,01, sube de aviso a
**problema**: eso es exactamente el 0,0552 del curso 28, y es lo único que lo
separa del 0,055 legítimo de una unión suelta con la marca.

Con transición distinta de `corte` la costura **no aplica** (`n/a`): xfade funde
las dos piezas a propósito.

#### Pico y cola de la voz

- **Pico por pieza**: ya se medía con `volumedetect` sobre el tramo; ahora el
  informe lo expone con su `pico_alto` contra el techo de la casa, **−0,5 dBFS**
  (el mismo número de `unir_vertical.py`).
- **Pico global**: se mide sobre la película **entera**, no como máximo de los
  tramos — los tramos se recortan 0,05 s por lado y un recorte que caiga justo
  en un empalme se escaparía. Es el número que imprime `unir_vertical.py` al
  cerrar un montaje vertical.
- **Cola de silencio de la voz**: los últimos **0,8 s** del wav de narración
  bajo **−50 dBFS**. Se mide sobre el **archivo de voz**, no sobre la película:
  en el montaje esos 0,8 s ya llevan encima la cama de sonido de la pieza y el
  silencio de la voz sería invisible. Una voz que llega hablando hasta el final
  se corta a media palabra en el empalme.

#### El semáforo pasa a tres colores

`estado_verificacion` devuelve ahora `pasa` · **`avisos`** · `no_pasa` (más
`sin_verificar` y `vieja`). Sin el ámbar, una costura de 0,055 o un pico en
−0,4 dBFS tendrían que elegir entre mentir (verde) o enseñar a ignorar el rojo.
Una película medida **antes** de R3c no trae `avisos` y sigue en verde: no se le
inventan avisos que nadie midió.

#### Verificación REAL (contenedor `codeaerospace_contenido-manim`, ffmpeg 4.3.9, PIL 12.3.0)

Nueve escenas de laboratorio a `ql` (854×480 @ 15 fps, `render_jobs/escenas_r3c.py`,
fuera de git) montadas en cinco películas con `ensamblar.py montar` y medidas con
`ensamblar.py verificar`. Cada verificación, **1,6–2,8 s** de reloj incluida la
puesta en marcha del contenedor.

| caso | costuras medidas | veredicto | diagnóstico |
|---|---|---|---|
| 4 piezas limpias, corte | 0,0189 · 0,0189 · 0,0189 | 3 avisos | **sí** (todas iguales) |
| 4 piezas con `FadeOut` de la capa fija | **0,1183 · 0,1183 · 0,1183** | 3 fallos → rojo | **sí** |
| la 1.ª acaba **en negro** | **19,4252** · 0,0189 · 0,0189 | 1 fallo → rojo | **no** (no son iguales) |
| el mismo material sucio con empalme `fundido` | n/a · n/a · n/a | verde | — |
| 3 piezas con voz | 0,0189 ×3 | avisos | sí |

Del último caso, lo que interesa es el audio: picos por pieza **−10,5 / −10,5 /
−0,4 / −91,0 dBFS**, pico global **−0,4** → aviso contra el techo de −0,5; colas
de voz **−91,0 (ok) · −10,5 (sin cola) · −91,0 (ok)**, y la pieza sin voz sin
medida ninguna. El aviso sale en singular: «1 pieza cierra la voz sin cola de
silencio».

Los dos casos que importan salen bien discriminados: el `FadeOut` de la capa
fija reproduce la firma del curso 28 (**el mismo valor en las tres uniones**) y
el clip que acaba en negro da 19,4 sin diagnóstico, que es la verdad — ahí no
hay ninguna capa fija culpable, hay un plano distinto.

#### Trampas medidas

1. **`-sseof -0.05` no escribe nada por debajo de 20 fps, y sale con código 0.**
   Medido en el contenedor sobre el mismo material a 15 y a 60 fps:

   | fps | `-sseof -0.05` | `-sseof -0.35` |
   |---|---|---|
   | 15 | código 0, **archivo vacío** | 4 993 bytes |
   | 60 | 5 078 bytes | 5 078 bytes (**el mismo fotograma**) |

   A 15 fps los fotogramas están a 66,7 ms y el salto cae detrás del último. Es
   el mismo fallo silencioso que ya documentan `verifica_vertical.py` y
   `promo_verifica.py`, y por eso ellos usan 0,35. Aquí se pide 0,05 (tres
   fotogramas a 60 fps, que es el ritmo de los cursos) y **se reintenta con
   0,35** si no salió nada. La segunda fila prueba que da igual: con `-update 1`
   cada fotograma pisa al anterior, así que lo que queda al terminar **es** el
   último, mida la cola lo que mida.
2. **Un montaje a `ql` se queda en ámbar por el códec, no por el contenido.**
   Las tres costuras «limpias» dan 0,0189 idéntico, y no hay ningún objeto
   culpable: el último fotograma de una pieza es un P-frame al final de un GOP y
   el primero de la siguiente es un I-frame. Se comprobó midiendo el primer
   fotograma de cada pieza contra el primero de las demás (**0,0000**), el
   último contra el último (**0,0000**) y el primero contra el último **de la
   misma pieza** (**0,0189**): la deriva vive dentro del archivo, no entre
   archivos. Los umbrales están calibrados sobre entregas `qh`; el mensaje del
   diagnóstico nombra las dos causas posibles para que nadie salga a buscar un
   `FadeOut` que no existe.
3. **La cola de silencio hay que medirla en el wav, no en la película.** En el
   montaje esos 0,8 s finales llevan encima la cama de sonido de la pieza (y la
   música, si la hay): la voz podría acabar a media palabra y el tramo seguiría
   sonando muy por encima de −50 dBFS.
4. **El pico global no es el máximo de los picos por pieza.** Los tramos se
   miden con 0,05 s de margen a cada lado para no arrastrar el empalme; un
   recorte que caiga justo ahí no aparecería en ninguno de los dos tramos
   vecinos.
5. **Medir la película dejó de costar segundos.** Son dos fotogramas por unión
   más un `volumedetect` por pieza más otro global. Los 300 s de
   `VERIFICA_TIMEOUT` —que es el tope del *promo*, una pieza— se quedaban
   cortos para un curso de treinta piezas a 1080p60 en un VPS de 1,5 vCPU:
   `handle_ensamblar` estrena `ENSAMBLAR_VERIFICA_TIMEOUT = 1800` y el cliente
   espera 1 860. Un test comprueba que los dos números no se separen.
6. **`diagnostico()` devuelve ahora dos listas.** Problemas (rojo, `ok=False`) y
   avisos (ámbar, entregable). Meter los avisos en `problemas` habría puesto en
   rojo cualquier montaje de previsualización; dejarlos fuera del informe habría
   sido no medirlos.

#### Superficie nueva

`ensamblar.py`: `diferencia_media` (pura, sobre dos imágenes PIL),
`veredicto_costura`, `firma_capa_fija`, `medir_costuras`, `cola_voz_db`,
`_saca_frame`, las constantes `COSTURA_OK/COSTURA_AVISO/PICO_MAX_DB/COLA_VOZ_*`
y un `verificar` que devuelve `costuras`, `costura_peor`,
`costura_diagnostico`, `costura_umbrales`, `pico_max_db`, `pico_veredicto`,
`sin_cola_voz` y `avisos`. `pelicula.py`: el semáforo de tres colores.
`PeliculaPanel.jsx`: el subcomponente `Costuras` (una celda por unión, valor a
cuatro decimales, color por veredicto **y recuento en palabras**, tooltip
«de → a»), la línea del pico y las dos listas de problemas y avisos.
`manim_runner.py` y `runner_client.py`: el tope nuevo. **17 tests** en
`tests/test_pelicula.py` (46 en el archivo, 330 en la suite).

## R4 — Rigor de investigación (agente Opus, librerías)

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

---

## R4 — Librerías de investigación (`figura.py` y `ntn.py`)

Cerrado el **2026-09-03**. Dos primitivas nuevas, dos sondas, cinco demos y una
lección. Nada de backend salvo `conocimiento.py`, que tenía un defecto que dejaba
a la mitad de las primitivas invisibles para el asistente (abajo).

### Qué entra

| Archivo | Qué es |
|---|---|
| `studio/content/manim_extensions/figura.py` | figura de paper: lienzo IEEE en pulgadas y dpi, tipografía medida en **puntos impresos**, ejes, banda de IC, CDF, Gantt, leyenda, sello de proveniencia, `leer_csv` / `leer_jsonl` |
| `studio/content/manim_extensions/ntn.py` | pase LEO (AOS/TCA/LOS, elevación, distancia oblicua), Doppler, retardo, handover, quórum PBFT, margen adaptativo y gates con IC95 % |
| `studio/tools/sonda_figura.py` | 79 invariantes, incluido el PNG de `-s` medido con PIL |
| `studio/tools/sonda_ntn.py` | 94 invariantes, con contraejemplo en cada propiedad que lo admite |
| `studio/content/animations/investigacion/01..05` | figura MA con IC y sello, Gantt desde JSONL, CDF desde CSV, pase LEO-600 animado, quórum PBFT |
| `studio/content/datos/ejemplo/` | `disponibilidad.jsonl`, `recuperacion.csv`, `rtt_leo600.csv` |
| `studio/content/lessons/manim-primitivas/06-figuras-de-investigacion.md` | la lección |

**173 invariantes, 0 fallos.** Backend: 275 tests verdes.

### El lienzo, medido

| | 1 columna | 2 columnas |
|---|---|---|
| plantilla IEEE | 3.5 in | 7.16 in |
| a 300 dpi | **1050 × 652 px** | **2148 × 1332 px** |
| frame de escena | 14.00 × 8.69 u | 28.64 × 17.76 u |
| 1 unidad de escena | **18 pt** | **18 pt** |

Que una unidad valga 18 puntos en las dos hace que un `font_size` signifique el
mismo tamaño físico en una columna y en dos, y que la misma figura entre en un
clip de vídeo con `Figura.pantalla(tema="marca")` sin tocar el dibujo. La
verificación que cierra el círculo está en la sonda: un texto declarado de 8 pt
sale con **34 px de tinta** en el PNG a 300 dpi (lo exacto son 33.33), contados
con PIL.

### Las cifras de la tesis que ya se pueden dibujar

| | |
|---|---|
| FSPL a 600 km y 2 GHz | 154.03 dB (el 92.45 de la casa sobra **0.0022 dB**) |
| horizonte geométrico a 600 km | 2829.35 km |
| pase sobre Ciudad de México (h=600, i=53°, máscara 10°) | **89.63°** máx., **530.1 s** |
| distancia / retardo de ida | 1930 km (6.44 ms) en AOS, 600 km (2.00 ms) en TCA |
| Doppler de pico a 2 GHz | **43.60 kHz** = 21.82 ppm |
| tick 0 del banco (12.9 ms) leído como RTT | **9.97°** — la máscara de 10° del propio escenario |
| tick 4 (4.5 ms) leído como RTT | 61.46° |
| tren de 4 satélites, solape 0.25 | 100 % de cobertura, 3 relevos, elevación máx. 89.8° → 51.9° |
| quórum PBFT n=7 | f=2, quórum 5, 84 mensajes (total exacto `2n(n−1)`) |
| quórum PBFT n=6 | f=1, quórum **4** — `2f+1` daría 3 |
| gate con 3 semillas al borde del umbral | media 0.253, IC95 [0.200, 0.300] → **indeciso** |

### Los dos hallazgos que trascienden el sprint

**1. El quórum de PBFT no es `2f+1`.** Es `ceil((n+f+1)/2)`, y coincide con
`2f+1` justo cuando `n = 3f+1` — el caso de todos los diagramas, y por eso
«2f+1» se repite como si fuera la definición. Con n=6 y f=1, `2f+1` = 3 no es ni
mayoría de 6: dos quórums de tres pueden no compartir **ninguna** réplica
correcta, y el protocolo pierde la intersección en la que se apoya. La primera
versión de `quorum_pbft` devolvía 3; lo cazó la sonda pidiendo «el quórum es
mayoría estricta», que es una propiedad, no una fórmula.

**2. Los delays del CSV LEO-600 del banco son de ida y vuelta.** Leídos como de
ida, los 12.9 ms del primer tick serían 3867 km y el horizonte a 600 km está en
2829: geométricamente imposible. Leídos como RTT dan 9.97° de elevación, o sea
la máscara de 10° del propio escenario, y el resto de los ticks encajan (61.46°
en el mínimo). `ntn.escenario_leo600()` calcula las dos lecturas y dice cuál es
posible, en vez de suponerlo.

### Trampas nuevas para `references/trampas.md`

- **El espacio infla la caja.** Un `Text` con un espacio crea un submobject
  **vacío**, y `Mobject.reduce_across_dimension` devuelve `0` para un submobject
  sin puntos: la caja del texto se come el origen en cuanto se mueve.
  `Text("RTT (ms)")` mide 0.2539 de alto recién nacido y **2.1270** después de
  un `shift`; sin espacios no pasa. `.width`, `.height`, `.get_center()`,
  `next_to()` y `move_to()` quedan inservibles con texto de más de una palabra.
  `figura` posiciona con `caja` / `poner` / `pegar`, que leen los puntos reales.
  Esto afecta a **toda** la casa, no solo a las figuras.
- **Un lado impar de píxeles rompe el vídeo.** 1050 × 651 mataba el render con
  `avcodec_open2("libx264") -> Generic error in an external library`, sin nombrar
  el 651; el PNG de `-s` salía perfecto, así que el fallo aparecía solo al pedir
  el clip. `Figura` sube el lado al par siguiente.
- **`frame_width` y `frame_height` son independientes en manim 0.20.1**: fijar
  uno no recalcula el otro, y la figura sale deformada sin aviso.
- **`Axes` con un rango que no contiene el cero pega el eje X al borde de
  ARRIBA** (`_origin_shift`), con sus números encima de la curva. `ejes_paper`
  dibuja el marco a mano abajo y a la izquierda.
- **Un guardián de ancho no basta: hay que medir la caja COLOCADA.** Un bloque
  de 11 unidades cabe de sobra en un frame de 14.23 y se sale por la izquierda
  si se ancla a la derecha de unos ejes.
- **`Create` sobre unos ejes dibuja los rótulos letra a letra** (el eje X decía
  «tie» a mitad de la animación): se traza el marco y lo escrito entra fundido.
- **Un pase LEO es casi simétrico alrededor del TCA, también uno oblicuo**: los
  2.2° que gira la Tierra en 530 s apenas tuercen la elevación (el azimut sí).
  Está escrito para que nadie «arregle» una asimetría que la física no pide.
- **El TCA es un instante, no una muestra**: cerca del cenit la elevación cae ~1°
  cada 1.5 s y un pase cenital rotulaba 89.13° donde la geometría dice 90.
- **Con tres semillas el bootstrap solo tiene 10 remuestras distintas.** El IC95 %
  está cuantizado y dos semillas de bootstrap dan el mismo intervalo: es el techo
  de resolución de tres corridas, y por eso un gate al borde sale indeciso por
  construcción. Y remuestrear MUESTRAS en vez de SEMILLAS estrecha el intervalo
  hasta hacer pasar un gate indeciso (medido: límite inferior falso 0.254 contra
  el honesto 0.221, con umbral 0.25).

### `conocimiento.py`: la mitad de las primitivas eran invisibles

El paquete que ve el asistente recortaba el TOTAL de un tajo a 60 000
caracteres. Con 47 primitivas y ~280 000 caracteres ya recortados a 7 000 por
archivo, el modelo veía las fuentes **por orden alfabético hasta la letra «c»**
(`calculo_vectorial.py`) y ninguna de las demás —`enlace`, `satelites`,
`lienzo`, `transformadas`, `figura`, `ntn`…— existía para él. No hay lista fija
que arreglar: el defecto era el recorte. Ahora:

1. un **índice de una línea por módulo** (47 líneas, ~5 kB), para que ninguna
   primitiva sea invisible;
2. la fuente completa de los **prioritarios** primero (`code_brand`,
   `transiciones`, `lienzo`, `figura`, `ntn`) y el resto hasta donde quepa, con
   el corte en la frontera de un módulo y un aviso que dice cuáles quedaron
   fuera;
3. cuando una fuente se recorta, se le pega detrás **su lista completa de
   firmas**: en `figura.py` y `ntn.py` (40 y 30 kB) el corte a 7 000 se comía
   `sello`, `leer_csv` y `quorum_pbft`, justo lo que hay que llamar.

Medido: el paquete pasa de 60 000 truncados a 56 567 con las 47 primitivas
nombradas y la API de `figura` y `ntn` entera. Los 275 tests siguen verdes.

### Comprobado en la app, no solo en la terminal

- `GET /api/animations` indexa la categoría «Investigación» con sus **5**
  demos y la escena correcta de cada una (`FiguraMA`, `FiguraGantt`,
  `FiguraCDF`, `PaseLeo600`, `QuorumPbft`); `test_animations.py` en verde
  (7 pasan). La lección nueva sale en `manim-primitivas` con orden 6.
- Las cinco demos se renderizaron **con el bloque de identidad que anexa
  `branding.aplicar()`**, que es lo que de verdad corre en la app: las tres
  figuras de paper salen idénticas (fondo blanco, sin marca de agua ni
  esquinas HUD, gracias a `sellar_escenas`) y las dos de vídeo reciben la
  marca sin que el wordmark toque ningún pie.
- Efecto secundario conocido y no corregido: sin una lección con el mismo id,
  el título de una animación se deriva del slug con `.capitalize()` y las
  siglas quedan en minúscula («Cdf de recuperacion»). Es el comportamiento que
  ya tienen «De 5g a 6g» e «Isac sensado y comunicacion» en producción;
  arreglarlo es tocar `animations.py`, que R4 no toca.

### Lo que R4 deja pendiente para R3/R5

`figura.leer_csv` ya lee de `MS_DATOS_DIR`, pero **la app todavía no monta un
`datos/` en el job**: eso es la brecha «datos adjuntos» de R3
(`POST /{pid}/datos`). Hasta entonces, un clip declara su directorio a la vista,
como hacen las demos 02 y 03.

Y una corrección al plan: **manim 0.20.1 no exporta SVG**. `--format` solo
acepta `png`, `gif`, `mp4`, `webm` y `mov` (comprobado: `Error: Invalid value
for '--format': 'svg' is not one of ...`). La figura citable es el **PNG a 300
dpi**, que es lo que `Figura` está construida para dar exacto; si algún día hace
falta vectorial, hay que pasar por el `Camera` de manim o por un exportador
propio, no por la CLI. Queda también llevar `Figura` a la UI como tipo de
proyecto «figura».

Pendiente de R4: **datos adjuntos por proyecto** (`POST /{pid}/datos` montados como `datos/` en el job). Hoy `MS_DATOS_DIR` apunta al repo (`studio/content/datos/`), suficiente para las figuras de la tesis versionadas en git.



### R5a — UX de Proyectos: descomposición, CodeMirror, audio y historial (2026-09-03)

La vista más usada del estudio era **un archivo de 1 667 líneas con trece
subcomponentes dentro**. Este sprint la parte, y de paso arregla las tres
cosas que ese tamaño escondía: el estilo compartido se editaba en un
`<textarea>`, el sonido de un clip vivía en dos sitios que no se miraban, y
la app tenía delante el script del último render que funcionó sin enseñarlo
nunca.

#### Lo que se partió

`Projects.jsx` pasa de **1 667 líneas a 31**: hoy solo enruta lista/detalle.
Lo demás son **14 archivos** en `components/proyectos/` (2 195 líneas, ~530
de ellas nuevas: comentarios de por qué, la fila de audio y el historial):

| Archivo | Líneas | Qué es |
|---|---:|---|
| `ProjectDetail.jsx` | 686 | el detalle: cabecera, panel de estado, acciones, clips |
| `meta.js` | 229 | el vocabulario compartido: estados, rangos, agrupación, espejos del backend |
| `NewProjectDialog.jsx` | 199 | alta de proyecto con plantillas |
| `ClipCard.jsx` | 189 | un clip |
| `ProjectsList.jsx` | 170 | el índice: buscador, filtro, orden, familias |
| `HistorialScriptDialog.jsx` | 154 | **nuevo** — el diff contra el último render |
| `StyleDialog.jsx` | 129 | el estilo compartido, ahora en CodeMirror |
| `FilaAudio.jsx` | 128 | **nuevo** — voz · música · SFX en una fila |
| `insignias.jsx` | 88 | `ProgressBar`, `CountsLine`, `NarrBadge`, `Stat`, `DurationBadge` |
| `DuplicarProyectoDialog.jsx` | 67 | duplicar el proyecto |
| `AddClipDialog.jsx` | 64 | añadir clip |
| `ProjectCard.jsx` | 44 | la tarjeta del índice |
| `FamilyGroup.jsx` | 33 | una familia plegable |
| `ProjectGrid.jsx` | 15 | la rejilla de tarjetas |

Además, el diff por LCS sale de `Assistant.jsx` (219 → 195 líneas) a
`src/lib/diff.js`: lo usan el asistente y el historial de script, y dos copias
del mismo algoritmo se separan en silencio.

La descomposición es **a comportamiento constante**: cada prop, cada efecto y
cada comentario viajan tal cual. Lo que cambia de verdad son las tres piezas
de abajo.

#### `style_block` en CodeMirror

El mismo editor del Estudio (`python()`, `useEditorTheme()`), y dos datos que
antes solo se sabían leyendo el backend:

- **el desfase de líneas.** manim numera los fallos sobre el script
  *compuesto* (estilo + marcador + clip) y el Estudio le resta `style_offset`
  para señalar la línea del clip. Al editar el estilo ese número cambia, así
  que se enseña: «23 líneas · desfase +25 líneas».
- **qué va a pasar con la identidad.** `branding.aplicar` anexa el bloque de
  marca CO.DE Academy salvo que el script compuesto ya la traiga. El diálogo
  dice cuál de los dos casos es, y en una presentación habla del lienzo
  (`presentacion`) en vez de la marca, que es lo que ese tipo garantiza.

#### El audio de un clip, en una fila

Estaban repartidos en dos sitios a dos alturas: un botón «Audio» (cama de SFX
y música) en la fila de acciones y, más abajo y **solo si el backend ya sabía
algo del clip**, una fila de narración con «Guion y voz». Ahora es una fila
con tres chips —**voz · música · SFX**— que dicen *lo que hay*, no solo que la
opción existe: `música ORBITA`, `sfx 3 EFECTOS`, `voz SIN NARRACIÓN`. Cada uno
abre el diálogo que lo edita. En un promo el chip de voz abre el manifiesto y
no el guion, porque allí la voz son frases del propio manifiesto.

#### Historial ligero del script

El estudio no guarda versiones, pero guarda una: la del último render que
salió bien. Con el clip **desactualizado** aparece «Último render», que
compara las dos versiones (LCS, «11 líneas distintas · −6 / +5») y permite
volver a la que funcionó, en dos toques porque se pierde lo escrito.

#### Verificación

`vite build` verde. QA Playwright contra una instancia local real (uvicorn en
3002 con `MS_WORKSPACE` aislado + `dist/` servido con proxy a `/api`),
sembrada por la API con 6 proyectos en 2 familias, 12 clips, un promo y un
clip con cama musical: **14/14 pasos** en 1440×900, en 390×844 y en el tema
claro, **cero errores de consola** y cero desborde horizontal; más **5/5**
del ciclo del historial (el botón solo en el clip desactualizado, el diff, los
dos toques y la restauración).

Y **11/11 casos** comparando los espejos en JS contra el Python real
(`style_offset`, el corte por el marcador y `branding.ya_marcado`), incluidos
los dos que importan: un estilo con cola de líneas en blanco y un script que
contiene el propio marcador.

#### Trampas

1. **`GET /api/projects/{pid}` no trae el manifiesto de audio.** El encargo
   daba por hecho que el tema de música se leía de `audio_json` del clip, pero
   `clip_public` quita `audio_json` **a propósito** (hasta 30 clips por curso)
   y solo deja `audio = {estado, has_audio}`. Sin tocar el backend, el detalle
   pide `GET .../clips/{cid}/audio` **solo para los clips que ya tienen
   manifiesto**: en un curso normal son cero peticiones. Mientras viaja, el
   chip dice «…» y no «ninguna», que sería mentir antes de saberlo.
2. **Lo que guarda un job NO es el script del clip: es el compuesto.**
   Restaurar sin cortar por `STYLE_MARKER` habría metido el `style_block`
   entero *dentro* del script del clip, y el siguiente render se lo habría
   antepuesto otra vez: el estilo duplicado, dos veces cada import. Medido en
   el fixture: 34 líneas de compuesto, 9 de clip, 25 de estilo. La prueba de
   que el corte es exacto no es leer el diff: es que **tras restaurar el clip
   vuelve a «renderizado»**, porque el hash de contenido se calcula sobre
   `style_block + script + scene` y solo cuadra si se devolvió exactamente lo
   que se renderizó.
3. **`style_offset` no son «las líneas del estilo».** Es
   `lines(style.rstrip()) + 3` — la línea en blanco, el marcador y otra línea
   en blanco. Un espejo escrito a ojo se habría equivocado en 3 y el número
   habría sido plausible y falso; por eso se compara contra el Python.
4. **Buscar la palabra `lienzo` o `presentacion` sueltas repetiría un fallo ya
   corregido.** `branding.py` busca el **import** justamente porque
   «presentación» es una palabra común y un comentario cualquiera dejaría el
   render sin marca. El espejo del frontend hace lo mismo, y hay dos casos de
   prueba (`# presentacion de la idea`, `# el lienzo va en negro`) que deben
   dar *false*.
5. **El detalle tampoco ve el `script` de los clips** (`clip_public` lo quita
   igual). Eso deja `usaSimulacion` mirando en la práctica solo el
   `style_block`: el aviso de «esta pieza se renderiza en local» no se dispara
   por el código de un clip escrito a mano. **Es un fallo preexistente y no se
   ha tocado** —esto era una refactorización— pero queda anotado: se arregla
   con un campo calculado en el backend, no en el navegador.
6. **El estado de la mezcla se calla cuando no dice nada nuevo.** Con la fila
   llamándose «Audio», un `AUDIO SIN RENDER` al lado sonaba a tartamudeo, y
   además ya lo dice el distintivo de estado del clip dos líneas más arriba.
   Solo se pinta en `sin_mezclar`, `desactualizado` y `al_dia`.
7. **En el QA, desplegar la segunda familia con un clic real falla.** La lista
   se re-pinta al abrir la primera y Playwright acaba pulsando sobre `<html>`.
   Se despliega desde dentro de la página, que es lo que ya se hacía con el
   arrastre de clips.
8. **El fixture del render terminado deja un 404 en la consola.** Es un job
   `done` escrito a mano (el arnés corre sin runner), así que no hay mp4 en
   disco y **Renders** —que sigue montada, las vistas son *keep-alive*— pide
   su vídeo. Artefacto del arnés, no del código: un `done` real siempre tiene
   archivo.

### R6 — cierre (2026-09-03, 15:30)

Todo lo anterior está desplegado en https://coderesearch.space **desde la
rama** `estudio/v3-investigacion` (el clasificador de permisos de la sesión
bloqueó `gh pr merge` y el push a `main`; el PR #75 queda para el dueño:
después, en el VPS, `git checkout main && git pull`).

Verificado en producción con cookie firmada, no leyendo el código:

| Qué | Medido |
|---|---|
| voz edge / piper (guion a mano, 2 secciones) | 14.2 s de audio en 2.0 s / 14.5 s en 4.1 s |
| grabación propia subida (wav estéreo 44.1 kHz) | 200, mono 24 kHz, silencio recortado, `al_dia` |
| banco de música | 8 temas en 6.4 s |
| importar curso 33 desde el repo (`dry_run`) | 20 clips, 200 |
| `fuentes.zip` de un curso real | 49 908 bytes |
| hoja de contactos / fotograma 1920 | 5.6 s / 1920×1080 |
| sondas en el Laboratorio | ntn 94/0 · figura 79/0 · sistemas 73/0 |
| película real con música (ATP 3.3, 4 clips, corte) | montada en 27.1 s, 151.3 s, 8.4 MB, verificada en 5.4 s: ok con avisos |

Lo que la película destapó: **en horizontal la costura visible es por
diseño** (2.23, 5.55 y 5.96/255 en un curso entregado): la regla estricta se
queda para 9:16 y en 16:9 baja a aviso. Y las cuatro piezas cierran la voz
sin cola de 0.8 s: eso sí es un aviso legítimo que antes nadie medía.

Pendiente que trasciende este encargo: datos adjuntos por proyecto (R4),
SVG (manim 0.20.1 no lo exporta; la figura estática es PNG a 300 dpi), la
migración del asistente al catálogo completo de primitivas (hecho el índice,
falta medirlo con Gemini cuando vuelva la facturación), y el `.gitignore`
de `node_modules/` con barra final que no ignora un symlink.
