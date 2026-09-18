# Cifras de `06-pase-ntn-seminario.py` y `07-pada-gemelo-digital.py`

Dos animaciones para el seminario de divulgación de tesis de Alan Rosas
Palacios (25-nov-2026), pedidas para reemplazar dos figuras estáticas del
`.pptx` en `tesis-doctorado-6g`. Verificado contra el repo de tesis el
2026-09-17 (esta sesión sí tuvo acceso de lectura a
`/home/alanrosasp/Claude/tesis-doctorado-6g/`, a diferencia de lo que asumía
el prompt original).

## v2 (2026-09-17): rehecho por dirección de arte, no por cifras

Feedback textual del doctorando sobre la v1: "no me gustó que tuvieran tanto
texto las animaciones, eso se puede poner en la presentación ... más
visuales, con mejor estructura, sin textos" (ver
`PROMPT_MANIM_REHACER_VISUAL_2026-09-17.md` en el repo de tesis). Las CIFRAS
de las tablas de abajo **no cambiaron** — se volvió a verificar que seguían
citando lo mismo, no se recalculó nada — lo que cambió es que casi ninguna
sale ya como texto en pantalla: el título y el subtítulo se quitaron (los
pone `deck_seminario.js` en la diapositiva) y el resto se cuenta con
movimiento real, reusando primitivas de `manim_extensions/` que la v1 no
usaba: `satelites.ConstelacionWalker`/`AnimarWalker`, `transiciones.py`,
`ntn.handover()` (el tren de 3 satélites), `brillo.py` (halos),
`particulas.py` (materializar/Desintegrar). El detalle completo de qué
cambió en cada script está en el docstring de cada archivo. Los .mp4 v1
(con título, subtítulo y las frases completas) quedan en el historial de
`git log` de esta rama si hace falta compararlos; los archivos actuales en
`figuras/` del repo de tesis son la v2.

Dos cifras que la v1 mostraba como texto explicativo se quitaron de la
pantalla en la v2 (siguen citadas en las tablas de abajo, solo que ya no se
dibujan): el par `[0.095, 0.318]` del margen adaptativo (necesitaba una
frase para explicarse) y el "% de una vuelta" del pase (lo reemplazó el
hueco VISIBLE entre los tres satélites del tren, que cuenta lo mismo sin
número).

## `06-pase-ntn-seminario.py` — geometría del pase

| Cifra en pantalla | De dónde sale | Fuente |
|---|---|---|
| h = 600 km, i = 53°, elevación máx., duración del pase, AOS/TCA/LOS | Calculado en vivo por `ntn.pase_leo(600, 53, 19.43, -99.13)` | `manim_extensions/ntn.py`, `ALTURA_LEO600_KM` |
| "% de una vuelta" | `duracion_s / periodo_s` del propio pase, calculado en el script | — (aritmética directa sobre lo anterior) |
| "escenario ilustrativo... no NTNEnv-v2" | Verificado: `NTNEnv-v2` real usa `altitude_km = 550.0`, `min_elevation_deg = 10.0`, y **no modela una órbita real** (es un simulador abstracto de M satélites/K celdas sin inclinación ni propagación SGP4) | `03_IMPLEMENTACION/ntn_env/ntn_env/config.py:31,33` (repo tesis) |

**Lo que NO se usó, a propósito**: el hallazgo real de duty cycle ≈ 1 % (2
pases de 6.7 min en 24 h) que el prompt original pedía verificar SÍ existe y
SÍ se confirmó — está en `05_PROGRESO/CHECKLIST.md:1085` (repo tesis),
medido con SGP4/OMM real a ~400 km sobre CDMX (`ntn_env/ntn_env/
visibility_omm.py`, conector L1, 2026-09-02). Es una cifra real pero de OTRO
código (SGP4 sobre TLE reales), no reproducible con `ntn.pase_leo` de este
repo sin reimplementar esa cadena. Se dejó fuera de la animación para no
mezclar tres escenarios distintos (LEO-600 del testbed, NTNEnv-v2 a 550 km
sin geometría real, y el hallazgo L1 a ~400 km) bajo una sola cifra. Si
quieres ese dato en el video, dímelo y lo agrego como texto citado (no
recalculado).

## `07-pada-gemelo-digital.py` — PADA y margen adaptativo

