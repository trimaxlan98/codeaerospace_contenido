# Curso 11 — Matemáticas en la naturaleza

- **Proyecto**: name `Matemáticas en la naturaleza`, quality `qh`.
- **Fuente**: original (divulgación pura, como el curso 1 de fractales);
  toca de refilón la Academia (IA L2: crecimiento exponencial; Señales:
  nada — este curso no canibaliza ninguno publicado).
- **Slug**: `matematicas-en-la-naturaleza`.
- **Público**: divulgación general; es el curso más visual del canal
  desde Fractales, y su heredero directo (reutiliza la técnica de
  imágenes RGBA precomputadas de `fractales.py`).
- **Hilo narrativo — la tesis**: la naturaleza no "sabe" matemáticas:
  hace lo más barato, y las matemáticas son el idioma de lo que no
  desperdicia. Girasol (¿quién le enseñó a contar?) → el ángulo áureo
  como mejor reparto → φ y la espiral que crece sin cambiar de forma →
  fractales como instrucciones cortas repetidas → patrones de Turing
  (la química que pinta gatos) → π escondido en los ríos → e como
  ritmo del crecimiento continuo → el hexágono como mínimo material, y
  el cierre de la tesis.

## Que NO entra (para no canibalizar cursos ya publicados)

- **Mandelbrot, Julia, dimensión fractal, zoom infinito**: son el
  curso 1 (Fractales). Aquí los fractales son BIOLÓGICOS (helecho de
  Barnsley, árbol, micelio) y el énfasis es "instrucción corta,
  repetida", no la iteración compleja.
- **Gradientes, redes, aprendizaje**: curso 5. El crecimiento
  exponencial de aquí es poblacional, no de entrenamiento.

## Honestidad (regla editorial del curso)

Dos mitos se corrigen EN PANTALLA, no se repiten: (1) el nautilus
crece en espiral logarítmica pero NO en la espiral áurea — el mito es
bonito, la verdad es mejor; (2) la sinuosidad ~π de los ríos es un
promedio sobre meandros maduros (Stølum 1996), no una ley de cada
río. Turing se cuenta como hipótesis confirmada en pelajes modelo
(pez cebra, felinos) sin sobrevender.

## Paleta del curso

| Constante | Valor | Rol |
|-----------|-------|-----|
| `C_REGLA` | `#f59e0b` ámbar | la regla matemática: curvas, ángulos, teselas |
| `C_VIDA` | `#34d399` verde | lo vivo: semillas, helecho, ramas, micelio |
| `C_CONSTANTE` | `#22d3ee` cian | las constantes y resultados: φ, π, e, 137.5° |
| `C_MITO` | `#f43f5e` rojo | el desperdicio, el error, el mito |
| `C_QUIMICA` | `#a78bfa` violeta | la química que calcula: morfógenos, decaimiento |
| `C_EJE` | `#31414f` | mobiliario (ejes, guías, marcos) |

Regla de color, columna vertebral: **ámbar es la regla, verde lo
vivo, cian lo que la regla produce (la constante), rojo lo que la
naturaleza descarta**. El espectador debe leer "regla → vida →
constante" sin narración. No mezclar roles.

## Contrato de la librería `studio/content/manim_extensions/naturaleza.py`

Determinista, sin red, sin disco (`np.random.default_rng(semilla)`
donde hay azar: micelio, ruido inicial de Turing). Mismo estilo que
`enlace.py`: subclases de `VGroup`/`VMobject` con localizadores sobre
la geometría ACTUAL, y los NÚMEROS que se rotulan salen de la pieza
(`.sinuosidad()`, `.cociente(i)`, `.perimetro_por_area(n)`), nunca a
mano. Para los campos densos (helecho, Turing) reutiliza la técnica
RGBA→`ImageMobject` de `fractales.py` (bicúbico, `z_index` bajo la
marca de agua). Topes duros con `ValueError`: `SEMILLAS_MAX = 900`,
`HELECHO_PUNTOS_MAX = 400_000`, `RES_CAMPO_MAX = 360`,
`NIVELES_ARBOL_MAX = 8`, `MUESTRAS_MAX = 600`.

