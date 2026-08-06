# Proyectos (cursos) con continuidad — Plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Añadir a ManimStudio la entidad Proyecto (curso) con clips ordenados, continuidad garantizada (calidad fija, estilo compartido, notas de encadenado, detección de desactualización) y exportación para concatenación externa (manifest + concat.txt + zip).

**Architecture:** SQLite con migraciones aditivas; lógica de negocio en `app/projects.py` (ProjectService); rutas en `app/projects_api.py` (APIRouter montado en main); el JobManager gana columnas `project_id/clip_id/content_hash` y un callback `on_job_done`; frontend React con nueva vista Proyectos + integración en Studio/Library.

**Tech Stack:** FastAPI + sqlite3 síncrono con lock (patrón existente), pytest con conftest de recarga de módulos, React 18 + Tailwind v4 + shadcn/Radix + CodeMirror.

**Spec:** `docs/superpowers/specs/2026-07-16-proyectos-cursos-design.md` — LEERLA COMPLETA antes de implementar.

## Global Constraints

- **Un commit atómico por sprint**, subject **sin acentos** (regla dura del proyecto).
- NUNCA commitear `.env`, `gcp-key.json`, `render_jobs/`, `manimstudio.db*`, `metrics_history.json*`.
- Backend: 1 worker uvicorn; cola y SSE viven en memoria — no introducir estado que lo rompa.
- Todos los endpoints nuevos con `Depends(require_auth)`.
- Tests: `cd studio/backend && venv/bin/pytest -q` — TODOS verdes al cerrar cada sprint (73 existentes + nuevos).
- Comentarios y mensajes de error de cara al usuario en español (patrón existente).
- El runner (`studio/runner/`) NO se toca en este plan.
- Frontend: `cd studio/frontend && node_modules/.bin/vite build` debe pasar al cerrar sprints 4-5.
- Estética: tokens de `theme.css` y componentes `components/ui/*` existentes; el mock `FileManager.jsx`/`GlowCard.jsx` es referencia visual (glass cards), NO se conecta tal cual.

---

### Sprint 1: Persistencia y servicio de proyectos (backend puro)

**Files:**
- Modify: `studio/backend/app/db.py` (schema + migraciones + métodos SQL)
- Create: `studio/backend/app/projects.py` (ProjectService)
- Test: `studio/backend/tests/test_projects_store.py`

**Interfaces (Produces):**

`db.py` — añadir al `SCHEMA` las tablas del spec §3 (projects, clips, con `CREATE TABLE IF NOT EXISTS` y `CREATE INDEX IF NOT EXISTS idx_clips_project ON clips(project_id, position)`), añadir a `MIGRATIONS` de jobs: `("project_id", "ALTER TABLE jobs ADD COLUMN project_id TEXT")`, `("clip_id", "ALTER TABLE jobs ADD COLUMN clip_id TEXT")`, `("content_hash", "ALTER TABLE jobs ADD COLUMN content_hash TEXT")`. Métodos nuevos en `Database` (mismo estilo lock+commit, dicts):

```python
def insert_project(self, p: dict) -> None            # todas las cols de projects
def get_project(self, pid: str) -> dict | None
def list_projects(self) -> list[dict]                # ORDER BY updated_at DESC
def update_project(self, pid: str, **fields) -> None # setea updated_at fuera (caller)
def delete_project(self, pid: str) -> None           # borra clips y fila, misma transaccion
def insert_clip(self, c: dict) -> None
def get_clip(self, cid: str) -> dict | None
def list_clips(self, pid: str) -> list[dict]         # ORDER BY position
def update_clip(self, cid: str, **fields) -> None
def delete_clip(self, cid: str) -> None
def clip_job_ids(self) -> set[str]                   # SELECT job_id FROM clips WHERE job_id IS NOT NULL
def clips_unlink_job(self, job_id: str) -> None      # UPDATE clips SET job_id=NULL, rendered_hash=NULL WHERE job_id=?
def renumber_clips(self, pid: str, ordered_ids: list[str]) -> None  # UPDATE position en una transaccion
```

`projects.py` — `ProjectService(db: Database)` con:

