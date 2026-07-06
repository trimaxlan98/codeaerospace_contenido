# Rediseño panel Admin: sub-pestañas — diseño

**Fecha:** 2026-07-06
**Ámbito:** ManimStudio (`studio/frontend/`), vista Admin de coderesearch.space

---

## Problema

`Admin.jsx` apila 5 secciones (`salud del sistema`, `historia · gráficas`, `gestión
de jobs`, `almacenamiento`, `contenedores docker`) en una sola columna con
`overflow: auto` (`.monitor`). Resultado: demasiada información amontonada y las
gráficas históricas de CPU/RAM/Disco (SVG de altura fija 130px en `charts.jsx`)
quedan chicas y apretadas al competir por espacio vertical con todo lo demás.

## Diseño

Se introduce una barra de sub-pestañas dentro de Admin, reutilizando el patrón
`.seg` / `.seg__opt` (`role="tablist"`) ya usado en `Assistant.jsx` y
`Studio.jsx`. Solo se renderiza el contenido de la pestaña activa.

**3 pestañas:**

1. **Salud** — KPIs (CPU/RAM/Disco/Renders/Activos), barras (meters) de
   CPU/RAM/Swap/Disco, y las 3 gráficas históricas (CPU/RAM/Disco, últimos 30
   min) en 3 columnas — igual disposición que hoy pero con mucha más altura al
   no compartir espacio con jobs/almacenamiento/contenedores.
2. **Jobs** — contenido actual de "gestión de jobs" (botones de purga + tabla),
   sin cambios de lógica.
3. **Recursos** — combina "almacenamiento" (barra de cuota) + "contenedores
   docker" (tabla), ambos de solo lectura sobre infraestructura.

**Cambios de código:**

- `Admin.jsx`: `useState` para la pestaña activa (default `'salud'`), barra de
  tabs (`<div className="seg admin__tabs" role="tablist">`), render condicional
  de las 3 secciones ya existentes reordenadas. No cambia ninguna prop ni
  lógica de fetch/acciones (`onJobsChanged`, `run`, `clearFailed`, `purge`).
- `charts.jsx`: sube la constante `H` (altura del SVG) de 130 a ~220px y ajusta
  el padding derivado (`PAD`); no cambia lógica de escalado ni de datos.
- `styles.css`: agrega `.admin__tabs` (mismo estilo que `.seg`, con margen
  respecto al borde del panel).

**Fuera de alcance:** sin cambios de backend, API, ni de los datos mostrados —
reorganización puramente visual de componentes existentes.

## Testing

Cambio puramente de frontend (JSX/CSS), sin lógica nueva que cubrir con tests
automatizados. Verificación manual: `vite build` + revisar en el navegador que
las 3 pestañas alternan correctamente y que las gráficas se ven más grandes en
"Salud".
