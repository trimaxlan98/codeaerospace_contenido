# Sistema de diseño — ManimStudio

Decisiones de sistema del rediseño (`UX-REDISENO.md`). Documento corto a
propósito: aquí solo va lo que hay que respetar para no volver a romper la
interfaz.

## Capas de CSS — la regla que ya nos costó una vez

Tailwind v4 mete **todo `theme.css` en `@layer base`**, y en CSS las reglas
**sin capa ganan siempre a las de capa**, sin importar el orden de import ni
la especificidad. Por eso un `styles.css` sin `@layer` con

```css
* { border-color: transparent !important; outline-color: transparent !important; }
```

dejó la app entera sin bordes y sin anillo de foco durante semanas.

**Regla:** todo estilo global nuevo va en `theme.css` (dentro de `@layer base`
o como `@utility`). `styles.css` está reducido a cuatro selectores que no se
pueden expresar con utilidades (`.boot`, `.login__sky`, `.editor`, `.reader`)
y **no debe crecer**. Nada de reglas sobre `*` y nada de `!important`.

## Tokens

Definidos en `theme.css` por tema (`:root` = `orbital`, más `[data-theme="…"]`)
y expuestos a Tailwind con `@theme inline`, para que cambiar de tema en
runtime funcione (los utilitarios referencian `var()`, no el valor).

| Token | Para qué | Nota |
|-------|----------|------|
| `--canvas` | fondo del documento | |
| `--surface` / `--surface-2` | vidrio de panel / elemento elevado | **velo claro sobre lienzo oscuro**; un velo oscuro sobre fondo oscuro no se ve |
| `--elevated` | fondo **opaco** de lo que flota: diálogos, cajón del asistente, menú de `Select`, tooltip, avisos | = `surface-2` compuesto sobre el lienzo en los temas oscuros; blanco en `daylight`. Existe porque un velo se apoya en lo que tenga debajo, y debajo de un diálogo está el overlay negro: en `daylight` el panel salía gris `#acadad` y el texto secundario a 2,2–3,4:1 (sprint 11) |
| `--line` / `--line-strong` | bordes, separadores, **barra de scroll** | **nunca `transparent`**: toda la estructura de la app se dibuja con `border-line` y el scrollbar usa `--line-strong` |
| `--ink` / `--muted` / `--faint` | texto principal / secundario / terciario | los tres cumplen **AA como texto normal** (4,5:1) sobre el fondo más claro donde aparecen. `faint` NO es un token de adorno: sus 59 usos son contadores, unidades y pistas de teclado |
| `--code-ink` | salida monoespaciada: registro de render, script generado | rol propio, ni `ink` ni `muted`. Existe porque era un literal `#a8bcd4` que en `daylight` daba 1,77:1 |
| `--accent` / `--accent-ink` | firma del tema y su texto encima | |
| `--brand` / `--brand-2` | ámbar CO.DE Academy (punto del wordmark, escuadras HUD, viñetas) | **no es el acento del tema**: es la marca del canal. Ámbar `#f59e0b` en los tres temas oscuros; `#b45309` en `daylight` (el ámbar del canal sobre lienzo claro da 1,6:1) |
| `--cyan` | anillo de foco y estado "en cola" | |
| `--ok` / `--warn` / `--err` | semáforo de estado | verde vigente · ámbar desactualizado/fuera de rango · rojo fallo |
| `--glass-*`, `--glow-*`, `--grad-*`, `--star-*` | vidrio, resplandores del fondo y cielo del login | |

Los cuatro temas (`orbital`, `ion`, `nebula`, `daylight`) deben definir **todos**
los tokens. La muestra de `themes.js` tiene que enseñar el lienzo real del
tema, no uno inventado. La **lista de ids también vive en `index.html`** (el
script que fija `data-theme` antes del primer pintado): si se añade o retira un
tema hay que tocar los dos sitios, o un id guardado en `localStorage` acabará
sin reglas CSS y la app arrancará en `:root` con el selector marcando otra cosa.

Los tokens se declaran **por atributo, no por elemento**: cualquier contenedor
con `data-theme="…"` tiñe su subárbol. De ahí salen las miniaturas vivas de
Configuración, sin copiar ni un color. El tema por defecto necesita para eso el
selector doble `:root, [data-theme="orbital"]` — con solo `:root`, una
miniatura de `orbital` hereda los tokens del tema activo y miente.

**El tema claro no puede usar los tonos 500 de la paleta.** Sobre `#f1f5f9`,
`accent #0ea5e9` da 2,8:1 con texto blanco encima y `ok #10b981` da 2,3:1 como
texto: AA exige 4,5:1 (3:1 para indicadores no textuales). Por eso `daylight`
usa la misma familia dos escalones más oscura. Cualquier token de color nuevo
se mide antes de darlo por bueno.

