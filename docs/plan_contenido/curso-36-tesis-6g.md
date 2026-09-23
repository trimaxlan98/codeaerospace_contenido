# Curso 36 — La tesis 6G por dentro (familia horizontal + piezas limpias para PowerPoint)

## 1. Cómo reanudar

- Worktree: `/home/alanrosasp/Documentos/github/codeaerospace_contenido-tesis`, rama
  `curso/tesis-6g` (desde `origin/main` ed1b331). `exports/` y `render_jobs/` son
  enlaces al segundo disco, igual que en el checkout principal. El checkout
  principal está en `feat/escritorio` y lo usa otro agente: **no tocarlo**.
- Tablero: §12 de este archivo. Fuente de la tesis:
  `/home/alanrosasp/Claude/tesis-doctorado-6g` (repo **PRIVADO**, licencia restrictiva).
- Frase para reanudar: *"continuamos con el curso de la tesis 6G"*.
- Orden pactado con el dueño (2026-09-22): **primero las piezas limpias**
  (WITCOM 2-6 nov; seminario de divulgación 25-nov), **después el curso**,
  que reutiliza la misma librería.

## 2. Formato — DOS entregables que comparten librería

### 2.1 Las piezas limpias (`presentacion`) — PRIMERO

Animaciones que se funden con un slide de PowerPoint. Decisiones del dueño:

- **Nada de títulos ni subtítulos**: los pone PowerPoint. Solo etiquetas
  imprescindibles (rótulo de mapa: "AOS", "Gateway", un número que cambia).
  Tope duro: **3 palabras por etiqueta**, ninguna oración. Feedback literal
  del dueño en el PR #83: *"no me gustó que tuvieran tanto texto las
  animaciones, eso se puede poner en la presentación"*.
- **Dos fondos, las dos versiones de cada pieza**: navy `#0B1F3A` (los slides
  oscuros del deck del seminario) y blanco (los claros). La paleta se voltea
  con la luminancia del fondo (§8).
- **Sin marca de agua ni escuadras HUD**: `presentacion.aplicar(self, lz,
  marca_agua=False, esquinas=False)`. Lo que mimetiza es no traer identidad
  propia.
- Tipografía de etiquetas: **Carlito** (métricamente idéntica a Calibri, la
  del deck; OFL). Admite acentos, a diferencia de la regla de los cursos.
  Cifras: Carlito también (no Space Mono: en el deck no hay mono).
- Avanza **con el clic**: `presentacion.paso()` entre momentos; un render,
  N fragmentos, empalme invisible. Se empaquetan con
  `studio/tools/empaquetar_presentacion.py` → `.pptx` + mp4/gif sueltos.
- Duración: la que pida la idea (8–30 s por pieza, 1–4 pasos). Sin voz.
- Carpeta: `studio/content/presentaciones/tesis-6g/NN-<tema>/escena.py`.

### 2.2 El curso (familia horizontal) — DESPUÉS

- 12 lecciones × 4 clips = **48 clips**, ~25 min, en 3 módulos de 4.
- Estilo **CONSOLA** (defecto horizontal), **narrado SIN subtítulos** (modo
  del curso 27): título ≤ 6 palabras, rótulos ≤ 4, cifras ≤ 5, guardián
  `_vigilar()` que aborta el render. Molde del `style_block`:
  `studio/content/cursos/procesamiento-senales-1-1-muestreo/style_block.py`.
- Proyecto `Tesis 6G · N.M <título>`, slug `tesis6g-N-M-<tema>`.
- Voz: `guiones.py` en el VPS con el proveedor vigente (edge por defecto
  mientras GCP siga en mora; ver skill manimstudio v3).

## 3. Ángulo editorial

