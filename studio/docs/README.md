# ManimStudio

Consola web privada (un solo usuario) para renderizar escenas de Manim Community en el
contenedor Docker existente de `codeaerospace_contenido`, con biblioteca de videos,
monitoreo en tiempo real e histórico del VPS y asistente IA de depuración (Vertex AI).

**URL:** https://coderesearch.space · **Usuario:** `alanrosasp` · la password vigente vive en
la DB (tabla `auth`, ver «Autenticación y cambio de contraseña» más abajo), no en un archivo.

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
  legibles viven en `studio/content/lessons/categories.yaml`. Estado actual: **12 categorías
  × 5 lecciones = 60** (del espacio y los satélites a IA, agentes, IA agéntica y tecnología
  de frontera).
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
| POST | `` | crea proyecto (`name`, `description`, `quality`, `style_block`) |
| GET | `/{pid}` | detalle con clips ordenados |
| PATCH | `/{pid}` | edita nombre/descripción/calidad/estilo (413 si `style_block` > 200 KB) |
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

**Flujo de unión externa** (cuando se quiere el curso completo como un solo archivo, algo que
ManimStudio no hace en el servidor para no sumar otro paso de render):

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
