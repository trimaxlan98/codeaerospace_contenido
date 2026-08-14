# Curso 17 · «Tsiolkovsky: la tiranía del cohete» (archivo curso-14)

> **Numeración**: los archivos `curso-NN-*.md` van por orden de creación;
> la numeración REAL la lleva `PLAN.md`. Este es el **curso 17**.

## Tesis

Un cohete es un 90 % combustible y solo un ~4 % llega a órbita — y no es
mala ingeniería: es un **logaritmo**. La ecuación de Tsiolkovsky
Δv = vₑ·ln(m₀/mf) convierte cada km/s extra en un MULTIPLICADOR de masa,
y con la química que tenemos el planeta nos cobra 9.4 km/s. Una sola
etapa ni siquiera cierra la cuenta (carga útil **negativa**); soltar masa
muerta en el camino es lo único que la salva. La tiranía no se derrota:
se negocia.

## Los números (todos calculados por la librería, jamás a mano)

| Cantidad | Valor | Fuente |
|---|---|---|
| v orbital a 200 km | **7.79 km/s** | √(GM/(R+h)) |
| Presupuesto a LEO | **9.4 km/s** | 7.79 + pérdidas por gravedad/arrastre (~1.6, cita) |
| vₑ RP-1/LOX | 3.0 km/s (Isp ≈ 306 s) | cita motores queroseno |
| vₑ química promedio | 3.5 km/s (Isp ≈ 357 s) | valor de trabajo del curso |
| vₑ hidrolox | 4.4 km/s | cita RL-10 |
| vₑ iónico | 30 km/s | cita propulsores de Hall/iones |
| m₀/mf a LEO con RP-1 | **23.0** (95.6 % propelente) | e^(Δv/vₑ) |
| m₀/mf con vₑ=3.5 | **14.7** (93.2 % propelente) | e^(Δv/vₑ) |
| m₀/mf con hidrolox | 8.5 (88.2 %) | e^(Δv/vₑ) |
| m₀/mf iónico | **1.4** (26.9 %) | e^(Δv/vₑ) |
| Carga útil SSTO (vₑ=3.5, ε=0.08) | **−1.29 %** (imposible) | modelo de etapas |
| Carga útil 2 etapas | **+3.87 %** | modelo de etapas |
| Carga útil 3 etapas | +4.55 % | modelo de etapas |
| Saturn V / Falcon 9 / Soyuz | 4.7 % / 4.2 % / 2.3 % | 140/2970, 22.8/549, 7.08/308 t (citas) |
| Retroceso del patinador | **0.769 m/s** | 5 kg a 10 m/s relativos; quedan 65 kg |

## Reglas de honestidad

- El **−1.29 %** del SSTO se muestra como barra NEGATIVA bajo el eje: la
  ecuación no da; no se suaviza. Con hidrolox el SSTO da +4.1 % pero sin
  margen: se menciona en pie, no se dibuja como salvación.
- El modelo de etapas es el clásico (ε estructural constante = 0.08,
  etapas de Δv igual); se rotula «modelo» y las barras de cohetes REALES
  van al lado con sus citas de masas.
- El cañón de Newton integra la balística real (RK4 en el campo 1/r²);
  las trayectorias son las calculadas, no dibujos. La montaña es alta
  para verse (se confiesa en pie).
- Las pérdidas por gravedad (~1.6 km/s) son cita, no cálculo nuestro: se
  rotulan como «pérdidas (cita)».
- El patinador conserva el momento de verdad (masa que decrece por
  lanzamiento); su retroceso 0.714 m/s sale de la cuenta.

## Paleta (regla semántica)

- `C_PROPELENTE` ámbar `#f59e0b` — lo que se quema: propelente, la llama.
- `C_CARGA` cian `#22d3ee` — lo que llega: la carga útil, lo medido.
- `C_TIERRA` verde `#34d399` — la Tierra, la órbita conquistada.
- `C_MUERTO` rojo `#f43f5e` — la masa muerta, lo imposible, el SSTO.
- `C_ESTRUCTURA` violeta `#a78bfa` — tanques, motores, la estructura.
- `C_EJE` gris azulado `#31414f` — mobiliario.

## Los 8 clips (28–45 s duros; pies ≥5 s; pie cambia ANTES del transform)

### 1 · Un tanque con alas de nada
La silueta del cohete a proporciones REALES: 93 % propelente (ámbar),
~7 % estructura (violeta) y una franja cian minúscula arriba: la carga.
Zoom/brace a la franja: «todo esto… para esto». Pregunta: ¿mala
ingeniería? No: matemáticas. Final: silueta + fracciones rotuladas.

