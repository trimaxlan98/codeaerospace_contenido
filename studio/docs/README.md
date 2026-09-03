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
                                        render/cancel/thumbnail/frames/fotograma/
                                        ejecutar/stats/ping + los de audio y montaje)
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
  (root) expone un puñado de comandos con validación regex estricta y solo sobre este compose
  file; `cancel` solo puede matar contenedores `manimstudio-render-*`. **Ninguno acepta una
  ruta del exterior**: todas se derivan de un id validado (el nombre del PNG de una figura lo
  compone el propio runner a partir de `t` y `ancho`).
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
  sus clips), `tipo` (`curso` o `promo` de redes), `estilo` (el nombre del estilo visual —
  `lienzo`— cuando el manifiesto del curso lo declara; no se puede deducir del código) y
  `style_block` (código Python opcional que se antepone a cada clip antes de renderizar —
  imports, paleta de colores, helpers de continuidad…).
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
| POST | `/{pid}/render-lote` | lote de renders: `{clips: [ids]｜null, calidad: ql/qm/qh｜null, force}` → `{queued, lote_id, saltados, calidad, calidad_cambiada}`; 409 si se cambia la calidad con `clips` elegidos a dedo |
| GET | `/{pid}/lote` | progreso agregado del lote vigente: `{total, hechos, fallidos, en_curso, pendientes, media_s, eta_s, derivado}` o `{lote: null}` |
| POST | `/{pid}/duplicar` | `{name}` → copia el proyecto y sus clips **sin** los renders (201); 409 si el nombre ya existe |
| POST | `/{pid}/clips/{cid}/duplicar` | inserta la copia justo detrás, con título «… (copia)» (201) |
| POST | `/importar` | importa un curso-como-archivos (ver abajo); `?dry_run=1` valida sin escribir |
| GET | `/importables` | los slugs que hay en `studio/content/{cursos,verticales,promos}/` |
| GET | `/{pid}/export` | manifiesto JSON del curso (clips, orden, estado, sin campos internos) |
| GET | `/{pid}/fuentes.zip` | las **fuentes** del proyecto: `curso.json` + `style_block.py` + `clips/NN-*.py` + `guiones/NN-*.{secciones.json,txt}` |
| GET | `/{pid}/archive` | ZIP con los videos vigentes + `concat.txt` + `manifest.json` + `LEEME.txt`; 404 si ningún clip tiene video vigente |

**Un proyecto es un directorio** (sprint R3a): un curso vive igual de bien en la base y en
git, y se pasa de una a otro sin salir de la app.

- **Exportar** — «Fuentes (.zip)» en el detalle del proyecto (`GET /{pid}/fuentes.zip`). No
  lleva vídeos (para eso está «Descargar curso»): lleva `curso.json`, `style_block.py`, un
  `.py` por clip y, si los hay, los guiones. Es **el mismo esquema que lee `subir_curso.py`**,
  así que se puede versionar en `studio/content/cursos/<slug>/` tal cual. El zip es
  determinista (sin compresión, fecha fija en cada miembro, orden fijo): exportar dos veces
  el mismo proyecto da **los mismos bytes**.
- **Importar** — «Importar…» en la lista de proyectos (`POST /importar`), por dos puertas:
  un **.zip de fuentes** (cuerpo crudo `Content-Type: application/zip`, ≤ 5 MB) o un
  **directorio del repo** (`{"slug": "...", "origen": "cursos"｜"verticales"｜"promos"}`, leído
  de `MS_CONTENT_DIR`, por defecto `studio/content/`). El slug se valida contra un regex
  cerrado (minúsculas, dígitos y guiones) y la ruta resuelta se comprueba dentro de su origen.
  Un **vertical** convierte cada pieza (`clip.json` + `escena.py`) en un clip: su bloque
  `audio`/`voz` va al manifiesto de audio del clip, y `modulo` + `duracion_objetivo` a sus
  notas. **Idempotente por nombre exacto** y por posición de clip, igual que el CLI: crea lo
  que falta, actualiza lo que cambió y **nunca borra**. «Comprobar» es el `--dry-run`.
