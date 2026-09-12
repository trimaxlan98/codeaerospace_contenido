# Curso 34 · Funciones con nombre propio (VERTICAL 9:16, LIENZO, NARRADO)

**Encargo del 2026-09-11:**

> *"Estan teniendo muy buena recepcion los reels, de fondo liso azul, en
> vertical, los ultimos a los que les hemos puesto voz y sonidos. Vamos a
> crear otro curso completo de esta manera, sera de funciones especiales, y
> llamativas, como el del caos de la mariposa, etc, analiza cuales estaria
> bien integrar y hazlo en este curso."*

Lo que fija el encargo sin preguntar nada: **vertical 9:16, estilo LIENZO,
sin numeracion en la esquina, portada con tesis de ≤ 5 palabras**, y —esto
es lo nuevo respecto al 32 y al 33— **NARRADO DESDE EL PRINCIPIO**: voz
`es-MX-JorgeNeural` + cama de SFX, no un curso mudo al que se le añade audio
despues. Confirmado con el dueño antes de escribir nada: **20 piezas**
(intro + 18 + cierre) y el reparto de la seccion 2.

**El ritmo sigue siendo el del curso mudo** (`leer()` no baja de 1.8 s) y no
es una inercia: el 32 y el 33 demostraron que ese silencio pausado deja
sitio de sobra para una voz que PUNTUA en vez de narrar de corrido, y que es
lo que hace que cada pieza funcione tambien sin sonido, que es como la mitad
de Instagram las ve.

## 0. La capa que ocupa (la decision que mas importa)

"Funciones llamativas" toca cuatro cursos publicados. Sin una capa declarada,
este curso seria un refrito:

| Curso | Capa | Que se queda alli |
|---|---|---|
| 11 · Matematicas en la naturaleza | que patron sale de repetir una regla | Fibonacci, angulo aureo, Turing, Gray-Scott |
| 12 · Caos | cuando la iteracion deja de ser predecible | mapa logistico, bifurcaciones, Lyapunov, pendulo doble |
| 26 · Fractales (vertical) | autosemejanza y dimension | Koch, Julia, Mandelbrot, conteo de cajas |
| 32 · Transformadas | como se cambia de dominio | Fourier y sus dieciocho parientes |
| 33 · Señales y sistemas | que le hace un sistema a una señal | impulso, convolucion, estabilidad |
| **34 · Funciones con nombre propio** | **la funcion COMO PERSONAJE** | — |

El hilo: **una funcion tiene nombre propio porque ninguna combinacion de las
elementales hacia su trabajo.** Cada pieza presenta una, con el problema que
la obligo a existir y **una cifra que solo ella sabe dar**.

Consecuencias operativas de esa capa, y hay que respetarlas pieza a pieza:

- **La mariposa de Lorenz entra, pero no como caos.** El curso 12 conto el
  efecto mariposa y el 26 midio la dimension de su traza. Aqui es *el
  atractor como objeto*: una curva que no se corta nunca a si misma. La
  cifra no es la dimension ni el exponente de Lyapunov (esas son de los
  otros dos cursos): es **cuanto tarda** una diferencia de mil millonesima
  en hacerse del tamaño del dibujo.
- **Nada de dimension fractal en ninguna pieza.** Weierstrass y Cantor se
  cuentan por lo que le pasa a la PENDIENTE y a la SUBIDA, no por su
  dimension: eso ya lo hizo el 26 tres veces.
- **Las transformadas se citan y no se explican** (Bessel aparece en la FM,
  zeta en los primos), igual que hacia el 33.

## 1. El angulo: "la funcion que hubo que inventar"

Mismo reparto en tres del 32 y el 33, que es lo que permite que la pantalla
explique sola:

1. **La portada** dice el nombre y que vuelve facil (≤ 5 palabras).
2. **La animacion** lo demuestra con un solo verbo visual.
3. **La cifra** lo prueba, calculada por `especiales.py` en el render.

Y una regla propia de este curso: **cada pieza enseña la funcion HACIENDO
algo, no su grafica.** Una curva bonita con su nombre debajo no es una
pieza; un pendulo que se retrasa, una placa que dibuja con arena, tres
cuentas que caen por tres curvas, si.

