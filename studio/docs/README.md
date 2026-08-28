# ManimStudio

Consola web privada (un solo usuario) para renderizar escenas de Manim Community en el
contenedor Docker existente de `codeaerospace_contenido`, con biblioteca de videos,
monitoreo en tiempo real e histórico del VPS y asistente IA de depuración (Vertex AI).

**URL:** https://coderesearch.space · **Usuario:** `alanrosasp` · la password vigente vive en
la DB (tabla `auth`, ver «Autenticación y cambio de contraseña» más abajo), no en un archivo.

Este documento describe el **despliegue en el VPS**. Para levantarlo en una máquina de
desarrollo, ver [`docs/entorno_desarrollo/`](../../docs/entorno_desarrollo/README.md).

## Arquitectura

```
navegador ──HTTPS──▶ nginx (coderesearch.space)
                      ├─ /            → estático  studio/frontend/dist  (React+Vite+CodeMirror)
                      └─ /api/        → 127.0.0.1:3002  backend FastAPI (usuario manimstudio, sin privilegios)
                                            │  cola en memoria: 1 render a la vez
                                            │  SQLite: studio/backend/manimstudio.db
                                            │  Vertex AI (unico modulo con salida a red;
                                            │  HTTPS a us-central1-aiplatform.googleapis.com)
                                            ▼ socket unix /run/manimstudio/runner.sock (0660 root:manimstudio)
                                        manim-runner (root, superficie minima:
                                        render/cancel/thumbnail/stats/ping)
                                            ▼ docker compose run … manim-render
                                        contenedor de render: network_mode:none, cpus:1.5, mem:2g,
                                        pids:256, no-new-privileges, timeout duro, --rm,
                                        --user manimstudio (los archivos creados son borrables
                                        por el backend)
```

Decisiones clave (y por qué):

- **FastAPI**: tipado, async nativo, SSE trivial. **Un solo worker uvicorn** — la cola y el bus
  SSE viven en memoria del proceso; no escalar workers sin mover eso a otra parte.
- **React + Vite + CodeMirror 6**: bundle mucho más ligero que Monaco para un editor de un
  archivo; sin fuentes/CDN externos (autocontenido).
- **SSE en vez de WebSocket**: flujo unidireccional (metricas/estados/logs), reconexión
  automática de `EventSource`, menos partes móviles detrás de nginx.
- **Rutas relativas `/api`**: no hay URL horneada en el build del frontend (lección del
  despliegue de finanzas-app).
- **SQLite (WAL)**: historial de jobs. Sin Postgres/Redis nuevos.
- **Frontend estático servido por nginx** (en lugar de proxy a un proceso node en 5174):
  un proceso menos en un VPS con 2 vCPU; el puerto interno de ManimStudio es solo 3002.
- **Runner separado**: el proceso web NUNCA toca `docker.sock` (equivale a root). El runner
  (root) expone 4 comandos con validación regex estricta y solo sobre este compose file;
  `cancel` solo puede matar contenedores `manimstudio-render-*`.
- **Escenas por AST**: la lista de escenas del script se extrae con `ast.parse`, jamás
  ejecutándolo fuera del contenedor.

## Funcionalidades

### Biblioteca (pestaña «Biblioteca»)

- Grid de tarjetas de los renders exitosos: miniatura, escena, fecha, duración, calidad y
  tamaño; acciones **ver** (lightbox), **descargar** y **borrar** (confirmación en dos pasos).
- La miniatura la genera el runner al terminar cada render (`ffmpeg -frames:v 1` DENTRO del
  contenedor `manim-render`; el backend no tiene ffmpeg). Se sirve por
  `GET /api/jobs/{id}/thumb` con la misma defensa de path que `/video`.
- `DELETE /api/jobs/{id}` borra fila SQLite + directorio; los jobs activos devuelven 409
  (cancelar primero).
- **Acciones en lote** (botones de la pestaña Admin, todas devuelven el uso de disco actualizado):
  - `DELETE /api/jobs/failed` — purga todos los jobs `error`/`timeout`/`cancelled`.
  - `DELETE /api/jobs/older-than/{days}` — purga los jobs `done` con más de `days` días
    (rango 1–3650; fuera de rango → 422).
- **Cuota de disco**: `MS_MAX_STORAGE_MB` (default 2048). Si `render_jobs/` supera la cuota,
  crear un job responde **507** con mensaje claro; la barra de uso se muestra en la pestaña.