- **La misma lógica que la terminal**: `app/importar.py` es el único sitio donde se lee un
  curso-como-archivos; `subir_curso.py` y `subir_promo.py` son envoltorios suyos.

**Render en lote** («Render en lote…», `POST /{pid}/render-lote`): encola varios clips en
orden en la cola de siempre (un render a la vez), saltando los que estén al día —salvo
`force`— y los que ya tengan un render en vuelo. Como **la calidad es del proyecto**, pedir
otra la cambia en el proyecto *antes* de encolar y lo dice en la respuesta
(`calidad_cambiada`); eso rehace el curso entero, así que con `clips` elegidos a dedo se
responde 409 en vez de dejar vídeos de dos tamaños. `GET /{pid}/lote` da el progreso agregado
(hechos/total, fallidos, ETA con la duración media de los renders `done` de ese proyecto) y
sobrevive a un reinicio del backend: si el estado en memoria se perdió, el lote se **deriva**
de los jobs del proyecto (los activos y todo lo encolado desde el primero de ellos).
«Re-renderizar desactualizados» usa este mismo endpoint.

**Duplicar**: «Duplicar proyecto» copia estilo compartido, formato, calidad, fondo y todos los
clips (script, escena, `final_state`, notas y manifiesto de audio); «Duplicar» en un clip
inserta la copia justo detrás. **En ninguno de los dos se copia el render**: un vídeo es de un
solo clip, y dos clips apuntando al mismo job harían que borrarlo dejase sin vídeo a un
proyecto que nadie estaba tocando.

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

**Medición**: la unión puede salir mal **sin fallar** (un offset de `xfade` que deja una pieza
fuera da un mp4 bien formado y más corto; un `concat` con audios distintos enmudece a mitad).
`POST /api/projects/{pid}/pelicula/verificar` mide la película contra su plan —duración con
±0,5 s de tolerancia, sonido **pieza a pieza** y resolución— y se dispara sola al terminar de
montar. Solo se acusa a las piezas que **traían** sonido: un curso sin narrar es mudo a
propósito. El informe vive en `pelicula.json` con el mismo hash que el montaje, así que
volver a montar lo deja en «medición vieja» en vez de enseñar números de otra película.

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

### Piezas de simulación (plantilla «Pieza de simulación»)

Al crear un proyecto, la plantilla **«Pieza de simulación»** deja listo un clip donde
**el fotograma entero lo calcula numpy en el render**: miles de agentes o una malla de
cientos de miles de celdas, presentados a pantalla completa, con la cámara siguiendo a un
agente y la cifra medida abajo. Nace en `vertical` y calidad `qh`, pero el lienzo lo elige
el proyecto: el mismo código sale en 9:16 y en 16:9 sin tocar una línea.

Lo sostiene el paquete `studio/content/manim_extensions/emergencia/` — el núcleo
`Pelicula` (la pila de fotogramas como `ImageMobject` animado) y **trece simuladores**:
bandada, moho, arena, vida, turing, ondas, chladni, ising, pendulos, cuencas, epiciclos,
rio y galaxias. Todos devuelven lo mismo (`frames`, `cifras`, `extra`), así que cambiar
`em.bandada` por `em.rio` en el clip es una línea.

Dos cosas que conviene saber antes de darle a Render:

- **Cuesta.** La simulación va aparte del render (la plantilla arranca con `pasos=420`
  para que la vista previa sea rápida) y el render de una pieza larga en `qh` va a
  ~0.29 s/frame. En el VPS eso son horas: **los `qh` de piezas con película se hacen en
  local** con `studio/tools/render_vertical.py`, como los cursos verticales.
- **La cifra no se inventa.** Lo que aparece en cian sale de `cifras`/`extra` de ese
  render; lo que venga de literatura va en gris. La sonda `studio/tools/sonda_emergencia.py`
  comprueba los invariantes físicos de los trece simuladores (hoy: 36 ok, 0 fallos).