## 2. Las 20 piezas

Cifras **ya medidas** por `sonda_especiales.py` (155 invariantes, 0 fallos)
antes de escribir un solo clip. La columna "cifra" es literal: es lo que va
a salir en pantalla.

| # | Pieza | Portada (tesis) | Verbo visual | Cifra |
|---|---|---|---|---|
| 00 | intro | — | Wordmark CO.DE + `FUNCIONES CON NOMBRE PROPIO` | — |
| 01 | GAMMA | el factorial sin escalones | Los puntos de n! y una curva que los enhebra; y sigue por donde no hay factoriales | **1.7725** = Γ(½) |
| 02 | LAMBERT | el despeje imposible | La telaraña de x → e^-x cayendo al unico punto fijo | **0.5671** |
| 03 | LA ELIPTICA | el pendulo real, medido | Dos pendulos sueltos a la vez, uno a 10° y otro a 90°: se descuelgan | **18.03 %** de mas |
| 04 | FRESNEL | girar sin dar un tiron | Un punto recorre la clotoide; su curvatura sube como una recta | **0.5000** (el ojo) |
| 05 | CHEBYSHEV | el error repartido por igual | El mismo grado 20 con nodos repartidos (estalla) y con los suyos | **59.82 → 0.0177** |
| 06 | BESSEL | el tambor no da notas | El modo de una membrana redonda y su circulo quieto | **2.4048** |
| 07 | CHLADNI | el sonido dibuja | La arena huye de donde vibra y dibuja la figura de la placa | **3** lineas nodales |
| 08 | AIRY | el borde de la sombra | El escalon de luz que la optica promete, y las franjas que salen | **-2.3381** |
| 09 | LEGENDRE | la Tierra no es esfera | Una circunferencia deformada por P2, P3, P4: las capas de un planeta | **21.4 km** |
| 10 | CATENARIA | la cadena no es parabola | Cadena y parabola con los mismos extremos, superpuestas | **20.94 %** de cable |
| 11 | WEIERSTRASS | continua y sin pendiente | Cuatro zooms seguidos: nunca se alisa | **16936** |
| 12 | CANTOR | sube sin subir nunca | El peine se va comiendo el segmento y la escalera crece | **99.23 %** plano |
| 13 | CAUCHY | la campana sin media | Dos medias corriendo: una se asienta, la otra salta siempre | **0.282** |
| 14 | LORENZ | nunca pasa dos veces | La mariposa se dibuja de un trazo y dos trayectorias se separan | **19.44 s** |
| 15 | CICLOIDE | el camino mas rapido | Tres cuentas caen a la vez por recta, arco y cicloide | **0.8053 s** |
| 16 | LISSAJOUS | dos senos en angulo recto | La figura se cierra y se cuentan los toques en el lado y el techo | **3:2** |
| 17 | ZETA | los primos tienen musica | La curva de la recta critica pasa exactamente por el origen | **14.1347** |
| 18 | SUPERFORMULA | una formula, mil formas | Cuatro numeros cambian y la forma se vuelve estrella, flor, diatomea | **12** lobulos |
| 19 | cierre | — | Las curvas del curso se recogen en el punto ambar de CO.DE | — |

**El arco**, en cuatro modulos de lectura (no se rotulan en pantalla, son
para escribir el curso):

- **01-05 · las que hubo que inventar** — alguien pidio algo que las
  elementales no sabian hacer: interpolar el factorial, despejar x·e^x,
  el periodo de verdad, curvar sin tirones, repartir el error.
- **06-10 · las que dibujan la fisica** — la funcion es la forma que toma
  algo real: un tambor, una placa, el borde de una sombra, un planeta, un
  cable.
- **11-14 · los monstruos** — las que se inventaron para demostrar que la
  intuicion miente: sin derivada, sin subida, sin media, sin repeticion.
- **15-18 · las que resuelven un oficio** — bajar rapido, leer una razon de
  frecuencias en una pantalla, contar primos, resumir mil formas.

## 3. Contrato de la libreria

`studio/content/manim_extensions/especiales.py`, dos mitades como siempre.
**Ya escrita y validada.**