- El log de cada render se persiste como `render_jobs/<id>/render.log` al terminar (done,
  error y timeout) y sobrevive reinicios del backend: `get_logs` cae a ese archivo cuando el
  buffer en memoria ya no existe (el buffer se libera al terminar → sin fugas de memoria).

### Biblioteca de lecciones (pestaña «Aprender»)

- Contenido educativo en Markdown + frontmatter YAML, versionado en git (sin CRUD web) en
  `studio/content/lessons/<categoria>/<NN>-<slug>.md`. El orden de categorías y sus nombres
  legibles viven en `studio/content/lessons/categories.yaml`. Estado actual: **18 lecciones
  en 4 categorías** — Manim · Fundamentos (5), Intermedio (5), Primitivas del Estudio (5) y
  Flujo de trabajo (3). `categories.yaml` declara 17 categorías porque las de dominio
  (espacio, satélites, redes, IA…) siguen agrupando las animaciones de la pestaña
  «Animaciones»; aparecen vacías en «Aprender».
- Formato de archivo: frontmatter con `title`, `level` (`intro`/`medio`/`avanzado`),
  `summary`, `tags`, `minutes`, `order`; cuerpo Markdown con matemáticas en sintaxis KaTeX
  (`$…$` en línea, `$$…$$` en bloque). El `order` fija la posición dentro de la categoría.
- Endpoints (auth obligatoria):
  - `GET /api/lessons` — índice: categorías con sus lecciones (solo metadatos, sin cuerpo).
  - `GET /api/lessons/{categoria}/{NN-slug}` — detalle con el Markdown ya sin frontmatter.
- **Cache**: el índice se construye una vez y se guarda en memoria; se invalida solo cuando
  cambia el `mtime` más reciente del árbol de `lessons/` (editar/añadir/borrar un `.md` lo
  refresca en la siguiente petición, sin reiniciar). Ver `app/lessons.py` (`LessonStore`).
- **Seguridad**: el id de lección se valida con un regex estricto
  (`^[a-z0-9][a-z0-9-]*/[0-9]{2}-[a-z0-9][a-z0-9-]*$`) que impide cualquier path traversal;
  un frontmatter YAML corrupto degrada con gracia (título = id) sin tumbar el índice.
- El frontend renderiza el Markdown con `marked` + `dompurify` (sanitizado) y las fórmulas
  con `katex`; todo autocontenido, sin CDN. El lector añade ~270 KB min al bundle.

### Biblioteca de animaciones (pestaña «Animaciones»)

- Scripts Manim ejecutables en `studio/content/animations/<categoria>/<NN>-<slug>.py`,
  versionados en git. Comparten `categories.yaml` con las lecciones; el título y el orden
  se toman de la lección homónima cuando existe (si no, se derivan del slug).
- **Alta web** (auth obligatoria): desde la pestaña se pueden añadir secciones nuevas y
  animaciones a una sección; editar/borrar sigue siendo por git.
  - `POST /api/animations/categories` `{name}` — crea la sección: añade la entrada a
    `categories.yaml` (escritura atómica) y crea su directorio. 409 si el slug ya existe.
  - `POST /api/animations` `{category, title, script}` — valida el script por AST (debe
    definir al menos una escena; nunca se ejecuta) y escribe `<NN>-<slug>.py` con el
    siguiente `NN` libre. 404 si la sección no existe, 422 si el script no vale.
  - Los archivos creados quedan como *untracked* en el árbol de git hasta que se
    commiteen; el índice (`GET /api/animations`) los sirve al instante (cache por mtime).
- El índice marca cada categoría con `has_dir`: la pestaña muestra las que tienen
  animaciones o directorio propio (p. ej. recién creadas, aún vacías) y oculta las
  solo-lecciones del curso de Manim.
- Requiere que el servicio pueda escribir en `studio/content/animations` y
  `studio/content/lessons` (`ReadWritePaths` en la unit + ownership `manimstudio`).

### Monitoreo histórico (pestaña «Monitoreo»)

- Ring buffer en memoria (`deque`, ~30 min al intervalo configurado; 450 muestras a 4 s)
  alimentado por el mismo `_metrics_loop` del SSE. Cero procesos nuevos, cero disco.
- `GET /api/metrics/history` + gráficas SVG dibujadas a mano (sin librerías de charting):
  CPU, RAM y disco de los últimos 30 min, actualizadas en vivo por el SSE, con bandas
  doradas en los intervalos donde hubo un render activo.

### Proyectos (cursos) (pestaña «Proyectos»)

Agrupan varios renders (**clips**) en un curso con continuidad narrativa y estilo visual
compartido, y permiten exportar el resultado como un solo video sin salir de ManimStudio.

