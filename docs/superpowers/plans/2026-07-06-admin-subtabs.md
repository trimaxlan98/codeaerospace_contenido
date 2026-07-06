# Admin sub-pestañas Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reorganizar el panel Admin de ManimStudio (`studio/frontend/src/Admin.jsx`) en 3 sub-pestañas (Salud / Jobs / Recursos) y agrandar las gráficas históricas de CPU/RAM/Disco, resolviendo el amontonamiento visual actual descrito en `docs/superpowers/specs/2026-07-06-admin-subtabs-design.md`.

**Architecture:** `Admin.jsx` gana un `useState` de pestaña activa y una barra de tabs reutilizando el patrón CSS `.seg`/`.seg__opt` ya usado en `Assistant.jsx`/`Studio.jsx`. Las 5 secciones actuales (salud, historia, jobs, almacenamiento, contenedores) se reordenan sin cambiar su lógica interna, agrupadas en 3 bloques condicionales. `charts.jsx` sube la altura fija del SVG. No hay cambios de backend ni de props.

**Tech Stack:** React (JSX, sin TypeScript), CSS plano (`styles.css`), Vite.

## Global Constraints

- No tocar backend/API ni las props que `App.jsx` pasa a `<Admin>` (`metrics`, `containers`, `jobs`, `storage`, `onJobsChanged`).
- No hay suite de tests de frontend en este proyecto (`studio/frontend/package.json` solo tiene `dev`/`build`/`preview`) — la verificación es manual en navegador tras `vite build`.
- `vite build` escribe directamente `studio/frontend/dist/`, que nginx sirve en producción (coderesearch.space) — **no es un build aislado**. Pedir confirmación explícita al usuario antes de ejecutarlo (es el mismo paso que el deploy real).
- Seguir el patrón visual existente: usar las clases CSS ya definidas (`.panel`, `.panel__bar`, `.kpis`, `.meters`, `.charts`, `.tablewrap`, `.ctable`, `.seg`/`.seg__opt`) — no introducir un sistema de estilos nuevo.
- Commits sin acentos en el subject (convención del repo), un commit atómico por tarea.

---

### Task 1: Sub-pestañas en Admin.jsx + CSS de la barra de tabs

**Files:**
- Modify: `studio/frontend/src/Admin.jsx` (todo el archivo — reordena las 5 `<section className="panel">` en 3 bloques condicionales)
- Modify: `studio/frontend/src/styles.css:364` (agrega `.admin__tabs` cerca de `.admin__actions`)

**Interfaces:**
- Consumes: mismas props que hoy — `{ metrics, containers, jobs, storage, onJobsChanged }` (sin cambios de firma).
- Produces: estado interno `tab` (`'salud' | 'jobs' | 'recursos'`) — no se expone a otros componentes.

- [ ] **Step 1: Agregar el estado de pestaña y la barra de tabs**

En `studio/frontend/src/Admin.jsx`, dentro de `export default function Admin(...)`, junto al `const [notice, setNotice] = useState('')` existente (línea 72), agregar:

```jsx
  const [tab, setTab] = useState('salud')
```

Y en el JSX, inmediatamente después de `<main className="monitor admin">` (línea 97), agregar la barra de tabs:

```jsx
      <div className="seg admin__tabs" role="tablist" aria-label="secciones de administracion">
        {[
          { id: 'salud', label: 'Salud' },
          { id: 'jobs', label: 'Jobs' },
          { id: 'recursos', label: 'Recursos' },
        ].map((t) => (
          <button key={t.id} role="tab" aria-selected={tab === t.id}
            className={tab === t.id ? 'seg__opt seg__opt--on' : 'seg__opt'}
            onClick={() => setTab(t.id)}>{t.label}</button>
        ))}
      </div>
```

- [ ] **Step 2: Envolver las secciones "salud del sistema" e "historia" en el bloque `tab === 'salud'`**

Las dos `<section>` existentes (líneas 98-132 "salud del sistema" y 134-150 "historia") quedan igual por dentro, pero envueltas así:

```jsx
      {tab === 'salud' && (
        <>
          <section className="panel" aria-label="salud del sistema">
            {/* ...contenido existente sin cambios... */}
          </section>

          <section className="panel" aria-label="graficas historicas">
            {/* ...contenido existente sin cambios... */}
          </section>
        </>
      )}
```

- [ ] **Step 3: Envolver la sección "gestión de jobs" en el bloque `tab === 'jobs'`**

La `<section className="panel" aria-label="gestion de jobs">` existente (líneas 152-189) queda igual por dentro, envuelta así:

```jsx
      {tab === 'jobs' && (
        <section className="panel" aria-label="gestion de jobs">
          {/* ...contenido existente sin cambios... */}
        </section>
      )}
```

- [ ] **Step 4: Envolver "almacenamiento" y "contenedores" en el bloque `tab === 'recursos'`**

Las dos `<section>` existentes (líneas 191-200 "almacenamiento" y 202-237 "contenedores") quedan igual por dentro, envueltas así:

```jsx
      {tab === 'recursos' && (
        <>
          <section className="panel" aria-label="almacenamiento">
            {/* ...contenido existente sin cambios... */}
          </section>

          <section className="panel" aria-label="contenedores">
            {/* ...contenido existente sin cambios... */}
          </section>
        </>
      )}
```

- [ ] **Step 5: Agregar el CSS de la barra de tabs**

En `studio/frontend/src/styles.css`, justo antes de la línea `364: .admin__actions { ... }`, agregar:

```css
.admin__tabs { margin: 12px 12px 0; align-self: flex-start; }
```

- [ ] **Step 6: Commit**

```bash
git add studio/frontend/src/Admin.jsx studio/frontend/src/styles.css
git commit -m "$(cat <<'EOF'
feat: sub-pestanas Salud/Jobs/Recursos en panel Admin

Reorganiza Admin.jsx en 3 sub-pestanas para reducir el amontonamiento
visual de las 5 secciones que hoy se apilan en una sola columna scrolleable.
EOF
)"
```

---

### Task 2: Gráficas históricas más altas

**Files:**
- Modify: `studio/frontend/src/charts.jsx:8-10`

**Interfaces:**
- Consumes: nada nuevo — mismos parámetros de `Chart({ title, samples, field, color, now })` y `useHistory(metrics, containers)`.
- Produces: mismo componente `Chart`, solo con más alto en pantalla.

- [ ] **Step 1: Subir la altura fija del SVG**

En `studio/frontend/src/charts.jsx`, cambiar:

```js
const W = 600
const H = 130
const PAD = { l: 30, r: 6, t: 8, b: 16 }
```

por:

```js
const W = 600
const H = 220
const PAD = { l: 30, r: 6, t: 10, b: 18 }
```

(El `viewBox` de `<svg>` usa `W`/`H` directamente — línea 55 — así que no hace falta tocar más nada; al ser un SVG con `width: 100%; height: auto` vía CSS, escala manteniendo la proporción 600:220 en vez de 600:130.)

- [ ] **Step 2: Commit**

```bash
git add studio/frontend/src/charts.jsx
git commit -m "$(cat <<'EOF'
feat: graficas historicas mas altas en pestana Salud

Sube la altura del SVG de 130 a 220px ahora que las graficas ya no
comparten columna con jobs/almacenamiento/contenedores.
EOF
)"
```

---

### Task 3: Build y verificación visual manual

**Files:**
- No se modifican archivos de código — solo se genera `studio/frontend/dist/` (build) para verificar en navegador.

**Interfaces:**
- Consumes: el `Admin.jsx`/`charts.jsx`/`styles.css` de las Tasks 1-2.
- Produces: confirmación humana de que las 3 pestañas alternan y las gráficas de "Salud" se ven notablemente más grandes.

- [ ] **Step 1: Confirmar con el usuario antes de construir**

Este build escribe `studio/frontend/dist/`, que nginx sirve en producción — es el mismo paso que un deploy real. Preguntar explícitamente antes de ejecutar el Step 2 (no asumir aprobación previa del diseño como aprobación de deploy).

- [ ] **Step 2: Build de producción**

Run: `cd studio/frontend && node_modules/.bin/vite build`
Expected: build exitoso, termina con `✓ built in Xs` y sin errores.

- [ ] **Step 3: Verificar el asset servido**

Run: `curl -s https://coderesearch.space | grep -o 'index-[a-z0-9]*\.js'`
Expected: un nombre de chunk distinto al que había antes del build (confirma que nginx está sirviendo el build nuevo).

- [ ] **Step 4: Verificación manual en navegador**

Abrir `https://coderesearch.space`, iniciar sesión, ir a la vista Admin, y confirmar:
- La barra de tabs "Salud / Jobs / Recursos" aparece arriba y alterna contenido al hacer click.
- En "Salud": KPIs + barras + las 3 gráficas (CPU/RAM/Disco) se ven, y las gráficas son visiblemente más altas que antes.
- En "Jobs": la tabla de jobs y los botones de purga siguen funcionando igual que antes (no se movió lógica).
- En "Recursos": la barra de cuota de almacenamiento y la tabla de contenedores Docker aparecen juntas.

No hay Step 5 de commit — Task 3 es solo verificación, no genera cambios de código para commitear.