```python
QUALITY_SPECS = {"ql": {"resolution": "854x480",  "fps": 15},
                 "qm": {"resolution": "1280x720", "fps": 30},
                 "qh": {"resolution": "1920x1080","fps": 60}}

def compose_script(style_block: str, script: str) -> str
    # sin style_block.strip(): devuelve script tal cual
    # con estilo: f"{style_block.rstrip()}\n\n# --- fin estilo del proyecto ---\n\n{script}"

def content_hash(style_block: str, script: str) -> str   # sha256 hex del compuesto

def style_offset(style_block: str) -> int
    # lineas que el estilo antepone al script del clip (0 si no hay estilo);
    # con estilo: len(compose(style,"X").splitlines()) - 1

class ProjectService:
    def create_project(self, name, description, quality, style_block) -> dict      # valida quality in QUALITIES
    def get_project_detail(self, pid) -> dict | None
        # {**project, "clips": [ {**clip_public, "stale": bool, "status": str} ]}
        # clip_public = clip sin script (añade script_len); stale = clip["job_id"] y
        #   clip["rendered_hash"] != content_hash(style_block, clip["script"])
        # status: "rendered" | "stale" | "no_render" (job activo lo resuelve la UI con /api/jobs)
    def list_projects_summary(self) -> list[dict]
        # {**project(sin style_block), "clip_count", "rendered_count", "stale_count"}
    def update_project(self, pid, **fields) -> dict     # quality inmutable si algun clip tiene job_id (ValueError)
    def delete_project(self, pid) -> None               # desliga jobs de sus clips (db.update_job? NO: jobs conservan project_id/clip_id como texto historico; solo borra projects/clips)
    def add_clip(self, pid, title, script="", scene="", position=None, adopt_job: dict | None=None) -> dict
        # position None => al final; adopt_job: copia script/scene del job;
        # si adopt_job["quality"] == project["quality"]: job_id=job["id"],
        #   rendered_hash=content_hash(style, job_script) (solo si compone igual)
    def update_clip(self, cid, **fields) -> dict        # tocar script/scene NO borra job_id (stale lo detecta el hash)
    def move_clip(self, pid, cid, position: int) -> None  # reordena y compacta 0..n-1
    def delete_clip(self, pid, cid) -> None             # compacta posiciones
    def handle_job_done(self, job: dict) -> None
        # si job["clip_id"]: clip = db.get_clip(...); si existe y clip["project_id"]==job["project_id"]:
        #   db.update_clip(cid, job_id=job["id"], rendered_hash=job["content_hash"], updated_at=now)
    def export_manifest(self, pid, jobs_by_id: dict[str, dict]) -> dict   # spec §4 (incluye specs de QUALITY_SPECS, filename "NNN-slug.mp4")
```

Slug de filename: `f"{position+1:03d}-" + re.sub(r"[^a-z0-9]+","-",title.lower()).strip("-")[:40] + ".mp4"` (si queda vacío, usar `clip`).

- [ ] **Paso 1: tests que fallan** — escribir `tests/test_projects_store.py` (usa `Database` directo sobre `tmp_path / "t.db"`, sin TestClient):
  - `test_compose_and_hash`: sin estilo compose==script; con estilo contiene marcador; hash cambia si cambia estilo o script; `style_offset("")==0` y con estilo de 2 líneas ==4 (2 estilo + blank + marcador... verificar contando: compose("a\nb","X") → líneas: a,b,'','# --- fin estilo del proyecto ---','','X' → offset 5).
  - `test_project_crud`: create → get → update name → delete (clips desaparecen).
  - `test_clip_ordering`: 3 clips, move último a 0, posiciones quedan [0,1,2] compactas y en orden esperado; delete del medio compacta.
  - `test_stale_detection`: clip con job_id+rendered_hash correcto no está stale; editar script → stale; cambiar style_block del proyecto → stale.
  - `test_handle_job_done`: actualiza job_id/rendered_hash; con clip borrado no explota; con clip de otro proyecto no enlaza.
  - `test_quality_immutable_with_renders`: update_project(quality=...) lanza ValueError si hay clip con job_id; permitido si ninguno.
  - `test_adopt_job`: misma calidad adopta job; calidad distinta no adopta (job_id None).
  - `test_manifest`: 2 clips renderizados + 1 sin render → manifest lista solo info completa correcta, filenames `001-...mp4` ordenados, specs de calidad correctos.
