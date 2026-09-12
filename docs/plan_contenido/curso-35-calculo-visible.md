# Curso 35 · Calculo visible (VERTICAL 9:16, LIENZO, NARRADO)

**Encargo del 2026-09-12:**

> *"continuamos con otro curso igual en vertical, fondo liso, este sera de
> calculo, de las cosas mas visuales del calculo"*

"Igual" fija todo el formato sin preguntar nada: **vertical 9:16, estilo
LIENZO, sin numeracion en la esquina, portada con tesis de ≤ 5 palabras,
narrado desde el principio** (voz `es-MX-JorgeNeural` + cama de SFX) y
**20 piezas** (intro + 18 + cierre), que es el tamaño del 32, el 33 y el 34.

Y "las cosas mas visuales del calculo" fija el criterio de seleccion, que
es lo unico que habia que decidir: entra lo que se DEMUESTRA MIRANDO.

## 0. La capa que ocupa (la decision que mas importa)

El calculo toca cuatro cursos publicados. Sin una capa declarada, este
seria un refrito del 21:

| Curso | Capa | Que se queda alli |
|---|---|---|
| 21 · Calculo vectorial | el espacio que FLUYE | campos, gradiente, divergencia, rotacional, Green, Stokes, Maxwell |
| 26 · Fractales | autosemejanza y dimension | Koch, Julia, Mandelbrot, Newton en el plano complejo |
| 32 · Transformadas | como se cambia de dominio | Fourier y sus dieciocho parientes |
| 33 · Señales y sistemas | que le hace un sistema a una señal | impulso, convolucion, estabilidad |
| 34 · Funciones con nombre propio | la funcion como personaje | gamma, Bessel, Airy, Lorenz, la cicloide |
| **35 · Calculo visible** | **la idea de una variable, contada por el dibujo que la demuestra** | — |

El hilo: **cada pieza es una afirmacion del calculo cuya prueba se puede
MIRAR**, y termina en una cifra que el render calcula. No es un temario de
calculo I ordenado por capitulos: es el catalogo de sus demostraciones
visuales.

Consecuencias operativas, y hay que respetarlas pieza a pieza:

- **Una variable.** Nada de campos, gradientes ni operadores: eso es del
  21 y alli esta bien contado. La unica pieza que sale al plano es la
  campana (12), y sale para volver a entrar: gira la curva para poder
  integrarla en una sola variable, el radio.
- **El zoom se usa UNA sola vez** (pieza 03). El curso 34 zumbo cuatro
  veces sobre Weierstrass para enseñar la excepcion; aqui se zumba para
  enseñar la regla, y una sola vez, o el gesto se gasta.
- **Newton entra como METODO, no como fractal.** El curso 26 pinto sus
  cuencas en el plano complejo. Aqui es la tangente que te lleva a la
  raiz y la cifra es cuantos decimales ganas por paso.
- **Ninguna pieza enseña una formula como respuesta.** Si lo que se ve es
  una formula apareciendo, la pieza esta mal elegida.

## 1. El angulo: "esto se demuestra mirando"

Mismo reparto en tres del 32, el 33 y el 34, que es lo que permite que la
pantalla explique sola:

1. **La portada** dice el nombre y que vuelve facil (≤ 5 palabras).
2. **La animacion** lo demuestra con un solo verbo visual.
3. **La cifra** lo prueba, calculada por `calculo.py` en el render.

Y una regla propia: **la cifra tiene que ser la que cierra el argumento**,
no una medida cualquiera del dibujo. En la escalera no vale rotular
"1024 escalones": vale rotular que mide 4 y que la circunferencia mide
3.1416.

## 2. Las 20 piezas

Cifras **ya medidas** por `sonda_calculo.py` (**231 invariantes, 0
fallos**) antes de escribir un solo clip. La columna "cifra" es literal:
es lo que va a salir en pantalla.

