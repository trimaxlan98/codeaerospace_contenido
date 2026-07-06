# Fable 5 + biblioteca de primitivas Manim — diseño

**Fecha:** 2026-07-06
**Ámbito:** ManimStudio (`studio/`), infraestructura Docker del render y nuevo módulo admin

---

## Problema / motivación

Hoy ManimStudio solo puede producir animaciones a partir de: (a) lecciones
escritas a mano en `studio/content/animations/`, o (b) scripts generados por
el Asistente IA (`ai.py`, Gemini 2.5) que se limita a la API estándar de
Manim CE. No hay forma de expandir de forma acumulativa qué *tipos* de
animación son posibles, ni de aprovechar un modelo con mayor capacidad de
razonamiento (Claude Fable 5) para diseñar técnicas visuales nuevas.

Al mismo tiempo, ejecutar código generado por un LLM (no revisado antes de
correr, aunque sí antes de aceptarse como reusable) expone un supuesto que
antes no se había puesto a prueba: que el sandbox del contenedor de render es
suficiente para código no confiable. Una auditoría dirigida (con Claude
Fable 5, ver más abajo) confirmó que el sandbox es sólido en varios ejes pero
tiene un hueco real: el bind mount `.:/workspace` monta **todo el repo en
lectura-escritura** dentro del contenedor de render, incluyendo secretos
(`.env`, `gcp-key.json`) y el propio `manim_runner.py`/`docker-compose.yml`
que el daemon root ejecuta después. Cerrar esto es prerequisito de todo lo
demás en este documento.

Este trabajo tiene 3 fases. La Fase 0 bloquea a las Fases 1 y 2 (ambas
ejecutan código dentro del mismo contenedor de render); las Fases 1 y 2 son
independientes entre sí y pueden implementarse en cualquier orden una vez
cerrada la Fase 0.

---

## Fase 0 — Endurecer el sandbox de render (prerequisito bloqueante)

### Problema concreto

`docker-compose.yml` monta `- .:/workspace` (ancla `x-manim-base`, heredada
por `manim-render`). Un script de render —generado o no— corre con el mismo
uid (`manimstudio`) dueño de esos archivos en el host, así que puede:

- Leer `studio/backend/.env` (`MS_SECRET_KEY`) y `studio/backend/gcp-key.json`
  (credenciales de Vertex AI). `network_mode: none` bloquea la exfiltración
  por red, no la lectura local ni una futura vía de escritura a un archivo
  que sí se sirva (p.ej. dentro de `render_jobs/`).
- Sobrescribir `studio/runner/manim_runner.py` o `docker-compose.yml`: la
  próxima vez que el runner (que corre como root vía systemd) haga
  `docker compose run`, usaría un compose file o runner potencialmente
  manipulado.

Adicionalmente: el contenedor no dropea capabilities de Linux (`cap_drop` no
está seteado — conserva el set por defecto de Docker) y no hay límite de
disco por job más allá de la cuota chequeada solo al *crear* el job
(`main.py`, `MS_MAX_STORAGE_MB`), no durante el render.

### Diseño

1. **Mount read-only + rw acotado al job.** `manim_runner.py` deja de heredar
   el volumen global del compose y en su lugar pasa volúmenes explícitos por
   invocación de `docker compose run`:
   - `.:/workspace:ro` (todo el repo, solo lectura)
   - un volumen adicional rw solo para `render_jobs/<job_id>/` (donde Manim
     escribe `media/` y donde ya se lee `scene.py`)
   Esto requiere ajustar el `argv` de `handle_render`/`handle_thumbnail` en
   `manim_runner.py` para inyectar el mount por job en vez de depender del
   volumen fijo del `docker-compose.yml`.
2. **Sacar secretos del árbol montado.** Mover `studio/backend/.env` y
   `studio/backend/gcp-key.json` fuera de `PROJECT_DIR` (p.ej. a un directorio
   hermano fuera del repo, o excluirlos explícitamente si el mount pasa a ser
   por-subpath en vez de la raíz completa). Si el mount ya es `:ro`, esto es
   defensa en profundidad más que bloqueante — pero de todas formas cierra la
   lectura de secretos incluso en modo solo-lectura.
