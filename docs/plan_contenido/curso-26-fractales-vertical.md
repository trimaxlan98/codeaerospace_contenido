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
| `studio/tools/narrar_promo.py` | ya sirve: acepta `clip.json` ademas de `promo.json` |
| `studio/tools/unir_vertical.py` | mux por clip (video + voz + SFX) y `concat -c copy` de las 16 piezas |

## Tablero de estado

| Paso | Estado |
|---|---|
| Plan maestro | hecho |
| Libreria ampliada + sonda de validacion | pendiente |
| Herramientas (render/sfx/unir) | pendiente |
| Molde (clip 1) | pendiente |
| Esqueletos de los 16 | pendiente |
| Clips 1-3 (M1) | pendiente |
| Clips 4-6 (M2) | pendiente |
| Clips 7-11 (M3) | pendiente |
| Clips 12-14 (M4) | pendiente |
| Intro + cierre verticales | pendiente |
| `qh` de las 16 piezas | pendiente |
| Voz (VPS, serial) | pendiente |
| Mux + union + picos | pendiente |

## Cosecha de trampas

(se llena durante la produccion)