**El problema de poner IA a gobernar una red de satélites no es sólo de
algoritmos, es de instrumento: antes de preguntar si el agente gana hay que
medir si el entorno premia adaptarse.** El curso va de la red que se mueve
(por qué hace falta gobernarla) a las herramientas (Dec-POMDP, MARL, PBFT,
PADA) y termina en el corazón de la tesis: el Margen Adaptativo como
compuerta de falsabilidad, lo que ya encontró —incluido lo que salió mal— y
por qué corre prisa (el congelamiento 6G de 2029).

Frase de cierre del curso (del guion del seminario, del dueño): *"No estoy
tratando de demostrar que la inteligencia artificial gana. Estoy tratando de
que, cuando gane o cuando pierda, sepamos que la medición significaba algo."*

## 4. Público y qué asume

Posgrado técnico no especialista (misma audiencia que el seminario). Asume
el curso 28 (satélites, órbitas) y el 15 (sistemas distribuidos) sin
re-explicarlos; el RL se cuenta desde cero pero rápido.

## 5. Qué NO pisa

| vecino | qué queda por debajo | qué se usa sin re-explicar |
|---|---|---|
| 2 Satélites e IA (8 clips, sólo DB) | la versión divulgativa de 2026-08: este curso la **releva** con el estado vigente de la tesis (HC, Lema reatribuido, G2b) | — |
| 28 Satélites vertical | mecánica orbital, cobertura | pase LEO, ventana de visibilidad |
| 15 Distribuidos | consenso clásico, Paxos/Raft | la idea de quórum |
| 21 Teoría de la información | entropía, MI | el cuello de botella se cuenta como compresión |
| 25 Protocolos | pila TCP/IP | — |

**Regla editorial heredada del curso 2 y del dueño (R6 de la tesis)**: el
estado del arte se afirma con su fuente; lo que la tesis aún no validó a
escala **no se presenta como validado** (G3 desbloqueada y **sin correr**;
MI acción-visibilidad es descriptor, no criterio cumplido). Prohibido
"el primero del mundo" de nada.

## 6. Principio visual no negociable

1. **La red se mueve**: satélites que de verdad recorren su órbita
   (`kepler.py`/`satelites.py`), ventanas que se abren y se cierran.
2. **El margen es una distancia que se ve**: siempre como separación
   vertical entre la línea estática y el techo privilegiado, nunca como
   número suelto.
3. **Lo que un agente no ve, se dibuja apagado**: estado completo en gris,
   observación local encendida.
4. **El clic separa causa y efecto** (piezas): un paso = una consecuencia.
5. **Lo que se invalida se tacha a la vista** (R5, G0, el mock de 3×).
6. **Lo pendiente va a trazos** (G3, fidelidad): nunca sólido.

## 7. Mapa de lecciones (curso)

| # | Lección | 4 clips |
|---|---|---|
| **M1** | **El problema** | |
| 1.1 | La red que se mueve | escala · pase LEO · ventana y hueco · relevo |
| 1.2 | Una red, dos mundos | TN+NTN · eclipse · gateway congestionado · canal oculto |
| 1.3 | Gobernar no es controlar | tres eras · ritmo equivocado (ASTREA) · lazos O-RAN · políticas como software |
| 1.4 | Decidir sin verlo todo | MDP · POMDP · Dec-POMDP · el coste de descentralizar |
| **M2** | **Las herramientas** | |
| 2.1 | Aprender por refuerzo | recompensa · valor · explorar · curva real |
| 2.2 | Muchos agentes | no estacionariedad · CTDE · mezclador monótono · VDN no empeora |
| 2.3 | Consenso con traidores | 3f+1 · quórum · mensajes · reputación |
| 2.4 | La arquitectura PADA | cuatro módulos · cuello de botella · mapa O-RAN · políticas intercambiables |
| **M3** | **El corazón** | |
| 3.1 | El termómetro roto | estática vs adaptativa · política ciega · semillas · definición MA |
| 3.2 | Lo que el margen acota | tres clases · envolvente (Oliehoek 2008) · piso de falsabilidad · holgura sin cota |
| 3.3 | Medir sin engañarse | oráculo = cota inferior · exogeneidad · maldición del ganador · R5 |
| 3.4 | Lo que ya se encontró | 1.7 % → 31.8 % · G2b · compuertas · ¿sobrevive a la fidelidad? |

