# Pendientes recomendados — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Cuatro mejoras de operación/UX de ManimStudio: cachear `storage_usage()`, persistir el ring buffer de métricas entre deploys, un botón «Corregir con IA» directo en jobs fallidos, e identidad git en el VPS.

**Architecture:** Cambios independientes y aislados. Backend Python (FastAPI + `JobManager` en memoria, tests con pytest sobre workspace temporal). Frontend React (Vite, sin suite JS: verificación manual). Los tres cambios de código se commitean como sprints atómicos; el `git config` es un comando de una vez en el VPS.

**Tech Stack:** Python 3.13, FastAPI, pytest; React + Vite; git.

## Global Constraints

- Commits atómicos: un commit por tarea/sprint. Mensajes en español, sin tildes en el asunto (estilo del repo).
- JAMÁS commitear `.env`, `gcp-key.json`, `render_jobs/`, ni el snapshot de métricas.
- Suite backend actual: 41 tests en `studio/backend`, correr con el venv (`studio/backend/venv`). No debe romperse ninguno.
- El backend corre como servicio `manimstudio-backend.service`; el runner como `manimstudio-runner.service` (estos cambios NO tocan el runner).
- Identidad git a aplicar en commits nuevos: `Alan R. <ingalanr@gmail.com>`.

---

### Task 1: Cachear `storage_usage()`

**Files:**
- Modify: `studio/backend/app/jobs.py` (cabecera de constantes; `JobManager.__init__`; `storage_usage`; `_finish`; `delete_job`)
- Test: `studio/backend/tests/test_jobs_api.py` (añadir un test)

**Interfaces:**
- Produces: `JobManager.storage_usage() -> int` (firma sin cambios, ahora cacheada); `JobManager._invalidate_storage() -> None` (fuerza recálculo en la próxima lectura).
- Consumes: nada nuevo. Los llamadores existentes (`main.py:156`, `_storage_public()` en `main.py:166`, endpoint de borrado `main.py:243`) no cambian.

- [ ] **Step 1: Write the failing test**

Añadir a `studio/backend/tests/test_jobs_api.py`:

```python
def test_storage_usage_cached_until_invalidated(client):
    from app.main import manager
    root = manager.cfg.render_jobs_dir
    root.mkdir(parents=True, exist_ok=True)

    (root / "a.bin").write_bytes(b"x" * 100)
    assert manager.storage_usage() == 100          # primera lectura: calcula

    (root / "b.bin").write_bytes(b"y" * 50)
    assert manager.storage_usage() == 100          # dentro del TTL: cacheado

    manager._invalidate_storage()
    assert manager.storage_usage() == 150          # invalidado: recalcula

    (root / "c.bin").write_bytes(b"z" * 10)
    manager._storage_cache_at = 0.0                # simula TTL expirado
    assert manager.storage_usage() == 160          # recalcula por TTL
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd studio/backend && venv/bin/pytest tests/test_jobs_api.py::test_storage_usage_cached_until_invalidated -v`
Expected: FAIL con `AttributeError: 'JobManager' object has no attribute '_invalidate_storage'` (o `_storage_cache_at`).

- [ ] **Step 3: Add the module constant**

En `studio/backend/app/jobs.py`, junto a la constante `LOG_BUFFER_MAX` en la cabecera del módulo, añadir:

```python
STORAGE_TTL = 15.0  # s: caché de storage_usage() para no recorrer el FS en cada request
```

- [ ] **Step 4: Initialize cache fields**

En `JobManager.__init__` (después de `self._worker_task: asyncio.Task | None = None`):

```python
        self._storage_cache: int | None = None
        self._storage_cache_at: float = 0.0
```

- [ ] **Step 5: Rewrite `storage_usage` and add `_invalidate_storage`**

Reemplazar el cuerpo de `storage_usage` (actualmente `studio/backend/app/jobs.py:118-129`) por:

```python
    def storage_usage(self) -> int:
        """Bytes totales usados por render_jobs/ (videos, scripts, logs).

        Cacheado STORAGE_TTL s: recorrer el FS en cada GET /api/jobs es
        O(nº archivos). Se invalida al terminar o borrar un job.
        """
        now = time.time()
        if self._storage_cache is not None and now - self._storage_cache_at < STORAGE_TTL:
            return self._storage_cache
        total = 0
        root = self.cfg.render_jobs_dir
        if root.is_dir():
            for p in root.rglob("*"):
                try:
                    if p.is_file():
                        total += p.stat().st_size
                except OSError:
                    pass
        self._storage_cache = total
        self._storage_cache_at = now
        return total

    def _invalidate_storage(self) -> None:
        """Fuerza recálculo de storage_usage() en la próxima lectura."""
        self._storage_cache = None
```