**Modelo:**

- **Proyecto**: `name`, `description`, `quality` (fija para todos sus clips, `ql`/`qm`/`qh`),
  `formato` (`horizontal` 16:9 · `vertical` 9:16 · `cuadrado` 1:1, también fijo para todos
  sus clips), `tipo` (`curso` o `promo` de redes) y `style_block` (código Python opcional que
  se antepone a cada clip antes de renderizar — imports, paleta de colores, helpers de
  continuidad…).
- **Clip**: pertenece a un proyecto, tiene `position` (orden dentro del curso), `title`,
  `script` (el código del clip, **sin** el estilo del proyecto), `scene` (nombre de la clase
  `Scene` a renderizar), `final_state` (nota de en qué queda la escena al terminar, visible
  como contexto para el clip siguiente) y `notes` libres.
- Cada clip enlaza como mucho a un job de render (`job_id`); su estado se deriva comparando
  el hash del contenido compuesto (ver abajo) contra `rendered_hash`.

**Reglas de continuidad y estilo:**

- **Calidad fija por proyecto**: todos los clips de un proyecto se renderizan a la misma
  calidad (`project.quality`); el Estudio no permite cambiarla mientras se edita un clip.
- **Formato del lienzo**: la calidad fija el **lado corto** y los fps; el formato fija la
  **proporción**. «1080p» son 1920×1080 en horizontal y 1080×1920 en vertical (fijar el
  *alto* daría 607×1080, que no es calidad alta sino un video pequeño). `projects.specs()`
  calcula la pareja y la API la publica en `GET /api/projects/{pid}` (`specs`).
  Calidad y formato quedan **bloqueados** en cuanto un clip tiene render vigente: mezclarlos
  dejaría videos de dos tamaños en el mismo curso (y un `concat -c copy` que no pega).
- **Quién aplica el lienzo**: la *escena*, no el runner. Un clip de curso 16:9 sale del flag
  `-q` de manim, como siempre. Un promo llama a `promo.formato()` en su bloque de estilo, y el
  runner le pasa al contenedor `PROMO_FORMATO`, `PROMO_CORTO`, `PROMO_LARGO`, `PROMO_FPS` y
  `PROMO_CALIDAD` (valores validados contra un conjunto y rangos cerrados). Por eso **el mismo
  código sale en 9:16 o en 16:9 cambiando el desplegable**, sin tocar una línea.
- **La resolución que se muestra es la medida**: al terminar un render, el runner mide el
  archivo con `ffprobe` y la guarda en `jobs.resolution`; la interfaz pinta miniaturas y
  reproductores con esa proporción (`formatos.js`). Si una escena no aplicó el formato pedido,
  se ve en la Biblioteca en vez de quedar tapado.
- **Estilo compuesto**: al renderizar, el backend antepone `style_block` al `script` del
  clip (`compose_script`) y detecta las escenas (`detect_scenes`) sobre ese script
  **compuesto**, no sobre el script crudo. Si el estilo ocupa `N` líneas, los mensajes de
  error de sintaxis/escena citan números de línea del compuesto — el Estudio muestra ese
  desfase (`style_offset`, vía `GET .../clips/{cid}/script`) junto a esos errores.
- **Stale (desactualizado)**: cada clip guarda `rendered_hash`, el hash de
  `style_block + script + scene` en el momento de su último render exitoso. Si cualquiera de
  los tres cambia (se edita el script del clip, su escena, o el estilo del proyecto), el hash
  actual ya no coincide y el clip pasa a `stale` — se resalta en la UI y puede
  re-renderizarse individualmente o con «Re-renderizar desactualizados» (que encola solo los
  que no tengan ya un render en curso).
- **Un render a la vez**: los renders de clips comparten la misma cola global que los renders
  sueltos del Estudio (`JobManager`, un worker); un clip con job `queued`/`running` no se
  vuelve a encolar hasta que termine.

**Endpoints** (todos `Depends(require_auth)`, prefijo `/api/projects`):

