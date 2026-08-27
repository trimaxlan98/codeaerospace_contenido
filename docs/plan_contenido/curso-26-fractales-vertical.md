# Curso 26 — Fractales: la forma del infinito (FORMATO VERTICAL)

Rama `curso/fractales-vertical` (worktree `~/Documentos/github/codeaerospace_contenido-fractales`),
basada sobre `exp/promos-redes` porque necesita `promo.py` (el lienzo 9:16 real).

Encargo (2026-08-27): *"tenemos otra forma de hacer videos ahora en vertical,
para instagram; se probo en promocionales, pero ahora lo probaremos en un
curso: hay que desarrollar un curso de fractales, mas extenso y mas
impactante que el original en horizontal. Debe ser muy visual; en estos
formatos no incluimos subtitulos, solo audio y efectos de sonido. Recuerda la
secuencia: Intro + clip 1 ... + clip n + Cierre, hechos por separado para
mejorar el procesamiento pero unidos al final."*

## Qué es este curso y en qué se diferencia

El curso 1 de la coleccion, **"Fractales: la belleza de los numeros
complejos"** (horizontal, 8 clips, solo en la DB de produccion), se queda
corto por dos lados: solo mira el plano complejo, y cuenta con pies de texto.
Este lo **releva**: 14 clips, cuatro modulos, y la mitad del curso ocurre
fuera de los complejos (la costa, Koch, el juego del caos, el helecho, la
dimension, Newton, las antenas).

| | Curso 1 (horizontal) | Curso 26 (vertical) |
|---|---|---|
| Formato | 16:9 | **9:16 real** (1080x1920 @60) |
| Piezas | 8 clips | **14 clips + intro + cierre** |
| Texto | pies de 5 s, rotulos | **ningun subtitulo**: solo la CIFRA y su etiqueta HUD |
| Audio | narracion TTS sobre el pie | **voz escrita a mano y alineada** al instante visual + cama de SFX |
| Alcance | Mandelbrot/Julia | medida, dimension, IFS, complejos, Newton, caos, aplicaciones |
| Entrega | `curso_narrado.mp4` | **un solo vertical** intro+14+cierre unidos |

Lo que NO cambia: tema `code_brand`, **toda cifra en pantalla la calcula la
libreria** con numpy y semilla fija, y la revision de frames uno a uno.

## Reglas del formato vertical (duras)

1. **Sin subtitulos.** Prohibido el pie de frase. Se permite: una **cifra**
   grande, su **etiqueta HUD** de 1-3 palabras en MAYUSCULAS, y el
   identificador de modulo. Si una idea necesita una frase para entenderse,
   el clip esta mal diseñado: se rehace la imagen.
2. **La voz no lleva la leccion sola.** Mucha gente mira en silencio: la
   imagen tiene que enseñar por si misma (leccion del promo 2). La voz
   remata, no explica.
3. **Zona segura.** `promo.SEGURA["vertical"]`: 10 % arriba, 20 % abajo,
   14 % a la derecha. El fondo puede llenar el lienzo entero; **lo que
   importa cabe dentro**. Se comprueba con `--guias`.
4. **1 unidad = 135 px** igual que en horizontal: los `font_size` de los
   cursos valen tal cual; solo hay que RECOLOCAR (columna, no fila).
5. **Duracion por clip: 30-45 s.** El clip es una pieza de curso, no un
   promo; no necesita bucle, pero **empieza y termina en fondo limpio** para
   que el `concat -c copy` no chasquee.
6. Sin acentos en texto renderizado (Rajdhani / Space Mono). Los acentos
   viven en los `.json`, que no se renderizan — **salvo el texto de la voz**,
   que si los lleva (lo lee el TTS, no manim).

## Paleta por ROL (heredada, un rol = un significado)

