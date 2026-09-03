# Curso 33 · Señales y sistemas (VERTICAL 9:16, estilo LIENZO, MUDO)

**Encargo del 2026-09-02**, inmediatamente después del 32:

> *"continuamos de esta misma manera con otro curso, este sera de señales
> y sistemas."*

*"De esta misma manera"* fija el formato sin preguntar nada: **vertical
9:16, estilo LIENZO, MUDO** (música encima, sin voz ni SFX), **sin
numeración** en la esquina, **portada de ~3.7 s** con el nombre y la tesis,
y **20 piezas** (intro + 18 + cierre). Todo lo que aprendió el 32 se aplica
tal cual.

## 0. La capa que ocupa (la decisión que más importa)

Un curso clásico de "señales y sistemas" contiene Fourier, Laplace y Z — es
decir, **el curso 32 entero**— y roza el 27 (*Procesamiento de señales*, 30
lecciones). Hacerlo con el temario de toda la vida sería re-explicar dos
cursos.

Así que este ocupa **la capa de los SISTEMAS**:

| Curso | Capa | Qué asume |
|---|---|---|
| 27 · Procesamiento de señales | qué se le hace a una señal muestreada | — |
| 32 · Transformadas | cómo se cambia de dominio | — |
| **33 · Señales y sistemas** | **qué le hace un sistema a una señal** | cita las transformadas como herramienta; **no las explica** |

La pieza 12 (*las autofunciones*) es la bisagra: explica **por qué** existe
el curso 32 —una exponencial compleja entra en un sistema lineal y sale
igual salvo un número— sin volver a contar ninguna transformada.

## 1. El ángulo: "qué le hace a la señal"

Mismo espíritu que el 32 (*lo que vuelve fácil*) pero girado hacia los
sistemas: **cada pieza mete una señal por un lado y enseña qué sale por el
otro.** El sistema es una caja que se conoce por lo que hace, y toda la
gracia del curso es que con **una sola medida** —la respuesta al impulso—
queda determinado para siempre.

Se mantiene entero el reparto en tres del curso 32, que es lo que permite
que un curso mudo explique sin llenarse de texto:

1. **La portada** dice el nombre y qué vuelve fácil (≤ 5 palabras).
2. **La animación** lo demuestra con un solo verbo visual.
3. **La cifra** lo prueba, calculada en el render.

## 2. Las 20 piezas

| # | Pieza | Portada (tesis) | Verbo visual | Cifra |
|---|---|---|---|---|
| 00 | intro | — | Wordmark CO.DE + `SEÑALES Y SISTEMAS` | — |
| 01 | El impulso | no dura nada y vale para todo | Un pulso que se estrecha y crece a área constante hasta ser una raya | el área, que no cambia |
| 02 | La respuesta al impulso | golpea una vez y ya lo sabes todo | Un golpe entra en la caja y sale una forma que se apaga | duración de la cola |
| 03 | La convolución | deslizar, multiplicar, sumar | La señal invertida desliza sobre la otra y el área barrida dibuja la salida | longitud de la salida |
| 04 | El escalón | la suma de infinitos impulsos | El escalón se descompone en impulsos; su respuesta es la suma acumulada | valor final |
| 05 | Linealidad | dos entradas no se estorban | Dos señales por separado, luego juntas: la salida es la suma exacta | error de superposición |
| 06 | Invarianza | mañana hace exactamente lo mismo | La entrada se retrasa y la salida se retrasa igual, sin deformarse | desfase = retardo |
| 07 | Causalidad | no puede responder antes del golpe | Una respuesta que empieza antes de t=0, y por qué es imposible | muestras antes de cero |
| 08 | Estabilidad | entrada acotada, salida acotada | Dos sistemas: uno se apaga, el otro crece sin parar | suma de la respuesta |
| 09 | En cascada | el orden no importa | Dos cajas encadenadas; se intercambian y la salida es idéntica | diferencia = 0 |
| 10 | Realimentación | la salida vuelve a la entrada | Se cierra el lazo y la respuesta cambia de forma | ganancia del lazo |
| 11 | Ecuación en diferencias | el sistema como receta | Cada muestra de salida se construye con las anteriores | coeficientes |
| 12 | Autofunciones | lo único que no deforma | Una exponencial entra y sale idéntica salvo un factor | el factor |
| 13 | Respuesta en frecuencia | no puede inventar frecuencias | Entra un tono, sale el mismo tono con otra amplitud | ganancia por frecuencia |
| 14 | Fase y retardo de grupo | la forma se rompe sin tocar amplitudes | Mismas amplitudes, fases movidas: la señal deja de parecerse | retardo de grupo |
| 15 | Resonancia | un empujón a tiempo lo mueve todo | La misma energía a la frecuencia justa levanta la respuesta | factor de amplificación |
| 16 | Transitorio y permanente | lo que pasa antes de asentarse | La respuesta se divide en dos partes; una se apaga | tiempo de asentamiento |
| 17 | Un filtro | dejar pasar unas y no otras | Una señal con dos tonos entra; sale con uno | atenuación |
| 18 | Cuando deja de ser lineal | aparecen tonos que no entraron | Un tono entra en una caja que satura y salen armónicos | distorsión |
| 19 | cierre | — | La convolución se recoge en el punto ámbar de CO.DE | — |

