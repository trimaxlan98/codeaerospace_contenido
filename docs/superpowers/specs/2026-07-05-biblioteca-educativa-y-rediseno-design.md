# Diseño: Biblioteca educativa, rediseño visual (login + 7 temas) y panel de administración

Fecha: 2026-07-05
Estado: aprobado por el usuario (conversación de brainstorming)

## Contexto

ManimStudio (`studio/`) es una consola privada de renderizado Manim: backend
FastAPI (`studio/backend/app/`), frontend React + Vite (`studio/frontend/src/`),
autenticación de usuario único con cookie firmada, runner Docker y asistente IA
(Vertex AI). Vistas actuales: Studio, Library (videos renderizados), Monitor.

Este diseño añade una biblioteca de lecciones educativas, renueva el login,
introduce un sistema de 7 temas, convierte Monitor en un panel de
administración con acciones de gestión y corrige errores de lógica detectados.

## 1. Biblioteca educativa

### Contenido

- Ubicación: `studio/content/lessons/` (Markdown versionado en git).
- 12 categorías: satélites, redes de telecomunicaciones, redes de datos,
  sistemas distribuidos, dinámica orbital, espacio, apuntamiento satelital,
  inteligencia artificial, agentes de IA, IA agéntica, tecnología de frontera,
  redes 6G.
- 4–6 lecciones por categoría (~55–60 en total), 1000–2000 palabras cada una,
  en español.
- Frontmatter YAML por lección: `title`, `category` (slug), `order`, `level`
  (`intro` | `medio` | `avanzado`), `summary`, `tags`, `minutes`.
- Estructura pedagógica: objetivos → desarrollo (con fórmulas LaTeX, tablas y
  diagramas ASCII) → ideas clave → lecturas siguientes.
- Nombre de archivo = slug estable: `<categoria>/<orden>-<slug>.md`.

### Backend (`app/lessons.py`, nuevo)

- `GET /api/lessons` → índice: categorías (slug, nombre, orden, conteo) +
  metadatos de cada lección (id, título, nivel, resumen, tags, minutos). Sin
  cuerpo de la lección.
- `GET /api/lessons/{id}` → lección completa: metadatos + markdown crudo.
- Ambos protegidos con `require_auth` (dependencia existente).
- Índice cacheado en memoria; invalidación por mtime del directorio/archivos.
- IDs validados contra path traversal (slug ∈ `[a-z0-9-]` + categoría
  conocida); nunca se construyen rutas con entrada sin validar.
- Parse de frontmatter con PyYAML (ya disponible en el venv como dependencia
  transitiva; se añade explícitamente `PyYAML>=6.0` a `requirements.txt`).

### Frontend (`Lessons.jsx`, nueva vista + pestaña "Aprender" en Header)

- Layout de dos paneles:
  - Izquierdo: categorías con conteo, lista de lecciones (nivel + minutos),
    búsqueda por título/tags.
  - Derecho: lector de la lección abierta.
- Render Markdown con `marked`, sanitizado con `DOMPurify`; fórmulas LaTeX con
  **KaTeX** (delimitadores `$...$` y `$$...$$`).
- Tipografía de lectura cómoda (ancho máximo ~70ch), barra de progreso de
  scroll, navegación anterior/siguiente dentro de la categoría.
- Progreso "leída / no leída" en `localStorage` (clave por id de lección).
- Carga perezosa: el cuerpo se pide solo al abrir la lección.

Dependencias frontend nuevas: `marked`, `dompurify`, `katex`.

## 2. Login renovado

- Card con glassmorphism: fondo translúcido con `backdrop-filter: blur`,
  borde luminoso sutil, sombra suave. Los colores derivan de los tokens del
  tema activo.
- Fondo tranquilo: gradiente animado lento + campo de estrellas/aurora suave
  en CSS puro (sin imágenes externas, sin red).
- Ojito de contraseña: botón dentro del campo que alterna
  `type="password"/"text"`, icono SVG inline (ojo / ojo tachado),
  `aria-label` y `aria-pressed`.
- Micro-detalles: transición de entrada del card, foco visible, shake sutil en
  error.
- Mensajes de error diferenciados (ver §5.1): red vs. credenciales vs. bloqueo
  por intentos (429).

## 3. Sistema de 7 temas

- Los tokens actuales de `:root` en `styles.css` se convierten en 7 conjuntos
  de variables seleccionados por `data-theme` en `<html>`.