3. **`cap_drop: [ALL]`** en el servicio `manim-render` (Manim/Cairo/ffmpeg no
   necesitan ninguna capability con `network_mode: none`).
4. **Rootfs read-only + tmpfs acotado para `/tmp`** (HOME de Manim dentro del
   contenedor, vía `read_only: true` + `tmpfs: {/tmp: size=...}` en el
   servicio `manim-render`).
5. Límite de disco por job (tmpfs dimensionado o watcher que aborte el
   contenedor si `render_jobs/<id>` supera un umbral) — se deja como mejora
   de disponibilidad, no bloqueante para las fases 1-2.

### Testing

- Verificar manualmente que un job normal (lección existente) sigue
  renderizando igual tras el cambio de mounts.
- Prueba negativa: una escena que intente `open("/workspace/studio/backend/.env")`
  debe fallar (permiso denegado, filesystem read-only) en vez de leer el
  archivo.
- Prueba negativa: una escena que intente escribir fuera de
  `render_jobs/<job_id>/` debe fallar.
- Confirmar que `handle_thumbnail` (que también invoca `docker compose run`)
  sigue funcionando con los mounts acotados.

---

## Fase 1 — Renderer OpenGL headless

### Contexto

La imagen ya incluye `moderngl`, `moderngl-window` y `glcontext` (dependencias
Python del renderer OpenGL de Manim CE), pero el `Dockerfile` no instala las
librerías de sistema necesarias para crear un contexto GL headless (sin
display, sin GPU) — faltan Mesa/EGL.

### Diseño

- Añadir al `Dockerfile`: `libgl1-mesa-glx libegl1-mesa libglu1-mesa` (o la
  variante OSMesa si el contexto EGL headless no arranca sin GPU en el host).
- Validar la creación de contexto headless **sobre el sandbox ya endurecido
  de la Fase 0** (mounts ro/rw, cap_drop, rootfs read-only) — el orden importa
  porque el renderer OpenGL puede necesitar escritura en rutas que el rootfs
  read-only bloquee (p.ej. cachés de shaders), y eso hay que descubrirlo antes
  de dar la fase por cerrada.
- Escena de prueba con `manim render --renderer=opengl` de punta a punta por
  el pipeline normal (JobManager → runner → docker), confirmando que produce
  un vídeo válido.

### Testing

- Render de una escena 3D simple con `--renderer=opengl` vía el flujo normal
  de creación de job, verificando que el video final se genera y no se cuelga
  el contenedor.
- Verificar que el renderer Cairo (por defecto, todo el contenido existente)
  sigue funcionando sin cambios tras añadir las libs Mesa.

---

## Fase 2 — Biblioteca de primitivas generadas con Fable 5

### Componentes

**Backend — `studio/backend/app/fable.py` (nuevo)**

Mismo patrón que `ai.py`: clase con SDK de Anthropic importado de forma
perezosa, feature-flag por la presencia de una API key configurada en
`Settings` (nuevo campo en `config.py`), rate limiter (`AIRateLimiter`,
reusado). Diferencias respecto a `ai.py`:

- `model="claude-fable-5"`, sin fijar `thinking` (adaptativo por defecto),
  `output_config={"effort": "high"}`.
- Fallback por defecto: `betas=["server-side-fallback-2026-06-01"],
  fallbacks=[{"model": "claude-opus-4-8"}]` — si el clasificador de
  seguridad de Fable 5 rechaza una petición legítima, se resuelve con Opus
  4.8 en la misma llamada.
- Método principal `propose_primitive(description, feedback=None,
  previous_code=None) -> {primitive_code, demo_scene, explanation}`: el
  system prompt describe las convenciones del módulo de extensiones
  (ejemplos de primitivas ya aprobadas para mantener estilo consistente) y
  pide dos bloques de código en una sola respuesta. Si `feedback` está
  presente (iteración sobre una propuesta rechazada), se incluye junto al
  código previo para que Fable 5 produzca una nueva versión.

