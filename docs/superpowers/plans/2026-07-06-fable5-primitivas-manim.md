# Fable 5 + biblioteca de primitivas Manim — plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Cerrar un hueco de seguridad real en el sandbox de render de ManimStudio, habilitar el renderer OpenGL headless de Manim, y añadir una herramienta admin-only donde Claude Fable 5 propone primitivas nuevas de Manim (Mobjects/Animations autocontenidos) que, tras revisión humana con render de muestra, se incorporan a una biblioteca curada versionada en git.

**Architecture:** 3 fases secuenciales. Fase 0 (bloqueante) endurece `docker-compose.yml`/`manim_runner.py` para que el contenedor de render monte el repo read-only + solo el directorio del job en read-write. Fase 1 añade las librerías Mesa/EGL al `Dockerfile` para el renderer OpenGL. Fase 2 añade dos módulos backend nuevos (`fable.py`: cliente Anthropic; `primitives.py`: orquestador de propuestas) que reutilizan el `JobManager`/`EventBus` existentes sin modificarlos, más endpoints FastAPI y un panel nuevo en el frontend.

**Tech Stack:** Python 3.13 / FastAPI (backend), React + Vite (frontend), Docker Compose, SDK oficial `anthropic` (Python), pytest.

## Global Constraints

- Modelo Anthropic: `model="claude-fable-5"`, sin fijar `thinking` (adaptativo por defecto), `output_config={"effort": "high"}`, con fallback por defecto `betas=["server-side-fallback-2026-06-01"], fallbacks=[{"model": "claude-opus-4-8"}]`.
- Toda llamada al SDK de Anthropic va detrás de un método `_call_model` mockeable en tests — igual que `ai.py`. Ningún test debe tocar la red real.
- El bind mount `.:/workspace` del contenedor `manim-render` pasa a ser **read-only**; solo el directorio del job (`render_jobs/<job_id>/`) se monta read-write, inyectado por invocación desde `manim_runner.py`.
- La biblioteca de primitivas aprobadas vive en `studio/content/manim_extensions/` (git). Las propuestas pendientes viven en `pending_primitives/<id>/` (fuera de git, mismo patrón efímero que `render_jobs/`).
- Nunca commitear `.env`, `gcp-key.json`, `render_jobs/`, `pending_primitives/`, `manimstudio.db`, `metrics_history.json*` (reglas ya existentes del proyecto).
- Commits atómicos por tarea, siguiendo el estilo de mensajes ya usado en el repo (`feat:`, `fix:`, `docs:`, `build:`).

---

## FASE 0 — Endurecer el sandbox de render

### Task 1: `docker-compose.yml` — mount read-only + cap_drop + rootfs read-only

**Files:**
- Modify: `docker-compose.yml`

**Interfaces:**
- Produces: el servicio `manim-render` deja de heredar `volumes: [".:/workspace"]` (rw) del ancla `x-manim-base`; monta `.:/workspace:ro` en su lugar. Tareas posteriores (Task 2) inyectan el mount rw del job vía `docker compose run -v`.

- [ ] **Step 1: Editar `docker-compose.yml`**

Reemplazar el bloque `manim-render:` completo (líneas 38-50) por:

```yaml
  # Servicio usado por ManimStudio para renders bajo demanda (docker compose
  # run). Misma imagen y limites que `manim`, pero sin red, sin puertos y sin
  # TTY: cada render ejecuta codigo Python arbitrario y se trata como no
  # confiable. El perfil "render" evita que arranque con `docker compose up`.
  #
  # El repo se monta READ-ONLY (a diferencia de `manim`, que lo monta rw para
  # uso interactivo): codigo no confiable no debe poder leer .env/gcp-key.json
  # con intencion de exfiltrarlos ni, sobre todo, reescribir manim_runner.py o
  # este mismo compose file (que el runner root ejecuta despues). El unico
  # directorio escribible es el del job en curso, montado por invocacion
  # desde manim_runner.py (ver RUN_AS_ARGS / argv en ese archivo).
  manim-render:
    <<: *manim-base
    image: codeaerospace_contenido-manim
    volumes:
      - .:/workspace:ro
    network_mode: "none"
    profiles: ["render"]
    read_only: true
    tmpfs:
      - /tmp:size=512m,mode=1777
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true
    deploy:
      resources:
        limits:
          <<: *manim-limits
          pids: 256
        reservations: *manim-reservations
```

- [ ] **Step 2: Validar la sintaxis del compose**

Run: `docker compose -f /var/www/codeaerospace_contenido/docker-compose.yml config --quiet`
Expected: sin salida ni error (exit code 0). Si falla, revisar indentación YAML.

- [ ] **Step 3: Commit**

```bash
git add docker-compose.yml
git commit -m "$(cat <<'EOF'
fix: montar el repo read-only en manim-render y dropear capabilities

El bind mount .:/workspace en modo lectura-escritura permitía a un script
de render (potencialmente generado por IA, no revisado antes de ejecutar)
leer secretos (.env, gcp-key.json) y reescribir manim_runner.py o este
mismo compose file, que el daemon runner (root) ejecuta después. Ahora
el repo se monta :ro; el directorio del job se monta rw por invocación
(Task siguiente). cap_drop: [ALL] + rootfs read-only + tmpfs para /tmp
cierran capabilities y escrituras sobrantes que Manim/ffmpeg no necesitan.
EOF
)"
```

---

### Task 2: `manim_runner.py` — mount rw acotado al directorio del job

**Files:**
- Modify: `studio/runner/manim_runner.py:96-113` (función `handle_render`)
- Modify: `studio/runner/manim_runner.py:152-199` (función `handle_thumbnail`)

**Interfaces:**
- Consumes: `PROJECT_DIR`, `RENDER_JOBS_DIR` (constantes ya definidas en el archivo, líneas 30-32).
- Produces: cada invocación de `docker compose run` para render/thumbnail incluye un flag `-v <host_job_dir>:/workspace/render_jobs/<job_id>:rw` adicional, de modo que el job puede escribir su propio directorio (`media/`, `thumb.jpg`) aunque el resto de `/workspace` sea read-only (Task 1).

- [ ] **Step 1: Añadir el mount rw en `handle_render`**

En `studio/runner/manim_runner.py`, reemplazar el bloque de construcción de `argv` (líneas 104-112):

```python
    container = CONTAINER_PREFIX + job_id
    argv = [
        "docker", "compose", "-f", COMPOSE_FILE, "--profile", "render",
        "run", "--rm", "--no-deps", "-T", *RUN_AS_ARGS, "--name", container,
        "manim-render",
        "manim", "render", f"-{quality}", "--disable_caching",
        "--media_dir", f"/workspace/{RENDER_JOBS_DIR}/{job_id}/media",
        f"/workspace/{script_rel}", scene,
    ]
```

por:

```python
    container = CONTAINER_PREFIX + job_id
    # El repo se monta read-only (docker-compose.yml); solo el directorio de
    # ESTE job se monta rw, por invocacion, para que Manim pueda escribir
    # media/ sin exponer el resto del repo en escritura.
    job_mount = f"{os.path.join(PROJECT_DIR, RENDER_JOBS_DIR, job_id)}:/workspace/{RENDER_JOBS_DIR}/{job_id}:rw"
    argv = [
        "docker", "compose", "-f", COMPOSE_FILE, "--profile", "render",
        "run", "--rm", "--no-deps", "-T", *RUN_AS_ARGS,
        "-v", job_mount,
        "--name", container,
        "manim-render",
        "manim", "render", f"-{quality}", "--disable_caching",
        "--media_dir", f"/workspace/{RENDER_JOBS_DIR}/{job_id}/media",
        f"/workspace/{script_rel}", scene,
    ]
```

- [ ] **Step 2: Añadir el mismo mount rw en `handle_thumbnail`**

En la misma función (líneas 182-190 actuales), reemplazar:

```python
    thumb_rel = f"{RENDER_JOBS_DIR}/{job_id}/thumb.jpg"
    container = f"{CONTAINER_PREFIX}{job_id}-thumb"
    code, _out, err = await run_cmd(
        "docker", "compose", "-f", COMPOSE_FILE, "--profile", "render",
        "run", "--rm", "--no-deps", "-T", *RUN_AS_ARGS, "--name", container,
        "--entrypoint", "ffmpeg", "manim-render",
        "-y", "-i", f"/workspace/{video_rel}",
        "-frames:v", "1", "-vf", "scale=320:-1",
        f"/workspace/{thumb_rel}",
        timeout=90,
    )
```

por:

