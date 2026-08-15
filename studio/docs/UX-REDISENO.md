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
| 2 | Login legible con marca CO.DE Academy + favicon propio (encargos 1 y 2) | ⏳ pendiente | — |
| 3 | Vista `#/configuracion`: tema, contraseña, sesión, preferencias fuera de la barra (encargo 8) | ⏳ pendiente | — |
| 4 | Mapa de navegación: fusionar secciones que no se justifican por tarea (encargo 7) | ⏳ pendiente | — |
| 5 | Rutas guiadas para no-programadores sin perder el editor (encargo 9) | ⏳ pendiente | — |
| 6 | Aprender: lectura, progreso, continuidad con Animaciones/Estudio (encargo 10) | ⏳ pendiente | — |
| 7 | Marca CO.DE Academy garantizada en todo camino de render + visible en la UI (encargo 11) | ⏳ pendiente | — |
| 8 | Auditoría de los 4 temas en las 8 vistas + cero solapes de menús (encargos 3 y 4) | 🟡 parcial (temas saneados en el sprint 0; falta la pasada vista por vista) | — |

Leyenda: ✅ hecho · 🟡 parcial · ⏳ pendiente.

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

## Pendiente conocido (entra en sprints siguientes)

- La tira de cola/historial del Estudio y los avisos de fin de render siguen
  identificando los jobs solo por escena (`Clip3`), igual que hacía la
  Biblioteca antes del sprint 1.
- `Projects.jsx` (≈900 líneas) y `Studio.jsx` (≈650) piden descomponerse.
- El resumen de `GET /api/projects` no trae estado de narración, así que el
  índice de familias no puede mostrar progreso de narración sin abrir cada
  curso.
- Los 4 temas están saneados pero falta la pasada formal vista por vista que
  pide el criterio 3 del brief.