La guía completa de la librería, con la API y las trampas medidas, está en
[`studio/docs/EMERGENCIA.md`](EMERGENCIA.md). El curso 29 «Emergencia» es el ejemplo
grande: 16 piezas en `studio/content/verticales/emergencia/`.

### Cama de sonido (botón «Audio» en cualquier clip)

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

**Desde el sprint E3 la cama también es de los cursos**, con una regla que manda sobre todo
lo demás: **un clip de curso no lleva voz aquí**. Su narración sale de «Generar narración» y
la película la pega al montar; un manifiesto de curso con frases es un **error 422**, no un
aviso — aceptarlo pegaría dos voces sobre el mismo clip. Lo que cambia por tipo:

| | promo | curso |
|---|---|---|
| voz en el manifiesto | sí | no (422) |
| pico por defecto de la cama | −3 dB | **−16 dB** (nace bajo la voz) |
| avisos | bucle, frases que se empujan, cola de silencio | cama que compite con la voz, sonidos fuera del clip |
| verificación | sí | 409 (mide la costura del bucle y 8-15 s, que en un curso no existen) |

La película usa el mp4 **que la app sirve** (el sonorizado si existe) y, cuando además hay
narración, **mezcla** las dos pistas (`amix`) en vez de reemplazar la cama por la voz.

### Banco de sonidos audible (`/api/sfx`)

Los 18 efectos de `sfx.py` se elegían a ciegas, por su nombre. `sfx.py paleta` los sintetiza
como wavs sueltos en `exports/sfx/` (comando `paleta` del runner: el backend no tiene numpy),
y el diálogo de audio los reproduce con un ▶ por línea. La síntesis es determinista: se
generan una vez y no caducan.

| Método | Ruta | Notas |
|---|---|---|
| GET | `/api/sfx` | la paleta, cuáles están listos, si está completa |
| POST | `/api/sfx` | sintetiza (409 si ya se está sintetizando) |
| GET | `/api/sfx/{nombre}` | el wav; el nombre va contra el conjunto **cerrado** de la paleta |

El listado cruza el directorio con la paleta viva: `exports/sfx/` sobrevive a los cambios de
`PALETA` y una corrida vieja deja efectos que ya no existen.

### Música procedural (`musica.py` y `/api/musica`)

Hasta el sprint R2 la app no tenía música: `unir_vertical.py --mudo` existe *precisamente*
porque el dueño se la ponía fuera. `studio/tools/musica.py` sintetiza **ocho temas** con
numpy —sin un solo asset, con semillas fijas, determinista al byte— dentro del contenedor de
render. Cada tema declara raíz, progresión de acordes por grados, bpm y el nivel de sus tres
capas: **drone** (pad aditivo por nota del acorde), **arpegio** (Karplus-Strong en las
subdivisiones del pulso) y **sub-bajo** (senoidal articulado a cada tiempo, que es lo que da
el pulso medible). Todo por debajo de ~950 Hz: «espacial pero tranquilo», el criterio que el
dueño verificó para la marca. Medido en los ocho, a 12 s y a 37,3 s: duración exacta al
sample, pico ≤ −3 dBFS, **95,4–99,8 %** de la energía bajo 300 Hz, **99,8–100 %** bajo 950, y
el bpm reconocible por autocorrelación con ≤ 2,2 % de error.

`tema(nombre, dur)` dura exactamente lo que se le pide y termina con una caída suave —lo que
mantiene mudos los extremos de un promo en bucle—. `escribe_cama()` la escribe por bloques de
90 s sobre el reloj absoluto, para que una película de media hora no pida más de un giga de
FFT.

Dónde entra:

- **manifiesto de una pieza**: `audio.musica = {tema, db, bpm?}`. `sfx.promo()` suma la cama
  **antes** del `_norm` a `pico_db`, así que el pico final no se mueve (medido sobre el promo
  de filotaxis: −3,0 dBFS con y sin música). Por encima de **−21 dB** salta un aviso: ahí la
  voz deja de quedar los 12 dB por encima que pide la casa (medido: 15,0 dB de separación con
  la cama en −24, 9,0 en −18).