| # | Pieza | Portada (tesis) | Verbo visual | Cifra |
|---|---|---|---|---|
| 00 | intro | — | Wordmark CO.DE + `CALCULO VISIBLE` | — |
| 01 | SECANTE | la pendiente de un instante | El segundo punto se acerca y la recta deja de girar | **1.0000** |
| 02 | EPSILON-DELTA | el limite sin trampas | Tu estrechas la banda de arriba, yo contesto con la de al lado | **0.0166** |
| 03 | RECTA ESCONDIDA | de cerca todo es recta | Cuatro zooms sobre el mismo punto: la curva se vuelve su tangente | **0.0043** (y entre 4) |
| 04 | NUMERO E | su pendiente es su altura | Cuatro tangentes, y las cuatro cortan el eje una unidad antes | **1.0000** / **2.7183** |
| 05 | VALOR MEDIO | el radar siempre te pilla | La cuerda del viaje baja paralela hasta tocar la curva | **87.5 km/h** |
| 06 | NEWTON | los decimales se duplican | Tangente, eje, subir, tangente: cuatro veces | **1 2 4 9 16** |
| 07 | LATA | gastar el minimo aluminio | La lata se estira y se achata; la curva del aluminio dibuja su valle | **264.4 cm2** |
| 08 | RIEMANN | el area se deja rellenar | Los rectangulos de dentro y los de fuera aprietan el numero | **0.3333** |
| 09 | TEOREMA FUNDAMENTAL | derivar deshace integrar | Arriba el area se llena, abajo la curva del area crece a esa altura | **2.1093 = 2.1093** |
| 10 | HIPERBOLA | convierte productos en sumas | La franja se estira al doble y se encoge a la mitad: no cambia | **0.6931** |
| 11 | ESCALERA | la longitud no se escalona | La escalera se pega a la circunferencia y su perimetro no baja | **4.0000** vs **3.1416** |
| 12 | CAMPANA | un area sin formula, exacta | La campana gira y se corta en anillos; el anillo si se integra | **3.1416** → **1.7725** |
| 13 | CAVALIERI | rebanada a rebanada | Una altura cualquiera: el circulo de la esfera y el del cono suman el del cilindro | **0.6667** |
| 14 | CEBOLLA | desenrollar para medir | Los anillos salen del circulo y se apilan en un triangulo | **78.5398** |
| 15 | ANILLO | manda el agujero | Dos esferas muy distintas con el mismo taladro dejan el mismo anillo | **113.10 cm3** |
| 16 | GABRIEL | se llena, no se pinta | La trompeta se llena de pintura y la pared no se acaba nunca | **3.1416** / **87.52** |
| 17 | TAYLOR | un polinomio que se pega | Grado a grado, el polinomio abraza el seno un poco mas lejos | **4.00** |
| 18 | ARMONICA | crece siempre, y despacio | Las columnas se apoyan en el area de la hiperbola y la pasan | **14.39** |
| 19 | cierre | — | Las curvas del curso se recogen en el punto ambar de CO.DE | — |

**El arco**, en cinco modulos de lectura (no se rotulan en pantalla, son
para escribir el curso):

- **01-04 · acercarse** — que pasa cuando dos puntos se juntan: la
  pendiente existe, el limite tiene reglas, la curva se vuelve recta y hay
  una curva que es su propia pendiente.
- **05-07 · lo que la derivada resuelve** — el radar, la raiz y la lata:
  tres cosas que solo se saben mirando donde la pendiente vale algo
  concreto.
- **08-12 · medir lo que no tiene formula** — area y longitud: rellenar,
  acumular, estirar sin perder, escalonar (y fallar), y girar para poder.
- **13-16 · cuerpos** — rebanar, desenrollar, taladrar y girar hasta el
  infinito.
- **17-18 · infinito controlado** — sumar infinitos terminos y que salga
  bien; sumar infinitos terminos y que no pare.

## 3. Contrato de la libreria

`studio/content/manim_extensions/calculo.py`, dos mitades como siempre.
**Ya escrita y validada.**

- **Numerica** (numpy puro, importable sin manim): cociente incremental,
  delta de la definicion de limite, despegue de la tangente, subtangente,
  viaje y valor medio, Newton con conteo de decimales, optimizacion de la
  lata, sumas de Riemann con su pinza, area acumulada por trapecios,
  areas de la hiperbola, escalera y poligono inscritos, longitud por la
  integral de arco, campana y sus anillos, rebanadas de Cavalieri, anillos
  del circulo, anillo de servilleta, trompeta de Gabriel, Taylor del seno
  con su alcance y la serie armonica.