| Método | Ruta | Notas |
|---|---|---|
| GET | `` | lista con contadores (`clip_count`, `rendered_count`, `stale_count`) |
| POST | `` | crea proyecto (`name`, `description`, `quality`, `formato`, `tipo`, `style_block`); 422 si el formato o el tipo no existen |
| GET | `/{pid}` | detalle con clips ordenados y `specs` (resolución y fps reales del proyecto) |
| PATCH | `/{pid}` | edita nombre/descripción/calidad/formato/estilo (413 si `style_block` > 200 KB; 409 si se cambia calidad o formato con clips ya renderizados) |
| DELETE | `/{pid}` | borra proyecto y sus clips (no los jobs/videos ya generados) |
| POST | `/{pid}/clips` | crea clip; `from_job_id` adopta un job existente como ya renderizado *si* su calidad coincide con la del proyecto y el estilo compuesto es idéntico al script del job (en la práctica: proyecto sin `style_block`) |
| PATCH | `/{pid}/clips/{cid}` | edita `title`/`script`/`scene`/`final_state`/`notes` (413 si `script` > 200 KB) |
| DELETE | `/{pid}/clips/{cid}` | borra el clip (no el job/video que tuviera enlazado) |
| POST | `/{pid}/clips/{cid}/move` | reordena (`position`) |
| GET | `/{pid}/clips/{cid}/script` | `{script, style_offset}` — script crudo del clip (sin estilo) + líneas que antepone el estilo actual |
| POST | `/{pid}/clips/{cid}/render` | compone estilo+script, valida la escena y encola el render (201, devuelve el job); 422 si no hay escena asignada, si el script compuesto es inválido, o si la escena no existe en él |
| POST | `/{pid}/render-stale` | encola todos los clips `stale`/`no_render` sin job en vuelo; devuelve `{queued, skipped}` |
| GET | `/{pid}/export` | manifiesto JSON del curso (clips, orden, estado, sin campos internos) |
| GET | `/{pid}/archive` | ZIP con los videos vigentes + `concat.txt` + `manifest.json` + `LEEME.txt`; 404 si ningún clip tiene video vigente |

**Estudio en contexto de clip**: desde un proyecto, «Editar en Estudio» abre el script del
clip en el editor con un banner (`Proyecto · clip · calidad fija`) y botón «Salir del clip»
(vuelve al render libre sin tocar el script del editor). Mientras el contexto está activo:
la calidad queda fija a la del proyecto, «Guardar en clip» hace `PATCH .../clips/{cid}`
(`script`, `scene`) sin renderizar, y «Renderizar» guarda primero y luego llama a
`POST .../clips/{cid}/render` (en vez de `POST /api/jobs`) para que el render use el estilo
compuesto del proyecto.

**Biblioteca → Proyectos**: cada video renderizado tiene un botón «Añadir a proyecto…» que
crea un clip en el proyecto elegido a partir de ese job (`from_job_id`). Al borrar un video
que es el render vigente de un clip, la confirmación avisa de que el clip se queda sin video
(el clip en sí no se borra, solo pierde su render).

### La película del curso (panel «La película» en un proyecto)

Desde el sprint E1 el curso completo se monta **dentro de la app**: los clips en orden, su
narración pegada y, si se quieren, el intro y el cierre de marca, en un solo `pelicula.mp4`.
Detalle completo y decisiones en `ESTUDIO-V2.md`.

- **Quién monta**: `studio/tools/ensamblar.py` dentro del contenedor manim (el único sitio con
  ffmpeg), disparado por el comando `ensamblar` del runner. Del exterior solo llega un
  `project_id` validado con regex — mismo patrón que `postproceso` y `verificar`. El plan lo
  escribe el backend en `exports/peliculas/<project_id>/plan.json`, y ese directorio es lo
  único montado con escritura.
- **Empalme**: `corte` (por defecto) une con `concat -c copy` y tarda **segundos**, porque el
  vídeo se copia. `fundido`, `negro`, `blanco`, `deslizar`, `barrido` y `disolver` pasan por
  `xfade` y **recodifican la película entera**: en el VPS, decenas de minutos para un curso de
  media hora. La interfaz lo avisa antes de montar.
- **La voz** usa la misma lógica que `mux.sh`: `apad` + `-shortest` si cabe, `atempo` con tope
  1.15 si no. Una pieza sin narración recibe pista de silencio — un `concat` que mezcla clips
  con y sin audio sale mudo desde el primero sin pista, sin fallar.
- **La marca** son dos renders más del proyecto «Marca…»; se valida que su resolución medida
  coincida con la del curso.
- **Caducidad**: `pelicula.json` guarda el hash del plan (nombre, resolución, fps, empalme y el
  **mtime** de cada vídeo y wav). Estados: `sin_clips` · `faltan_renders` · `sin_montar` ·
  `desactualizada` · `al_dia` · `montando`.