```python
# --- filotaxis: el reparto perfecto ----------------------------------
filotaxis(n=600, angulo_deg=137.5077, escala=2.6, color_centro, color_borde)
    # -> Filotaxis(VGroup de Dots): n semillas en r=c·√k, θ=k·ángulo,
    #    degradado radial centro→borde. .con_angulo(a) -> nueva pieza
    #    de la misma caja (Transform); .aparecer(run_time) ->
    #    LaggedStart de nacimiento (las semillas nacen del CENTRO,
    #    como en la planta); .parastica(m, color) -> VMobject que une
    #    las semillas k, k+m, k+2m… (las espirales visibles);
    #    .semilla(k) -> np.array. Atributo .angulo.

# --- φ y la espiral --------------------------------------------------
rectangulos_fibonacci(n=7, lado=0.32)
    # -> RectangulosFib(VGroup): cuadrados 1,1,2,3,5,8,13 en espiral
    #    con el arco de cuarto de círculo dentro de cada uno.
    #    .cuadro(i) -> VGroup, .arco(i), .aparecer(i) -> Animation.
    #    Números: FIB (tupla) y .cociente(i) -> float (F(i+1)/F(i)).
espiral_log(b=0.3063, vueltas=3.0, escala=1.0, color)
    # -> EspiralLog(VMobject): r = a·e^{bθ}. .punto_en(theta) ->
    #    np.array; .autosemejante(factor) -> (copia, angulo_rad):
    #    escalar por `factor` equivale a rotar `angulo` — LA
    #    demostración visual de la autosemejanza. b=ln(φ)/(π/2) es la
    #    áurea; el nautilus real ronda b≈0.18 (razón ~3.1 por vuelta,
    #    no φ por cuarto): `B_AUREA` y `B_NAUTILUS` exportadas.
gato_dormido(escala=1.0, color)
    # -> VMobject cerrado: silueta de gato enroscado (cabeza recostada
    #    sobre el cuerpo, cola envolviendo). Trazada para que una
    #    espiral_log(b≈0.35, ~1.9 vueltas) anclada en .ancla_espiral()
    #    siga el enrollado cuerpo→cola. Puro mobiliario narrativo.

# --- fractales biológicos --------------------------------------------
imagen_helecho(puntos=250_000, res=(720, 1080), color="#34d399", alto_escena)
    # -> ImageMobject del helecho de Barnsley (IFS de 4 mapas afines,
    #    chaos game determinista, brillo por densidad log). Con
    #    `puntos` chico (300, 3_000) la nube rala para animar la
    #    acumulación: mismos primeros puntos (misma semilla).
MAPAS_HELECHO  # tupla de 4 (matriz 2x2, traslacion, probabilidad)
arbol_fractal(niveles=7, angulo_deg=27, razon=0.72, escala)
    # -> ArbolFractal(VGroup): árbol binario; .nivel(i) -> VGroup de
    #    las ramas de esa generación (crecimiento por niveles);
    #    .con_angulo(a) -> nueva pieza (Transform). Tope 8 niveles.
red_micelio(radios=5, brotes=26, semilla=5, escala, color)
    # -> RedMicelio(VGroup): red de hifas creciendo radialmente con
    #    ramificación aleatoria determinista. .anillo(i) -> VGroup de
    #    la generación i (crecer con FadeIn/Create por anillos).

# --- Turing: la química que pinta ------------------------------------
campo_turing(f, k, pasos=3200, res=(288, 162), semilla=7)
    # -> np.ndarray float (res_y, res_x) en [0,1]: Gray-Scott con
    #    laplaciano por np.roll (frontera periódica), ruido inicial en
    #    un parche central. Presets: TURING_MANCHAS (f=.0367,k=.0649)
    #    y TURING_RAYAS (f=.0545,k=.0620). pasos*res acotados.
secuencia_turing(f, k, cuadros=8, pasos=3200, res, semilla)
    # -> lista de campos a tiempos crecientes (mismo estado inicial):
    #    el clip encadena imágenes para "ver" a la química calcular.
imagen_turing(campo, color_fondo="#05070a", color_tinta, alto_escena,
              silueta=None, escala_silueta=1.0)
    # -> ImageMobject; con `silueta` (VMobject cerrado) el campo solo
    #    pinta DENTRO (ray-casting numpy): un gato con el pelaje que
    #    la ecuación acaba de calcular. Alpha 0 fuera.
gato_sentado(escala=1.0, color)
    # -> VMobject cerrado: gato sentado de perfil (orejas, pecho,
    #    lomo, cola al frente). Sirve de silueta para imagen_turing y
    #    de contorno dibujado encima.

# --- π en el río ------------------------------------------------------
rio_meandro(omega_deg=90, ancho=9.0, muestras=420, color)
    # -> RioMeandro(VMobject): curva sine-generated de Langbein-
    #    Leopold θ(s)=ω·sin(2πs/L), el modelo canónico del meandro.
    #    .con_omega(w) -> nueva pieza de la misma caja (Transform);
    #    .sinuosidad() -> float MEDIDO sobre la propia curva (longitud
    #    de camino / distancia recta); .extremos() -> (A, B) para la
    #    cuerda. OMEGA_PI exportada: el ω cuya sinuosidad ≈ π (~110°).
onda_circular(radios, centro, color)
    # -> VGroup de círculos concéntricos punteados (gota en el agua).

# --- e: el ritmo de lo vivo ------------------------------------------
curva_crecimiento(tasa=1.0, t_max=3.0, ancho=5.6, alto=2.8, color)
    # -> CurvaCrecimiento(VGroup): ejes + e^{tasa·t}. .punto_en(t) ->
    #    np.array, .valor(t) -> float. Con tasa negativa, decaimiento.
escalera_compuesta(n, t_max=1.0, ...)
    # -> EscaleraCompuesta(VGroup): la poligonal de capitalizar en n
    #    saltos (interés compuesto discreto) sobre la misma caja que
    #    la curva continua. .valor_final() -> (1+1/n)^n. La sucesión
    #    2, 2.25, 2.44, 2.61, 2.71 → e es el gancho del clip.

# --- hexágonos: el mínimo material -----------------------------------
panal(filas=4, columnas=6, lado=0.42, color)
    # -> Panal(VGroup): retícula hexagonal. .celda(i) -> Polygon,
    #    .aparecer() -> LaggedStart. Con jitter (semilla) -> basalto.
tesela_unidad(n_lados, area=1.0, color)
    # -> Polygon regular de área EXACTA 1 (triángulo, cuadrado,
    #    hexágono: los únicos que teselan). perimetro_por_area(n) ->
    #    float: 4.559, 4.000, 3.722 — el número que gana el hexágono.
```

