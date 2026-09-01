# Auditoría de lógica UX — ManimStudio

Fecha: 2026-07-06 · Método: lectura completa del frontend (`studio/frontend/src`, ~2 000 líneas)
y de la lógica de cola del backend (`jobs.py`, `db.py`, `main.py`), más QA visual con Playwright
(build real de `dist/` con `/api` mockeado; escritorio 1440×900 y móvil 390×844).
Capturas del arnés en el scratchpad de la sesión (`qa/*.png`).

Severidad: **P0** rompe el uso o pierde trabajo · **P1** rompe el flujo · **P2** pulido.

---

## P0 — Pérdida de trabajo y estados rotos

### 1. Cambiar de pestaña destruye el trabajo del editor
`App.jsx:108-121` monta/desmonta cada vista condicionalmente. Todo el estado de `Studio.jsx`
vive en `useState` local (`script`, `quality`, `timeoutS`, `selectedId`). Consecuencia:
escribes 80 líneas de escena, pasas a Biblioteca a ver un video, vuelves — **el editor
regresó al SAMPLE**. Lo mismo pierde: la lección abierta y el scroll en Aprender, la categoría
y animación abiertas en Animaciones, la pestaña activa de Admin.
**Arreglo:** subir el estado a App (o contexto), o mantener las vistas montadas con
`display:none`, + persistir el script en `localStorage` (sobrevivir también a F5).

### 2. Móvil inutilizable en Estudio
Captura `mobile-1-studio.png`: el shell es `height:100%` fijo (`styles.css:91`) y en columna
los paneles se reparten 844 px; la sección del editor (con su toolbar y el botón **Renderizar**)
colapsa a altura 0. En móvil literalmente no se puede renderizar ni editar. Además el log
desborda su panel y se dibuja debajo de la tira de cola.
**Arreglo:** en `<lg` abandonar el layout de viewport fijo (dejar scroll de página y alturas
mínimas por panel), o pestañas internas Editor/Registro.

### 3. Paneles solapados en Biblioteca y Admin (móvil y escritorio)
Capturas `desktop-2-library.png` y `mobile-2-admin.png`: las secciones `.panel` dentro de
`main.flex-col` no tienen `shrink-0`, se comprimen para caber en el viewport y su contenido
se pinta encima de la sección siguiente (las tarjetas de video sobre la lista de fallidos;
los medidores de Salud sobre el panel Historia).
**Arreglo:** `shrink-0` en cada sección de las vistas con `overflow-auto` en el main.

### 4. Sesión expirada → interfaz zombi
`api.js` no intercepta 401 y `App.jsx` solo consulta `/api/me` al montar. Si la cookie expira:
el SSE muere (EventSource reintenta contra 401 para siempre), `refreshJobs` traga el error
(`App.jsx:34`), y cada acción falla con mensajes crípticos. Nunca se redirige a Login y no
existe ningún indicador de "desconectado / datos congelados" — grave para un centro de control.
**Arreglo:** ante 401 en cualquier request → `setAuth(false)`; añadir indicador de conexión
del stream (último evento recibido hace N s).

### 5. Sin rutas: F5, atrás y deep-links rotos
No hay router: la vista es `useState` en memoria. F5 siempre vuelve a Estudio; el botón
Atrás del navegador sale de la aplicación; no puedes enlazar una lección, una animación ni
un job. **Arreglo:** hash-router mínimo (`#/estudio`, `#/aprender/:id`, …) — no requiere
cambios en nginx.

### 6. Sin error boundary
Cualquier excepción de render deja la pantalla en negro absoluto (observado durante el QA
cuando un endpoint devolvió una forma inesperada: `useHistory` → `samples.undefined`).
**Arreglo:** ErrorBoundary raíz con mensaje y botón de recarga; defensas en `useHistory`.

---

## La cola de renders: qué es hoy y por qué confunde (P0/P1)

Respuesta directa a "¿qué lógica tiene? ¿crece indefinidamente?":