- **De dibujo**: `marco_igual` (escala isotropa, para que un circulo salga
  redondo), `region`, `rectangulos_dibujados`, `banda`, `silueta_lata`,
  `anillos_concentricos`, `barras`, `tiras`, `circulo_en`, `segmento`.

**Se apoya en `especiales.py`** (curso 34) para el sustrato de dibujo del
estilo —`marco`, `curva`, `eje_x/eje_y` con guarda de cero, `recuadro`,
`marca_en`, `vertical`, `plomada`, `recortar`—, que no tiene nada de
funciones especiales y esta calibrado en 20 piezas. Duplicarlo aqui seria
mantener dos copias que se desincronizan; es lo mismo que hizo el curso 21
con `algebra_lineal.py`.

**Nada de scipy en la libreria.** Se usa **solo en la sonda, como
oraculo**: la libreria integra con trapecios y scipy con cuadratura
adaptativa, y que dos caminos que no se parecen en nada coincidan a 1e-10
es una prueba de verdad.

### Lo que la sonda tumbo antes de dibujar nada

Cuatro cosas, y ninguna se habria visto en un fotograma:

1. **La escalera medía la circunferencia, no 4.** Los tres cuadrantes que
   faltan salen de girar el primero, y yo los giraba *y* les daba la
   vuelta: el camino volvia sobre sus pasos y aparecian tramos en diagonal
   —que es justo lo que una escalera no tiene—. Medía 6.82, o sea 2π: la
   pieza habria "demostrado" lo contrario de lo que dice, con un dibujo
   que se ve perfecto.
2. **El anillo de servilleta tiene un techo numerico.** La corona es
   `(R^2 - y^2) - c^2`, la resta de dos numeros casi iguales. Con R = 1e6
   devuelve **113.0996** en vez de 113.0973: un numero creible, con dos
   decimales, que nadie discutiria. Con R de un planeta en centimetros da
   **cero**. `volumen_anillo` aborta por encima de 1e5 cm.
3. **La ventana del zoom no tocaba a su tangente.** Con malla par el
   centro no es ninguna muestra, y curva y tangente se cruzaban medio
   pixel al lado del punto del que habla la pieza. Malla impar. (Es la
   misma trampa que en el curso 34 dejo sin vertice a la parabola.)
4. **"Fallar un 10 % cuesta menos del 1 %" era falso**: cuesta 1.07 %. La
   idea —que cerca del minimo la curva es plana— es correcta y la cifra
   que la prueba es esa, no la que yo habia supuesto.

## 4. Lotes

| Lote | Piezas | Estado |
|------|--------|--------|
| A | 00 intro, 01 secante (MOLDE), 02, 03, 04 | **cerrado** |
| B | 05, 06, 07, 08, 09 | **cerrado** |
| C | 10, 11, 12, 13, 14 | **cerrado** |
| D | 15, 16, 17, 18, 19 cierre | **cerrado** |

**En serie, no por subagentes.** En el curso 34 la ola de cinco agentes
murio entera con un 429 de cuota de sesion sin dejar una linea en disco.
Aqui se escribieron las veinte a mano, a razon de ~8 min por pieza
incluyendo render de validacion y revision del fotograma.

## 5. Tablero de estado

| Paso | Estado |
|---|---|
| Libreria `calculo.py` | **hecha** |
| Sonda (231 invariantes, 0 fallos) | **hecha** |
| `curso.json` + `style_block.py` + esqueletos | **hecho** |
| Molde (pieza 01) escrito y validado | **hecho** |
| Lotes A-D (las 20 piezas) | **hecho**, 20/20 en `ql` |
| Guion de voz (97 frases) + SFX | **hecho** (huecos medidos con `sonda_tiempos_voz.py`) |
| Renders `qh` (1080x1920 @ 60) | **hechos**, 20/20 |
| Hoja de contactos de portadas + de interiores | **hechas**, sin defectos |
| Voz sintetizada y alineada (97 frases) | **hecha**, 0 solapes |
| Mux y verificacion (0 fallos, costuras 0.0000) | **hecho** |
| PR, catalogo, memoria | en curso |

## 6. Storyboard pieza a pieza

Lo que cada pieza tiene que ENSEÑAR, con las funciones de `calculo.py` que
lo calculan y la cifra literal.