- **Numerica** (numpy puro, importable sin manim): gamma de Lanczos, W de
  Lambert por Halley, K por la media aritmetico-geometrica, Fresnel por
  trapecio acumulado, interpolacion baricentrica, J_n por la integral de
  Bessel, Ai por su serie, P_l por Bonnet, catenaria por biseccion,
  Weierstrass, escalera de Cantor exacta, Cauchy y Gauss con semilla,
  Lorenz por RK4, braquistocrona por biseccion + integral impropia,
  Lissajous, zeta por Borwein y la superformula de Gielis.
- **De dibujo**: `marco()` (la regla de tres datos → escena que comparten
  TODAS las piezas), `curva`, `polar`, `nube`, `campo_signo`, `eje_x/eje_y`
  con guarda de cero, `vertical`, `marca_en`, `ritmo_fisico`.

**Nada de scipy en la libreria**, aunque la imagen lo traiga como
dependencia de manim: lo que se dibuja tiene que salir de codigo que se
pueda leer y explicar. scipy se usa **solo en la sonda, como oraculo**: dos
implementaciones independientes que coinciden a 1e-10 es una prueba de
verdad.

Sonda: `studio/tools/sonda_especiales.py` — **155 invariantes, 0 fallos**.
Cada funcion tiene que cumplir la propiedad que solo cumple si esta bien
(la reflexion de Euler, la recurrencia de Bessel, `Ai'' = x·Ai`, la
ortogonalidad de Legendre, el periodo medido sobre un pendulo integrado de
verdad) **y su contraejemplo**.

### Lo que la sonda tumbo antes de dibujar nada

Siete cosas, y ninguna se habria visto en un fotograma:

1. **La escalera de Cantor por expansion en base 3 no es monotona.** Con
   flotantes, `v = v*3 - d` acumula error: la escalera BAJABA en 41 sitios y
   en x=1 devolvia 0 en vez de 1. Se reescribio desde la definicion
   geometrica (los 2^n intervalos supervivientes), que ademas es la que se
   dibuja.
2. **El arco de circunferencia de la carrera tardaba 4.11 s**, cinco veces
   la cicloide: por los dos mismos puntos pasan infinitas circunferencias y
   yo habia elegido la tangente a la HORIZONTAL, que sale del reposo sin
   pendiente. La honrada es la de Galileo, tangente a la vertical: **0.8229
   s contra 0.8053 s**. Que pierda por poco es justo lo que hace buena la
   pieza; con la otra, la comparacion habria sido un espantapajaros.
3. **Contar lobulos comparando cada muestra con sus vecinas da una de
   menos** cuando el maximo cae entre dos muestras: m=6 contaba 5 y m=12
   contaba 11. Se cuenta por el cambio de signo de la PENDIENTE, con
   envoltura y arrastrando las mesetas.
4. **Lo mismo en el osciloscopio**: `linspace` repite el punto final, y en
   3:2 ese punto es un maximo — la razon se leia 4:2, que no es ninguna
   razon.
5. **P_l impar perdia un cero** porque x=0 caia exactamente en una muestra y
   el producto de signos daba 0 en vez de negativo. Malla de numero par.
6. **La parabola no tenia la flecha que decia** (1e-6 corta) porque con un
   numero par de muestras el vertice no cae en ninguna.
7. **La ventana de medida del pendulo era mas corta que su periodo** a 150°,
   y `periodo_medido` devolvia `nan`. El banco de pruebas estaba mal, no K.

## 4. Lotes

| Lote | Piezas | Estado |
|------|--------|--------|
| A | 00 intro, 01 gamma (MOLDE), 02, 03, 04 | **cerrado** |
| B | 05, 06, 07, 08, 09 | **cerrado** |
| C | 10, 11, 12, 13, 14 | **cerrado** |
| D | 15, 16, 17, 18, 19 cierre | **cerrado** |

**Las 20 escritas y revisadas fotograma a fotograma.** El reparto por
subagentes se intento y NO salio: los cinco agentes de la primera ola
murieron a la vez con un 429 de cuota de sesion, cada uno a mitad de la
lectura de contexto y sin haber escrito una linea. Las veinte piezas se
escribieron en serie en la sesion principal. La leccion no es nueva
—esta en el catalogo de trampas desde el curso 22— pero si su tamaño:
**una ola de cinco agentes puede agotar la cuota antes de producir
nada**, y el trabajo parcial que deja en disco es cero, no la mitad.

