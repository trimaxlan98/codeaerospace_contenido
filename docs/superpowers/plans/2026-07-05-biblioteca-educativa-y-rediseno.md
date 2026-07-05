# Biblioteca Educativa + Rediseño Visual — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Añadir a ManimStudio una biblioteca de ~60 lecciones educativas en Markdown (12 categorías), 7 temas de diseño, login con glassmorphism y ojito de contraseña, panel de administración con acciones en lote, y corregir errores de lógica detectados.

**Architecture:** Backend FastAPI (`studio/backend/app/`) gana `lessons.py` (lecciones Markdown+frontmatter servidas desde `studio/content/lessons/`, cache por mtime) y endpoints de borrado en lote en `main.py`/`jobs.py`. Frontend React+Vite (`studio/frontend/src/`) gana sistema de temas por variables CSS (`data-theme` en `<html>`), vista `Lessons.jsx` (marked+DOMPurify+KaTeX) y `Admin.jsx` que reemplaza a `Monitor.jsx`.

**Tech Stack:** FastAPI, PyYAML, pytest · React 18, Vite 5, marked, dompurify, katex · CSS variables (sin framework CSS).

## Global Constraints

- Todo el contenido y los textos de UI en **español** (código y commits siguen el estilo actual del repo: mensajes en español sin tildes en el subject).
- Backend: correr tests con `cd /var/www/codeaerospace_contenido/studio/backend && venv/bin/pytest -q`. Los 41 tests existentes deben seguir pasando en cada commit.
- Frontend: no hay test runner JS; verificar con `cd /var/www/codeaerospace_contenido/studio/frontend && npm run build` (debe terminar sin errores). No introducir framework de tests JS.
- Dependencias nuevas permitidas: `PyYAML>=6.0` (backend); `marked`, `dompurify`, `katex` (frontend). Ninguna otra.
- Variables CSS: conservar los nombres actuales (`--gold`, `--cyan`, `--void`, `--panel`, etc.). En temas nuevos, `--gold` = acento primario y `--cyan` = acento secundario aunque el color real no sea oro/cian.
- Rutas exactas: workspace `/var/www/codeaerospace_contenido`; contenido en `studio/content/lessons/`.
- Todo endpoint nuevo lleva `Depends(require_auth)`.
- Commits atómicos por tarea, terminados en:
  `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`

---

### Task 1: Poda del rate limiter de login (fuga de memoria lenta)

**Files:**
- Modify: `studio/backend/app/auth.py:26-64`
- Test: `studio/backend/tests/test_auth.py` (añadir al final)

**Interfaces:**
- Produces: `LoginRateLimiter._prune(now: float) -> None` (interno); sin cambios de API pública.

- [ ] **Step 1: Escribir el test que falla**

Añadir al final de `studio/backend/tests/test_auth.py`:

```python
def test_rate_limiter_poda_entradas_expiradas(monkeypatch):
    """Muchas IPs distintas no deben dejar residuos tras expirar su ventana."""
    from app.auth import LoginRateLimiter

    t = [1000.0]
    monkeypatch.setattr("app.auth.time.time", lambda: t[0])

    rl = LoginRateLimiter(max_failures=5, lockout_seconds=60)
    for i in range(200):
        rl.record_failure(f"10.0.{i // 250}.{i % 250}")
    assert len(rl._failures) > 100  # 200 ips + global

    t[0] = 1000.0 + 61  # ventana y bloqueos expirados
    rl.check("10.9.9.9")  # cualquier consulta dispara la poda
    assert rl._failures == {}
    assert rl._locked_until == {}
```

- [ ] **Step 2: Verificar que falla**

Run: `cd /var/www/codeaerospace_contenido/studio/backend && venv/bin/pytest tests/test_auth.py::test_rate_limiter_poda_entradas_expiradas -q`
Expected: FAIL (`assert {...} == {}` — las entradas siguen ahí).

- [ ] **Step 3: Implementar la poda**

En `studio/backend/app/auth.py`, dentro de `LoginRateLimiter`, añadir método y llamarlo desde `check` y `record_failure`:

```python
    def _prune(self, now: float) -> None:
        """Elimina fallos fuera de ventana y bloqueos vencidos.

        Sin poda, el dict crece una entrada por IP atacante para siempre
        (fuga de memoria lenta en un proceso de larga vida).
        """
        window = self.lockout_seconds
        self._failures = {
            k: kept for k, ts in self._failures.items()
            if (kept := [x for x in ts if now - x < window])
        }
        self._locked_until = {k: u for k, u in self._locked_until.items() if u > now}
```

En `check`, como primera línea tras `now = time.time()`: `self._prune(now)`.
En `record_failure`, como primera línea tras `now = time.time()`: `self._prune(now)`.

- [ ] **Step 4: Verificar que pasa todo**

Run: `venv/bin/pytest -q`
Expected: 42 passed.

- [ ] **Step 5: Commit**

```bash
git add studio/backend/app/auth.py studio/backend/tests/test_auth.py
git commit -m "fix: podar entradas expiradas del rate limiter de login"
```

---

### Task 2: Correcciones de lógica en el frontend

**Files:**
- Modify: `studio/frontend/src/Login.jsx:18-19`
- Modify: `studio/frontend/src/App.jsx:26-39,75,86-88`
- Modify: `studio/frontend/src/Library.jsx:8-12`

**Interfaces:**
- Produces: `App.jsx` expone internamente `refreshMe()`; `Login` recibe `onLogin` que ahora es `refreshMe` (misma prop, nueva semántica: re-consulta `/api/me` y fija `auth` y `aiEnabled` de una vez).

- [ ] **Step 1: Login — distinguir error de red / 401 / 429 / otros**

En `Login.jsx`, reemplazar el bloque `catch`:

```jsx
    } catch (err) {
      if (!err.status) setError('No se pudo conectar con el servidor')
      else if (err.status === 429) setError(err.message)
      else if (err.status === 401) setError('Credenciales inválidas')
      else setError(`Error del servidor (${err.status})`)
    } finally {
```

- [ ] **Step 2: App — eliminar la dependencia `[auth === true]`**

En `App.jsx`, reemplazar el efecto de las líneas 34-39 por un callback reutilizable (colocarlo junto a `refreshJobs`):

```jsx
  // Consulta /api/me: fija sesion y flag de IA en una sola pasada.
  const refreshMe = useCallback(async () => {
    try {
      const d = await api.me()
      setAuth(d.authenticated)
      setAiEnabled(Boolean(d.ai_enabled))
    } catch {
      setAuth(false)
    }
  }, [])

  useEffect(() => { refreshMe() }, [refreshMe]) // consulta inicial al montar
```

Y cambiar la línea 75:

```jsx
    return <Login onLogin={refreshMe} />
```

El `logout` (líneas 86-88) queda igual: `setAuth(false)` sin re-consulta.

- [ ] **Step 3: Library — escala KB en `fmtSize`**

En `Library.jsx`, reemplazar `fmtSize`:

```jsx
function fmtSize(bytes) {
  if (bytes == null) return '—'
  if (bytes >= 1024 * MB) return `${(bytes / (1024 * MB)).toFixed(2)} GB`
  if (bytes >= MB) return `${(bytes / MB).toFixed(1)} MB`
  return `${Math.max(1, Math.round(bytes / 1024))} KB`
}
```

- [ ] **Step 4: Verificar build**

Run: `cd /var/www/codeaerospace_contenido/studio/frontend && npm run build`
Expected: build exitoso sin warnings nuevos.

- [ ] **Step 5: Commit**

```bash
git add studio/frontend/src/Login.jsx studio/frontend/src/App.jsx studio/frontend/src/Library.jsx
git commit -m "fix: errores de logica en frontend (mensaje de red en login, efecto /api/me, fmtSize KB)"
```

---

### Task 3: Sistema de 7 temas

**Files:**
- Create: `studio/frontend/src/themes.js`
- Create: `studio/frontend/src/ThemePicker.jsx`
- Modify: `studio/frontend/index.html` (script anti-flash)
- Modify: `studio/frontend/src/styles.css` (bloques `data-theme` + variables nuevas)
- Modify: `studio/frontend/src/Header.jsx` (montar el picker)

**Interfaces:**
- Produces: `themes.js` exporta `THEMES` (array `{id, name, swatch: [bg, acc1, acc2]}`), `currentTheme(): string`, `applyTheme(id: string): void`. `ThemePicker.jsx` exporta default `ThemePicker` (sin props). Clave de localStorage: `ms_theme`. Variables CSS nuevas por tema: `--grad-a`, `--grad-b`, `--grad-c` (fondo del login), `--star-1`, `--star-2` (campo de estrellas del body).

- [ ] **Step 1: Crear `themes.js`**

```js
// Temas: conjuntos de variables CSS aplicados via data-theme en <html>.
// El id 'orbital' es el tema por defecto (los valores de :root).

export const THEMES = [
  { id: 'orbital', name: 'Orbital', swatch: ['#070b12', '#e8b84b', '#6fc3df'] },
  { id: 'aurora', name: 'Aurora', swatch: ['#06120f', '#5ee6a8', '#9d7bff'] },
  { id: 'deepspace', name: 'Deep Space', swatch: ['#000000', '#ff5fa2', '#7f7cff'] },
  { id: 'daylight', name: 'Daylight', swatch: ['#f4f1ea', '#a3742c', '#2b7a9e'] },
  { id: 'nebula', name: 'Nebula', swatch: ['#0d0716', '#b388ff', '#ff8fd4'] },
  { id: 'ion', name: 'Ion', swatch: ['#04121c', '#2fd4ff', '#45e0c0'] },
  { id: 'solar', name: 'Solar', swatch: ['#120c06', '#ffb347', '#ff7847'] },
]

export function currentTheme() {
  const saved = localStorage.getItem('ms_theme')
  return THEMES.some((t) => t.id === saved) ? saved : 'orbital'
}

export function applyTheme(id) {
  document.documentElement.dataset.theme = id
  localStorage.setItem('ms_theme', id)
}
```

- [ ] **Step 2: Script anti-flash en `index.html`**

Añadir dentro de `<head>`, antes de cualquier CSS/JS:

```html
    <script>
      (function () {
        try {
          var t = localStorage.getItem('ms_theme')
          var valid = ['orbital','aurora','deepspace','daylight','nebula','ion','solar']
          document.documentElement.dataset.theme =
            valid.indexOf(t) >= 0 ? t : 'orbital'
        } catch (e) { document.documentElement.dataset.theme = 'orbital' }
      })()
    </script>
```

- [ ] **Step 3: Variables por tema en `styles.css`**

(a) En el `:root` existente, AÑADIR las variables nuevas (tema Orbital):

```css
  --grad-a: #0a1220;
  --grad-b: #101c33;
  --grad-c: #17263f;
  --star-1: #2c4266;
  --star-2: #223753;
```

(b) Tras el bloque `:root`, añadir los 6 temas restantes:

```css
:root[data-theme="aurora"] {
  --void: #06120f; --panel: #0b1b17; --panel-2: #0e211c; --line: #1b3a31;
  --ink: #d8f0e6; --muted: #6f9c8d; --gold: #5ee6a8; --cyan: #9d7bff;
  --ok: #63c98a; --err: #e86a6a; --warn: #e8b84b;
  --grad-a: #071612; --grad-b: #0c2b1f; --grad-c: #16223a;
  --star-1: #2b5c48; --star-2: #23414a;
}
:root[data-theme="deepspace"] {
  --void: #000000; --panel: #0a0a0f; --panel-2: #101018; --line: #23232f;
  --ink: #e8e6f0; --muted: #77748c; --gold: #ff5fa2; --cyan: #7f7cff;
  --ok: #58c88a; --err: #ff6a6a; --warn: #e8a04b;
  --grad-a: #000000; --grad-b: #0d0716; --grad-c: #160b22;
  --star-1: #3a3a55; --star-2: #2a2a40;
}
:root[data-theme="daylight"] {
  --void: #f4f1ea; --panel: #ffffff; --panel-2: #f7f4ee; --line: #ddd6c8;
  --ink: #2b2a26; --muted: #8a8577; --gold: #a3742c; --cyan: #2b7a9e;
  --ok: #2f9e60; --err: #c04545; --warn: #c07f2f;
  --grad-a: #f2ede2; --grad-b: #e8eef2; --grad-c: #f6f0e4;
  --star-1: transparent; --star-2: transparent;
}
:root[data-theme="nebula"] {
  --void: #0d0716; --panel: #150d24; --panel-2: #1a1130; --line: #2e2050;
  --ink: #e6dcf5; --muted: #8d7fae; --gold: #b388ff; --cyan: #ff8fd4;
  --ok: #63c98a; --err: #e86a6a; --warn: #e8b84b;
  --grad-a: #0e0819; --grad-b: #1d1033; --grad-c: #241243;
  --star-1: #4a3a70; --star-2: #382a58;
}
:root[data-theme="ion"] {
  --void: #04121c; --panel: #082030; --panel-2: #0a2839; --line: #14405a;
  --ink: #d6ecf7; --muted: #6d94a8; --gold: #2fd4ff; --cyan: #45e0c0;
  --ok: #45e0a0; --err: #ff7a7a; --warn: #ffc86b;
  --grad-a: #051624; --grad-b: #082b40; --grad-c: #0b3550;
  --star-1: #1e4e6e; --star-2: #17405c;
}
:root[data-theme="solar"] {
  --void: #120c06; --panel: #1c1408; --panel-2: #241a0b; --line: #3a2d15;
  --ink: #f0e6d4; --muted: #9c8a67; --gold: #ffb347; --cyan: #ff7847;
  --ok: #8fc963; --err: #e86a6a; --warn: #ffd36b;
  --grad-a: #150e07; --grad-b: #2a1c0c; --grad-c: #331f0e;
  --star-1: #55401f; --star-2: #453318;
}
```

(c) En `body`, reemplazar los colores fijos del campo de estrellas por
`var(--star-1)` / `var(--star-2)` (los 5 `radial-gradient` existentes: los dos
primeros con `--star-1`, los tres restantes con `--star-2`), y añadir
`transition: background-color .25s ease, color .25s ease;`.

(d) Añadir CSS del picker (al final de la sección header):

```css
.themepicker { position: relative; }
.themepicker__btn {
  display: flex; align-items: center; gap: 6px;
  background: none; border: 1px solid var(--line); border-radius: 3px;
  color: var(--muted); font: inherit; font-size: 12px;
  padding: 4px 10px; cursor: pointer;
}
.themepicker__btn:hover { color: var(--ink); }
.themepicker__menu {
  position: absolute; right: 0; top: calc(100% + 6px); z-index: 50;
  min-width: 170px; padding: 4px;
  background: var(--panel); border: 1px solid var(--line); border-radius: 6px;
  box-shadow: 0 12px 30px rgba(0, 0, 0, .35);
}
.themepicker__item {
  display: flex; align-items: center; gap: 8px; width: 100%;
  background: none; border: 0; border-radius: 4px; color: var(--ink);
  font: inherit; font-size: 13px; padding: 7px 9px; cursor: pointer;
  text-align: left;
}
.themepicker__item:hover { background: var(--panel-2); }
.themepicker__item--on { color: var(--gold); }
.themepicker__dots { display: flex; gap: 3px; }
.themepicker__dot {
  width: 10px; height: 10px; border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, .18);
}
```

- [ ] **Step 4: Crear `ThemePicker.jsx`**

```jsx
// Selector de tema: dropdown con muestra de paleta. Persiste en localStorage.

import { useEffect, useRef, useState } from 'react'
import { THEMES, applyTheme, currentTheme } from './themes.js'

export default function ThemePicker() {
  const [open, setOpen] = useState(false)
  const [theme, setTheme] = useState(currentTheme)
  const ref = useRef(null)

  useEffect(() => {
    if (!open) return
    const close = (e) => { if (!ref.current?.contains(e.target)) setOpen(false) }
    const esc = (e) => { if (e.key === 'Escape') setOpen(false) }
    document.addEventListener('mousedown', close)
    document.addEventListener('keydown', esc)
    return () => {
      document.removeEventListener('mousedown', close)
      document.removeEventListener('keydown', esc)
    }
  }, [open])

  const pick = (id) => {
    applyTheme(id)
    setTheme(id)
    setOpen(false)
  }

  const active = THEMES.find((t) => t.id === theme)
  return (
    <div className="themepicker" ref={ref}>
      <button className="themepicker__btn" onClick={() => setOpen(!open)}
        aria-haspopup="listbox" aria-expanded={open} title="Tema de la interfaz">
        <span className="themepicker__dots" aria-hidden="true">
          {active.swatch.map((c) => (
            <span key={c} className="themepicker__dot" style={{ background: c }} />
          ))}
        </span>
        {active.name}
      </button>
      {open && (
        <div className="themepicker__menu" role="listbox" aria-label="temas">
          {THEMES.map((t) => (
            <button key={t.id} role="option" aria-selected={t.id === theme}
              className={`themepicker__item${t.id === theme ? ' themepicker__item--on' : ''}`}
              onClick={() => pick(t.id)}>
              <span className="themepicker__dots" aria-hidden="true">
                {t.swatch.map((c) => (
                  <span key={c} className="themepicker__dot" style={{ background: c }} />
                ))}
              </span>
              {t.name}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 5: Montar en `Header.jsx`**

Importar `ThemePicker` y añadirlo en `.hdr__telemetry`, antes del botón de logout:

```jsx
import ThemePicker from './ThemePicker.jsx'
// ...dentro de hdr__telemetry, antes de "Cerrar sesión":
        <ThemePicker />
```

- [ ] **Step 6: Verificar build y revisión manual**

Run: `npm run build` → exitoso. Revisar manualmente: cambiar de tema recorre las vistas sin colores rotos; recargar conserva el tema sin flash; Daylight mantiene contraste legible en charts, chips y tablas.

- [ ] **Step 7: Commit**

```bash
git add studio/frontend/index.html studio/frontend/src/themes.js studio/frontend/src/ThemePicker.jsx studio/frontend/src/Header.jsx studio/frontend/src/styles.css
git commit -m "feat: sistema de 7 temas con selector y persistencia sin flash"
```

---

### Task 4: Login glassmorphism + ojito de contraseña

**Files:**
- Modify: `studio/frontend/src/Login.jsx` (reescritura del cuerpo del form)
- Modify: `studio/frontend/src/styles.css` (sección `.login`)

**Interfaces:**
- Consumes: variables `--grad-a/b/c` del tema (Task 3); manejo de errores de Task 2 (se conserva tal cual).

- [ ] **Step 1: Reescribir `Login.jsx`**

```jsx
import { useState } from 'react'
import { api } from './api.js'
import { OrbitGlyph } from './Header.jsx'

function EyeIcon({ off }) {
  return off ? (
    <svg viewBox="0 0 24 24" width="18" height="18" fill="none"
      stroke="currentColor" strokeWidth="1.7" aria-hidden="true">
      <path d="M3 3l18 18M10.6 10.7a2.8 2.8 0 0 0 3.9 4M6.6 6.8C4.6 8 3 9.8 2 12c1.8 3.9 5.5 6.5 10 6.5 1.9 0 3.7-.5 5.2-1.3M9.9 5.8A10.8 10.8 0 0 1 12 5.5c4.5 0 8.2 2.6 10 6.5a13 13 0 0 1-2.6 3.6" />
    </svg>
  ) : (
    <svg viewBox="0 0 24 24" width="18" height="18" fill="none"
      stroke="currentColor" strokeWidth="1.7" aria-hidden="true">
      <path d="M2 12c1.8-3.9 5.5-6.5 10-6.5S20.2 8.1 22 12c-1.8 3.9-5.5 6.5-10 6.5S3.8 15.9 2 12z" />
      <circle cx="12" cy="12" r="2.8" />
    </svg>
  )
}

export default function Login({ onLogin }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPass, setShowPass] = useState(false)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      await api.login(username, password)
      onLogin()
    } catch (err) {
      if (!err.status) setError('No se pudo conectar con el servidor')
      else if (err.status === 429) setError(err.message)
      else if (err.status === 401) setError('Credenciales inválidas')
      else setError(`Error del servidor (${err.status})`)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="login">
      <div className="login__sky" aria-hidden="true" />
      <form className={`login__card${error ? ' login__card--shake' : ''}`}
        onSubmit={submit}>
        <div className="login__brand">
          <OrbitGlyph state="idle" />
          <h1 className="login__mark">MANIM·STUDIO</h1>
          <p className="login__sub">Consola privada de renderizado · coderesearch.space</p>
        </div>
        <label className="field">
          <span>Usuario</span>
          <input value={username} onChange={(e) => setUsername(e.target.value)}
            autoComplete="username" autoFocus required />
        </label>
        <label className="field field--pass">
          <span>Contraseña</span>
          <div className="field__wrap">
            <input type={showPass ? 'text' : 'password'} value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password" required />
            <button type="button" className="field__eye"
              onClick={() => setShowPass(!showPass)}
              aria-pressed={showPass}
              aria-label={showPass ? 'Ocultar contraseña' : 'Mostrar contraseña'}>
              <EyeIcon off={showPass} />
            </button>
          </div>
        </label>
        {error && <p className="login__error" role="alert">{error}</p>}
        <button className="btn btn--primary" disabled={busy}>
          {busy ? 'Verificando…' : 'Entrar'}
        </button>
      </form>
    </div>
  )
}
```

- [ ] **Step 2: CSS del login**

Reemplazar la sección `.login` existente en `styles.css` por:

```css
.login {
  position: relative; display: grid; place-items: center;
  height: 100%; overflow: hidden; padding: 20px;
}

/* Fondo tranquilo: gradiente que deriva lentamente, por tema. */
.login__sky {
  position: absolute; inset: -20%;
  background: linear-gradient(135deg,
    var(--grad-a) 0%, var(--grad-b) 45%, var(--grad-c) 75%, var(--grad-a) 100%);
  background-size: 300% 300%;
  animation: skydrift 40s ease-in-out infinite;
}
@keyframes skydrift {
  0%, 100% { background-position: 0% 0%; }
  50% { background-position: 100% 100%; }
}
@media (prefers-reduced-motion: reduce) {
  .login__sky { animation: none; }
}

.login__card {
  position: relative; z-index: 1;
  width: min(380px, 100%);
  display: flex; flex-direction: column; gap: 16px;
  padding: 34px 30px 30px;
  border-radius: 14px;
  background: color-mix(in srgb, var(--panel) 55%, transparent);
  backdrop-filter: blur(18px) saturate(1.15);
  -webkit-backdrop-filter: blur(18px) saturate(1.15);
  border: 1px solid color-mix(in srgb, var(--ink) 14%, transparent);
  box-shadow:
    0 22px 60px rgba(0, 0, 0, .38),
    inset 0 1px 0 color-mix(in srgb, var(--ink) 10%, transparent);
  animation: cardin .45s cubic-bezier(.2, .8, .25, 1);
}
@keyframes cardin {
  from { opacity: 0; transform: translateY(14px) scale(.985); }
  to { opacity: 1; transform: none; }
}
.login__card--shake { animation: shake .3s ease; }
@keyframes shake {
  25% { transform: translateX(-5px); }
  50% { transform: translateX(4px); }
  75% { transform: translateX(-2px); }
}