### 00 · intro
Wordmark CO.DE + titulo en dos lineas (`CALCULO` / `VISIBLE`) y el gesto:
tres siluetas del curso en el mismo sitio, una detras de otra (la
escalera sobre la circunferencia, el triangulo de la cebolla, la campana).
Las tres las calcula la libreria.

### 01 · SECANTE — la pendiente de un instante (MOLDE)
La cubica `x^3-2x` y el punto x=1. Un segundo punto en x=2 y la recta que
los une: **5.00**. Se acerca a 1.5, a 1.25, a 1.1 — **2.75**, **1.81**,
**1.31** — y la recta deja de girar. Cifra **1.0000**. `f_cubica`,
`secante`, `pendientes_secantes`, `recta_por`.

### 02 · EPSILON-DELTA — el limite sin trampas
`x^2` cerca de x=3. Aparece una banda horizontal de 9 ± 1: yo contesto con
una vertical de 3 ± 0.1623 y la curva no se sale. La banda se estrecha a
±0.3, ±0.1: contesto **0.0499**, **0.0166**. Cifra **0.0166**. Remate: con
el doble de delta ya se sale. `delta_para`, `cumple_la_banda`, `banda`.

### 03 · RECTA ESCONDIDA — de cerca todo es recta
El seno en x=1 con su tangente. Cuatro ventanas: ±0.8, ±0.4, ±0.2, ±0.1. El
hueco entre las dos cae **0.2999 → 0.0721 → 0.0175 → 0.0043**, o sea se
divide **entre cuatro** cada vez que la ventana se parte por dos. Cifra
**0.0043**. `ventana`, `despegues`, `razon_de_despegue`.

### 04 · NUMERO E — su pendiente es su altura
`e^x` y cuatro tangentes en x = -0.5, 0.4, 1.2, 2.0. Las cuatro cortan el
eje **exactamente una unidad antes** del punto: la subtangente vale
**1.0000** siempre. Y por eso, en x=1, la pendiente es la altura:
**2.7183**. `subtangente`, `corte_de_tangente`, `tangente_exp`, `numero_e`.

### 05 · VALOR MEDIO — el radar siempre te pilla
Dos paneles: arriba la posicion del viaje (175 km en 2 h), abajo el
velocimetro. La cuerda de extremo a extremo tiene pendiente **87.5**; baja
paralela hasta tocar la curva, y toca en **dos** sitios: 0.42 h y 1.58 h.
Abajo, el velocimetro cruza los 87.5 en esos mismos dos instantes. Cifra
**87.5 km/h**. `posicion`, `velocidad`, `instantes_de_la_media`.

### 06 · NEWTON — los decimales se duplican
`x^3-2x-5`, el ejemplo del propio Newton. Desde x=2: tangente, bajar al
eje, subir a la curva, otra vez. Los decimales correctos van **1, 2, 4, 9,
16**: el ultimo paso no gana mas porque se acabo el float64, y eso se dice.
Cifra **16 decimales en 4 pasos**. `camino_newton`, `digitos_correctos`.

### 07 · LATA — gastar el minimo aluminio
330 ml. La lata se estira y se achata mientras un punto recorre la curva
del aluminio: el valle esta en **r=3.74, h=7.49** (la altura es el
diametro) y gasta **264.4 cm2**. Remate: la lata real gasta solo **3.2 %**
mas, y equivocarse un 10 % en el radio cuesta **1.07 %** — porque en el
minimo la curva es plana. `lata_optima`, `superficie_lata`,
`exceso_de_la_real`, `coste_de_fallar`, `silueta_lata`.

### 08 · RIEMANN — el area se deja rellenar
`x^2` entre 0 y 1. Rectangulos por dentro y por fuera: con 4 el area esta
entre **0.2188** y **0.4688**; con 16, entre **0.3027** y **0.3652**; con
128 la pinza mide 1/128. Cifra **0.3333**. `suma_riemann`, `pinza`,
`rectangulos`, `rectangulos_dibujados`.

### 09 · TEOREMA FUNDAMENTAL — derivar deshace integrar
Panel de arriba: `1.2 + sin x` y el area que se llena de izquierda a
derecha. Panel de abajo: la curva del area, creciendo. En x=2 la altura de
arriba es **2.1093** y la pendiente de abajo es **2.1093**. Se marca en
tres puntos. `area_acumulada`, `altura_y_ritmo`, `region`, `dos_dominios`.