## 5. Tablero de estado

| Paso | Estado |
|---|---|
| Imagen de render reconstruida (bullseye EOL + pines) | **hecho** |
| Libreria `especiales.py` | **hecha** |
| Sonda (155 invariantes, 0 fallos) | **hecha** |
| Portadas medidas (19/19 entran) | **hecho** |
| `curso.json` + `style_block.py` + esqueletos | **hecho** |
| Molde (pieza 01) escrito y validado | **hecho** |
| Lotes A-D (las 20 piezas) | **hecho** |
| Renders `qh` (1080x1920 @ 60) | **hechos**, 20/20 |
| Guion de voz (98 frases) + SFX (173 eventos) | **hecho** |
| Mux y verificacion (0 fallos, costuras 0.0000) | **hecho** |
| Hoja de contactos de las 20 portadas | **hecha** (destapo "LA ELIPTICA") |
| PR, catalogo, memoria | en curso |

## 6. Storyboard pieza a pieza

Lo que cada pieza tiene que ENSEÑAR, con las funciones de `especiales.py`
que lo calculan y la cifra literal. Es el encargo que recibe cada agente.

### 00 · intro (escrita)
Wordmark CO.DE (como el 31/33) + titulo en TRES lineas —"CON NOMBRE
PROPIO" a cuerpo 56 mide 6.53 y la zona segura son 5.76— y el gesto: tres
siluetas en el mismo sitio, una detras de otra (clotoide, mariposa de
Lorenz, diatomea de la superformula). Las tres las calcula la libreria.
**15.66 s.**

### 01 · GAMMA — el factorial sin escalones (MOLDE, escrita)
Cuatro puntos (0! a 3!) en CIAN; la curva de gamma los enhebra en AMBAR;
marca en x=0.5 → **1.7725**; su cuadrado → **3.1416**; la curva sigue a la
izquierda y aparecen los polos → **-3.5449**. `gamma`, `curva_gamma`,
`factorial`. **31.00 s.**

### 02 · LAMBERT — el despeje imposible
La telaraña de x → e^-x cayendo al unico punto fijo. `telarana`,
`iteracion_punto_fijo`, `omega`. Cifra **0.5671**, repetida con dos
etiquetas: es el punto fijo Y la solucion de x·e^x = 1.

### 03 · LA ELIPTICA — el pendulo real, medido
Dos pendulos sueltos a la vez, 10° (CIAN) y 90° (AMBAR), que se descuelgan
a la vista. `Pendulo`, `pendulo` (RK4 sin aproximar el seno),
`periodo_pendulo`, `exceso_de_periodo`. Cifra **18.03 %**.

### 04 · FRESNEL — girar sin dar un tiron
La espiral de Cornu se dibuja de un trazo y, debajo, su curvatura sube
como una recta. `clotoide`, `curvatura`, `ojo_de_la_espiral`. Cifra: lo
que le falta para llegar a su ojo (**0.0198** en s=8) y el limite
**0.5000**.

### 05 · CHEBYSHEV — el error repartido por igual
Los mismos 21 nodos, dos repartos, EL MISMO cuadro: el equiespaciado se
sale por arriba y por abajo. `runge`, `nodos_*`, `interpola`,
`error_interpolacion`, `recortar`. Cifras **59.82** → **0.0177**.

### 06 · BESSEL — el tambor no da notas
J0 y su primer cero; el tambor visto desde arriba con el circulo quieto.
`bessel_J`, `ceros_J`, `modo_tambor`, `campo_signo`, `razon_de_modos`.
Cifras **2.4048**, el radio del circulo nodal **0.4357**, y **1.5933** de
remate (en una cuerda saldria 2 exacto).

### 07 · CHLADNI — el sonido dibuja
El modo puro (3,2) es una rejilla de rectas. Pero (3,2) y (2,3) suenan a
la MISMA frecuencia, asi que su mezcla tambien es un modo — y la mezcla ya
no son rectas. La arena huye de donde vibra y dibuja la figura.
`modo_cuadrado`, `chladni`, `arena`, `lineas_nodales`, `frecuencia_modo`.
Cifras: **3** lineas nodales del modo puro y **3.6056** de frecuencia
relativa, la misma para los dos modos que se mezclan.