- **No es una cola, es historial.** `db.list_jobs(limit=50)` devuelve los últimos 50 jobs
  de cualquier estado; el Estudio muestra 20 (`Studio.jsx:326`) bajo el rótulo "Cola de
  renders" con un contador que es el total del historial, no los encolados. Crece hasta 50
  visibles y las filas en SQLite **nunca se purgan solas**.
- **Los jobs viejos se vuelven invisibles pero siguen ocupando disco.** Biblioteca se
  alimenta de la misma lista limitada a 50: un video más antiguo que los últimos 50 jobs
  desaparece de la UI pero sigue contando contra la cuota de `render_jobs/`. Puedes llegar
  a "Almacenamiento lleno" sin nada visible que borrar.
- **No se puede vaciar/depurar desde donde se ve.** La limpieza vive lejos: Admin → Jobs
  (solo "fallidos", ">7 días", ">30 días") y Biblioteca (uno a uno). No existe "vaciar
  historial", ni "borrar todos los terminados", ni purga con días personalizados, ni
  descartar un chip individual de la tira.
- **Límite invisible de 1 encolado.** `canSubmit` (`Studio.jsx:196`) deshabilita Renderizar
  si ya hay *un* job `queued`, sin tooltip ni mensaje — el botón simplemente no funciona y
  no sabes por qué. Es además una regla solo del frontend (la API acepta encolar sin límite).
- **Sin "Reintentar".** Para relanzar un job fallido hay que "Cargar al editor" + Renderizar.
- **Doble submit posible.** `submit` no se deshabilita mientras la petición está en vuelo.

**Propuesta de modelo:** separar *cola activa* (queued/running, con Cancelar y posición) de
*historial* (terminados, con Reintentar/Descartar/Limpiar todo), mostrar el motivo cuando
Renderizar esté deshabilitado, y añadir "Vaciar historial" + purga con días libres en Admin.

---

## P1 — Rupturas de flujo por sección

### Animaciones (la queja original) y Aprender
- Patrón "categorías arriba + lista debajo" en la misma barra: con 13 categorías la lista
  queda aplastada al fondo (captura `desktop-2-animations.png`: la lista empieza a ~600 px y
  se ven 4 ítems), y al hacer clic en una categoría nada te lleva a los resultados. En móvil
  hay que atravesar 13 botones + lista para llegar a la vista previa.
  **Arreglo:** acordeón (categoría expande sus ítems debajo, estilo submenu), o categorías
  como chips horizontales y el panel principal como **grid de tarjetas** de la categoría —
  hoy el 75 % de la pantalla está vacío hasta que eliges.
- **La búsqueda solo busca en la categoría activa** (`Animations.jsx:32-37`, igual en
  Lessons): buscar "órbita" no encuentra nada de otras categorías. Debe ser global.
- "Abrir en el Estudio" reemplaza el editor **sin confirmar** (pierdes lo que hubiera).
- Al volver a la vista, todo se reseteó (ver P0-1).
- Aprender: una lección se marca "leída" al abrirla, no al terminarla (`Lessons.jsx:59`);
  el progreso de scroll no se persiste; sin tabla de contenidos en lecciones largas.

### Estudio
- **Sobrescrituras silenciosas del editor:** "Cargar al editor", "Aplicar al editor" (IA) y
  "Abrir en el Estudio" pisan el script sin confirmación ni undo garantizado.
- **Autoscroll forzado del log** (`Studio.jsx:170-172`): mientras corre un render no puedes
  subir a leer — cada línea nueva te arrastra al fondo. Solo debe autoscrollear si ya estabas
  al fondo.
- **Sin notificación al terminar.** Si estás en otra pestaña interna, nada avisa que el
  render acabó (solo el glifo del header cambia). Falta toast + `document.title`.
- La selección `selected = … || jobs[0]` salta sola al job más nuevo cuando no hay selección
  explícita; duraciones calculadas con reloj del cliente vs. timestamps del servidor pueden
  dar valores raros; `fmtTime` muestra solo HH:MM:SS aunque el job sea de ayer.
