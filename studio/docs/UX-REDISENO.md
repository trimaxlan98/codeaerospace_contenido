# Rediseño de ManimStudio — plan vivo y tablero

Encargo y criterios de aceptación: `UX-REDISENO-BRIEF.md`.
Decisiones de sistema (tokens, capas, componentes): `DESIGN-SYSTEM.md`.
Auditoría histórica: `UX-AUDITORIA.md` (2026-07-06) + la sección nueva de 2026-08-15.

Rama de trabajo: `ui/rediseno-empresarial`. Un commit atómico por sprint,
asuntos **sin acentos**. Deploy = `git pull` en el VPS + `vite build`
(frontend) y `systemctl restart manimstudio-backend` (backend).

---

## Principio rector

ManimStudio dejó de ser "una consola para renderizar una escena suelta". Hoy
el catálogo son **58 proyectos / ~300 clips** organizados en familias
(Aerodinámica 1.1–4.5, Electromagnetismo 1.1–4.3, Metrología óptica 1.1–3.3)
y el trabajo real se hace con las herramientas de `studio/tools/`
(`render_local.py`, `subir_curso.py`, `guiones.py`, `mux.sh`). La app web es
el **panel de control de ese catálogo**: mirar estado, disparar lo que falta,
leer el resultado. Todo el rediseño se juzga contra esa tarea.

---

## Tablero de sprints

| # | Sprint | Estado | Commit |
|---|--------|--------|--------|
| 0 | Base visual: bordes, foco, temas, coste del fondo | ✅ hecho 2026-08-15 | ver abajo |
| 1 | Flujo de cursos: índice por familias, duración de clip, narración | ✅ hecho 2026-08-15 | ver abajo |
| 2 | Login legible con marca CO.DE Academy + favicon propio (encargos 1 y 2) | ✅ hecho 2026-08-15 | ver abajo |
| 3 | Vista `#/configuracion`: tema, contraseña, sesión, preferencias fuera de la barra (encargo 8) | ✅ hecho 2026-08-15 | ver abajo |
| 4 | Mapa de navegación: fusionar secciones que no se justifican por tarea (encargo 7) | ✅ hecho 2026-08-15 | ver abajo |
| 5 | Rutas guiadas para no-programadores sin perder el editor (encargo 9) | ✅ hecho 2026-08-15 | ver abajo |
| 6 | Aprender: lectura, progreso, continuidad con Animaciones/Estudio (encargo 10) | ✅ hecho 2026-08-15 | ver abajo |
| 7 | Marca CO.DE Academy garantizada en todo camino de render + visible en la UI (encargo 11) | ⏳ pendiente | — |
| 8 | Auditoría de los 4 temas en las 8 vistas + cero solapes de menús (encargos 3 y 4) | ✅ hecho 2026-08-15 | ver `UX-AUDITORIA.md` |

Leyenda: ✅ hecho · 🟡 parcial · ⏳ pendiente.