### 10 · HIPERBOLA — convierte productos en sumas
El area bajo `1/x` de 1 a 2 vale **0.6931**. La franja se estira al doble
a lo ancho y se encoge a la mitad a lo alto: cae exactamente sobre la
hiperbola otra vez, entre 2 y 4, con la misma area. De 1 a 4 son
**1.3863**, o sea el doble: por eso ese area es un logaritmo.
`area_hiperbola`, `estirada`, `franjas_que_doblan`.

### 11 · ESCALERA — la longitud no se escalona
Una circunferencia de diametro 1 y una escalera que la envuelve. Se afina:
2, 8, 32, 256 escalones. Se pega tanto que ya no se distinguen — y su
perimetro sigue siendo **4.0000** en los cuatro casos. La circunferencia
mide **3.1416**. Un 27 % de diferencia que no se ve. Cifra **4.0000** →
**3.1416**. `escalera_circulo`, `longitud_poligonal`, `poligono_inscrito`,
`longitud_circunferencia`.

### 12 · CAMPANA — un area sin formula, exacta
`e^(-x^2)` y sus rectangulos: **1.7725**, medido pero sin formula. Entonces
la curva gira (anillos concentricos que pesan lo que pesa la campana) y el
volumen se corta en anillos: el anillo trae un factor r delante, y con ese
r la integral SI es elemental. Volumen **3.1416**; su raiz, **1.7725**.
`area_campana`, `anillo`, `volumen_campana`, `anillos_concentricos`.

### 13 · CAVALIERI — rebanada a rebanada
Media esfera, medio cono y medio cilindro en corte, con una altura que
sube. A cada altura, el circulo de la esfera y el del cono suman el del
cilindro — se enseña con las tres barras. Por eso la esfera es **0.6667**
del cilindro, y por eso vale **523.6** para R=5. `areas_rebanada`,
`volumen_esfera`, `razon_esfera_cilindro`, `circulo_en`.

### 14 · CEBOLLA — desenrollar para medir
Un circulo de radio 5 hecho de anillos. Los anillos salen y se apilan: sale
un **triangulo** de base 31.4159 y altura 5. Su area es **78.5398**, la del
circulo. Y explica de paso por que la derivada del area es el perimetro.
`anillos_circulo`, `area_por_tiras`, `tiras`, `derivada_del_area`.

### 15 · ANILLO — manda el agujero
Dos esferas, R=4 y R=9, taladradas de lado a lado dejando un anillo de
**6 cm** de alto. A cada altura, las dos coronas tienen la misma area; el
anillo mide **113.10 cm3** en las dos. Remate: y en una esfera de un
kilometro, lo mismo. `volumen_anillo`, `area_corona`, `radio_del_agujero`.

### 16 · GABRIEL — se llena, no se pinta
El perfil `1/x` girado, de 1 en adelante. El volumen se para en **3.1416**
por mucho que se alargue. La superficie a x=10^6 va por **87.52** y al
cuadrar el limite se DUPLICA: **174.32**. Se llena con pi de pintura y con
esa pintura no se puede pintar por dentro. `volumen_trompeta`,
`superficie_trompeta`, `perfil_trompeta`.

### 17 · TAYLOR — un polinomio que se pega
El seno y sus polinomios de grado 1, 3, 5, 7 y 11. Cada uno lo sigue mas
lejos: **0.39, 1.04, 1.76, 2.50, 4.00** (hasta donde el error se mantiene
por debajo de 0.01, que es un parametro ELEGIDO y va en gris). Cifra
**4.00**. `taylor_seno`, `alcance`, `alcances`, `error_taylor`.

### 18 · ARMONICA — crece siempre, y despacio
Columnas de altura 1/k apoyadas sobre la hiperbola: la suma va siempre por
encima del area y por debajo del area mas uno. Con un millon de sumandos
va por **14.3927**. Para pasar de 100 harian falta **1.5e43** terminos.
`bloques`, `sumas_parciales`, `encierra_al_logaritmo`, `terminos_para`.

### 19 · cierre
La escalera y su circunferencia se recogen en el punto ambar de CO.DE. La
marca no se posa encima del contenido: es el sitio al que el contenido
tiende.