```python
    thumb_rel = f"{RENDER_JOBS_DIR}/{job_id}/thumb.jpg"
    container = f"{CONTAINER_PREFIX}{job_id}-thumb"
    job_mount = f"{os.path.join(PROJECT_DIR, RENDER_JOBS_DIR, job_id)}:/workspace/{RENDER_JOBS_DIR}/{job_id}:rw"
    code, _out, err = await run_cmd(
        "docker", "compose", "-f", COMPOSE_FILE, "--profile", "render",
        "run", "--rm", "--no-deps", "-T", *RUN_AS_ARGS,
        "-v", job_mount,
        "--name", container,
        "--entrypoint", "ffmpeg", "manim-render",
        "-y", "-i", f"/workspace/{video_rel}",
        "-frames:v", "1", "-vf", "scale=320:-1",
        f"/workspace/{thumb_rel}",
        timeout=90,
    )
```

- [ ] **Step 3: Verificación manual de un render real**

Esta parte de la infraestructura no tiene suite de pytest (no hay `test_runner.py`; `manim_runner.py` corre como daemon root separado). Verificar a mano en el servidor:

Run:
```bash
sudo systemctl restart manimstudio-runner
sudo systemctl restart manimstudio-backend
```
Luego, desde la UI, crear un job con una lección existente (p.ej. cualquier animación de `studio/content/animations/`) y confirmar que renderiza igual que antes.

- [ ] **Step 4: Prueba negativa — confirmar que el resto del repo es read-only**

Crear un job de prueba con este script y renderizarlo (calidad `ql`, cualquier nombre de escena):

```python
from manim import *


class ProbeReadOnly(Scene):
    def construct(self):
        try:
            with open("/workspace/studio/backend/app/main.py", "a") as f:
                f.write("# probe\n")
            result = "ESCRIBIBLE (MAL)"
        except OSError as e:
            result = f"BLOQUEADO (bien): {e}"
        self.add(Text(result, font_size=24))
        self.wait(1)
```

Expected: el render debe mostrar "BLOQUEADO (bien): ..." — si muestra "ESCRIBIBLE (MAL)", el mount read-only no se aplicó (revisar Task 1) y no se debe continuar a la Fase 1/2 hasta corregirlo.

- [ ] **Step 5: Commit**

```bash
git add studio/runner/manim_runner.py
git commit -m "$(cat <<'EOF'
fix: montar rw solo el directorio del job en manim-render

Con el repo montado read-only (commit anterior), Manim necesita un mount
rw explicito para escribir media/ y thumb.jpg del job en curso. Se inyecta
por invocacion (-v en el argv de docker compose run) en vez de depender de
un volumen global, acotando la escritura al directorio de ESE job.
EOF
)"
```

---

### Task 3: sacar `.env` y `gcp-key.json` del árbol montado (defensa en profundidad)

**Files:**
- Modify: `studio/backend/app/config.py:51-52`
- Modify: `studio/deploy/manimstudio-backend.service`

**Interfaces:**
- Produces: valores por defecto de `gcp_key_path` y la ruta de `EnvironmentFile` apuntando fuera de `/var/www/codeaerospace_contenido` (fuera del árbol que monta `manim-render`), configurables por variable de entorno como ya lo eran.

Con el mount ya read-only (Task 1), esto es defensa en profundidad, no bloqueante: un script de render ya no puede *escribir* estos archivos, pero técnicamente aún podría *leerlos* si siguen dentro de `/workspace` (ro). Sacarlos del árbol montado elimina también la lectura.

- [ ] **Step 1: Cambiar el valor por defecto de `gcp_key_path` en `config.py`**

En `studio/backend/app/config.py`, reemplazar la línea 51-52:

```python
        self.gcp_key_path = Path(os.environ.get(
            "MS_GCP_KEY_PATH", str(Path(__file__).resolve().parents[1] / "gcp-key.json")))
```

por:

```python
        # Por defecto fuera del arbol montado en el contenedor de render
        # (/var/www/codeaerospace_contenido = /workspace ahi dentro): el
        # mount read-only ya evita la escritura, esto evita tambien la
        # lectura del secreto desde codigo no confiable.
        self.gcp_key_path = Path(os.environ.get(
            "MS_GCP_KEY_PATH", "/etc/manimstudio/gcp-key.json"))
```

- [ ] **Step 2: Actualizar `EnvironmentFile=` en el unit de systemd**

En `studio/deploy/manimstudio-backend.service`, cambiar:

```
EnvironmentFile=/var/www/codeaerospace_contenido/studio/backend/.env
```

por:

```
EnvironmentFile=/etc/manimstudio/env
```

- [ ] **Step 3: Pasos manuales de despliegue (no automatizables desde este repo)**

Estos pasos los ejecuta el operador en el servidor, con acceso root — no forman parte de ningún test automatizado:

```bash
sudo mkdir -p /etc/manimstudio
sudo mv /var/www/codeaerospace_contenido/studio/backend/.env /etc/manimstudio/env
sudo mv /var/www/codeaerospace_contenido/studio/backend/gcp-key.json /etc/manimstudio/gcp-key.json
sudo chown root:manimstudio /etc/manimstudio/env /etc/manimstudio/gcp-key.json
sudo chmod 640 /etc/manimstudio/env /etc/manimstudio/gcp-key.json
sudo cp studio/deploy/manimstudio-backend.service /etc/systemd/system/manimstudio-backend.service
sudo systemctl daemon-reload
sudo systemctl restart manimstudio-backend
curl -s http://127.0.0.1:3002/api/health
```

Expected del último comando: `{"ok":true,"runner":true}` — confirma que el backend arrancó leyendo las variables desde la nueva ubicación.

- [ ] **Step 4: Commit**

```bash
git add studio/backend/app/config.py studio/deploy/manimstudio-backend.service
git commit -m "$(cat <<'EOF'
fix: mover .env/gcp-key.json fuera del arbol montado en manim-render

Defensa en profundidad sobre el mount read-only del Task anterior: aunque
ya no se pueden escribir, tampoco deben ser legibles desde codigo de
render no confiable si siguen bajo /var/www/codeaerospace_contenido
(= /workspace dentro del contenedor). Requiere mover los archivos reales
en el servidor y recargar systemd (ver mensaje del commit anterior /
pasos manuales en el plan) — no aplica solo con este commit.
EOF
)"
```

---

## FASE 1 — Renderer OpenGL headless

### Task 4: añadir librerías Mesa/EGL al `Dockerfile`

**Files:**
- Modify: `Dockerfile:10-30`

**Interfaces:**
- Produces: la imagen `codeaerospace_contenido-manim` incluye las librerías de sistema necesarias para que `moderngl`/`moderngl-window` (ya en `requirements.txt` como dependencias transitivas de `manim`) puedan crear un contexto EGL headless sin GPU.

- [ ] **Step 1: Editar el `Dockerfile`**

Reemplazar el bloque `RUN apt-get install` (líneas 10-30) por:

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Video rendering
    ffmpeg \
    # Text layout (Pango)
    libpango1.0-dev \
    # LaTeX suite for equation rendering
    texlive \
    texlive-latex-extra \
    texlive-fonts-extra \
    texlive-latex-recommended \
    dvisvgm \
    # Cairo / pkg-config (required by pycairo / manim)
    pkg-config \
    libcairo2-dev \
    # OpenGL headless (Mesa/EGL): permite --renderer=opengl sin GPU/display
    libgl1-mesa-glx \
    libegl1-mesa \
    libglu1-mesa \
    # Build utilities
    build-essential \
    git \
    curl \
    # Clean up apt caches
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*
```

- [ ] **Step 2: Reconstruir la imagen**

Run: `docker compose -f /var/www/codeaerospace_contenido/docker-compose.yml build manim`
Expected: build exitoso (exit code 0). Anotar el tamaño final con `docker images codeaerospace_contenido-manim` para comparar contra los 5.17 GB previos (referencia del informe de auditoría).

- [ ] **Step 3: Commit**

```bash
git add Dockerfile
git commit -m "$(cat <<'EOF'
feat: añadir librerías Mesa/EGL para el renderer OpenGL headless de Manim

moderngl/moderngl-window/glcontext ya estaban instalados como dependencias
Python de manim, pero faltaban las librerías de sistema para crear un
contexto GL sin GPU/display. Habilita --renderer=opengl dentro del
contenedor de render (sin red, sin display).
EOF
)"
```

---

### Task 5: verificación end-to-end del renderer OpenGL

**Files:** (ninguno — solo verificación manual)

- [ ] **Step 1: Crear un job de prueba con una escena OpenGL simple**

Desde el editor de ManimStudio (o vía `POST /api/jobs` autenticado), crear un job con este script, calidad `ql`:

```python
from manim import *
import manim.utils.color as color


class ProbeOpenGL(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=60 * DEGREES, theta=30 * DEGREES)
        cube = Cube(side_length=2, fill_opacity=0.7, fill_color=color.BLUE)
        self.add(cube)
        self.wait(1)