**Producción:** sprints 0–5 desplegados el 2026-08-15 (PR #22, #23, #25, #27
y #29 a `main`, `git pull` + `vite build` en el VPS). El sprint 4 sirve
`index-D5BP1EWT.js`, el mismo hash que produjo el build local ya sometido a
QA; comprobado además que el bundle de producción contiene la interfaz nueva
(«Animaciones por dominio», «Curso de Manim», «Con video») y ya no la vieja
(ni «Biblioteca» ni el `ThemePicker`), con `/api/health` devolviendo
`runner: true`. El sprint 5 sirve `index-TLSc1W7U.js`, otra vez el mismo hash
que el build local ya sometido a QA, con «Empezar desde», «Curso monográfico»
y «Modo guiado» presentes en el bundle. Verificado con cargas reales de
https://coderesearch.space en escritorio y móvil: bundle nuevo servido, título
e iconos de marca correctos, `/api/health` con runner vivo, sin errores de
consola. El sprint 3 se comprobó además **con sesión** (cookie firmada con
`MS_SECRET_KEY`, el método E2E de la skill): `#/configuracion` con sus cinco
secciones, las cuatro miniaturas de tema con lienzos distintos y la barra sin
*Salir*, en 1440×900 y 390×844.

**Trampa del despliegue:** en el VPS `node` solo existe bajo nvm. `vite build`
falla con `/usr/bin/env: 'node': No such file or directory` si no se antepone
`export PATH=/root/.nvm/versions/node/v24.15.0/bin:$PATH`.

---

## Sprint 0 — la base visual estaba rota (hecho 2026-08-15)

Diagnóstico: la app **no tenía ni un borde ni anillo de foco visible**, y no
por falta de estilos sino por dos interruptores que los anulaban.

1. **`styles.css` (legacy, sin `@layer`) mataba a `theme.css`.** Contenía

   ```css
   * { border-color: transparent !important; outline-color: transparent !important; }
   ```

   Como Tailwind v4 mete todo `theme.css` en `@layer base` y las reglas **sin
   capa siempre ganan a las de capa**, ese reset se imponía a todo el sistema
   de diseño: cabeceras de panel, separadores de filas, bordes de input,
   tarjetas y tablas quedaban invisibles, y `:focus-visible { outline }`
   nunca se pintaba (**fallo de accesibilidad WCAG 2.4.7**). Por la misma
   razón su `body { font-family: var(--sans) }` ganaba: la app se veía en
   system-ui y las tres fuentes variables descargadas no se usaban.
2. **`theme.css` declaraba `--line: transparent` y `--line-strong: transparent`
   en los 4 temas** ("no borders for seamless glassmorphism"). Efecto extra:
   la barra de scroll (`scrollbar-color: var(--line-strong)`) era invisible en
   una interfaz llena de paneles con scroll interno.
3. **Los velos de vidrio eran oscuros sobre lienzo oscuro** (`--surface:
   rgba(23,23,23,.05)` sobre `#030712`): los paneles no se distinguían del
   fondo. El tema claro `daylight` tenía el problema simétrico.
4. **`StarfieldBackground` tapaba contenido.** Es una capa `fixed inset-0`
   **opaca** que pinta `var(--canvas)`; con `z-0` (posicionada) quedaba por
   encima de todo contenido **no posicionado** que viniera después en el
   árbol. Víctima concreta: las pestañas **Salud / Jobs / Recursos** de Admin
   (un `<div>` plano, sin `.panel`) eran invisibles.
5. **Coste del fondo:** `requestAnimationFrame` sin límite, enlaces O(n²)
   entre 85 partículas y un `getComputedStyle` **por fotograma**, en una
   consola que se deja abierta horas vigilando renders. Sin
   `prefers-reduced-motion`.

Arreglos:

- `styles.css`: de 594 a 72 líneas. Fuera el reset destructivo y el `body`
  duplicado; quedan solo `.boot`, `.login__sky`, `.editor` (CodeMirror) y
  `.reader` (markdown de Aprender), que son las cuatro cosas que no se pueden
  expresar con utilidades. Las ~120 clases legacy restantes no las usaba
  ningún JSX.
- `theme.css`: `--line` / `--line-strong` con valores reales por tema y velos
  de superficie claros en los tres temas oscuros (y más opacos en el claro).
- `themes.js`: la muestra de `daylight` enseñaba un lienzo oscuro; ahora
  enseña el suyo (`#f1f5f9`).
- `StarfieldBackground`: `-z-10`, ~30 fps, acento releído por
  `MutationObserver` sobre `data-theme` en vez de por fotograma, y fotograma
  único con `prefers-reduced-motion`.
- Borrado `FileManager.jsx` (916 líneas): un mock sin ninguna llamada a la API
  que no estaba importado en ningún sitio desde el commit `c90bee4`.

---

## Sprint 1 — el flujo de cursos (hecho 2026-08-15)

### Proyectos: de rejilla plana a índice de familias

La lista era una rejilla plana de tarjetas sin buscador, sin orden y sin
agrupación. Con 58 proyectos —de los cuales 41 pertenecen a 3 familias— era
un muro. Ahora:

- **Agrupación por familia** leyendo el propio nombre (`Familia · N.M
  Título`), plegable y persistida en `localStorage`. Un prefijo con un solo
  proyecto (p. ej. `Marca · Intro y cierre`) no crea grupo: cae en *Cursos
  sueltos*.
- **Progreso agregado** por familia y global (clips totales / listos /
  desactualizados / sin render) con barra de dos tramos (verde vigente, ámbar
  desactualizado).
- **Buscador** sobre nombre y descripción, **filtro** por estado (todos / con
  pendientes / completos) y **orden** por actividad o nombre. Buscando o
  filtrando los grupos se abren solos.
- Dentro de una familia las tarjetas enseñan solo la parte de lección del
  nombre (el prefijo ya está en la cabecera del grupo) y ordenan por número
  de lección, no por actividad.
- El botón destructivo de cada tarjeta aparece al pasar por encima o con foco
  de teclado: con ~60 tarjetas a la vista, permanente era ruido y riesgo.

### Detalle: lo que el pipeline necesita mirar

- **Duración real de cada clip**, que es el dato del que depende todo el
  formato (28–45 s, el mismo rango que valida `studio/tools/render_local.py`).
  El backend ya la calculaba (`narracion.duracion_mp4` → `video_s` en
  `GET /api/projects/{id}/narracion`) y **la UI no la enseñaba en ningún
  sitio**. Ahora va como distintivo junto al estado del clip, en ámbar si se
  sale del rango.
- **Panel de estado del curso**: render (listos/total + cuántos hay que
  rehacer), duración total del curso y cuántos clips se salen del rango, y
  narración (al día/total + voz).
- **Fila de narración siempre visible** cuando el backend sabe algo del clip.
  Antes solo aparecía si ya había audio, así que desde la app no había forma
  de ver qué faltaba narrar.
- **Lector del guion** (`GET /api/projects/{pid}/narracion/{cid}/texto`): el
  endpoint existía desde el primer día y no había ninguna forma de leer el
  texto sin bajarse el zip del curso.

### Corrección de comportamiento: la narración de otro proyecto

`run` es **global** (solo se genera una narración a la vez en toda la app) y
el detalle lo tomaba como propio sin mirar `run.project_id`. Consecuencias
reales: un proyecto ajeno mostraba "Narrando 3/9…" con el progreso de otro, y
su botón **Cancelar narración abortaba el trabajo del otro proyecto**. Ahora
se distingue la corrida propia de la ajena; con una ajena en curso se explica
la espera y el botón de generar queda deshabilitado con su motivo (antes
fallaba con un 409 críptico).

### Estudio

- **Volver al proyecto** desde el contexto de clip. El viaje de vuelta era:
  nav Proyectos → caías en la **lista** (la ruta pierde el id al navegar al
  Estudio) → buscar el curso entre 58 → abrirlo.
- **El registro ya no arrastra al fondo**: solo autoscrollea si ya estabas
  abajo. Antes era imposible subir a leer un traceback mientras el render
  seguía escribiendo (pendiente desde la auditoría de julio).
- **Ctrl/⌘+Enter renderiza** desde el editor.
- El campo *Timeout* se normaliza al salir (vaciarlo mandaba `NaN` a la API).
- Cancelar un job ya no se traga el error: si falla de verdad, se dice.

### Biblioteca

- **Nombre del curso en cada tarjeta.** Casi todos los renders son clips y su
  escena se llama `Clip1`…`Clip8`: eran cientos de tarjetas indistinguibles.
- **Buscador** (escena + curso) y **orden** (recientes / antiguos / más
  pesados / nombre).
- Los fallidos muestran su mensaje de error, que hasta ahora vivía solo en el
  chip del Estudio.

### Verificación

`npm run build` verde · `venv/bin/pytest -q` 149/149 · QA visual con
Playwright contra una instancia local sembrada con el catálogo real (58
cursos desde `studio/content/cursos/*/curso.json`, mp4 con duraciones dentro
y fuera de rango, narración parcial): escritorio 1440×900, móvil 390×844,
temas oscuro y claro, sin errores de consola.

---

## Sprint 2 — la puerta de entrada y la marca (hecho 2026-08-15)

Encargos 1 y 2. Diagnóstico del dueño: *"el login está todo oscuro y ni se ve
el logo"*, y el favicon seguía siendo el de Vite.

### Por qué el login estaba "todo oscuro"

La tarjeta era un `GlowCard`: un panel con `--backdrop: var(--glass-bg)` —un
velo del **4,5 %**— sobre el cielo animado, y encima una viñeta que oscurecía
hasta `--canvas`. Resultado: un rectángulo apenas más claro que el fondo, sin
borde perceptible. Su resplandor era además un `hsl()` **morado fijo**
(`glowColor="purple"`), ajeno a los cuatro temas, seguía el puntero con un
listener global de `pointermove` e inyectaba un `<style>` con reglas
`[data-glow]` por cada instancia montada.

Y de marca no había nada: el único símbolo era `OrbitGlyph`, que es el
**indicador de estado del render**, no un logotipo. En la puerta de entrada de
la consola de un canal, la marca del canal no aparecía.

### Lo que hay ahora

- **Marca en la interfaz** (`components/Brand.jsx`): `BrandMark` (glifo),
  `Wordmark` (`CO.DE ACADEMY` con el punto en ámbar) y `HudCorners` (las
  cuatro escuadras que ya enmarcan cada escena renderizada). Es
  deliberadamente la misma familia visual que
  `manim_extensions/code_brand.py` estampa en el video: consola y render se
  reconocen como lo mismo.
- **`AuthCard`** sustituye a `GlowCard` (borrado; no lo usaba nadie más):
  columna de marca + formulario en escritorio, apilados en móvil, con fondo
  `bg-canvas/88` y `border-line-strong`. La tarjeta se lee como tarjeta en los
  cuatro temas y ya no depende de `backdrop-filter`.
- **`PasswordInput`** en el sistema (`ui/input.jsx`): el conmutador de
  visibilidad estaba copiado en Login y ChangePassword, y lo volverá a
  necesitar Configuración (sprint 3).
- **La marca aparece en todo el recorrido**, no solo en el login: glifo +
  `CONECTANDO…` en la pantalla de arranque y wordmark bajo *ManimStudio* en la
  cabecera de todas las vistas.
- **Iconos propios** en `frontend/public/`: `favicon.svg` (el que usan los
  navegadores modernos), `favicon-32.png`, `apple-touch-icon.png`,
  `icon-192/512.png` y `site.webmanifest`. Los genera
  `frontend/tools/brand_icons.mjs` desde una sola definición de la geometría,
  rasterizando con el Chromium de Playwright (la máquina no tiene
  rsvg/inkscape/magick y no hacía falta una dependencia nueva).
  `index.html` estrena título, descripción, `theme-color` y manifest.

### Dos hallazgos de paso

1. **La lista de temas del arranque en `index.html` estaba desfasada**: seguía
   validando siete ids (`aurora`, `deepspace`, `solar` ya no existen). Un tema
   retirado guardado en `localStorage` se escribía tal cual en `data-theme`, no
   casaba con ninguna regla CSS y la app arrancaba con los tokens de `:root`
   mientras el selector marcaba otra cosa. Ahora valida los cuatro reales.
2. **El tema claro no cumplía AA** (medido, no estimado): blanco sobre
   `--accent: #0ea5e9` daba **2,8:1** en el botón primario, `text-ok` **2,3:1**
   y `text-warn` **2,6:1** sobre el lienzo. Los cinco tokens de color del tema
   `daylight` bajan dos escalones de la misma familia
   (`accent #0369a1`, `cyan #1d4ed8`, `ok #047857`, `warn #8f6106`,
   `err #b91c1c`) y ahora todo el texto pasa 4,5:1. Es parte del sprint 8, pero
   el botón *Entrar* del login es texto sobre acento: no se podía cerrar el
   encargo 1 ("contraste AA") sin arreglarlo.

El ámbar de la marca tiene el mismo problema al revés: `#f59e0b` sobre lienzo
claro da 1,6:1. Por eso `--brand` es un token por tema (ámbar del canal en los
tres oscuros, `#b45309` en `daylight`) en vez de un literal.

### Verificación

`npm run build` verde · `venv/bin/pytest -q` 149/149 (el backend no se tocó) ·
contraste calculado sobre el peor caso real de la tarjeta (lienzo al 88 % sobre
la parada más clara del cielo, más el velo de la columna de marca): mínimo
**4,70:1** en los cuatro temas · QA visual con Playwright: login en 4 temas ×
{1440×900, 390×844}, estado de error, cambio obligatorio de contraseña
(levantando `must_change_password` en la base de QA), pantalla de arranque y
las 6 vistas internas en tema claro y oscuro. Sin errores de consola.

---

## Sprint 3 — Configuración, y la barra deja de ser un panel de control (hecho 2026-08-15)

Encargo 8: *"todas las configuraciones de usuario a un menú de Configuración"*.

### Lo que había

La barra superior mezclaba tres cosas distintas en la misma fila: navegación
(6 pestañas), estado del sistema (CPU, RAM, reloj, señal del stream) y
**ajustes** (selector de tema y *Salir*). Dos problemas concretos:

1. **El selector de tema era un popover propio**, con su `mousedown` global,
   su `Escape` y su `z-[70]` a mano — justo el patrón que el encargo 4 quiere
   erradicar. Además solo daba una lista de nombres: los cuatro temas se
   elegían a ciegas salvo por tres puntos de color.
2. **`Salir` estaba a 40 px de `Admin`**, sin confirmación. Cerrar la sesión
   por error mientras se vigila un render es barato de provocar y caro de
   sufrir (vuelves al login con el render corriendo a ciegas).

Y no había ningún sitio donde vivieran las preferencias: lo que no cupo en la
barra simplemente no existía.

### Lo que hay ahora

Vista nueva **`#/configuracion`** (`Settings.jsx`), con índice lateral en
escritorio y una sola columna en móvil, en cinco secciones:

- **Apariencia.** Los cuatro temas como tarjetas con **miniatura viva**: el
  contenedor de la miniatura lleva `data-theme` y por tanto **se pinta con los
  tokens reales** de ese tema (`theme.css` define los tokens por atributo, no
  por elemento). Cero valores copiados a un tercer sitio. Para que funcionara
  también con el tema por defecto hubo que abrir el selector a
  `:root, [data-theme="orbital"]`: antes la miniatura de `orbital` heredaba los
  tokens del tema activo y mentía. Debajo, **fondo animado** (automático /
  desactivado) con el resultado — `animado` / `estático` — junto al control,
  porque en «automático» decide el sistema operativo.
- **Interfaz.** *Vista al abrir* (la app entraba siempre en el Estudio aunque
  el trabajo real empiece en Proyectos), *avisos de fin de render* y
  *telemetría en la barra* (CPU/RAM/reloj) — este último es el encargo 5
  aplicado a la barra: quien no quiere instrumentos los apaga y la barra queda
  en navegación + marca + señal del stream.
- **Cuenta y sesión.** Usuario (fijo, del servidor), cambio de contraseña
  desplegable en la propia vista y cierre de sesión **en dos toques**.
- **Datos locales.** Qué guarda la app en este navegador, clave a clave y con
  su tamaño, y un borrado que restablece tema y preferencias **conservando el
  script del editor** (es lo único irrecuperable de la lista) y sin tocar nada
  del servidor.
- **Acerca de.** Marca CO.DE Academy, estado del asistente IA y enlace a
  Admin → Salud.

La barra superior se queda con navegación, estado y **un solo botón que es
navegación, no ajuste**: *Configuración*. `ThemePicker.jsx` se borra.

### Piezas nuevas del sistema

- **`prefs.js`** — store de preferencias sobre `useSyncExternalStore`: la misma
  preferencia la leen la cabecera, el fondo y los avisos, así que un `useState`
  local no valía. El tema **no** vive aquí: lo lee `index.html` antes del primer
  pintado para evitar el destello.
- **`ui/switch.jsx`** — `Switch` (`role="switch"` a mano, sin dependencia nueva)
  y `SettingRow`, la fila rótulo + explicación + control que arma toda la vista.
- **`components/PasswordChange.jsx`** — el cambio de contraseña se usa ahora en
  dos marcos (la pantalla obligatoria del primer login y esta vista); la
  validación y el manejo de errores viven en un sitio.

### Trampa encontrada

**Los anclajes de toda la vida no se pueden usar aquí.** La navegación es por
hash, así que un `<a href="#cuenta">` cambiaría de vista en vez de bajar a la
sección. El índice lateral navega con `scrollIntoView` sobre refs, sin tocar la
URL.

### Verificación

`npm run build` verde · `venv/bin/pytest -q` 149/149 (el backend no se tocó) ·
QA Playwright contra una instancia local real (backend uvicorn + vite):
**35/35 checks** — barra sin ajustes, las 5 secciones, 4 miniaturas con lienzos
distintos (`#030712` / `#010c08` / `#06010d` / `#f1f5f9`), tema aplicado y
persistido, telemetría que vacía la barra y vuelve, fondo a estático, vista al
abrir (y un enlace directo ganándole), borrado local que conserva el script,
error real de contraseña actual (422 del backend) y no-coincidencia en cliente,
cierre de sesión en dos toques hasta volver al login, y **cero solapes** entre
secciones en 1440×900 y 390×844, tema oscuro y claro. Sin errores de consola
(salvo el 422 provocado a propósito).

---

## Pendiente conocido (entra en sprints siguientes)

- La tira de cola/historial del Estudio y los avisos de fin de render siguen
  identificando los jobs solo por escena (`Clip3`), igual que hacía la
  Biblioteca antes del sprint 1.
- `Projects.jsx` (≈900 líneas) y `Studio.jsx` (≈650) piden descomponerse.
- El resumen de `GET /api/projects` no trae estado de narración, así que el
  índice de familias no puede mostrar progreso de narración sin abrir cada
  curso.
- Los 4 temas están saneados y el claro ya cumple AA en sus tokens, pero falta
  la pasada formal vista por vista que pide el criterio 3 del brief (y la
  revisión de solapes de menús del criterio 4).
- La web usa Space Grotesk donde el video usa Rajdhani: el wordmark de la
  consola no es tipográficamente idéntico al del render. Traer la TTF del repo
  a `public/` es viable si algún día se quiere fidelidad exacta.

---

## Sprint 4 — el mapa de navegación (hecho 2026-08-15)

Criterio 7 del brief: *que las secciones tengan sentido; fusionar si hace
falta*. La barra tenía seis entradas y dos de ellas no se sostenían.

### Aprender + Animaciones eran la misma sección partida en dos

El hallazgo que decide el sprint está en el backend, no en la interfaz:
`animations.py` dice que **el id de una animación es 1:1 el de su lección**
(misma categoría, mismo `NN-slug`) y las dos vistas leían el **mismo**
`studio/content/lessons/categories.yaml`. Eran dos proyecciones de un solo
índice. En la práctica hoy no se solapan —18 lecciones en las 4 categorías
`manim-*` (la teoría) y 89 animaciones en 13 categorías de dominio (los
ejemplos)— pero eso empeoraba las cosas, no las mejoraba: **buscar "órbita" en
Aprender no encontraba la animación de órbita**, porque cada pestaña buscaba
solo en su mitad del índice.

Ahora hay una sola sección **Aprender** (`Learn.jsx`) con:

- un índice con dos grupos, *Curso de Manim* y *Animaciones por dominio*;
- **una sola búsqueda** que recorre los dos;
- un lector que enseña lo que el item tenga: markdown con progreso de lectura
  y navegación anterior/siguiente, o el script con *Abrir en el Estudio*. Si
  algún día un id trae las dos cosas —lo que el backend contempla— aparece un
  conmutador Lección/Animación en la cabecera del lector.

`CategoryBrowser` pasa de `categories` a `groups`; el alta de secciones y
animaciones vive en el grupo que le corresponde.

### Biblioteca era un nombre prestado y una lista partida

*Biblioteca* chocaba con la biblioteca de contenido de Aprender, y la vista
partía la misma lista en dos bloques: una rejilla de videos y, debajo, una
lista de "fallidos / cancelados". Son **el mismo objeto (un job) en distinto
estado**. Ahora es **Renders** (`Renders.jsx`): una rejilla con filtro de
estado (Con video / Fallidos / Todos), la cuota de disco reducida a una línea
de contexto —la versión con historia sigue en Admin → Recursos— y el error del
job visible en su propia tarjeta.

### La unión con Proyectos es un enlace, no una fusión

El brief permitía fusionar Biblioteca ↔ Proyectos. No se hizo, y la razón es
que responden a tareas distintas: Proyectos es *construir un curso*, Renders
es *el archivo de todo lo que ha salido de la cola*, incluidos los renders
sueltos que no pertenecen a ningún proyecto. Lo que sí faltaba era el camino
entre ambas: cada tarjeta de Renders dice de qué curso es y **lleva a él**.

### Nav resultante

`Proyectos · Estudio · Renders · Aprender · Admin` (+ Configuración), de seis
entradas a cinco, con Proyectos primero porque es donde vive el trabajo real.

**Enlaces antiguos:** `#/animaciones/<id>` y `#/biblioteca` siguen funcionando
(alias en `router.js`), y una preferencia de *vista al abrir* guardada con un
id viejo (`library`, `lessons`, `animations`) se traduce en vez de caer al
valor por defecto sin explicación.

**Verificación:** `vite build` verde, `pytest -q` 149/149, QA Playwright 17/17
checks en 1440×900 y 390×844 (nav de 5 entradas y en orden, los dos grupos de
Aprender, búsqueda global cruzando ambos, lector de lección y de animación,
los dos alias de ruta, filtro de estado de Renders, error visible en la
tarjeta fallida, salto de tarjeta a proyecto, sin scroll horizontal en móvil),
sin errores de consola.

---

## Sprint 5 — plantillas de curso y asistente de clip (hecho 2026-08-15)

Criterio 9 del brief: *fácil de usar sin saber programar, **sin perder
potencia***. El dueño añadió la condición dura al asignarlo: «cuida que para
quien sabe programar no sea molesto, esto solo se debe habilitar cuando se
requiera». De ahí sale el reparto de este sprint en dos piezas con reglas
distintas.

### Plantillas de curso — siempre disponibles, sin coste para nadie

Crear un proyecto «en blanco» deja el estilo compartido vacío, y sin él los
clips no heredan la identidad CO.DE Academy, la tipografía de marca ni los
helpers de rótulo. Ese bloque son ~90 líneas que **todos** los cursos del repo
repiten palabra por palabra (compárese cualquier
`studio/content/cursos/*/style_block.py`), incluida la sombra de `Text` que
arregla una trampa real de Manim 0.20. No es conocimiento de novato: es
copiar-pegar que hasta ahora tocaba hacer a mano.

`Nuevo proyecto` gana un selector *Empezar desde* con tres opciones:

- **En blanco** (seleccionada por defecto) — el diálogo se comporta
  exactamente igual que antes de que esto existiera. Quien sabe lo que hace no
  paga ni un clic.
- **Curso monográfico** — 8 clips a 1080p, el estilo con el tema oficial y un
  clip de arranque que ya renderiza.
- **Lección de una familia** — 4 clips a 1080p; deduce la constante `LECCION`
  del propio nombre `Familia · N.M Título`.

El textarea de estilo sigue mandando: si escribes algo, reemplaza al de la
plantilla.

**Validado renderizando de verdad**, no solo leyendo: la plantilla se
materializó como curso real y se pasó por `studio/tools/render_local.py` en el
contenedor. Sale un mp4 con escuadras HUD, marca de agua CO.DE Academy y la
tipografía de marca, y el propio validador lo marca `<-- CORTO (minimo 28 s)`
porque el clip de arranque dura 3,4 s — que es justo lo que el distintivo de
duración de Proyectos enseñará en ámbar hasta que el clip crezca.

### Asistente de clip — detrás de una preferencia, apagada por defecto

Esta es la parte que **sí** estorbaría a quien escribe Manim a mano, así que
va tras `prefs.guided`, **`false` por defecto**: con el modo guiado apagado,
Proyectos no monta ni el botón. El camino de siempre —*Añadir clip* y *Editar
en Estudio*— no cambia un pixel. Se enciende en Configuración → Interfaz.

Con él encendido, *Asistente* abre un formulario con tres orígenes:

1. **Descríbelo y lo escribe la IA** (solo si Vertex está configurado; si no,
   la opción aparece deshabilitada y dice por qué). El prompt lleva el
   contexto real: nombre y descripción del curso, número de clip, **dónde
   terminó el clip anterior** (`final_state`), los helpers del estilo y el
   tope de 28–45 s del formato.
2. **Partir de una animación de ejemplo** — copia el script de cualquiera de
   las 89 animaciones de Aprender.
3. **Esqueleto en blanco**.

Dos decisiones que importan:

- **Nunca guarda a ciegas.** Genera, **enseña** el script y la escena que
  detectó (con `POST /api/scenes`, el AST del backend, no una suposición) y
  solo entonces ofrece *Guardar como clip*.
- **Quita los imports de cabecera** cuando el proyecto tiene estilo, y lo
  avisa. Es obligatorio: el estilo hace `from manim import *` y después
  instala la sombra de `Text`; si el clip vuelve a importar, ese `import *`
  **repone el `Text` de manim y se pierde la corrección**. Es la trampa que
  los cursos del repo documentan como «los clips NO repiten imports».

**Verificación:** `vite build` verde, `pytest -q` 149/149, QA Playwright
**21/21** en 1440×900 — 18 del recorrido principal (empezando por comprobar
que sin modo guiado no aparece ni un botón nuevo, que la plantilla crea sus 8
clips con escena `Clip1`…`Clip8` y que el estilo llega con `code_brand` y la
sombra de `Text`, que al apagar el modo guiado el asistente desaparece) y 3 de
la rama de copiar una animación (avisa de las 3 líneas de import quitadas y
conserva el cuerpo). Sin errores de consola. Y el render real descrito arriba.

---

## Sprint 6 — Aprender: lectura y progreso (hecho 2026-08-15)

Criterio 10: *lectura cómoda, progreso, búsqueda, continuidad con
Animaciones/Estudio*. La búsqueda y la continuidad con Animaciones ya las
resolvió la fusión del sprint 4; quedaban la lectura y el progreso.

**Lo que NO se hizo, y por qué.** La auditoría de julio pedía «tabla de
contenidos en lecciones largas». No hay lecciones largas: las 18 miden 47–66
líneas con 4–5 encabezados. Un índice flotante ahí sería adorno que estorba,
así que se descartó tras medirlo.

### Los ejemplos de código ahora se pueden ejecutar

Este era el agujero real. Las lecciones enseñan Manim con **42 bloques de
código** y no se podía hacer nada con ellos: ni copiarlos cómodamente ni
probarlos. En un producto cuyo objetivo es aprender Manim, leer un ejemplo sin
poder ejecutarlo es el fallo, no un detalle.

Cada bloque gana una barra (visible al pasar por encima o al tabular hasta
ella, para no competir con la lectura) con **Copiar** y, cuando el bloque
define una `Scene` completa, **Probar en el Estudio**.

El botón aparece **solo donde va a funcionar**: 4 de las 18 lecciones traen un
bloque ejecutable; el resto son fragmentos (`self.play(...)`) que sueltos solo
darían «el script no define ninguna Scene» en el Estudio. Envolverlos en un
andamio se descartó: muchos referencian variables de bloques anteriores y el
resultado sería un `NameError` presentado como si fuera a funcionar.

La barra se inyecta en el DOM tras pintar el markdown en vez de tocar
`markdown.js`: lo que se añade son nodos propios sobre HTML ya saneado por
DOMPurify, y el efecto limpia lo suyo antes de que React reemplace el
contenido.

### Progreso que sobrevive al navegador

- La **posición de lectura se guarda por lección** (`ms_lessons_progress`) y se
  retoma al volver — antes el scroll solo vivía mientras la vista siguiera
  montada. Solo se retoma entre el 5 % y el 95 %: al principio no hay nada que
  retomar y al final desorienta más de lo que ahorra.
  **Trampa que costó una iteración:** restaurar el scroll justo después de
  `setItem` no funciona; el markdown aún no está en el DOM y el contenedor mide
  0, así que el cálculo siempre acababa arriba. Ahora lo aplica un efecto que
  reintenta unos fotogramas hasta que el contenido tiene altura (KaTeX y las
  fuentes la cambian después del primer pintado).
- El índice muestra una **barra fina** bajo las lecciones empezadas y sin
  terminar, y el grupo lleva su **contador** (`Curso de Manim 8/18`).
- El estado vacío ofrece **Empezar el curso / Continuar** con la primera
  lección sin leer, y felicita cuando están las 18.

### El curso es una secuencia, no cuatro islas

*Anterior/siguiente* recorre ahora **las 18 lecciones seguidas** en vez de
pararse al final de cada categoría; cuando el salto cruza de categoría, el
botón lo dice en su `title`. Antes, terminar «Fundamentos 05» te dejaba sin
salida.

**Verificación:** `vite build` verde, `pytest -q` 149/149, QA Playwright
**14/14** en 1440×900 y 390×844 (contador del grupo, *Empezar el curso*, barra
por bloque, *Copiar* dejando el código en el portapapeles, avance guardado al
50 % y **retomado tras recargar**, marcado como leída al terminar, salto de
categoría, y *Probar* llevando el código real al Estudio). Sin errores de
consola.

---

## Sprint 8 — auditoría de temas y solapes (hecho 2026-08-15)

Criterios 3 y 4 del brief. Se ejecutó como **auditoría automatizada**, no como
revisión a ojo: 6 vistas × 4 temas, 12 pares de tokens por tema, recorrido de
foco por teclado y comportamiento de popovers. Método, criterios y resultado
completo en `UX-AUDITORIA.md` (tercera auditoría).

Resumen: **48/48** pares de contraste tras corregir uno (`faint` del tema
claro, 2,34:1 → 4,34:1), **18/18** elementos con foco visible, **0** desbordes
horizontales y **0** errores de consola en las 24 combinaciones, y popovers
dentro del viewport, por encima del contenido y cerrando con Escape.

El criterio 4 («sin menús que se sobrepongan») se cumple por construcción
desde el sprint 3: el único popover hecho a mano —el selector de temas de la
barra— se sustituyó por tarjetas dentro de Configuración; los que quedan son
de Radix con portal.