- **película del curso**: `plan.json` acepta `musica: {tema, db}` global. `ensamblar.py` mide
  el montaje, saca la envolvente de la voz y sintetiza la cama de esa duración con el
  *ducking* ya aplicado: −9 dB donde hay voz, ataque 0,12 s, liberación 0,60 s.
- **banco audible**: `musica.py banco` deja una vista previa de 12 s por tema en
  `exports/musica/` (comando `musica` del runner, calcado de `paleta`).

| Método | Ruta | Notas |
|---|---|---|
| GET | `/api/musica` | los temas con bpm, carácter y descripción, y cuáles están listos |
| POST | `/api/musica` | sintetiza el banco (409 si ya se está sintetizando) |
| GET | `/api/musica/{tema}` | el wav; el nombre va contra el catálogo **cerrado**, igual que en SFX |

`MusicaSelector.jsx` es el mismo control en los dos sitios: el diálogo de audio de un clip y
el panel de la película.

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

### Fotogramas de un render: hoja de contactos y figura (sprint R3b)

Hasta R3b el único resultado de un render en la app era el mp4. En la terminal el bucle es
otro: `render_local.py --frames 8` deja los PNG y **se miran uno a uno** antes de dar un clip
por bueno —la regla dura del proyecto es que nada quede encimado, y eso no lo dice ningún
número—; y cuando una figura tiene que entrar en la tesis se saca un `ffmpeg -ss` a mano.

- **Hoja de contactos** (botón bajo el vídeo, en el Estudio y en el modal de Renders): N
  fotogramas equiespaciados en `t = dur·(i+½)/N` —el mismo reparto que `render_local.py`, que
  evita los fundidos de los extremos— **más el último fotograma real**, que va aparte y
  destacado porque es el que cierra la pieza (y el que empalma con la siguiente en un
  vertical). 480 px de ancho; cada miniatura lleva su instante encima y se amplía al pulsar.
- **Fotograma → PNG**: el instante que se está viendo (`currentTime` del `<video>`) a 1920,
  2560 o 3840 px, descargado al momento. Es la salida estática para una figura de paper o de
  tesis: el vídeo está a la calidad con que se renderizó, pero el PNG se pide al ancho que
  necesita la página.

La extracción vive en `studio/tools/hoja_contactos.py` — **una sola implementación**, un
contenedor por hoja (no uno por fotograma: arrancar `docker compose run` cuesta ~1,5 s) y un
informe JSON, igual que `promo_verifica.py`.

| Método | Ruta | Notas |
|---|---|---|
| POST | `/api/jobs/{id}/frames` | `{n: 1..24}`. **Idempotente**: si el índice de esa `n` ya está en disco con todos sus PNG, devuelve `recalculada: false` sin arrancar contenedor (el mp4 de un job es inmutable). 409 si el job no tiene vídeo |
| GET | `/api/jobs/{id}/frames/{archivo}` | `NN.png` o `final.png`, conjunto cerrado y misma defensa de path que `/thumb` |
| POST | `/api/jobs/{id}/fotograma` | `{t, ancho: 320..3840, formato: "png"}` → `{archivo, url, ancho, alto, bytes}` |
| GET | `/api/jobs/{id}/figuras/{archivo}` | `t<ms>_<ancho>.png`; el nombre lo **deriva el runner**, y el regex se vuelve a exigir aquí |

**Dos trampas medidas**: un `-ss` al filo de la duración *sale con éxito sin escribir nada*, y
el navegador manda justo ese instante al terminar el vídeo (`currentTime == duration`), así
que la cola final se atiende con `-sseof -0.4 -update 1`; y `scale=3840:-2` sobre un 854×480
da **2158** de alto, no 2160 — la resolución que se enseña es la medida sobre el PNG escrito,
no la que se pidió.

