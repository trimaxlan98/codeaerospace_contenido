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
| `studio/tools/sfx.py promo` | cama sonora desde el bloque `audio` del manifiesto, ajustada a la duracion REAL del video |
| `studio/content/promos/<slug>/` | `promo.json` + `style_block.py` + `escena.py` |
| `naturaleza.Filotaxis.girar_a()` | recoloca las semillas existentes (aditivo; `con_angulo` sigue igual) |

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

## Lo que falta (cuando se valide)

1. Ver el vertical en un telefono de verdad (es lo unico que no se puede
   comprobar aqui) y decidir si el disco crece o el ritmo cambia.
2. Sacar el 16:9 en `qh`: el camino esta validado en `ql` (960x540, bucle
   limpio), pero la composicion horizontal merece una pasada de ajuste — el
   bloque de la cifra pide subir un poco.
3. Decidir si algun promo lleva voz: la sintesis TTS **solo** se puede hacer
   en el VPS (las credenciales no estan en local).
4. Mas promos: un formato por curso, empezando por los mas visuales (caos,
   algebra lineal, protocolos).
5. Cuando el formato este validado, mergear a `main` y añadir la seccion de
   promos a la skill `curso-de-video`.