## 7bis. Mapa de piezas limpias (lote P, para el seminario y WITCOM)

Cada pieza = una idea, los pasos entre corchetes. Bloque = bloque del
`GUION_SEMINARIO_DIVULGACION.md` de la tesis.

| NN | pieza | qué se ve (sin texto) | pasos | cifras (fuente) | bloque |
|---|---|---|---|---|---|
| 01 | ritmo-orbital | órbita con satélite; lazo rápido girando; pulsos del consejero cada 15 min vs 1 por vuelta | [lazo] [15 min] [90 min] | +24.2 % / −66.2 % (ASTREA, gris) | 1 |
| 02 | escala | puntos que llenan el cielo; 2 de cada 3 de una sola constelación | [uno] [miles] [dos tercios] | 16 279 · 10 742 (dato público, gris) | 2 |
| 03 | ventana | tren de 2-3 satélites sobre la estación; cono que se abre y se cierra; hueco entre pases | [pase] [hueco] | AOS/TCA/LOS de `ntn.pase_leo` (calculado) | 1/2 |
| 04 | red-integrada | 2 satélites + gateway + ruta terrestre (topología de NTNEnv-v2); eclipse, congestión, canal oculto | [red] [eclipse] [congestión] [canal oculto] | parámetros del YAML (gris) | 4 |
| 05 | termometro | dos barras que "compiten"; aguja fija; la diferencia se disuelve | [dos] [aguja] [nada que medir] | — | 3 |
| 06 | politica-ciega | reloj + secuencia fija de acciones que ignora el mundo, y aun así puntúa | [mundo] [ciega] | (Ellis et al. 2023, gris) | 3 |
| 07 | margen | línea estática, techo privilegiado, la separación = MA | [estática] [privilegiada] [margen] | juego de juguete calculado | 4 |
| 08 | tres-clases | conjuntos anidados const ⊂ dec ⊂ priv y su orden de valores | [anidar] [ordenar] [MA_dec ≤ MA] | — | 4 |
| 09 | piso | MA = 0: toda política adaptativa queda bajo la estática | [margen cero] [ninguna gana] | calculado | 4 |
| 10 | holgura | juego de coordinación a ciegas: MA = m−1 crece, MA_dec = 0 | [m=2] [m crece] | exacto, calculado | 4 |
| 11 | ganador | 27 estáticas en pocos episodios: el máximo miente; converge con más | [1 ep] [30 ep] | 0.199→0.318 (tesis, `MA_SENSIBILIDAD.json`) | 5 |
| 12 | recorrido | termómetro vertical: v1 1.7 % bajo la raya del 25 %, v2 31.8 % encima | [umbral] [v1] [v2] | GATES G0/G1 (tesis) | 5 |
| 13 | g2b | por semilla: estática, QMIX, oráculo | [estática] [QMIX] [oráculo] | `G2B_RECUALIFICACION_v7.json` | 5 |
| 14 | guardia-r5 | el piloto mock sale 3× por encima del oráculo y se tacha | [oráculo] [piloto] [invalidado] | `G2B_PILOTO_GPU_v2.json` | 5 |
| 15 | pada | lazo P→A→D→A; lazo rápido dentro, lento fuera | [lazo] [dos ritmos] | — | 4 |
| 16 | ctde | entrenar viendo todo, ejecutar viendo lo propio | [entrenar] [ejecutar] | — | 4 |
| 17 | compuertas | G0…G4 como esclusas; G3 abierta a trazos | [G0-G2b] [G3 pendiente] | GATES.md | 5 |
| 18 | fidelidad | eje de realismo; el punto actual; lo que viene con "?" | [hoy] [¿sobrevive?] | 0.318 (tesis) | 6 |
| 19 | horizonte | línea 2026→2030: WITCOM, freeze 6G, defensa | [hoy] [2029] [2030] | fechas públicas (gris) | 6 |

