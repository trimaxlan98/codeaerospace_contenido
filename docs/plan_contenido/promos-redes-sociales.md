# Promos de redes sociales (formato nuevo, experimental)

Rama `exp/promos-redes`. Encargo 2026-08-27: *"clips de promocion de los
cursos para redes; no un resumen del curso, sino videos interesantes POR SI
MISMOS, visualmente atractivos, con bucle — que al terminar empiece y el
usuario lo repita. Sin subtitulos: solo audio (narracion, sonidos o ambos).
Horizontal esta bien pero probemos vertical, y vertical de verdad, no el
horizontal con bandas negras. Empezar con poco."*

## Qué es un promo (y qué no)

Un promo **no** es una leccion ni un resumen del curso:

| | Leccion (cursos) | Promo (redes) |
|---|---|---|
| Duracion | 28–45 s por clip | **8–15 s** |
| Formato | 16:9 | **9:16 real**, y 16:9 del mismo codigo |
| Texto | pies, rotulos, cifras | **solo la cifra** y su etiqueta HUD |
| Audio | narracion TTS + marca | **SFX en bucle** (o voz, si algun dia) |
| Final | cierre a pantalla limpia | **el estado inicial**: el video se repite solo |
| Verdad | toda cifra calculada | igual: **toda cifra calculada** |

Lo que NO cambia: el tema `code_brand`, la libreria del curso del que sale
el promo, y que ningun numero en pantalla este inventado.

## El bucle es la pieza

La regla dura: **el ultimo frame tiene que ser el primero**. No se consigue
con un fundido: se consigue diseñando el clip como un ciclo que vuelve a su
estado de partida (aqui, "el polo solo"). `render_promo.py` lo **mide**:
compara los dos frames y da la diferencia media y el porcentaje de
subpixeles con salto visible. A ojo esto no se valida.

En el audio pasa lo mismo por otra via: la cama sonora **empieza y termina
en silencio de verdad** (la mezcla se pone a cero antes de que acabe el
video), asi el salto del final al principio no suena.

## Formato vertical: lo que costo averiguar

`manim render -r 1080,1920` da un lienzo de 1080x1920 **pero deja el mundo
de la escena en 16:9**: el contenido sale encajonado en una isla horizontal
con bandas negras arriba y abajo — exactamente lo que el encargo prohibia.
Hay que reconfigurar el mundo, y el orden importa:

```python
config.pixel_width, config.pixel_height = 1080, 1920
config.frame_height = 14.222...   # al fijar la altura, manim COPIA el
config.frame_width = 8.0          # valor a las dos: el ancho va DESPUES
```

Dos consecuencias buenas:

- **No hay deformacion**: el mapeo sigue siendo isotropico (un circulo es un
  circulo); lo unico que cambia es que cabe.
- **1 unidad = 135 px en los dos formatos** (1920/14.222 = 1080/8.0). Un
  `font_size` de 40 se ve igual de grande en vertical y en horizontal, asi
  que una escena bien compuesta solo necesita **recolocar** piezas, nunca
  re-dimensionarlas.

`code_brand` se adapta solo: `esquinas_hud` lee `config`, y `marca_agua` usa
`to_corner`. Lo unico que hubo que mover es la marca: en vertical la esquina
inferior derecha es **la columna de botones de Instagram**, asi que sube al
borde superior (`promo.marca_promo`).

## Zonas seguras

`promo.SEGURA` guarda, como fraccion del lado, lo que la app tapa. En
vertical: 10 % arriba, **20 % abajo** (autor, texto, CTA) y 14 % a la
derecha (corazon, comentarios, compartir). Si algo IMPORTA, cabe dentro.
`render_promo.py --guias` lo dibuja para comprobarlo.

## Lo que se construyo