- [ ] **Step 6: Invalidate on job completion**

En `_finish` (`studio/backend/app/jobs.py:219`), al final del método, justo antes de `self._publish_job(job_id)`:

```python
        self._invalidate_storage()  # el tamaño en disco cambió (video nuevo o archivos borrados)
```

- [ ] **Step 7: Invalidate on job deletion**

En `delete_job` (`studio/backend/app/jobs.py:108`), tras `self.delete_job_files(job_id)` y antes de `self.db.delete_job(job_id)`:

```python
        self._invalidate_storage()  # se liberó espacio; la Biblioteca debe reflejar la cuota al instante
```

- [ ] **Step 8: Run the new test and the full suite**

Run: `cd studio/backend && venv/bin/pytest tests/test_jobs_api.py::test_storage_usage_cached_until_invalidated -v && venv/bin/pytest -q`
Expected: el test nuevo PASA y los 41 tests previos siguen en verde (42 total).

- [ ] **Step 9: Commit**

```bash
cd /var/www/codeaerospace_contenido
git add studio/backend/app/jobs.py studio/backend/tests/test_jobs_api.py
git commit -m "Sprint 5: cachear storage_usage (TTL 15s + invalidacion en fin/borrado de job)"
```

---

### Task 2: Persistir snapshot del ring buffer de métricas

**Files:**
- Modify: `studio/backend/app/config.py` (nueva ruta `metrics_snapshot_path`)
- Modify: `studio/backend/app/metrics.py` (`History.save` / `History.load`)
- Modify: `studio/backend/app/main.py` (`lifespan`: load al startup, save al shutdown)
- Modify: `.gitignore` (ignorar el snapshot)
- Test: `studio/backend/tests/test_metrics_history.py` (añadir 3 tests)

**Interfaces:**
- Produces:
  - `Settings.metrics_snapshot_path: Path` (env `MS_METRICS_SNAPSHOT`, por defecto `db_path.parent / "metrics_history.json"`).
  - `History.save(path) -> None` — vuelca `list(self.samples)` a JSON de forma atómica; errores de I/O se loguean y se ignoran.
  - `History.load(path, interval: float, now: float | None = None) -> None` — recarga muestras cuyo `ts` cae dentro de la ventana `maxlen * interval` respecto a `now` (por defecto `time.time()`); archivo ausente o corrupto → no falla.
- Consumes: `cfg.metrics_interval: float` (ya existe) para calcular la ventana en `main.py`.

> **Extensión durante implementación (aprobada por el usuario):** el guardado
> solo-al-apagar NO corre en prod — con una conexión SSE `/api/events` abierta,
> uvicorn se cuelga drenando y systemd hace SIGKILL a los 90 s antes del shutdown
> del `lifespan` (confirmado por `journalctl`; el snapshot nunca se escribía). Se
> añade guardado **periódico** dentro de `_metrics_loop` cada
> `cfg.metrics_snapshot_interval` s (env `MS_METRICS_SNAPSHOT_INTERVAL`, def. 120)
> y se conserva el `save` al apagar. `main.py` importa `time`. Verificación E2E:
> reiniciar el servicio, esperar >1 intervalo, confirmar que
> `metrics_history.json` aparece y es JSON válido no vacío.

- [ ] **Step 1: Write the failing tests**

Añadir a `studio/backend/tests/test_metrics_history.py`:

```python
def test_history_save_and_load_roundtrip(tmp_path):
    from app.metrics import History
    host = {"ts": 5000.0, "cpu_pct": 10.0, "mem": {"pct": 20.0}, "disk": {"pct": 30.0}}
    h = History(maxlen=10)
    h.add(host, None)
    h.add(host | {"ts": 5004.0}, None)
    path = tmp_path / "snap.json"
    h.save(path)

    h2 = History(maxlen=10)
    h2.load(path, interval=4.0, now=5010.0)  # ventana=40s: ambas caben
    assert [s["ts"] for s in h2.samples] == [5000.0, 5004.0]
    assert h2.samples[0]["cpu"] == 10.0


def test_history_load_drops_stale(tmp_path):
    from app.metrics import History
    h = History(maxlen=10)
    h.add({"ts": 1000.0, "cpu_pct": 1.0, "mem": {"pct": 1.0}, "disk": {"pct": 1.0}}, None)
    h.add({"ts": 9000.0, "cpu_pct": 2.0, "mem": {"pct": 2.0}, "disk": {"pct": 2.0}}, None)
    path = tmp_path / "snap.json"
    h.save(path)

    h2 = History(maxlen=10)
    h2.load(path, interval=4.0, now=9010.0)  # ventana=40s: corta ts=1000
    assert [s["ts"] for s in h2.samples] == [9000.0]


def test_history_load_missing_or_corrupt_ok(tmp_path):
    from app.metrics import History
    h = History(maxlen=10)
    h.load(tmp_path / "nope.json", interval=4.0, now=0.0)  # ausente: no falla
    assert len(h.samples) == 0
    bad = tmp_path / "bad.json"
    bad.write_text("{no es json", encoding="utf-8")
    h.load(bad, interval=4.0, now=0.0)                     # corrupto: no falla
    assert len(h.samples) == 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd studio/backend && venv/bin/pytest tests/test_metrics_history.py -k "save or load or corrupt" -v`
