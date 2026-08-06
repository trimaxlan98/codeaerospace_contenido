# ManimStudio → Estudio: Proyectos (cursos) con continuidad

Fecha: 2026-07-16 · Autor: Claude (sesión autónoma nocturna, decisiones documentadas)

## 1. Problema y objetivo

Hoy ManimStudio renderiza escenas sueltas: cada render es un *job* efímero
(la Biblioteca los lista, pero los purgados en lote los destruyen). No hay
forma de construir un **video largo por piezas**: un curso donde cada clip
es una animación corta que, renderizada con parámetros homogéneos y en un
orden definido, se concatena **fuera de la app** (ffmpeg) para producir el
video final.

Objetivo: convertir la app en un estudio de producción por piezas, sin ser
editor de video:

1. **Proyectos** (cursos) que agrupan **clips ordenados** (capítulos).
2. **Continuidad garantizada**: mismos parámetros de render, mismo estilo
   visual y notas de encadenado entre clips.
3. **Exportación para unión externa**: manifiesto + `concat.txt` de ffmpeg
   + descarga en lote, con nombres ordenados (`001-intro.mp4`, …).

## 2. Lógica de continuidad (el razonamiento)

Para que N clips renderizados por separado se unan en un video continuo sin
recodificar (`ffmpeg -f concat -c copy`), deben cumplirse tres niveles:

### Nivel técnico (obligatorio, lo garantiza la app)
- **Misma resolución y fps.** En manim, la calidad fija ambos: `ql`=854×480@15,
  `qm`=1280×720@30, `qh`=1920×1080@60. Por eso **la calidad se fija a nivel
  de proyecto** y todo clip del proyecto renderiza con ella. Es la regla
  número uno: un proyecto es concat-safe por construcción.
- **Mismo códec/pix_fmt**: manim CE produce h264/yuv420p uniforme en el
  mismo contenedor Docker → ya garantizado por el pipeline actual.

### Nivel visual (lo facilita la app)
- **Estilo compartido por proyecto**: un bloque Python opcional
  (`style_block`) con paleta, constantes y helpers (`COLOR_FONDO`,
  `TITULO_STYLE`, funciones de intro/outro…). Al renderizar un clip, el
  backend compone `scene.py = style_block + "\n\n" + script_del_clip`.
  Cambias la paleta una vez → todos los clips re-renderizados la heredan.
  - El bloque se antepone con un marcador de comentario para que los
    números de línea de los errores sean interpretables; la UI muestra el
    offset ("el estilo del proyecto añade N líneas").
  - `detect_scenes` y la validación operan sobre el **script compuesto**
    (una clase de escena podría heredar de una base definida en el estilo).
- **`background_color` y fuentes** viven en el style_block (config de manim
  por código), no en flags: mantiene el runner intacto.