- [ ] **Paso 2: correr y ver fallar** — `venv/bin/pytest tests/test_projects_store.py -q` → falla por import.
- [ ] **Paso 3: implementar** `db.py` (schema/migraciones/métodos) y `projects.py` completos.
- [ ] **Paso 4: verde total** — `venv/bin/pytest -q` (los 73 existentes + nuevos).
- [ ] **Paso 5: commit** — `git add studio/backend && git commit -m "feat: persistencia y servicio de proyectos con clips y continuidad (sprint 1)"` (+ trailer Co-Authored-By).

---

### Sprint 2: API de proyectos + integración con JobManager

**Files:**
- Create: `studio/backend/app/projects_api.py`
- Modify: `studio/backend/app/main.py` (wiring: service, router, callback)
- Modify: `studio/backend/app/jobs.py` (create_job con campos extra, job_public, callback on_job_done, protección de purgas, unlink al borrar)
- Test: `studio/backend/tests/test_projects_api.py`

**Interfaces:**
- Consumes: `ProjectService` y métodos `Database` del Sprint 1.
- Produces (contratos HTTP del spec §4):

```
GET    /api/projects                          → {"projects": [summary...]}
POST   /api/projects                          201 {project}   body: {name(1..120), description?, quality, style_block?(<=max_script_bytes)}
GET    /api/projects/{pid}                    → detail (clips con stale/status/script_len, SIN script)
GET    /api/projects/{pid}/clips/{cid}/script → {"script", "style_offset"}
PATCH  /api/projects/{pid}                    → {project}; quality con renders → 409
DELETE /api/projects/{pid}                    → {"ok": true}
POST   /api/projects/{pid}/clips              201 {clip}  body: {title, script?, scene?, position?, from_job_id?}
PATCH  /api/projects/{pid}/clips/{cid}        → {clip}
DELETE /api/projects/{pid}/clips/{cid}        → {"ok": true}
POST   /api/projects/{pid}/clips/{cid}/move   {position:int} → {"clips":[...]}  (detail refrescado)
POST   /api/projects/{pid}/clips/{cid}/render 201 {job}
POST   /api/projects/{pid}/render-stale       → {"queued": [job_ids...]}
```

- `clips/{cid}/render`: compone script (estilo+clip), valida `_check_script`, `detect_scenes` sobre el compuesto, escena del clip presente (422 si el clip no tiene scene o no existe), `_check_quota()`, y llama `manager.create_job(composed, scene, project["quality"], timeout=cfg.default_timeout, project_id=pid, clip_id=cid, content_hash=hash)`.
- `render-stale`: itera clips en orden, encola los stale o sin render que tengan script+scene válidos; sigue con los demás si uno falla la validación (lo reporta en `"skipped": [{clip_id, error}]`).
- `jobs.py`:
  - `create_job(self, script, scene, quality, timeout, project_id=None, clip_id=None, content_hash=None)` — inserta columnas nuevas; `job_public` añade `project_id`, `clip_id`.
  - Nuevo atributo `self.on_job_done: callable | None = None`; en `_finish`, si `status=="done"` y hay callback: `job = self.db.get_job(job_id)` y llamarlo con el job (try/except con print, nunca romper el worker). Llamar ANTES de `_publish_job` para que el SSE salga con el clip ya enlazado.
  - `delete_failed_jobs`/`delete_finished_jobs`/`delete_jobs_older_than`: `protected = self.db.clip_job_ids()` una vez y saltar `job["id"] in protected`.
  - `delete_job`: tras borrar, `self.db.clips_unlink_job(job_id)`.
- `main.py`: `service = ProjectService(db)`, `manager.on_job_done = service.handle_job_done`, `app.include_router(projects_router)`. El router se crea con una factory `make_router(cfg, db, manager, service)` para no importar globals de main (evita ciclo) — main lo monta después de crear todo.
- `retry_job` de un job con clip: conserva `project_id/clip_id/content_hash` del job original.