## 7. Cierre (2026-09-12)

**Entregado.** `exports/verticales/calculo/`:

| | |
|---|---|
| Pelicula | `calculo_vertical.mp4`, **591.81 s (9.86 min)**, 1080x1920 @ 60 fps, 25 MB |
| Piezas sueltas | `piezas/*.mp4` — **las 20 sonorizadas**, que son EL producto para Instagram |
| Voz | `voz/*.wav` — 18 piezas, `es-MX-JorgeNeural` por `edge-tts` |
| Pico del montaje | **-2.0 dB** (ninguna pieza paso de -2.0; no hizo falta re-muxear) |
| Costuras | **19 a 0.0000/255**, igual que el 31, el 32, el 33 y el 34 |
| Verificacion | `verifica_vertical.py`: **0 fallos**, 63 avisos (todos de `estima()`) |
| Sonda | `sonda_calculo.py`: **231 invariantes, 0 fallos** |

**La voz volvio a entrar a la primera**: 97 frases escritas contra los huecos
MEDIDOS y a 2.2 palabras por segundo, y `alinear_voz.py` no devolvio ni un
solape ni una cola corta en las 18 piezas. La cola mas corta quedo en
**1.53 s** sobre un minimo de 0.8.

Los 63 avisos de `verifica_vertical` son los de siempre: `estima()` cuenta
palabras sobre el texto ANTES de sintetizar y no sabe que `alinear_voz.py`
ya coloco cada frase con su duracion real. Mismo ruido que el 32 (60), el
33 (90) y el 34 (53).

### La sonda de tiempos hay que correrla sobre el scene.py DE VERDAD

Y aqui casi se cuela un defecto de los que no se ven: las escenas se
copiaron al scratchpad **mientras** el render de validacion todavia estaba
recomponiendolas, asi que una pieza se midio con una version vieja. El
manifiesto decia 29.9 s y el render dio 30.5: `render_vertical` lo aviso
—"la voz se alinea con el manifiesto: cuadralos antes de narrar"— y se
volvio a medir todo. Tras la segunda medida, **las 18 piezas de contenido
coinciden al centesimo** con su render (0.00 de desfase) y las dos de marca
por 0.03, que es el redondeo a fotograma de 60 fps.

### Las dos hojas de contactos

- **Portadas**: los dieciocho nombres son sustantivos pelados, sin articulo
  —la leccion del curso 34, aplicada desde el principio— y las dieciocho
  tesis entran en cinco palabras. GABRIEL se queda como esta: es el nombre
  propio del objeto (la trompeta de Gabriel) y su tesis lo desambigua.
- **Interiores** (un fotograma al 62 % de cada pieza, sacado de la pelicula
  YA ENTREGADA): ninguna curva se sale de su cuadro, ningun rotulo cruza
  otro y todas las cifras corresponden a lo que se esta viendo. Es el
  chequeo que en el curso 34 destapo la resta de la catenaria.

## 8. Cosecha de trampas

Lo que este curso añade al catalogo de la casa.

### De la libreria y las cifras

1. **Girar un cuadrante Y darle la vuelta lo convierte en otra cosa.** La
   escalera que envuelve la circunferencia sale de repetir el primer
   cuadrante girado; al invertir tambien el orden de los puntos, el camino
   volvia sobre sus pasos y aparecian tramos en DIAGONAL. Medía 6.82 —o
   sea 2π, la circunferencia— en vez de 4: la pieza habria demostrado lo
   contrario de lo que dice, con un dibujo que se ve perfecto.
2. **Una resta de dos numeros gigantes miente antes de fallar.** La corona
   del anillo de servilleta es `(R^2 - y^2) - c^2`. Con R = 1e6 devuelve
   113.0996 en vez de 113.0973 —un numero creible, con dos decimales, que
   nadie discutiria— y con el radio de un planeta en centimetros devuelve
   CERO. El guardian no se pone donde sale cero: se pone donde empieza a
   desviarse.
3. **Una malla par no contiene su propio centro.** La ventana del zoom se
   dibujaba con 400 muestras y curva y tangente no llegaban a tocarse en
   el punto del que habla la pieza: se cruzaban medio pixel al lado. Es la
   misma trampa que en el curso 34 dejo sin vertice a la parabola.