### 2 · Empujar tirando masa
No hay nada contra qué empujar. El patinador en el hielo lanza masas y
retrocede (0.769 m/s al lanzar 5 kg a 10 m/s relativos): cada
lanzamiento un impulso, y cada bola sale un poco menos rápido que la
anterior porque el patinador ya se mueve. El cohete es un patinador que lanza su propio peso en gas a
3 km/s. Final: patinador + masas lanzadas + cifra de retroceso.

### 3 · La ecuación del portero
1903, Tsiolkovsky. Δv = vₑ·ln(m₀/mf) grande al centro; cada término se
ilumina con su tag: lo que quieres (Δv), lo que tu química da (vₑ), lo
que te cobra (m₀/mf). Es la única ecuación que decide quién sube.
Final: ecuación + los tres tags.

### 4 · El logaritmo tirano
La curva m₀/mf = e^(Δv/vₑ) con vₑ=3.5: suave al principio, vertical
después. Marcadores: 3 km/s (×2.4), 7.79 (órbita pura), 9.4 (LEO real
→ ×14.7). Cambia vₑ: con RP-1 ×23; con hidrolox ×8.5. Cada km/s extra
no SUMA cohete: lo MULTIPLICA. Final: curva + los tres marcadores.

### 5 · Orbitar es caer de lado
El cañón de Newton: desde la montaña, cada disparo más rápido cae más
lejos — hasta que a 7.79 km/s la caída ya no alcanza el suelo: órbita.
Trayectorias balísticas reales (RK4). El pie honesto: subir es fácil;
lo caro es correr de lado. Final: Tierra + abanico de trayectorias + la
órbita cerrada cian con su cifra.

### 6 · Etapas o nada
La cuenta completa con estructura (ε=0.08): una sola etapa → carga útil
**−1.29 %**: barra roja bajo el eje, IMPOSIBLE. Dos etapas (soltar el
tanque vacío a mitad de camino) → **+3.87 %**; tres → +4.55 %. Soltar
masa muerta es lo único que cierra la ecuación. Final: las tres barras
(roja negativa, cian, cian) + rótulo del modelo.

### 7 · La tiranía, confirmada
Los cohetes reales: barras de carga útil a LEO — Saturn V 4.7 %,
Falcon 9 4.2 %, Soyuz 2.3 % — con sus masas citadas. Sesenta años de
ingeniería distinta, la misma cuenta: nadie le gana al logaritmo por
fuerza bruta. Final: barras + cifras.

### 8 · Negociar con el tirano
La única variable libre: vₑ. Iónico: vₑ=30 km/s → m₀/mf = 1.4 (¡27 % de
propelente!)… pero empuje de gramos: sirve en el vacío, no para
despegar. Recapitulación en miniaturas (silueta, curva, cañón, barras).
Cierre: «La ecuación no se derrota: se negocia.» / «Cada gramo en órbita
la pagó en logaritmos.»

## Contrato de la librería `cohete.py`

Núcleos numpy puros y deterministas; capa Manim con localizadores sobre
geometría ACTUAL y anclas invisibles; números por funciones; topes duros
con ValueError.

Funciones: `delta_v(ve, m0, mf)`, `razon_masas(dv, ve)`,
`fraccion_propelente(dv, ve)`, `carga_util(dv, ve, eps, etapas)` (¡puede
ser negativa!), `v_orbital(h)`, `isp(ve)`, `retroceso(m_bola, v_bola,
m_total)`, constantes DV_LEO, VE_*, EPS_ESTRUCTURA, COHETES_REALES.

Piezas: `silueta_cohete` (contorno + zonas apiladas por fracción;
`.zona(nombre)`, `.con_fracciones`), `patinador` (hielo + patinador +
bolas; `.en(t)` reproducible por momento conservado), `curva_tirania`
(e^(Δv/vₑ); `.en(dv)`, `.con_ve`), `canon_newton` (Tierra + montaña +
`.trayectoria(v_frac)` balística RK4 que corta en el impacto; con
v_frac=1 cierra), `barras_carga` (barras con soporte de valores
NEGATIVOS bajo el eje; `.barra(i)`, `.tope(i)`), `llama_escape`
(partículas deterministas para el empuje).

## Producción

Igual que cursos 14–16: validación numérica/visual EN contenedor →
stubs de clips ANTES de paralelizar subagentes (trampa render_local) →
3 Opus (clips delegados) + Sonnet (demo 25-cohete.py) + clips finos
propios → render_local ql + frames → tests → PR (con PLAN.md) → qh
local 3 procesos → adoptar en VPS → guiones.py → mux local. Proyecto:
`studio/content/cursos/tsiolkovsky-la-tirania-del-cohete/`, qh.