| Método | Ruta | Notas |
|---|---|---|
| GET | `/api/projects/{pid}/pelicula` | estado, opciones, piezas e informe medido |
| POST | `/api/projects/{pid}/pelicula` | monta en segundo plano (202); 409 sin material o con otro montaje en curso |
| POST | `/api/projects/{pid}/pelicula/cancel` | corta el montaje |
| GET | `/api/projects/{pid}/pelicula/video` | el mp4, con soporte de Range |
| DELETE | `/api/projects/{pid}/pelicula` | borra la película, no el material |

Operación: `exports/` necesita `ReadWritePaths` en la unidad del backend y `exports/peliculas/`
debe ser del usuario `manimstudio` — el contenedor corre con ese uid y `cap_drop: ALL` le quita
a root el `CAP_DAC_OVERRIDE` que le dejaría escribir en un directorio ajeno.

**Flujo de unión externa** (sigue disponible; es lo que hace el ZIP, y no necesita el servidor):

1. Renderizar todos los clips del proyecto (individualmente o con «Re-renderizar
   desactualizados»).
2. Descargar el curso: botón «Descargar curso (.zip)» → `GET /api/projects/{pid}/archive`.
3. Dentro del ZIP, unir los clips en orden con ffmpeg (copia sin recodificar):

   ```bash
   unzip curso.zip -d curso/
   cd curso/
   ffmpeg -f concat -safe 0 -i concat.txt -c copy curso.mp4
   ```

   `concat.txt` ya trae los archivos en el orden del proyecto; `-c copy` es posible porque
   todos los clips de un proyecto comparten calidad (mismo códec/resolución).

### Audio de los promos (botón «Audio» en un proyecto de tipo promo)

Un promo de redes no lleva subtítulos: si no suena, no comunica. Este camino monta la
**cama de sonido** y la **voz** sobre el video, dentro de la app (antes se hacía fuera, a
mano, con `studio/tools/sfx.py`).

- **Manifiesto por clip** (`clips.audio_json`, misma forma que el `promo.json` de los promos
  escritos a mano): eventos `[sonido, t, dB]` y frases `[t_inicio, texto]`. Los sonidos son
  los de `PALETA` en `sfx.py` — la UI los ofrece en un desplegable y `test_audio_promo.py`
  compara las dos listas leyendo el archivo, para que no se separen en silencio.
- **Avisos calculados** (no bloquean, se enseñan siempre): cuánta voz cabe entre dos
  `t_inicio` a **2.45 sílabas/s** (medido con Charon sobre los diez primeros promos) y si la
  voz termina a menos de **0.6 s** del final — en ese caso el salto del bucle se oye.
- **Voz**: reusa `narracion.sintetizar()` con el texto escrito a mano, **sin** pasar por el
  guion de Gemini, y se sintetiza contra `duración − 0.6 s` para que calle antes del último
  frame. Se cachea por el hash del bloque `voz` (`voz.hash` en el directorio del job): mover
  un sonido de la cama no vuelve a gastar TTS. Mismo feature-flag que el asistente.
- **Mezcla**: el runner corre `sfx.py promo` dentro del contenedor manim (comando
  `postproceso`, calcado de `thumbnail`: rutas fijas, solo recibe el `job_id`). El resultado
  es `promo_audio.mp4` **al lado** del mudo: re-mezclar no obliga a re-renderizar.
- **Lo que sirve la app**: `GET /api/jobs/{id}/video` devuelve el sonorizado si existe (la
  Biblioteca marca «con sonido»), y si falta vuelve al mudo sin romperse.
- **Estado**: `sin_manifiesto` · `sin_render` · `sin_mezclar` · `desactualizado` (cambió el
  manifiesto o el video) · `al_dia`. Sale en el botón del clip y en el panel del proyecto.

| Método | Ruta | Notas |
|---|---|---|
| GET | `/api/projects/{pid}/clips/{cid}/audio` | manifiesto + estado + avisos + duración real del video |
| PUT | `/api/projects/{pid}/clips/{cid}/audio` | guarda el manifiesto (422 si un sonido no existe o un nivel se sale de rango) |
| POST | `/api/projects/{pid}/clips/{cid}/audio/mezclar` | sintetiza la voz si hace falta y mezcla (409 sin render, 503 sin Vertex si hay frases) |

Los tres responden 409 en un proyecto que no sea `tipo='promo'`: un curso se narra desde
«Generar narración», que es otro camino y otro formato.

### Importar los promos del repo (`subir_promo.py`)

Los diez promos escritos a mano viven en `studio/content/promos/<slug>/` (`promo.json` +
`style_block.py` + `escena.py`). `studio/tools/subir_promo.py` los mete en la base del Studio
usando los mismos módulos que la API, sin pasar por HTTP — hermano de `subir_curso.py`:

```bash
studio/backend/venv/bin/python studio/tools/subir_promo.py --todos --dry-run
studio/backend/venv/bin/python studio/tools/subir_promo.py --todos
```

Cada promo entra como un proyecto de **un clip**, `tipo='promo'`, vertical y `qh`, y **con su
audio**: los bloques `audio` y `voz` del `promo.json` se guardan como manifiesto del clip,
listos para mezclar desde la interfaz. El nombre lleva el prefijo `Promo · `, así que el
índice los agrupa juntos (agrupa por lo que hay antes del `·`) y el grupo se cuenta en
«promos», no en «lecciones».

Es idempotente (empareja por nombre exacto): crea lo que falta, actualiza lo que cambió y
avisa de lo que queda `stale` o con la mezcla vieja. No borra nada ni toca renders.

### Verificación de un promo (botón «Verificar»)

Un promo se juzga por cuatro cosas y ninguna se ve mirando el vídeo una vez. La app las
**mide sobre el archivo que sirve** (el sonorizado si ya se mezcló) y enseña los números:

- **La costura del bucle** — el último frame tiene que ser el primero, y se compara **contra
  el suelo del códec**: dos frames que en la escena son el mismo dibujo no salen idénticos
  del h264 (en fondo plano y oscuro la cuantización llega al 0.18 % de los subpíxeles). Sin
  descontar ese suelo, un bucle perfecto parece sucio. Se enseña el exceso sobre el suelo.
- **La duración** — 8-15 s (`audio_promo.DUR_MIN/MAX`, los mismos números que usa la
  herramienta; un test compara las dos parejas leyendo el archivo).
- **El audio** — que exista, a qué pico suena y que los dos extremos estén en silencio. Los
  extremos se miden **en las muestras**, no con `volumedetect`: una ventana de 50 ms arrastra
  el frame AAC entero y acusa de ruidoso un arranque que en las muestras es cero exacto.
- **Los frames** — una tira equiespaciada y el par primero|último uno al lado del otro.
  Mirarlos es la costumbre que caza lo que ningún número dice (un elemento fuera del lienzo,
  dos cifras que se leen pegadas).

La medición vive en `studio/tools/promo_verifica.py` — **una sola implementación**, que usan
tanto el CLI local (`render_promo.py`) como el runner dentro del contenedor (comando
`verificar`). El informe se guarda en `jobs.verify_json` y **caduca solo**: si se vuelve a
renderizar o a mezclar, el estado pasa a «verificación vieja» en vez de enseñar números de
otro archivo.

| Método | Ruta | Notas |
|---|---|---|
| POST | `/api/projects/{pid}/clips/{cid}/verificar` | mide y guarda el informe (409 sin render vigente) |
| GET | `/api/jobs/{job_id}/verificacion/{archivo}` | PNG del informe; el nombre va contra un conjunto cerrado (`primero`, `ultimo`, `costura`, `fNN`) |

Mezclar el audio dispara la verificación al terminar: recién mezclado es cuando el informe
anterior deja de valer.

### Asistente IA (Vertex AI · Gemini 2.5 · us-central1)

- Feature-flag: si no existe `studio/backend/gcp-key.json` (service account GCP, chmod 600,
  SIEMPRE en .gitignore), la app funciona igual y la UI de IA se oculta (`/api/me` →
  `ai_enabled`).
- Endpoints (auth obligatoria, ~10 req/min, script/logs truncados a un presupuesto fijo):
  - `POST /api/ai/explain` — log + script → explicación breve del fallo en español
    (`MS_GEMINI_MODEL_FAST`, gemini-2.5-flash).
  - `POST /api/ai/fix` — script + error → script corregido completo; la UI muestra un diff
    y el botón «Aplicar al editor» (`MS_GEMINI_MODEL_DEEP`, gemini-2.5-pro).
  - `POST /api/ai/generate` — descripción en lenguaje natural → script manim.
- UI: botón «✨ Explicar error» en el panel de registro cuando un job falla, y drawer
  «✨ Asistente» con las 3 acciones.
- **Nunca se auto-renderiza** el código de la IA: pasa por el mismo pipeline (validación
  AST → sandbox sin red) que el código escrito a mano.

### Narración de cursos (botón «Generar narración» en Proyectos)

- Guion cronometrado con `gemini-2.5-pro` (secciones con `t_inicio`/`t_fin` leyendo los
  `run_time`/`wait` del script compuesto) y voz con `gemini-2.5-flash-preview-tts`
  (Vertex, misma service account del asistente; sin `gcp-key.json` la función se oculta).