**Ola P1** (seminario, lo irrenunciable): 03, 05, 07, 12, 13, 14, 15, 01.
**Ola P2**: 02, 04, 06, 08, 09, 10, 11, 16, 17, 18, 19.

Las dos piezas del PR #83 (`06-pase-ntn-seminario`, `07-pada-gemelo-digital`)
quedan **sustituidas** por 03 y 15; el PR #83 se cierra al entregar la ola P1.

## 8. Paleta por ROL

Las piezas usan la paleta del **deck** (`deck_common.js` de la tesis):
navy `0B1F3A`, azul `2E6F95`, ámbar `E8A33D` / `A96A12`, verde `3E8E7E`,
rojo `C1443C`, gris `5A6B7C`. Cada rol tiene variante para fondo oscuro y
claro; la sonda verifica contraste WCAG ≥ 4.5 en texto y ≥ 3 en trazo.

| rol | papel | semántica fija |
|---|---|---|
| `TINTA` | trazo y texto principal | — |
| `APOYO` | mobiliario, ejes, lo que "no se ve" | estado oculto, apagado |
| `ESTATICA` | gestión estática, best_static | siempre este color |
| `ADAPTA` (ámbar) | política adaptativa / aprendida | QMIX, heurística |
| `PRIV` (azul) | información privilegiada, oráculo | techo |
| `OK` (verde) | compuerta aprobada | — |
| `NO` (rojo) | invalidado, tachado | — |

En el curso CONSOLA rige la convención de la casa: cian = calculado aquí;
gris (`dato_pie`) = dado (literatura, resultados de la tesis no recalculados).

## 9. Contrato de la librería `manim_extensions/tesis6g.py`

Reutiliza: `presentacion.py` (lienzo, pasos), `ntn.py` (pase LEO, PBFT,
`margen_adaptativo`), `satelites.py`, `kepler.py`, `brillo.py`, `bloques.py`.

**Numérico (determinista, `default_rng`), con sonda `studio/tools/sonda_tesis6g.py`:**
- `juego_coordinacion(m)` → `V_est, V_dec, V_priv, MA, MA_dec` EXACTOS (§2.2
  del Teorema: MA = m−1, MA_dec = 0). Contraejemplo en la sonda: con
  observación informativa MA_dec = MA.
- `juego_coordinacion_ruidoso(m, eps, semilla)` → MA_dec interpola entre MA
  y 0 al perder observación (se mide por simulación y cierra contra lo exacto
  en los extremos).
- `maldicion_ganador(n_politicas, episodios, semilla)` → sesgo del máximo
  muestral; converge a 0 al crecer los episodios (contraejemplo: con una sola
  política no hay sesgo).
- `datos_tesis()` → lee `studio/content/datos/tesis-6g-privado/` (gitignored,
  lo llena `studio/tools/traer_datos_tesis.py`) y devuelve las cifras con
  su fichero de origen. Si falta, error claro. **Nunca** se transcribe una
  cifra de la tesis a mano.

**Dibujo (toma un `Paleta`, sirve para piezas y para curso):**
- `Paleta.de(lienzo)` → roles de §8 según el fondo.
- `etiqueta(texto, pal, fs)` → Carlito, guardián de ≤ 3 palabras en piezas.
- `barra_margen(...)`, `conjuntos_anidados(...)`, `termometro(...)`,
  `esclusas(...)`, `lazo_pada(...)`, `red_ntn(...)` — se escriben en la ola P1.

## 10. Lotes

| lote | contenido | aporta a la librería | estado |
|---|---|---|---|
| P1 | 8 piezas (ola P1) × 2 fondos + .pptx | paleta, etiqueta, datos, juego, margen, termómetro, lazo, barras | en curso |
| P2 | 11 piezas × 2 fondos + .pptx | conjuntos, esclusas, red, ganador | — |
| C1 | M1 (1.1–1.4) | style_block CONSOLA del curso | — |
| C2 | M2 (2.1–2.4) | — | — |
| C3 | M3 (3.1–3.4) | — | — |

