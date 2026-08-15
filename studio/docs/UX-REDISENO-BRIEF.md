# Brief — Rediseño integral de ManimStudio a estándar empresarial

Encargo del dueño del producto (2026-08-15). Este documento es el **punto de partida**
del agente que ejecuta el rediseño (cron diario 09:03). No es el diseño: el diseño se
escribe en `studio/docs/UX-REDISENO.md` durante la primera ejecución.

---

## 1. Qué se pide (palabras del dueño, ordenadas)

| # | Encargo | Criterio de aceptación |
|---|---------|------------------------|
| 1 | El login "está todo oscuro y ni se ve el logo" | Login legible, con la marca CO.DE Academy visible y contraste AA; se ve bien en los 7 temas |
| 2 | Favicon | Favicon propio (SVG + PNG + apple-touch), no el de Vite; `<title>` y manifest coherentes |
| 3 | "Los temas son muy básicos y a veces feos en su implementación" | Sistema de temas con tokens reales (superficie, línea, texto, acento, estados), auditado en las 8 vistas; ningún tema con texto ilegible o paneles invisibles |
| 4 | Sin menús que se sobreponen | Cero solapes: popovers/menús con capa y `z-index` de sistema, cierre por Esc y clic fuera; verificado en escritorio y móvil |
| 5 | Sin interfaces saturadas de información o componentes | Jerarquía visual por vista: una acción primaria, densidad controlada, lo secundario colapsado |
| 6 | Mejor flujo de trabajo y fluidez excepcional | Navegación sin pérdidas de estado, transiciones, estados de carga/vacío/error en todas las vistas, teclado y foco |
| 7 | Que las secciones tengan sentido; **fusionar si hace falta** | Mapa de navegación justificado por tarea, no por endpoint. Fusiones permitidas (p. ej. Biblioteca ↔ Proyectos, Animaciones ↔ Aprender) |
| 8 | **Todas las configuraciones de usuario a un menú de Configuración** | La barra superior deja de llevar ajustes (tema, contraseña, sesión, preferencias). Todo vive en `#/configuracion` |
| 9 | Fácil de usar sin saber programar, **sin perder potencia** | Rutas guiadas para el novato (plantillas, asistente, formularios) que conviven con el editor de código, voz, video, audio, texto y las librerías propias |
| 10 | Mejorar la sección Aprender | Lectura cómoda, progreso, búsqueda, continuidad con Animaciones/Estudio |
| 11 | El tema global CO.DE Academy debe renderizarse **siempre** | Verificar que `branding.aplicar` cubre todo camino de render (cola, thumbnails, demos de Animaciones, re-render) y hacerlo visible en la UI |
| 12 | Documentar todo, llegar a producción en el VPS y todo a GitHub | Docs actualizados, PR mergeado a `main`, `dist/` reconstruido en el VPS, prod verificada |

**Libertad creativa concedida.** Lo único intocable es la potencia actual: renderizado
Manim, cola, narración/voz, exportación de video, librerías de contenido propias.

---

## 2. Estado real al momento del encargo (verificado, 2026-08-15 08:10)

### Trabajo del agente UX/UI anterior — **sin commitear y a medio camino**
La sesión previa (`80f80f6d`, ver `.claude/RESUME.md`) murió por rate limit a las 06:52.
Dejó 4 archivos modificados en el árbol de trabajo, sin commit:

- `studio/frontend/src/styles.css` — **de ~660 líneas a 72**. Eliminó un reset global
  (`* { border-color: transparent !important }`) que, al no estar en `@layer`, ganaba a
  todo `theme.css`: por eso no se veía ni un borde, el anillo de `:focus-visible` era
  invisible y la tipografía caía a system-ui en vez de Inter. Ahora solo quedan `.boot`,
  `.login__sky`, `.editor` (CodeMirror) y `.reader` (markdown).
- `studio/frontend/src/theme.css` — los 7 temas tenían `--surface` como velo **oscuro**
  sobre lienzo oscuro (paneles indistinguibles del fondo) y `--line: transparent`. Los
  pasó a velo claro con valores de borde reales.
- `studio/frontend/src/themes.js` — retoque menor.
- `studio/frontend/src/components/StarfieldBackground.jsx` — el fondo hacía
  `getComputedStyle` por fotograma y enlaces O(n²) a 60 fps; ahora ~30 fps, acento releído
  por `MutationObserver` sobre `data-theme`, y fotograma único con `prefers-reduced-motion`.

**Este trabajo va en la dirección correcta: conservarlo como base, no revertirlo.**
Pero está sin verificar — hay que compilar, revisar las 8 vistas en los 7 temas y
commitearlo como primer paso del rediseño.

### El build local no compila ahora mismo
`npm run build` falla: `Cannot find package '@tailwindcss/vite'`. `node_modules` está
desactualizado respecto a `package.json` (falta Tailwind v4 y sus dependencias).
**Primer comando de la sesión: `cd studio/frontend && npm install`.**

### Stack del frontend
React 18 + Vite 5 + **Tailwind v4** (`@tailwindcss/vite`, tokens en `theme.css`) +
Radix UI (`dialog`, `select`, `tabs`, `tooltip`, `slot`) + `class-variance-authority` +
`tailwind-merge` + `lucide-react` + fuentes Inter / JetBrains Mono / Space Grotesk +
CodeMirror. Ya hay un embrión de design system en `src/components/ui/`
(`button`, `dialog`, `input`, `select`, `tooltip`) — ampliarlo, no inventar otro.