### Nivel narrativo (lo registra la app, lo aplica el humano/IA)
- Cada clip tiene **notas de continuidad**: `estado_final` ("termina con el
  diagrama de órbita centrado, título arriba") y `notas` libres. Al crear o
  editar el clip siguiente, la UI muestra el `estado_final` del clip
  anterior — el guionista (o el asistente IA) sabe desde dónde arranca.
- El orden es explícito (`position`), reordenable.

### Frescura (detección de desfase)
- Un clip guarda su script canónico y apunta al job de su **último render
  bueno**. Si el script del clip (o el style_block del proyecto) cambia
  después de ese render, el clip se marca **desactualizado** (`stale`):
  se compara `content_hash` (sha256 del script compuesto) guardado en el
  render contra el actual. La UI lo señala y ofrece re-render en un clic
  (también "re-renderizar todos los desactualizados", que encola en orden).

## 3. Modelo de datos (SQLite, migraciones aditivas)

```sql
CREATE TABLE projects (
    id TEXT PRIMARY KEY,           -- uuid4.hex[:16]
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    quality TEXT NOT NULL,         -- ql|qm|qh, fijo para todos los clips
    style_block TEXT DEFAULT '',   -- python antepuesto a cada clip
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL
);

CREATE TABLE clips (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id),
    position INTEGER NOT NULL,     -- orden 0..n-1, compactado al reordenar/borrar
    title TEXT NOT NULL,
    script TEXT NOT NULL DEFAULT '',    -- script canónico del clip (sin style_block)
    scene TEXT DEFAULT '',              -- escena a renderizar
    final_state TEXT DEFAULT '',        -- notas: cómo termina en pantalla
    notes TEXT DEFAULT '',
    job_id TEXT,                        -- último render bueno (nullable)
    rendered_hash TEXT,                 -- sha256 del script compuesto de ese render
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL
);
```

En `jobs` (aditivo): `project_id TEXT`, `clip_id TEXT`, `content_hash TEXT`
(sha256 del script compuesto con que se lanzó). Un job puede nacer ligado a
un clip; al terminar `done`, el worker actualiza `clips.job_id = job.id` y
`clips.rendered_hash = job.content_hash` (solo si el clip aún existe y
pertenece al mismo proyecto). `stale = rendered_hash != hash(compuesto actual)`.

**Protección de renders de curso**: `delete_failed_jobs`,
`delete_finished_jobs` y `delete_jobs_older_than` **saltan** los jobs que
sean el render vigente de algún clip (`job_id` referenciado). El borrado
individual desde la Biblioteca sí lo permite (la UI avisa "es el render del
clip X del proyecto Y"); al borrarse, el clip queda "sin render" (job_id
NULL) — nunca referencias colgantes. Borrar un proyecto NO borra jobs (los
desliga); borrar un clip tampoco.

## 4. API (todas con auth, mismo estilo actual)

```
GET    /api/projects                     → lista con conteos y estado agregado
POST   /api/projects                     {name, description?, quality, style_block?}
GET    /api/projects/{id}                → proyecto + clips ordenados (+stale por clip)
PATCH  /api/projects/{id}                {name?, description?, style_block?}  (quality inmutable si hay clips renderizados)
DELETE /api/projects/{id}                desliga jobs, borra clips
POST   /api/projects/{id}/clips          {title, script?, scene?, after?/position?, from_job_id?}
PATCH  /api/projects/{id}/clips/{cid}    {title?, script?, scene?, final_state?, notes?}
DELETE /api/projects/{id}/clips/{cid}
POST   /api/projects/{id}/clips/{cid}/move   {position}
POST   /api/projects/{id}/clips/{cid}/render → crea job (calidad del proyecto, script compuesto)
POST   /api/projects/{id}/render-stale       → encola en orden los clips desactualizados
GET    /api/projects/{id}/export             → manifest.json (clips, orden, hashes, specs)
GET    /api/projects/{id}/archive            → zip: NNN-titulo.mp4 + concat.txt + manifest.json
```

- `from_job_id`: crear clip desde un video existente de la Biblioteca
  (copia script/escena del job; adopta ese job como render vigente solo si
  la calidad coincide con la del proyecto; si no, queda stale).
- `archive` incluye solo clips con render vigente; streaming ZIP_STORED
  (mp4 no comprime) sin duplicar en disco; `concat.txt` con líneas
  `file 'NNN-titulo.mp4'` en orden. README corto dentro del zip con el
  comando: `ffmpeg -f concat -safe 0 -i concat.txt -c copy curso.mp4`.
- Validaciones: mismos límites de script actuales aplicados al compuesto;
  `scene` con el mismo patrón regex; cuota de disco igual que hoy.

## 5. Frontend

Nueva vista **Proyectos** (`#/proyectos`, `#/proyectos/<id>`), pestaña en el
Header entre Estudio y Biblioteca.

- **Lista**: tarjetas tipo carpeta (estética del mock FileManager/GlowCard:
  glass, acentos por proyecto) con nombre, nº clips, nº renderizados/stale,
  duración total estimada (suma de duraciones de jobs), calidad.
  Crear/renombrar/borrar (borrado en dos toques, patrón existente).
- **Detalle**: lista ordenada de clips (miniatura del job, título, duración,
  estado: `renderizado | desactualizado | sin render | en cola/render`),
  reordenar (subir/bajar), añadir clip (vacío / desde video de Biblioteca),
  editar estilo del proyecto (editor pequeño con CodeMirror), notas de
  continuidad visibles ("clip anterior termina: …"), botones Exportar
  (manifest) y Descargar curso (zip), y "Re-renderizar desactualizados".
- **Integración Estudio**: "Editar clip" navega al Estudio con contexto de
  clip (badge "Proyecto X · clip N", calidad bloqueada a la del proyecto,
  botón *Guardar en clip* que persiste script+escena, y el render desde ahí
  se liga al clip). Salir del contexto vuelve al modo libre actual.
  El estado SSE existente ya refresca jobs; el detalle de proyecto se
  refresca al recibir eventos `job` con `clip_id`.
- **Biblioteca**: acción "Añadir a proyecto…" en cada video (selector de
  proyecto → crea clip al final). Aviso al borrar un video que es render
  vigente de un clip.

## 6. Errores y bordes

- Render de clip con proyecto/clip borrado a mitad: el worker actualiza el
  clip solo si aún existe y sigue apuntando; si no, el job queda como
  render suelto normal.
- Script compuesto inválido (colisión de nombres con style_block): el error
  de manim/detect_scenes se muestra con la nota del offset de líneas.
- Cambio de calidad del proyecto: permitido solo si ningún clip tiene
  render vigente (si no, 409 con detalle) — evita cursos mixtos.
- Posiciones: transacción única al mover/borrar; siempre compactas 0..n-1.
- SQLite sin FK enforcement (no se activa PRAGMA foreign_keys): la
  integridad la mantiene la capa ProjectStore con el lock existente.

## 7. Pruebas

- Unit/API (pytest, mismo patrón conftest): CRUD proyectos/clips, orden y
  compactación, render de clip → job ligado → clip actualizado al terminar
  (worker simulado como en tests actuales), stale por cambio de script y de
  style_block, protección de purgas en lote, from_job_id con calidad
  distinta, export manifest y archive (zip válido, orden, concat.txt),
  quality inmutable con renders, borrados con desligue.
- E2E manual con cookie firmada contra la API real al final.
- Frontend: build limpio; QA visual Playwright existente si aplica.

## 8. Qué NO entra (YAGNI)

- Concatenación/transcodificación dentro de la app (la unión es externa).
- Audio, subtítulos, multi-usuario, permisos por proyecto.
- Drag & drop sofisticado (basta subir/bajar).
- Versionado de scripts de clip (el historial de jobs ya da algo).