### Laboratorio: Python de validación en el sandbox (`#/laboratorio`, sprint R3b)

Las **sondas** (`studio/tools/sonda_*.py`) son el guardián de cada librería del repo: cada
invariante con su contraejemplo y una tabla de cifras medidas. Se corrían sólo desde una
terminal; en la app no había forma de «verificar la librería» antes de escribir un clip, ni de
calcular una cifra con numpy, ni de dibujar un PNG con PIL.

- Editor CodeMirror (Python, con el tema de la app) y **`Ctrl+Enter` para ejecutar**. La
  plantilla de partida usa numpy, una librería del repo y PIL, que es exactamente lo que hay a
  mano. El script se guarda en `localStorage`, como el del Estudio.
- Panel de salida con `stdout`/`stderr`, y **galería de lo que produjo**: los PNG se ven ahí
  mismo, los WAV se oyen, el resto se descarga.
- **Sondas del repo** con un botón «Correr» cada una. Se ejecuta el archivo del repo montado
  read-only, no una copia: si mañana cambia, el botón corre la versión nueva.
- Historial de las últimas 30 ejecuciones, con el **veredicto** (la última línea útil de la
  salida: «73 invariantes ok, 0 fallos») sin abrir la ejecución.

**Las garantías son las de un render**, porque es el mismo contenedor: sin red, repo
read-only, `cap_drop: ALL`, `no-new-privileges`, 1.5 vCPU / 2 GB / 256 pids, `--rm`, y como
único directorio escribible el de la propia ejecución. Ejecutar Python no confiable no es una
capacidad nueva —una escena de manim ya lo es desde el primer día—; lo que cambia es que este
Python **mide** en vez de dibujar. `PYTHONPATH` apunta a `manim_extensions`, así que
`import sistemas` funciona igual que en una sonda.

Cada ejecución es un directorio (`render_jobs/lab/<id>/`) con `script.py`, `meta.json` y sus
resultados: sin migración de esquema, y borrar una ejecución es borrar su directorio. **Una a
la vez** (409 si hay otra en curso): el VPS tiene 2 vCPU y no compite con un render. No pasa
por la cola de renders porque una sonda son 1–3 s, igual que `mezclar_audio` y
`verificar_promo`, que tampoco pasan.

| Método | Ruta | Notas |
|---|---|---|
| GET | `/api/laboratorio` | últimas 30 ejecuciones (sin la salida: 30 × 200 KB por refresco), `ocupado`, plantilla del editor y rango de timeout |
| POST | `/api/laboratorio` | `{script, timeout: 30..900, titulo}` → **202** con el id; la ejecución va en segundo plano y la vista consulta cada 1,2 s (nginx corta mucho antes de 900 s) |
| GET | `/api/laboratorio/{id}` | estado, `code`, `stdout`, `stderr` y archivos |
| GET | `/api/laboratorio/{id}/archivos/{nombre}` | PNG/JPG/SVG/WAV/TXT/JSON/CSV/MD/LOG; `script.py` y `meta.json` **no** se sirven |
| DELETE | `/api/laboratorio/{id}` | borra el directorio |
| GET | `/api/laboratorio/sondas` | las `sonda_*.py` del disco, con la primera línea de su docstring |
| POST | `/api/laboratorio/sondas/{nombre}` | corre esa sonda tal cual, sin argumentos (ruta cerrada) |

**`exit 1` no es una avería**: una sonda con invariantes rotos sale con 1 a propósito, y eso es
ámbar («con hallazgos»), no rojo. Rojo son `timeout` y `error` (runner caído).

### Atajos y paleta de comandos

| Tecla | Qué hace |
|---|---|
| `Ctrl+K` / `⌘K` | paleta de comandos: ir a un curso o a una sección escribiendo |
| `g` + `p`/`e`/`r`/`a`/`l`/`d`/`c` | Proyectos · Estudio · Renders · Aprender · Laboratorio · Admin · Configuración |
| `Ctrl+Enter` | renderizar (Estudio) o ejecutar (Laboratorio), desde el editor |
| `?` | la hoja con todo esto |