```

Nota: `detect_scenes` (basado en `ast`) reconoce `ThreeDScene` como base de escena (ya está en `SCENE_BASES`), así que este script pasa la validación existente sin cambios.

- [ ] **Step 2: Ejecutar el render con `--renderer=opengl`**

El flag `--renderer` no está expuesto hoy en la UI (`manim_runner.py` construye el comando sin él). Para esta verificación puntual, ejecutar manualmente contra la imagen ya construida, simulando el mismo comando que usa el runner:

```bash
cd /var/www/codeaerospace_contenido
docker compose -f docker-compose.yml --profile render run --rm --no-deps -T \
  --user "$(id -u manimstudio):$(id -g manimstudio)" -e HOME=/tmp \
  -v "$(pwd)/render_jobs/probe:/workspace/render_jobs/probe:rw" \
  manim-render \
  manim render -ql --renderer=opengl --disable_caching \
  --media_dir /workspace/render_jobs/probe/media \
  /workspace/render_jobs/probe/scene.py ProbeOpenGL
```

(previamente crear `render_jobs/probe/scene.py` con el contenido del Step 1).

Expected: exit code 0 y un `.mp4` bajo `render_jobs/probe/media/videos/`. Si falla con un error de contexto EGL/GL, ese es el resultado esperable de documentar antes de anunciar la capacidad como disponible — no es bloqueante para la Fase 2 (que no depende de OpenGL), pero sí antes de dar la Fase 1 por cerrada.

- [ ] **Step 3: Confirmar que el renderer Cairo (por defecto) sigue funcionando**

Repetir el Step 1 sin `--renderer=opengl` (o simplemente crear el job normal vía la UI, que no pasa ese flag) y confirmar que sigue renderizando igual que antes de la Fase 1.

- [ ] **Step 4: Limpiar el directorio de prueba**

```bash
rm -rf /var/www/codeaerospace_contenido/render_jobs/probe
```

No hay commit en esta tarea (es solo verificación).

---

## FASE 2 — Biblioteca de primitivas generadas con Fable 5

### Task 6: configuración — API key de Anthropic + directorios de la biblioteca

**Files:**
- Modify: `studio/backend/app/config.py`
- Modify: `studio/backend/requirements.txt`

**Interfaces:**
- Produces: `Settings.anthropic_api_key: str`, `Settings.fable_model: str`, `Settings.fable_rate_limit_per_min: int`, `Settings.manim_extensions_dir: Path`, `Settings.pending_primitives_dir: Path` — consumidos por `fable.py` y `primitives.py` (Tasks 7-8).

- [ ] **Step 1: Añadir los campos a `Settings.__init__`**

En `studio/backend/app/config.py`, añadir al final de `__init__` (después de la línea de `ai_rate_limit_per_min`):

```python
        # Fable 5 (Anthropic) — genera primitivas nuevas de Manim para la
        # biblioteca curada de studio/content/manim_extensions/. Feature-flag:
        # sin API key, el asistente queda deshabilitado y la app funciona igual.
        self.anthropic_api_key = os.environ.get("MS_ANTHROPIC_API_KEY", "")
        self.fable_model = os.environ.get("MS_FABLE_MODEL", "claude-fable-5")
        self.fable_rate_limit_per_min = int(os.environ.get("MS_FABLE_RATE_LIMIT", "5"))
        self.manim_extensions_dir = Path(os.environ.get(
            "MS_MANIM_EXTENSIONS_DIR",
            str(self.workspace / "studio" / "content" / "manim_extensions")))
        self.pending_primitives_dir = Path(os.environ.get(
            "MS_PENDING_PRIMITIVES_DIR", str(self.workspace / "pending_primitives")))
```

- [ ] **Step 2: Añadir el SDK de Anthropic a requirements**

En `studio/backend/requirements.txt`, añadir una línea (mismo formato que `google-genai>=1.0`):

```
anthropic>=0.72
```

- [ ] **Step 3: Instalar y verificar el import**

Run: `cd /var/www/codeaerospace_contenido/studio/backend && ./venv/bin/pip install -r requirements.txt`
Expected: instala `anthropic` sin error.

Run: `./venv/bin/python -c "import anthropic; print(anthropic.__version__)"`
Expected: imprime una versión >= 0.72.0.

- [ ] **Step 4: Commit**

```bash
git add studio/backend/app/config.py studio/backend/requirements.txt
git commit -m "feat: configuración de Fable 5 (Anthropic) y rutas de la biblioteca de primitivas"
```

---

### Task 7: `studio/backend/app/fable.py` — cliente de Fable 5

**Files:**
- Create: `studio/backend/app/fable.py`
- Test: `studio/backend/tests/test_fable.py`

**Interfaces:**
- Consumes: `Settings` (Task 6: `anthropic_api_key`, `fable_model`, `fable_rate_limit_per_min`).
- Produces: `FableError(status: int, detail: str)`; `FableAssistant(cfg).enabled -> bool`; `async FableAssistant(cfg).propose_primitive(description: str, feedback: str | None = None, previous_code: str | None = None) -> dict` con claves `primitive_code`, `demo_scene_code`, `explanation` (usado por `primitives.py`, Task 8).

- [ ] **Step 1: Escribir el test (falla porque `fable.py` no existe)**

Crear `studio/backend/tests/test_fable.py`. Nota: `propose_primitive` es `async def`, pero la suite del proyecto no usa `pytest-asyncio` en ningún otro archivo (todo pasa por `TestClient` síncrono) — aquí se ejecuta la corrutina con `asyncio.run(...)` desde funciones de test normales (`def`, sin `async`), sin añadir dependencias nuevas:

```python
"""Pruebas del cliente Fable 5. El SDK de Anthropic SIEMPRE va mockeado:
estos tests no deben tocar la red ni generar coste."""

import asyncio

import pytest


@pytest.fixture()
def fable_client(client, monkeypatch):
    """Cliente autenticado con Fable 5 habilitado (API key dummy)."""
    from .conftest import TEST_PASSWORD
    r = client.post("/api/login", json={"username": "tester",
                                        "password": TEST_PASSWORD})
    assert r.status_code == 200
    monkeypatch.setenv("MS_ANTHROPIC_API_KEY", "dummy-key-for-tests")
    from app.main import fable_assistant
    fable_assistant.cfg.anthropic_api_key = "dummy-key-for-tests"
    return client


def _mock_call(monkeypatch, text, record=None):
    from app.main import fable_assistant

    def fake(user):
        if record is not None:
            record["user"] = user
        return text

    monkeypatch.setattr(fable_assistant, "_call_model", fake)


FAKE_RESPONSE = (
    "Un efecto de disolucion en particulas.\n\n"
    "```python:primitive\n"
    "class Dissolve:\n"
    "    def __init__(self):\n"
    "        pass\n"
    "```\n"
    "```python:demo\n"
    "from manim import *\n"
    "from primitive import Dissolve\n\n\n"
    "class DemoScene(Scene):\n"
    "    def construct(self):\n"
    "        self.wait(1)\n"
    "```\n"
)


def test_disabled_by_default(client):
    from app.fable import FableError
    from app.main import fable_assistant
    assert fable_assistant.enabled is False
    with pytest.raises(FableError):
        asyncio.run(fable_assistant.propose_primitive("algo"))


def test_propose_primitive_extracts_both_blocks(fable_client, monkeypatch):
    from app.main import fable_assistant
    rec = {}
    _mock_call(monkeypatch, FAKE_RESPONSE, record=rec)
    result = asyncio.run(fable_assistant.propose_primitive("una disolucion en particulas"))
    assert "class Dissolve" in result["primitive_code"]
    assert "class DemoScene(Scene)" in result["demo_scene_code"]
    assert "disolucion" in rec["user"]


def test_propose_primitive_includes_feedback_and_previous_code(fable_client, monkeypatch):
    from app.main import fable_assistant
    rec = {}
    _mock_call(monkeypatch, FAKE_RESPONSE, record=rec)
    asyncio.run(fable_assistant.propose_primitive(
        "una disolucion en particulas",
        feedback="hazlo mas lento",
        previous_code="class Dissolve:\n    pass\n",
    ))
    assert "hazlo mas lento" in rec["user"]
    assert "class Dissolve" in rec["user"]


def test_propose_primitive_missing_blocks_raises(fable_client, monkeypatch):
    from app.fable import FableError
    _mock_call(monkeypatch, "solo texto sin bloques de codigo")
    from app.main import fable_assistant
    with pytest.raises(FableError):
        asyncio.run(fable_assistant.propose_primitive("algo"))


def test_rate_limit(fable_client, monkeypatch):
    from app.main import fable_assistant
    from app.fable import FableError
    _mock_call(monkeypatch, FAKE_RESPONSE)
    fable_assistant.limiter.per_minute = 2
    try:
        asyncio.run(fable_assistant.propose_primitive("a"))
        asyncio.run(fable_assistant.propose_primitive("b"))
        with pytest.raises(FableError) as exc_info:
            asyncio.run(fable_assistant.propose_primitive("c"))
        assert exc_info.value.status == 429
    finally:
        fable_assistant.limiter.per_minute = 5
        fable_assistant.limiter._hits.clear()