Expected: FAIL con `AttributeError: 'History' object has no attribute 'save'`.

- [ ] **Step 3: Add `save` / `load` to `History`**

En `studio/backend/app/metrics.py`, añadir estos imports arriba (junto a `import time`):

```python
import json
import os
from pathlib import Path
```

Añadir dentro de la clase `History` (tras el método `add`):

```python
    def save(self, path) -> None:
        """Vuelca las muestras a JSON de forma atómica. Nunca lanza."""
        try:
            path = Path(path)
            tmp = path.with_suffix(path.suffix + ".tmp")
            tmp.write_text(json.dumps(list(self.samples)), encoding="utf-8")
            os.replace(tmp, path)
        except OSError as e:
            print(f"[metrics] no se pudo guardar snapshot: {e!r}")

    def load(self, path, interval: float, now: float | None = None) -> None:
        """Recarga muestras dentro de la ventana maxlen*interval. Nunca lanza."""
        path = Path(path)
        if not path.is_file():
            return
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            print(f"[metrics] snapshot ilegible, se ignora: {e!r}")
            return
        if now is None:
            now = time.time()
        cutoff = now - (self.samples.maxlen or 0) * interval
        for s in raw:
            if isinstance(s, dict) and s.get("ts", 0) >= cutoff:
                self.samples.append(s)
```

- [ ] **Step 4: Run the new tests**

Run: `cd studio/backend && venv/bin/pytest tests/test_metrics_history.py -v`
Expected: PASS (los 3 nuevos + los existentes de este archivo).

- [ ] **Step 5: Add the config path**

En `studio/backend/app/config.py`, justo después de la línea `self.metrics_interval = float(...)`:

```python
        self.metrics_snapshot_path = Path(os.environ.get(
            "MS_METRICS_SNAPSHOT", str(self.db_path.parent / "metrics_history.json")))
```

- [ ] **Step 6: Wire load/save into the lifespan**

En `studio/backend/app/main.py`, en la función `lifespan` (`main.py:36-43`), reemplazar el cuerpo por:

```python
async def lifespan(app: FastAPI):
    history.load(cfg.metrics_snapshot_path, cfg.metrics_interval)
    manager.start()
    metrics_task = asyncio.get_event_loop().create_task(_metrics_loop())
    yield
    metrics_task.cancel()
    history.save(cfg.metrics_snapshot_path)
    await manager.stop()
    db.close()
```

- [ ] **Step 7: Gitignore the snapshot**

En `.gitignore`, bajo la sección `# ManimStudio`, añadir:

```
metrics_history.json
```

Verificar que git NO lo trackea: `git check-ignore studio/backend/metrics_history.json` debe imprimir la ruta.

- [ ] **Step 8: Run the full backend suite**

Run: `cd studio/backend && venv/bin/pytest -q`
Expected: todo en verde (44 tests: 41 previos + Task 1 + 3 de este task; ajustar el conteo si Task 1 no se ha corrido aún).

- [ ] **Step 9: Verify end-to-end that history survives a restart**

Run:
```bash
sudo systemctl restart manimstudio-backend.service
sleep 8   # deja pasar un par de ticks de métricas
ls -l studio/backend/metrics_history.json
```
Expected: el archivo existe tras el arranque (se escribió en el shutdown del proceso anterior y/o se recreará en el siguiente stop). Confirmar en la UI (Monitor) que la gráfica no arranca vacía tras el restart.

- [ ] **Step 10: Commit**

```bash
cd /var/www/codeaerospace_contenido
git add studio/backend/app/config.py studio/backend/app/metrics.py studio/backend/app/main.py studio/backend/tests/test_metrics_history.py .gitignore
git commit -m "Sprint 5: persistir snapshot del ring buffer de metricas entre deploys"
```