- [ ] **Paso 1: tests que fallan** — `tests/test_projects_api.py` con fixture `authed` existente:
  - `test_projects_crud_api`: POST/GET/PATCH/DELETE + validaciones (quality inválida 422, name vacío 422, 404s).
  - `test_clip_crud_and_move`: crear 3, move, DELETE, orden compacto en GET detail.
  - `test_clip_render_creates_linked_job`: POST render → 201, job con project_id/clip_id en GET /api/jobs; clip sin scene → 422.
  - `test_clip_render_composes_style`: proyecto con style_block que define una constante; GET /api/jobs/{id}/script devuelve compuesto con marcador.
  - `test_from_job_id`: crear job normal (queda error sin runner, da igual: usar su script), crear clip from_job_id copia script/scene.
  - `test_purge_protects_clip_renders`: simular render done enlazado (insertar/actualizar vía `Database` directo: `update_job(job_id, status="done", ...)` + `update_clip(cid, job_id=...)`, patrón de test_library.py si existe similar — revisar) → DELETE /api/jobs/finished no lo borra; DELETE /api/jobs/{id} individual sí y el clip queda job_id NULL.
  - `test_quality_change_conflict`: 409 con render vigente.
  - `test_render_stale_endpoint`: encola solo los stale, devuelve skipped para clip sin scene.
- [ ] **Paso 2: ver fallar.**
- [ ] **Paso 3: implementar** router + wiring + jobs.py.
- [ ] **Paso 4: suite completa verde** — `venv/bin/pytest -q`.
- [ ] **Paso 5: commit** — `"feat: API de proyectos y clips ligada al gestor de renders (sprint 2)"`.

---

### Sprint 3: Exportación (manifest + archive zip)

**Files:**
- Modify: `studio/backend/app/projects_api.py` (2 endpoints)
- Modify: `studio/backend/app/projects.py` (helpers de export si faltan)
- Test: `studio/backend/tests/test_projects_export.py`

**Interfaces:**
```
GET /api/projects/{pid}/export   → application/json manifest (spec §4)
GET /api/projects/{pid}/archive  → application/zip descarga "<slug-proyecto>.zip"
```
- Manifest: `{"project": {id,name,description,quality}, "specs": QUALITY_SPECS[q], "generated_at": epoch, "clips": [{"position","title","scene","filename","has_video","duration_s","size_bytes","stale"}], "concat": ["file 'NNN-slug.mp4'", ...]}` — `duration_s = finished_at-started_at` del job (None si falta). Clips sin video: `has_video:false` y fuera de `concat`.
- Archive: 404 si ningún clip tiene video vigente. Contenido: `NNN-slug.mp4` (video de cada clip con render, validando como `/video` que la ruta esté dentro del job dir), `concat.txt`, `manifest.json`, `LEEME.txt` con el comando ffmpeg (`ffmpeg -f concat -safe 0 -i concat.txt -c copy curso.mp4`). Implementación: `zipfile.ZipFile(tmp, "w", ZIP_STORED)` sobre `tempfile.NamedTemporaryFile(delete=False, dir=tempfile.gettempdir(), suffix=".zip")`; responder `FileResponse(..., background=BackgroundTask(os.unlink, tmp_path))` (import `starlette.background.BackgroundTask`). Si un video listado desaparece a mitad, saltarlo (el manifest dentro del zip es el generado en ese momento).

- [ ] **Paso 1: tests que fallan** — `tests/test_projects_export.py`:
  - `test_manifest_endpoint`: proyecto 2 clips (1 con "video": crear archivo mp4 falso en `tmp_path/render_jobs/<job_id>/media/videos/x/y/Demo.mp4`, `update_job(video_path=..., status="done", size_bytes=...)`, enlazar clip) → JSON con concat solo del renderizado, filename correcto.
  - `test_archive_zip`: descargar, abrir con `zipfile.ZipFile(io.BytesIO(r.content))`, verificar names `001-....mp4`, `concat.txt` (contenido con orden), `manifest.json`, `LEEME.txt`.
  - `test_archive_empty_404`: proyecto sin renders → 404.
- [ ] **Paso 2: ver fallar.** · **Paso 3: implementar.** · **Paso 4: suite verde.**
- [ ] **Paso 5: commit** — `"feat: exportacion de curso con manifest, concat y zip (sprint 3)"`.

---

### Sprint 4: Frontend — vista Proyectos