.login__brand { text-align: center; display: grid; justify-items: center; gap: 6px; }
.login__sub { color: var(--muted); font-size: 12px; }
.login__error { color: var(--err); font-size: 13px; text-align: center; }

.field--pass .field__wrap { position: relative; }
.field--pass input { width: 100%; padding-right: 40px; }
.field__eye {
  position: absolute; right: 6px; top: 50%; transform: translateY(-50%);
  display: grid; place-items: center;
  background: none; border: 0; padding: 6px; cursor: pointer;
  color: var(--muted); border-radius: 4px;
}
.field__eye:hover, .field__eye:focus-visible { color: var(--ink); }
```

Nota: conservar las reglas existentes de `.field` (inputs) y `.login__mark`; solo se reemplaza/añade lo listado.

- [ ] **Step 3: Verificar build y revisión manual**

Run: `npm run build` → exitoso. Manual: ojito alterna visibilidad y anuncia `aria-label` correcto; el card se ve translúcido sobre el gradiente en los 7 temas; con `prefers-reduced-motion` el fondo queda estático.

- [ ] **Step 4: Commit**

```bash
git add studio/frontend/src/Login.jsx studio/frontend/src/styles.css
git commit -m "feat: login con glassmorphism, fondo animado por tema y ojito de contrasena"
```

---

### Task 5: Endpoints de borrado en lote (backend)

**Files:**
- Modify: `studio/backend/app/jobs.py` (métodos nuevos en `JobManager`)
- Modify: `studio/backend/app/main.py` (2 rutas nuevas ANTES de `delete_job`)
- Test: `studio/backend/tests/test_jobs_api.py` (añadir al final)

**Interfaces:**
- Produces: `JobManager.delete_failed_jobs() -> int`; `JobManager.delete_jobs_older_than(days: int) -> tuple[int, int]` (conteo, bytes liberados). Rutas: `DELETE /api/jobs/failed` → `{"deleted": int, "storage": {...}}`; `DELETE /api/jobs/older-than/{days}` → `{"deleted": int, "freed_bytes": int, "storage": {...}}`.
- **CRÍTICO:** las rutas nuevas deben declararse en `main.py` ANTES de `@app.delete("/api/jobs/{job_id}")`, o `"failed"` será capturado como `job_id` y devolverá 404.

- [ ] **Step 1: Escribir los tests que fallan**

Añadir al final de `studio/backend/tests/test_jobs_api.py`:

```python
import time as _time
import uuid as _uuid


def _seed_job(status, finished_ago_s=0, size=0):
    """Inserta un job directamente en la BD de la app cargada."""
    import app.main as main
    job_id = _uuid.uuid4().hex[:16]
    now = _time.time()
    main.db.insert_job({
        "id": job_id, "scene": "Escena", "quality": "ql", "timeout": 120,
        "status": "queued", "script": "class Escena: pass", "created_at": now,
    })
    main.db.update_job(job_id, status=status,
                       finished_at=now - finished_ago_s, size_bytes=size)
    return job_id


def test_delete_failed_borra_solo_fallidos(authed):
    fallido = _seed_job("error")
    cancelado = _seed_job("cancelled")
    bueno = _seed_job("done")
    r = authed.delete("/api/jobs/failed")
    assert r.status_code == 200
    assert r.json()["deleted"] == 2
    ids = {j["id"] for j in authed.get("/api/jobs").json()["jobs"]}
    assert bueno in ids and fallido not in ids and cancelado not in ids


def test_purga_por_antiguedad_no_toca_recientes_ni_activos(authed):
    viejo = _seed_job("done", finished_ago_s=40 * 86400, size=1000)
    reciente = _seed_job("done", finished_ago_s=1 * 86400, size=500)
    r = authed.delete("/api/jobs/older-than/30")
    assert r.status_code == 200
    body = r.json()
    assert body["deleted"] == 1
    assert body["freed_bytes"] == 1000
    ids = {j["id"] for j in authed.get("/api/jobs").json()["jobs"]}
    assert reciente in ids and viejo not in ids


def test_purga_valida_rango_de_dias(authed):
    assert authed.delete("/api/jobs/older-than/0").status_code == 422


def test_bulk_requiere_auth(client):
    assert client.delete("/api/jobs/failed").status_code == 401
    assert client.delete("/api/jobs/older-than/30").status_code == 401
```

- [ ] **Step 2: Verificar que fallan**

Run: `venv/bin/pytest tests/test_jobs_api.py -q`
Expected: los 4 tests nuevos FAIL (404/405 en las rutas inexistentes).

- [ ] **Step 3: Métodos en `JobManager`** (`jobs.py`, sección "mantenimiento")

```python
    FAILED_STATES = ("error", "timeout", "cancelled")

    def delete_failed_jobs(self) -> int:
        """Borra todos los jobs fallidos/cancelados. Devuelve el conteo."""
        count = 0
        for job in self.db.list_jobs(limit=100_000):
            if job["status"] in self.FAILED_STATES and self.delete_job(job["id"]):
                count += 1
        return count

    def delete_jobs_older_than(self, days: int) -> tuple[int, int]:
        """Borra jobs 'done' terminados hace mas de `days` dias.

        Devuelve (conteo, bytes liberados segun size_bytes registrado).
        """
        cutoff = time.time() - days * 86400
        count = freed = 0
        for job in self.db.list_jobs(limit=100_000):
            if job["status"] == "done" and (job.get("finished_at") or 0) < cutoff:
                size = job.get("size_bytes") or 0
                if self.delete_job(job["id"]):
                    count += 1
                    freed += size
        return count, freed
```

(`FAILED_STATES` va como atributo de clase, junto a la definición de `JobManager`; `delete_job` ya ignora jobs activos, defensa extra.)

- [ ] **Step 4: Rutas en `main.py`** — insertar INMEDIATAMENTE ANTES de `@app.delete("/api/jobs/{job_id}")`:

```python
@app.delete("/api/jobs/failed")
async def delete_failed_jobs(_=Depends(require_auth)):
    """Borra en lote todos los jobs error/timeout/cancelled."""
    deleted = manager.delete_failed_jobs()
    return {"deleted": deleted, "storage": _storage_public()}


@app.delete("/api/jobs/older-than/{days}")
async def delete_old_jobs(days: int, _=Depends(require_auth)):
    """Purga jobs 'done' con mas de `days` dias de antiguedad."""
    if not (1 <= days <= 3650):
        raise HTTPException(status_code=422, detail="Dias fuera de rango (1-3650)")
    deleted, freed = manager.delete_jobs_older_than(days)
    return {"deleted": deleted, "freed_bytes": freed, "storage": _storage_public()}
```

- [ ] **Step 5: Verificar que pasa todo**

Run: `venv/bin/pytest -q`
Expected: 46 passed.

- [ ] **Step 6: Commit**

```bash
git add studio/backend/app/jobs.py studio/backend/app/main.py studio/backend/tests/test_jobs_api.py
git commit -m "feat: borrado en lote de jobs fallidos y purga por antiguedad"
```

---

### Task 6: Panel de administración (frontend)

**Files:**
- Create: `studio/frontend/src/charts.jsx` (mover `Chart`, `useHistory`, `renderBands`, `scaleX`, `scaleY` desde `Monitor.jsx`)
- Create: `studio/frontend/src/Admin.jsx` (reemplaza a `Monitor.jsx`)
- Delete: `studio/frontend/src/Monitor.jsx`
- Modify: `studio/frontend/src/api.js`, `studio/frontend/src/App.jsx`, `studio/frontend/src/Header.jsx`, `studio/frontend/src/styles.css`

**Interfaces:**
- Consumes: `api.deleteFailedJobs()` y `api.purgeJobsOlderThan(days)` (añadidos aquí, llaman a los endpoints de Task 5); props actuales de Monitor (`metrics`, `containers`) + `jobs`, `storage`, `onJobsChanged` (ya disponibles en `App.jsx`).
- Produces: `charts.jsx` exporta `Chart` (props `{title, samples, field, color, now}`) y `useHistory(metrics, containers)`. `Admin.jsx` exporta default `Admin({ metrics, containers, jobs, storage, onJobsChanged })`. La vista pasa de `'monitor'` a `'admin'`; pestaña del header: «Admin».

- [ ] **Step 1: `api.js` — métodos nuevos**

```js
  deleteFailedJobs: () => request('DELETE', '/api/jobs/failed'),
  purgeJobsOlderThan: (days) => request('DELETE', `/api/jobs/older-than/${days}`),
```

- [ ] **Step 2: Crear `charts.jsx`**

Mover TAL CUAL desde `Monitor.jsx`: constantes `GB, WINDOW_S, W, H, PAD`, funciones `scaleX, scaleY, renderBands`, componente `Chart` y hook `useHistory`. Exportar `Chart` y `useHistory` (nombrados) y también `GB`.

- [ ] **Step 3: Crear `Admin.jsx`**

```jsx
// Panel de administracion: salud del host, contenedores, gestion de jobs y disco.

import { useState } from 'react'
import { api } from './api.js'
import { Chart, useHistory, GB } from './charts.jsx'

const MB = 1024 ** 2

function fmtGB(bytes) { return `${(bytes / GB).toFixed(1)} G` }

function fmtSize(bytes) {
  if (bytes == null) return '—'
  if (bytes >= 1024 * MB) return `${(bytes / (1024 * MB)).toFixed(2)} GB`
  if (bytes >= MB) return `${(bytes / MB).toFixed(1)} MB`
  return `${Math.max(1, Math.round(bytes / 1024))} KB`
}

function fmtDate(ts) {
  if (!ts) return '—'
  return new Date(ts * 1000).toLocaleString('es', {
    day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit', hour12: false,
  })
}

function Kpi({ label, value, unit, level }) {
  return (
    <div className={`kpi${level ? ` kpi--${level}` : ''}`}>
      <span className="kpi__label">{label}</span>
      <span className="kpi__value">{value}<small>{unit}</small></span>
    </div>
  )
}

function ArmedButton({ label, confirmLabel, onFire, danger }) {
  const [arming, setArming] = useState(false)
  if (arming) {
    return (
      <span className="armed">
        <button className="btn btn--tiny btn--danger"
          onClick={() => { setArming(false); onFire() }}>{confirmLabel}</button>
        <button className="btn btn--tiny" onClick={() => setArming(false)}>No</button>
      </span>
    )
  }
  return (
    <button className={`btn btn--tiny${danger ? ' btn--danger' : ''}`}
      onClick={() => setArming(true)}>{label}</button>
  )
}

function Bar({ label, pct, detail, warnAt = 80 }) {
  const level = pct >= 92 ? 'crit' : pct >= warnAt ? 'warn' : 'ok'
  return (
    <div className="meter">
      <div className="meter__head">
        <span className="meter__label">{label}</span>
        <span className="meter__val">{pct.toFixed(1)}%</span>
      </div>
      <div className="meter__track" role="progressbar" aria-valuenow={Math.round(pct)}
        aria-valuemin="0" aria-valuemax="100" aria-label={label}>
        <div className={`meter__fill meter__fill--${level}`}
          style={{ width: `${Math.min(pct, 100)}%` }} />
      </div>
      <span className="meter__detail">{detail}</span>
    </div>
  )
}