| Rol | Color | Uso |
|---|---|---|
| Cifra medida | `CODE_CONST` cian `#22d3ee` | TODO numero calculado por la libreria |
| Regla / instrumento | `CODE_ACCENT` ambar `#f59e0b` | la regla que mide, el generador, el HUD activo |
| Lo que escapa | `#ea580c` naranja | orbitas fugitivas, cuencas que divergen |
| Lo atrapado | `#7c3aed` violeta | el conjunto, los prisioneros |
| Lo vivo | `#34d399` verde | helecho, arbol, pulmon, costa |
| Mobiliario | `#31414f` | ejes, reticula, cajas del conteo |
| Dato externo | `CODE_MUTED` `#94a0b0` | lo que NO calcula la libreria (se declara) |

Regla de honestidad: **el cian solo aparece si la libreria calculo esa
cifra en este render**. Un dato de la literatura (Shishikura, Feigenbaum) va
en gris y se dice que es de la literatura.

## Mapa del curso

### M1 · La medida que se rompe

| # | Clip | La imagen | La cifra medida |
|---|---|---|---|
| 1 | `01-la-costa` | una costa se mide con reglas cada vez mas cortas; el compas camina y la longitud SUBE sin parar | longitud con regla 1.00 / 0.50 / 0.25 / 0.125 (unidades de costa) |
| 2 | `02-el-copo` | Koch: el generador se aplica 6 veces; el perimetro corre, el area se para | perimetro x(4/3)^n vs area -> 1.600 del triangulo |
| 3 | `03-la-dimension` | cajas de lado decreciente cubren la curva; el ajuste log-log da la pendiente | D de Koch (teorico 1.2619) y de la costa, MEDIDOS por conteo |

### M2 · Una instruccion repetida

| # | Clip | La imagen | La cifra medida |
|---|---|---|---|
| 4 | `04-el-juego-del-caos` | un dado de tres caras, un punto que salta a la mitad: del ruido sale Sierpinski | D = log3/log2 = 1.5850, medida por conteo sobre la nube |
| 5 | `05-el-helecho` | 4 marcos afines, 24 numeros; cada marco contiene un helecho entero | probabilidades y % de puntos por mapa (contados) |
| 6 | `06-la-vida-copia` | arbol, pulmon, rio, rayo: la misma regla; superficie que cabe en un volumen | area del arbol de bronquios por generacion (modelo de Weibel, declarado) |

### M3 · El pais de los numeros complejos

| # | Clip | La imagen | La cifra medida |
|---|---|---|---|
| 7 | `07-girar-y-estirar` | z -> z^2 duplica el angulo y eleva el radio al cuadrado; tres semillas: una cae, una gira, una se dispara | |z| tras 8 pasos para r=0.9 / 1.0 / 1.1 |
| 8 | `08-julia` | z -> z^2+c: prisioneros y fugitivos; el Julia se rompe en polvo al salir c del conjunto | fraccion de la malla atrapada, medida |
| 9 | `09-mandelbrot` | el mapa de TODOS los Julia: cada pixel es un c, y su Julia asoma al tocarlo | numero de c del mosaico y su veredicto |
| 10 | `10-el-zoom` | zoom continuo x10^6 hacia un mini-Mandelbrot; el original reaparece dentro | factor acumulado en pantalla, y el ancho en unidades del plano |
| 11 | `11-la-frontera` | el conteo de cajas sobre la FRONTERA sube hacia 2 conforme se afina | D de la frontera medida por conteo (Shishikura = 2, declarado como literatura) |

### M4 · Fractales que trabajan

| # | Clip | La imagen | La cifra medida |
|---|---|---|---|
| 12 | `12-newton` | z^3=1 por Newton: tres cuencas; en CADA punto de frontera se tocan las tres | % de la malla por cuenca; iteraciones medias |
| 13 | `13-el-caos-tiene-forma` | el diagrama de bifurcacion (un Cantor por columna) y el atractor de Lorenz | Feigenbaum medido de los cocientes; D de Lorenz (literatura 2.06) |
| 14 | `14-la-regla-corta` | una antena de Koch dobla el mismo hilo en un tercio del ancho; un terreno nace de un desplazamiento aleatorio | longitud de hilo vs ancho ocupado (medido); rugosidad H del terreno |