Demo obligatoria:
`studio/content/animations/experimentacion/22-naturaleza.py` con
`DemoNaturaleza(Scene)` (~15 s): filotaxis 90°→137.5° con una
parástica, rectángulos de Fibonacci + espiral áurea, helecho
acumulándose en 3 imágenes, árbol por niveles, campo de Turing
manchas→rayas, gato sentado con pelaje de Turing, río con ω
subiendo y su sinuosidad medida, escalera compuesta n=1→12 sobre la
curva e^t, y panal contra cuadrado con sus perímetros.

## Reglas duras para los clips

Idénticas a los cursos 01-09: solo `class ClipN(Scene)`; `Rotulos`
para todo texto narrativo; un fenómeno por clip; **28-45 s**;
determinismo; MathTex raw corto; solo paleta del curso; comentario
`# --- momento: ... ---` por beat; cada pie visible >= 5 s; **el pie
cambia ANTES del transform que ilustra**. Todo número rotulado sale
de la librería o del style_block (φ, 137.5077°, sinuosidad medida,
(1+1/n)^n, perímetros). Sin superíndices Unicode (Space Mono no los
trae). Validación: `studio/tools/render_local.py <curso> --todos
--frames 8`.

---

## Clip 1 · Nadie le enseñó a contar (~35 s)

**Intención**: plantear la pregunta del curso con la imagen más bella
que tenemos: un girasol naciendo semilla a semilla.

**Visual**: portada («Matemáticas en la naturaleza» / «el código que
crece»). Sale, entra HUD `MODULO 01`. Un disco de filotaxis nace del
centro (`.aparecer`), 600 semillas ámbar→verde. Dos parásticas se
dibujan encima en cian (una familia de 21, otra de 34). Los números
de Fibonacci cruzan la base: `1 1 2 3 5 8 13 21 34 55`, con 21 y 34
encendidos en cian.

**Rótulos**
- Título: «Nadie le enseñó a contar»
- Pie 1: «Un girasol acomoda sus semillas una a una, siempre con el
  mismo giro.»
- Pie 2: «Y de ese giro brotan espirales: 21 hacia un lado, 34 hacia
  el otro.»
- Pie 3: «Números que se persiguen en toda planta. Ese código es
  este curso.»

**final_state**: disco de filotaxis completo con dos parásticas cian
y la sucesión de Fibonacci abajo con 21 y 34 resaltados; HUD
`MODULO 01`.

## Clip 2 · El ángulo que no se repite (~40 s)

**Intención**: el experimento central del curso — el ángulo áureo no
es decoración: es el único reparto que no desperdicia.