- Cada tema define: fondos (`--void`), paneles, líneas, tinta, muted, acentos
  (primario/secundario), colores semánticos (ok/err/warn) y el fondo del login.
- Temas:
  1. **Orbital** — el actual (oro/cian sobre azul muy oscuro). Tema por defecto.
  2. **Aurora** — verdes/violetas boreales.
  3. **Deep Space** — negro OLED + magenta.
  4. **Daylight** — claro (blanco cálido); único tema claro.
  5. **Nebula** — púrpuras profundos.
  6. **Ion** — azul eléctrico/teal.
  7. **Solar** — ámbar/carbón.
- Selector en el Header: dropdown con muestra de paleta (puntos de color) por
  tema. Accesible por teclado.
- Persistencia en `localStorage`; script inline en `index.html` aplica el tema
  guardado antes del primer paint (sin flash).
- El login también respeta el tema (el selector no es visible allí; usa el
  guardado o el por defecto).

## 4. Panel de administración (Monitor → "Admin")

### Frontend

Vista renovada en secciones:
- **Salud**: KPIs grandes (CPU/RAM/disco/uptime del stream) + las gráficas
  históricas existentes (30 min), estilizadas con el tema.
- **Contenedores**: tabla mejorada (la actual, con mejor jerarquía visual);
  sigue siendo solo lectura para contenedores ajenos.
- **Jobs**: tabla de gestión con duraciones; acciones en lote:
  - "Eliminar fallidos" (error/timeout/cancelled) con confirmación armada.
  - "Purgar renders antiguos" (parámetro de antigüedad: 7/30 días) con
    confirmación.
- **Almacenamiento**: cuota con desglose (número de videos, bytes) y acceso a
  las acciones de limpieza.

### Backend

- `DELETE /api/jobs/failed` → borra todos los jobs en estado
  error/timeout/cancelled. Reutiliza la lógica de borrado individual
  existente (invalidación de cache de storage incluida). Devuelve conteo.
- `DELETE /api/jobs/older-than/{days}` → borra jobs `done` con
  `finished_at` anterior al umbral. Devuelve conteo y bytes liberados.
- Ambos con `require_auth`. Nunca tocan jobs `queued`/`running`.

## 5. Correcciones de lógica

1. `Login.jsx:19` — errores de red (excepción sin `status`) se muestran como
   "Credenciales inválidas". Distinguir: sin `status` → "No se pudo conectar";
   429 → mensaje del servidor; resto → "Credenciales inválidas".
2. `App.jsx:39` — dependencia `[auth === true]` del `useEffect` de `/api/me`
   provoca re-llamadas redundantes (p. ej. tras logout). Refactor a un flujo
   explícito: consulta inicial al montar + re-consulta del flag IA tras login.
3. `Library.jsx` — `fmtSize` muestra "0.0 MB" para tamaños < 1 MB; añadir
   escala KB.
4. `auth.py` — `LoginRateLimiter` acumula entradas por IP sin poda (fuga de
   memoria lenta). Podar entradas expiradas en `record_failure`/`check`.
5. Auditoría oportunista de `jobs.py`, `main.py` y `Studio.jsx` durante la
   implementación; hallazgos extra se corrigen en commits propios documentados.

## 6. Pruebas

- Backend (pytest, se suman a los 41 existentes):
  - Lecciones: índice, detalle, 404, rechazo de path traversal, requiere
    auth, invalidación de cache por mtime.
  - Acciones en lote: eliminar fallidos, purga por antigüedad (no toca
    queued/running), conteos correctos.
  - Rate limiter: poda de entradas expiradas.
- Frontend: sin framework de tests JS (YAGNI); verificación con `vite build`
  y revisión manual de cada vista en los 7 temas.

## 7. Orden de implementación

1. Correcciones de lógica (base limpia).
2. Sistema de temas (7 temas + selector + persistencia).
3. Login glassmorphism + ojito.
4. Panel de administración + endpoints de gestión en lote.
5. Biblioteca educativa: backend (`lessons.py`) + frontend (`Lessons.jsx`).
6. Contenido: ~55–60 lecciones en las 12 categorías.

Cada bloque se implementa con commits atómicos y sus pruebas.

## Fuera de alcance

- CRUD de lecciones desde la web (el contenido se edita en el repo).
- Framework de tests de frontend.
- Control de contenedores ajenos desde el panel admin.
- Cambios en el runner o en el pipeline de renderizado.
