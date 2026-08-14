# Curso 12 — Caos: el orden escondido

- **Proyecto**: name `Caos: el orden escondido`, quality `qh`.
- **Fuente**: original (divulgación pura; tercer título de la línea visual
  Fractales → Matemáticas en la naturaleza).
- **Slug**: `caos-el-orden-escondido`.
- **Público**: divulgación general; el gancho ("el efecto mariposa") es de
  los más buscados de toda la divulgación matemática.
- **Hilo narrativo — la tesis**: determinismo no es predictibilidad. La
  promesa de Laplace (dame el presente y te doy el futuro) → la ecuación
  más simple del mundo (mapa logístico) → su cascada de duplicaciones y la
  constante universal de Feigenbaum → el atractor de Lorenz → el efecto
  mariposa medido (Lyapunov) → el péndulo doble (caos que puedes armar en
  tu escritorio) → el orden escondido (caos ≠ azar: el mapa de retorno
  delata la regla; ventanas de orden dentro del caos) → el horizonte de
  predicción (clima ~2 semanas, sistema solar ~5 millones de años) y el
  cierre de la tesis.

## Que NO entra (para no canibalizar cursos ya publicados)

- **Mandelbrot/Julia, zoom fractal, dimensión fractal como tema**: curso 1
  (Fractales). Aquí lo fractal solo se MENCIONA al ver la estructura del
  atractor (una frase, sin desarrollarlo).
- **Control de sistemas, retroalimentación, PID**: curso 11 (Control). El
  péndulo doble de aquí es libre, nunca controlado.
- **Predicción con IA / aprendizaje**: cursos 5-7.

## Honestidad (regla editorial del curso)

- El "horizonte del clima" (~2 semanas) es del sistema real; el exponente
  que MEDIMOS en pantalla es el del modelo de Lorenz (λ ≈ 0.9 por unidad
  de tiempo del modelo). No se mezclan: el clip lo dice explícito.
- El sistema solar es caótico con horizonte ~5 millones de años (Laskar):
  caos no significa que la Luna se caiga mañana.
- Todos los números rotulados (puntos de bifurcación, cocientes de
  Feigenbaum, pendiente de Lyapunov, divergencia de péndulos) salen de la
  librería, medidos o de constantes con cita.

## Paleta del curso

| Constante | Valor | Rol |
|-----------|-------|-----|
| `C_SISTEMA` | `#f59e0b` ámbar | el sistema: la trayectoria, la parábola, el péndulo |
| `C_GEMELO` | `#22d3ee` cian | el gemelo casi idéntico; la constante medida (δ, λ) |
| `C_ERROR` | `#f43f5e` rojo | el error que crece, la divergencia, lo impredecible |
| `C_ORDEN` | `#34d399` verde | el orden: equilibrios, ciclos, ventanas periódicas |
| `C_FASE` | `#a78bfa` violeta | el espacio de fases, el atractor como objeto, el ruido |
| `C_EJE` | `#31414f` | mobiliario (ejes, guías, diagonales) |

Regla de color: **ámbar es el sistema, cian su gemelo y lo que se mide,
rojo la separación entre ambos, verde el orden**. El efecto mariposa debe
poder leerse sin narración: dos trazas (ámbar/cian) y el rojo creciendo
entre ellas.

## Contrato de la librería `studio/content/manim_extensions/caos.py`

Determinista, sin red, sin disco. Núcleos numpy puros (integración RK4 y
mapas) separados de la capa Manim, como `naturaleza.py`. Localizadores
sobre geometría ACTUAL (anclas invisibles anti-`move_to`); imágenes RGBA
para el diagrama de bifurcación (técnica de `fractales.py`). Topes duros
con ValueError: `PASOS_MAX = 60_000`, `RES_BIF_MAX = 1600`,
`PENDULOS_MAX = 40`, `MUESTRAS_MAX = 600`, `PUNTOS_NUBE_MAX = 400`.