| Pieza | Qué hace |
|---|---|
| `studio/content/manim_extensions/promo.py` | el lienzo (`formato()`), zonas seguras, `marca_promo()`, `guias()`, `fondo_seguro()` |
| `studio/tools/render_promo.py` | render a cualquier formato, sin la regla de 28–45 s, y **mide la costura del bucle** |
| `studio/tools/sfx.py promo` | cama sonora desde el bloque `audio` del manifiesto, ajustada a la duracion REAL del video; con un wav de voz, la mezcla por debajo |
| `studio/tools/narrar_promo.py` | sintetiza el texto ESCRITO A MANO del manifiesto y lo alinea a los instantes visuales (se ejecuta en el VPS) |
| `studio/content/promos/<slug>/` | `promo.json` + `style_block.py` + `escena.py` |
| `naturaleza.Filotaxis.girar_a()` | recoloca las semillas existentes (aditivo; `con_angulo` sigue igual) |
| `naturaleza.hueco_maximo()` | el circulo vacio mas grande que CABE en el disco: la medida honesta del desperdicio (aditivo) |

El formato se pasa por entorno (`PROMO_FORMATO`), asi que **una escena, dos
formatos**: `--formato vertical` y `--formato horizontal` salen del mismo
archivo.

## Promo 1 — "El angulo que la naturaleza eligio" (curso 14)

`studio/content/promos/filotaxis-angulo-aureo/`. 10.80 s, 1080x1920 @ 60 fps.

```
0.00  el polo solo                       <- estado de arranque Y de cierre
0.35  las semillas nacen del centro hacia afuera
3.75  se encienden los 5 brazos de la familia 21 (cian)
4.80  se apagan y se encienden los 8 de la familia 34 (violeta, al reves)
6.35  el angulo se desafina +1.15 grados y VUELVE: el patron se rompe y
      se recompone, y la cifra en pantalla lo cuenta
8.95  el disco se consume desde el filo hacia el polo
10.45 el polo solo                       <- el ultimo frame ES el primero
```

**Verificado**: bucle con diferencia media 0.000/255 y 0.000 % de subpixeles
con salto visible (identico al pixel); audio AAC 24 kHz mono con pico
−3.0 dBFS y los extremos a −78 dB y −91 dB. Salida:
`exports/promos/filotaxis-angulo-aureo/vertical.mp4` (no versionado).

## Cosecha de trampas (medida durante la produccion)

- **`-r` no basta para el vertical**: sin reconfigurar el mundo, el
  contenido sale en una isla 16:9. Y `frame_height` hay que fijarlo ANTES
  que `frame_width`, o el ancho se queda con el valor de la altura.
- **La calidad tiene que fijar el LADO CORTO, no el alto.** Fijando el alto,
  un 16:9 en "qh" salia de 3413x1920: eso no es mas calidad, es otro
  formato. (Lo destapo el primer render horizontal: 1706x960.)
- **El ultimo frame no se saca con `-ss dur-epsilon`**: si el salto cae
  detras del ultimo paquete, ffmpeg termina con exito y **no escribe nada**.
  Se decodifica la cola con `-update 1` y lo que queda es el ultimo frame.
- **Una semilla de tamaño cero sigue siendo un mobject.** Tras la animacion
  de colapso hay que `self.remove(disco)`: la costura se mide al pixel.
- **Que un brazo se lea como espiral depende de cuanto gira por semilla**:
  con m=8 son +20.1 deg/semilla y ~3.9 vueltas por brazo — cuatro brazos ya
  se leen como anillos concentricos, no como espirales. Con m=21 (+7.7 deg,
  ~0.55 vueltas) y m=34 (−4.7 deg, y gira al reves) salen los brazos del
  girasol. Dibujar la familia ENTERA tapa el disco: hay que elegir cuantos
  brazos.
- **Encender las semillas es mejor que dibujar curvas encima**: el brazo son
  de verdad esas semillas, y el disco no se llena de tinta ajena. Para
  volver al estado original hay que restaurar el **degradado** semilla a
  semilla (se reconstruye un disco gemelo y se copia su color), no un color
  plano.
- `always_redraw` con un `Text` cuesta un render de pango por frame: se
  enciende solo durante el barrido de la cifra y se apaga despues.
- El `.animate` de un VGroup lo sube al frente: si algo tiene que quedar por
  encima, `set_z_index`, no confiar en el orden.

## Promo 2 — "Por que 137.5" (curso 14)

`studio/content/promos/filotaxis-por-que-137-5/`. 13.30 s, 1080x1920 @ 60 fps,
con voz Charon. Es la pareja del promo 1: aquel enganchaba, este responde.

