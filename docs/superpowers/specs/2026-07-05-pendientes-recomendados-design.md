# Pendientes recomendados — diseño

**Fecha:** 2026-07-05
**Ámbito:** ManimStudio (`studio/`), prod en coderesearch.space

Cuatro mejoras acotadas de operación/UX, sin dependencias entre sí. Se
implementan y (según el flujo habitual) se commitean por sprint atómico.

---

## 1. Cachear `storage_usage()`

**Problema.** `JobManager.storage_usage()` (`studio/backend/app/jobs.py`) hace
`render_jobs/.rglob("*")` y suma `stat().st_size` de cada archivo. Se invoca en
cada `GET /api/jobs` (`main.py:176`, vía `_storage_public()`), en el endpoint de
borrado (`main.py:243`) y en el chequeo de cuota de `create_job` (`main.py:156`).
Irrelevante a la escala actual, pero O(nº archivos) por request y medible con
cientos de jobs.

**Diseño.** Caché en memoria dentro de `JobManager` con **TTL corto +
invalidación explícita**:

- Campos nuevos: `_storage_cache: int | None` y `_storage_cache_at: float`.
- Constante `STORAGE_TTL = 15.0` (s).
- `storage_usage()` devuelve el valor cacheado si tiene menos de `STORAGE_TTL`
  segundos; si no, recalcula (el rglob actual), guarda y devuelve.
- `_invalidate_storage()` pone `_storage_cache = None` para forzar recálculo en
  la próxima lectura. Se llama en:
  - `_finish()` (un render terminó → cambió el tamaño en disco), y
  - `delete_job()` / `delete_job_files()` (se liberó espacio; la Biblioteca debe
    reflejar la cuota liberada al instante).

**Trade-off.** Durante un render los archivos crecen de a poco; el TTL de 15 s
absorbe esa variación sin necesidad de un contador incremental exacto (que sería
frágil: media/ temporal, thumbnails, renders parciales). El chequeo de cuota en
`create_job` tolera 15 s de staleness porque es un guard blando.

**Test.** En `tests/test_jobs_api.py` (o donde vivan los tests de `JobManager`):
dos lecturas consecutivas no recalculan (mock/spy del rglob o comprobar que el
timestamp no cambia); tras `_invalidate_storage()` sí recalcula; tras borrar un
job el valor baja.

---

## 2. Botón «Corregir con IA» en el job fallido

**Problema.** Para corregir un render fallido hay que abrir el drawer del
asistente y cambiar manualmente a la pestaña «Corregir». El botón «✨ Explicar
error» ya existe en la barra del panel REGISTRO; falta el equivalente para
corregir.

**Diseño.** En `studio/frontend/src/Studio.jsx`, junto a «✨ Explicar error»
(dentro de `panel__actions`, condicionado por `aiEnabled && ['error','timeout']
.includes(selected.status)`), añadir un botón **«🔧 Corregir con IA»** que:

```jsx
onClick={() => { setAiMode('fix'); setAiOpen(true) }}
```

Abre el drawer directamente en la pestaña «Corregir» (`aiMode='fix'`). **No**
auto-ejecuta la propuesta: el usuario pulsa «Proponer corrección» (modelo
profundo, coste IA). La infraestructura ya existe (`MODES` incluye
`{id:'fix', label:'Corregir'}`; el modo `fix` en `Assistant.jsx`). No requiere
cambios de backend.

**Test.** Cubierto por verificación manual E2E (frontend); no hay suite JS.

---

## 3. Persistir snapshot del ring buffer de métricas

**Problema.** `metrics.History` es un ring buffer en memoria (`~30 min`). En cada
deploy/reinicio se pierde toda la historia. Por diseño es en memoria (cero disco
en caliente), pero un snapshot al apagar evita perder la ventana en cada deploy.

**Diseño.**

- `config.py`: nueva ruta `metrics_snapshot_path` (env `MS_METRICS_SNAPSHOT`,
  por defecto junto al `.db`, p. ej. `studio/manimstudio_metrics.json`).
- `metrics.History`: métodos `save(path)` y `load(path)`.
  - `save`: vuelca `list(self.samples)` a JSON (átomico: escribir a `.tmp` y
    `os.replace`). Errores de I/O se loguean y se ignoran (no deben tumbar el
    shutdown).
  - `load`: lee el JSON si existe, descarta muestras con `ts` fuera de la ventana
    (más viejas que `maxlen * metrics_interval` respecto a ahora) y rellena el
    deque. Archivo ausente/corrupto → arranca vacío sin fallar.
- `main.py` `lifespan`:
  - **startup** (antes de crear `_metrics_loop`): `history.load(path)`.
  - **shutdown** (tras `yield`, junto a `manager.stop()`): `history.save(path)`.
- **Frecuencia: solo al apagar.** `systemctl stop` envía SIGTERM → el shutdown
  del lifespan de uvicorn corre limpio antes de un deploy. No se añade guardado
  periódico (YAGNI; el objetivo es sobrevivir deploys, no crashes duros).
- `.gitignore`: añadir el archivo de snapshot (nunca al repo).

**Test.** En `tests/test_metrics_history.py`: `save` luego `load` restaura las
muestras; `load` descarta muestras fuera de ventana; archivo ausente → deque
vacío sin excepción.

---

## 4. `git config` de identidad en el VPS

**Problema.** Los commits salen como `root <root@srv1568407.hstgr.cloud>`.

**Diseño.** `git config` **repo-local** (sin `--global`, solo este repositorio):

```
git config user.name  "<NOMBRE>"
git config user.email "<EMAIL>"
```

Valores pendientes de confirmar con el usuario (email candidato:
`ingalanr@gmail.com`). No reescribe historia previa; aplica a commits nuevos.

**Verificación.** `git config user.name && git config user.email` y un
`git log --format='%an <%ae>'` en el próximo commit.

---

## Fuera de alcance

- Contador de storage incremental exacto (frágil; el TTL basta).
- Auto-ejecución de la corrección IA (coste; decisión explícita del usuario).
- Snapshot periódico de métricas / supervivencia a crashes duros.
- Reescritura de autoría de commits históricos.