### 08 · AIRY — el borde de la sombra
La optica geometrica promete un escalon: luz de un lado, nada del otro. Lo
que hay es Ai: franjas que se apagan hacia la luz y un desvanecimiento
suave hacia la sombra. El maximo de luz NO esta en el borde geometrico.
`airy_Ai`, `ceros_Ai`, `borde_de_sombra`. Cifra **-2.3381**.

### 09 · LEGENDRE — la Tierra no es esfera
Una circunferencia deformada por P2 (el achatamiento), y luego por P3, P4,
P5: las capas con las que se escribe la forma de un planeta. `legendre_P`,
`perfil_armonico`, `cruces_por_cero`, `abultamiento_km`. Cifra **21.4 km**
(calculada de `a·f`; el achatamiento de WGS84 es DADO y va en gris) y los
**l** ceros de cada P_l, contados sobre el dibujo.

### 10 · CATENARIA — la cadena no es parabola
Las dos curvas con los MISMOS extremos y la MISMA flecha, superpuestas: se
separan un **0.71 %** del vano, casi nada. Y aun asi la cadena es la que
cuelga mas bajo (minima energia). `catenaria`, `parabola_equivalente`,
`exceso_de_cable`, `separacion_maxima`. Cifra de remate: **20.94 %** de
cable de mas que el vano — lo que paga el que compra el cable.

### 11 · WEIERSTRASS — continua y sin pendiente
Cuatro zooms seguidos sobre el mismo punto: no se alisa nunca. Y la
pendiente que se le pide al acercarse no converge: **10, 73, 196, 2780,
16936**. `ventana_zoom` (suma MAS terminos en cada zoom o el dibujo se
alisaria solo), `pendientes_que_se_disparan`. Cifra final **16936**.

### 12 · CANTOR — sube sin subir nunca
El peine se come el segmento por tercios; la escalera crece de 0 a 1
siendo plana en el **99.23 %** del recorrido. `tramos_cantor`,
`escalera_cantor`, `mesetas`, `medida_cantor`.

### 13 · CAUCHY — la campana sin media
Dos medias corriendo sobre 20 000 muestras: la de la gaussiana se asienta
(**0.00031** de salto final) y la de Cauchy sigue dando saltos de
**0.282** hasta el ultimo momento. `muestras_gauss`, `muestras_cauchy`,
`media_corrida`, `salto_maximo`, `barrido_semillas` (20 semillas, ninguna
invierte la conclusion).

### 14 · LORENZ — nunca pasa dos veces
La mariposa se dibuja de un trazo: **26** cambios de ala en 48 s y ni una
vuelta igual que otra. Dos trayectorias separadas por una milmillonesima
tardan **19.44 s** en separarse una unidad entera. `lorenz`, `par_lorenz`,
`separacion`, `tiempo_hasta`, `vueltas`. NO se habla de caos, ni de
Lyapunov, ni de dimension: eso es de los cursos 12 y 26.

### 15 · CICLOIDE — el camino mas rapido
Tres cuentas caen a la vez por la recta, el arco de Galileo y la cicloide.
Gana la cicloide: **0.8053 s** contra 0.8229 y 0.9996. Y el arco pierde
por un 2.2 %, que es lo que hace buena la carrera. `cicloide`, `recta`,
`arco_circular`, `tiempo_descenso`, `avance_en_tiempo` + `ritmo_fisico`
(la animacion va a la velocidad de la GRAVEDAD, no del `run_time`).

### 16 · LISSAJOUS — dos senos en angulo recto
La figura se cierra sobre si misma y la razon de frecuencias se LEE
contando toques: **3** en el lado y **2** en el techo. `lissajous`,
`toques`, `cierra_en`.

### 17 · ZETA — los primos tienen musica
La curva de zeta sobre la recta critica pasa exactamente por el origen. El
primer cero, en **14.1347**. `zeta`, `zeta_en_recta`, `hardy_Z`,
`primer_cero_zeta`, `basilea` (la suma a lo bruto se queda corta).