**El encargo era que el espectador APRENDIERA algo.** La decision de diseño
que manda sobre todas las demas: en redes mucha gente mira en silencio, asi
que la explicacion **no puede vivir en la voz**. Entra por el contraejemplo:

```
0.00  el polo solo                       <- estado de arranque Y de cierre
0.35  las semillas nacen con 90 grados: cuatro rayos y cuatro cuñas vacias
2.75  se dibuja el hueco: el circulo vacio MAS GRANDE que cabe en el disco
3.95  el angulo barre de 90 al aureo; los rayos se disuelven y el hueco se
      cierra, con la cifra contandolo
8.15  el hueco nuevo, 8 veces mas pequeño, junto al fantasma del viejo
11.35 el disco se consume desde el filo hacia el polo
12.95 el polo solo                       <- el ultimo frame ES el primero
```

La cifra del hueco **no se rotula: se dibuja**. `hueco_maximo` mide el radio
del circulo vacio mayor (1.2239 a 90 grados, 0.1537 en el aureo: **8.0 veces**)
y el aro que se ve en pantalla ES esa medida. La comprobacion de que la
funcion es correcta: para cuatro rayos la geometria analitica da 1.226 y la
malla mide 1.2239.

**Voz** (3 frases, 16 palabras, alineadas a los instantes visuales):
"Cada semilla nace girando igual." / "Con noventa grados dejan huecos." /
"El angulo aureo no deja ninguno."

**Verificado**: bucle identico al pixel; audio AAC 24 kHz mono con pico
−2.1 dBFS, silencio en los extremos (−90 dB al principio, −42 dB al final) y
la voz callada 0.8 s antes del ultimo frame. Salida:
`exports/promos/filotaxis-por-que-137-5/vertical.mp4`.

## Cosecha de trampas del promo 2

- **La peor, y la que casi se publica sin verse:** un `updater` sobre un
  mobject que NO participa del `play` se ejecuta pero **no se ve**. El
  renderer cachea en una imagen estatica todo lo que no es "moving mobject",
  asi que el disco se quedaba clavado en la cruz de 90 grados mientras la
  cifra —esa si, animada— subia hasta 137.5. El barrido tiene que ir como
  **animacion del propio disco** (`UpdateFromAlphaFunc`), no como updater
  suelto. **El promo 1 tenia el mismo fallo y paso la primera revision**: su
  patron "cambiado" era en realidad el aureo de siempre; se descubrio al
  comparar los dos promos. Los dos estan corregidos y re-renderizados.
- **Charon narra a ~1.7 palabras/s, no a 2.2**: 25 palabras pedian 14.5 s
  para un video de 12. Para un promo, contar las palabras a 1.7 w/s.
- **La voz tiene que CALLAR antes del ultimo frame.** Ajustada exacta a la
  duracion, terminaba a −23.5 dB en el ultimo frame y el salto del bucle se
  oia. El respiro largo antes del colapso no es estetico: es lo que hace que
  el audio tenga cola de silencio.
- **Una medida "del hueco mas grande" sin acotar al disco miente**: el
  circulo se sale por el borde (daba 2.15 en vez de 1.35 a 90 grados). El
  radio en cada punto es el menor de dos: hasta la semilla mas cercana y
  hasta el filo.
- **Antes de diagnosticar un defecto visual, ampliar el frame.** El aro
  pequeño parecia una flor de seis petalos; ampliado x4 es un circulo
  perfecto y lo que muerde son las cuatro semillas que lo tocan — que es
  justo lo que significa "circulo vacio maximo".
- A 90.3 grados los cuatro rayos se convierten en cuatro brazos curvos: el
  barrido regala su propio momento visual a los pocos frames de arrancar.

## Lote de la noche del 2026-08-27

Encargo: *"mas videos de extractos de los demas cursos, muy buenos y
llamativos, hechos con cuidado para que funcionen bien"*. Uno por curso, y
cada uno se termina ENTERO (visual -> qh -> voz -> mezcla -> verificado ->
commit) antes de empezar el siguiente: si la noche se corta, lo que hay
esta acabado, no a medias.

