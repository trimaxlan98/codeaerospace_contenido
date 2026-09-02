# Curso 32 · Transformadas (VERTICAL 9:16, estilo LIENZO)

**Encargo del 2026-09-02**, con las palabras del dueño:

> *"justo como este vamos a crear otro curso, este sera de Transformadas,
> como Fourier, Laplace, Zeta, Hartley, wavelet, etc. formato vertical
> lienzo azul, elimina la numeracion del tipo 01, 02 añade ruido"*

y a mitad de la preparacion, el dato que lo cambia todo:

> *"voy a tratar de publicarlas sin audio, sino con musica por lo cual que
> sea explicativa la animacion. sin saturar de informacion"*

## 0. Las cinco decisiones cerradas antes de escribir codigo

| Decision | Elegida | Consecuencia |
|---|---|---|
| El "ruido" | **Era el motivo de quitar la numeracion**, no una peticion de grano | La esquina superior izquierda queda VACIA. `Lienzo(modulo=None)`. Nada de textura: el azul sigue liso y las costuras siguen valiendo cero |
| Angulo | **Lo que vuelve facil** | Cada pieza abre con un problema imposible en su dominio y lo resuelve al cambiarlo. La transformada es la herramienta, no el tema |
| Tamaño | **20 piezas** = intro + 18 transformadas + cierre | ~10 min de montaje; 18 reels sueltos |
| Identidad de la pieza | **El nombre, solo al abrir** (portada de ~3 s) | Luego se apaga y queda el lienzo limpio |
| Sonido | **MUDO**, el dueño pone musica | Sin voz, sin cama de SFX. `unir_vertical.py --mudo` |

## 1. La regla que gobierna este curso

**Sin voz, la pantalla tiene que explicar — y no puede llenarse de texto.**
Las dos cosas a la vez solo salen si el trabajo se reparte en TRES piezas y
ninguna mas:

1. **La portada dice la tesis.** ~3 s: el nombre de la transformada y, bajo
   un filete ambar, que vuelve facil. `LAPLACE` / `DE DERIVADAS A ALGEBRA`.
   Es el unico sitio del curso donde se explica con palabras, y se explica
   UNA vez. Maximo 5 palabras en la linea de abajo.
2. **La animacion lo demuestra.** Un solo *verbo visual* por pieza: algo
   cruza de un dominio al otro y se convierte en otra cosa. Si hay que
   contarlo con una frase, el verbo esta mal elegido; se cambia el verbo,
   no se añade la frase.
3. **La cifra lo prueba.** Una sola, al final, medida en el render.

Lo que NO cambia respecto al curso 31: sigue prohibida la frase en pantalla.
Los rotulos son de <= 4 palabras y `lz.espaciado` + el guardian de
legibilidad siguen abortando el render. Que no haya voz **no es permiso para
subtitular**: es la razon de que el verbo visual tenga que ser bueno.

### Ritmo sin voz

El silencio ya no lo sostiene una frase hablada, asi que:

- **Todo estado importante se sostiene >= 1.8 s** despues de terminar de
  dibujarse. El ojo necesita leer el resultado, y sin voz nadie le dice
  cuando mirar.
- **Nada aparece de golpe si puede aparecer construyendose.** `Create`,
  `Transform` y updaters en lugar de `FadeIn` + `wait`.
- Duracion de pieza: **30-45 s** (tope duro por ambos lados, como siempre).

## 2. Las 20 piezas

Portada = nombre + tesis. Verbo = lo que se ve moverse. Cifra = el dato
grande del carril inferior (ambar si se calcula en el render).