Intro (`00-intro`) y cierre (`99-cierre`): la identidad CO.DE Academy
recompuesta para 9:16, con su propia cama sonora.

## Contrato de la libreria (`studio/content/manim_extensions/fractales.py`)

`fractales.py` ya existe (escape-time: `campo_escape`, `colorear`,
`imagen_mandelbrot`, `imagen_julia`, `zoom_fractal`, `morph_julia`,
`orbita`, `camino_cardioide`, `miniatura_julia`, `PALETAS`). Se AMPLIA sin
tocar lo existente (los clips del curso 1 en la DB siguen valiendo) con:

```
# --- medida y dimension ---
costa(nivel, semilla, aspereza)      -> (n,2) puntos del desplazamiento del punto medio
medir_con_regla(pts, paso)           -> dict(longitud, vertices, pasos) del compas
richardson(pts, pasos)               -> dict(pasos, longitudes, pendiente, D)
conteo_cajas(pts, lados)             -> dict(lados, conteos, D, ajuste)
curva_koch(nivel, largo)             -> (n,2) puntos de la curva
copo_koch(nivel, radio)              -> (n,2) puntos cerrados del copo
koch_perimetro(nivel), koch_area(nivel)  -> cifras exactas y medidas

# --- IFS / juego del caos ---
MAPAS = {"sierpinski", "helecho", "dragon", "arbol"}
ifs_puntos(mapas, n, semilla)        -> (n,2) con prefijo estable
ifs_reparto(mapas, n, semilla)       -> cuentas por mapa (para el % honesto)
imagen_ifs(mapas, puntos, res, ...)  -> ImageMobject por densidad
marcos_ifs(mapas, ...)               -> los cuadros donde cada mapa mete una copia
sierpinski_exacto(nivel)             -> VGroup de triangulos (version geometrica)

# --- complejos ---
traza_orbita(c, z0, n)               -> (n,2) para dibujar sobre un plano
prisioneros(c, res, ...)             -> fraccion atrapada de la malla
frontera_mandelbrot(res, ...)        -> (n,2) puntos de la frontera (borde del set)
imagen_newton(raices, res, ...)      -> ImageMobject de las cuencas
newton_reparto(raices, res)          -> % por cuenca + iteraciones medias
newton_orbita(z0, raices, n)         -> (n,2) del camino de Newton

# --- aplicaciones ---
antena_koch(nivel, ancho)            -> dict(puntos, longitud_hilo, ancho_ocupado)
terreno(n, H, semilla)               -> (n,) alturas del desplazamiento del punto medio
```

Todo determinista (`default_rng(semilla)`), topes duros de resolucion e
iteraciones (el VPS no renderiza esto, pero el contenedor local si), y
**cero cifras inventadas**.

## Herramientas nuevas

| Pieza | Qué hace |
|---|---|
| `studio/content/verticales/<slug>/` | curso vertical: `curso.json` + `style_block.py` + `clips/NN-<tema>/{clip.json,escena.py}` |
| `studio/tools/render_vertical.py` | renderiza un clip (o todos) en 9:16, mide duracion, saca frames y avisa fuera de 30-45 s |
| `studio/tools/sfx.py` (`vertical`) | cama sonora por clip desde `clip.json` (reusa `mezclar`) |
| `studio/tools/narrar_promo.py` | acepta `clip.json` ademas de `promo.json` (se usa para promos) |
| `studio/tools/alinear_voz.py` | narra frase a frase y las coloca en su `t_inicio` EXACTO, sin el tope de 2.5 s del ensamblador del backend |
| `studio/tools/unir_vertical.py` | mux por clip (video + voz + SFX) y `concat -c copy` de las 16 piezas |

## Tablero de estado