## 11. Receta

Piezas: escribir `scene.py` → `empaquetar_presentacion.py <dir> --fondo
'#0B1F3A' --calidad ql` → mirar pósters y fragmentos uno a uno → igual con
`--fondo blanco` → `qh` de los dos → copiar `.pptx`/mp4 a
`exports/presentaciones/tesis-6g/`. Curso: los 10 pasos de la skill
`curso-de-video`.

**Datos privados**: el repo de contenido es **PÚBLICO** y el de la tesis
privado con licencia restrictiva. Los JSON de resultados de la tesis NO se
versionan aquí: viven en `studio/content/datos/tesis-6g-privado/`
(gitignored) y los copia `traer_datos_tesis.py`, que sí se versiona. Lo que
se publica es lo que se ve en pantalla (las cifras de la charla), igual que
en el seminario. Consecuencia: una pieza/clip que lea esos datos **sólo
renderiza en esta máquina**; en el VPS los `qh` se adoptan, no se renderizan.

## 12. Tablero

Piezas (ql revisado frame a frame en los dos fondos; qh = 1080p60):

| NN | escena | ola | ql navy | ql blanco | qh navy | qh blanco |
|---|---|---|---|---|---|---|
| 01 | ritmo-orbital | P1 | ✔ | ✔ | ✔ | ✔ |
| 02 | escala | P2 | ✔ | ✔ | ✔ | ✔ |
| 03 | ventana | P1 | ✔ | ✔ | ✔ | ✔ |
| 04 | red-integrada | P2 | ✔ | ✔ | ✔ | ✔ |
| 05 | termometro | P1 | ✔ | ✔ | ✔ | ✔ |
| 06 | politica-ciega | P2 | ✔ | ✔ | ✔ | ✔ |
| 07 | margen | P1 | ✔ | ✔ | ✔ | ✔ |
| 08 | tres-clases | P2 | ✔ | ✔ | ✔ | ✔ |
| 09 | piso | P2 | ✔ | ✔ | ✔ | ✔ |
| 10 | holgura | P2 | ✔ | ✔ | ✔ | ✔ |
| 11 | ganador | P2 | ✔ | ✔ | ✔ | ✔ |
| 12 | recorrido | P1 | ✔ | ✔ | ✔ | ✔ |
| 13 | g2b | P1 | ✔ | ✔ | ✔ | ✔ |
| 14 | guardia-r5 | P1 | ✔ | ✔ | ✔ | ✔ |
| 15 | pada | P1 | ✔ | ✔ | ✔ | ✔ |
| 16 | ctde | P2 | ✔ | ✔ | ✔ | ✔ |
| 17 | compuertas | P2 | ✔ | ✔ | ✔ | ✔ |
| 18 | fidelidad | P2 | ✔ | ✔ | ✔ | ✔ |
| 19 | horizonte | P2 | ✔ | ✔ | ✔ | ✔ |

Herramientas: render de una pieza con
`empaquetar_presentacion.py <dir> --fondo '#0B1F3A'|blanco --calidad ql|qh
--salida $PWD/render_jobs/validacion/tesis6g-piezas/<NN>/<fondo>-<calidad>`
(la salida TIENE que ser absoluta: docker toma una ruta relativa por nombre
de volumen). Entrega reunida con `studio/tools/deck_tesis6g.py`.

Curso: `plan · librería · clips · ql ✔ · PR · subida · qh · narrada · mux`.

| lección | plan | lib | clips | ql | PR | subida | qh | voz | mux |
|---|---|---|---|---|---|---|---|---|---|
| 1.1–3.4 (las 12) | ✔ | ✔ | ✔ | ✔ | #87 ✔ | ✔ | ✔ local, adopción pendiente | ✔ (edge local) | ✔ |