| # | Pieza | Portada (tesis) | Verbo visual | Cifra |
|---|---|---|---|---|
| 00 | intro | — | Wordmark CO.DE + `TRANSFORMADAS` | — |
| 01 | Serie de Fourier | una esquina hecha de curvas | Senos que se suman uno a uno sobre la cuadrada gris | sobreimpulso de Gibbs, **no baja** |
| 02 | Transformada de Fourier | lo que dura poco suena a mucho | El pulso se estrecha arriba, el espectro se ensancha abajo | producto Δt·Δf, constante |
| 03 | DFT | el ordenador no sabe integrar | La curva se vuelve puntos; los puntos giran y se suman | fuga espectral en dB |
| 04 | FFT | el mismo resultado, muchas menos cuentas | La malla N² se pliega en mitades log₂N veces | factor de ahorro |
| 05 | DCT | tirar casi todo y que no se note | Bloque 8×8 → 64 coeficientes → se apagan los pequeños → vuelve | % de energia en 6 de 64 |
| 06 | Hartley | Fourier sin numeros imaginarios | El par (real, imaginario) se funde en un solo numero real | memoria: veces menos |
| 07 | Walsh–Hadamard | sin una sola multiplicacion | Ondas cuadradas ±1 en vez de senos; la mariposa solo suma y resta | multiplicaciones: 0 |
| 08 | Laplace | de derivadas a algebra | La EDO se vuelve cociente de polinomios; aparecen los polos | sobreimpulso predicho = medido |
| 09 | Transformada Z | el mismo truco, para el mundo a saltos | Un polo cruza el circulo unidad y la respuesta explota | radio del polo |
| 10 | Chirp-Z | hacer zoom en un trozo del espectro | Los puntos, repartidos por toda la circunferencia, se concentran en un arco | resolucion: veces mas |
| 11 | STFT | saber cuando, a medias | Una ventana desliza y pinta el espectrograma columna a columna | limite de Gabor |
| 12 | Wavelet | un zoom que se adapta | Ondas anchas para lo lento, estrechas para lo rapido; el salto se localiza | coeficientes no nulos |
| 13 | Fourier fraccional | girar el plano un angulo | El plano tiempo-frecuencia gira y la raya diagonal se vuelve un pico | angulo del maximo |
| 14 | Hilbert | la forma de lo que vibra | La envolvente abraza a la oscilacion; el desfase de 90° | amplitud instantanea |
| 15 | Mellin | lo mismo aunque cambie de tamaño | La forma se escala ×3: el espectro de Fourier se mueve, el de Mellin no | desplazamiento = 0 |
| 16 | Radon | ver dentro sin abrir | Sombras desde muchos angulos → sinograma → el interior aparece | proyecciones |
| 17 | Hough | encontrar la recta entre el ruido | Cada punto vota una senoide; las senoides se cruzan en un punto | votos en el pico |
| 18 | Karhunen–Loève | la base que hace tu propia señal | Los ejes giran hasta alinearse con la nube de puntos | % de varianza en 2 |
| 19 | cierre | — | La onda se contrae en el punto ambar, que se vuelve el punto de CO.DE | — |

**El arco**: 01-04 la familia de Fourier (de lo periodico al algoritmo),
05-07 las primas que resuelven un problema de ingenieria (comprimir, no usar
complejos, no multiplicar), 08-10 los sistemas y sus polos, 11-13 el
compromiso tiempo-frecuencia, 14-18 las que ya no son de frecuencia.

## 3. Lotes

| Lote | Piezas | Estado |
|---|---|---|
| A | 00 intro, 01, 02, 03, 04 | pendiente |
| B | 05, 06, 07, 08, 09 | pendiente |
| C | 10, 11, 12, 13, 14 | pendiente |
| D | 15, 16, 17, 18, 19 cierre | pendiente |

Cada lote recorre los 10 pasos entero antes de empezar el siguiente.

## 4. Contrato de la libreria

`studio/content/manim_extensions/transformadas.py`, dos mitades:

- **Numerica** (numpy puro, importable SIN manim, `default_rng(semilla)`):
  todas las cifras de la tabla anterior. Ninguna se escribe a mano en un
  clip. Guarda `_HAY_MANIM` como `esp32.py`.
- **De dibujo**: ejes minimos, curva, tren de muestras, plano complejo con
  circulo unidad, barras comparativas, malla 8×8, nube de puntos,
  sinograma. Todo con `RELLENO = 0.0` y trazo: el ambar traslucido sobre el
  azul da verde oliva (medido en el curso 31).

Sonda de invariantes: `studio/tools/sonda_transformadas.py`, se corre en el
contenedor antes de escribir un solo clip.

### Añadidos a `lienzo.py`

- `Lienzo.portada(nombre, tesis)` — la portada de ~3 s, con su propio
  guardian de longitud.