**El arco**: 01-04 el sistema y su huella; 05-08 las cuatro propiedades que
lo hacen manejable; 09-11 componer sistemas; 12-15 lo mismo visto en
frecuencia; 16-18 los límites.

## 3. Contrato de la librería

`studio/content/manim_extensions/sistemas.py`, dos mitades como siempre:

- **Numérica** (numpy puro, importable sin manim, `default_rng` con
  semilla): respuestas al impulso, convolución, escalón, comprobación de
  linealidad e invarianza, estabilidad BIBO, cascada, lazo cerrado,
  ecuaciones en diferencias, respuesta en frecuencia, retardo de grupo,
  resonancia, saturación y distorsión armónica.
- **De dibujo**: la CAJA del sistema (la pieza nueva de este curso), el
  deslizamiento de la convolución, el diagrama de bloques con lazo, y lo
  que ya sirve de `transformadas.py` (trazas, tallos, mapas, barras).

Sonda: `studio/tools/sonda_sistemas.py`, con los invariantes que sólo se
cumplen si está bien implementado — conmutatividad de la convolución,
longitud N+M-1, superposición exacta en un sistema lineal y **rota** en uno
que satura, BIBO contra la suma de |h|, y que la respuesta en frecuencia
salga igual medida con tonos que calculada con la FFT de h.

## 4. Lotes

| Lote | Piezas | Estado |
|---|---|---|
| A | 00 intro, 01, 02, 03, 04 | **cerrado** |
| B | 05, 06, 07, 08, 09 | **cerrado** |
| C | 10, 11, 12, 13, 14 | **cerrado** |
| D | 15, 16, 17, 18, 19 cierre | **cerrado** |

**LAS 20 ESCRITAS Y REVISADAS FOTOGRAMA A FOTOGRAMA.** Duraciones medidas en
`ql`: intro 15.07, 01 31.70, 02 32.40, 03 36.03, 04 31.50, 05 36.60,
06 32.83, 07 31.93, 08 34.57, 09 36.73, 10 31.67, 11 33.93, 12 41.90,
13 33.57, 14 41.50, 15 34.67, 16 30.07, 17 34.86, 18 35.03, cierre 13.63.
Suma ~11.4 min. Sonda: **73 invariantes, 0 fallos**.

**Piezas devueltas y por que** (nueve de dieciocho, y en cinco casos el
error estaba en MI encargo, no en el trabajo del agente):

| Pieza | Que estaba mal |
|---|---|
| 04 | "valor final" sobre una respuesta que seguia oscilando (0.1381 de vaiven) |
| 06 | el remate apinado en dos tercios del cuadro; y despues, ambar al 32 % = oliva |
| 08 | dos paneles a la misma altura con escalas que difieren 17.8x, sin declararlo |
| 09 | el cero solo era comprobable si el espectador RECORDABA la salida anterior |
| 10 | "60 muestras que duran" era el tamano de la ventana |
| 11 | el eje del cero en el suelo del cuadro con datos que bajan de cero |
| 15 | mi encargo daba una cifra de ventana (552) y decia que la campana "crece" |
| 16 | el cuarto decimal del valor final lo ponia la ventana |
| 17 | "COINCIDEN" sobre dos curvas en antifase: faltaba compensar el retardo |

**Nombres de portada, MEDIDOS** (no elegidos a ojo): los 18 caben con su
termino tecnico entero. Tres van en **dos lineas** al cuerpo 64 —RESPUESTA AL
IMPULSO, ECUACION EN DIFERENCIAS y RESPUESTA EN FRECUENCIA—; el resto en una
linea a 64 o 56.

La pieza 11 estuvo a punto de escaparse con el nombre corto. Cuando escribi
los esqueletos, "ECUACION EN DIFERENCIAS" no cabia y la llame **LA
ECUACION**; luego arregle `portada` para partir en dos lineas —precisamente
para no dejar que la tipografia decidiera el temario— y **no volvi a
cambiarle el nombre**. Lo destapo la hoja de contactos de las 20 portadas al
cerrar el curso: el plan predicaba una cosa y la pieza enseñaba otra. Ya
lleva su nombre entero. La leccion es que un principio nuevo hay que
aplicarlo hacia atras, a lo que se escribio antes de tenerlo.

## 5. Estado

- Rama `curso/senales-y-sistemas`. Desbloqueado: el curso 32 se entrego el
  2026-09-02.
- **Molde**: `clips/01-el-impulso/escena.py`, 31.70 s. Todas las piezas
  copian de ahi la forma (construir los estados antes, un solo grupo,
  morfeo entre ellos).
