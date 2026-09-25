# Catálogo de cursos — cómo se agrupan en el índice de Proyectos

Fecha: 2026-08-15 · Herramienta que lo aplica: `studio/tools/ordenar_cursos.py`

## La regla que impone el índice

La vista Proyectos no tiene campo de "área": deduce la **familia** partiendo el
nombre por el primer `·` y quedándose con lo de delante (`Projects.jsx:splitName`).
Dos consecuencias que mandan sobre todo lo demás:

1. **Un prefijo con un solo proyecto no forma grupo** — cae en *Cursos sueltos*.
   Por eso ninguna área tiene menos de dos cursos.
2. **Dentro de una familia se ordena por la etiqueta**, no por fecha
   (`localeCompare`). Por eso cada curso monográfico lleva un número delante: es
   lo único que fija el orden de lectura.

El nombre es, además, la **clave de emparejamiento** de `subir_curso.py:86`. Ver
"Cómo se aplica" antes de tocar un nombre a mano.

## Antes

58 proyectos: tres familias numeradas (Aerodinámica 1.1–4.5, Electromagnetismo
1.1–4.3, Metrología óptica 1.1–3.3; desde 2026-08-19 también Álgebra lineal 1.1–4.3) y **16 cursos monográficos de 8 clips en un
montón plano**, ordenados por actividad — es decir, por el azar de qué se tocó
la última vez.

## Después — 5 áreas

Cada área es una secuencia de lectura, no una etiqueta suelta: el número dice
por dónde se empieza.

### Comunicaciones — del espectro a apuntar la antena
| # | Curso |
|---|-------|
| 1 | El espectro: la guerra invisible por las ondas |
| 2 | SDR: la radio hecha software |
| 3 | Cerrar el enlace: la cuenta en decibelios |
| 4 | Apuntar a un satélite: el arte del seguimiento |

Primero qué es el recurso que se disputa, luego cómo se fabrica la radio que lo
usa, luego si el enlace cierra, y por último cómo se mantiene apuntado. Es la
continuación aplicada del módulo 4 de Electromagnetismo (ionosfera, enlace con
el satélite, clima y margen), que se queda en la física.

### Información y cómputo — medir la información, guardarla, repartirla
| # | Curso |
|---|-------|
| 1 | Teoría de la información: los bits de Shannon |
| 2 | Criptografía: el arte de guardar secretos |
| 3 | Sistemas distribuidos: la nube por dentro |

Shannon define qué es un bit y cuánto cabe; la criptografía decide quién puede
leerlo; los sistemas distribuidos, cómo sobrevive repartido entre máquinas que
fallan.

### Inteligencia artificial — la red, el lenguaje, el agente
| # | Curso |
|---|-------|
| 1 | Redes neuronales: la máquina que aprende |
| 2 | De la palabra al vector: embeddings y atención |
| 3 | Agentes de IA: máquinas que operan el mundo |

Progresión literal del campo: aprender una función, representar lenguaje, actuar
sobre el mundo.

### Sistemas dinámicos — el patrón, su ruptura, su control
| # | Curso |
|---|-------|
| 1 | Matemáticas en la naturaleza |
| 2 | Caos: el orden escondido |
| 3 | Control: domar sistemas que se resisten |

Los tres tratan la misma pregunta desde tres ángulos: qué patrón produce una
regla iterada (Fibonacci, fractales, Turing, Gray-Scott), cuándo esa misma
iteración deja de ser predecible (mapa logístico, Lorenz, Lyapunov) y cómo se
sujeta un sistema que se resiste (realimentación, estabilidad).

### Astronáutica — subir, sobrevivir allá arriba, medir el tiempo
| # | Curso |
|---|-------|
| 1 | Tsiolkovsky: la tiranía del cohete |
| 2 | Materiales que van al espacio |
| 3 | Relatividad y el GPS |

El coste de llegar, lo que aguanta el que llega, y la física fina que hace útil
al que ya está arriba.

### Lo que sigue suelto, a propósito
**Marca · Intro y cierre** (2 clips) no es un curso: son los clips de identidad
para posproducción. Su prefijo `Marca ·` no forma grupo porque está solo, y así
se queda — inventarle compañía sería peor que dejarlo en *Cursos sueltos*.

## Cómo se aplica

El nombre vive en **tres** sitios que tienen que ir a la par:

1. `studio/content/cursos/<slug>/curso.json` → campo `name` (la fuente en git).
2. `guiones/<slugify(nombre)>/` → las narraciones ya generadas.
3. La tabla `projects` de `manimstudio.db` (lo que ve la app).

**(1)** porque `subir_curso.py` empareja el proyecto **por nombre exacto**: si
solo se cambiara la base, la siguiente subida de ese curso no reconocería su
proyecto y **crearía un duplicado con todos sus clips**.

