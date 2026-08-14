# Curso 16 · «Relatividad y el GPS» (archivo curso-13)

> **Nota de numeración**: los archivos `curso-NN-*.md` van por orden de
> creación del documento; la numeración REAL del curso la lleva `PLAN.md`.
> Este es el **curso 16** del catálogo (curso-10 es de Aerodinámica,
> curso-11 = curso 14 Naturaleza, curso-12 = curso 15 Caos).

## Tesis

Tu teléfono sabe dónde estás porque unos relojes en órbita miden el tiempo
con 9 cifras — y a esa precisión **el tiempo mismo deja de ser universal**.
La relatividad especial atrasa los relojes del GPS 7 µs al día; la general
los adelanta 46. Si los ingenieros no corrigieran los **+38.5 µs/día**
netos, tu posición se degradaría **11.5 km cada día**. El GPS es la prueba
cotidiana de que Einstein tenía razón **dos veces**.

## Los números (todos calculados por la librería, jamás a mano)

| Cantidad | Valor | Fuente |
|---|---|---|
| Radio orbital GPS | 26 560 km (T = 11 h 58 m) | semieje real de la constelación |
| v satélite | **3.874 km/s** | v = √(GM/r) |
| Deriva SR | **−7.21 µs/día** | −v²/2c² |
| Deriva GR | **+45.72 µs/día** | (GM/c²)(1/R⊕ − 1/r) |
| Neta | **+38.50 µs/día** | suma |
| Error de posición | **11.5 km/día** (≈481 m/hora) | c·Δt |
| Altura de empate SR=GR | **3 186 km** (r = 1.5 R⊕) | cruce por cero de la curva |
| ISS (420 km) | **−24.5 µs/día** (los astronautas envejecen menos) | misma curva |
| Reloj de fábrica | 10.23 MHz → **10.22999999544 MHz** | f·(1−4.457e−10) |
| 1 ns de reloj | **30 cm** de posición | c·1 ns |
| Muones (15 km, 0.995c, τ=2.2 µs) | clásico ~0 %, relativista **~10 %** llegan | γ = 10.0 |
| γ(0.5c) | 1.1547 | 1/√(1−β²) |

## Reglas de honestidad

- La trilateración se cuenta **en el plano** («en 2D para verlo; en el
  espacio son esferas y hace falta un 4º satélite para el sesgo del
  reloj»). Nada de fingir 3D.
- La deriva GR usa el modelo simple (potencial newtoniano, sin geoide ni
  rotación terrestre): +45.7 µs/día contra el ~+45.9 citado — se rotula lo
  que calculamos, no lo citado.
- El reloj de luz deriva γ con el zigzag REAL medido en pantalla (la
  hipotenusa se mide, no se declama).
- Los relojes visuales que laten a ritmo distinto van SIEMPRE con su cifra
  en µs/día al lado: la exageración visual se confiesa.
- Muones: los porcentajes salen de la exponencial integrada, y se dice que
  γ=10 corresponde a 0.995c (muones típicos de rayos cósmicos).

## Paleta (regla semántica)

- `C_LUZ` ámbar `#f59e0b` — la luz, los pulsos, los fotones del reloj.
- `C_SATELITE` cian `#22d3ee` — los satélites, sus relojes, lo medido.
- `C_TIERRA` verde `#34d399` — la Tierra, el receptor, lo que está abajo.
- `C_ERROR` rojo `#f43f5e` — el error que se acumula, la deriva ignorada.
- `C_GRAVEDAD` violeta `#a78bfa` — la gravedad, el pozo de potencial, GR.
- `C_EJE` gris azulado `#31414f` — mobiliario.

## Los 8 clips (28–45 s duros; pies ≥5 s; pie cambia ANTES del transform)

### 1 · Tu posición es un reloj
Un pin de mapa: «¿cómo sabe tu teléfono dónde está?» Arriba, un satélite
emite un pulso ámbar que viaja hasta el receptor: **distancia = c·Δt**.
El giro: c es enorme — equivocarse **1 ns son 30 cm**. Zoom al número.
Cierre: «El GPS no mide distancias. Mide tiempos.» Final: satélite, pulso
y la fórmula d = c·Δt en el pie.

### 2 · Tres relojes te encuentran
Trilateración en el plano: tres satélites, tres círculos verdes que se
estrechan hasta cortarse en TU punto. Luego la trampa: si tu reloj barato
va 1 µs mal, los tres radios crecen a la vez y los círculos **dejan de
cortarse en un punto** (triángulo de error rojo). Honestidad 2D en el pie.
Final: triángulo de error con la etiqueta «1 µs = 300 m».