- Timeout: input numérico sin validación en el cliente (el error llega del servidor tras
  enviar).
- La cuota de disco solo se ve en Biblioteca; el Estudio no avisa antes del 507.

### Biblioteca
- Sin ordenar/filtrar (fecha, tamaño, escena) ni selección múltiple para borrar.
- Los fallidos no muestran su mensaje de error (hay que ir al Estudio y seleccionar el chip).
- Los jobs > últimos 50 no aparecen (ver sección de cola).

### Admin
- Tabla de jobs sin acciones por fila (ni cancelar, ni borrar, ni ver log) — solo purgas en
  lote fijas (7/30 días). Sin "vaciar todo" ni días personalizados.
- La pestaña activa se resetea a Salud en cada visita (P0-1).
- Header móvil: la navegación queda recortada (solo se ve parte del tab activo); falta
  patrón de navegación móvil (captura `mobile-2-admin.png`).

---

## P2 — Pulido
- `ThemePicker` sin navegación por teclado (flechas) pese a `role=listbox`.
- El estado "error" del glifo orbital persiste hasta que otro job termine.
- Cancelar un job traga errores en silencio (`Studio.jsx:186`).
- Chips de cola: `fmtTime` ambiguo entre días; sin tooltip con el error del job.
- Contador "N videos" del header de Biblioteca cuenta solo los visibles (límite 50).

---

## Orden de ataque sugerido
1. ~~**P0-1 + P0-5** (estado global + hash-router + localStorage del script)~~ — **hecho
   2026-07-06**: vistas keep-alive (montadas y ocultas con `display:none` vía `router.js` +
   `App.jsx`), rutas `#/estudio|biblioteca|aprender/<id>|animaciones/<id>|admin/<tab>` con
   atrás/adelante y deep-links, y editor/escena/calidad/timeout persistidos en localStorage
   (sobreviven F5). Verificado con QA Playwright (15 checks funcionales).
2. ~~**Cola:** separar activa/historial, motivo visible del botón deshabilitado, Reintentar,
   Vaciar historial, y subir/paginar el límite de 50 para que Biblioteca no oculte videos.~~ —
   **hecho 2026-07-06**: tira dividida en Cola (running/queued con posición `#n` y Cancelar) e
   Historial (Reintentar, Borrar en dos toques, Vaciar historial); eliminado el límite invisible
   de 1 encolado y el doble-submit; nuevos `DELETE /api/jobs/finished` y
   `POST /api/jobs/{id}/retry`; listado sube de 50 a 500 (`JOBS_LIST_LIMIT`) para que la
   Biblioteca no oculte videos que consumen cuota. 73 tests backend + QA Playwright.
3. ~~**P0-2/P0-3** layout móvil + `shrink-0`.~~ — **hecho 2026-07-06**: el shell
   abandona el viewport fijo en `<lg` (`min-h-dvh` + scroll de página; en `lg+` sigue
   `h-dvh`); en el Estudio móvil el editor fija `62dvh` y el registro `45dvh` (ambos
   scrollean por dentro), con Renderizar y toolbar visibles; `shrink-0` en todas las
   secciones de Biblioteca y Admin (adiós solapes, también en escritorio); header en
   dos filas en móvil (marca + acciones / nav a lo ancho con scroll horizontal);
   en Aprender/Animaciones la columna de categorías se acota a `45dvh` como
   guardarraíl (su rediseño es el punto 4). Verificado con QA Playwright
   (17 checks de geometría en 390×844 y 1440×900).
4. ~~**Animaciones/Aprender:** acordeón o grid de tarjetas + búsqueda global.~~ — **hecho
   2026-07-06**: sidebar compartida `CategoryBrowser` con acordeón (la categoría expande sus
   ítems debajo, estilo submenu; sigue a la categoría del ítem abierto en deep-links) y
   búsqueda global sobre todo el índice agrupada por categoría (título+escena en Animaciones,
   título+tags en Aprender). Además: confirmación antes de pisar trabajo propio en el editor
   ("Abrir en el Estudio", "Cargar al editor" y "Aplicar" de la IA pasan por `replaceScript`),
   y una lección se marca leída al TERMINARLA (IntersectionObserver sobre el pie; funciona con
   scroll interno en escritorio y de página en móvil), no al abrirla.