| Paso | Estado |
|---|---|
| Plan maestro | hecho |
| Libreria ampliada + sonda de validacion | hecho (0 fallos, 17 s) |
| Herramientas (render_vertical / sfx vertical / unir_vertical) | hecho |
| Molde (clip 01) | hecho |
| Esqueletos de los 16 | hecho |
| Clips 1-3 (M1) | escritos y validados en `ql` |
| Clips 4-6 (M2) | escritos y validados en `ql` |
| Clips 7-11 (M3) | escritos y validados en `ql` |
| Clips 12-14 (M4) | escritos y validados en `ql` |
| Intro + cierre verticales | escritos y validados en `ql` |
| `qh` de las 16 piezas | en curso |
| Voz (VPS, serial) | manifiestos subidos a `/tmp/narrar-fractales` |
| Mux + union + picos | pendiente |

Duraciones medidas (`ql`, identicas en `qh`): intro 12.43 · 01 36.83 ·
02 33.36 · 03 34.06 · 04 31.93 · 05 30.60 · 06 31.26 · 07 30.26 · 08 30.13 ·
09 30.43 · 10 32.37 · 11 30.23 · 12 31.03 · 13 35.03 · 14 30.83 · cierre 8.90.
**Total 8 min 30 s.**

## Cosecha de trampas

Las del formato vertical y las de manim que costaron una iteracion cada una.

**Composicion y texto**

- **La zona segura se mide, no se mira.** `hud()` y `cifra()` llaman a
  `cabe()`, que ABORTA el render si el rotulo pasa de 5.76 unidades (el
  doble del margen derecho, que es el mas ancho). Cazo nueve rotulos
  largos antes de renderizarlos. La alternativa —revisar frames— no sirve:
  un texto que se mete 0.2 unidades bajo la columna de botones de
  Instagram no se nota en el frame de validacion.
- **El ancho de `Text` NO escala de forma continua con `font_size`.** A
  font 11 y 13 el mismo texto mide 5.87 y 5.89; a 15 y 17, 8.80 y 8.82.
  Bajar un punto no reduce NADA: hay que acortar la cadena. (Se descubrio
  intentando meter "ciencia / ingenieria / espacio" en la intro.)
- **Un fundido cruzado en el mismo renglon deja dos rotulos encimados.**
  Con pies de texto se perdona; en un curso SIN subtitulos ese medio
  segundo es justo el que el espectador usa para leer la cifra. Se cambio
  todo por `cambiar()`: lo viejo se apaga ANTES de que entre lo nuevo. Se
  vio en el clip 05, con "24" y "200000" superpuestos.
- **El pie de cifra vive en tres renglones fijos** (`Y_ETIQUETA`,
  `Y_NUMERO`, `Y_SUB`). En vertical el ojo vuelve siempre al mismo punto:
  una cifra que se mueve entre clips se lee como otra cifra.

**Manim**

- **`FadeOut` de un VGroup no quita los submobjects que entraron a escena
  por su cuenta.** En el clip 04 cada marca del juego del caos entra con
  su propio `FadeIn` dentro de un `play`: ademas de estar en el grupo es
  un mobject suelto. `FadeOut(grupo)` lo saca del grupo y **lo deja
  dibujado encima de la nube**. Hay que apagarlos uno a uno.
- **z_index: lo que tapa el desbordamiento tambien tapa el texto.** Las
  cortinas del clip 10 (z=50) escondian el pie de cifra, que nace en z=0.
  `medida()` pone 800; los textos construidos a mano, no.
- **Un contador que sube 20 veces no se hace con `always_redraw`** (un
  render de pango por frame). Se pre-renderizan los 20 valores y se
  intercambian con `become` dentro de un `UpdateFromAlphaFunc`, que ademas
  garantiza que el mobject participe del `play` (la trampa del promo 2).
- **`Transform` entre curvas de distinto numero de puntos no vale.** Para
  hacer crecer los picos de Koch se reconstruye la MISMA curva con
  `altura` de 0 a 1: el numero de puntos no cambia durante el barrido.

**Honestidad de las cifras**

- **c = -0.4+0.6i y c = 0.285+0.01i estan FUERA del conjunto** (la orbita
  de 0 escapa en 25 y 18 pasos) aunque salgan en todos los libros como
  ejemplos de Julia: por eso son polvo. Y los que estan al filo
  (-0.8+0.156i) cambian de veredicto con `max_iter`: no se usan.