**Visual**: el mismo generador con tres ángulos. `filotaxis(90°)`:
cuatro rayos, y las cuñas vacías se tiñen de rojo (desperdicio).
Transform a 120°: tres rayos, mismo problema. Transform a 137.5077°:
el disco se llena parejo y el rojo no tiene dónde vivir. Fórmula
`360°/φ² ≈ 137.5°` y el rótulo cian del ángulo.

**Rótulos**
- Título: «El ángulo que no se repite»
- Pie 1: «Si cada hoja saliera a 90° de la anterior, taparía a las de
  abajo: rayos y huecos.»
- Pie 2: «Cualquier fracción exacta de vuelta acaba repitiéndose.»
- Pie 3: «El ángulo áureo nunca cae en el mismo sitio: cada semilla
  hereda un lugar libre.»
- Fórmula: `360°/φ^2 \approx 137.5°`
- Pie 4: «La planta no lo eligió: lo que reparte mejor, sobrevive
  mejor.»

**final_state**: disco lleno con el ángulo `137.5°` rotulado en cian
y la fórmula en la zona de pie; HUD `MODULO 02`.

## Clip 3 · La espiral que no cambia de forma (~42 s)

**Intención**: φ como límite de Fibonacci y la espiral logarítmica
como la forma del crecimiento; el mito del nautilus, corregido.

**Visual**: cocientes `2/1, 3/2, 5/3, 8/5, 13/8 → 1.618…` (cian).
`rectangulos_fibonacci` se arma cuadro a cuadro con su espiral de
arcos. Transform a `espiral_log` áurea continua. Demostración de
autosemejanza: la copia escalada ×φ ROTA hasta calzar sobre sí misma.
Al lado, `gato_dormido` con la espiral abrazando el enrollado, y el
rótulo honesto del nautilus (b real ≈ 0.18: espiral logarítmica sí,
áurea no — en rojo el mito, en verde la verdad).

**Rótulos**
- Título: «La espiral que no cambia de forma»
- Pie 1: «Los cocientes de Fibonacci se acercan a un número que la
  geometría conocía: φ.»
- Pie 2: «Crecer multiplicando es girar: la espiral logarítmica es
  la firma del crecimiento.»
- Pie 3: «El nautilus dibuja una espiral logarítmica. La "espiral
  áurea" del póster es un mito.»
- Pie 4: «Un gato dormido también lo sabe: enroscarse igual a
  cualquier tamaño.»

**final_state**: espiral logarítmica ámbar al centro con la copia
autosemejante calzada, el gato enroscado a la derecha con su espiral
verde y `φ = 1.618…` en cian; HUD `MODULO 03`.

## Clip 4 · Instrucciones que se repiten (~38 s)

**Intención**: un fractal biológico no es una figura: es un programa
corto ejecutado muchas veces. Helecho, árbol, micelio.

**Visual**: cuatro reglas del helecho como marcos fantasma
(`MAPAS_HELECHO` dibujados como cuadriláteros tenues sobre la
silueta). El helecho se acumula: 300 puntos → 3 000 → 250 000
(relevo de imágenes, misma semilla). A la derecha crece
`arbol_fractal` nivel a nivel, y bajo él `red_micelio` anillo a
anillo (los hongos también). Tríptico final helecho·árbol·micelio.

**Rótulos**
- Título: «Instrucciones que se repiten»
- Pie 1: «Cuatro reglas de copiar, encoger y girar. Nada más.»
- Pie 2: «Punto a punto, el azar obedece y aparece el helecho.»
- Pie 3: «Un árbol es una rama que se repite; un hongo, una red que
  se reparte.»
- Pie 4: «El genoma no guarda el plano: guarda la instrucción.»

**final_state**: tríptico — helecho verde (imagen), árbol fractal y
red de micelio — con el pie de la instrucción; HUD `MODULO 04`.

## Clip 5 · Las rayas del gato (~42 s)

**Intención**: el clip estrella. Turing 1952: dos sustancias que se
persiguen pintan solas manchas y rayas — y el pelaje del gato es una
ecuación resuelta.

**Visual**: campo violeta uniforme con ruido central
(`secuencia_turing`): en 6 relevos de imagen el ruido se organiza en
MANCHAS (leopardo). HUD con los parámetros `F .0367 / k .0649`.
Cambian dos perillas → mismo proceso → RAYAS. Entra `gato_sentado`:
primero contorno, luego su interior se llena con el campo de rayas
(`imagen_turing(silueta=...)`) — el gato atigrado calculado. Al lado,
el mismo gato con manchas: misma ecuación, otro ajuste.