```python
# --- el mapa logistico ------------------------------------------------
orbita_logistica(r, x0=0.2, n=60)              # nucleo numpy
    # -> np.array de la orbita x_{k+1} = r x_k (1-x_k).
cobweb(r, x0=0.2, pasos=14, lado=4.2, color=C_SISTEMA)
    # -> Cobweb(VGroup): parabola r·x(1-x), diagonal y=x y la telaraña
    #    (vertical a la parabola, horizontal a la diagonal). Grupos
    #    .parabola, .diagonal, .telarana (VGroup por segmento, para
    #    LaggedStart). .con_r(r) -> nuevo Cobweb de la misma caja
    #    (Transform); .punto_fijo() -> float 1-1/r y .en(x, y) ->
    #    np.array (coordenadas de la caja, geometria actual).

# --- la cascada -------------------------------------------------------
imagen_bifurcacion(r=(2.8, 4.0), res=(1400, 800), burn=400, muestra=260,
                   color=C_SISTEMA, alto_escena=5.2)
    # -> ImageMobject del diagrama de bifurcacion por densidad (histograma
    #    2D, brillo log). Expone .punto_de(r, x) -> np.array leido de la
    #    geometria ACTUAL de la imagen (cierra sobre get_center/width) y
    #    .rango = (r_min, r_max). Con r=(3.82, 3.87) es el zoom a la
    #    ventana de periodo 3.
R_BIFURCACIONES = (3.0, 3.449490, 3.544090, 3.564407, 3.568759)
    # los r_n de las primeras duplicaciones (Feigenbaum 1978);
feigenbaum_cocientes()  # -> (4.751, 4.656, 4.668) medidos de esa tupla
FEIGENBAUM_DELTA = 4.669201...

# --- Lorenz -----------------------------------------------------------
trayectoria_lorenz(x0=(1, 1, 20), n=9000, dt=0.005)   # nucleo numpy RK4
    # -> np.array (n, 3); sigma=10, rho=28, beta=8/3.
curva_lorenz(pts, plano="xz", escala=..., color=C_SISTEMA)
    # -> CurvaLorenz(VMobject): proyeccion 2D del atractor centrada, con
    #    .punto(i) sobre la geometria actual. Create() la dibuja.
par_lorenz(eps=1e-6, n=9000)
    # -> (pts_a, pts_b, d) con d = ||a-b|| por paso: el par gemelo y su
    #    separacion, TODO de la misma integracion.
curva_separacion(d, dt=0.005, ancho=5.6, alto=2.6, color=C_ERROR)
    # -> CurvaSeparacion(VGroup): ejes (t ->, log10 d ^) con la curva de
    #    separacion; la recta que se le pega es el crecimiento
    #    exponencial. .lyapunov() -> float: pendiente ln medida por
    #    ajuste sobre el tramo lineal (~0.9). El numero del clip 5.

# --- el pendulo doble -------------------------------------------------
pendulo_doble(th1, th2, n=6000, dt=0.004)             # nucleo numpy RK4
    # -> np.array (n, 4): th1, w1, th2, w2 (m1=m2, l1=l2, g=9.8).
    #    Validacion: la energia deriva < 0.1 %.
PenduloDoble(VGroup)  # brazos + bolas + traza opcional del extremo
abanico_pendulos(cuantos=25, eps_deg=0.01, n, escala, colores=...)
    # -> Abanico(VGroup de PenduloDoble): `cuantos` pendulos con th2
    #    separados eps grados. .en(alpha) coloca TODOS los brazos en la
    #    fraccion alpha de la simulacion (para UpdateFromAlphaFunc: la
    #    escena "reproduce" el caos). .divergencia(alpha) -> float
    #    (dispersion angular medida, para rotular).

# --- caos no es azar --------------------------------------------------
mapa_retorno(serie, lado=3.4, color=C_SISTEMA, radio=0.028)
    # -> MapaRetorno(VGroup): nube de puntos (x_k, x_{k+1}) sobre caja
    #    con diagonal tenue. Con la orbita logistica r=4 dibuja la
    #    parabola perfecta; con `ruido_uniforme(n, semilla)` llena la
    #    caja: la regla delatada vs el azar de verdad. Tope 400 puntos.
ruido_uniforme(n, semilla=9)   # -> np.array uniforme [0,1], determinista
```

Demo obligatoria:
`studio/content/animations/experimentacion/23-caos.py` con
`DemoCaos(Scene)` (~15 s): cobweb r=2.9 → 3.5 → 3.9, imagen_bifurcacion
con dos puntos marcados, curva_lorenz dibujándose, par de Lorenz con
curva_separacion y su lyapunov rotulado, abanico de péndulos en
UpdateFromAlphaFunc, mapa_retorno caos vs ruido.

## Reglas duras para los clips

Idénticas a los cursos anteriores: solo `class ClipN(Scene)`; `Rotulos`
para todo texto narrativo; un fenómeno por clip; **28-45 s**;
determinismo; MathTex raw corto; solo paleta del curso; comentario
`# --- momento: ... ---` por beat; cada pie visible >= 5 s; **el pie
cambia ANTES del transform que ilustra**. Sin superíndices Unicode.
`set_stroke(opacity=)` para trazos (JAMÁS `set_opacity` sobre un trazo).
Piezas asimétricas (Lorenz, cobweb) se anclan por localizador, no por
`move_to` a ojo. Validación: `render_local.py <curso> --todos --frames 8`.