```

- [ ] **Step 2: Correr el test para verificar que falla**

Run: `cd /var/www/codeaerospace_contenido/studio/backend && ./venv/bin/pytest tests/test_fable.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.fable'` (o similar, porque `app.main` tampoco expone `fable_assistant` todavía).

- [ ] **Step 3: Implementar `studio/backend/app/fable.py`**

Crear `studio/backend/app/fable.py`:

```python
"""Fable 5 (Anthropic): genera primitivas nuevas de Manim (Mobjects o
Animations autocontenidos) a partir de una descripcion en lenguaje natural,
para la biblioteca curada de studio/content/manim_extensions/.

Feature-flag: sin API key de Anthropic configurada, el asistente queda
deshabilitado y el resto de la app funciona igual (igual patron que ai.py
con Vertex AI).
"""

import asyncio
import re
import time
from collections import deque

from .config import Settings

MAX_DESCRIPTION_CHARS = 4_000
MAX_FEEDBACK_CHARS = 2_000
MAX_PREVIOUS_CODE_CHARS = 20_000
REQUEST_TIMEOUT_S = 600  # Fable 5 puede tardar varios minutos por turno

_PRIMITIVE_FENCE_RE = re.compile(r"```python:primitive\s*\n(.*?)```", re.DOTALL)
_DEMO_FENCE_RE = re.compile(r"```python:demo\s*\n(.*?)```", re.DOTALL)

SYSTEM_PROMPT = (
    "Eres un experto en Manim Community Edition (v0.20+) que investiga "
    "tecnicas de animacion poco comunes o nunca antes vistas. El usuario "
    "describe un efecto visual nuevo; devuelve DOS bloques de codigo Python "
    "en tu respuesta:\n\n"
    "1. Un bloque marcado exactamente ```python:primitive``` con UNA unica "
    "clase autocontenida (Mobject o Animation de Manim CE) que implemente el "
    "efecto. Debe ser importable como `from primitive import <NombreClase>`, "
    "sin dependencias externas, sin red ni acceso a archivos.\n"
    "2. Un bloque marcado exactamente ```python:demo``` con un script "
    "completo: `from manim import *`, la linea "
    "`from primitive import <NombreClase>` y EXACTAMENTE una clase que "
    "herede de Scene (o variante de Scene) que use la primitiva para "
    "mostrar el efecto en menos de 15 segundos de animacion.\n\n"
    "Responde con una linea de explicacion breve antes de ambos bloques, y "
    "nada de texto adicional despues."
)


class FableError(Exception):
    def __init__(self, status: int, detail: str) -> None:
        super().__init__(detail)
        self.status = status
        self.detail = detail


class FableRateLimiter:
    """~N peticiones/min. Mismo diseño que AIRateLimiter (ai.py)."""

    def __init__(self, per_minute: int) -> None:
        self.per_minute = per_minute
        self._hits: deque[float] = deque()

    def check(self) -> None:
        now = time.time()
        while self._hits and now - self._hits[0] > 60:
            self._hits.popleft()
        if len(self._hits) >= self.per_minute:
            wait = int(60 - (now - self._hits[0])) + 1
            raise FableError(429, f"Limite de Fable 5 alcanzado. Espera {wait} s.")
        self._hits.append(now)


class FableAssistant:
    def __init__(self, cfg: Settings) -> None:
        self.cfg = cfg
        self.limiter = FableRateLimiter(cfg.fable_rate_limit_per_min)
        self._client = None

    @property
    def enabled(self) -> bool:
        return bool(self.cfg.anthropic_api_key)

    def _get_client(self):
        if self._client is None:
            import anthropic
            self._client = anthropic.Anthropic(api_key=self.cfg.anthropic_api_key)
        return self._client

    def _call_model(self, user: str) -> str:
        """Llamada bloqueante al SDK (se ejecuta en thread; mockeada en tests)."""
        client = self._get_client()
        resp = client.messages.create(
            model=self.cfg.fable_model,
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            output_config={"effort": "high"},
            betas=["server-side-fallback-2026-06-01"],
            fallbacks=[{"model": "claude-opus-4-8"}],
            messages=[{"role": "user", "content": user}],
        )
        return "".join(b.text for b in resp.content if b.type == "text")

    async def propose_primitive(self, description: str, feedback: str | None = None,
                                previous_code: str | None = None) -> dict:
        if not self.enabled:
            raise FableError(503, "Fable 5 no configurado")
        self.limiter.check()

        user = f"DESCRIPCION DEL EFECTO:\n{_clip(description, MAX_DESCRIPTION_CHARS)}"
        if previous_code and feedback:
            user += (
                "\n\nVERSION ANTERIOR DE LA PRIMITIVA (rechazada):\n"
                f"{_clip(previous_code, MAX_PREVIOUS_CODE_CHARS)}\n\n"
                f"FEEDBACK PARA CORREGIR:\n{_clip(feedback, MAX_FEEDBACK_CHARS)}"
            )

        try:
            text = await asyncio.wait_for(
                asyncio.to_thread(self._call_model, user),
                timeout=REQUEST_TIMEOUT_S + 30)
        except asyncio.TimeoutError:
            raise FableError(504, "Fable 5 no respondio a tiempo")
        except FableError:
            raise
        except Exception as e:
            raise FableError(502, f"Error de Fable 5: {type(e).__name__}: {e}")

        primitive_code = _extract(text, _PRIMITIVE_FENCE_RE)
        demo_code = _extract(text, _DEMO_FENCE_RE)
        if not primitive_code or not demo_code:
            raise FableError(502,
                             "Fable 5 no devolvio los dos bloques de codigo esperados")

        explanation = text.split("```")[0].strip()
        return {"primitive_code": primitive_code, "demo_scene_code": demo_code,
                "explanation": explanation}