**Almacenamiento**

- `studio/content/manim_extensions/`: paquete versionado en git, un archivo
  por primitiva aprobada (`<slug>.py`), mismo patrón que
  `studio/content/animations/`.
- Staging efímero fuera de git (p.ej. `pending_primitives/<proposal_id>/`,
  mismo estilo que `render_jobs/`): guarda `primitive.py` + `demo_scene.py` +
  metadata (descripción, feedback previo si lo hay) mientras la propuesta
  está pendiente de revisión.

**Flujo (con soporte de iteración)**

1. Admin describe el efecto deseado en un panel nuevo, solo-admin.
2. Backend crea un `proposal_id`, llama a Fable 5 de forma asíncrona (los
   turnos pueden tardar varios minutos), y publica progreso por el
   `EventBus`/SSE existente (mismo canal que usan los jobs de render).
3. Al recibir código, el backend reutiliza el `JobManager` sin
   modificaciones para renderizar la escena demo (mismo pipeline
   sandboxeado que cualquier lección).
4. Panel muestra código de la primitiva + video renderizado.
5. Admin puede:
   - **Aprobar** → se copia `primitive.py` de staging a
     `studio/content/manim_extensions/<slug>.py` (queda en `git status` para
     commit manual, igual que el resto del contenido).
   - **Rechazar con feedback** → se llama de nuevo a
     `propose_primitive(description, feedback=<texto>, previous_code=<código
     anterior>)`, generando una nueva iteración sobre el mismo
     `proposal_id` (nuevo render demo, mismo ciclo). El staging anterior se
     descarta al generarse la nueva versión.
   - **Rechazar sin feedback** → se descarta el staging, no toca git.

**Frontend**

Nueva sub-sección solo-admin (no visible para usuarios del Asistente
normal) — sigue el patrón de sub-pestañas ya usado en `Admin.jsx`
(`role="tablist"`). Un formulario de descripción, estado en vivo vía SSE,
vista de código + video embebido, y botones Aprobar/Rechazar-con-feedback.

### Error handling

- `stop_reason == "refusal"` en la llamada a Fable 5: el fallback a Opus 4.8
  ya está configurado por defecto; si aún así falla, se muestra el error al
  admin sin reintento automático adicional.
- Render de la demo falla (código generado no compila, timeout, etc.): se
  muestra el log de error igual que cualquier job fallido; el admin puede
  rechazar con ese log como feedback ("falló con este error: ...") para que
  Fable 5 corrija en la siguiente iteración.
- Backend reiniciado con una propuesta pendiente: se pierde (staging en
  memoria/disco efímero, sin persistencia en SQLite) — aceptable para una
  herramienta experimental de uso esporádico.

### Testing

- Tests de backend (`pytest`, mockeando `_call_model` como ya hace
  `test_ai.py`/`ai.py`): feature-flag deshabilitado sin API key, extracción
  de los dos bloques de código de la respuesta, flujo de iteración con
  feedback, manejo de `refusal`.
- Verificación manual E2E: proponer una primitiva real, ver el render demo,
  aprobarla, confirmar que aparece en `git status` bajo
  `studio/content/manim_extensions/`.

---

## Fuera de alcance

- Escáner estático de seguridad sobre el código generado antes de aceptarlo
  en la biblioteca — la revisión humana obligatoria ya acordada es el
  control, consistente con cómo se trata el resto del contenido del repo.
- Persistencia en SQLite de las propuestas (historial de aprobadas/rechazadas)
  — se puede añadir después si esta herramienta deja de ser experimental.
- Límite de disco por job dentro del render (mencionado en Fase 0 como
  mejora de disponibilidad, no bloqueante).
- Integrar primitivas de la biblioteca en el flujo de generación del
  Asistente normal (Gemini) — por ahora la biblioteca solo se consume
  manualmente al escribir/generar escenas nuevas.