---

## Clip 1 · La promesa rota (~35 s)

**Intención**: plantear la tesis con la imagen más famosa del caos antes
de explicarla: el universo-relojería de Laplace y dos trayectorias
gemelas que se traicionan.

**Visual**: portada («Caos» / «el orden escondido»). Sale, entra HUD
`MODULO 01`. Cita de Laplace en pantalla (dos líneas, ámbar tenue):
conocer el presente = predecir el futuro. Detrás, el atractor de Lorenz
se dibuja lento en ámbar (Create parcial). Al cerrar, una segunda traza
cian arranca del MISMO punto (a 10⁻⁶) y durante un momento van juntas…
hasta separarse a ojos vista.

**Rótulos**
- Título: «La promesa rota»
- Pie 1: «1814: Laplace promete que conocer el presente es conocer el
  futuro.»
- Pie 2: «Dos mundos idénticos hasta la sexta cifra decimal…»
- Pie 3: «…y en minutos, dos futuros distintos. Este curso es sobre esa
  traición.»

**final_state**: atractor ámbar con la traza cian separándose de él y el
pie de la traición; HUD `MODULO 01`.

## Clip 2 · Una ecuación de nada (~38 s)

**Intención**: el caos no necesita ecuaciones monstruosas: la parábola
de los conejos basta.

**Visual**: fórmula `x_{n+1} = r·x_n(1−x_n)` arriba. `cobweb(r=2.9)`:
la telaraña converge en espiral al punto fijo verde (equilibrio).
Transform a r=3.3: la telaraña se abre en un cuadrado estable — ciclo de
2 (dos puntos verdes). Transform a r=3.9: la telaraña llena la caja sin
repetirse jamás (ámbar).

**Rótulos**
- Título: «Una ecuación de nada»
- Pie 1: «Una población de conejos: crecen si son pocos, se frenan si
  son muchos.»
- Pie 2: «Con r pequeño, la población se calma en un equilibrio.»
- Pie 3: «Sube r y la población oscila: un año muchos, un año pocos.»
- Pie 4: «Sube r un poco más… y no se repite nunca. Eso es el caos.»

**final_state**: telaraña densa llenando la caja con r = 3.9 rotulado y
la fórmula arriba; HUD `MODULO 02`.

## Clip 3 · La cascada (~40 s)

**Intención**: entre el orden y el caos no hay un salto: hay una
escalera de duplicaciones, y su ritmo es una constante universal.

**Visual**: `imagen_bifurcacion(2.8, 4.0)` aparece (FadeIn): EL
diagrama. Marcadores cian caen sobre r₁=3, r₂=3.4495, r₃=3.5441 (los
escalones se aprietan). Los cocientes aparecen a la derecha:
4.751 → 4.656 → 4.668 → δ = 4.669… (cian). Pie de universalidad.

**Rótulos**
- Título: «La cascada»
- Pie 1: «Un mapa de todos los destinos: cada columna es un valor de r.»
- Pie 2: «1 se vuelve 2, 2 se vuelve 4, 4 se vuelve 8… cada vez más
  rápido.»
- Fórmula: `\delta = 4.669\ldots`
- Pie 3: «Feigenbaum, 1978: ese ritmo es el mismo en cualquier sistema
  que se duplica. Una constante de la naturaleza.»

**final_state**: diagrama de bifurcación completo con tres marcadores
cian y δ = 4.669… a la derecha; HUD `MODULO 03`.

## Clip 4 · La mariposa (~36 s)

**Intención**: Lorenz 1963: doce ecuaciones del clima reducidas a tres,
y la trayectoria que nunca se repite y nunca se cruza.

**Visual**: las tres ecuaciones de Lorenz (MathTex chico, arriba
izquierda). `curva_lorenz` se dibuja con Create largo (~8 s): las dos
alas van apareciendo, la traza salta de una a otra sin patrón. Al final
la cámara del texto: «nunca se repite · nunca se corta» y el objeto se
rotula «atractor extraño» (violeta).

**Rótulos**
- Título: «La mariposa»
- Pie 1: «1963: Edward Lorenz destila el clima a tres ecuaciones de
  juguete.»
- Pie 2: «La trayectoria salta de un ala a la otra sin repetirse jamás.»
- Pie 3: «No es una curva: es un objeto — un atractor extraño.»

**final_state**: atractor completo ámbar con el rótulo violeta
«atractor extraño» y las ecuaciones arriba a la izquierda; HUD
`MODULO 04`.

## Clip 5 · El efecto mariposa, medido (~40 s)

