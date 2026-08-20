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
| `--line` / `--line-strong` | bordes, separadores, **barra de scroll** | **nunca `transparent`**: toda la estructura de la app se dibuja con `border-line` y el scrollbar usa `--line-strong` |
| `--ink` / `--muted` / `--faint` | texto principal / secundario / terciario | |
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
| Diálogos | portal de Radix | `components/ui/dialog` |

**Trampa:** `StarfieldBackground` es una capa **opaca** (pinta `var(--canvas)`).
Con `z-0` se colocaba por encima de cualquier contenido **no posicionado**
—los `.panel` se salvaban porque `@utility panel` lleva `position: relative`,
pero un `<div>` plano no— y ocultó las pestañas de Admin. Cualquier capa de
fondo nueva va con z negativo.

## Mapa de navegación

Una entrada por **tarea**, no por endpoint (sprint 4). Cinco secciones más
Configuración:

| Vista | Hash | Tarea |
|-------|------|-------|
| Proyectos | `#/proyectos[/<id>]` | construir y vigilar un curso (el hub: ~60 cursos en familias) |
| Estudio | `#/estudio` | escribir y renderizar una escena o el clip de un curso |
| Renders | `#/renders` | el archivo de todo lo que salió de la cola, con o sin video |
| Aprender | `#/aprender[/<id>]` | teoría del curso de Manim **y** animaciones de ejemplo, un solo índice |
| Admin | `#/admin[/<tab>]` | salud del host, jobs y disco |
| Configuración | `#/configuracion` | todo lo que el usuario ajusta (encargo 8) |

Reglas al tocar esto:

- **Los hash viejos no se rompen.** `router.js` mantiene alias
  (`#/animaciones` → Aprender, `#/biblioteca` → Renders) y `prefs.js` traduce
  las preferencias de *vista al abrir* guardadas con ids antiguos.
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
- Un contador que **se lee** usa `text-muted` como mínimo; `text-faint` es
  token de adorno (3,67:1 en el tema oscuro) y no llega a AA como texto
  normal.

## Convenciones de contenido

- **Idioma: español**, incluidos los comentarios del código.
- Los proyectos de una familia se nombran `Familia · N.M Título`: de ese
  prefijo salen la agrupación y el progreso agregado del índice de Proyectos.
- El formato de clip es **28–45 s** (`studio/tools/render_local.py`:
  `DURACION_MIN` / `DURACION_MAX`). Si la UI muestra duraciones, usa ese
  rango y **avisa** en vez de bloquear.