| # | Promo | Curso | Estado |
|---|---|---|---|
| 3 | El efecto mariposa | 15 · Caos | **LISTO** 12.90 s · bucle 0.000 · voz |
| 4 | La tirania del cohete | 17 · Tsiolkovsky | **LISTO** 11.65 s · bucle 0.006 · voz |
| 5 | Los 38 microsegundos del GPS | 16 · Relatividad | **LISTO** 11.70 s · bucle 0.050 % (*) · voz |
| 6 | Cuando el ruido se come el simbolo | 24 · Comunicaciones | **LISTO** 11.10 s · bucle 0.000 · voz |
| 7 | Que es un determinante | 22 · Algebra lineal | **LISTO** 12.20 s · bucle 0.014 · voz |
| 8 | El muro del sonido | 10 · Aerodinamica | **LISTO** 11.70 s · bucle 0.010 · voz |
| 9 | El secreto que se grita en publico | 19 · Criptografia | **LISTO** 12.50 s · bucle 0.001 · voz |
| 10 | Nadie manda en Internet | 25 · Protocolos | **LISTO** 12.80 s · bucle 0.000 · voz |

### Promo 3 — "El efecto mariposa" (curso 15)

`studio/content/promos/caos-efecto-mariposa/`. 12.90 s, 1080x1920 @ 60 fps.
Dos trayectorias de Lorenz separadas por **una millonesima** se dibujan a la
vez: durante 13.2 s simulados son la MISMA linea (el gemelo va encima) y
despues se van a alas opuestas. La cifra de abajo es la distancia euclidea
real paso a paso — se queda en `0.000` un buen rato y termina en **25.9**.

- El corte del trazo se ELIGIO midiendo: a t=22 s las dos van por alas
  opuestas con d=25.90; en t=20 o t=24 vuelven a coincidir de casualidad y
  el remate se desinfla.
- Lyapunov medido en el tramo recto: 0.807 /s.
- Verificado: bucle identico al pixel, audio a −1.6 dBFS con los dos
  extremos a −91 dB.

### Promo 4 — "La tirania del cohete" (curso 17)

`studio/content/promos/cohete-la-tirania/`. 11.65 s. Empieza con el cohete
ENTERO en cian (a dv=0 todo es carga util) y el combustible se lo va
comiendo mientras sube el impulso. La referencia **ORBITA 9388** esta en
pantalla desde el primer frame, asi que se ve la cifra subir hacia ella y
**pararse en 8840**: con motor quimico y una sola etapa la carga util llega
a cero antes de llegar. Remate en rojo: **FALTAN 548 M/S**.

- Todo medido con `cohete.py`: `dv_leo` = 9388 (orbital calculada 7788 +
  perdidas citadas 1600), `dv` de carga cero = −ve·ln(eps) = 8840.1, y las
  tres franjas suman 1 exacto en todo el barrido.
- El modelo da carga util NEGATIVA pasado ese punto (−1.26 % a 9388): esa
  es la tesis del curso, pero una franja de altura negativa no se dibuja,
  asi que el barrido se para justo en el cero y el rojo lo cuenta.

### Promo 5 — "Los 38 microsegundos del GPS" (curso 16)

`studio/content/promos/gps-38-microsegundos/`. 11.70 s. La cadena completa
en una pantalla: arriba la CAUSA (**ADELANTA 38.5 MICROSEGUNDOS**, que es
−7.21 de relatividad especial +45.72 de general), en medio el satelite
dando su dia de trabajo, y abajo la CONSECUENCIA subiendo hasta
**11.5 KM** de error de posicion sin corregir (cada microsegundo son 300 m
de tiempo de vuelo de la luz).

- El bucle lo cierra la fisica: un dia de GPS son **dos orbitas exactas**,
  asi que el satelite termina donde empezo.
- Trampa cazada a tiempo: `f"{38.50:.0f}"` escribe **39**, justo la cifra
  que delata un rotulo mal hecho. Un decimal y a la vista.
- El satelite de fabrica es un punto de dos pixeles en un telefono: se
  escala x2 y se le pone una estela de cometa (0.22 de vuelta) para que en
  la segunda vuelta, con la orbita ya pisada, se siga viendo avanzar.

### Promo 6 — "Cuando el ruido se come el simbolo" (curso 24)