- El audio se **alinea a las secciones**: cada una se sintetiza aparte, se recorta su
  silencio inicial/final y se coloca en su `t_inicio` (hueco máximo 2.5 s, cascada si la
  anterior se pasa).
- **Que quepa en el video** (tolerancia +5 %) se ataca en tres niveles, de menos a más
  invasivo: 1) los silencios entre secciones se comprimen por búsqueda binaria hasta el
  máximo que aún cabe (`_ajustar_al_limite`, no toca la voz); 2) hasta
  `MAX_INTENTOS_GUION` guiones, cada uno con menos palabras en proporción a lo que se
  pasó, **conservando el intento que mejor encaja** —no el último, que el TTS varía—;
  3) si aun así se pasa, `mux.sh` lo acelera con `atempo` al montar. Ninguna de las tres
  recorta la narración.
- Salida en `guiones/<slug-proyecto>/NN-slug.{md,txt,wav,secciones.json}` + `estado.json`
  (hash de script compuesto+escena+duración+voz → detecta narraciones desactualizadas).
- API: `GET/POST /api/projects/{pid}/narracion` (estado por clip / corrida en segundo
  plano, una a la vez), `POST .../narracion/cancel`, `GET .../narracion/{cid}/{audio,texto}`.
- El zip de `GET /api/projects/{pid}/archive` incluye los `.wav`/`.txt` emparejados con
  cada mp4, `mux.sh` y el estado de narración en `manifest.json`. `mux.sh` mide con
  `ffprobe`: si la voz cabe, `apad -shortest` (cada clip conserva su duración exacta y el
  concat no se desincroniza); si no cabe, `atempo` con el ratio justo (tope 1.15, preserva
  el tono) para no perder la cola de la narración. La lista de concat se **copia dentro de
  `con_audio/`**: ffmpeg resuelve las rutas relativas de un `concat.txt` contra el
  directorio del archivo, no contra el cwd — leerla desde `../` concatenaba los mp4
  originales y el curso salía mudo sin que nada fallara.
- CLI equivalente: `studio/tools/guiones.py` (`--solo-guion`, `--solo-audio`, `--voz`,
  `--force`); comparte la lógica de `app/narracion.py`.
- Operación: la unidad systemd necesita `ReadWritePaths` sobre `guiones/` y el directorio
  debe ser del usuario `manimstudio` (mismo patrón que Animaciones).

### Identidad CO.DE Academy en los videos

**Es el mínimo visual del canal, no una opción.** Todo render sale con la marca:
`JobManager.create_job` pasa el script por `app/branding.py` antes de escribir
`scene.py`, así que un clip de curso, un render suelto de la Biblioteca y un
re-render de código viejo salen los tres marcados sin tocar su código.

- El bloque se **anexa al final** del script, nunca al principio: manim importa el
  módulo entero antes de instanciar la escena, así que `marcar_escenas(globals())`
  alcanza a todas las clases ya definidas **y los números de línea de un error
  siguen siendo los del código del autor** (anteponer los correría).
- Se salta si el script ya menciona `code_brand`: los cursos con su propia base de
  marca en el `style_block` se respetan tal cual, sin duplicar la marca de agua.
  `marcar_escenas` es idempotente por su parte (marca `_code_brand` en la clase, que
  las subclases heredan).
- Va en `try/except`: si la extensión no estuviera montada, el render sale sin marca
  con un aviso en el log, pero sale. La marca no puede tumbar la cola.
- Lo que se guarda en la DB es el script del autor sin tocar; la marca es del render.
- El fondo de marca solo se impone si el script no eligió el suyo (si sigue en el
  negro por defecto de Manim).
- El asistente Gemini la tiene como regla en `conocimiento.py` (paleta, tipografías,
  `titulo_marca`/`etiqueta_hud`/`Rotulos`) y en los prompts de generar/corregir de
  `ai.py`: no puede quitarla al arreglar un script ni inventar otra paleta.

- `studio/content/manim_extensions/code_brand.py`: paleta oficial (fondo `#05070a`,
  ámbar `#f59e0b`), tipografías propias Rajdhani/Space Mono (OFL, en `fonts/`, registradas
  en Pango en runtime dentro del contenedor), `marca_agua()` sutil con z_index alto,
  `esquinas_hud()`, y `Rotulos` (rótulos por zona que se relevan con fundido, sin
  encimarse). Los cursos la activan en su `style_block` con una sombra de `Scene`.

## Operación