**Rótulos**
- Título: «Las rayas del gato»
- Pie 1: «1952: Alan Turing propone que dos químicos que se persiguen
  pueden pintar la piel.»
- Pie 2: «Uno activa, el otro frena: donde el freno no alcanza, nace
  una mancha.»
- Pie 3: «Dos perillas separan al leopardo de la cebra.»
- Pie 4: «Tu gato trae puesta la solución de una ecuación.»

**final_state**: dos gatos sentados frente a frente — uno atigrado
(rayas), uno moteado — con `F` y `k` rotulados entre ambos; HUD
`MODULO 05`.

## Clip 6 · π baja por el río (~34 s)

**Intención**: π aparece donde nadie lo invitó: en la sinuosidad
promedio de los ríos maduros. Con su caveat honesto.

**Visual**: `rio_meandro` casi recto (ω bajo); la cuerda cian
punteada une los extremos. El rótulo `sinuosidad = camino/recta`
marca `1.05`. El río serpentea (Transform con ω subiendo) y el
número — MEDIDO sobre la curva — sube: 1.6, 2.4… hasta ≈ 3.14. Cada
curva del meandro se abraza con un arco de circunferencia fantasma:
ahí es donde π se cuela. Cierre con `≈ π` en cian y el caveat.

**Rótulos**
- Título: «π baja por el río»
- Pie 1: «Un río joven va casi recto: camino y distancia miden casi
  lo mismo.»
- Pie 2: «Al envejecer, serpentea: cada curva es casi un arco de
  circunferencia.»
- Pie 3: «En promedio, sobre muchos ríos maduros, la sinuosidad
  ronda π. Promedio: ningún río está obligado.»

**final_state**: río muy sinuoso ámbar con su cuerda cian, arcos
fantasma sobre dos curvas y `sinuosidad ≈ π` en cian; HUD
`MODULO 06`.

## Clip 7 · El ritmo de lo vivo (~38 s)

**Intención**: e no es una letra rara: es lo que aparece cuando el
crecimiento no espera turno.

**Visual**: una colonia que se duplica por saltos:
`escalera_compuesta(n=1)` sobre los ejes (poligonal a saltos
anuales), valor final `2.00`. La escalera se refina: n=4 → `2.44`,
n=12 → `2.61`, n=52 → `2.69`… y la poligonal se pega a la curva
suave `curva_crecimiento` con el valor límite `e = 2.71828…` en
cian. Espejo rápido: con tasa negativa la misma curva decae (lo que
se enfría, lo que decae, también late con e).

**Rótulos**
- Título: «El ritmo de lo vivo»
- Pie 1: «Una bacteria no espera a fin de año para dividirse: crece a
  cada instante.»
- Pie 2: «Capitalizar más seguido rinde más… pero con un techo.»
- Fórmula: `\left(1+\tfrac{1}{n}\right)^n \to e`
- Pie 3: «Ese techo es e: el número del crecimiento continuo — y
  también del decaer.»

**final_state**: curva exponencial ámbar con la escalera n=52
pegada, `e = 2.71828…` en cian y la fórmula del límite en la zona de
pie; HUD `MODULO 07`.

## Clip 8 · El precio de la cera (~40 s)

**Intención**: cerrar donde la tesis se vuelve teorema: el hexágono
del panal es el mínimo material, y la naturaleza siempre cobra
barato. Recapitulación y cierre del curso.

**Visual**: tres teselas de ÁREA idéntica lado a lado — triángulo,
cuadrado, hexágono — con su perímetro medido debajo: `4.56`, `4.00`,
`3.72` (del helper, no a mano). El hexágono se enciende en ámbar y
tesela la pantalla (`panal().aparecer()`); nota Hales 1999. El panal
se vuelve piedra (jitter: basalto). Cierre: desfile de miniaturas
del curso (filotaxis, espiral, helecho, gato rayado, río, panal) y
el mensaje final en dos tiempos.

**Rótulos**
- Título: «El precio de la cera»
- Pie 1: «Misma área, tres formas: el hexágono usa menos pared que
  nadie.»
- Pie 2: «La abeja lo practicaba; Hales lo demostró en 1999.»
- Pie 3: «La naturaleza no sabe matemáticas: hace lo más barato.»
- Pie 4 (cierre, cian): «Matemáticas es el nombre que le pusimos a lo
  que no desperdicia.»

**final_state**: cierre a pantalla limpia: «La naturaleza no sabe
matemáticas.» sobre «Matemáticas es el nombre de lo que no
desperdicia.» en cian; HUD `MODULO 08`.