4. **La cifra que uno espera no es la que sale.** "Fallar un 10 % en el
   radio de la lata cuesta menos del 1 %" era falso: cuesta 1.07 %. La
   idea —que en el minimo la curva es plana— era correcta, y la sonda
   obligo a rotular la cifra de verdad en vez de la que redondeaba bonito.

### De composicion

5. **`plomada` cuelga del CERO, y no todos los cuadros lo contienen.** En
   la curva de aluminio de la lata (de 250 a 322 cm2) esa plomada se iba
   siete unidades por debajo del dibujo: el grupo pasaba a medir el triple
   de lo que se ve, `encajar` lo encogia entero y el render abortaba por el
   guardian de LEGIBILIDAD, con "el rotulo mas pequeño mide 0.101". El
   sintoma no señalaba la causa. De ahi sale `colgante`, que cuelga del
   suelo del cuadro.
6. **Cuatro medidas iguales dibujadas sobre el mismo eje se sueldan en
   una sola raya.** Las cuatro subtangentes de e^x van de x0-1 a x0 con x0
   distinto: puestas todas sobre el eje formaban una barra ambar continua
   de tres unidades, y la pieza afirmaba que las cuatro miden lo mismo
   mientras enseñaba una raya larga. Cada una a su profundidad, con sus
   dos topes.
7. **El primer estado no puede estar entero a opacidad cero.** El guardian
   de la fraccion mide lo que se PINTA en el momento de encajar, asi que
   abrir con todo apagado para encenderlo despues aborta con "ocupa el
   0 %". La curva entra encendida, con el fundido del carril, y el `Create`
   se guarda para lo que de verdad es el gesto de la pieza.
8. **Un destino de `Transform` construido fuera del grupo llega
   descolocado.** `Transform(a, b)` lleva `a` a donde esta `b` AHORA, y `b`
   solo esta en su sitio si paso por `encajar` — o sea, si viajaba dentro
   del grupo. De ahi `soltar()`: los destinos viajan dentro con el trazo
   apagado y se sacan justo despues de `L.escena`. De propina, mientras
   estan dentro fijan el bounding box y el encaje no cambia de un estado a
   otro (lo mismo que hace `caja()`).
9. **El relleno no dice de que color es una banda.** El ambar al 13 % sobre
   este azul marino sale gris verdoso (ya medido en el curso 31): la banda
   de la respuesta y la de la tolerancia se veian iguales. El color lo pone
   el BORDE, que va opaco; el relleno solo dice "aqui dentro".
10. **Las etiquetas dentro del cuadro compiten con el mobiliario.** En la
    hiperbola, tres rotulos de franja se solapaban entre ellos porque la
    franja mide 0.72 unidades y el rotulo 1.4; en Taylor, el rotulo del
    tope de error lo cruzaba una vertical de referencia. Se quitan los
    rotulos (la etiqueta de la cifra ya nombra de que habla) o se acorta el
    mobiliario, nunca al reves.
11. **Un triangulo apilado hacia arriba se apoya donde no mide nada.** Las
    tiras desenrolladas del circulo salian con la punta abajo y la linea de
    la base —que es el perimetro— quedaba justo en el vertice. El rango
    vertical del marco va al reves.
12. **La etiqueta de la cifra tiene un tope real de unos 25 caracteres.**
    Tres piezas abortaron el render por frases de etiqueta que sonaban
    bien en el codigo ("arriba la altura, abajo la pendiente"). El guardian
    hace su trabajo; el sitio donde cabe la frase larga es la voz.

### De proceso

13. **`render_jobs` es un enlace al segundo disco y NO existe dentro del
    contenedor.** La sonda de tiempos de voz se corre sobre los `scene.py`
    compuestos, asi que hay que copiarlos al scratchpad y montarlo aparte.
    Sin eso, la sonda falla con `FileNotFoundError` sobre una ruta que en
    el host existe perfectamente.
14. **El guion de voz se escribe contra los huecos MEDIDOS y a 2.2 palabras
    por segundo.** Es la leccion del 34 aplicada desde el principio: el 33
    escribio a 2.5 (el promedio documentado) y cinco de dieciocho piezas
    fallaron al sintetizar de verdad.