def _clip(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n… [truncado]"


def _extract(text: str, pattern: re.Pattern) -> str:
    m = pattern.search(text)
    return (m.group(1).strip() + "\n") if m else ""
```

- [ ] **Step 4: Exponer `fable_assistant` en `app/main.py` para que el test lo encuentre**

En `studio/backend/app/main.py`, añadir el import junto a los demás (línea 15, junto a `from .ai import AIError, Assistant`):

```python
from .fable import FableAssistant
```

Y añadir la instancia junto a `assistant = Assistant(cfg)` (línea 36):

```python
fable_assistant = FableAssistant(cfg)
```

(El resto de `main.py` —endpoints, `/api/me`— se completa en la Task 9; por ahora solo se expone la instancia para que el test de esta tarea pueda importarla.)

- [ ] **Step 5: Correr el test y verificar que pasa**

Run: `cd /var/www/codeaerospace_contenido/studio/backend && ./venv/bin/pytest tests/test_fable.py -v`
Expected: todos los tests en PASS.

- [ ] **Step 6: Commit**

```bash
git add studio/backend/app/fable.py studio/backend/app/main.py studio/backend/tests/test_fable.py studio/backend/requirements.txt
git commit -m "feat: cliente Fable 5 (fable.py) para proponer primitivas de Manim"
```

---

### Task 8: `studio/backend/app/primitives.py` — orquestador de propuestas

**Files:**
- Create: `studio/backend/app/primitives.py`
- Test: `studio/backend/tests/test_primitives.py`

**Interfaces:**
- Consumes: `Settings` (Task 6), `FableAssistant.propose_primitive` (Task 7), `JobManager.create_job`/`JobManager.db.get_job` (ya existentes en `jobs.py`), `EventBus.publish` (ya existente en `events.py`), `detect_scenes` (ya existente en `scenes.py`).
- Produces: `PrimitiveError(status, detail)`; `PrimitiveManager(cfg, fable, jobs, bus)` con métodos síncronos `propose(slug, description) -> dict`, `iterate(proposal_id, feedback) -> dict`, `approve(proposal_id) -> dict`, `reject(proposal_id) -> dict`, `list_proposals() -> list[dict]`, `get_proposal(proposal_id) -> dict | None` — consumidos por los endpoints de `main.py` (Task 9).

- [ ] **Step 1: Escribir el test**

Crear `studio/backend/tests/test_primitives.py`. `propose()`/`iterate()`/`approve()`/`reject()` son métodos sincronos, pero `propose()`/`iterate()` internamente hacen `asyncio.create_task(...)`, lo que requiere un event loop en ejecucion en el momento de la llamada. Para no introducir `pytest-asyncio` (la suite no lo usa en ningún otro archivo), cada test envuelve su lógica en una función `async def _run()` interna, ejecutada con `asyncio.run(_run())` desde una función de test normal (`def`, sin `async`) — así `create_task` sí encuentra un loop activo (el que crea `asyncio.run`) y el `await asyncio.sleep(...)` de espera corre sobre ESE mismo loop:

```python
"""Pruebas del orquestador de propuestas de primitivas. Fable 5 y el render
van siempre mockeados/mediante el JobManager real sobre un workspace temporal
(sin Docker real: se fuerza el estado del job manipulando la DB)."""

import asyncio

import pytest


FAKE_RESULT = {
    "primitive_code": "class Dissolve:\n    pass\n",
    "demo_scene_code": (
        "from manim import *\n"
        "from primitive import Dissolve\n\n\n"
        "class DemoScene(Scene):\n"
        "    def construct(self):\n"
        "        self.wait(1)\n"
    ),
    "explanation": "Una disolucion en particulas.",
}


@pytest.fixture()
def manager_with_deps(client, tmp_path, monkeypatch):
    """PrimitiveManager real, con FableAssistant.propose_primitive mockeado
    y el JobManager/EventBus reales de la app ya cargada por `client`."""
    from app.main import primitives_manager, fable_assistant

    async def fake_propose(description, feedback=None, previous_code=None):
        return FAKE_RESULT

    monkeypatch.setattr(fable_assistant, "propose_primitive", fake_propose)
    monkeypatch.setattr(fable_assistant, "enabled", True)
    return primitives_manager


async def _wait_until(manager, proposal_id, predicate, attempts=50):
    for _ in range(attempts):
        await asyncio.sleep(0.02)
        current = manager.get_proposal(proposal_id)
        if predicate(current):
            return current
    raise AssertionError(f"la propuesta {proposal_id} nunca cumplio la condicion esperada")


def test_propose_creates_proposal_and_job(manager_with_deps):
    async def _run():
        proposal = manager_with_deps.propose("disolucion-particulas", "un efecto de disolucion")
        assert proposal["status"] == "generating"
        current = await _wait_until(manager_with_deps, proposal["id"],
                                    lambda p: p["status"] != "generating")
        assert current["status"] == "rendering"
        assert current["job_id"] is not None
        assert "class Dissolve" in current["primitive_code"]

        staging = manager_with_deps.cfg.pending_primitives_dir / proposal["id"] / "primitive.py"
        assert staging.is_file()
        assert "class Dissolve" in staging.read_text()

    asyncio.run(_run())


def test_approve_requires_job_done(manager_with_deps):
    async def _run():
        proposal = manager_with_deps.propose("otra-primitiva", "otro efecto")
        await _wait_until(manager_with_deps, proposal["id"], lambda p: p["job_id"])
        with pytest.raises(Exception):
            manager_with_deps.approve(proposal["id"])  # job aun no "done"

    asyncio.run(_run())


def test_approve_writes_to_manim_extensions(manager_with_deps):
    async def _run():
        proposal = manager_with_deps.propose("aprobada-slug", "efecto aprobable")
        current = await _wait_until(manager_with_deps, proposal["id"], lambda p: p["job_id"])

        manager_with_deps.jobs.db.update_job(current["job_id"], status="done")

        result = manager_with_deps.approve(proposal["id"])
        assert result["status"] == "approved"
        target = manager_with_deps.cfg.manim_extensions_dir / "aprobada-slug.py"
        assert target.is_file()
        assert "class Dissolve" in target.read_text()
        # el staging se limpia tras aprobar
        assert not (manager_with_deps.cfg.pending_primitives_dir / proposal["id"]).exists()

    asyncio.run(_run())


def test_get_proposal_unknown_returns_none(manager_with_deps):
    assert manager_with_deps.get_proposal("no-existe") is None


def test_reject_unknown_raises(manager_with_deps):
    from app.primitives import PrimitiveError
    with pytest.raises(PrimitiveError) as exc_info:
        manager_with_deps.reject("no-existe")
    assert exc_info.value.status == 404
```

- [ ] **Step 2: Correr el test para verificar que falla**

Run: `cd /var/www/codeaerospace_contenido/studio/backend && ./venv/bin/pytest tests/test_primitives.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.primitives'` (y `ImportError: cannot import name 'primitives_manager'`).

- [ ] **Step 3: Implementar `studio/backend/app/primitives.py`**

Crear `studio/backend/app/primitives.py`:

```python
"""Orquestador de propuestas de primitivas de Manim generadas por Fable 5.

Cada propuesta vive en memoria + un directorio de staging efimero (fuera de
git, mismo patron que render_jobs/) hasta que se aprueba (se copia a
studio/content/manim_extensions/) o se rechaza (se borra el staging). Sin
persistencia en SQLite: si el backend se reinicia, las propuestas pendientes
se pierden — aceptable para una herramienta experimental de uso esporadico
con aprobacion humana obligatoria.
"""

import asyncio
import shutil
import time
import uuid
from pathlib import Path

from .config import Settings
from .events import EventBus
from .fable import FableAssistant, FableError
from .jobs import JobManager
from .scenes import detect_scenes

_PROPOSAL_KEYS = ("id", "slug", "description", "status", "primitive_code",
                  "demo_scene_code", "explanation", "job_id", "error",
                  "created_at", "feedback_history")


class PrimitiveError(Exception):
    def __init__(self, status: int, detail: str) -> None:
        super().__init__(detail)
        self.status = status
        self.detail = detail


def proposal_public(p: dict) -> dict:
    return {k: p.get(k) for k in _PROPOSAL_KEYS}


class PrimitiveManager:
    def __init__(self, cfg: Settings, fable: FableAssistant, jobs: JobManager,
                 bus: EventBus) -> None:
        self.cfg = cfg
        self.fable = fable
        self.jobs = jobs
        self.bus = bus
        self.proposals: dict[str, dict] = {}

    # ── API publica ──────────────────────────────────────────────────────

    def list_proposals(self) -> list[dict]:
        return sorted((proposal_public(p) for p in self.proposals.values()),
                      key=lambda p: p["created_at"], reverse=True)

    def get_proposal(self, proposal_id: str) -> dict | None:
        p = self.proposals.get(proposal_id)
        return proposal_public(p) if p else None

    def propose(self, slug: str, description: str) -> dict:
        if not self.fable.enabled:
            raise PrimitiveError(503, "Fable 5 no configurado")
        proposal_id = uuid.uuid4().hex[:16]
        proposal = {
            "id": proposal_id, "slug": slug, "description": description,
            "status": "generating", "primitive_code": None,
            "demo_scene_code": None, "explanation": None, "job_id": None,
            "error": None, "created_at": time.time(), "feedback_history": [],
        }
        self.proposals[proposal_id] = proposal
        self._publish(proposal_id)
        asyncio.create_task(
            self._generate_and_render(proposal_id, description, None, None))
        return proposal_public(proposal)

    def iterate(self, proposal_id: str, feedback: str) -> dict:
        proposal = self._get_or_404(proposal_id)
        if proposal["status"] == "generating":
            raise PrimitiveError(409, "Ya hay una generacion en curso para esta propuesta")
        proposal["feedback_history"].append(feedback)
        previous_code = proposal["primitive_code"]
        description = proposal["description"]
        proposal["status"] = "generating"
        proposal["error"] = None
        self._publish(proposal_id)
        asyncio.create_task(
            self._generate_and_render(proposal_id, description, feedback, previous_code))
        return proposal_public(proposal)

    def approve(self, proposal_id: str) -> dict:
        proposal = self._get_or_404(proposal_id)
        if proposal["status"] != "rendering" or self._job_status(proposal["job_id"]) != "done":
            raise PrimitiveError(409, "La propuesta no tiene un render listo para aprobar")
        target = self.cfg.manim_extensions_dir / f"{proposal['slug']}.py"
        if target.is_file():
            raise PrimitiveError(
                409, f"Ya existe una primitiva con el slug '{proposal['slug']}'")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(proposal["primitive_code"], encoding="utf-8")
        proposal["status"] = "approved"
        self._publish(proposal_id)
        self._cleanup_staging(proposal_id)
        return proposal_public(proposal)

    def reject(self, proposal_id: str) -> dict:
        proposal = self._get_or_404(proposal_id)
        if proposal["status"] == "generating":
            raise PrimitiveError(409, "Ya hay una generacion en curso para esta propuesta")
        proposal["status"] = "rejected"
        self._publish(proposal_id)
        self._cleanup_staging(proposal_id)
        return proposal_public(proposal)

    # ── internos ─────────────────────────────────────────────────────────

    async def _generate_and_render(self, proposal_id: str, description: str,
                                   feedback: str | None, previous_code: str | None) -> None:
        proposal = self.proposals[proposal_id]
        try:
            result = await self.fable.propose_primitive(
                description, feedback=feedback, previous_code=previous_code)
        except FableError as e:
            proposal["status"] = "failed"
            proposal["error"] = e.detail
            self._publish(proposal_id)
            return
        except Exception as e:  # nunca debe morir el task en segundo plano
            proposal["status"] = "failed"
            proposal["error"] = f"error interno: {e}"
            self._publish(proposal_id)
            return

        proposal["primitive_code"] = result["primitive_code"]
        proposal["demo_scene_code"] = result["demo_scene_code"]
        proposal["explanation"] = result["explanation"]

        try:
            scenes = detect_scenes(result["demo_scene_code"])
        except ValueError as e:
            proposal["status"] = "failed"
            proposal["error"] = f"escena demo invalida: {e}"
            self._publish(proposal_id)
            return
        if len(scenes) != 1:
            proposal["status"] = "failed"
            proposal["error"] = (
                f"la escena demo debe definir exactamente 1 escena (encontradas: {len(scenes)})")
            self._publish(proposal_id)
            return
        scene_name = scenes[0]

        try:
            staging = self._staging_dir(proposal_id)
            staging.mkdir(parents=True, exist_ok=True)
            (staging / "primitive.py").write_text(
                result["primitive_code"], encoding="utf-8")

            bootstrap = f'import sys\nsys.path.insert(0, "/workspace/pending_primitives/{proposal_id}")\n\n'
            full_script = bootstrap + result["demo_scene_code"]

            job = self.jobs.create_job(full_script, scene_name, "ql",
                                       self.cfg.default_timeout)
        except Exception as e:
            proposal["status"] = "failed"
            proposal["error"] = f"no se pudo lanzar el render de muestra: {e}"
            self._publish(proposal_id)
            return

        proposal["job_id"] = job["id"]
        proposal["status"] = "rendering"
        self._publish(proposal_id)

    def _staging_dir(self, proposal_id: str) -> Path:
        return self.cfg.pending_primitives_dir / proposal_id

    def _cleanup_staging(self, proposal_id: str) -> None:
        shutil.rmtree(self._staging_dir(proposal_id), ignore_errors=True)

    def _job_status(self, job_id: str | None) -> str | None:
        if not job_id:
            return None
        job = self.jobs.db.get_job(job_id)
        return job["status"] if job else None

    def _get_or_404(self, proposal_id: str) -> dict:
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            raise PrimitiveError(404, "Propuesta no encontrada")
        return proposal

    def _publish(self, proposal_id: str) -> None:
        proposal = self.proposals.get(proposal_id)
        if proposal:
            self.bus.publish({"type": "primitive", "proposal": proposal_public(proposal)})
```

- [ ] **Step 4: Exponer `primitives_manager` en `app/main.py`**

En `studio/backend/app/main.py`, añadir el import junto a `from .fable import FableAssistant` (añadido en la Task 7):

```python
from .primitives import PrimitiveManager
```

Y la instancia justo despues de `fable_assistant = FableAssistant(cfg)`:

```python
primitives_manager = PrimitiveManager(cfg, fable_assistant, manager, bus)
```

(Los endpoints HTTP que usan `primitives_manager` se añaden en la Task 9.)

- [ ] **Step 5: Correr el test y verificar que pasa**

Run: `cd /var/www/codeaerospace_contenido/studio/backend && ./venv/bin/pytest tests/test_primitives.py -v`
Expected: todos los tests en PASS.

- [ ] **Step 6: Commit**

```bash
git add studio/backend/app/primitives.py studio/backend/app/main.py studio/backend/tests/test_primitives.py
git commit -m "feat: orquestador de propuestas de primitivas (primitives.py)"
```

---

### Task 9: endpoints FastAPI de `/api/primitives`

**Files:**
- Modify: `studio/backend/app/main.py`
- Test: `studio/backend/tests/test_primitives_api.py`

**Interfaces:**
- Consumes: `primitives_manager` (Task 8), `fable_assistant` (Task 7).
- Produces: `GET /api/primitives`, `GET /api/primitives/{id}`, `POST /api/primitives`, `POST /api/primitives/{id}/approve`, `POST /api/primitives/{id}/reject`, `POST /api/primitives/{id}/iterate`; `/api/me` incluye `fable_enabled`.

- [ ] **Step 1: Escribir el test**

Crear `studio/backend/tests/test_primitives_api.py`. El task en segundo plano (`asyncio.create_task` dentro de `PrimitiveManager.propose`) corre sobre el event loop interno que `TestClient` mantiene en su propio hilo durante todo el `with TestClient(...) as c:` — un `time.sleep()` real en el hilo del test le da tiempo de avanzar; no hace falta (ni sirve) `asyncio.sleep`/`pytest-asyncio` aquí, porque el hilo del test no comparte ese loop:

```python
"""Pruebas de los endpoints /api/primitives. Fable 5 mockeado."""

import time

import pytest


@pytest.fixture()
def fable_enabled(authed, monkeypatch):
    from app.main import fable_assistant

    async def fake_propose(description, feedback=None, previous_code=None):
        return {
            "primitive_code": "class Dissolve:\n    pass\n",
            "demo_scene_code": (
                "from manim import *\n"
                "from primitive import Dissolve\n\n\n"
                "class DemoScene(Scene):\n"
                "    def construct(self):\n"
                "        self.wait(1)\n"
            ),
            "explanation": "explicacion",
        }

    monkeypatch.setattr(fable_assistant, "propose_primitive", fake_propose)
    monkeypatch.setattr(fable_assistant, "enabled", True)
    return authed


def test_primitives_requires_auth(client):
    assert client.get("/api/primitives").status_code == 401
    assert client.post("/api/primitives", json={"slug": "x", "description": "y"}).status_code == 401


def test_me_reports_fable_flag(authed):
    assert authed.get("/api/me").json()["fable_enabled"] is False


def test_propose_disabled_returns_503(authed):
    r = authed.post("/api/primitives", json={"slug": "x", "description": "un efecto"})
    assert r.status_code == 503


def _wait_until_rendering(client, proposal_id, attempts=50):
    for _ in range(attempts):
        time.sleep(0.02)
        r = client.get(f"/api/primitives/{proposal_id}")
        if r.json()["status"] != "generating":
            return r.json()
    raise AssertionError("la propuesta nunca salio de 'generating'")


def test_propose_list_and_get(fable_enabled):
    r = fable_enabled.post("/api/primitives",
                           json={"slug": "disolucion", "description": "un efecto de disolucion"})
    assert r.status_code == 201
    proposal_id = r.json()["id"]
    assert r.json()["status"] == "generating"

    current = _wait_until_rendering(fable_enabled, proposal_id)
    assert current["status"] == "rendering"
    assert current["job_id"]

    listed = fable_enabled.get("/api/primitives").json()["proposals"]
    assert any(p["id"] == proposal_id for p in listed)


def test_approve_flow(fable_enabled):
    from app.main import primitives_manager
    r = fable_enabled.post("/api/primitives",
                           json={"slug": "aprobar-api", "description": "otro efecto"})
    proposal_id = r.json()["id"]
    current = _wait_until_rendering(fable_enabled, proposal_id)
    primitives_manager.jobs.db.update_job(current["job_id"], status="done")

    r = fable_enabled.post(f"/api/primitives/{proposal_id}/approve")
    assert r.status_code == 200
    assert r.json()["status"] == "approved"

    target = primitives_manager.cfg.manim_extensions_dir / "aprobar-api.py"
    assert target.is_file()


def test_reject_with_feedback_relaunches(fable_enabled):
    r = fable_enabled.post("/api/primitives",
                           json={"slug": "iterar-api", "description": "otro efecto mas"})
    proposal_id = r.json()["id"]
    _wait_until_rendering(fable_enabled, proposal_id)

    r = fable_enabled.post(f"/api/primitives/{proposal_id}/iterate",
                           json={"feedback": "hazlo mas lento"})
    assert r.status_code == 200
    assert r.json()["status"] == "generating"


def test_get_unknown_proposal_404(authed):
    assert authed.get("/api/primitives/no-existe").status_code == 404
```

- [ ] **Step 2: Correr el test para verificar que falla**

Run: `cd /var/www/codeaerospace_contenido/studio/backend && ./venv/bin/pytest tests/test_primitives_api.py -v`
Expected: FAIL — 404 en rutas que no existen aún, y `/api/me` sin `fable_enabled`.

- [ ] **Step 3: Añadir los endpoints y el flag en `/api/me`**

En `studio/backend/app/main.py`, modificar `/api/me` (línea ~125-130):

```python
@app.get("/api/me")
async def me(request: Request):
    if session_valid(cfg, request):
        return {"authenticated": True, "user": cfg.admin_user,
                "ai_enabled": assistant.enabled,
                "fable_enabled": fable_assistant.enabled}
    return {"authenticated": False}
```

Añadir, después de la sección `# ── asistente IA ──` (después del endpoint `ai_generate`, antes de `# ── monitoreo / SSE ──`), una nueva sección completa:

```python
# ── biblioteca de primitivas (Fable 5) ────────────────────────────────────────

from .primitives import PrimitiveError  # noqa: E402  (junto a los otros imports arriba, ver Step 4)


class PrimitiveProposeBody(BaseModel):
    slug: str = Field(pattern=r"^[a-z0-9][a-z0-9-]*$", max_length=64)
    description: str = Field(min_length=3, max_length=4_000)


class PrimitiveFeedbackBody(BaseModel):
    feedback: str = Field(min_length=1, max_length=2_000)


@app.get("/api/primitives")
async def list_primitives(_=Depends(require_auth)):
    return {"proposals": primitives_manager.list_proposals()}


@app.get("/api/primitives/{proposal_id}")
async def get_primitive(proposal_id: str, _=Depends(require_auth)):
    proposal = primitives_manager.get_proposal(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Propuesta no encontrada")
    return proposal


@app.post("/api/primitives", status_code=201)
async def propose_primitive(body: PrimitiveProposeBody, _=Depends(require_auth)):
    try:
        return primitives_manager.propose(body.slug, body.description)
    except PrimitiveError as e:
        raise HTTPException(status_code=e.status, detail=e.detail)


@app.post("/api/primitives/{proposal_id}/approve")
async def approve_primitive(proposal_id: str, _=Depends(require_auth)):
    try:
        return primitives_manager.approve(proposal_id)
    except PrimitiveError as e:
        raise HTTPException(status_code=e.status, detail=e.detail)


@app.post("/api/primitives/{proposal_id}/reject")
async def reject_primitive(proposal_id: str, _=Depends(require_auth)):
    try:
        return primitives_manager.reject(proposal_id)
    except PrimitiveError as e:
        raise HTTPException(status_code=e.status, detail=e.detail)


@app.post("/api/primitives/{proposal_id}/iterate")
async def iterate_primitive(proposal_id: str, body: PrimitiveFeedbackBody,
                            _=Depends(require_auth)):
    try:
        return primitives_manager.iterate(proposal_id, body.feedback)
    except PrimitiveError as e:
        raise HTTPException(status_code=e.status, detail=e.detail)
```

Nota: mover el `from .primitives import PrimitiveError` real al bloque de imports superior del archivo (junto a `from .jobs import ...`), no dejarlo inline — el snippet lo muestra ahí solo para ubicar el punto de inserción; en el archivo final debe quedar arriba con el resto de imports (`from .primitives import PrimitiveError, PrimitiveManager`, sustituyendo el import de solo `PrimitiveManager` añadido en la Task 8).

- [ ] **Step 4: Ajustar el import combinado**

En la parte superior de `studio/backend/app/main.py`, dejar un único import de `primitives`:

```python
from .primitives import PrimitiveError, PrimitiveManager
```

(sustituye el `from .primitives import PrimitiveManager` que la Task 8 había añadido).

- [ ] **Step 5: Correr el test y verificar que pasa**

Run: `cd /var/www/codeaerospace_contenido/studio/backend && ./venv/bin/pytest tests/test_primitives_api.py -v`
Expected: todos los tests en PASS.

- [ ] **Step 6: Correr la suite completa para confirmar que nada se rompió**

Run: `cd /var/www/codeaerospace_contenido/studio/backend && ./venv/bin/pytest -v`
Expected: todos los tests en PASS (incluidos los ya existentes: `test_ai.py`, `test_animations.py`, `test_auth.py`, `test_jobs_api.py`, `test_lessons.py`, `test_library.py`, `test_metrics_history.py`, `test_scenes.py`, y los nuevos `test_fable.py`, `test_primitives.py`, `test_primitives_api.py`).

- [ ] **Step 7: Commit**

```bash
git add studio/backend/app/main.py studio/backend/tests/test_primitives_api.py
git commit -m "feat: endpoints /api/primitives (proponer, listar, aprobar, rechazar, iterar)"
```

---

### Task 10: frontend — cliente API + componente `Primitives.jsx`

**Files:**
- Modify: `studio/frontend/src/api.js`
- Create: `studio/frontend/src/Primitives.jsx`

**Interfaces:**
- Consumes: `api.js` (nuevos métodos), prop `jobs` (ya existente en `App.jsx`) para cruzar `proposal.job_id` con el estado/video del job.
- Produces: componente `<Primitives primitives={...} jobs={...} fableEnabled={...} />` — consumido por `Admin.jsx` (Task 11).

- [ ] **Step 1: Añadir los métodos a `api.js`**

En `studio/frontend/src/api.js`, añadir al objeto `api` (después de `getAnimation`):

```js
  listPrimitives: () => request('GET', '/api/primitives'),
  getPrimitive: (id) => request('GET', `/api/primitives/${id}`),
  proposePrimitive: (payload) => request('POST', '/api/primitives', payload),
  approvePrimitive: (id) => request('POST', `/api/primitives/${id}/approve`),
  rejectPrimitive: (id) => request('POST', `/api/primitives/${id}/reject`),
  iteratePrimitive: (id, feedback) =>
    request('POST', `/api/primitives/${id}/iterate`, { feedback }),
```

- [ ] **Step 2: Crear `studio/frontend/src/Primitives.jsx`**

```jsx
// Panel admin-only: Fable 5 propone primitivas nuevas de Manim (Mobjects /
// Animations) a partir de una descripcion en lenguaje natural. Cada
// propuesta genera un render de muestra por el pipeline normal; solo tras
// aprobacion humana se copia a studio/content/manim_extensions/ (git).

import { useState } from 'react'
import { api } from './api.js'
import { videoUrl } from './api.js'

function statusLabel(proposal, job) {
  if (proposal.status === 'generating') return 'generando con Fable 5…'
  if (proposal.status === 'failed') return `fallo: ${proposal.error || 'error desconocido'}`
  if (proposal.status === 'approved') return 'aprobada'
  if (proposal.status === 'rejected') return 'rechazada'
  if (proposal.status === 'rendering') {
    if (!job) return 'render en cola…'
    if (job.status === 'done') return 'render listo — revisar'
    if (['queued', 'running'].includes(job.status)) return `render ${job.status}…`
    return `render ${job.status}`
  }
  return proposal.status
}

function ProposalCard({ proposal, job, onApprove, onReject, onIterate }) {
  const [feedback, setFeedback] = useState('')
  const [busy, setBusy] = useState(false)
  const renderReady = proposal.status === 'rendering' && job?.status === 'done'
  const canIterate = proposal.status !== 'generating'

  const wrap = async (fn) => {
    setBusy(true)
    try { await fn() } finally { setBusy(false) }
  }

  return (
    <div className="panel" aria-label={`propuesta ${proposal.slug}`}>
      <div className="panel__bar">
        <span className="panel__title">{proposal.slug.toUpperCase()}</span>
        <span className="panel__aside">{statusLabel(proposal, job)}</span>
      </div>
      <p className="drawer__hint">{proposal.description}</p>
      {proposal.explanation && <p className="drawer__hint">{proposal.explanation}</p>}
      {proposal.primitive_code && (
        <pre className="diff diff--plain">{proposal.primitive_code}</pre>
      )}
      {renderReady && (
        <video key={job.id} className="video" controls preload="metadata"
          src={videoUrl(job.id)} />
      )}
      {(renderReady || proposal.status === 'failed') && (
        <div className="admin__actions">
          {renderReady && (
            <button className="btn btn--primary" disabled={busy}
              onClick={() => wrap(() => onApprove(proposal.id))}>
              Aprobar
            </button>
          )}
          <button className="btn btn--tiny btn--danger" disabled={busy}
            onClick={() => wrap(() => onReject(proposal.id))}>
            Rechazar
          </button>
        </div>
      )}
      {canIterate && (
        <div className="admin__actions">
          <textarea className="drawer__prompt" rows={2} value={feedback}
            placeholder="feedback para que Fable 5 corrija esta version…"
            onChange={(e) => setFeedback(e.target.value)} />
          <button className="btn btn--tiny" disabled={busy || feedback.trim().length < 1}
            onClick={() => wrap(async () => {
              await onIterate(proposal.id, feedback)
              setFeedback('')
            })}>
            Iterar con feedback
          </button>
        </div>
      )}
    </div>
  )
}

export default function Primitives({ fableEnabled, primitives, jobs, onChanged }) {
  const [slug, setSlug] = useState('')
  const [description, setDescription] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const jobById = (id) => jobs.find((j) => j.id === id)

  const propose = async () => {
    setBusy(true); setError('')
    try {
      await api.proposePrimitive({ slug, description })
      setSlug(''); setDescription('')
      onChanged()
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }

  const approve = async (id) => { await api.approvePrimitive(id); onChanged() }
  const reject = async (id) => { await api.rejectPrimitive(id); onChanged() }
  const iterate = async (id, feedback) => { await api.iteratePrimitive(id, feedback); onChanged() }

  if (!fableEnabled) {
    return (
      <section className="panel" aria-label="primitivas fable 5">
        <div className="panel__bar"><span className="panel__title">PRIMITIVAS · FABLE 5</span></div>
        <p className="empty">Fable 5 no está configurado (falta la API key de Anthropic).</p>
      </section>
    )
  }

  const validSlug = /^[a-z0-9][a-z0-9-]*$/.test(slug)

  return (
    <>
      <section className="panel" aria-label="proponer primitiva">
        <div className="panel__bar">
          <span className="panel__title">PROPONER PRIMITIVA NUEVA</span>
        </div>
        <p className="drawer__hint">
          Describe un efecto visual nuevo; Fable 5 propone una primitiva de Manim
          (Mobject/Animation) y una escena de muestra, que se renderiza automáticamente
          para tu revisión antes de entrar a la biblioteca.
        </p>
        {error && <p className="notice notice--warn" role="alert">{error}</p>}
        <input className="drawer__prompt" style={{ marginBottom: '0.5rem' }}
          value={slug} placeholder="slug (p. ej. disolucion-particulas)"
          onChange={(e) => setSlug(e.target.value)} />
        <textarea className="drawer__prompt" rows={3} value={description}
          placeholder="p. ej. texto que se disuelve en particulas y forma la siguiente ecuación"
          onChange={(e) => setDescription(e.target.value)} />
        <button className="btn" disabled={busy || !validSlug || description.trim().length < 3}
          onClick={propose}>
          {busy ? 'Enviando…' : 'Proponer a Fable 5'}
        </button>
      </section>

      {primitives.length === 0 ? (
        <p className="empty">Sin propuestas todavía.</p>
      ) : (
        primitives.map((p) => (
          <ProposalCard key={p.id} proposal={p} job={jobById(p.job_id)}
            onApprove={approve} onReject={reject} onIterate={iterate} />
        ))
      )}
    </>
  )
}
```

- [ ] **Step 3: Verificación manual (no hay suite JS en este proyecto)**

Esto se verifica junto con la Task 11 (una vez el componente está montado en `Admin.jsx`) y con la Task 12 (E2E completo).

- [ ] **Step 4: Commit**

```bash
git add studio/frontend/src/api.js studio/frontend/src/Primitives.jsx
git commit -m "feat: componente Primitives.jsx + cliente API para primitivas"
```

---

### Task 11: wiring — nueva pestaña en `Admin.jsx` + SSE en `App.jsx`

**Files:**
- Modify: `studio/frontend/src/App.jsx`
- Modify: `studio/frontend/src/Admin.jsx`

**Interfaces:**
- Consumes: `Primitives.jsx` (Task 10).
- Produces: `App.jsx` mantiene el estado `primitives` (lista) y `fableEnabled` (bool), actualizados vía `/api/me` + `/api/primitives` + eventos SSE `type: 'primitive'`; `Admin.jsx` gana una 4ª pestaña "Primitivas".

- [ ] **Step 1: Añadir estado y fetch de primitivas en `App.jsx`**

En `studio/frontend/src/App.jsx`, añadir junto a los demás `useState` (línea ~19, después de `storage`):

```js
  const [primitives, setPrimitives] = useState([])
```

Añadir junto a `refreshJobs` (después de su definición, línea ~35):

```js
  const refreshPrimitives = useCallback(async () => {
    try {
      const data = await api.listPrimitives()
      setPrimitives(data.proposals)
    } catch { /* fable puede estar deshabilitado o la sesion expiro */ }
  }, [])
```

En `refreshMe` (línea ~38-46), añadir el flag `fableEnabled` junto a `aiEnabled`:

```js
  const [fableEnabled, setFableEnabled] = useState(false)

  const refreshMe = useCallback(async () => {
    try {
      const d = await api.me()
      setAuth(d.authenticated)
      setAiEnabled(Boolean(d.ai_enabled))
      setFableEnabled(Boolean(d.fable_enabled))
    } catch {
      setAuth(false)
    }
  }, [])
```

En el `useEffect` del SSE (línea ~51-78), añadir la carga inicial y el manejo del nuevo tipo de evento:

```js
  useEffect(() => {
    if (auth !== true) return
    refreshJobs()
    refreshPrimitives()
    const es = new EventSource('/api/events')
    esRef.current = es
    es.onmessage = (msg) => {
      const ev = JSON.parse(msg.data)
      if (ev.type === 'metrics') {
        if (ev.host) setMetrics(ev.host)
        if (ev.containers !== undefined) setContainers(ev.containers)
      } else if (ev.type === 'job') {
        setJobs((prev) => {
          const rest = prev.filter((j) => j.id !== ev.job.id)
          return [ev.job, ...rest].sort((a, b) => b.created_at - a.created_at)
        })
        if (!['queued', 'running'].includes(ev.job.status)) refreshJobs()
      } else if (ev.type === 'joblog') {
        setLiveLog((prev) =>
          prev.jobId === ev.job_id
            ? { jobId: ev.job_id, lines: [...prev.lines.slice(-4999), ev.line] }
            : { jobId: ev.job_id, lines: [ev.line] },
        )
      } else if (ev.type === 'primitive') {
        setPrimitives((prev) => {
          const rest = prev.filter((p) => p.id !== ev.proposal.id)
          return [ev.proposal, ...rest].sort((a, b) => b.created_at - a.created_at)
        })
      }
    }
    es.onerror = () => { /* EventSource reintenta solo */ }
    return () => { es.close(); esRef.current = null }
  }, [auth, refreshJobs, refreshPrimitives])
```

Y pasar las nuevas props a `Admin`:

```jsx
        <Admin metrics={metrics} containers={containers} jobs={jobs}
          storage={storage} onJobsChanged={refreshJobs}
          fableEnabled={fableEnabled} primitives={primitives}
          onPrimitivesChanged={refreshPrimitives} />
```

- [ ] **Step 2: Añadir la pestaña "Primitivas" en `Admin.jsx`**

En `studio/frontend/src/Admin.jsx`, añadir el import (junto a `Chart, useHistory, GB`):

```jsx
import Primitives from './Primitives.jsx'
```

Cambiar la firma de `Admin` para aceptar las nuevas props:

```jsx
export default function Admin({ metrics, containers, jobs, storage, onJobsChanged,
  fableEnabled, primitives, onPrimitivesChanged }) {
```

Añadir la 4ª pestaña al array de tabs (línea ~100-104):

```jsx
        {[
          { id: 'salud', label: 'Salud' },
          { id: 'jobs', label: 'Jobs' },
          { id: 'recursos', label: 'Recursos' },
          { id: 'primitivas', label: 'Primitivas' },
        ].map((t) => (
```

Y añadir el bloque de contenido de la pestaña, justo antes del cierre `</main>` (después del bloque `{tab === 'recursos' && ...}`):

```jsx
      {tab === 'primitivas' && (
        <Primitives fableEnabled={fableEnabled} primitives={primitives}
          jobs={jobs} onChanged={onPrimitivesChanged} />
      )}
```

- [ ] **Step 3: Build y verificación manual**

Run: `cd /var/www/codeaerospace_contenido/studio/frontend && npm run build`
Expected: build exitoso sin errores.

Abrir la app en el navegador, entrar a Admin → pestaña "Primitivas", confirmar que:
- Si `fable_enabled` es `false` (sin API key configurada), se muestra el mensaje de "no configurado".
- La pestaña alterna correctamente con Salud/Jobs/Recursos sin romper nada existente.

- [ ] **Step 4: Commit**

```bash
git add studio/frontend/src/App.jsx studio/frontend/src/Admin.jsx
git commit -m "feat: pestaña Primitivas en el panel Admin (Fable 5)"
```

---

### Task 12: configurar la API key y verificación E2E completa

**Files:** (ninguno de código — configuración de despliegue + verificación manual)

- [ ] **Step 1: Añadir la API key de Anthropic al entorno del backend**

En el servidor, añadir a `/etc/manimstudio/env` (ruta ya migrada en la Task 3):

```
MS_ANTHROPIC_API_KEY=sk-ant-...
```

Run: `sudo systemctl restart manimstudio-backend`

- [ ] **Step 2: Confirmar el feature-flag activo**

Run: `curl -s -b cookies.txt https://coderesearch.space/api/me` (con una cookie de sesión válida, o desde el navegador)
Expected: `"fable_enabled": true`.

- [ ] **Step 3: Flujo E2E completo desde el navegador**

1. Entrar a Admin → Primitivas.
2. Proponer una primitiva real (slug + descripción de un efecto concreto).
3. Confirmar que el estado pasa de "generando…" a "render …" y finalmente a "render listo — revisar" (puede tardar varios minutos: Fable 5 + el render).
4. Revisar el código de la primitiva y el video.
5. Aprobar.
6. En una terminal: `git -C /var/www/codeaerospace_contenido status --short` y confirmar que aparece `studio/content/manim_extensions/<slug>.py` como archivo nuevo sin trackear.
7. Repetir el flujo pero **rechazando con feedback** en el paso 4, confirmar que el estado vuelve a "generando…" y produce una nueva versión.

- [ ] **Step 4: No hay commit de código en esta tarea** — es puramente configuración de despliegue + verificación. Si el flujo E2E revela un bug, corregirlo en una tarea/commit separado referenciando esta verificación.