5. ~~**P0-4/P0-6** (401 → login, indicador de conexión, ErrorBoundary) + toasts de fin de
   render.~~ — **hecho 2026-07-06**: cualquier 401 de la API (salvo `/api/login`) dispara
   `setAuth(false)` → login inmediato; si el SSE cae se sondea `/api/me` (acelerado a 8 s) por
   si la sesión expiró; chip ámbar "sin señal Ns" en el header cuando el stream calla >10 s;
   ErrorBoundary raíz con mensaje y recarga (adiós pantalla en negro) + defensa en `useHistory`
   ante `samples` con forma inesperada; toasts de fin de render (clic → Estudio) y
   `document.title` con "● Renderizando…" mientras corre un job. QA Playwright: 18 checks
   funcionales de los bloques 4+5, más regresión de los 17 del bloque 3.

---

# Segunda auditoría — 2026-08-15

Método: lectura completa de `studio/frontend/src` (~5 600 líneas) y de los
módulos de backend que la alimentan (`projects.py`, `projects_api.py`,
`narracion.py`, `jobs.py`), más QA visual con Playwright contra una instancia
local sembrada con el catálogo real (58 cursos leídos de
`studio/content/cursos/*/curso.json`).

Contexto: la primera auditoría es de julio, cuando la app renderizaba escenas
sueltas. Desde entonces el catálogo pasó a **58 proyectos / ~300 clips** en
familias, y el trabajo real se hace con `studio/tools/`. Los 6 P0 de julio
siguen resueltos; lo que sigue es nuevo.

## P0 — la base visual estaba anulada

1. **Ni un borde ni anillo de foco en toda la app.** `styles.css` (sin
   `@layer`, y por tanto ganando a todo `theme.css`) traía
   `* { border-color: transparent !important; outline-color: transparent
   !important }`. Todo `border-line` era invisible y `:focus-visible` nunca
   se pintaba: **fallo de accesibilidad WCAG 2.4.7**. Por lo mismo su `body`
   ganaba y la tipografía caía a system-ui pese a cargar Inter.
2. **`--line: transparent` en los 4 temas**, un segundo interruptor del mismo
   fallo; además dejaba **invisible la barra de scroll**
   (`scrollbar-color: var(--line-strong)`) en una interfaz llena de paneles
   con scroll interno.
3. **Paneles indistinguibles del fondo**: velo de vidrio oscuro sobre lienzo
   oscuro (`--surface: rgba(23,23,23,.05)` sobre `#030712`).
4. **Las pestañas Salud / Jobs / Recursos de Admin eran invisibles**:
   `StarfieldBackground` es una capa opaca `fixed inset-0` con `z-0` que
   tapaba todo contenido no posicionado posterior en el árbol.

## P0 — comportamiento

5. **Cancelar la narración de otro proyecto.** `run` es global y el detalle no
   miraba `run.project_id`: un proyecto ajeno mostraba el progreso de otro y
   su botón *Cancelar narración* **abortaba el trabajo del otro proyecto**.

## P1 — el flujo de cursos

6. **Proyectos era una rejilla plana de 58 tarjetas** sin buscador, orden ni
   agrupación, con 41 de ellas pertenecientes a 3 familias.
7. **La duración del clip no se veía en ningún sitio**, siendo el dato del que
   depende el formato (28–45 s). El backend ya la calculaba y la servía
   (`video_s` en `GET /api/projects/{id}/narracion`).
8. **La narración solo se veía si ya había audio**: desde la app no había
   forma de saber qué faltaba narrar.
9. **El guion generado no se podía leer** sin bajarse el zip del curso, pese a
   existir `GET /api/projects/{pid}/narracion/{cid}/texto`.