- **El conteo de cajas sobre una CURVA converge despacio y por arriba**:
  Koch mide 1.29 frente a 1.2619. Sobre una NUBE es fino (Sierpinski
  1.592 frente a 1.5850). Por eso el clip 03 saca la D de Koch de la
  autosemejanza —exacta— y deja la verificacion del metodo para
  Sierpinski, donde medido y exacto coinciden al 0.5 %.
- **Medir la frontera del Mandelbrot contando el borde de la mascara da
  1.03**, porque mide el contorno de la cardioide: los filamentos son mas
  finos que un pixel y no entran en la mascara. Hay que ir por el
  estimador de distancia y el AREA DE LA ORLA. Y el resultado sube al
  afinar la malla (1.593 a 900, 1.617 a 1400, 1.639 a 2200), que es
  justamente lo que hay que enseñar.
- **Los picos de Koch salen hacia dentro** si el poligono se recorre en
  sentido antihorario (el generador gira +60 grados, o sea hacia la
  izquierda de la marcha). El area BAJA en vez de subir. Lo caza
  `area_poligono` contra `koch_area`, no el ojo.
- **256 circulos en rejilla ocupan mas envoltorio que el circulo del que
  salen** (el empaquetado deja un 22 % de aire), asi que "la seccion se
  conserva" se dibuja con baldosas que teselan, partiendo alternando lado.
  Con circulos, la imagen diria lo contrario que la cifra.
- **Una orbita que se fuga hay que RECORTARLA al encuadre.** Sin recorte
  cruza la pantalla entera y se lee como ruido; y en el clip 07 se metia
  por encima del pie de cifra. Se conserva el ultimo punto de dentro y se
  añade uno fuera del borde, en la misma direccion.
- Los puntos de partida del clip 12 se eligieron **midiendo**: el par mas
  manso (radio maximo 1.24) entre los que, separados 0.02, caen en raices
  distintas. Con otros pares, Newton pega un salto enorme.

**Voz**

- **El ensamblador del backend acota el silencio entre frases a
  `MAX_HUECO_S = 2.5 s`** (`app.narracion._ensamblar`). Para un guion de
  curso horizontal, que habla casi todo el rato, esta bien; en un curso
  vertical la voz es rala **a proposito** —la imagen enseña y la voz
  remata— y hay huecos de 4 a 7 s. Con el tope, cada frase se ADELANTA
  hasta 2.8 s y acaba comentando el plano equivocado. Medido sobre el
  envelope RMS de los wavs: 2.8 s en el clip 01, 2.7 en el 02, 1.5 en el
  10. Se resolvio con `studio/tools/alinear_voz.py`, que sintetiza frase a
  frase y las coloca en su instante SIN tope. Tras el cambio, la voz cae
  donde dice el manifiesto.
- **La alineacion se verifica midiendo, no escuchando**: envelope RMS en
  ventanas de 100 ms, arranques de habla y comparacion con los `t_inicio`.
  Ocho minutos de audio no se auditan de oido frase por frase.
- Si una frase se pasa de larga empuja a la siguiente: `alinear_voz.py` lo
  AVISA con cuanto, y se arregla acortando el texto, no moviendo el audio.
- La `duracion_objetivo` tiene que ser la del render **qh**, que no es la de
  `ql`: en clips con muchos `play` cortos la diferencia llega a 0.3 s (el
  redondeo a frame es distinto a 30 y a 60 fps).

**Herramienta**

- El worktree usa el **venv del checkout principal** (`~/…contenido/studio/
  backend/venv/bin/python`): el worktree no tiene venv propio.
- Lanzar tres renders en paralelo desde una sola linea de bash con
  `nohup … &` **se enreda con las comillas**: uno de los tres arranco con
  la linea de comandos mezclada. Va en un `.sh` del scratchpad.
- Los renders largos pasan del timeout por defecto de la herramienta bash
  (2 min): hay que subirlo o lanzarlos en background.