## 13. Storyboard del curso

Cada clip: lo que se ve · de dónde sale la cifra (lib = calculado aquí,
cian; dato = gris). El clip 4 cierra con dos líneas (la 2.ª en cian).
Las piezas marcadas → Pnn se reutilizan en su versión CONSOLA.

### M1 · El problema

**1.1 La red que se mueve** — por qué una red satelital no se puede fijar.
1. *Dieciséis mil satélites* — la malla de puntos (→P02) · dato McDowell 16 279 / 10 742.
2. *Un pase LEO* — vista lateral a escala, AOS/TCA/LOS · lib `ntn.pase_leo`: elev. máx 89.6°, 8.8 min.
3. *La red que se va* — la vista se aleja, la vuelta entera (→P03) · lib: 8.8 / 96.7 min = fracción de contacto.
4. *El relevo* — cascada de handover de un tren · lib `ntn.handover`: instantes de relevo y hueco. Cierre: "La red no esta siempre ahi." / "Se gobierna, no se fija."

**1.2 Una red, dos mundos** — la instancia de la tesis (NTNEnv-v2) sin llamarla así todavía.
1. *Satélite y tierra* — 2 satélites + gateway + ruta alterna (→P04 paso 1) · lib `ntn.retardo_ida_ms` cenit vs 10°.
2. *El eclipse* — visibilidad bajo 0.35 → throughput ×0.10 · dato YAML (gris).
3. *El gateway se llena* — ciclo de congestión de 45 pasos contra la órbita de 60: nunca coinciden igual · lib: mcm de los dos ciclos.
4. *El canal que no se ve* — rota cada 80 pasos, no observable; la interferencia lo delata · lib: ΔI = 0.75·0.7^t. Cierre: "Tres ritmos que no coinciden." / "Adaptarse puede pagar."

**1.3 Gobernar no es controlar**
1. *Tres eras* — manual → SON (Rel-16) → autónoma · dato (Cap 2 §2.1).
2. *El ritmo equivocado* — ASTREA (→P01) · dato arXiv:2509.13380.
3. *Dos lazos* — near-RT 10 ms–1 s dentro, non-RT > 1 s fuera · dato O-RAN.
4. *Políticas como software* — el mismo zócalo `PolicyFn` recibe estática, heurística o QMIX. Cierre: "Separar al que piensa" / "del que actua."

**1.4 Decidir sin verlo todo**
1. *El estado* — 10 dimensiones del estado contra 6 de cada observación · dato YAML.
2. *Creer sin ver* — actualización bayesiana de la creencia sobre el canal oculto · lib (Bayes de dos hipótesis).
3. *Tres que deciden* — 3 agentes × 3 acciones = 27 conjuntas · lib.
4. *El coste de descentralizar* — NEXP frente a P (Bernstein 2002) y el aviso: complejidad ≠ brecha de valor. Cierre: "Nadie ve el estado entero." / "Y hay que decidir igual."

### M2 · Las herramientas

**2.1 Aprender por refuerzo**
1. *La recompensa* — r = α·tp + β·lat − γ·intf · dato YAML.
2. *El valor* — Q-learning en un juguete de 3 acciones · lib.
3. *Explorar* — ε con decaimiento 0.999 · lib: episodios hasta ε = 0.05.
4. *La curva real* — recompensa de entrenamiento de la tesis (history_seed42) · dato tesis. Cierre.

**2.2 Muchos agentes**
1. *Perseguirse* — aprendices independientes: el entorno de cada uno cambia porque aprenden los otros · lib (juego de 2×2).
2. *Entrenar y ejecutar* — CTDE (→P16).
3. *Mezclar sin romper* — VDN (suma) frente a QMIX (monótona) · lib: superficies Q_tot.
4. *La complejidad no paga* — brazo VDN: +7.2/+5.0 y +6.8/+5.7 % en 2 de 3 semillas (la 44 sin política) · dato tesis. Cierre.

