# CO.DE Studio — ManimStudio de escritorio

App de escritorio (Electron) para trabajar con ManimStudio **en local**, sin depender del VPS:

- **Estudio**: la misma interfaz que <https://coderesearch.space>, servida desde esta máquina
  (runner + backend levantados por la app). Un selector cambia a la instancia de producción.
- **Exports**: `exports/` ordenado por **tema → proyecto** con la regla del catálogo
  (`Área · N.M Título`, ver `studio/docs/CATALOGO-CURSOS.md`), agrupado por módulo, con
  búsqueda, reproductor, y abrir / mostrar en carpeta / copiar ruta. Verticales, promos,
  películas, presentaciones y bancos de audio van en colecciones aparte. Solo lee.
- **Terminal**: terminales reales (xterm + node-pty) abiertas en el repo, con accesos a
  *Claude Code*, *Continuar sesión* y **Nuevo curso**: un formulario (tema, área, formato,
  estilo, sonido, tamaño, permisos) que arma el encargo para la skill `curso-de-video` y lo
  lanza en una pestaña.
- **Sistema**: estado de los servicios y su registro, Docker, imagen de render, GPU, disco,
  si la interfaz compilada está al día, y tareas (recompilar interfaz, construir la imagen,
  inventariar exports, tests del backend, git).

## Instalar

**Linux** (esta máquina):

```bash
bash studio/desktop/scripts/install-linux.sh
```

Compila, prueba, instala en `~/.local/opt/code-studio` y crea el lanzador, el ícono y el
acceso directo del Escritorio. Opcional, para arrancar con el sandbox de Chromium activo en
Ubuntu 24.04+: `sudo bash studio/desktop/scripts/install-linux.sh --apparmor`.

**Windows**: [`INSTALAR-WINDOWS.md`](INSTALAR-WINDOWS.md) (los servicios corren en WSL2).

## Cómo está hecha

```
src/main.cjs         ventana, IPC, ciclo de vida (detiene los servicios al salir)
src/services.cjs     supervisa scripts/servicios.sh (nativo o vía wsl.exe); reutiliza
                     un backend que ya esté vivo en :3002 (studio/dev.sh) sin adueñarse de él
src/localServer.cjs  127.0.0.1:5190 — studio/frontend/dist + proxy /api (SSE incluido)
                     + /__media con Range y token por sesión (lo que en prod hace nginx)
src/exports.cjs      catálogo tema → proyecto (lee curso.json; solo lectura)
src/terminal.cjs     ptys; cada orden se escribe como script en .run/desktop/tareas/
src/config.cjs       ~/.config/CO.DE Studio/config.json (%APPDATA% en Windows)
renderer/            interfaz de la app (HTML/CSS/JS sin bundler)
scripts/             servicios.sh, instaladores, iconos, .env local
```

La app **no** empaqueta el repo: orquesta un checkout real (escenas, backend, venv, imagen
de Docker). Por eso una actualización del Estudio llega con `git pull` + *Recompilar
interfaz*, sin reinstalar la app.

## Desarrollo

```bash
cd studio/desktop
npm ci
npm start                 # electron . (añade --no-sandbox si AppArmor lo exige)
npm test                  # lógica pura y servidor local, sin Electron
CODE_STUDIO_SMOKE_CLAUDE=1 npx electron test/smoke.cjs --no-sandbox
                          # prueba de humo real: arranca, recorre las vistas y captura
npm run icons             # regenera build/ desde build/icon.svg
```
