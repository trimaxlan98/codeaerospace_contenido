# codeaerospace_contenido

Contenido audiovisual de **Co.De Aerospace** generado con
[Manim Community](https://www.manim.community/): divulgación sobre mecánica
orbital, satélites y redes de telecomunicaciones.

El repo son dos cosas a la vez:

- **Las escenas** (`src/`, más algunos scripts sueltos en la raíz) — el
  contenido en sí, Python plano.
- **ManimStudio** (`studio/`) — la consola web desde la que se escriben y
  renderizan esas escenas sin tocar la terminal.

## Estructura

```
├── Dockerfile              imagen de render: Manim + LaTeX + ffmpeg + Cairo/Pango
├── docker-compose.yml      servicio interactivo (manim) y sandbox de render (manim-render)
├── setup.sh                verificación del entorno dentro del contenedor
├── .devcontainer/          VS Code Dev Container sobre el mismo Dockerfile
│
├── src/episodio1/          escenas del episodio 1 (órbitas LEO vs MEO, formatos reel)
├── p1.py                   escena mínima de ejemplo
├── apt_tracking.py         escena de seguimiento satelital (APT)
│
├── studio/                 ManimStudio (ver más abajo)
└── docs/
    ├── entorno_desarrollo/ cómo levantar todo en local + rendimiento medido
    └── superpowers/        planes y especificaciones de diseño
```

## Renderizar una escena

Con Docker, sin instalar nada en el host:

```bash
docker compose build manim
docker compose run --rm manim \
  manim render -ql --media_dir media src/episodio1/orbit_logic_ep1.py OrbitLogicEp1V2
```

`-ql` es 480p15, `-qm` 720p30, `-qh` 1080p60. El video sale en `media/`.

También hay un Dev Container de VS Code (`.devcontainer/`) que construye la
misma imagen y corre `setup.sh` para comprobar que Manim, LaTeX, ffmpeg y
Cairo quedaron bien.

Para escenas 3D pesadas, el tiempo de render escala con el **número de frames**,
no con la resolución — hay números concretos en
[`docs/entorno_desarrollo/rendimiento.md`](docs/entorno_desarrollo/rendimiento.md).

## ManimStudio (`studio/`)

Consola web privada de un solo usuario para escribir, renderizar y archivar
escenas. En producción vive en <https://coderesearch.space>.

Documentación completa: [`studio/docs/README.md`](studio/docs/README.md).
Auditoría de seguridad: [`studio/docs/AUDITORIA.md`](studio/docs/AUDITORIA.md).

**Editor y renderizado.** Editor CodeMirror con las escenas del script
detectadas por AST (nunca se ejecuta código fuera del sandbox), cola de un
render a la vez y log en vivo por SSE.

**Biblioteca.** Grid de los renders correctos con miniatura, reproductor,
descarga y borrado; purga en lote de fallidos o antiguos, con cuota de disco
configurable.

**Aprender.** Curso de Manim y del propio Estudio en Markdown con fórmulas
KaTeX, versionado en `studio/content/lessons/` y servido por `/api/lessons`.
Actualmente 18 lecciones repartidas en Fundamentos, Intermedio, Primitivas del
Estudio y Flujo de trabajo.

**Animaciones y primitivas.** Biblioteca curada de primitivas de Manim
reutilizables en `studio/content/manim_extensions/` (10 módulos: órbitas de
Kepler, constelaciones, redes neuronales, láser, transiciones, pizarra 3D…),
más un flujo de propuesta y aprobación de primitivas nuevas.

**Monitoreo.** CPU, RAM y disco en vivo por SSE, con histórico de ~30 min en
gráficas SVG que marcan los intervalos con renders activos.

**Asistente IA.** Feature-flag: sin credenciales la app funciona igual y su
UI se oculta. Vertex AI (Gemini 2.5) explica errores, corrige scripts y genera
escenas desde lenguaje natural. El código que genera **nunca** se renderiza
solo: pasa por la misma validación AST y el mismo sandbox sin red que el
escrito a mano.

**Estudio de investigación (v3, 2026-09).** Voz sin depender de GCP (edge-tts
y Piper, o la grabación del dueño subida por clip, con guion editable por
secciones), música procedural con *ducking* bajo la voz, un proyecto que se
importa y exporta como directorio (`curso.json` + `style_block.py` +
`clips/`), render en lote, hoja de contactos y fotograma a PNG para figuras
de tesis, un **Laboratorio** que ejecuta Python de validación en el sandbox
(las sondas de invariantes de cada librería), y las primitivas `figura`
(figuras de paper con sello de proveniencia) y `ntn` (pase LEO, Doppler,
PBFT, margen adaptativo). Tablero y decisiones:
[`studio/docs/ESTUDIO-V3.md`](studio/docs/ESTUDIO-V3.md).

### Arquitectura, en corto

```
navegador ──HTTPS──▶ nginx ──┬─ /      → studio/frontend/dist  (React + Vite + CodeMirror)
                             └─ /api/  → FastAPI :3002  (usuario sin privilegios)
                                            │ SQLite + cola en memoria
                                            ▼ socket Unix
                                        manim-runner  (root; único con acceso a Docker)
                                            ▼ docker compose run
                                        manim-render  (sin red, read-only, cpus/mem/pids
                                                       limitados, no-new-privileges)
```

El proceso web nunca toca `docker.sock`. El runner expone cuatro comandos
—render, cancel, thumbnail, stats— validados por regex y limitados a este
compose file. Cada render corre en un contenedor sin red, con el repo montado
en solo lectura y escritura únicamente en el directorio de su propio job.

## Desarrollo local

```bash
studio/dev.sh    # runner + backend + Vite → http://127.0.0.1:5173
```

Requiere haber creado antes el venv, el `.env`, `node_modules` y la imagen de
Docker. La guía completa —incluidos dos errores de configuración que dan un
401 silencioso— está en
[`docs/entorno_desarrollo/README.md`](docs/entorno_desarrollo/README.md).

Tests del backend (365, sin tocar Docker ni las APIs de IA):

```bash
cd studio/backend && venv/bin/python -m pytest tests/ -q
```
