# ManimStudio

Consola web privada (un solo usuario) para renderizar escenas de Manim Community en el
contenedor Docker existente de `codeaerospace_contenido`, con monitoreo en tiempo real del VPS.

**URL:** https://coderesearch.space · **Usuario:** `admin` · **Password:** `/root/.manimstudio_admin_password`

## Arquitectura

```
navegador ──HTTPS──▶ nginx (coderesearch.space)
                      ├─ /            → estático  studio/frontend/dist  (React+Vite+CodeMirror)
                      └─ /api/        → 127.0.0.1:3002  backend FastAPI (usuario manimstudio, sin privilegios)
                                            │  cola en memoria: 1 render a la vez
                                            │  SQLite: studio/backend/manimstudio.db
                                            ▼ socket unix /run/manimstudio/runner.sock (0660 root:manimstudio)
                                        manim-runner (root, superficie minima: render/cancel/stats/ping)
                                            ▼ docker compose run … manim-render
                                        contenedor de render: network_mode:none, cpus:1.5, mem:2g,
                                        pids:256, no-new-privileges, timeout duro, --rm
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
- Artefactos de renders: `render_jobs/<job_id>/` (script + media). Limpieza manual segura:
  borrar directorios de jobs viejos; el historial en SQLite se conserva.
- El vhost activo es un symlink: `/etc/nginx/sites-enabled/coderesearch_space →
  studio/deploy/coderesearch.space.nginx`. Tras editar: `nginx -t && systemctl reload nginx`.

## Límites conocidos

- Un job a la vez por diseño (2 vCPU compartidas con ~19 contenedores de producción).
- Rate-limit de login en memoria: se reinicia con el proceso (aceptable, single-user).
- Si el backend se reinicia en medio de un render, el job se marca `error` y el runner/
  contenedor se limpia al cerrarse la conexión.
- El video se sirve por FastAPI (FileResponse con soporte Range); suficiente para un usuario.