## Marca CO.DE Academy en la interfaz

`components/Brand.jsx`: `BrandMark` (glifo), `Wordmark` (`CO.DE ACADEMY`, punto
en `--brand`) y `HudCorners` (las cuatro escuadras). Es la misma identidad que
`studio/content/manim_extensions/code_brand.py` estampa en cada video —
wordmark con el punto ámbar, escuadras HUD, ámbar → naranja— para que consola y
render se lean como una sola cosa. Divergencia consciente: el video usa
Rajdhani; la web, la display que ya carga (Space Grotesk).

Los iconos (`public/favicon.svg`, `favicon-32.png`, `apple-touch-icon.png`,
`icon-192/512.png`) los genera `frontend/tools/brand_icons.mjs`, que es la
fuente única de la geometría; el JSX de `BrandMark` la repite y debe seguirla.
**Trampa:** `*.png` está ignorado en todo el repo y `public/*.png` vive de una
excepción explícita en `.gitignore`. Si esa línea desaparece, los iconos no
llegan al VPS y producción se queda sin favicon sin que nada falle.

## Capas de apilamiento (z-index)

| Capa | z | Quién |
|------|---|-------|
| Fondo animado | `-10` | `StarfieldBackground` |
| Contenido | auto | vistas y `.panel` |
| Cabecera pegajosa | `40` | `Header` |
| Avisos de fin de render | `50` | toasts de `App.jsx` |
| Overlay de diálogo / diálogo | `60` / `61` | `components/ui/dialog`, `Assistant` (portal de Radix) |
| Menú de `Select` | `70` | `components/ui/select` |
| Tooltip | `80` | `components/ui/tooltip` |

**Lo que flota es opaco (`bg-elevated`), nunca vidrio.** El vidrio (`surface`,
`.panel`) está calibrado para apoyarse en el lienzo. Un diálogo se apoya en el
overlay `bg-black/70`, un menú o un aviso en contenido cualquiera: con vidrio,
el color del panel depende de lo que haya debajo y ningún token de texto puede
garantizar contraste. Una auditoría que compone el fondo **subiendo por los
ancestros** no lo ve —el overlay es hermano del panel, no ancestro—; la que lee
el píxel pintado sí (sprint 11).

**Trampa:** `StarfieldBackground` es una capa **opaca** (pinta `var(--canvas)`).
Con `z-0` se colocaba por encima de cualquier contenido **no posicionado**
—los `.panel` se salvaban porque `@utility panel` lleva `position: relative`,
pero un `<div>` plano no— y ocultó las pestañas de Admin. Cualquier capa de
fondo nueva va con z negativo.

## Mapa de navegación

Una entrada por **tarea**, no por endpoint (sprint 4). Siete secciones más
Configuración:

| Vista | Hash | Tarea |
|-------|------|-------|
| Proyectos | `#/proyectos[/<id>]` | construir y vigilar un curso (el hub: ~60 cursos en familias) |
| Estudio | `#/estudio` | escribir y renderizar una escena o el clip de un curso |
| Renders | `#/renders` | el archivo de todo lo que salió de la cola, con o sin video |
| Biblioteca | `#/biblioteca[/…]` | lo que se **entrega**: el árbol de `exports/` (películas, verticales, presentaciones, bancos), en solo lectura. Renders es la cocina; Biblioteca, el mostrador |
| Aprender | `#/aprender[/<id>]` | teoría del curso de Manim **y** animaciones de ejemplo, un solo índice |
| Laboratorio | `#/laboratorio` | ejecutar Python de validación en el sandbox: las sondas de las librerías, y numpy/PIL a mano (sprint R3b) |
| Admin | `#/admin[/<tab>]` | salud del host, jobs y disco |
| Configuración | `#/configuracion` | todo lo que el usuario ajusta (encargo 8) |

Reglas al tocar esto:

- **Los hash viejos no se rompen.** `router.js` mantiene alias
  (`#/animaciones` → Aprender, `#/entregas` → Biblioteca) y `prefs.js` traduce
  las preferencias de *vista al abrir* guardadas con ids antiguos. `#/biblioteca`
  llevó a Renders hasta que existió la Biblioteca de entregas (Estudio v3);
  desde entonces vuelve a significar lo que dice.
- **La barra cabe en cualquier ancho, o la entrada nueva no entra.** Con siete
  vistas, por debajo de `xl` (1280 px) solo la vista **activa** lleva rótulo y
  las demás son icono con `title` (el rótulo sigue en `sr-only`); por debajo de
  360 px, ni la activa. Lo que cede antes que la nav es la telemetría: reloj y
  rótulos de *Buscar* desde `2xl`, medidores desde 1680 px. Una vista más en
  `NAV` obliga a volver a correr `studio/tools/ux_barra.mjs`, que recorre de
  320 a 1920 px con cada vista activa y falla si algo se corta, hace scroll o
  se parte en dos líneas. La auditoría general mide 1440 y 390, y la barra se
  rompía **entre medias**: a 1280, «Admin» salía cortado.