### 3 · El reloj de luz
EL argumento visual del curso. Un reloj de luz en reposo: fotón que rebota
vertical, tic-tac. El mismo reloj a bordo del satélite en movimiento: el
fotón recorre un **zigzag más largo** — y como c es la misma, su tic dura
más. Se mide la hipotenusa en pantalla y aparece γ = 1/√(1−β²); curva de γ
contra β con el punto β=0.5 → 1.1547. «Un reloj que se mueve late más
despacio. No parece: ES.»

### 4 · La prueba que cae del cielo
Muones: nacen a 15 km, viven 2.2 µs — clásicamente ninguno debería tocar
el suelo (recorrerían ~660 m). Lluvia de puntos ámbar decayendo con dos
curvas: la clásica (roja, muere en nada) y la relativista con γ=10 (cian,
**~10 % llegan**). Los detectores en el suelo los cuentan de verdad.
«Cada muón que llega al suelo es un reloj que llegó tarde.»

### 5 · El reloj que vuela
Ahora el GPS de verdad: órbita a 26 560 km, T = 11 h 58 m, v = 3.874 km/s
calculada de v=√(GM/r). Relatividad especial aplicada: el reloj del
satélite pierde **−7.21 µs/día** contra el tuyo. Dos caritas de reloj
latiendo (exageradas, cifra al lado). Final: órbita + −7.21 µs/día.

### 6 · La gravedad también opina
Einstein 1915: los relojes **hondos en el pozo laten más despacio**. Pozo
de potencial violeta; tu reloj está al fondo, el satélite arriba: su reloj
adelanta **+45.72 µs/día**. La curva estrella: deriva neta contra altura,
que cruza por cero a **3 186 km** — la ISS por debajo (−24.5, los
astronautas envejecen menos), el GPS muy por encima (+38.5). Dos efectos,
signos opuestos, un empate a 1.5 radios terrestres.

### 7 · 38 microsegundos
El presupuesto: −7.21 + 45.72 = **+38.50 µs/día**. ¿Y si nadie corrigiera?
c·Δt: el pin de tu posición se difumina — **481 m en una hora, 11.5 km en
un día**; círculo de error rojo creciendo sobre el mapa con el contador de
horas. «En una semana, el GPS te ubicaría en otra ciudad.»

### 8 · El reloj fabricado lento
El final de ingeniería: antes de lanzar cada satélite, su reloj atómico se
**desafina a propósito**: 10.23 MHz → 10.22999999544 MHz, para que EN
ÓRBITA lata exacto. Pulsos de fábrica vs pulsos en órbita alineándose.
Recapitulación con miniaturas (zigzag, círculos, pozo, órbita). Cierre:
«El tiempo no es el mismo para todos.» / «Tu teléfono lo corrige a cada
segundo: Einstein tenía razón dos veces.»

## Contrato de la librería `relatividad.py`

Núcleos numpy puros y deterministas; capa Manim con localizadores sobre
geometría ACTUAL y anclas invisibles; números expuestos por funciones
(`derivas_gps()`, `altura_empate()`, `gamma(beta)`, `frac_muones()`,
`frecuencia_fabrica()`); topes duros con ValueError.

Piezas: `reloj_luz` (espejos + fotón; `.zigzag(beta)`, `.longitud_camino()`
medida), `curva_gamma` (γ vs β con `.punto_en(beta)`), `orbita_gps`
(Tierra + órbita + satélite; `.satelite(alpha)`, `.con_alpha`),
`trilateracion` (círculos + `.con_sesgo(dt)` que infla radios y devuelve
el triángulo de error medido), `lluvia_muones` (decaimiento por altura,
curvas clásica/relativista, `.frac(gamma)`), `pozo_potencial` (curva
1/r + relojes a alturas), `curva_deriva` (neta vs altura, `.altura_cero()`
MEDIDA sobre la curva, `.punto_de(r)`), `carita_reloj` (esfera + manecilla,
`.con_fase`, late por updater con tasa rotulada), `mapa_error` (pin +
círculo creciente, `.radio_km(horas)`), `tren_pulsos` (pulsos de fábrica
vs órbita para el clip 8).

## Producción

Igual que cursos 13–15: validación numérica/visual EN el contenedor con
PIL antes de clips → render_local ql + frames → tests → PR → qh locales
(3 procesos) → adoptar en VPS → guiones.py → mux local. Proyecto:
`studio/content/cursos/relatividad-y-el-gps/`, quality qh, HUD
«Modulo NN». Construido en worktree (checkout principal ocupado con
Aerodinámica).