### Superficie a rediseñar (`studio/frontend/src`, ~5 600 líneas)
| Archivo | Líneas | Nota |
|---------|--------|------|
| `FileManager.jsx` | 916 | El más grande; candidato claro a descomponer |
| `Projects.jsx` | 806 | Proyectos, clips, continuidad, export, narración |
| `Studio.jsx` | 630 | Editor + cola + log |
| `Admin.jsx` | 290 | Salud / Jobs / Recursos |
| `Animations.jsx` | 270 | Biblioteca curada + alta web |
| `Library.jsx` | 277 | Videos renderizados |
| `App.jsx` | 266 | Shell, router hash, sesión |
| `Assistant.jsx` | 219 | Asistente Vertex AI (Gemini 2.5) |
| `Lessons.jsx` | 184 | **Aprender** |
| `ChangePassword.jsx` | 136 | Cambio obligatorio en primer login |
| `Header.jsx` | 103 | La barra que hay que vaciar de ajustes (encargo 8) |
| `Login.jsx` | 101 | Encargo 1 |
| `ThemePicker.jsx` | 76 | Se muda a Configuración |

### Auditoría previa
`studio/docs/UX-AUDITORIA.md` (2026-07-06, 179 líneas) listó 6 P0 — pérdida de estado al
cambiar de pestaña, móvil inutilizable, paneles solapados, sesión zombi, sin rutas, sin
error boundary. Varios se arreglaron después (rutas hash, ErrorBoundary, `shrink-0`,
401 → login). **Releerla y verificar cuáles siguen vivos antes de rediseñar encima.**

### La marca CO.DE Academy en los renders (encargo 11)
Ya existe y es obligatoria del lado del servidor: `studio/backend/app/branding.py` anexa
el bloque `code_brand` **al final** de cada `scene.py` (`jobs.py:89`), salvo que el script
ya mencione `code_brand` (los cursos con `style_block.py` propio). Va en `try/except`: la
marca nunca tumba un render. Tests en `studio/backend/tests/test_branding.py`.
Lo que falta: comprobar que **ningún** camino se salta `branding.aplicar` (thumbnails,
demos de Animaciones, re-renders) y que la UI lo comunique.

---

## 3. Restricciones operativas (no negociables)

- **Producción está en el VPS, no en esta máquina.** `ssh root@187.124.55.225`, repo en
  `/var/www/codeaerospace_contenido`. Esta laptop es solo desarrollo (el servicio
  `manimstudio-backend` está `inactive` aquí).
- **Desplegar el frontend = compilar en el VPS**: `git pull` + `cd studio/frontend &&
  node_modules/.bin/vite build`. nginx sirve `dist/` desde disco. Verificar con
  `curl -s https://coderesearch.space | grep -o 'index-[a-z0-9]*\.js'`.
- Backend: `sudo systemctl restart manimstudio-backend.service` (1 worker — la cola y el
  bus SSE viven en memoria del proceso; no añadir workers).
- Tests backend antes de desplegar: `cd studio/backend && venv/bin/pytest -q` (117 tests).
- **Nunca commitear** `.env`, `gcp-key.json`, `render_jobs/`, `manimstudio.db*`,
  `metrics_history.json*`, `node_modules/`.
- Ramas: el trabajo va en `ui/rediseno-empresarial` — **está por crear**; este brief, el
  prompt y el lanzador del cron siguen sin commitear en el árbol de trabajo, así que el
  primer commit de la rama debe incluirlos. PR a `main`, commits atómicos por sprint,
  asuntos de commit **sin acentos**.
- **Trampa del `.gitignore`: `*.png`, `*.jpg` y `*.gif` están ignorados en todo el repo.**
  Un favicon PNG o un logo PNG nuevo **no entra al commit** en silencio. Opciones: usar
  SVG (preferible para el favicon), añadir una excepción explícita
  (`!studio/frontend/public/*.png`) o `git add -f`. Verifica siempre con `git status` que
  el asset llegó al commit antes de desplegar; si no, en producción faltará el archivo.
- Detalles y trampas del sistema: skill `manimstudio` (`.claude/skills/manimstudio/SKILL.md`)
  y `studio/docs/README.md`.

---

## 4. Cómo se ejecuta

Un crontab del usuario dispara `studio/tools/cron_rediseno_ui.sh` todos los días a las
09:03. El script lanza Claude Code en modo headless con el prompt de
`studio/tools/cron_rediseno_ui.prompt.md`, con `flock` para que dos ejecuciones no se
pisen, y deja el log en `~/.local/state/manimstudio-rediseno/<fecha>.log`.

Instalación de la entrada (la ejecuta el dueño, Claude no tiene permiso para escribir el
crontab):

```
( crontab -l 2>/dev/null; echo "3 9 * * * /home/alanrosasp/Documentos/github/codeaerospace_contenido/studio/tools/cron_rediseno_ui.sh" ) | crontab -
```

Cada ejecución:

1. Lee este brief y `studio/docs/UX-REDISENO.md` (el plan vivo, con su tablero de sprints).
2. Continúa por el primer sprint no terminado; no repite lo hecho.
3. Cierra el sprint con: build verde, tests verdes, QA visual, commit, push, deploy y
   una línea en el tablero.
4. Si el tablero está completo y prod verificada, no toca nada: solo informa.

Todo hallazgo de diseño se documenta en `studio/docs/UX-REDISENO.md`; las decisiones de
sistema (tokens, componentes, capas, navegación) en `studio/docs/DESIGN-SYSTEM.md`.