- **Fusionar solo si las dos vistas sirven a la misma tarea.** Aprender y
  Animaciones sí (mismo índice del backend, ids 1:1, y la búsqueda partida era
  un fallo). Renders y Proyectos no: Renders incluye renders sueltos sin
  proyecto. Ahí la respuesta es un **enlace** entre ambas, no una fusión.
- Las vistas son **keep-alive** (montadas y ocultas con `display:none`), así
  que un selector de QA sin acotar encuentra controles de otras vistas: usa
  `main[data-view="…"]` como raíz.

## Componentes

La base vive en `src/components/ui/` (`button`, `dialog`, `input` +
`PasswordInput`, `select`, `switch` + `SettingRow`, `tooltip`), sobre Radix +
`class-variance-authority` + `tailwind-merge`. **Ampliar esa base, no inventar
otra.** Variantes de `Button`: `primary` (una por vista), `default`, `outline`,
`ghost`, `accent`, `danger`. `Switch` está escrito a mano (`role="switch"`):
un botón de dos estados no justifica otra dependencia de Radix.

Compartidos por varias vistas: `CategoryBrowser` (acordeón + búsqueda global
de Aprender y Animaciones), `DeleteButton` (destructivo en dos toques),
`AuthCard` + `Field` (login y cambio de contraseña), `PasswordChange`
(`useChangePassword` + campos, usados por la pantalla obligatoria del primer
login y por Configuración), `Brand`, `OrbitGlyph` (estado del render como
ornamento — **no es el logotipo**), `ErrorBoundary`.

## Dónde va cada cosa: ajustes, estado y navegación

- La **barra superior** lleva navegación, marca y **estado** (glifo del render,
  señal del stream, telemetría). **Ningún ajuste**: todo lo que el usuario
  configura vive en `#/configuracion` (encargo 8). Un control en la barra que
  abre esa vista es navegación y sí vale.
- Las **preferencias** viven en `prefs.js` (`useSyncExternalStore` +
  `localStorage`), no en `useState` de la vista: las lee más de una pieza a la
  vez. El **tema** es la excepción y tiene su propia clave, porque
  `index.html` lo aplica antes del primer pintado para evitar el destello.
- Una preferencia nueva solo entra si **hace algo visible**; si no cambia nada
  en pantalla, es ruido y no se añade.
- El **catálogo de cursos** (`GET /api/projects`) vive en `catalogo.js`, mismo
  patrón de store: una sola copia para el índice de Proyectos, la lista de
  Renders, el diálogo *A un proyecto…*, la tira de la cola del Estudio y los
  avisos de fin de render. Quien muta proyectos o clips llama a
  `refreshCatalogo()`; el índice además revalida al montarse
  (*stale-while-revalidate*), porque en el detalle de un curso se pudo
  renderizar, narrar o borrar.
- **Una entrega también se nombra por su curso.** `exports/peliculas/<id>` y
  las carpetas con slug truncado (`sat-lites-e-ia-la-red-que-aprende-a-gobe`,
  con el acento vuelto guion) no se leen. `EntregasService` recibe la lista de
  proyectos y resuelve cada carpeta por id o por cualquiera de las **dos
  familias de slug** que conviven en `exports/` (`entregas.slugs_de`); la
  interfaz enseña `titulo` y deja el nombre crudo en el `title`.
- **Un render se identifica por su curso, no por su escena.** Las escenas del
  catálogo se llaman `Clip1`…`Clip8`: cualquier sitio que enseñe un job
  (fichas de la cola, cabecera del registro, resultado, avisos, tarjetas de
  Renders) tiene que resolver `job.project_id` contra el catálogo y enseñar la
  etiqueta corta del curso. `cursoDeJob(job, catalogo)` hace justo eso.

## Una dimensión solo entra en la interfaz si el catálogo la usa

El encargo 5 (*sin interfaces saturadas*) tiene una regla operativa: un dato
que sale **igual en todas las filas** no informa, decora. La narración del
índice de Proyectos se pinta solo si algún curso tiene audio (`showNarr`), y
el filtro *Sin narrar* solo se ofrece en ese caso; en una instalación que no
usa voz, la interfaz es exactamente la de antes de que existiera el dato.

## Coste de un dato en una lista de ~60 cursos

