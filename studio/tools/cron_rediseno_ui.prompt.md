Continúa el rediseño integral de ManimStudio a estándar empresarial. Trabajas en automático, con libertad creativa y sin pedir confirmaciones: el dueño ya autorizó llegar hasta producción (VPS) y GitHub.

PASO 0 — Contexto obligatorio antes de tocar nada:
1. Invoca la skill `manimstudio` (arquitectura, deploy, trampas, reglas duras).
2. Lee `studio/docs/UX-REDISENO-BRIEF.md`: es el encargo completo del dueño, con los 12 criterios de aceptación, el estado real del repo y las restricciones operativas.
3. Lee `studio/docs/UX-REDISENO.md` si existe — es el plan vivo con el tablero de sprints. Si NO existe, esta es la primera ejecución y te toca crearlo (PASO 1 del brief).
4. Lee `studio/docs/UX-AUDITORIA.md` y verifica cuáles de sus P0/P1 siguen vivos hoy.
5. Carga la skill de diseño que corresponda al sprint: `dataviz` antes de tocar cualquier gráfica del panel Admin, `claude-in-chrome` o `run` para el QA visual real de la app.

PASO 1 — Ejecuta el primer sprint NO terminado del tablero (uno por ejecución si es grande; encadena varios si son pequeños). Los sprints previstos están en el brief: fundaciones y design system, login y marca, temas, shell y navegación con la vista de Configuración, densidad y flujo, doble camino en el Estudio, Aprender, y marca CO.DE Academy garantizada en todo render.

PASO 2 — Cierre de CADA sprint, sin excepción:
- `cd studio/frontend && npm run build` verde.
- `cd studio/backend && venv/bin/pytest -q` verde si tocaste backend.
- QA visual real de lo que cambiaste, en escritorio y móvil.
- Commit atómico con asunto sin acentos y push de la rama `ui/rediseno-empresarial`.
- Actualiza el tablero de `studio/docs/UX-REDISENO.md`.
- Despliegue a producción cuando el sprint deje la app usable: PR a `main`, merge, y en el VPS `git pull` + `vite build` (+ reinicio del backend solo si lo tocaste). Verifica prod con una carga real de https://coderesearch.space.

PASO 3 — Si el tablero ya está completo y producción verificada: no toques código, solo verifica salud de prod e informa en una línea.

Termina con un resumen de qué sprint cerraste, qué quedó desplegado en producción y cuál es el siguiente.