**Files:**
- Modify: `studio/frontend/src/router.js` (hash `proyectos` → view `projects`)
- Modify: `studio/frontend/src/api.js` (funciones project*)
- Modify: `studio/frontend/src/Header.jsx` (pestaña Proyectos, icono `FolderKanban` de lucide, entre Estudio y Biblioteca)
- Modify: `studio/frontend/src/App.jsx` (montar vista keep-alive; estado `clipContext`)
- Create: `studio/frontend/src/Projects.jsx` (lista + detalle; subcomponentes internos)
- Test: build + smoke por vista

**Interfaces:**
- `api.js` añade (mismo estilo `req` existente): `listProjects()`, `createProject(body)`, `getProject(id)`, `patchProject(id, body)`, `deleteProject(id)`, `createClip(pid, body)`, `patchClip(pid, cid, body)`, `deleteClip(pid, cid)`, `moveClip(pid, cid, position)`, `renderClip(pid, cid)`, `renderStale(pid)`, `getClipScript(pid, cid)`, `projectExportUrl(pid)`, `projectArchiveUrl(pid)`.
- `App.jsx`: `const [clipContext, setClipContext] = useState(null)` — `{projectId, projectName, clipId, clipTitle, quality, styleOffset}`. Pasa a `<Projects onEditClip={(ctx, script, scene) => { setPendingScript(script); setClipContext(ctx); navigate('studio') }} jobs={jobs} />`. (El Studio consume `clipContext` en el Sprint 5; este sprint solo lo define y navega.)
- `Projects.jsx` (`export default function Projects({ jobs, onEditClip, routeId, onRoute })`):
  - `routeId == null` → **lista**: grid de tarjetas glass (borde acento, patrón visual de `GlowCard`/paneles existentes): nombre, descripción, `X clips · Y listos · Z desactualizados`, calidad (`480p/720p/1080p` como en Library `QUALITY_LABEL`), fecha. Botón "Nuevo proyecto" abre Dialog (nombre, descripción, calidad select, estilo opcional textarea). Borrar con patrón `DeleteButton` de dos toques (copiarlo o extraerlo a `components/DeleteButton.jsx` y reutilizar en Library — extraer es lo correcto).
  - `routeId` → **detalle** (`onRoute(id)` navega, deep-link `#/proyectos/<id>`): cabecera (nombre editable, descripción, calidad como badge fijo, botones Exportar manifest / Descargar curso (.zip, deshabilitado si 0 renderizados) / Re-renderizar desactualizados / Editar estilo (Dialog con `<textarea>` monoespaciada, no hace falta CodeMirror aquí)). Lista de clips: tarjeta por clip con miniatura (thumbUrl del job si `has_thumb` — el detalle de proyecto trae `job_id`; buscar el job en `jobs` prop para thumb/duración/estado activo), título editable, escena, estado (`badge`: renderizado/desactualizado/sin render/en cola/renderizando — los dos últimos si hay job activo con ese clip_id en `jobs`), notas de continuidad plegables (`final_state`, `notes`, y arriba "El clip anterior termina: …" leyendo el `final_state` del clip previo), botones: Editar en Estudio (pide script vía `getClipScript` y llama `onEditClip`), Render, ↑ ↓ (move), Borrar (dos toques). Botón "Añadir clip" (Dialog: título + escena opcional).
  - Refresco: cargar detalle con `getProject(routeId)` al montar/cambiar ruta y cuando llegue por props un cambio en `jobs` de un job cuyo `clip_id` pertenezca al proyecto y pase a estado terminal (efecto sobre `jobs` con ref del estado previo, patrón de App.jsx con jobsRef).
  - Errores: patrón `error` state + `<p role="alert">` de Library.
- `router.js`: añadir `proyectos: 'projects'` a `HASH_TO_VIEW`.
- `App.jsx`: bloque keep-alive `visited.current.has('projects')` idéntico al de otras vistas, con `routeId={view === 'projects' ? route.param : null}` y `onRoute={(id) => navigate('projects', id)}`.

- [ ] **Paso 1: implementar** router + api + Header + App + Projects.jsx.
- [ ] **Paso 2: build** — `node_modules/.bin/vite build` sin errores.
- [ ] **Paso 3: smoke backend+frontend** — arrancar uvicorn efímero sobre workspace temporal (patrón E2E: env MS_* dummy) y verificar con curl que `/` sirve y `GET /api/projects` responde 401 sin cookie (wiring correcto).
- [ ] **Paso 4: commit** — `"feat: vista Proyectos con clips, continuidad y export (sprint 4)"`.