### 18 · SUPERFORMULA — una formula, mil formas
Cuatro numeros cambian y la misma formula da estrella, flor, gota,
diatomea y cuadrado. Los lobulos se CUENTAN sobre la curva dibujada:
**12** en la diatomea. `superformula`, `FORMAS`, `lobulos`. Cierra el
curso al reves que las otras: aqui la funcion nueva no resuelve un
problema, RESUME una familia de formas.

### 19 · cierre (escrita)
La espiral de Cornu se dibuja entera y se recoge en su propio limite, que
es el punto ambar de CO.DE. La marca no se posa encima del contenido: es
el sitio al que el contenido tiende. **12.5 s.**

## 7. Cierre (2026-09-12)

**Entregado.** `exports/verticales/funciones/`:

| | |
|---|---|
| Pelicula | `funciones_vertical.mp4`, **596.66 s (9.94 min)**, 1080x1920 @ 60 fps, 25 MB |
| Piezas sueltas | `piezas/*.mp4` — **las 20 sonorizadas**, que son EL producto para Instagram |
| Voz | `voz/*.wav` — 18 piezas, `es-MX-JorgeNeural` por `edge-tts` |
| Pico del montaje | **-1.8 dB** (ninguna pieza paso de -1.8; no hizo falta re-muxear) |
| Costuras | **19 a 0.0000/255**, igual que el 31, el 32 y el 33 |
| Verificacion | `verifica_vertical.py`: **0 fallos**, 53 avisos (todos de `estima()`) |
| Sonda | `sonda_especiales.py`: **177 invariantes, 0 fallos** |

**La voz entro a la primera, y esa es la diferencia con el curso 33.** Alli,
cinco de dieciocho piezas fallaron al sintetizar de verdad despues de pasar
la verificacion por conteo de palabras. Aqui las 98 frases se escribieron
contra los huecos MEDIDOS por `sonda_tiempos_voz.py` y con un tope de **2.2
palabras por segundo de hueco** en vez de las 2.5 que documentaba el 32:
`alinear_voz.py` no devolvio ni un solape ni una cola corta en las 18
piezas. La cola mas corta quedo en 1.67 s sobre un minimo de 0.8. El
margen del 12 % sobre la velocidad documentada es lo que compro las cinco
correcciones que el 33 tuvo que hacer a mano.

Los 53 avisos son los de siempre: `estima()` cuenta palabras sobre el texto
ANTES de sintetizar y no sabe que `alinear_voz.py` ya coloco cada frase con
su duracion real. Mismo ruido que el 32 (60 avisos) y el 33 (90).

### La hoja de contactos, y por que es un paso fijo

Las 20 portadas juntas destaparon que **diecisiete llevaban el nombre pelado
—GAMMA, FRESNEL, BESSEL, CANTOR— y una llevaba articulo**: "LA ELIPTICA".
Pieza a pieza no se ve; las veinte juntas, si. Se cambio a **"ELIPTICA K"**,
que ademas nombra la funcion de verdad (la integral eliptica completa de
primera especie). Costo un re-render y un re-mux de una pieza, y la
duracion no se movio: la portada es una coreografia de tiempos fijos, no
depende de lo larga que sea la palabra.

## 8. Cosecha de trampas

Lo que este curso añade al catalogo de la casa.

### De la libreria y las cifras

1. **La escalera de Cantor por expansion en base 3 no sobrevive a los
   flotantes.** `v = v*3 - d` acumula error: bajaba en 41 sitios y en x=1
   devolvia 0. Se construye de la definicion geometrica.
2. **Por dos puntos pasan infinitas circunferencias, y la eleccion decide
   el resultado.** El arco tangente a la horizontal tarda 4.11 s contra los
   0.8053 de la cicloide —un espantapajaros—; el de Galileo, tangente a la
   vertical, pierde por un 2.2 %. Elegir el competidor debil es una forma
   de mentir que no deja rastro en ninguna cifra.