- Contrato de subagente en el scratchpad de la sesion.
- Lo que se hereda del 32 y no hay que volver a hacer: el estilo LIENZO con
  portada y modo mudo, los guardianes, `sellar_duraciones.py`,
  `unir_vertical.py --mudo` y el contrato.

## 6. Cosecha de trampas

(se rellena al cerrar cada lote)

### Del arranque (las tres del molde)

- **Un nombre que no cabe no se renombra: se parte en dos lineas.** Medidos
  los 18 nombres, RESPUESTA AL IMPULSO solo entraba al cuerpo 40 —la mitad
  que EL IMPULSO, en la misma serie— y otros dos no entraban ni a 40. La
  salida facil era renombrar las piezas (LA ECUACION, EN FRECUENCIA), que es
  dejar que la tipografia decida el temario. `lz.portada` parte en dos lineas
  por debajo del cuerpo 50 y conserva el termino tecnico, que es lo unico que
  el espectador se lleva escrito.
- **El guardian de la fraccion medía el bounding box, no lo que se pinta.**
  El patron que esta casa recomienda —construir todos los estados antes y
  encenderlos con opacidad— mete en el grupo estados invisibles que inflan la
  caja: el molde paso el guardian con un dibujo visible que ocupaba el 22 % de
  la franja. Un guardian al que se le cuela el caso que el propio manual
  recomienda no es un guardian. Ahora mide sobre los miembros con opacidad.
  **Corolario para las piezas**: dentro de un cuadro con el rango fijo, el
  estado mas bajo no puede bajar de la mitad del mas alto; se encadenan pares
  de razon 2 y se DECLARA el salto de escala entre pares.
- **`cola` no es "cuanto dura".** Mide donde se acaba la senal contando desde
  el origen, asi que un impulso puesto en la muestra 20 tiene cola 21 y dura
  1. El ultimo plano del molde rotulaba "muestra que dura" sobre un **21**.
  Separado en `sis.duracion`, con el contraejemplo en la sonda (55
  invariantes).

### De la produccion (lo que cazo revisar los frames)

- **Una cifra que cambia con la ventana no es del sistema.** La pieza 10
  rotulaba "60 muestras que duran" sobre una respuesta divergente: ese 60 era
  `N=60`, y con N=200 habria dicho 200 sin que nada cambiara en el sistema. Se
  cambio por cuanto multiplica cada muestra a la anterior (`h[-1]/h[-2]`), que
  no depende del cuadro. Es la misma regla de la malla, aplicada al eje del
  tiempo.
- **Y una cifra que no se ha asentado tampoco.** La 04 rotulaba "valor final"
  sobre una respuesta que en pantalla seguia oscilando: 0.1381 de vaiven en
  las 8 ultimas muestras, y un 2.2 % de distancia al valor de asentamiento de
  verdad. `sis.valor_final` es la suma de la `h` que le pases.
- **Normalizar cada panel a su propio maximo es mentir por omision.** La 08
  dibujaba dos sistemas a la misma altura con escalas que difieren 17.8 veces:
  el que se dispara parecia manso y el dibujo contradecia a su cifra. Se
  declara la escala (1X / 18X), como en el molde.
- **Lo que hay que RECORDAR para creerse una cifra, en un reel mudo no se
  recuerda.** La 09 ensenaba una salida, el intercambio y otra salida; el cero
  solo es comprobable desde que las dos se dibujan SUPERPUESTAS. Mismo remedio
  que la 06.
- **La igualdad bit a bit solo se puede exigir cuando es alcanzable.** En la
  06 las dos curvas son tramos del mismo array y `np.array_equal` vale; en la
  09 son dos convoluciones por caminos distintos y sumar en otro orden mueve
  el ultimo bit (1.33e-15 sobre un pico de 1.9). La guarda va en 1e-9, que
  sigue cazando un desfase real de un indice.
- **Tres huecos de API del mismo tipo**: una pieza obligada a pescar cosas de
  un grupo por indice o por tipo. `sis.tallos` acepta `colores=` por muestra,
  `sis.lazo` acepta `color_entrada`/`color_salida` y devuelve `g.vuelta` por
  nombre. Todos se rompen en silencio, no con un error.
- **`sis.banda` pintaba en LINEA**, que es el azul de las rejillas, a un paso
  del fondo. Una banda de tolerancia no es mobiliario: es el umbral que la
  pieza afirma. Ahora va en APAGADO.
- **Trampas de manim nuevas**, las tres en `references/trampas.md`: `Indicate`
  escala alrededor del centro del bounding box (sobre un tallo estira la raya
  hacia abajo y cruza el eje); el objetivo de un `Transform` tiene que estar
  VIVO aunque no se vea (copia tambien la opacidad, y transformar hacia un
  estado apagado deja el dibujo invisible); y `Create` RE-ANADE su mobject a
  la escena al terminar (`introducer=True`), lo que saca del grupo del carril
  la parte que animas.
- **El acento traslucido no es solo cosa de masas**: un trazo grueso (7.0) al
  32 % da el mismo verde oliva ilegible. Una curva de referencia va en
  APAGADO opaco.