**2.3 Consenso con traidores**
1. *3f+1* — `ntn.quorum_pbft` · lib.
2. *Tres fases* — pre-prepare/prepare/commit, 2n(n−1) mensajes · lib `ntn.diagrama_pbft`.
3. *Por grupos* — 5G-PBFT con clústeres: mensajes contra n · lib.
4. *Quién manda* — líder por reputación. Cierre.

**2.4 La arquitectura PADA**
1. *Cuatro módulos* — el lazo (→P15 paso 1).
2. *Comprimir lo que se dice* — cuello de botella de información: curva compresión/relevancia · lib (gaussiano cerrado).
3. *El mapa O-RAN* — PADA sobre E2/A1/O1, xApp/rApp · dato COMPATIBILIDAD_PROTOCOLAR.
4. *Primero el gemelo* — (→P15 paso 3). Cierre.

### M3 · El corazón

**3.1 El termómetro roto** — 1 (→P05) · 2 (→P06) · 3 *Cinco semillas no bastan*: dos algoritmos iguales cuyo orden se invierte de 5 a 10 semillas · lib · 4 (→P07) + cierre.

**3.2 Lo que el margen acota** — 1 (→P08) · 2 *La envolvente ya existía*: Oliehoek, Spaan y Vlassis 2008, Q* ≤ Q_BG ≤ Q_POMDP ≤ Q_MDP · dato · 3 (→P09) · 4 (→P10) + cierre.

**3.3 Medir sin engañarse** — 1 *El oráculo no es el techo*: k=2 gana 0.03–0.77 % · dato `oraculo_k2.json` · 2 *La acción deja huella*: dos ramas desde el mismo estado, ‖ΔI‖ = 0.75·0.7^t · lib · 3 (→P11) · 4 (→P14) + cierre.

**3.4 Lo que ya se encontró** — 1 (→P12) · 2 (→P13) · 3 (→P17) · 4 (→P18 + P19). Cierre del curso: "Que gane o que pierda." / "Que la medicion signifique algo."

## 14. Cosecha heredada con más riesgo aquí

- Rajdhani < 22 px junta palabras (en piezas no se usa: Carlito).
- `Create` re-añade su mobject; `Transform` sólo entre gemelas.
- `set_opacity` enciende el relleno de polilíneas.
- El acento traslúcido sobre fondo oscuro se ensucia: áreas con trazo.
- Elegir el competidor débil miente sin dejar rastro: la estática es
  **la mejor** de las 27, el oráculo es **cota inferior** del óptimo.

## 15. Cosecha de este curso

Lote P (piezas), medida, no supuesta:

- **La sonda tumbó tres cosas antes de dibujar**: el ámbar oscuro del deck
  (`A96A12`) da 4.41:1 sobre blanco (no llega a 4.5) → `935B0A`; estática y
  privilegiada se confundían en claro (distancia RGB 54) → `575757`/`1D63A6`;
  y el brazo VDN **no** "no empeora en 3/3": la semilla 44 no encontró
  política adaptativa. Se dice 2/3.
- **Una lectura en vivo contradecía la cifra del pie** (clip 1.1.2): el
  dibujo es un pase exactamente cenital (90.0°) y `ntn.pase_leo` da 89.6°.
  Se quitó la lectura; la cifra del pie es la del pase real.
- **Semilla representativa, no afortunada**: la primera tirada de la
  maldición del ganador daba un sesgo de 1.2 frente a 9.5 de media. Se fija
  la semilla cuyo sesgo es el medio de 20 000 repeticiones.
- **Salida de `empaquetar_presentacion.py` en ruta ABSOLUTA**: con una
  relativa, docker la toma como nombre de volumen y aborta.
- **En el deck del seminario los slides de CONTENIDO son blancos** (título
  arriba, figura abajo) y los navy son separadores: la versión blanca es la
  de uso diario. Maqueta: `exports/presentaciones/tesis-6g/maqueta-en-tu-deck.png`.