Antes de añadir una columna al índice, mira lo que cuesta calcularla para
**todo** el catálogo. `narracion.estado_proyecto` no servía para la lista:
para decidir si una narración está *desactualizada* necesita la duración del
vídeo y `duracion_mp4` lee el archivo entero — cientos de MB por petición.
Por eso el índice usa `resumen_audio`, que solo hace un `stat` por clip, y el
estado fino se queda en el detalle del curso, donde se mira un curso a la vez.

## Navegación por hash: los anclajes están prohibidos

Con `router.js` la vista vive en el hash, así que `<a href="#seccion">` **cambia
de vista** en vez de bajar a una sección. Para navegar dentro de una vista
larga: `scrollIntoView` sobre refs (así funciona el índice de Configuración).
Solo son enlaces válidos los que apuntan a una ruta real (`#/admin/salud`).

Se borró `GlowCard`: pintaba un resplandor `hsl()` morado fijo ajeno a los
temas, dejaba la tarjeta en un velo del 4,5 % sobre el cielo (el "está todo
oscuro" del encargo 1) y montaba un `pointermove` global más un `<style>`
inyectado por instancia.

## Accesibilidad — mínimos que se verifican

- Anillo de foco visible en todo control: `focus-visible:ring-2 ring-cyan`
  (o el `outline` de `:focus-visible` de `theme.css`). Nunca anularlo.
- Toda acción destructiva confirma en dos toques.
- Estados por color **siempre** acompañados de texto (`renderizado`,
  `desactualizado`, `sin render`), nunca solo el punto de color.
- `aria-label` en los controles que solo llevan icono; `role="alert"` en los
  mensajes de error y `role="status"` en los informativos.
- `prefers-reduced-motion` respetado por el fondo animado y el cielo del login.
- **Saltar al contenido** es el primer tabulador del documento (`App.jsx`).
  No puede ser un `<a href="#...">` — ver la regla del hash — así que es un
  botón que mueve el foco al `<main>` de la vista visible (`#contenido main`).
- **Ningún color literal en el JSX.** Un `text-[#a8bcd4]` es invisible para
  una auditoría de tokens y sobrevivió a dos: en el tema claro daba 1,77:1 en
  el registro de render. Si un rol no tiene token, se crea el token.
- **`text-faint` también es AA** (4,5:1 sobre el fondo más claro en que
  aparece). Lo que NO llega es `faint` sobre **dos velos apilados** (un chip
  `bg-surface-2` dentro de un panel `bg-surface`): ~4,05:1. Ahí, o el texto es
  dato y sube a `muted`, o es un separador puro y lleva `aria-hidden="true"`.
- **Medir lo que se pinta, no lo que se declara.** Comparar pares de tokens da
  falsos aprobados; componer el fondo subiendo por los ancestros también
  (no ve un overlay hermano ni un degradado). El instrumento vigente,
  `studio/tools/ux_auditoria.mjs`, **lee el píxel**: captura la página con
  todo el texto en transparente y muestrea el fondo real bajo cada nodo. Y
  **esperar a que acabe la transición de tema** (`transition: all .3s`) o se
  miden colores interpolados inexistentes.
- **El ornamento no es fondo.** Una capa decorativa y en movimiento (hoy solo
  las partículas de `StarfieldBackground`) lleva `data-ornamento` y
  `aria-hidden`, y la auditoría la apaga antes de fotografiar el fondo: una
  estrella de 2 px bajo una letra da un contraste que no existe en el
  fotograma siguiente, y media interfaz son nodos de **un carácter** (JSX
  corta el texto en cada expresión), donde no hay sitio para muestrear
  alrededor. Regla del sprint 11: **un fallo que no se repite en dos pasadas
  es del instrumento, no de la interfaz**. Lo que sí es fondo —el lienzo, los
  velos, los chips, los degradados— lo pintan elementos quietos y se sigue
  midiendo.
- **CodeMirror sigue al tema de la app** (`useEditorTheme()` en `themes.js`).
  `.cm-editor` tiene el fondo transparente para heredar el panel, así que un
  `theme="dark"` fijo pinta One Dark sobre el lienzo claro: 1,60:1. En claro
  no basta con `'light'`: el `defaultHighlightStyle` de CodeMirror trae tres
  colores bajo AA (`#e40` de f-strings, `#085` de tipos, `#f00` de lo
  inválido), así que `useEditorTheme()` devuelve un estilo entero con esos
  tres oscurecidos. Entero, porque un resaltador no-`fallback` anula al de
  `basicSetup`.

## Convenciones de contenido

- **Idioma: español**, incluidos los comentarios del código.
- Los proyectos de una familia se nombran `Familia · N.M Título`: de ese
  prefijo salen la agrupación y el progreso agregado del índice de Proyectos.
- El formato de clip es **28–45 s** (`studio/tools/render_local.py`:
  `DURACION_MIN` / `DURACION_MAX`). Si la UI muestra duraciones, usa ese
  rango y **avisa** en vez de bloquear.