**(2)** porque el directorio de narración **no se guarda en ninguna parte: se
deriva del nombre** (`narracion.destino` → `guiones_dir / slugify(name)`).
Renombrar el proyecto sin mover su carpeta deja las narraciones huérfanas: los
16 cursos aparecerían como *sin narración*, su zip saldría sin `.wav` ni
`.txt`, y regenerarlas costaría ~128 llamadas a Vertex y su TTS — aunque los
archivos siguieran intactos en disco. Este punto se descubrió auditando el
script antes de correrlo en producción y por eso lo hace él mismo, en el mismo
paso y antes de tocar la base (así, cuando la app ve el nombre nuevo, su
carpeta ya está donde la va a buscar).

Por eso el renombrado se hace con una sola herramienta, idempotente y con
dry-run por defecto:

```bash
# plan, sin escribir nada
studio/backend/venv/bin/python studio/tools/ordenar_cursos.py

# aplicar en el VPS (repo + base de producción)
studio/backend/venv/bin/python studio/tools/ordenar_cursos.py --aplicar
```

Estado: **aplicado en el repo y en producción** (2026-08-15). Verificado sobre
un banco de pruebas con los nombres viejos antes de tocar el VPS: 16/16
proyectos renombrados, **cero narraciones huérfanas**, contenido preservado y
segunda pasada sin cambios (idempotente).

**El prefijo de área no entra en el video.** Los `style_block.py` y las librerías de
`manim_extensions/` siguen rotulando en pantalla "Relatividad y el GPS", no
"Astronáutica · 3 Relatividad y el GPS": el área ordena el índice de trabajo, no es
parte del título que ve el espectador. No hay que re-renderizar nada.

Renombrar toca `updated_at`, así que con el orden *por actividad* los 16 suben
al principio una vez. Con el orden *por nombre* el índice queda como se diseñó.
No toca clips, jobs ni renders: los videos ya renderizados siguen vigentes.

---

## Familias añadidas despues del reordenado (2026-08-19 a 2026-08-27)

El reordenado de arriba tocó los 16 cursos monográficos. Las familias que han
ido llegando desde entonces **ya nacen agrupadas**, porque su nombre lleva el
prefijo delante del `·` y son más de una:

| Familia | Lecciones | Curso |
|---|---|---|
| Álgebra lineal | 18 | 22 |
| Cálculo vectorial | 12 | 23 |
| Comunicaciones digitales | 18 | 24 |
| Protocolos de Internet | 24 | 25 |
| **Procesamiento de señales** | **30** | **27** |
| Tesis 6G | 12 | 36 |
| Rendimiento SQL | 21 | 37 |
| SDR | 24 | 38 |

`Procesamiento de señales` es la familia más grande del índice: 30 proyectos
numerados de 1.1 a 10.3, que la vista de Proyectos ordena por etiqueta y por
tanto en el orden de lectura del curso. No hace falta tocar
`ordenar_cursos.py`: el prefijo ya está en el nombre desde que se sube.

Es también el primer curso horizontal **sin subtítulos**: sus `style_block`
no definen `pie_curso` y llevan un guardián que aborta el render si un rótulo
pasa de cinco o seis palabras. Si algún día se copia uno de esos bloques para
una familia que sí quiera pie narrativo, hay que volver a añadirlo a mano.

## Curso 29 — Emergencia (vertical, experimental)

El tercer curso en 9:16 y el primero en el que **el fotograma entero es una
simulación**: no hay objetos vectoriales sobre un fondo, el fondo *es* el
sistema. Catorce clips, cada uno con dos o tres reglas que caben en una
etiqueta HUD y que producen un mundo delante del espectador: una bandada de
2500 agentes, un moho que tiende una red, una pila de arena de 50 000 granos,
el cañón de Gosper, Gray-Scott, la doble rendija, Chladni, Ising, doscientos
péndulos dobles, las cuencas de tres imanes, los epiciclos de Fourier, una
calle de vórtices y dos galaxias que chocan.

Lo sostiene un paquete nuevo, `manim_extensions/emergencia/`: el núcleo
`Pelicula` presenta una pila de frames uint8 como `ImageMobject` a pantalla
completa y la anima con `UpdateFromAlphaFunc`, con cámara (seguir un agente,
zoom) y ritmo (cámara lenta en el instante en que nace el patrón); trece
módulos numpy puros producen esas pilas, cada uno con `medir()` para la sonda
`studio/tools/sonda_emergencia.py`.

Dos cosas que este curso hace distinto y conviene saber antes de copiarlo:

- **Cada clip está hecho para subirse solo.** Por eso todos arrancan con la
  simulación ya en movimiento, y por eso las uniones del montaje son cortes
  secos y no empalmes invisibles (medido: hasta 66/255 entre piezas, frente a
  los 0.003/255 del curso 26, que nacía y moría en negro).
- **El texto va sobre un fondo que a veces es claro.** `velos_de_contraste()`
  en el `style_block` pone una banda oscura con degradado detrás del HUD y del
  pie de cifra; es lo que hace legible el gris sobre el laberinto de
  Gray-Scott o la mandala de arena. Si se baja su opacidad, el clip 03 es el
  primero que lo acusa.


## Curso 30 — Sistemas ATP: apuntamiento y seguimiento de satelites

Familia horizontal de **9 lecciones / 36 clips** (3 modulos x 3), formato
mudo, 20.4 min. Libreria `atp.py` sobre el sustrato de dibujo de
`apuntado.py` (curso 9). Publicado en PR #67 el 2026-08-29.

El arco: *una antena que persigue es una cadena de eslabones, y cada
eslabon tiene su cifra*. De un TLE a una prediccion, de la prediccion a
una trayectoria, de la trayectoria a un lazo, del lazo a una campaña que
acota su cola, y de ahi a un numero de decibelios. Lo tensa una paradoja
— el mejor pase para el enlace es el peor para la mecanica — y cierra
respondiendo por que el objetivo es 0.1 grados: no es un numero de
mecanica, es un numero de radio.

**Que NO pisa** (cuatro cursos vecinos tocan el tema): el 9 conto la
divulgacion del mismo asunto, el 11 la teoria de control generica, el 13
el link budget completo y el modulo 3 del 20 el ATP **optico** entre
satelites. Esta familia ocupa la ingenieria del ATP de radiofrecuencia
desde tierra.

- Modulo 1, **donde mirar**: el cielo que se mueve · de dos lineas a dos
  angulos · la ventana y el keyhole.
- Modulo 2, **los dos seguimientos** (angulo y frecuencia): la frecuencia
  que se mueve · la montura es un robot · el lazo sobre una rampa.
- Modulo 3, **del lazo nominal al sistema real**: LQR · la campaña Monte
  Carlo · por que una decima de grado.


## Curso 31 — ESP32: el chip por dentro (vertical, estilo LIENZO)

El cuarto curso en 9:16 y el primero con un **lenguaje visual propio**, que no
es una variante del de los tres anteriores: los cursos 26, 28 y 29 usan la
estética de consola de vuelo de la marca (fondo casi negro, escuadras HUD,
telemetría en las cuatro esquinas, pie de cifra de tres renglones). El estilo
LIENZO va al revés — una superficie lisa azul marino con **una cosa y un
dato**, y nada más. Se elige por curso, no por clip; los tres cursos
anteriores siguen exactamente igual.

Catorce clips en cuatro módulos, del silicio a lo que el chip hace con el
mundo: los ciclos que ejecuta mientras miras el reel, el reparto entre dos
núcleos, lo que cabe en 520 KB, el tamaño físico de un ciclo de reloj, el
registro de 32 bits y su flanco, el PWM que fabrica voltajes que no existen,
la escalera del ADC, I2C contra SPI, la onda de 12.3 cm, la anatomía de una
trama Wi-Fi, los anuncios BLE, sondeo contra interrupción, el jitter del
planificador y la vida de una pila.

Lo sostienen dos módulos nuevos:

- **`manim_extensions/lienzo.py`** — el estilo. Cuatro carriles con **un solo
  ocupante cada uno** (`L.escena`, `L.dato`, `L.relevo`), de modo que nada se
  encima *por construcción* y no por disciplina del autor; paleta de cuatro
  colores con un solo acento; escala tipográfica cerrada con escalón
  automático; y guardianes que abortan el render si un texto se sale de la
  zona que tapa la app o si un rótulo queda por debajo de 24 px reales. Guía
  completa en `studio/docs/LIENZO.md`.
- **`manim_extensions/esp32.py`** — la librería del curso, en dos mitades:
  numérica (numpy puro, importable sin manim, verificada por
  `studio/tools/sonda_esp32.py`) y de dibujo. Toda cifra en pantalla sale de
  la primera mitad durante el render.

Tres cosas que conviene saber antes de copiar este estilo:

- **La procedencia va en el color de la ETIQUETA, no del número.** La cifra
  siempre es tinta; la etiqueta es ámbar si el número sale de medir o calcular
  en ese render, y apagada si está *dado* — hoja de datos, literatura o un
  parámetro elegido de la simulación. Un parámetro elegido no es una medida
  por mucho que esté escrito en el código.