- Las piezas no llevan marca de agua ni escuadras: sobre el slide no se ve
  el borde del vídeo (fondo idéntico al del slide).

Lote C (curso), medida:

- **La malla decide también aquí**: NTNEnv-v2 avanza en pasos enteros. El
  eclipse ocupa 25 de 60 pasos (41.7 %, no el 40.3 % de la fórmula
  continua) y el pico del gateway 14 de 45 (31.1 %, no 30 %). En pantalla,
  las cifras discretas: son las que vive el entorno.
- **VDN no tiene 3/3**: la semilla 44 del brazo 3 no encontró política
  adaptativa. Para comparar VDN con QMIX se usa la MEJOR evaluación greedy de
  la fase 0 (mismo protocolo en las dos) y se rotula así, porque es un máximo
  sobre puntos de control.
- **La heurística del rival importa** (compuerta G-H): la ingenua de umbral
  0.35 queda POR DEBAJO de la estática (7 718 < 9 504) y la afinada, de 270
  probadas, la supera por poco (+1.2 a +5.1 %). Es el clip 1.3.4.
- **Una demo de una semilla no es una demo**: los aprendices independientes
  «se persiguen» solo en algunas semillas. La cifra es la mediana de 1000
  (13-14 pasos contra 1 del aprendiz conjunto) y el dibujo es la semilla de
  la mediana (89).
- **Los números con espacios cuentan como palabras** en el guardián
  («1 998 000» son tres): se escribe `n=1000: 1 998 000` o se acorta el pie.
- **Mis duraciones salen cortas por sistema** (~4 s): lo que funcionó fue
  subir 1.5 s cada pausa de lectura de 1 s o más, no alargar al final.
- **Un clip de muchos `play` cortísimos dura MENOS en qh que en ql**: el
  redondeo a fotograma de 60 fps no es el de 30. 2.2.1 (40 celdas a 0.07 s)
  bajó de 29.1 a 26.8 s. Se deja 1.5 s de margen sobre el mínimo en ql.
- `set_opacity` sobre un grupo casilla+texto enciende el relleno y tapa el
  texto (clip 1.4.1): se apaga el trazo y el texto por separado.
- Un mapa de calor de Q_tot no distingue un mezclador monótono de la suma:
  los cortes a Q2 fija sí (la curva que BAJA delata al no monótono).

## 16. Hitos

- 2026-09-22 — exploración de la tesis, decisiones del dueño (12 lecciones,
  dos fondos, piezas primero, narrado sin subtítulos), plan.
- 2026-09-23 — **lote P entregado**: 19 piezas × 2 fondos en qh, sonda de
  66 invariantes en verde, decks combinados en
  `exports/presentaciones/tesis-6g/{navy,blanco}/piezas-*-{video,gif}.pptx`
  (56 slides cada uno). Molde del curso (1.1) en ql revisado. pytest 386 ✔.
- 2026-09-23 — **las 12 lecciones escritas y revisadas en ql** (48 clips,
  28–36 s), sonda de 120 invariantes; qh local en marcha.
- 2026-09-23 — PR #87 fusionado (6e8cb93); VPS en main y las 12 lecciones
  subidas a la base de producción. Voz sintetizada EN LOCAL con edge
  (es-MX-JorgeNeural, 48/48 dentro de su clip) y **12 montajes con intro y
  cierre en `exports/tesis6g-*/curso_narrado.mp4`**: 27.7 min, picos ≤ −0.9 dB,
  marca sonora −6.0 dB, sin atempo. **Adopción de los qh en el VPS
  PENDIENTE**: un `rsync -a` a `/root/` cambió el dueño de `/root` y bloqueó
  el SSH (ver trampas.md). Los qh ya están en `/root/staging-tesis6g-*/`;
  falta `python3 /root/adoptar_renders.py "Tesis 6G · N.M" /root/staging-<slug>`
  por lección cuando el dueño restaure `/root`.
