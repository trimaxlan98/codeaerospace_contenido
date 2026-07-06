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
3. **P0-2/P0-3** layout móvil + `shrink-0`.
4. **Animaciones/Aprender:** acordeón o grid de tarjetas + búsqueda global.
5. **P0-4/P0-6** (401 → login, indicador de conexión, ErrorBoundary) + toasts de fin de render.