---

### Sprint 5: Integración Estudio/Biblioteca + docs + E2E

**Files:**
- Modify: `studio/frontend/src/Studio.jsx` (contexto de clip)
- Modify: `studio/frontend/src/App.jsx` (pasar clipContext/onExitClip a Studio)
- Modify: `studio/frontend/src/Library.jsx` ("Añadir a proyecto", aviso al borrar render de clip)
- Modify: `studio/docs/README.md` (sección Proyectos: modelo, endpoints, flujo de unión externa)
- Test: suite backend completa + build + E2E real con cookie firmada

**Interfaces:**
- `Studio.jsx` recibe `clipContext` y `onExitClip()`:
  - Banner encima del editor: `Proyecto {projectName} · clip “{clipTitle}” · calidad {quality} (fija)` + botón "Salir del clip" (llama `onExitClip`, no toca el script).
  - Selector de calidad deshabilitado con la del proyecto mientras hay contexto.
  - Botón "Guardar en clip": `patchClip(projectId, clipId, { script, scene })` (script SIN el style_block: el Studio edita el script del clip tal cual; `pendingScript` que llegó de Projects es `getClipScript().script`, que ya viene sin estilo — verificar que el endpoint devuelve el script crudo del clip, sí según contrato Sprint 2).
  - Render con contexto: en vez de `api.createJob`, guarda primero en el clip (mismo PATCH) y llama `api.renderClip(projectId, clipId)`; los errores de render muestran nota "el estilo del proyecto añade N líneas" usando `styleOffset` si > 0.
- `App.jsx`: `<Studio ... clipContext={clipContext} onExitClip={() => setClipContext(null)} />`.
- `Library.jsx`: en cada tarjeta de video, botón "Añadir a proyecto…" → Dialog con select de proyectos (cargar `listProjects()` al abrir) + crear (`createClip(pid, { title: j.scene, from_job_id: j.id })`), toast/aviso de éxito con link "#/proyectos/<pid>". Al borrar un video cuyo `clip_id`/pertenencia a clip exista (el job trae `clip_id`), el DeleteButton confirma con texto "Es el render de un clip; el clip quedara sin video. ¿Confirmar?".
- `README.md` de studio/docs: sección "Proyectos (cursos)" — modelo, reglas de continuidad, endpoints, flujo: renderizar clips → Descargar curso → `ffmpeg -f concat -safe 0 -i concat.txt -c copy curso.mp4`.

- [ ] **Paso 1: implementar** Studio/App/Library/docs.
- [ ] **Paso 2: verificación total** — backend `venv/bin/pytest -q` verde; frontend build limpio.
- [ ] **Paso 3: E2E producción local** — deploy (build ya hecho + `sudo systemctl restart manimstudio-backend.service`), cookie firmada con `MS_SECRET_KEY` de `/etc/manimstudio/env`, y contra `http://127.0.0.1:3002`: crear proyecto real, añadir clip con script Manim trivial, `POST .../render` (RENDER REAL: esperar polling `GET /api/jobs/{id}` hasta done, ~1-2 min), verificar clip enlazado + thumb, `GET export` y `GET archive` (zip válido), borrar el proyecto de prueba y el job. Verificar `https://coderesearch.space` sirve el bundle nuevo (`curl -s | grep -o 'index-[a-z0-9]*\.js'`).
- [ ] **Paso 4: commit** — `"feat: estudio con contexto de clip, biblioteca a proyectos y docs (sprint 5)"`.

---

## Self-review del plan (hecho)

- Cobertura del spec: §2 continuidad (calidad fija S1/S2, estilo S1-S2, notas S1/S4, stale S1), §3 modelo (S1), §4 API completa (S2/S3), §5 frontend (S4/S5), §6 bordes (S1/S2 tests), §7 pruebas (todas), §8 exclusiones respetadas.
- Sin placeholders: contratos y firmas explícitos; el detalle JSX queda a criterio del implementador siguiendo patrones citados (Library/App) — intencional.
- Consistencia de nombres verificada: `ProjectService`, `content_hash`, `clip_job_ids`, `clips_unlink_job`, `renderClip`, `getClipScript`, `styleOffset`.