| Cifra en pantalla | De dónde sale | Fuente |
|---|---|---|
| Sensibilidad 1/5/10/30 episodios → MA 0.199/0.288/0.307/0.318 | Citada tal cual (no recalculada: no hay desglose por semilla de este barrido en este repo) | `02_TEORIA/TEOREMA_MARGEN_ADAPTATIVO.md:317` (repo tesis) |
| Umbral 0.25 y veredicto "G1 ... PASA" | Citado de la compuerta canónica | `05_PROGRESO/GATES.md`, sección `G1 · MA NTNEnv-v2 ≥ 0.25`, `estado: passed`, `valor: MA = 0.318` (repo tesis) |
| Par [0.095, 0.318] | Citado tal cual: 0.095 = margen decisional mínimo demostrado constructivamente en G2b; 0.318 = envolvente estimada (G1). La holgura del Lema 4.7 NO está acotada, por eso se reporta el par y no el 0.318 suelto | `02_TEORIA/TEOREMA_MARGEN_ADAPTATIVO.md:144,188,326,346` (repo tesis) |
| "G0 a G2b aprobadas, G3 desbloqueada, sin correr todavía" | Citado del estado canónico de compuertas | `05_PROGRESO/GATES.md`: G0/G1/G2a/G2b `estado: passed`; G3 `estado: pending`, `accion: Desbloqueado (2026-07-23) · decidir secuenciación` (repo tesis) |
| `+9.5 % a +16.3 %`, `84-87 % del oráculo`, 3/3 semillas | **Verificadas pero NO usadas en el clip final** (se dejaron fuera por presupuesto de tiempo del clip de 20-30 s, hay espacio si quieres una tercera pieza) | `05_PROGRESO/GATES.md` G2b; `03_IMPLEMENTACION/results/gates/G2B_RECUALIFICACION_v7.json` (repo tesis) |

**Nota sobre el chip `fg.etiqueta()`**: es una primitiva añadida a
`manim_extensions/figura.py` (regla de la casa §5.1 — un archivo, un tema).
No existía en este repo como función reutilizable: la versión que usa el
curso "Satélites e IA" vive en la base de datos del Estudio (`style_block`
de ese proyecto), no como archivo git, así que no se pudo importar
directamente. `fg.etiqueta()` es genérica (funciona en tema `paper` y
`marca`) y queda disponible para cualquier figura futura que necesite el
mismo aviso.

En `07-pada-gemelo-digital.py` el chip aparece **una vez**, primero y solo
(la v2 ya no tiene título ni subtítulo antes de él), no pegado en una
esquina durante todo el clip: el lienzo de video de `Figura.pantalla` es
físicamente chico (2 in de alto, fijo, con independencia de `-ql`/`-qh`) y
un chip fijo arriba a la derecha se montaba sobre el lazo PADA y sobre la
curva de MA en las etapas siguientes — se midió en el `-ql`, y se corrigió
antes de la pasada final.

## Duración y resolución final (verificado con `ffprobe`, v2)

| Clip | Resolución | Cuadros/s | Duración |
|---|---|---|---|
| `PaseNtnSeminario.mp4` | 1920×1080 | 60 | 24.8 s |
| `PadaGemeloDigital.mp4` | 1920×1080 | 60 | 26.85 s |

Ambos dentro del objetivo de 20-30 s. Salen en
`media/videos/<script>/1080p60/<Escena>.mp4` dentro de esta rama
(`anim/seminario-ntn-pada`) y ya están copiados a `figuras/` del repo de
tesis con el mismo nombre de archivo que la v1 (`deck_seminario.js` los
referencia por ese nombre exacto, no hacía falta tocarlo).

## Lo que sigue pendiente (declarado, no asumido)

- Insertar los `.mp4` en el `.pptx` — tarea aparte, no hecha aquí.
- Si se quiere la cifra real de duty cycle ~1 % (SGP4 a ~400 km), pedirla
  explícitamente: no está en ninguna de las dos animaciones.
- El JSON `G2B_RECUALIFICACION_v7.json` se verificó pero sus cifras de
  ganancia de QMIX no se dibujaron (ver tabla de arriba).
- El par `[0.095, 0.318]` del margen adaptativo ya no aparece en pantalla en
  la v2 (ver nota de arriba): sigue citado en la tabla si se quiere
  recuperar como rótulo aparte.