3. **Weierstrass tiene un tope numerico.** Por encima de trece terminos el
   argumento `b^k·pi·x` pasa de 1e13 y float64 pierde la FASE: el termino
   fino sale con desfase aleatorio y, como su amplitud es pequeña, la curva
   no sale ruidosa sino **SUAVE** — exactamente lo contrario de lo que la
   pieza demuestra. `ventana_zoom` aborta.
4. **Contar maximos comparando cada muestra con sus vecinas da uno de
   menos** cuando el maximo cae entre dos muestras: tres de las cinco
   formas de la superformula salian con un lobulo menos, y los lobulos que
   se VEN eran los correctos. Se cuenta por el cambio de signo de la
   pendiente, con envoltura.
5. **`linspace` sobre una curva cerrada repite el punto final.** Si ese
   punto es un maximo, se cuenta dos veces: el osciloscopio leia 4:2, que
   no es ninguna razon.
6. **Una malla impar pone x=0 sobre una muestra**, y `sign(0)` no es
   negativo: los polinomios de Legendre de grado impar perdian un cero.
7. **Una biseccion solo vale si el intervalo contiene UNA raiz.** El pico
   del borde de sombra daba un punto con el intervalo (-4, 0) y otro
   distinto con (-6, 0), los dos con toda la seguridad del mundo. Se barre
   desde el borde hasta el primer cambio de signo.
8. **Hay cifras cuyos decimales son de la truncatura.** La pendiente de
   Weierstrass se mueve un 0.25 % al sumar dos terminos mas: se rotula
   ENTERA. Lo que la pieza afirma no es el valor, es que la sucesion no se
   para.

### De composicion

9. **Una copia de un mobject ya encajado, metida en un grupo nuevo, llega
   descolocada**: el segundo `encajar` le aplica su desplazamiento encima.
   En la pieza 08 el escalon de referencia salia flotando por encima de su
   cuadro. Se reconstruye, no se copia.
10. **Una curva con `stroke_opacity=0` se "crea" entera sin pintar un
    pixel.** `Create` no enciende el trazo: el render sale limpio, sin
    aviso y sin curva. El molde entero se renderizo una vez sin ninguna de
    sus cinco curvas.
11. **Un rotulo colocado con `next_to` sobre un punto cercano al borde
    sobresale del grupo**, `encajar` lo encoge todo y el guardian de
    legibilidad aborta con "el rotulo mas pequeño mide 0.143". El sintoma
    no señala la causa. Los rotulos van con `move_to` sobre coordenadas de
    datos elegidas en zona vacia.
12. **El cuadro lo fija el dato mas extremo, no el mas importante.** El de
    la carrera de la cicloide se ajusto a la meta (-1.0) y el arco de
    Galileo baja a -1.25: se salia, el grupo medio mas que la franja y el
    rotulo acabo encima de la curva.
13. **Un punto ambar sobre una curva ambar no existe.** Las marcas que
    señalan de donde sale una cifra van en TINTA, el color de la cifra.
14. **Una cifra que habla de un objeto tridimensional junto a un dibujo que
    es un corte, miente.** "4 paralelos quietos" sobre un perfil donde se
    cuentan OCHO cruces: cada paralelo nodal corta el meridiano dos veces.
    Se rotula lo que se puede contar en pantalla, y se marcan los puntos.
15. **Un polinomio dibujado fuera del intervalo donde interpola se
    dispara**, y contradice a su propia cifra de error: el de Chebyshev
    salia con dos rayas verticales en los bordes junto al rotulo "0.0177
    de error".

### De proceso

16. **Una ola de cinco subagentes puede agotar la cuota de sesion antes de
    producir nada.** Los cinco murieron a la vez con un 429, cada uno a
    mitad de la lectura de contexto, y dejaron cero trabajo parcial en
    disco. Las veinte piezas se escribieron en serie en la sesion
    principal.
17. **La imagen de render puede no poder reconstruirse.** Debian bullseye
    llego a su fin de vida: `deb.debian.org` devuelve 404 en todo
    `bullseye-security` y el Release principal vencio. Se apunta al
    snapshot del que salio la imagen base. Y **manim y numpy quedan
    pineados**: una reconstruccion se trajo manim 0.21.0 donde produccion
    corre 0.20.1, y el render local habria dejado de ser el de produccion
    sin que nada avisara.