10. **Sin vuelta al proyecto desde el Estudio**: editar un clip y volver
    significaba caer en la lista y buscar el curso entre 58.
11. **Biblioteca con cientos de tarjetas llamadas `Clip1`…`Clip8`**, sin
    buscador ni orden, y sin decir a qué curso pertenece cada render.
12. **Los fallidos no mostraban su error** (vivía solo en el chip del Estudio).

## P2

13. **El registro del Estudio arrastraba al fondo** en cada línea nueva
    (pendiente desde julio): imposible leer un traceback durante el render.
14. **Sin atajo de teclado para renderizar** en el bucle editar → render →
    leer → corregir.
15. **`Timeout` sin normalizar**: vaciar el campo mandaba `NaN` a la API.
16. **Cancelar un job se tragaba el error** en silencio.
17. **`FileManager.jsx`**: 916 líneas de mock sin ninguna llamada a la API y
    sin importar en ningún sitio desde `c90bee4`.
18. **La muestra del tema claro `daylight`** enseñaba un lienzo oscuro.
19. **Coste del fondo animado**: `requestAnimationFrame` sin límite con
    enlaces O(n²) entre 85 partículas y un `getComputedStyle` por fotograma,
    sin respetar `prefers-reduced-motion`, en una consola que se deja abierta
    horas.

**Estado:** 1–19 corregidos en la rama `ui/rediseno-empresarial` (sprints 0 y
1). El detalle de cada arreglo y lo que queda vivo están en
`UX-REDISENO.md`; las reglas para no repetirlos, en `DESIGN-SYSTEM.md`.

---

# Tercera auditoría — 2026-08-15 (tras los sprints 0–6)

Automatizada con Playwright sobre la app real: **6 vistas × 4 temas = 24
combinaciones**, más una medición de contraste de **12 pares de tokens en cada
tema (48 comprobaciones)**, el recorrido de foco por teclado y el
comportamiento de los popovers. El arnés vive en el scratchpad de la sesión;
lo que mide está descrito aquí para poder repetirlo.

## Qué se midió y con qué criterio

| Dimensión | Criterio |
|-----------|----------|
| Contraste texto/fondo | AA: 4,5:1 texto normal · 3:1 indicadores no textuales. Los velos translúcidos se componen sobre el lienzo antes de medir |
| Foco | Todo elemento alcanzable con Tab debe tener `outline` o `box-shadow` visible |
| Desborde | `scrollWidth − clientWidth ≤ 1 px` en el documento, escritorio y móvil |
| Consola | Cero `pageerror` y cero `console.error` en las 24 combinaciones |
| Popovers | Dentro del viewport, recibiendo el clic (nada encima) y cerrando con Escape |

## Resultado

- **Contraste: 48/48** tras corregir un hallazgo (abajo). El resto de los
  temas iba sobrado: el mínimo del tema oscuro por defecto es 3,67:1
  (`faint`) y el máximo 16,7:1 (`ink`).
- **Foco: 18/18** elementos con indicador visible al tabular. Confirma que el
  `border-color/outline-color: transparent !important` que mató el foco (P0-1
  de la auditoría anterior) sigue enterrado.
- **Desborde: 0** en las 24 combinaciones, escritorio y móvil.
- **Consola: 0 errores** en las 24 combinaciones.
- **Popovers: correctos** — dentro del viewport, por encima del contenido y
  cerrando con Escape. El criterio 4 del brief («sin menús que se sobrepongan»)
  se da por cumplido: el único popover hecho a mano, el selector de temas de la
  barra, desapareció en el sprint 3; los que quedan son de Radix con portal.

## Hallazgo corregido

**`daylight · faint / canvas = 2,34:1`** (mínimo 3:1). El único tema claro
usaba slate-400 (`#94a3b8`) sobre `#f1f5f9` para el texto terciario — fechas,
unidades, contadores —, que es texto real y no adorno. Corregido a slate-500
(`#64748b`): **4,34:1**, AA incluso como texto normal.