`studio/content/promos/qam-el-ruido/`. 11.10 s. Una constelacion 16-QAM con
**500 envios**: al bajar la señal las nubes crecen hasta rozar la del vecino
y el receptor decide mal. Los que caen en region ajena se ponen rojos y se
cuentan: **31 de 500** en el peor momento.

- **El ruido es una realizacion gaussiana FIJA que se escala por la sigma de
  cada Eb/N0** (la misma formula que `awgn`). Asi la nube respira en vez de
  parpadear como estatica de television, y sigue siendo AWGN legitimo: los
  500 dan 6.2 % de error a 7 dB frente al 6.69 % del Monte Carlo de 200 000.
- **El barrido para en 7 dB, no en 6**, y la razon es pedagogica: a 7 dB la
  nube de cada simbolo (3σ = 1.04 u) casi toca la del vecino (1.39 u) y se
  VE por que falla; a 6 dB el cuadro es confeti y se pierde la rejilla.
- La escala de la constelacion se bajo de 3.05 a 2.2 u: con la primera, la
  nube del peor momento se salia del lienzo por los cuatro lados.

### Promo 7 — "Que es un determinante" (curso 22)

`studio/content/promos/determinante/`. 12.20 s. La respuesta sin una sola
formula: la rejilla se inclina bajo **M(s) = [[1,s],[s,1]]**, el cuadrado
unidad se vuelve paralelogramo y la cifra es su area. En s=1 la matriz es
singular y el plano ENTERO se aplasta sobre la recta y=x con el
determinante en **0.00** exacto.

- La cifra es `paralelogramo(pl, M).area` (area con signo de las columnas):
  lo que se ve y lo que se lee son la misma cuenta.
- La familia se eligio para que el barrido sea monotono (det = 1 − s²) y
  para que el estado inicial vuelva solo, que es lo que cierra el bucle.
- `pl.aplicar(M)` reconstruye la rejilla viva cada frame sin animar: es lo
  que permite meter la transformacion dentro de un `UpdateFromAlphaFunc`.

### Promo 8 — "El muro del sonido" (curso 10)

`studio/content/promos/muro-del-sonido/`. 11.70 s. Cada circunferencia es el
sonido emitido hace k intervalos. Por debajo de Mach 1 los frentes se
adelantan —el aire se entera de que vas—; **a Mach 1 son todos tangentes en
la propia fuente**, que es la pared; y por encima la envolvente es el cono
de Mach, con su semiangulo medido (**34 grados a Mach 1.8**).

- Todo sale de `frentes_moviles` y `angulo_mach`: el dibujo a Mach 1 es
  tangente por geometria, no por un ajuste a ojo.
- El dibujo se **gira 90 grados** para que la fuente suba y la estela caiga:
  asi una figura naturalmente horizontal llena el vertical. Como en la
  construccion la fuente esta en el origen, girar alrededor del origen la
  deja quieta y basta un `shift`.
- Trampa: `next_to` respecto de una etiqueta VACIA no mide nada, y el
  rotulo del cono aparecio en mitad del dibujo. Los renglones que a veces
  estan vacios se posicionan por coordenada, no por vecindad.
- Trampa de voz: los `t_inicio` tienen que dejar sitio a la frase anterior.
  Con 0.8 / 4.0 / 7.4 cada frase empujaba a la siguiente y la cadena
  terminaba pegada al ultimo frame — es decir, el bucle sonaba. Con
  0.8 / 4.5 / 8.0 la voz acaba 1.3 s antes del final.

### Promo 9 — "El secreto que se grita en publico" (curso 19)

`studio/content/promos/secreto-en-publico/`. 12.50 s. Diffie-Hellman con los
numeros de juguete REALES del curso (p=23, g=5): Ana guarda un **6**, Beto un
**15**, se gritan un **8** y un **19** por un canal que ve todo el mundo, y
los dos acaban con el mismo **2**. El color lo cuenta sin palabras: ambar lo
privado (no se mueve nunca), cian lo publico (lo unico que cruza la linea),
verde el secreto. Pie: **EL VERDE NUNCA CRUZO**.

- Tres columnas por persona (privado / recibido / secreto): en la primera
  version el "19" y el "2" quedaban a 1.1 u y se leian como **192**.
