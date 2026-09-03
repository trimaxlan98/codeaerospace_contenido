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
| A | 00 intro, 01, 02, 03, 04 | pendiente |
| B | 05, 06, 07, 08, 09 | pendiente |
| C | 10, 11, 12, 13, 14 | pendiente |
| D | 15, 16, 17, 18, 19 cierre | pendiente |

## 5. Estado

- **Bloqueado por el curso 32**, que va por 12 de 20 piezas. Este no empieza
  a producirse hasta que el 32 esté entregado.
- Lo que ya se hereda del 32 y no hay que volver a hacer: el estilo LIENZO
  con portada y modo mudo, los guardianes (`FRACCION_MINIMA`, legibilidad,
  ancho, tesis de 5 palabras), `unir_vertical.py --mudo`, y el contrato de
  subagente.

## 6. Cosecha de trampas

(se rellena al cerrar cada lote)