Es el mismo patrón que ya obligó a oscurecer `accent`, `ok` y `brand` en el
sprint 2: **en el tema claro los tonos 400–500 de la paleta no valen**. La
regla está en `DESIGN-SYSTEM.md`.

## Restos benignos que se dejan a propósito

- `api.metrics` no lo llama nadie: las métricas llegan por el stream SSE. Se
  conserva porque el endpoint existe y es la vía de consulta puntual.
- `components/ui/tooltip.jsx` no se usa todavía. Es parte de la base del
  sistema de diseño que `DESIGN-SYSTEM.md` manda ampliar, no código muerto.

---

# Cuarta auditoría — 2026-09-01 (regresión de las superficies nuevas)

El tablero del rediseño cerró el 2026-08-20 con los 12 criterios verificados.
Entre el 21 y el 29 de agosto entraron ~1 900 líneas de interfaz nueva que
**nunca pasaron por él**: Estudio v2 (`PeliculaPanel`, paleta de comandos,
`Atajos`, sonido en cursos) y presentaciones (`PresentacionPanel`,
`AbrirComoPresentacion`). Esta auditoría las mide contra los mismos criterios
y, de paso, vuelve a medir lo viejo.

## El cambio de método: medir lo que se PINTA, no lo que se declara

La tercera auditoría comparó **12 pares de tokens por tema**. Ese método tiene
un punto ciego enorme: no ve un color escrito a mano en el JSX, ni ve un token
correcto puesto sobre un fondo que no estaba en la lista de pares.

El instrumento nuevo recorre **cada nodo de texto visible del DOM**, lee su
`color` computado y **compone el fondo real** subiendo por los ancestros hasta
encontrar uno opaco (los velos de vidrio se apilan: un chip `bg-surface-2`
dentro de un panel `bg-surface` no está sobre el lienzo, está sobre los dos).
Clasifica por tamaño y peso — 3:1 para texto grande, 4,5:1 para el resto — y
salta los subárboles `aria-hidden`.

Cobertura: **4 temas × 8 vistas × 2 viewports** (1440×900 y 390×844), más
**5 overlays** abiertos uno a uno en los 4 temas y los 2 viewports, más un
recorrido de tabulación de 26 paradas por vista.

## Lo que encontró: 130 fallos de contraste, en tres familias

### 1. El editor de código era ilegible en el tema claro (1,60:1)

`Studio.jsx`, `Learn.jsx` (×2) y `ClipAssistant.jsx` pasaban `theme="dark"`
**fijo** a CodeMirror, mientras `styles.css` fuerza
`.cm-editor { background: transparent }` para que herede el panel. En
`daylight` eso pintaba la paleta One Dark sobre un panel casi blanco:

| token | color | sobre `#f9fbfc` |
|-------|-------|-----------------|
| literal | `#e5c07b` | **1,60:1** |
| operador | `#abb2bf` | 2,05:1 |
| función | `#61afef` | 2,27:1 |
| palabra clave | `#c678dd` | 2,83:1 |
| clase | `#e06c75` | 3,07:1 |

El editor es el núcleo del Estudio y el cuerpo de las lecciones de Aprender.
En el único tema claro, ilegible entero. **Arreglo:** `themes.js` gana una
marca `light` por tema y un store del tema activo (`useThemeId`,
`useSyncExternalStore` sobre `data-theme`, el mismo patrón que
`StarfieldBackground`); `useEditorTheme()` devuelve `'light'` o `'dark'` y los
cuatro CodeMirror lo consumen.

### 2. Un color escrito a mano en el registro de render (1,77:1)

`text-[#a8bcd4]` en el `<pre>` del registro del Estudio y en dos sitios del
asistente. Sobre lienzo oscuro daba 10,4:1; sobre `#f1f5f9`, **1,77:1**.
Venía del rediseño original (`20c4cdd`) y sobrevivió a la tercera auditoría
justamente porque no es un token. **Arreglo:** token nuevo `--code-ink`
(salida monoespaciada: ni `ink` ni `muted`), con el mismo `#a8bcd4` en los
tres temas oscuros —cero cambio visual— y `#334155` en `daylight` (9,45:1).