- **El dibujo se apoya en el suelo de su franja, no se centra.** Centrarlo
  parecía lo natural y está medido que no lo es: cualquier dibujo más bajo que
  la franja se queda a dos unidades de su cifra y la composición se parte en
  dos mitades sin relación.
- **Nada de ámbar traslúcido.** Medido sobre el fondo #0B1B33: el acento
  mezclado al 26-45 % da un verde oliva sucio, y al 14 % un gris que ya no es
  ámbar. Las piezas de área se dibujan con trazo y el fondo del lienzo dentro.

## Curso 32 — Transformadas (vertical, estilo LIENZO, **mudo**)

Dieciocho transformadas, una por pieza, más intro y cierre: serie de Fourier,
Fourier, DFT, FFT, DCT, Hartley, Walsh-Hadamard, Laplace, Z, Chirp-Z, STFT,
wavelet de Haar, Fourier fraccional, Hilbert, Mellin, Radon, Hough y Karhunen-Loève. Cada
una se cuenta por **lo que vuelve fácil**, nunca por su fórmula: la DCT
existe porque concentra la energía de un bloque en unos pocos coeficientes,
Radon porque convierte un objeto en las sombras que proyecta.

Lo que hace distinto a este curso es el tercer eje del estilo. Hasta aquí un
curso se elegía en dos: **formato** (horizontal o vertical) y **estilo**
(CONSOLA o LIENZO). El 32 estrena el **sonido**: se publica **mudo**, sin
pista de audio, para ponerle música encima en posproducción. Eso no es un
detalle de entrega, cambia cómo se escribe cada pieza — sin voz que explique,
la animación tiene que explicar sola, y llenar la pantalla de texto para
compensar es exactamente lo que arruina el estilo.

La regla que lo resuelve reparte el trabajo en tres cosas y ninguna más:

1. **La portada** (~3.7 s) dice el nombre y una tesis de **≤ 5 palabras** —
   la única explicación con palabras de la pieza. El guardián aborta el
   render en la sexta.
2. **La animación** es **un solo verbo visual**. Si para entenderla hiciera
   falta una frase en pantalla, el verbo está mal elegido: se cambia el
   dibujo, no se añade la frase.
3. **La cifra**, una, calculada por la librería durante el render.

Y como sin voz el único momento para entender un estado es el silencio que lo
sostiene, `Pieza.leer()` **rechaza cualquier pausa menor de 1.8 s**.

Dos afirmaciones no llegaron a publicarse porque la sonda las midió antes de
que se dibujara nada:

- **Chirp-Z no separa dos tonos más cerca que la resolución de Rayleigh.** La
  pieza iba a enseñar dos tonos a 0.4 bins resueltos por el zoom, y ningún
  método lineal hace eso. La tesis pasó a ser la correcta —**puntería**, no
  resolución: la CZT pone las muestras donde te interesan.
- **La transformada fraccional de Fourier discretizando el núcleo continuo no
  es unitaria** (155.3 contra 128 de energía), y ordenar autovectores tampoco
  es estable (funcionaba a N=32 y 64, fallaba a 128). Lo que se abandonó fueron
  los dos **caminos**, no el tema: la pieza sigue siendo la fraccional y llega
  por **Radon-Wigner**, que es riguroso y además ES el verbo visual. El módulo
  al cuadrado de la FrFT de orden *a* **es** la sombra de la distribución de
  Wigner proyectada sobre un eje girado *a*·π/2, así que girar el plano y mirar
  su sombra no es una metáfora de la fraccional: es la fraccional.

Se apoya en `manim_extensions/transformadas.py`, con
`studio/tools/sonda_transformadas.py` — **91 invariantes, cada uno con su
contraejemplo**. Esa última parte es la que sirve: un invariante que solo
comprueba que el caso bueno sale bien no distingue una implementación correcta
de una que devuelve siempre lo mismo.

Entrega: 20 piezas, **11.05 min** en 1080x1920 @ 60 fps, 19 costuras a
0.0000/255, sin pista de audio.

## Curso 33 — Señales y sistemas (vertical, estilo LIENZO, **mudo**)

Dieciocho piezas más intro y cierre sobre lo que un **sistema** le hace a una
señal: el impulso, la respuesta al impulso, la convolución, el escalón, las
cuatro propiedades que hacen manejable un sistema (linealidad, invarianza,
causalidad, estabilidad), cómo se componen (cascada, realimentación, la
ecuación en diferencias), lo mismo visto en frecuencia (autofunciones,
respuesta en frecuencia, fase y retardo de grupo, resonancia) y los límites
(transitorio, un filtro, saturación).