**Intención**: la sensibilidad no es poesía: es una tasa. El error
crece exponencialmente y se puede medir la pendiente.

**Visual**: dos trayectorias (`par_lorenz(1e-6)`), ámbar y cian,
arrancan juntas sobre el atractor; el rojo de la separación va pintando
por debajo `curva_separacion` (log d contra t): una RECTA — crecimiento
exponencial. La recta de ajuste cian y su pendiente λ ≈ 0.9 (medida,
`.lyapunov()`). Cierre: cada Δt el error se multiplica; duplicar la
precisión inicial solo compra un ratito más.

**Rótulos**
- Título: «El efecto mariposa, medido»
- Pie 1: «Dos atmósferas separadas una millonésima. Míralas separarse.»
- Pie 2: «En escala logarítmica la separación es una recta: el error
  crece exponencialmente.»
- Fórmula: `d(t) \approx d_0\, e^{\lambda t}`
- Pie 3: «Diez veces más precisión no compra diez veces más futuro:
  compra un suspiro.»

**final_state**: atractor con las dos trazas separadas y debajo la
curva de separación con su recta y `λ ≈ 0.9` en cian; HUD `MODULO 05`.

## Clip 6 · El péndulo que enloquece (~38 s)

**Intención**: el caos no vive solo en ecuaciones: cuelga de dos barras
que puedes armar en tu escritorio.

**Visual**: un `PenduloDoble` grande reproduce su simulación
(UpdateFromAlphaFunc) con la traza del extremo dibujándose (violeta
tenue): garabato que no se repite. Después, `abanico_pendulos(25,
0.01°)`: veinticinco péndulos indistinguibles arrancan JUNTOS —
degradado ámbar→cian — y a mitad del clip el abanico revienta en todas
direcciones. Rótulo de la divergencia medida.

**Rótulos**
- Título: «El péndulo que enloquece»
- Pie 1: «Dos barras y dos tornillos: el sistema caótico más barato del
  mundo.»
- Pie 2: «Veinticinco péndulos separados una centésima de grado.»
- Pie 3: «Ningún sensor del planeta distingue sus arranques. El péndulo
  sí.»

**final_state**: abanico de péndulos abierto en todas direcciones con
sus trazas y el pie del sensor; HUD `MODULO 06`.

## Clip 7 · El orden escondido (~38 s)

**Intención**: caos NO es azar. La regla se esconde, pero se delata; y
dentro del caos hay islas de orden.

**Visual**: dos series de puntos saltando (arriba): una del mapa
logístico r=4 (ámbar), otra `ruido_uniforme` (violeta) —
indistinguibles a simple vista. Abajo, sus `mapa_retorno`: el caos
dibuja la parábola perfecta; el ruido llena la caja. Después, zoom a la
ventana de periodo 3: `imagen_bifurcacion(3.82, 3.87)` — en medio del
caos, tres líneas limpias (verde).

**Rótulos**
- Título: «El orden escondido»
- Pie 1: «Dos señales que saltan igual de locas. Una es azar; la otra,
  caos.»
- Pie 2: «Grafica cada valor contra el siguiente: el caos se delata —
  tenía una regla.»
- Pie 3: «Y dentro del caos hay islas: sube r y el desorden se vuelve,
  por un momento, un vals de tres pasos.»

**final_state**: los dos mapas de retorno abajo (parábola vs caja
llena) y el zoom de la ventana de periodo 3 a la derecha; HUD
`MODULO 07`.

## Clip 8 · El horizonte (~40 s)

**Intención**: cerrar la tesis: el caos no prohíbe predecir — pone
fecha de caducidad. Y saberlo es conocimiento, no derrota.

**Visual**: una barra de horizontes (escala log, mobiliario): el doble
péndulo (~segundos), el clima (~2 semanas), las órbitas del sistema
solar (~5 millones de años) — cada uno con su icono mínimo y su marca
cian. Pie del modelo vs realidad (honestidad). Desfile de miniaturas
del curso (cobweb, bifurcación, mariposa, péndulo, mapa de retorno).
Cierre a pantalla limpia en dos tiempos.

**Rótulos**
- Título: «El horizonte»
- Pie 1: «El caos no prohíbe predecir: pone fecha de caducidad.»
- Pie 2: «Segundos para un péndulo; dos semanas para el clima; cinco
  millones de años para las órbitas.»
- Pie 3: «Determinista no significa predecible.»
- Pie 4 (cierre, cian): «El caos es orden que no se deja predecir.»

**final_state**: cierre a pantalla limpia: «Determinista no significa
predecible.» sobre «El caos es orden que no se deja predecir.» en cian;
HUD `MODULO 08`.