La tabla `ATAJOS` de `components/Atajos.jsx` es a la vez la implementación y la hoja de ayuda.
Las teclas sueltas **no actúan mientras se escribe** (input, textarea, `contenteditable` o
CodeMirror); `Ctrl+K` sí funciona siempre, porque es el atajo para *salir* de donde estás.

La paleta no pide nada al servidor (usa el store del catálogo) y **puntúa** en vez de filtrar:
`alg 42` encuentra «Álgebra lineal · 4.2 Diagonalizar» — ignora tildes y reintenta cada palabra
contra el texto sin puntuación, porque nadie teclea el punto de «4.2».

Los clips de un proyecto se **reordenan arrastrando** por su asa (el `draggable` es el asa, no
la tarjeta: dentro hay campos de texto).

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

**Desde 2026-09-03 la voz no depende de GCP.** Hay cuatro proveedores
(`app/tts.py`), y la interfaz enseña cuáles están disponibles y por qué no:

| Proveedor | Qué es | Red | Guion |
|---|---|---|---|
| `edge` (defecto) | edge-tts, 45 voces neuronales en español (es-MX Jorge/Dalia…) | desde el backend | no |
| `piper` | Piper offline; un `.onnx` por voz en `MS_PIPER_VOICES_DIR` (`/etc/manimstudio/voces`) | no | no |
| `vertex` | Gemini TTS; el único que **escribe** el guion (Gemini 2.5 Pro) | sí, de pago | sí |
| `archivo` | la grabación del dueño, subida por clip | — | — |

Flujo:

- **Guion**: si Vertex está disponible lo escribe Gemini a partir del script
  (como siempre). Si no, se escribe a mano en «Guion y voz» (tabla de
  secciones `t_inicio / t_fin / momento / texto`; `PUT
  /api/projects/{pid}/narracion/{cid}/guion`) o lo escribe Claude desde la
  terminal. Un guion a mano se alinea **exacto** a sus tiempos (sin el tope
  de 2.5 s de hueco que aplica a los tiempos estimados por Gemini).
- **Voz**: `POST /api/projects/{pid}/narracion` acepta `{proveedor, voz,
  solo_audio, clips, force}`. Sin guion y sin Vertex responde 409 diciendo
  qué clips lo necesitan. `GET /api/narracion/proveedores` es el catálogo.
- **Grabación propia**: `PUT /api/projects/{pid}/narracion/{cid}/audio?nombre=toma.m4a`
  con el archivo como cuerpo (wav/mp3/flac/ogg se decodifican en el backend
  con miniaudio; m4a/aac/webm/opus pasan por ffmpeg en el contenedor,
  comando `normalizar_voz` del runner). Se convierte a mono 24 kHz, se le
  recorta el silencio y queda en la **misma ruta canónica** que el TTS
  (`guiones/<slug>/NN-<slug>.wav`), así la película la recoge sin cambios.
  nginx admite 25 MB en `/api/`.
- Cambiar el proveedor por defecto **no** deja desactualizado el catálogo: el
  hash de frescura usa la voz con que se narró cada clip.
- Piper corre como subproceso (`python -m piper`); la unidad del backend sube
  a `MemoryMax=1024M` por eso. Sale a 0 dBFS y se atenúa a −3 dB.
- Los tests simulan «solo Vertex» con `MS_TTS_PROVEEDORES=vertex,archivo`.

Lo anterior sigue vigente: guion por secciones cronometradas, síntesis por
sección con recorte de silencio, compresión de silencios para caber en el
vídeo y hasta tres guiones más cortos (solo con Gemini), estado en
`guiones/<slug>/estado.json` (hash de script compuesto+escena+duración+voz →
detecta narraciones desactualizadas). API: `GET/POST
/api/projects/{pid}/narracion`, `POST .../narracion/cancel`, `GET
.../narracion/{cid}/{audio,texto,guion}`.

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