La decisión que más importa es **la capa que ocupa**. Un curso clásico de
señales y sistemas contiene Fourier, Laplace y Z — es decir, el curso 32
entero— y roza el 27. Este ocupa la capa de encima: la caja que convierte una
entrada en una salida, y toda su gracia es que con **una sola medida** —la
respuesta al impulso— la caja queda determinada para siempre. Las
transformadas se citan como herramienta y no se explican; la pieza 12
(*autofunciones*) es la bisagra, porque explica **por qué** existe el curso 32
—una exponencial entra en un sistema lineal y sale igual salvo un número— sin
volver a contar ninguna transformada.

### Lo que enseñó este curso, y trasciende al curso

Nueve de las dieciocho piezas volvieron corregidas, y **siete de esas nueve
fallaban de la misma manera**: una cifra o un rótulo que afirmaba algo sobre
el **sistema** cuando en realidad hablaba del **cuadro** en que lo dibujamos.
El catálogo tenía esa trampa escrita solo para el eje de frecuencia ("la
profundidad de un nulo cambia con el número de puntos; su posición no"), y
apareció en cinco disfraces distintos:

| Disfraz | Medido |
|---|---|
| La ventana de muestras | "60 muestras que duran" sobre una respuesta que no se acaba nunca; con N=200 diría 200 |
| Una respuesta sin asentar | "valor final" con 0.1381 de vaivén en las ocho últimas muestras dibujadas |
| La rejilla de la FFT | la amplificación de un Q=40 sube de 37.38 a 38.25 solo al afinar la malla |
| La escala del panel | dos sistemas dibujados a la misma altura con escalas que difieren 17.8× |
| Los decimales | el cuarto decimal del valor final lo ponía el tamaño de la ventana |

La regla que sale de ahí, y que conviene aplicar antes de rotular cualquier
cifra: **mídela con dos ventanas y dos rejillas distintas, y si se mueve, no
es del sistema.** A veces la salida no es cambiar el cálculo sino la
precisión: las tres amplificaciones de la pieza 15 solo son del sistema
redondeadas a entero (4, 11, 38), y ahí se quedaron.

En **cinco de los nueve casos el error estaba en el encargo**, no en el
trabajo del agente. Y dos veces un agente devolvió una corrección con una
medida encima: uno demostró que exigir igualdad *bit a bit* entre dos
convoluciones calculadas por caminos distintos era imposible (1.33e-15, el
ULP de la máquina) y propuso la tolerancia que sí distingue un desfase real;
otro, que el filtro especificado en su brief tenía ganancia 0.794 donde su
plano necesitaba 1.000, así que el plano habría enseñado lo contrario de su
propio rótulo.

### Defectos de librería, corregidos en la librería

- **`deformar_fases` sí cambiaba las amplitudes**: para que la salida sea real
  el bin de Nyquist tiene que ser real, `irfft` lo fuerza tirando su parte
  imaginaria, y girarlo movía su módulo (0.4857 → 0.1014) bajo un rótulo que
  decía "las mismas amplitudes". Lo grave es que **la sonda ya afirmaba esa
  propiedad y pasaba** — no por suerte del código sino de la señal elegida.
  Un invariante que solo prueba tu caso no prueba la propiedad.
- **`sis.cero` ponía el eje en el suelo del cuadro**, que solo es el cero si el
  rango empieza en cero. El molde del curso dibuja áreas positivas, así que se
  copió intacto a piezas cuyos datos bajan de cero: la raya caía bajo el cero
  verdadero y el dibujo afirmaba que las muestras negativas eran positivas.
  Ahora se calcula, y aborta si el cero no cae dentro del rango.
- **`cola` no es "cuánto dura"**: mide dónde se acaba contando desde el origen,
  así que un impulso en la muestra 20 tiene cola 21 y dura 1 → `sis.duracion`.
- **Cuatro huecos de API que obligaban a una pieza a pescar cosas de un grupo
  por índice o por tipo** — y todos se rompen en silencio, no con un error:
  `sis.tallos(colores=)`, `sis.lazo(color_entrada=, color_salida=)` con
  `g.vuelta`, `tf.barras(rango_y=)` y `L.morfeo` (que es `relevo` para un
  dibujo que se transforma en vez de relevarse).
- **`sis.banda` pintaba en `LINEA`**, el azul de las rejillas: una banda de
  tolerancia no es mobiliario, es el umbral que la pieza afirma, y era
  invisible.

### Y una corrección a la trampa del acento

Estaba escrita como "el ámbar traslúcido sobre este azul da verde oliva". La
transparencia no es la causa: lo es el **ancho efectivo**. Dos trazos
**opacos** de colores distintos, uno fino sobre una banda gruesa, se funden en
el mismo oliva si el de encima mide un par de píxeles y casi todo él es borde
antialiasado. Cuando dos curvas tienen que verse *coincidir*, la de encima va
**a trozos**: en cada hueco se ve el color puro de abajo y en cada trazo el de
arriba, y "coinciden" se lee porque se ven **dos** curvas, no una mezcla. Tres
piezas de este curso usan ese remate y las tres se ven iguales.

Entrega: 20 piezas, **10.82 min** en 1080x1920 @ 60 fps, 19 costuras a
0.0000/255, sin pista de audio.

## Curso 34 — Funciones con nombre propio (vertical, estilo LIENZO, narrado)

Dieciocho funciones más intro y cierre. Cada pieza presenta **una**, con el
problema que la obligó a existir y una cifra que sólo ella sabe dar: gamma
interpola el factorial (Γ(½) = 1.7725), la W de Lambert despeja lo que no se
despeja (0.5671), la integral elíptica da el periodo de verdad de un péndulo
(18.03 % más que la fórmula del instituto), Fresnel curva sin tirones,
Chebyshev reparte el error por igual (59.82 → 0.0177), Bessel dibuja un
tambor (2.4048), Chladni el sonido, Airy el borde de una sombra (−2.3381),
Legendre la forma de un planeta (21.4 km), la catenaria un cable (22.19 % más
que el vano), Weierstrass una curva sin pendiente, Cantor una escalera que
sube sin subir, Cauchy una campana sin media, Lorenz una curva que no se
repite, la cicloide el camino más rápido (0.8053 s), Lissajous una razón de
frecuencias que se lee contando, zeta los primos (14.1347) y la superfórmula
mil formas con cuatro números.

**La capa que ocupa** es la decisión que más importa, porque "funciones
llamativas" toca cuatro cursos publicados. El 11 cuenta qué patrón sale de
repetir una regla; el 12, cuándo esa iteración deja de ser predecible; el 26,
la autosemejanza y la dimensión; el 32, cómo se cambia de dominio. Éste
cuenta **la función como personaje**: tiene nombre propio porque ninguna
combinación de las elementales hacía su trabajo. La mariposa de Lorenz entra
como *objeto* —una curva que no se corta nunca a sí misma— y su cifra es
cuánto tarda una diferencia de una milmillonésima en notarse (19.44 s), no la
dimensión ni el exponente de Lyapunov, que son de los otros dos cursos.

**Primer curso narrado desde el principio con el ritmo del curso mudo.** Los
cursos 32 y 33 nacieron mudos y se les añadió voz después; éste se escribió
sabiendo que llevaría voz y aun así mantiene el suelo de 1.8 s de
`Pieza.leer()`. Dos razones medidas: la voz de esta casa **puntúa** en vez de
narrar de corrido y necesita huecos donde caber, y la mitad de Instagram ve
los reels sin sonido, así que una pieza que sólo se entiende con voz está a
medio hacer.

### Lo que enseñó este curso, y trasciende al curso

**Una función especial mal implementada no se ve mal**: dibuja una curva
razonable y saca una cifra plausible con cuatro decimales. La única defensa
es una sonda de invariantes escrita ANTES que los clips, que le pida a cada
una la propiedad que sólo cumple si está bien —la reflexión de Euler, la
recurrencia de Bessel, Ai'' = x·Ai, la ortogonalidad de Legendre, el periodo
medido sobre un péndulo integrado de verdad— **y su contraejemplo**. La del
curso 34 llegó a 177 invariantes y tumbó siete cosas antes de dibujar nada.

Tres merecen quedar escritas porque no son de este curso:

- **Por dos puntos pasan infinitas circunferencias, y elegir el competidor
  débil es una forma de mentir que no deja rastro en ninguna cifra.** El arco
  de la carrera de la cicloide, tangente a la horizontal, tardaba 4.11 s
  contra 0.8053: un espantapájaros. El de Galileo, tangente a la vertical,
  pierde por un 2.2 %, y que pierda por poco es lo que hace buena la pieza.
- **Hay cifras cuyos decimales son de la truncatura y no de la función.** La
  pendiente de Weierstrass se mueve un 0.25 % al sumar dos términos más, así
  que se rotula entera: lo que la pieza afirma no es el valor, es que la
  sucesión no se para.
- **Una cifra que habla de un objeto y un dibujo que es un corte no dicen lo
  mismo.** "4 paralelos quietos" junto a un perfil donde se cuentan ocho
  cruces: cada paralelo nodal corta el meridiano dos veces. Se rotula lo que
  se puede contar en pantalla, y se marcan los puntos para que se cuente.

### La hoja de contactos de las portadas, como paso fijo del cierre

Ver las veinte portadas juntas destapó que diecisiete llevaban el nombre
pelado y una llevaba artículo ("LA ELIPTICA"). Pieza a pieza no se ve. El
curso 33 dejó escrito que esa hoja merecía ser un paso fijo; aquí lo fue, y
encontró lo que tenía que encontrar. Costó un re-render y un re-mux de una
pieza — y ninguna duración se movió, porque la portada es una coreografía de
tiempos fijos que no depende de lo larga que sea la palabra.

### Dos cosas de infraestructura que no son del curso

- **La imagen de render ya no se podía reconstruir.** Debian bullseye llegó a
  su fin de vida: `deb.debian.org` devuelve 404 en todo `bullseye-security` y
  el Release principal venció. Ahora apunta al *snapshot* del que salió la
  imagen base. No se sube a bookworm a propósito: cambiaría Pango y las
  fuentes, y con ellas las medidas sobre las que están calibrados los
  guardianes de `lienzo.py`.
- **`manim` y `numpy` quedan pineados a las versiones de producción** (0.20.1
  y 2.5.1). Sin el pin, la reconstrucción se trajo manim 0.21.0 y el render
  local habría dejado de ser el de producción sin que nada avisara.

## Curso 35 — Cálculo visible (vertical, estilo LIENZO, narrado)

Dieciocho piezas más intro y cierre. Cada una es **una afirmación del
cálculo de una variable cuya prueba se puede mirar**, y termina en una cifra
que el render calcula: la secante que deja de girar (1.0000), la banda de
tolerancia que siempre encuentra respuesta (0.0166), la curva que de cerca
es su tangente y se despega cuatro veces menos en cada zoom, las cuatro
tangentes de e^x que cortan el eje exactamente una unidad antes (1.0000), el
radar que te pilla dos veces a 87.5 km/h, el zigzag de Newton que duplica
los decimales, la lata que gasta 264.4 cm² y el valle plano que hace que
fallar un 10 % cueste 1.07 %, la pinza de Riemann que se cierra sobre
0.3333, el área que crece al ritmo de la altura (2.1093 = 2.1093), la franja
de la hipérbola que se estira al doble sin cambiar de área (0.6931), la
escalera que se pega a la circunferencia y sigue midiendo 4.0000 cuando ella
mide 3.1416, la campana que gira para poder integrarse (√π = 1.7725), la
esfera que es dos tercios de su cilindro rebanada a rebanada (0.6667), el
círculo que se desenrolla en un triángulo (78.5398), el anillo de servilleta
que no depende de su esfera (113.10 cm³), la trompeta que se llena con π y
no se puede pintar, el polinomio de Taylor que abraza el seno hasta 4.00 y
la serie armónica que con un millón de sumandos va por 14.39.

**La capa que ocupa.** El cálculo toca cuatro cursos publicados. El 21
cuenta el espacio que *fluye* —campos, gradiente, divergencia, Green,
Stokes—, el 26 la dimensión, el 32 el cambio de dominio y el 34 las
funciones con nombre propio. Éste ocupa **el cálculo de una variable contado
por el dibujo que lo demuestra**: no es un temario ordenado por capítulos,
es el catálogo de sus demostraciones visuales. La única pieza que sale al
plano es la campana, y sale para volver a entrar: gira la curva para poder
integrarla en una sola variable.

### Lo que enseñó este curso, y trasciende al curso

**Un dibujo correcto puede demostrar lo contrario de lo que dice.** La
escalera que envuelve la circunferencia sale de repetir el primer cuadrante
girado; al invertir además el orden de los puntos, el camino volvía sobre
sus pasos y aparecían tramos en diagonal —que es justo lo que una escalera
no tiene—. Medía 6.82, o sea 2π. El fotograma se veía perfecto. La sonda de
`calculo.py` (**231 invariantes, 0 fallos**) lo cazó antes de dibujar nada,
junto con otras tres cosas.

Tres merecen quedar escritas porque no son de este curso:

- **Una resta de dos números gigantes miente antes de fallar.** La corona
  del anillo de servilleta es `(R²−y²)−c²`. Con R = 10⁶ devuelve 113.0996 en
  vez de 113.0973: un número creíble, con dos decimales, que nadie
  discutiría. Con el radio de un planeta en centímetros devuelve cero. El
  guardián no se pone donde sale cero, se pone donde empieza a desviarse.
- **`plomada` cuelga del cero, y no todos los cuadros lo contienen.** En una
  curva de coste que va de 250 a 322 se iba siete unidades por debajo del
  dibujo; el grupo pasaba a medir el triple de lo que se ve, `encajar` lo
  encogía entero y el render abortaba por el guardián de *legibilidad* con
  "el rótulo más pequeño mide 0.101". El síntoma no señalaba la causa.
- **Un destino de `Transform` construido fuera del grupo llega
  descolocado**, porque no ha pasado por `encajar`. Los destinos viajan
  dentro del grupo con el trazo apagado y se sacan justo después de
  `L.escena`; de propina, mientras están dentro fijan el *bounding box* y el
  encaje no cambia de un estado a otro.

### El zoom se gasta una vez

El curso 34 hizo cuatro *zooms* sobre Weierstrass para enseñar la excepción
—una curva que no se alisa nunca—. Aquí se hace uno, en la pieza 03, para
enseñar la regla. Y tiene que ser **isótropo**: si en cada ventana se
reajusta el rango vertical al recorrido de la curva, la curva sale igual de
curvada en las cuatro y la pieza demuestra lo contrario de lo que dice.

### La entrega

| | |
|---|---|
| Película | `exports/verticales/calculo/calculo_vertical.mp4`, **591.81 s (9.86 min)**, 1080x1920 @ 60 fps, 25 MB |
| Piezas sueltas | las **20 sonorizadas**, que son el producto para Instagram |
| Pico del montaje | **−2.0 dB** |
| Costuras | **19 a 0.0000/255** |
| Verificación | 0 fallos, 63 avisos (todos de `estima()`, que cuenta palabras antes de sintetizar) |

**La voz entró a la primera otra vez.** 97 frases escritas contra los huecos
*medidos* con `sonda_tiempos_voz.py` y a **2.2 palabras por segundo de
hueco**; `alinear_voz.py` no devolvió ni un solape ni una cola corta en las
18 piezas, y la cola más corta quedó en 1.53 s sobre un mínimo de 0.8. Es la
segunda vez que ese margen del 12 % sobre la velocidad documentada compra no
tener que corregir piezas a mano.

Con un matiz nuevo que conviene dejar escrito: **esa sonda hay que correrla
sobre el `scene.py` recién compuesto**. Aquí las escenas se copiaron al
scratchpad *mientras* el render de validación todavía las estaba
recomponiendo, y una pieza se midió con una versión vieja: el manifiesto
decía 29.9 s y el render dio 30.5. Lo avisó `render_vertical` ("la voz se
alinea con el manifiesto: cuádralos antes de narrar"). Tras volver a medir,
las 18 piezas de contenido coinciden **al centésimo** con su render.


## Curso 37 — Rendimiento de SQL Server

Familia horizontal de **21 lecciones / 84 clips** (7 modulos x 3), estilo
CONSOLA, narrada sin subtitulos, ~48 min. Libreria `sqlperf.py`. Primer
curso de la coleccion sobre bases de datos y primero **sin la etiqueta
«Modulo 0N»** en pantalla: el dueño la considero ruido visual y
`hud_modulo()` aborta el render en estos `style_block`.

El arco: *una consulta no se paga en segundos, se paga en paginas*. De la
pagina de 8 KB (1.1) a una tienda que baja de 53 s a 3.9 s (7.3), pasando
por arboles B, lookups, indices que cubren, sargabilidad, histogramas,
parameter sniffing, Query Store y bloqueos.

Rol de color nuevo: **ambar = lo que midio SQL Server 2025** (lecturas
logicas, segundos). El cian sigue siendo «calculado aqui»: la libreria
reproduce fila por fila el generador determinista de la base de ejemplo, y
sus conteos coinciden con el motor (el cliente 1 da 149,970 filas, el
EQ_ROWS del histograma real).


## Curso 38 — Radio definida por software (familia «SDR»)

Familia horizontal de **24 lecciones / 96 clips** (8 modulos x 3), estilo
CONSOLA, narrada sin subtitulos y sin «Modulo 0N», ~57 min. Libreria `sdr.py`
con sonda de 130 invariantes. Es la version completa del curso 8 («SDR: la
radio hecha software», 8 clips), que queda como introduccion divulgativa.

El arco: *una radio es una cadena de aritmetica y cada eslabon deja una huella
medible*. Del ADC de 8 bits y el caudal de 38.4 Mbit/s (1.1) a la estacion
completa que recibe una imagen de Meteor-M con margen de 16.9 dB (8.3), pasando
por mezcla e IQ, ruido y ganancia, NCO y diezmado, FM estereo con RDS,
Costas y Gardner, ADS-B, AIS, LoRa, Doppler, Viterbi y GPS bajo el ruido.

Roles de color propios: fucsia = lo que PONE el receptor (LO, NCO, lazo);
gris = norma, hoja de datos o parametro elegido. Las senales «reales» se
construyen a norma y se decodifican en pantalla (aviones, barcos y emisoras
ficticios, declarados como tales; un mensaje ADS-B real sirve de oraculo).

