# ManimStudio

Consola web privada (un solo usuario) para renderizar escenas de Manim Community en el
contenedor Docker existente de `codeaerospace_contenido`, con biblioteca de videos,
monitoreo en tiempo real e histórico del VPS y asistente IA de depuración (Vertex AI).

**URL:** https://coderesearch.space · **Usuario:** `admin` · **Password:** `/root/.manimstudio_admin_password`

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
- **Cuota de disco**: `MS_MAX_STORAGE_MB` (default 2048). Si `render_jobs/` supera la cuota,
  crear un job responde **507** con mensaje claro; la barra de uso se muestra en la pestaña.
- El log de cada render se persiste como `render_jobs/<id>/render.log` al terminar (done,
  error y timeout) y sobrevive reinicios del backend: `get_logs` cae a ese archivo cuando el
  buffer en memoria ya no existe (el buffer se libera al terminar → sin fugas de memoria).

### Monitoreo histórico (pestaña «Monitoreo»)

- Ring buffer en memoria (`deque`, ~30 min al intervalo configurado; 450 muestras a 4 s)
  alimentado por el mismo `_metrics_loop` del SSE. Cero procesos nuevos, cero disco.
- `GET /api/metrics/history` + gráficas SVG dibujadas a mano (sin librerías de charting):
  CPU, RAM y disco de los últimos 30 min, actualizadas en vivo por el SSE, con bandas
  doradas en los intervalos donde hubo un render activo.

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

- Config del backend: `studio/backend/.env` (chmod 600). Cambiar password:
  `venv/bin/python -c "import bcrypt;print(bcrypt.hashpw(b'NUEVA', bcrypt.gensalt(12)).decode())"`
  → pegar en `MS_ADMIN_PASSWORD_HASH` → `systemctl restart manimstudio-backend`.
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