### 3. `--faint` no cumplía AA en ningún tema

| tema | faint | canvas | surface | surface-2 |
|------|-------|--------|---------|-----------|
| orbital | `#5c6a80` | 3,67 | 3,41 | **3,18** |
| ion | `#438e62` | 5,00 | 4,58 | **4,22** |
| nebula | `#7c3aed` | 3,62 | 3,37 | **3,15** |
| daylight | `#64748b` | **4,34** | 4,57 | 4,67 |

La tercera auditoría ya había subido el `faint` de `daylight` a `#64748b`
declarando que 4,34:1 «cumple AA incluso como texto normal». **No: AA como
texto normal son 4,5:1.** Y de los tres temas oscuros no se midió el `faint`
contra nada.

Importa porque los **59** usos de `text-faint` del código no son adorno:
contadores (`6/6 proyectos · 2 familias`, `16 de 17 renders`,
`0/18 lecciones leídas`), unidades (`UTC`, `s`), la carga del servidor, la
pista de teclado `Ctrl K` de la paleta y la columna de tipo de sus resultados.
La ficción de «token decorativo» ya la había roto la propia nota del sprint 9
(«esto es un contador que se lee»).

**Arreglo:** `--faint` sube en los cuatro temas hasta cumplir 4,5:1 sobre el
fondo más claro en que aparece, quedando aún por debajo de `--muted` para que
la escala tipográfica sobreviva:

| tema | antes | ahora | peor caso | `muted` ahí |
|------|-------|-------|-----------|-------------|
| orbital | `#5c6a80` | `#778396` | 4,55 | 5,91 |
| ion | `#438e62` | `#4b9369` | 4,53 | 7,48 |
| nebula | `#7c3aed` | `#9762f1` | 4,55 | 6,59 |
| daylight | `#64748b` | `#617188` | 4,54 | 6,92 |

Dos casos no se arreglan subiendo el token, porque el fondo son **dos velos
apilados** (~4,05:1 ahí) y llegar a 4,5 colapsaría `faint` contra `muted`:

- Los `·` sueltos de la tira de la cola y de la cabecera de Proyectos son
  separadores puros → `aria-hidden="true"`. WCAG 1.4.3 exime el texto
  decorativo, y de paso un lector de pantalla deja de decir «punto medio»
  entre cada par de datos.
- La columna de tipo de la paleta de comandos (`Ir a`, …) sí es dato: la fila
  **seleccionada** sube ahora de tono entera (`muted`), como ya hacían su
  rótulo y su icono. Es el único sitio con fondo `surface-2`.

## Lo que estaba bien

- **Solapes: 0.** Los 5 overlays × 4 temas × 2 viewports salen dentro del
  viewport, reciben el clic (nada encima) y cierran con Escape. El criterio 4
  sigue cumplido por construcción: todo lo que flota es Radix con portal, y la
  escala de capas (barra 40 · avisos 50 · diálogo 60/61 · select 70 · tooltip
  80) no tiene huecos.
- **Foco: limpio.** Las únicas paradas de tabulación sin anillo son los `div`
  internos de CodeMirror, que gestiona su propio cursor.
- **Desborde horizontal: 0** · **errores de consola: 0**, en las 64
  combinaciones de la primera pasada y las 40 de overlays.

## Un aviso sobre el propio instrumento

El primer informe acusó al botón primario del login de **1,26:1** en
`daylight`. Era falso: `theme.css` anima el cambio de tema
(`transition: all .3s`) y la medición cayó **dentro** de la transición, sobre
un color interpolado que no existe en reposo. Con 700 ms de espera el fallo
desaparece y el botón mide lo que debe (blanco sobre `#0369a1`). Cualquier
auditoría automática de color en esta app tiene que esperar a que la
transición termine, o se inventará defectos.

## Resultado final

**0 fallos** en las 64 combinaciones de vistas y las 40 de overlays, tras los
arreglos. Contraste, desborde, consola, capas, Escape y foco.
