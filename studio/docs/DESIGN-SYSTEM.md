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
| `--cyan` | anillo de foco y estado "en cola" | |
| `--ok` / `--warn` / `--err` | semáforo de estado | verde vigente · ámbar desactualizado/fuera de rango · rojo fallo |
| `--glass-*`, `--glow-*`, `--grad-*`, `--star-*` | vidrio, resplandores del fondo y cielo del login | |

Los cuatro temas (`orbital`, `ion`, `nebula`, `daylight`) deben definir **todos**
los tokens. La muestra de `themes.js` tiene que enseñar el lienzo real del
tema, no uno inventado.

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

## Componentes

La base vive en `src/components/ui/` (`button`, `dialog`, `input`, `select`,
`tooltip`), sobre Radix + `class-variance-authority` + `tailwind-merge`.
**Ampliar esa base, no inventar otra.** Variantes de `Button`: `primary`
(una por vista), `default`, `outline`, `ghost`, `accent`, `danger`.

Compartidos por varias vistas: `CategoryBrowser` (acordeón + búsqueda global
de Aprender y Animaciones), `DeleteButton` (destructivo en dos toques),
`GlowCard` (login y cambio de contraseña), `OrbitGlyph` (estado del sistema
como ornamento), `ErrorBoundary`.

## Accesibilidad — mínimos que se verifican

- Anillo de foco visible en todo control: `focus-visible:ring-2 ring-cyan`
  (o el `outline` de `:focus-visible` de `theme.css`). Nunca anularlo.
- Toda acción destructiva confirma en dos toques.
- Estados por color **siempre** acompañados de texto (`renderizado`,
  `desactualizado`, `sin render`), nunca solo el punto de color.
- `aria-label` en los controles que solo llevan icono; `role="alert"` en los
  mensajes de error y `role="status"` en los informativos.
- `prefers-reduced-motion` respetado por el fondo animado y el cielo del login.

## Convenciones de contenido

- **Idioma: español**, incluidos los comentarios del código.
- Los proyectos de una familia se nombran `Familia · N.M Título`: de ese
  prefijo salen la agrupación y el progreso agregado del índice de Proyectos.
- El formato de clip es **28–45 s** (`studio/tools/render_local.py`:
  `DURACION_MIN` / `DURACION_MAX`). Si la UI muestra duraciones, usa ese
  rango y **avisa** en vez de bloquear.