export default function Admin({ metrics, containers, jobs, storage, onJobsChanged }) {
  const samples = useHistory(metrics, containers)
  const now = metrics?.ts || Date.now() / 1000
  const [notice, setNotice] = useState('')

  const done = jobs.filter((j) => j.status === 'done')
  const failed = jobs.filter((j) => ['error', 'timeout', 'cancelled'].includes(j.status))
  const active = jobs.filter((j) => ['queued', 'running'].includes(j.status))
  const storagePct = storage?.quota_bytes
    ? (storage.used_bytes / storage.quota_bytes) * 100 : 0

  const run = async (fn, msg) => {
    setNotice('')
    try {
      const r = await fn()
      setNotice(msg(r))
      onJobsChanged()
    } catch (err) {
      setNotice(`Error: ${err.message}`)
    }
  }

  const clearFailed = () => run(api.deleteFailedJobs,
    (r) => `${r.deleted} job(s) fallidos eliminados.`)
  const purge = (days) => run(() => api.purgeJobsOlderThan(days),
    (r) => `${r.deleted} render(s) purgados · ${fmtSize(r.freed_bytes)} liberados.`)

  return (
    <main className="monitor admin">
      <section className="panel" aria-label="salud del sistema">
        <div className="panel__bar">
          <span className="panel__title">SALUD DEL SISTEMA</span>
          {metrics && (
            <span className="panel__aside">
              load {metrics.load.join(' / ')} · {metrics.cpu_count} vCPU
            </span>
          )}
        </div>
        {!metrics ? <p className="empty">Esperando telemetría…</p> : (
          <>
            <div className="kpis">
              <Kpi label="CPU" value={metrics.cpu_pct.toFixed(0)} unit="%"
                level={metrics.cpu_pct >= 90 ? 'crit' : metrics.cpu_pct >= 75 ? 'warn' : 'ok'} />
              <Kpi label="RAM" value={metrics.mem.pct.toFixed(0)} unit="%"
                level={metrics.mem.pct >= 92 ? 'crit' : metrics.mem.pct >= 80 ? 'warn' : 'ok'} />
              <Kpi label="DISCO /" value={metrics.disk.pct.toFixed(0)} unit="%"
                level={metrics.disk.pct >= 92 ? 'crit' : metrics.disk.pct >= 80 ? 'warn' : 'ok'} />
              <Kpi label="RENDERS" value={String(done.length)} unit=" ok" level="ok" />
              <Kpi label="ACTIVOS" value={String(active.length)} unit=""
                level={active.length ? 'warn' : 'ok'} />
            </div>
            <div className="meters">
              <Bar label="CPU" pct={metrics.cpu_pct} warnAt={75}
                detail={`${metrics.cpu_count} vCPU compartidas con producción`} />
              <Bar label="RAM" pct={metrics.mem.pct}
                detail={`${fmtGB(metrics.mem.used)} / ${fmtGB(metrics.mem.total)} · disp ${fmtGB(metrics.mem.available)}`} />
              <Bar label="SWAP" pct={metrics.swap.pct} warnAt={40}
                detail={`${fmtGB(metrics.swap.used)} / ${fmtGB(metrics.swap.total)}`} />
              <Bar label="DISCO /" pct={metrics.disk.pct}
                detail={`${fmtGB(metrics.disk.used)} / ${fmtGB(metrics.disk.total)} · libres ${fmtGB(metrics.disk.free)}`} />
            </div>
          </>
        )}
      </section>

      <section className="panel" aria-label="graficas historicas">
        <div className="panel__bar">
          <span className="panel__title">HISTORIA · ÚLTIMOS 30 MIN</span>
          <span className="panel__aside">
            <span className="chart__legendband" aria-hidden="true" /> render activo
          </span>
        </div>
        {samples.length < 2 ? (
          <p className="empty">Acumulando historia… (una muestra cada pocos segundos)</p>
        ) : (
          <div className="charts">
            <Chart title="CPU" field="cpu" color="var(--cyan)" samples={samples} now={now} />
            <Chart title="RAM" field="mem" color="var(--gold)" samples={samples} now={now} />
            <Chart title="DISCO /" field="disk" color="var(--ok)" samples={samples} now={now} />
          </div>
        )}
      </section>

      <section className="panel" aria-label="gestion de jobs">
        <div className="panel__bar">
          <span className="panel__title">GESTIÓN DE JOBS</span>
          <span className="panel__aside">
            {done.length} ok · {failed.length} fallidos · {active.length} activos
          </span>
        </div>
        <div className="admin__actions">
          <ArmedButton danger label={`Eliminar fallidos (${failed.length})`}
            confirmLabel="¿Confirmar?" onFire={clearFailed} />
          <ArmedButton danger label="Purgar renders > 30 días"
            confirmLabel="¿Confirmar purga?" onFire={() => purge(30)} />
          <ArmedButton danger label="Purgar renders > 7 días"
            confirmLabel="¿Confirmar purga?" onFire={() => purge(7)} />
        </div>
        {notice && <p className="notice" role="status">{notice}</p>}
        <div className="tablewrap">
          <table className="ctable">
            <thead>
              <tr><th>Escena</th><th>Estado</th><th>Creado</th><th>Duración</th><th>Tamaño</th></tr>
            </thead>
            <tbody>
              {jobs.slice(0, 25).map((j) => (
                <tr key={j.id}>
                  <td className="mono">{j.scene}</td>
                  <td><span className={`state state--${j.status}`}>{j.status}</span></td>
                  <td>{fmtDate(j.created_at)}</td>
                  <td className="num">
                    {j.started_at && j.finished_at
                      ? `${(j.finished_at - j.started_at).toFixed(0)}s` : '—'}
                  </td>
                  <td className="mono num">{fmtSize(j.size_bytes)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="panel" aria-label="almacenamiento">
        <div className="panel__bar">
          <span className="panel__title">ALMACENAMIENTO · render_jobs/</span>
          <span className="panel__aside">{done.length} videos</span>
        </div>
        {storage && (
          <Bar label="CUOTA" pct={storagePct} warnAt={75}
            detail={`${fmtSize(storage.used_bytes)} de ${fmtSize(storage.quota_bytes)} · al superar la cuota no se aceptan nuevos renders`} />
        )}
      </section>

      <section className="panel" aria-label="contenedores">
        <div className="panel__bar">
          <span className="panel__title">CONTENEDORES DOCKER</span>
          <span className="panel__aside">solo lectura · sin controles</span>
        </div>
        {containers === null || containers === undefined ? (
          <p className="empty">Telemetría de contenedores no disponible (runner desconectado).</p>
        ) : (
          <div className="tablewrap">
            <table className="ctable">
              <thead>
                <tr><th>Contenedor</th><th>Estado</th><th>CPU %</th><th>MEM %</th><th>Memoria</th></tr>
              </thead>
              <tbody>
                {containers.map((c) => {
                  const own = c.name === 'codeaerospace-contenido'
                    || c.name.startsWith('manimstudio-render-')
                  return (
                    <tr key={c.name} className={own ? 'ctable__own' : ''}>
                      <td className="mono">{c.name}{own ? ' ◆' : ''}</td>
                      <td><span className={`state state--${c.state}`}>{c.state}</span></td>
                      <td className="num">{c.cpu_pct.toFixed(1)}</td>
                      <td className="num">{c.mem_pct.toFixed(1)}</td>
                      <td className="mono num">{c.mem_usage || '—'}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
        <p className="finePrint">
          ◆ contenedores de ManimStudio. El resto pertenece a otros proyectos de este VPS:
          esta consola solo muestra métricas agregadas y no permite ninguna acción sobre ellos.
        </p>
      </section>
    </main>
  )
}
```

- [ ] **Step 4: CSS de KPIs y acciones** (añadir en `styles.css`, sección monitor)

```css
.kpis {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
  gap: 10px; padding: 12px 14px 4px;
}
.kpi {
  display: grid; gap: 2px; padding: 10px 12px;
  background: var(--panel-2); border: 1px solid var(--line); border-radius: 6px;
}
.kpi__label { font-family: var(--mono); font-size: 11px; color: var(--muted); letter-spacing: .12em; }
.kpi__value { font-family: var(--mono); font-size: 26px; font-weight: 600; color: var(--ink); }
.kpi__value small { font-size: 13px; color: var(--muted); margin-left: 2px; }
.kpi--warn .kpi__value { color: var(--warn); }
.kpi--crit .kpi__value { color: var(--err); }
.kpi--ok .kpi__value { color: var(--ok); }

.admin__actions { display: flex; flex-wrap: wrap; gap: 8px; padding: 12px 14px 4px; }
.armed { display: inline-flex; gap: 6px; }
.admin .notice { margin: 8px 14px 0; }
```

- [ ] **Step 5: Cablear `App.jsx` y `Header.jsx`**

`App.jsx`: `import Admin from './Admin.jsx'` (quitar el import de Monitor) y reemplazar la rama de la vista:

```jsx
      ) : (
        <Admin metrics={metrics} containers={containers} jobs={jobs}
          storage={storage} onJobsChanged={refreshJobs} />
      )}
```

La rama `view === 'library'` queda intacta; el valor de la vista pasa de `'monitor'` a `'admin'` (estado inicial `'studio'` sin cambios).

`Header.jsx`: reemplazar el botón Monitoreo:

```jsx
        <button className={view === 'admin' ? 'tab tab--on' : 'tab'}
          onClick={() => onView('admin')}>Admin</button>
```

Borrar `studio/frontend/src/Monitor.jsx` (`git rm`).

- [ ] **Step 6: Verificar build y revisión manual**

Run: `npm run build` → exitoso. Manual: KPIs reflejan métricas; «Eliminar fallidos» y purgas piden confirmación armada, muestran el aviso con conteo y refrescan la tabla; contenedores siguen siendo solo lectura.

- [ ] **Step 7: Commit**

```bash
git add -A studio/frontend/src
git commit -m "feat: panel de administracion con KPIs y acciones en lote (reemplaza Monitor)"
```

---

### Task 7: Backend de lecciones (`lessons.py`)

**Files:**
- Create: `studio/backend/app/lessons.py`
- Modify: `studio/backend/app/config.py` (añadir `lessons_dir`)
- Modify: `studio/backend/app/main.py` (2 rutas)
- Modify: `studio/backend/requirements.txt` (añadir `PyYAML>=6.0`)
- Modify: `studio/backend/tests/conftest.py` (env `MS_LESSONS_DIR`)
- Test: `studio/backend/tests/test_lessons.py` (nuevo)

**Interfaces:**
- Produces: `LessonStore(root: Path)` con `.index() -> dict` y `.get(lesson_id: str) -> dict | None`. Rutas: `GET /api/lessons` → `{"categories": [{slug, name, count, lessons: [{id, title, level, summary, tags, minutes, order}]}]}`; `GET /api/lessons/{id}` (id = `categoria/NN-slug`) → lo mismo que el item del índice + `"markdown": str`. Formato de archivo: `studio/content/lessons/<categoria>/<NN>-<slug>.md` con frontmatter YAML delimitado por `---`; categorías en `studio/content/lessons/categories.yaml` (lista de `{slug, name}` en orden de presentación).

- [ ] **Step 1: Config + conftest**

`config.py`, tras `self.runner_socket`:

```python
        self.lessons_dir = Path(os.environ.get(
            "MS_LESSONS_DIR", str(self.workspace / "studio" / "content" / "lessons")))
```

`tests/conftest.py`, en `_set_env`, tras `MS_RUNNER_SOCKET`:

```python
    os.environ["MS_LESSONS_DIR"] = str(tmp_path / "lessons")
```

- [ ] **Step 2: Escribir tests que fallan** — crear `studio/backend/tests/test_lessons.py`:

```python
"""Tests de la biblioteca de lecciones (indice, detalle, seguridad, cache)."""

import os
import time
from pathlib import Path

LESSON = """---
title: Órbitas de Kepler
level: intro
summary: Las tres leyes que gobiernan el movimiento orbital.
tags: [kepler, orbitas]
minutes: 12
order: 1
---

# Órbitas de Kepler

La primera ley dice que $r = \\frac{p}{1 + e\\cos\\theta}$.
"""

CATS = """- slug: dinamica-orbital
  name: Dinámica Orbital
- slug: satelites
  name: Satélites
"""


def _seed(tmp: Path) -> None:
    root = Path(os.environ["MS_LESSONS_DIR"])
    (root / "dinamica-orbital").mkdir(parents=True, exist_ok=True)
    (root / "categories.yaml").write_text(CATS, encoding="utf-8")
    (root / "dinamica-orbital" / "01-orbitas-kepler.md").write_text(
        LESSON, encoding="utf-8")


def test_indice_lista_categorias_y_metadatos(authed, tmp_path):
    _seed(tmp_path)
    r = authed.get("/api/lessons")
    assert r.status_code == 200
    cats = r.json()["categories"]
    assert [c["slug"] for c in cats] == ["dinamica-orbital", "satelites"]
    dyn = cats[0]
    assert dyn["name"] == "Dinámica Orbital"
    assert dyn["count"] == 1
    lesson = dyn["lessons"][0]
    assert lesson["id"] == "dinamica-orbital/01-orbitas-kepler"
    assert lesson["title"] == "Órbitas de Kepler"
    assert lesson["minutes"] == 12
    assert "markdown" not in lesson  # el indice no incluye el cuerpo


def test_detalle_devuelve_markdown(authed, tmp_path):
    _seed(tmp_path)
    r = authed.get("/api/lessons/dinamica-orbital/01-orbitas-kepler")
    assert r.status_code == 200
    body = r.json()
    assert body["title"] == "Órbitas de Kepler"
    assert "# Órbitas de Kepler" in body["markdown"]
    assert "---" not in body["markdown"].split("\n")[0]  # sin frontmatter


def test_detalle_404_y_path_traversal(authed, tmp_path):
    _seed(tmp_path)
    assert authed.get("/api/lessons/dinamica-orbital/99-no-existe").status_code == 404
    assert authed.get("/api/lessons/../../etc/passwd").status_code == 404
    assert authed.get("/api/lessons/dinamica-orbital/..%2F..%2Fsecreto").status_code == 404


def test_lecciones_requieren_auth(client, tmp_path):
    _seed(tmp_path)
    assert client.get("/api/lessons").status_code == 401
    assert client.get(
        "/api/lessons/dinamica-orbital/01-orbitas-kepler").status_code == 401


def test_indice_se_actualiza_al_cambiar_archivos(authed, tmp_path):
    _seed(tmp_path)
    assert authed.get("/api/lessons").json()["categories"][1]["count"] == 0
    root = Path(os.environ["MS_LESSONS_DIR"])
    (root / "satelites").mkdir(exist_ok=True)
    nueva = LESSON.replace("Órbitas de Kepler", "Anatomía de un satélite")
    time.sleep(0.02)  # asegura mtime distinto
    (root / "satelites" / "01-anatomia.md").write_text(nueva, encoding="utf-8")
    assert authed.get("/api/lessons").json()["categories"][1]["count"] == 1
```

- [ ] **Step 3: Verificar que fallan**

Run: `venv/bin/pytest tests/test_lessons.py -q`
Expected: FAIL con 404 (rutas inexistentes).

- [ ] **Step 4: Implementar `lessons.py`**

```python
"""Biblioteca de lecciones educativas: Markdown + frontmatter YAML en disco.

El contenido vive en studio/content/lessons/<categoria>/<NN>-<slug>.md y se
versiona en git (sin CRUD web). El indice se cachea en memoria y se invalida
cuando cambia el mtime mas reciente del arbol.
"""

import re
import threading
from pathlib import Path

import yaml

# id valido: "<categoria>/<NN>-<slug>" — sin puntos ni barras extra, lo que
# tambien bloquea cualquier path traversal.
RE_LESSON_ID = re.compile(r"^[a-z0-9][a-z0-9-]*/[0-9]{2}-[a-z0-9][a-z0-9-]*$")


def _meta(meta: dict, lesson_id: str) -> dict:
    return {
        "id": lesson_id,
        "title": meta.get("title", lesson_id),
        "level": meta.get("level", "intro"),
        "summary": meta.get("summary", ""),
        "tags": meta.get("tags", []),
        "minutes": meta.get("minutes", 10),
        "order": meta.get("order", 99),
    }


class LessonStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self._lock = threading.Lock()
        self._index: dict | None = None
        self._mtime: float = -1.0

    @staticmethod
    def parse(text: str) -> tuple[dict, str]:
        """Separa frontmatter YAML (entre '---') del cuerpo markdown."""
        if not text.startswith("---"):
            return {}, text
        parts = text.split("---", 2)
        if len(parts) < 3:
            return {}, text
        meta = yaml.safe_load(parts[1]) or {}
        return (meta if isinstance(meta, dict) else {}), parts[2].lstrip("\n")

    def _tree_mtime(self) -> float:
        latest = 0.0
        try:
            latest = self.root.stat().st_mtime
            for p in self.root.rglob("*"):
                latest = max(latest, p.stat().st_mtime)
        except OSError:
            pass
        return latest

    def _build_index(self) -> dict:
        cats_file = self.root / "categories.yaml"
        try:
            cats = yaml.safe_load(cats_file.read_text(encoding="utf-8")) or []
        except OSError:
            cats = []
        categories = []
        for cat in cats:
            cat_dir = self.root / cat["slug"]
            lessons = []
            if cat_dir.is_dir():
                for md in sorted(cat_dir.glob("*.md")):
                    try:
                        meta, _ = self.parse(md.read_text(encoding="utf-8"))
                    except OSError:
                        continue
                    lessons.append(_meta(meta, f"{cat['slug']}/{md.stem}"))
            lessons.sort(key=lambda l: (l["order"], l["id"]))
            categories.append({"slug": cat["slug"], "name": cat["name"],
                               "count": len(lessons), "lessons": lessons})
        return {"categories": categories}

    def index(self) -> dict:
        with self._lock:
            mtime = self._tree_mtime()
            if self._index is None or mtime != self._mtime:
                self._index = self._build_index()
                self._mtime = mtime
            return self._index

    def get(self, lesson_id: str) -> dict | None:
        if not RE_LESSON_ID.match(lesson_id):
            return None
        path = self.root / f"{lesson_id}.md"  # el regex garantiza ruta interna
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            return None
        meta, body = self.parse(text)
        return _meta(meta, lesson_id) | {"markdown": body}
```

- [ ] **Step 5: Rutas en `main.py`**

Import: `from .lessons import LessonStore`. Tras `assistant = Assistant(cfg)`:

```python
lessons_store = LessonStore(cfg.lessons_dir)
```

Nueva sección antes de `# ── asistente IA`:

```python
# ── biblioteca de lecciones ───────────────────────────────────────────────────

@app.get("/api/lessons")
async def lessons_index(_=Depends(require_auth)):
    return lessons_store.index()


@app.get("/api/lessons/{lesson_id:path}")
async def lesson_detail(lesson_id: str, _=Depends(require_auth)):
    lesson = lessons_store.get(lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Leccion no encontrada")
    return lesson
```

`requirements.txt`: añadir línea `PyYAML>=6.0`.

- [ ] **Step 6: Verificar que pasa todo**

Run: `venv/bin/pytest -q`
Expected: 51 passed.

- [ ] **Step 7: Commit**

```bash
git add studio/backend/app/lessons.py studio/backend/app/config.py studio/backend/app/main.py studio/backend/requirements.txt studio/backend/tests/conftest.py studio/backend/tests/test_lessons.py
git commit -m "feat: API de biblioteca de lecciones (markdown + frontmatter, cache por mtime)"
```

---

### Task 8: Frontend de lecciones (`Lessons.jsx`)

**Files:**
- Create: `studio/frontend/src/Lessons.jsx`
- Create: `studio/frontend/src/markdown.js`
- Modify: `studio/frontend/src/api.js`, `studio/frontend/src/App.jsx`, `studio/frontend/src/Header.jsx`, `studio/frontend/src/styles.css`, `studio/frontend/package.json`

**Interfaces:**
- Consumes: `GET /api/lessons` y `GET /api/lessons/{id}` (Task 7).
- Produces: `api.lessonsIndex()`, `api.getLesson(id)`; `markdown.js` exporta `renderMarkdown(md: string): string` (HTML sanitizado con KaTeX aplicado); vista `'lessons'` con pestaña «Aprender»; clave localStorage `ms_lessons_read` (JSON array de ids).

- [ ] **Step 1: Instalar dependencias**

Run: `cd /var/www/codeaerospace_contenido/studio/frontend && npm install marked dompurify katex`
Expected: added 3+ packages.

- [ ] **Step 2: `api.js`**

```js
  lessonsIndex: () => request('GET', '/api/lessons'),
  getLesson: (id) => request('GET', `/api/lessons/${id}`),
```

- [ ] **Step 3: Crear `markdown.js`**

```js
// Pipeline de render: KaTeX sobre $...$/$$...$$ -> marked -> DOMPurify.
// Las formulas se extraen ANTES de marked para que este no rompa los
// backslashes de LaTeX; se reinyectan como placeholders ya renderizados.

import { marked } from 'marked'
import DOMPurify from 'dompurify'
import katex from 'katex'

marked.setOptions({ gfm: true, breaks: false })

function renderMath(md) {
  const chunks = []
  // Token improbable en prosa: no colisiona con texto real de las lecciones.
  const keep = (html) => `%%KTX${chunks.push(html) - 1}%%`
  // Bloques $$...$$ primero (pueden contener $ simples dentro)
  let out = md.replace(/\$\$([\s\S]+?)\$\$/g, (_, tex) =>
    keep(katex.renderToString(tex.trim(), { displayMode: true, throwOnError: false })))
  // Inline $...$ (sin saltos de linea dentro)
  out = out.replace(/\$([^$\n]+?)\$/g, (_, tex) =>
    keep(katex.renderToString(tex.trim(), { throwOnError: false })))
  return { out, chunks }
}

export function renderMarkdown(md) {
  const { out, chunks } = renderMath(md)
  let html = marked.parse(out)
  html = html.replace(/%%KTX(\d+)%%/g, (_, i) => chunks[Number(i)])
  return DOMPurify.sanitize(html, {
    USE_PROFILES: { html: true, mathMl: true, svg: true },
  })
}
```

- [ ] **Step 4: Crear `Lessons.jsx`**

```jsx
// Biblioteca educativa: categorias + lista + lector con progreso de lectura.

import { useEffect, useMemo, useRef, useState } from 'react'
import { api } from './api.js'
import { renderMarkdown } from './markdown.js'
import 'katex/dist/katex.min.css'

const READ_KEY = 'ms_lessons_read'

function readSet() {
  try { return new Set(JSON.parse(localStorage.getItem(READ_KEY)) || []) }
  catch { return new Set() }
}

const LEVEL_LABEL = { intro: 'intro', medio: 'medio', avanzado: 'avanzado' }

export default function Lessons() {
  const [index, setIndex] = useState(null)
  const [error, setError] = useState('')
  const [catSlug, setCatSlug] = useState(null)
  const [lesson, setLesson] = useState(null) // {id,...,markdown}
  const [query, setQuery] = useState('')
  const [read, setRead] = useState(readSet)
  const [progress, setProgress] = useState(0)
  const readerRef = useRef(null)

  useEffect(() => {
    api.lessonsIndex()
      .then((d) => {
        setIndex(d)
        if (d.categories.length) setCatSlug(d.categories[0].slug)
      })
      .catch((err) => setError(err.message))
  }, [])

  const cat = index?.categories.find((c) => c.slug === catSlug)
  const list = useMemo(() => {
    if (!cat) return []
    if (!query.trim()) return cat.lessons
    const q = query.toLowerCase()
    return cat.lessons.filter((l) =>
      l.title.toLowerCase().includes(q)
      || l.tags.some((t) => String(t).toLowerCase().includes(q)))
  }, [cat, query])

  const open = async (id) => {
    setError('')
    try {
      const l = await api.getLesson(id)
      setLesson(l)
      setProgress(0)
      readerRef.current?.scrollTo(0, 0)
      setRead((prev) => {
        const next = new Set(prev).add(id)
        localStorage.setItem(READ_KEY, JSON.stringify([...next]))
        return next
      })
    } catch (err) {
      setError(err.status === 404 ? 'Lección no encontrada' : err.message)
    }
  }

  const onScroll = (e) => {
    const el = e.target
    const max = el.scrollHeight - el.clientHeight
    setProgress(max > 0 ? Math.min(100, (el.scrollTop / max) * 100) : 100)
  }

  const idx = lesson && cat ? cat.lessons.findIndex((l) => l.id === lesson.id) : -1
  const prev = idx > 0 ? cat.lessons[idx - 1] : null
  const next = idx >= 0 && idx < cat.lessons.length - 1 ? cat.lessons[idx + 1] : null
  const html = useMemo(
    () => (lesson ? renderMarkdown(lesson.markdown) : ''), [lesson])

  if (error && !index) return <main className="lessons"><p className="empty">{error}</p></main>
  if (!index) return <main className="lessons"><p className="empty">Cargando biblioteca…</p></main>

  return (
    <main className="lessons">
      <aside className="lessons__nav panel">
        <div className="panel__bar"><span className="panel__title">APRENDER</span></div>
        <input className="lessons__search" type="search" placeholder="Buscar…"
          value={query} onChange={(e) => setQuery(e.target.value)}
          aria-label="buscar lecciones" />
        <nav className="lessons__cats" aria-label="categorías">
          {index.categories.map((c) => (
            <button key={c.slug}
              className={`lessons__cat${c.slug === catSlug ? ' lessons__cat--on' : ''}`}
              onClick={() => { setCatSlug(c.slug); setQuery('') }}>
              {c.name} <span className="lessons__count">{c.count}</span>
            </button>
          ))}
        </nav>
        <ul className="lessons__list">
          {list.map((l) => (
            <li key={l.id}>
              <button
                className={`lessons__item${lesson?.id === l.id ? ' lessons__item--on' : ''}`}
                onClick={() => open(l.id)}>
                <span className={`lessons__dotread${read.has(l.id) ? ' lessons__dotread--yes' : ''}`}
                  aria-label={read.has(l.id) ? 'leída' : 'no leída'} />
                <span className="lessons__ititle">{l.title}</span>
                <span className="lessons__imeta">
                  {LEVEL_LABEL[l.level] || l.level} · {l.minutes} min
                </span>
              </button>
            </li>
          ))}
          {list.length === 0 && <li className="empty">Sin resultados.</li>}
        </ul>
      </aside>

      <section className="lessons__reader panel" aria-label="lector">
        {lesson ? (
          <>
            <div className="lessons__progress" aria-hidden="true">
              <div style={{ width: `${progress}%` }} />
            </div>
            <div className="lessons__scroll" onScroll={onScroll} ref={readerRef}>
              <header className="lessons__head">
                <p className="lessons__crumb">{cat?.name}</p>
                <h1>{lesson.title}</h1>
                <p className="lessons__sub">
                  {LEVEL_LABEL[lesson.level] || lesson.level} · {lesson.minutes} min
                  {lesson.tags.length > 0 && <> · {lesson.tags.join(' · ')}</>}
                </p>
              </header>
              <article className="reader" dangerouslySetInnerHTML={{ __html: html }} />
              <footer className="lessons__foot">
                {prev ? (
                  <button className="btn" onClick={() => open(prev.id)}>← {prev.title}</button>
                ) : <span />}
                {next && (
                  <button className="btn btn--primary" onClick={() => open(next.id)}>
                    {next.title} →
                  </button>
                )}
              </footer>
            </div>
          </>
        ) : (
          <div className="lessons__welcome">
            <p className="empty">
              Elige una lección. {index.categories.reduce((n, c) => n + c.count, 0)} lecciones
              en {index.categories.length} categorías.
            </p>
          </div>
        )}
        {error && index && <p className="notice notice--warn" role="alert">{error}</p>}
      </section>
    </main>
  )
}
```

- [ ] **Step 5: CSS de la biblioteca** (añadir en `styles.css`)

```css
/* ── lecciones ──────────────────────────────────────────────────────────── */
.lessons {
  flex: 1; display: grid; grid-template-columns: 300px 1fr;
  gap: 14px; padding: 14px; min-height: 0;
}
.lessons__nav { display: flex; flex-direction: column; min-height: 0; }
.lessons__search {
  margin: 10px 12px 6px; padding: 7px 10px;
  background: var(--panel-2); border: 1px solid var(--line); border-radius: 4px;
  color: var(--ink); font: inherit;
}
.lessons__cats { display: flex; flex-direction: column; padding: 4px 8px; }
.lessons__cat {
  display: flex; justify-content: space-between; align-items: center;
  background: none; border: 0; border-radius: 4px; color: var(--muted);
  font: inherit; font-size: 13px; text-align: left;
  padding: 6px 9px; cursor: pointer;
}
.lessons__cat:hover { color: var(--ink); background: var(--panel-2); }
.lessons__cat--on { color: var(--gold); background: var(--panel-2); }
.lessons__count { font-family: var(--mono); font-size: 11px; }
.lessons__list {
  list-style: none; padding: 6px 8px 10px; margin: 0;
  overflow-y: auto; border-top: 1px solid var(--line);
}
.lessons__item {
  display: grid; grid-template-columns: 10px 1fr; column-gap: 8px;
  width: 100%; background: none; border: 0; border-radius: 4px;
  color: var(--ink); font: inherit; text-align: left;
  padding: 8px 9px; cursor: pointer;
}
.lessons__item:hover { background: var(--panel-2); }
.lessons__item--on { background: var(--panel-2); outline: 1px solid var(--line); }
.lessons__dotread {
  width: 7px; height: 7px; border-radius: 50%; margin-top: 5px;
  border: 1px solid var(--muted);
}
.lessons__dotread--yes { background: var(--ok); border-color: var(--ok); }
.lessons__ititle { font-size: 13px; }
.lessons__imeta { grid-column: 2; color: var(--muted); font-size: 11px; }

.lessons__reader { position: relative; display: flex; flex-direction: column; min-height: 0; }
.lessons__progress {
  position: absolute; top: 0; left: 0; right: 0; height: 2px; z-index: 2;
  background: var(--line);
}
.lessons__progress div { height: 100%; background: var(--gold); transition: width .1s linear; }
.lessons__scroll { overflow-y: auto; padding: 26px 34px 34px; }
.lessons__head { max-width: 70ch; margin: 0 auto 18px; }
.lessons__crumb {
  font-family: var(--mono); font-size: 11px; letter-spacing: .14em;
  color: var(--gold); text-transform: uppercase;
}
.lessons__head h1 { font-size: 26px; margin: 6px 0 4px; }
.lessons__sub { color: var(--muted); font-size: 12px; }
.lessons__foot {
  display: flex; justify-content: space-between; gap: 10px;
  max-width: 70ch; margin: 30px auto 0;
}
.lessons__welcome { display: grid; place-items: center; flex: 1; }

.reader { max-width: 70ch; margin: 0 auto; font-size: 15px; line-height: 1.75; }
.reader h1, .reader h2, .reader h3 { line-height: 1.3; margin: 1.4em 0 .5em; }
.reader h2 { font-size: 20px; border-bottom: 1px solid var(--line); padding-bottom: 6px; }
.reader h3 { font-size: 16px; }
.reader p, .reader ul, .reader ol { margin: 0 0 1em; }
.reader li { margin: .3em 0; }
.reader code {
  font-family: var(--mono); font-size: .88em;
  background: var(--panel-2); border: 1px solid var(--line);
  border-radius: 3px; padding: 1px 5px;
}
.reader pre {
  background: var(--panel-2); border: 1px solid var(--line); border-radius: 6px;
  padding: 12px 14px; overflow-x: auto; margin: 0 0 1em;
}
.reader pre code { background: none; border: 0; padding: 0; }
.reader table { border-collapse: collapse; margin: 0 0 1em; width: 100%; }
.reader th, .reader td { border: 1px solid var(--line); padding: 6px 10px; text-align: left; }
.reader th { background: var(--panel-2); }
.reader blockquote {
  border-left: 3px solid var(--gold); margin: 0 0 1em; padding: 4px 14px;
  color: var(--muted);
}
.reader .katex-display { overflow-x: auto; padding: 4px 0; }

@media (max-width: 860px) {
  .lessons { grid-template-columns: 1fr; }
  .lessons__nav { max-height: 40vh; }
}
```

- [ ] **Step 6: Cablear `App.jsx` y `Header.jsx`**

`App.jsx`: `import Lessons from './Lessons.jsx'` y añadir la rama:

```jsx
      ) : view === 'lessons' ? (
        <Lessons />
```

`Header.jsx`: añadir pestaña entre Biblioteca y Admin:

```jsx
        <button className={view === 'lessons' ? 'tab tab--on' : 'tab'}
          onClick={() => onView('lessons')}>Aprender</button>
```

- [ ] **Step 7: Verificar build y revisión manual**

Run: `npm run build` → exitoso. Manual (con las lecciones de prueba de Task 9 o un `.md` provisional): fórmulas `$...$`/`$$...$$` renderizan; búsqueda filtra; punto verde marca leídas tras abrir; anterior/siguiente navegan; barra de progreso avanza al hacer scroll.

- [ ] **Step 8: Commit**

```bash
git add studio/frontend/src studio/frontend/package.json studio/frontend/package-lock.json
git commit -m "feat: vista Aprender con lector markdown + KaTeX y progreso de lectura"
```

---

## Tareas de contenido (9–14)

Las seis tareas siguientes crean las ~60 lecciones. Reglas comunes a TODAS:

- Cada lección es un `.md` en `studio/content/lessons/<categoria>/<NN>-<slug>.md` con frontmatter completo:

```markdown
---
title: <título con tildes>
level: intro | medio | avanzado
summary: <una frase de 15-25 palabras>
tags: [<3-5 tags en minúsculas>]
minutes: <8-20, estimando ~150 palabras/min>
order: <N, igual al NN del archivo>
---
```

- Cuerpo: 1000–2000 palabras en español, con esta estructura exacta de secciones:
  `## Objetivos` (3-5 bullets) → 3-5 secciones `## <desarrollo>` (con fórmulas `$...$`/`$$...$$` donde el tema lo pida, tablas comparativas y diagramas en bloques de código cuando aclaren) → `## Ideas clave` (4-6 bullets) → `## Para seguir` (referencia a las lecciones siguientes de la categoría por título).
- El contenido debe ser técnicamente correcto y sustancial: definiciones precisas, números reales (frecuencias, altitudes, latencias), fórmulas correctas.
- Verificación por tarea: `venv/bin/pytest tests/test_lessons.py -q` sigue verde, y `curl` manual no aplica — basta abrir la vista Aprender en dev o confirmar que `GET /api/lessons` indexa el número esperado de lecciones (puede hacerse con un test rápido de conteo NO comprometido, o visualmente).
- Commit por tarea.

### Task 9: `categories.yaml` + categorías Espacio y Satélites

**Files:**
- Create: `studio/content/lessons/categories.yaml`
- Create: `studio/content/lessons/espacio/01..05-*.md` (5 lecciones)
- Create: `studio/content/lessons/satelites/01..05-*.md` (5 lecciones)

- [ ] **Step 1: `categories.yaml`** (orden de presentación definitivo):

```yaml
- slug: espacio
  name: El Espacio
- slug: satelites
  name: Satélites
- slug: dinamica-orbital
  name: Dinámica Orbital
- slug: apuntamiento-satelital
  name: Apuntamiento Satelital
- slug: redes-telecomunicaciones
  name: Redes de Telecomunicaciones
- slug: redes-datos
  name: Redes de Datos
- slug: sistemas-distribuidos
  name: Sistemas Distribuidos
- slug: redes-6g
  name: Redes 6G
- slug: inteligencia-artificial
  name: Inteligencia Artificial
- slug: agentes-ia
  name: Agentes de IA
- slug: ia-agentica
  name: IA Agéntica
- slug: tecnologia-frontera
  name: Tecnología de Frontera
```

- [ ] **Step 2: Lecciones de `espacio/`**

1. `01-el-entorno-espacial.md` — *El entorno espacial* (intro): dónde empieza el espacio (línea de Kármán, 100 km), capas de la atmósfera y arrastre residual, vacío, radiación (cinturones de Van Allen), temperatura y ciclos térmicos, micrometeoritos.
2. `02-el-sistema-solar-como-escenario.md` — *El sistema solar como escenario de misiones* (intro): regiones de interés (LEO/MEO/GEO/cislunar/interplanetario), puntos de Lagrange y sus usos (jwst en L2), viento solar y clima espacial.
3. `03-cohetes-y-acceso-al-espacio.md` — *Cohetes y acceso al espacio* (medio): ecuación de Tsiolkovsky $\Delta v = v_e \ln(m_0/m_f)$, etapas, ventanas de lanzamiento, inclinación vs latitud del sitio, costo por kg y reutilización.
4. `04-basura-espacial.md` — *Basura espacial y sostenibilidad orbital* (medio): población de escombros por tamaño, síndrome de Kessler, maniobras de evasión (COLA), mitigación (desorbitado a 25/5 años), tracking terrestre.
5. `05-clima-espacial.md` — *Clima espacial y sus efectos* (avanzado): fulguraciones y CME, índices Kp/Dst, efectos en electrónica (SEU, latch-up), en comunicaciones (scintilación ionosférica) y en arrastre atmosférico; el evento Carrington.

- [ ] **Step 3: Lecciones de `satelites/`**

1. `01-anatomia-de-un-satelite.md` — *Anatomía de un satélite* (intro): bus vs payload; subsistemas EPS (paneles, baterías), TT&C, ADCS, propulsión, térmico, estructura, OBC; presupuestos de masa y potencia.
2. `02-orbitas-y-tipos-de-satelite.md` — *Órbitas y familias de satélites* (intro): LEO/MEO/GEO/HEO con altitudes y periodos típicos, SSO y hora local del nodo, Molniya, aplicaciones por órbita (observación, navegación, comunicaciones); tabla comparativa latencia/cobertura.
3. `03-comunicaciones-por-satelite.md` — *Comunicaciones por satélite* (medio): bandas (L/S/C/X/Ku/Ka con GHz), transpondedores, FDMA/TDMA, ecuación de enlace $C/N_0 = EIRP - L_p + G/T - k$, VSAT, HTS y beam-hopping.
4. `04-megaconstelaciones.md` — *Megaconstelaciones LEO* (medio): Starlink/OneWeb/Kuiper (números y altitudes), ISL láser, handover entre satélites, latencia vs GEO ($\sim$25 ms vs $\sim$250 ms RTT teórico mínimo), retos regulatorios y astronómicos.
5. `05-cubesats-y-newspace.md` — *CubeSats y NewSpace* (medio): estándar U (10 cm, 1.33 kg), COTS, rideshare, arquitecturas de misión distribuidas, casos (Planet, Spire), cadena de valor NewSpace.

- [ ] **Step 4: Verificar y commit**

Run: `venv/bin/pytest tests/test_lessons.py -q` → verde.

```bash
git add studio/content
git commit -m "content: categorias + lecciones de Espacio y Satelites (10)"
```

### Task 10: Dinámica Orbital y Apuntamiento Satelital

**Files:**
- Create: `studio/content/lessons/dinamica-orbital/01..05-*.md`
- Create: `studio/content/lessons/apuntamiento-satelital/01..05-*.md`

- [ ] **Step 1: Lecciones de `dinamica-orbital/`** (uso intensivo de KaTeX)

1. `01-leyes-de-kepler-y-gravitacion.md` — *Leyes de Kepler y gravitación* (intro): las tres leyes, $F = GMm/r^2$, ecuación de la cónica $r = p/(1+e\cos\theta)$, periodo $T = 2\pi\sqrt{a^3/\mu}$ con $\mu_\oplus = 398600.4\ \text{km}^3/\text{s}^2$.
2. `02-elementos-orbitales.md` — *Elementos orbitales clásicos* (medio): los 6 elementos keplerianos $(a, e, i, \Omega, \omega, \nu)$ con figura conceptual (diagrama ASCII), anomalías verdadera/excéntrica/media, ecuación de Kepler $M = E - e\sin E$, TLE y su lectura.
3. `03-maniobras-orbitales.md` — *Maniobras orbitales* (medio): vis-viva $v^2 = \mu(2/r - 1/a)$, transferencia de Hohmann con $\Delta v$ total, cambio de plano $\Delta v = 2v\sin(\Delta i/2)$, bielíptica, rendezvous básico.
4. `04-perturbaciones.md` — *Perturbaciones orbitales* (avanzado): $J_2$ y precesión nodal $\dot\Omega = -\frac{3}{2}J_2 n \left(\frac{R_\oplus}{p}\right)^2 \cos i$ (base de SSO), arrastre atmosférico y decaimiento, presión de radiación solar, tercer cuerpo; propagadores (SGP4 vs integración numérica).
5. `05-determinacion-de-orbitas.md` — *Determinación y propagación de órbitas* (avanzado): observables (radar, óptico, GNSS), mínimos cuadrados y filtro de Kalman (idea conceptual), catálogos (18 SDS, Space-Track), precisión y covarianza.

- [ ] **Step 2: Lecciones de `apuntamiento-satelital/`**

1. `01-geometria-de-apuntamiento.md` — *Geometría de apuntamiento* (intro): azimut/elevación desde una estación, ángulo de elevación mínimo, cálculo de visibilidad, huella (footprint) y su radio $\rho = R_\oplus \arccos\left(\frac{R_\oplus}{R_\oplus + h}\cos\varepsilon\right) - \varepsilon$ simplificado, pases y su duración en LEO.
2. `02-sistemas-de-referencia.md` — *Sistemas de referencia y actitud* (medio): ECI/ECEF/topocéntrico/LVLH, transformaciones, representación de actitud (ángulos de Euler, cuaterniones y por qué evitan gimbal lock), definición de apuntamiento nadir/target/inercial.
3. `03-adcs-sensores-y-actuadores.md` — *ADCS: sensores y actuadores* (medio): star trackers, sun sensors, magnetómetros, IMU; ruedas de reacción y su saturación, magnetorquers, propulsión; presupuesto de apuntamiento (precisión vs estabilidad, arcsec/arcmin).
4. `04-seguimiento-desde-tierra.md` — *Seguimiento desde estaciones terrenas* (medio): predicción de pases con TLE+SGP4, curvas Az/El, programa de seguimiento (rotores), efecto Doppler $\Delta f = f_0 v_r / c$ y su compensación, keyhole en monturas Az/El.
5. `05-apuntamiento-de-antenas-geo.md` — *Apuntamiento de antenas a GEO* (intro): cálculo de azimut/elevación/polarización hacia un satélite GEO desde lat/lon, ancho de haz $\theta_{3dB} \approx 70\lambda/D$ grados, pointing loss, alineación práctica de una VSAT.

- [ ] **Step 3: Verificar y commit**

```bash
git add studio/content
git commit -m "content: lecciones de Dinamica Orbital y Apuntamiento Satelital (10)"
```

### Task 11: Redes de Telecomunicaciones y Redes de Datos

**Files:**
- Create: `studio/content/lessons/redes-telecomunicaciones/01..05-*.md`
- Create: `studio/content/lessons/redes-datos/01..05-*.md`

- [ ] **Step 1: Lecciones de `redes-telecomunicaciones/`**

1. `01-fundamentos-de-señales.md` — *Fundamentos de señales y espectro* (intro): señal, ancho de banda, dB y dBm, Fourier conceptual, Nyquist $C = 2B\log_2 M$ y Shannon $C = B\log_2(1 + S/N)$, ejemplo numérico.
2. `02-modulacion-y-codificacion.md` — *Modulación y codificación* (medio): AM/FM/PM → ASK/FSK/PSK/QAM, constelaciones, BER vs Eb/N0, FEC (convolucional, turbo, LDPC) y code rate, modulación adaptativa (DVB-S2X, MODCOD).
3. `03-medios-de-transmision.md` — *Medios de transmisión* (intro): par trenzado (categorías), coaxial, fibra (monomodo/multimodo, atenuación dB/km, WDM), radioenlace y su balance, comparativa tabla capacidad/alcance/costo.
4. `04-redes-celulares.md` — *Redes celulares: de 1G a 5G* (medio): concepto celular y reuso de frecuencia, arquitectura (RAN/core), evolución generacional con hitos técnicos (GSM, UMTS, LTE con OFDMA, 5G NR con numerologías), mmWave y masivo MIMO.
5. `05-conmutacion-y-señalizacion.md` — *Conmutación y señalización* (medio): circuitos vs paquetes, PSTN y SS7, VoIP y SIP, QoS (jitter, latencia, MOS), la migración a all-IP.

- [ ] **Step 2: Lecciones de `redes-datos/`**

1. `01-modelo-osi-y-tcpip.md` — *Modelos OSI y TCP/IP* (intro): las 7 capas con ejemplos, encapsulación, PDU por capa, mapeo OSI↔TCP/IP, crítica práctica del modelo.
2. `02-ethernet-y-conmutacion.md` — *Ethernet y conmutación LAN* (intro): tramas, MAC, dominio de colisión vs difusión, switches y tabla CAM, VLAN y trunking (802.1Q), STP conceptual, velocidades (10M→800G).
3. `03-ip-y-enrutamiento.md` — *IP y enrutamiento* (medio): IPv4/IPv6, subneteo con ejemplos CIDR, tabla de rutas y longest-prefix-match, IGP (OSPF conceptual) vs BGP, NAT y sus problemas.
4. `04-transporte-tcp-udp-quic.md` — *Transporte: TCP, UDP y QUIC* (medio): three-way handshake, control de flujo y congestión (slow start, AIMD, CUBIC/BBR), head-of-line blocking, UDP y cuándo usarlo, QUIC/HTTP-3.
5. `05-redes-definidas-por-software.md` — *SDN y virtualización de red* (avanzado): plano de control vs datos, OpenFlow/P4 conceptual, NFV, overlays (VXLAN), intent-based networking; el datacenter como red Clos.

- [ ] **Step 3: Verificar y commit**

```bash
git add studio/content
git commit -m "content: lecciones de Redes de Telecomunicaciones y Redes de Datos (10)"
```

### Task 12: Sistemas Distribuidos y Redes 6G

**Files:**
- Create: `studio/content/lessons/sistemas-distribuidos/01..05-*.md`
- Create: `studio/content/lessons/redes-6g/01..05-*.md`

- [ ] **Step 1: Lecciones de `sistemas-distribuidos/`**

1. `01-fundamentos-y-falacias.md` — *Fundamentos y las 8 falacias* (intro): qué es un sistema distribuido, las 8 falacias de Deutsch comentadas, modelos de fallo (crash, omisión, bizantino), sincronía vs asincronía.
2. `02-tiempo-y-orden.md` — *Tiempo, relojes y orden de eventos* (medio): relojes físicos y deriva, NTP/PTP, happened-before de Lamport, relojes lógicos y vectoriales con ejemplo trabajado, TrueTime de Spanner.
3. `03-consistencia-y-cap.md` — *Consistencia y el teorema CAP* (medio): linealizabilidad vs serializabilidad vs eventual, CAP bien enunciado (y sus malentendidos), PACELC, ejemplos por base de datos (tabla).
4. `04-consenso.md` — *Consenso: Paxos y Raft* (avanzado): el problema (FLP conceptual), quórums, Raft paso a paso (elección de líder, replicación de log, term), Paxos en una página, usos (etcd, ZooKeeper).
5. `05-arquitecturas-modernas.md` — *Arquitecturas distribuidas modernas* (medio): microservicios vs monolito, colas y event-driven, sagas e idempotencia, service mesh, observabilidad (métricas/logs/trazas); cuándo NO distribuir.

- [ ] **Step 2: Lecciones de `redes-6g/`**

1. `01-de-5g-a-6g.md` — *De 5G a 6G: visión y calendario* (intro): qué dejó pendiente 5G, IMT-2030 y sus 6 escenarios de uso (ITU-R), KPIs objetivo (tabla 5G vs 6G: pico 1 Tbps, latencia <0.1 ms, densidad 10^7 disp/km²), hoja de ruta 3GPP (Rel-20/21).
2. `02-espectro-thz-y-nuevas-bandas.md` — *Espectro: sub-THz y nuevas bandas* (medio): bandas centimétricas 7-15 GHz (FR3), 100-300 GHz, propagación THz (absorción molecular, alcance), fotónica integrada, retos de RF.
3. `03-isac-sensado-y-comunicacion.md` — *ISAC: sensado y comunicación integrados* (avanzado): la red como radar, formas de onda duales, casos de uso (detección de gestos, mapeo, vehicular), métricas CRB conceptual, privacidad.
4. `04-ris-y-superficies-inteligentes.md` — *Superficies inteligentes reconfigurables (RIS)* (avanzado): metasuperficies, control de fase por elemento, canal programable $y = (\mathbf{h}_r^H \boldsymbol{\Theta} \mathbf{h}_t) x + n$ conceptual, near-field, prototipos y limitaciones reales.
5. `05-redes-no-terrestres-ntn.md` — *Redes no terrestres (NTN) en 6G* (medio): integración satélite-celular (3GPP NTN Rel-17+), direct-to-device (Starlink/AST), arquitectura de capas LEO/HAPS/terrestre, doppler y timing advance en NTN, el enlace con las categorías de satélites de esta biblioteca.

- [ ] **Step 3: Verificar y commit**

```bash
git add studio/content
git commit -m "content: lecciones de Sistemas Distribuidos y Redes 6G (10)"
```

### Task 13: Inteligencia Artificial y Agentes de IA

**Files:**
- Create: `studio/content/lessons/inteligencia-artificial/01..05-*.md`
- Create: `studio/content/lessons/agentes-ia/01..05-*.md`

- [ ] **Step 1: Lecciones de `inteligencia-artificial/`**

1. `01-panorama-de-la-ia.md` — *Panorama de la IA moderna* (intro): IA simbólica vs aprendizaje, ML/DL/GenAI como subconjuntos, tareas (clasificación, regresión, generación), el ciclo datos→entrenamiento→inferencia, hitos 2012-2025.
2. `02-redes-neuronales.md` — *Redes neuronales desde cero* (medio): neurona $y = \sigma(\mathbf{w}^T\mathbf{x} + b)$, funciones de activación, descenso de gradiente $\theta \leftarrow \theta - \eta \nabla_\theta \mathcal{L}$, backpropagation conceptual, overfitting y regularización.
3. `03-transformers-y-llms.md` — *Transformers y LLMs* (medio): atención $\text{softmax}(QK^T/\sqrt{d_k})V$, arquitectura encoder/decoder, tokenización, pre-entrenamiento vs fine-tuning vs RLHF, leyes de escala, ventana de contexto.
4. `04-ia-generativa-multimodal.md` — *IA generativa multimodal* (medio): difusión conceptual (ruido→imagen), CLIP y espacios compartidos, generación de video/audio/código, evaluación (benchmarks y sus límites), alucinaciones.
5. `05-etica-y-seguridad-de-la-ia.md` — *Ética y seguridad de la IA* (intro): sesgos y su origen en datos, privacidad, alineación (RLHF/constitucional), interpretabilidad, regulación (AI Act con niveles de riesgo), uso responsable.

- [ ] **Step 2: Lecciones de `agentes-ia/`**

1. `01-que-es-un-agente.md` — *Qué es un agente de IA* (intro): del chatbot al agente (percepción→razonamiento→acción), el bucle agente-entorno, agencia y autonomía graduales, ejemplos actuales (coding agents, asistentes operativos).
2. `02-uso-de-herramientas.md` — *Uso de herramientas (tool use)* (medio): function calling, esquemas JSON, selección de herramienta, errores y reintentos, sandboxing y permisos, el patrón ReAct (razonar-actuar-observar) con traza de ejemplo.
3. `03-memoria-y-contexto.md` — *Memoria y gestión de contexto* (medio): ventana de contexto como recurso, memoria de corto vs largo plazo, RAG (embeddings, chunking, recuperación), resúmenes progresivos, memoria persistente en archivos.
4. `04-planificacion-y-razonamiento.md` — *Planificación y razonamiento* (avanzado): descomposición de tareas, chain/tree-of-thought, planificar-ejecutar-verificar, reflexión y autocorrección, límites actuales (horizonte largo, olvidos).
5. `05-evaluacion-de-agentes.md` — *Evaluación de agentes* (avanzado): benchmarks (SWE-bench, GAIA, tau-bench), métricas (tasa de éxito, costo, pasos), evaluación por LLM-juez y sus sesgos, trazas y observabilidad, evaluación en producción.

- [ ] **Step 3: Verificar y commit**

```bash
git add studio/content
git commit -m "content: lecciones de Inteligencia Artificial y Agentes de IA (10)"
```

### Task 14: IA Agéntica y Tecnología de Frontera

**Files:**
- Create: `studio/content/lessons/ia-agentica/01..05-*.md`
- Create: `studio/content/lessons/tecnologia-frontera/01..05-*.md`

- [ ] **Step 1: Lecciones de `ia-agentica/`**

1. `01-de-agentes-a-sistemas-agenticos.md` — *De agentes a sistemas agénticos* (intro): agente único vs sistema agéntico, orquestación, workflows vs agencia plena (cuándo cada uno), niveles de autonomía y supervisión humana (human-in-the-loop).
2. `02-sistemas-multiagente.md` — *Sistemas multiagente* (medio): topologías (orquestador-trabajadores, jerárquico, debate), delegación y subagentes, comunicación entre agentes, fallos típicos (bucles, deriva de objetivo), coste vs paralelismo.
3. `03-protocolos-e-interoperabilidad.md` — *Protocolos e interoperabilidad (MCP y más)* (medio): por qué hacen falta protocolos, MCP (recursos, herramientas, prompts), A2A conceptual, descubrimiento de capacidades, seguridad de la cadena de herramientas.
4. `04-agentes-en-produccion.md` — *IA agéntica en producción* (avanzado): guardrails y políticas de permisos, sandboxing, auditoría de acciones, gestión de costes y presupuestos de tokens, patrones de despliegue (colas de trabajo, checkpoints, rollback).
5. `05-el-futuro-del-trabajo-agentico.md` — *El futuro del trabajo agéntico* (intro): equipos humano-agente, delegación confiable, economía de agentes, riesgos (concentración, dependencia) y oportunidades; qué habilidades humanas se revalorizan.

- [ ] **Step 2: Lecciones de `tecnologia-frontera/`**

1. `01-computacion-cuantica.md` — *Computación cuántica* (medio): qubit y superposición $|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$, entrelazamiento, puertas y circuitos, algoritmos (Shor, Grover conceptual), corrección de errores y era NISQ, estado real de la industria.
2. `02-fotonica-y-comunicaciones-opticas.md` — *Fotónica y comunicaciones ópticas avanzadas* (medio): fotónica de silicio, comunicación óptica en espacio libre (FSO) y láser intersatelital, QKD (BB84 conceptual) y redes cuánticas, LiFi.
3. `03-computacion-neuromorfica-y-edge.md` — *Computación neuromórfica y edge* (avanzado): spiking neural networks, chips (Loihi conceptual), computación en el borde vs nube (latencia/privacidad/energía), TinyML, aceleradores de IA (GPU/TPU/NPU comparados).
4. `04-materiales-y-energia.md` — *Materiales avanzados y energía* (intro): grafeno y 2D, metamateriales (enlace con RIS), superconductores, perovskitas solares, baterías de estado sólido, fusión (progresos reales: NIF, ITER, startups).
5. `05-biotecnologia-computacional.md` — *Biotecnología computacional* (medio): plegamiento de proteínas (AlphaFold y su impacto), CRISPR conceptual, biología sintética, interfaces cerebro-computadora (estado real), convergencia bio-IA.

- [ ] **Step 3: Verificación final de contenido**

Run: `venv/bin/pytest -q` → todo verde. Con backend en dev, `GET /api/lessons` debe reportar 12 categorías y 60 lecciones en total.

```bash
git add studio/content
git commit -m "content: lecciones de IA Agentica y Tecnologia de Frontera (10)"
```

---

### Task 15: Verificación final y documentación

**Files:**
- Modify: `studio/docs/` (el doc de arquitectura existente que corresponda) y `README.md` del repo (mención breve de la biblioteca educativa)

- [ ] **Step 1: Suite completa**

Run: `cd /var/www/codeaerospace_contenido/studio/backend && venv/bin/pytest -q`
Expected: 51 passed (41 previos + 10 nuevos).

- [ ] **Step 2: Build de producción**

Run: `cd /var/www/codeaerospace_contenido/studio/frontend && npm run build`
Expected: exitoso. KaTeX añade ~270 KB min al bundle. Si `vite` avisa de chunks >500 KB, NO subir `chunkSizeWarningLimit`; separar las libs del lector en un chunk manual:

```js
// vite.config.js — SOLO si aparece el warning de chunk:
build: {
  rollupOptions: {
    output: { manualChunks: { reader: ['marked', 'dompurify', 'katex'] } },
  },
},
```

- [ ] **Step 3: Revisión manual integral**

Checklist: login glass en 2-3 temas distintos + ojito; cambio de tema en caliente en las 4 vistas; Aprender con 60 lecciones, fórmulas y búsqueda; Admin con acciones en lote reales sobre un job de prueba fallido; Biblioteca de videos intacta.

- [ ] **Step 4: Actualizar docs**

En el documento de arquitectura de `studio/docs/`: añadir sección de la biblioteca de lecciones (rutas API, formato de archivo, cache) y de los endpoints en lote. En `README.md` raíz: una línea mencionando la biblioteca educativa.

- [ ] **Step 5: Commit final**

```bash
git add studio/docs README.md studio/frontend/vite.config.js
git commit -m "docs: biblioteca educativa, temas y panel admin en la documentacion"
```