```bash
systemctl status manimstudio-backend manimstudio-runner   # estado
journalctl -u manimstudio-backend -f                      # logs API
journalctl -u manimstudio-runner -f                       # logs renders/docker
systemctl restart manimstudio-backend                     # reinicio (jobs activos → error)
```

- Config del backend: `EnvironmentFile=/etc/manimstudio/env` (chmod 640, `root:manimstudio`),
  fuera del árbol del repo (ver `.claude/skills/manimstudio/SKILL.md`).
- `MS_DEFAULT_TIMEOUT=1200` en ese env (2026-08-05): los clips con `ImageMobject` a
  pantalla completa (fractales) renderizan a ~2.5 fps en Cairo y un clip de ~50 s
  no cabía en los 600 s por defecto. El contenedor sigue capado a 1.5 vCPU, así que
  el cambio solo alarga la espera permitida, no la carga.
- Librerías de animación propias en `studio/content/manim_extensions/`: `fractales.py`
  (ver `FRACTALES.md`) y `satelites.py` — constelaciones Walker/NTN, mapa mundial y
  cobertura raster, visuales de RL (ver `SATELITES-IA.md`). Cursos que las usan:
  «Fractales» y «Satélites e IA» en la pestaña Proyectos.

### Autenticación y cambio de contraseña

- **Usuario único** fijado por `MS_ADMIN_USER` en `/etc/manimstudio/env` — cambiarlo exige
  editar el archivo y `systemctl restart manimstudio-backend`.
- **Password mutable en runtime**: vive en la fila única de la tabla `auth` de la DB
  (`app/db.py`), no en el env. `MS_ADMIN_PASSWORD_HASH` solo actúa como semilla la primera
  vez que arranca el backend (`db.ensure_auth_seed`); tras eso la DB manda.
- **Cambio de password desde la UI**: `POST /api/change-password` (autenticado) con
  `current_password` + `new_password` (mínimo 8 caracteres, distinta de la actual).
  `app/auth.py::change_password` reverifica la actual con bcrypt antes de guardar la nueva.
- **Forzar el cambio en el primer login de una cuenta nueva**: poner a mano
  `must_change_password=1` en esa fila (p. ej. `Database.set_password(hash, True)`, o UPDATE
  directo). Un middleware en `main.py` (`_enforce_password_change`) bloquea con 403
  `PASSWORD_CHANGE_REQUIRED` toda la API bajo `/api/` salvo login/logout/me/change-password/
  health mientras el flag siga activo; el frontend muestra `ChangePassword.jsx` en vez de la
  app hasta que se limpia. Restablecer el hash sin querer forzar el cambio:
  `venv/bin/python -c "import bcrypt;print(bcrypt.hashpw(b'NUEVA', bcrypt.gensalt(12)).decode())"`
  → `Database(...).set_password(hash, must_change_password=False)`.
- Rebuild frontend: `cd studio/frontend && npm ci && npx vite build` (nginx sirve `dist/` al instante).
- Artefactos de renders: `render_jobs/<job_id>/` (script + media + thumb.jpg + render.log).
  Limpieza normal: pestaña Biblioteca (o `DELETE /api/jobs/<id>`); borra fila + directorio.
- Tests: `cd studio/backend && source venv/bin/activate && python -m pytest tests/`
  (los tests de IA mockean el cliente Vertex: jamás llaman a la API real).
- Credenciales IA: `studio/backend/gcp-key.json` (600, manimstudio). El `project_id` se lee
  del propio JSON; ubicación fija `MS_GCP_LOCATION=us-central1`, solo modelos Gemini 2.5.
- El vhost activo es un symlink: `/etc/nginx/sites-enabled/coderesearch_space →
  studio/deploy/coderesearch.space.nginx`. Tras editar: `nginx -t && systemctl reload nginx`.

## Límites conocidos

- Un job a la vez por diseño (2 vCPU compartidas con ~19 contenedores de producción).
- Rate-limit de login en memoria: se reinicia con el proceso (aceptable, single-user).
- Si el backend se reinicia en medio de un render, el job se marca `error` y el runner/
  contenedor se limpia al cerrarse la conexión.
- El video se sirve por FastAPI (FileResponse con soporte Range); suficiente para un usuario.
- El historial de métricas vive en memoria: se pierde al reiniciar el backend (por diseño:
  cero almacenamiento en disco para métricas).
- El rate-limit del asistente IA es un único cubo en memoria (app de sesión única).
- Los renders corren como uid `manimstudio` dentro del contenedor (`--user` del runner);
  los jobs anteriores a este cambio quedaron root y se normalizaron con `chown` una vez.