---

### Task 3: Botón «Corregir con IA» en el job fallido

**Files:**
- Modify: `studio/frontend/src/Studio.jsx` (barra del panel REGISTRO, `panel__actions`, ~línea 208-216)

**Interfaces:**
- Consumes: estado y setters ya existentes en `Studio.jsx` — `aiEnabled`, `selected`, `setAiMode`, `setAiOpen`. El modo `fix` ya existe en `Assistant.jsx` (`MODES` incluye `{ id: 'fix', label: 'Corregir' }`).
- Produces: ninguna interfaz nueva. Sin cambios de backend.

- [ ] **Step 1: Add the button next to «Explicar error»**

En `studio/frontend/src/Studio.jsx`, dentro del bloque `aiEnabled && ['error', 'timeout'].includes(selected.status)` (justo después del botón `✨ Explicar error`, antes del cierre de ese bloque en la línea ~216), añadir:

```jsx
                {aiEnabled && ['error', 'timeout'].includes(selected.status) && (
                  <button className="btn btn--tiny btn--ai"
                    onClick={() => { setAiMode('fix'); setAiOpen(true) }}>
                    🔧 Corregir con IA
                  </button>
                )}
```

Nota: es un segundo bloque hermano con la misma condición, inmediatamente después del bloque del botón «✨ Explicar error». Abre el drawer directamente en la pestaña «Corregir» sin auto-ejecutar la propuesta (el usuario pulsa «Proponer corrección», que gasta el modelo profundo).

- [ ] **Step 2: Build & deploy the frontend**

REQUIRED SUB-SKILL: usar la skill `deploy-frontend` de este proyecto para construir y desplegar `dist` al contenedor. No copiar `dist` a mano.

- [ ] **Step 3: Verify end-to-end in the app**

Con un job en estado `error` o `timeout` seleccionado:
- Aparecen DOS botones en la barra de REGISTRO: «✨ Explicar error» y «🔧 Corregir con IA».
- Pulsar «🔧 Corregir con IA» abre el drawer del asistente directamente en la pestaña «Corregir» (no en «Explicar»).
- La propuesta NO se lanza sola: se ve el botón «Proponer corrección» a la espera.
- Con un job en estado `done` los botones de IA no aparecen.

- [ ] **Step 4: Commit**

```bash
cd /var/www/codeaerospace_contenido
git add studio/frontend/src/Studio.jsx studio/frontend/dist
git commit -m "Sprint 5: boton Corregir con IA directo desde el job fallido"
```

Nota: incluir `studio/frontend/dist` solo si el flujo del repo versiona el build; si `dist` está gitignored (lo está: `studio/frontend/dist/`), NO añadirlo y commitear solo el fuente `Studio.jsx`.

---

### Task 4: Identidad git en el VPS

**Files:**
- Ninguno del repo. Configuración local de git (`.git/config`).

**Interfaces:** N/A.

- [ ] **Step 1: Set repo-local identity**

```bash
cd /var/www/codeaerospace_contenido
git config user.name  "Alan R."
git config user.email "ingalanr@gmail.com"
```

Repo-local a propósito (sin `--global`): solo afecta este repositorio.

- [ ] **Step 2: Verify**

```bash
git config user.name && git config user.email
```
Expected:
```
Alan R.
ingalanr@gmail.com
```

- [ ] **Step 3: Confirm on the next commit**

Los commits de las Tasks 1-3 ya saldrán con la nueva autoría si esta tarea se ejecuta primero. En cualquier caso, verificar tras el próximo commit:

```bash
git log -1 --format='%an <%ae>'
```
Expected: `Alan R. <ingalanr@gmail.com>` (ya no `root <root@srv1568407.hstgr.cloud>`).

No reescribe historia previa; aplica solo a commits nuevos. **Sugerencia de orden:** ejecutar Task 4 antes que las Tasks 1-3 para que esos commits ya lleven la autoría correcta.

---

## Notas de ejecución

- **Orden recomendado:** Task 4 primero (para que el resto de commits lleven la autoría correcta), luego Tasks 1, 2, 3 en cualquier orden (son independientes).
- **Reinicios:** Task 1 y 2 requieren `sudo systemctl restart manimstudio-backend.service` para verificar en prod. Ninguna toca el runner. Task 3 requiere el deploy del frontend.
- **Conteo de tests:** parte de 41; termina en 45 (Task 1 +1, Task 2 +3).