- `dos_dominios(arriba, abajo, rotulos)` — el panel partido que necesitan
  las piezas 02, 05, 11, 15 y 16.

## 5. Estado

- Rama `curso/transformadas-vertical`.
- Tablero: esta tabla de lotes.

## 6. Cosecha de trampas

### De la libreria (las cazo la sonda, 83 invariantes)

La sonda se escribio ANTES que ningun clip y saco **10 fallos a la
primera**. Dos eran errores conceptuales que habrian salido publicados:

- **La chirp-Z NO rompe el limite de Rayleigh.** La pieza 10 iba a afirmar
  que separa dos tonos que la DFT no separa, con los tonos a 0.4 ciclos por
  ventana. Eso no lo hace ningun metodo lineal: esa informacion no esta en
  la señal. Lo que la chirp-Z da son PUNTOS donde interesan, no
  resolucion. Tesis reescrita.
- **El sobreimpulso de Gibbs es el 8.95 % DEL SALTO, no de la amplitud.**
  Medido sobre la amplitud sale 17.9 %, que es un numero correcto que nadie
  reconoce. La sonda lo comparo con la constante y lo tumbo.
- **El primer nulo de un sinc no se busca con un umbral absoluto.** En una
  malla discreta el cero casi nunca cae sobre una muestra, asi que la
  busqueda se iba al ruido numerico de lejos: el producto tiempo-banda
  salia 42.9 en vez de 1. Se busca el primer MINIMO LOCAL bajo un corte
  relativo.
- **`searchsorted` desplaza cada voto medio escalon.** En el acumulador de
  Hough el pico se repartia entre dos filas y de 24 puntos alineados solo
  juntaba 11. Al vecino mas cercano: 22.
- **El angulo de un EJE propio vive modulo 180.** El signo de un
  autovector es arbitrario: la sonda leia -152.25 donde la nube estaba
  girada 27.75 grados, que es el mismo eje.
- **La FrFT por el nucleo continuo discretizado no es unitaria.** El
  termino cruzado gira 3.5 rad por muestra en los bordes de la malla —mas
  de pi, o sea alias— y la energia salia 155.3 donde tenia que salir 128.
  El intento de arreglarlo diagonalizando la DFT tampoco cerro: la
  sucesion de indices de Hermite en malla discreta no tiene un orden
  canonico estable (funcionaba en N=32 y 64 y no en 128). **Se cambio de
  camino**: la pieza 13 va por el teorema de Radon-Wigner, que es a la vez
  mas riguroso —los dos marginales de la distribucion de Wigner salen
  exactos— y mejor pedagogia, porque girar el plano y mirar su sombra ES
  el verbo visual de la pieza. Y de paso reutiliza el Radon de la 16.
- **Los ejes de la matriz de Wigner no son los de una FFT.** Su eje de
  frecuencia va al DOBLE (la correlacion se toma a desfase 2m), asi que la
  cresta de un chirp tiene pendiente 2*beta y no beta. La formula del
  angulo optimo decia 73.3 grados donde la medida daba 59.0: la formula
  estaba bien y los ejes no.

### De composicion (medidas en el molde)

- **`set_opacity` sobre una polilinea enciende el RELLENO** y la convierte
  en una mancha maciza blanca. En una curva se toca `set_stroke(opacity=)`.
- **`traza` no recorta.** Un solo valor fuera de `rango_y` manda la
  polilinea kilometros fuera del cuadro, el grupo mide el triple de la
  franja, `encajar` lo encoge y el guardian de legibilidad aborta con "el
  rotulo mas pequeño mide 0.09". Se elige la ventana de datos, no se
  recorta a posteriori.
- **Enseñar UNA curva no demuestra que algo no baja.** El zoom de Gibbs
  con una sola aproximacion no probaba nada; y las dos en la misma ventana
  dejaban el sobreimpulso en el 7 % de la altura del dibujo. La solucion
  fue dos zooms a distinta escala (0.081 y 0.0082 de ventana) con la misma
  raya arriba: el pico no se encoge, se ESTRECHA.
- **"TRANSFORMADA DE FOURIER" no cabe en la portada** ni al cuerpo minimo.
  Medidos los 20 nombres: entran todos menos ese. La pieza se llama
  FOURIER.