- Los dos numeros publicos cruzan por carriles distintos para no pisarse.

### (*) La unica costura que no es cero

El promo del GPS marca 0.050 % de subpixeles distintos (los otros nueve
estan en 0.000 %). Se persiguio hasta el final: NO es la estela acumulando
dos vueltas —eso se normalizo con un modulo, y la cifra no cambio— sino el
**antialiasing del trazo curvo** al reconstruirlo con `become`. Recortando
la zona y mirandola al 100 % los dos frames son indistinguibles. Se deja
asi, anotado, en vez de fingir que es cero.

### Calibracion de la voz (vale para todos los promos)

Charon narra a **2.3–2.6 silabas por segundo, contando pausas** — no a
2.2 palabras/s, que es lo que yo suponia el primer dia. Y hay una trampa
peor que quedarse largo: **si dos `t_inicio` se solapan, el ensamblador
empuja la frase siguiente**, la cadena se pega al ultimo frame y entonces
el bucle SUENA. Regla: ≥ 4.5 s entre `t_inicio` para una frase de ~10
silabas, y si la duracion que reporta la herramienta es casi el limite, es
que se comprimieron los silencios. `narrar_promo.py` ahora **avisa** de ese
caso (antes solo avisaba si no cabia).

### Promo 10 — "Nadie manda en Internet" (curso 25)

`studio/content/promos/tcp-la-sierra/`. 12.80 s. La sierra de TCP dibujandose
en directo: la ventana sube un paquete por viaje hasta que algo se pierde
(marca roja) y entonces se parte por la mitad. Al final aparece la media
MEDIDA de la traza: **27.6**. La leccion es que no hay ninguna autoridad
repartiendo el ancho de banda — la red aguanta porque cada emisor frena solo.

- Las marcas rojas no se encienden a ojo: cada una compara el avance del
  trazo con su indice en la traza de `aimd`.

### La metrica del bucle tiene un suelo, y hay que descontarlo

Este promo marcaba 0.184 % de subpixeles distintos entre el primer frame y
el ultimo. No era una costura: **dos frames que en la escena son EL MISMO
dibujo (el 0 y el 1 del respiro inicial) daban exactamente la misma cifra**.
Es la cuantizacion del h264 sobre un fondo plano y oscuro. `render_promo.py`
mide ahora ese suelo y juzga la costura por encima de el; lo imprime al lado
para que la cifra no engañe en ningun sentido: sin descontarlo, un bucle
perfecto parece sucio, y con un umbral generoso uno sucio pasaria por
limpio.

## Verificacion final del lote (2026-08-27, madrugada)

Los diez `exports/promos/*/vertical.mp4`, medidos sobre el archivo que se
publica (no sobre el render intermedio):

- **10/10** en 1080x1920 a 60 fps, de 10.80 a 13.30 s.
- **10/10** con la costura del bucle en el suelo del codec (nueve en
  0.000 %, el del GPS en 0.050 % — ver arriba).
- **10/10** con audio AAC 24 kHz mono, picos entre −3.3 y −1.1 dBFS y los
  dos extremos en silencio (−73 a −91 dB), asi que el salto del bucle no
  suena.
- **8/10** con voz Charon alineada a los instantes visuales (los dos de
  filotaxis: el primero es solo SFX por diseño, el segundo lleva voz).

## Lo que falta (cuando se valide)

1. Verlos en un telefono de verdad, que es lo unico que no se puede
   comprobar aqui.
2. Sacar el 16:9 en `qh`: el camino esta validado en `ql` (960x540, bucle
   limpio), pero la composicion horizontal de cada promo merece una pasada
   de ajuste. Las escenas ya tienen su rama `else` escrita.
3. La voz ya esta resuelta (promo 2): `narrar_promo.py` se copia al VPS, se
   sintetiza, se baja el wav y `sfx.py promo` lo mezcla con la cama. Los
   ficheros temporales del VPS se borran al terminar.
4. Mas promos: un formato por curso, empezando por los mas visuales (caos,
   algebra lineal, protocolos).
5. Cuando el formato este validado, mergear a `main` y añadir la seccion de
   promos a la skill `curso-de-video`.
