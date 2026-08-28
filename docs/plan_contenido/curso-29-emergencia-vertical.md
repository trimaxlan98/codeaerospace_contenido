# Curso 29 — Emergencia: reglas simples, mundos enteros (FORMATO VERTICAL, EXPERIMENTAL)

Rama `curso/emergencia-vertical` (worktree
`~/Documentos/github/codeaerospace_contenido-emergencia`), basada en la rama
local `chore/consolidar-todo` (la unica que junta los dos cursos verticales
26 y 28 con sus herramientas ya arregladas; `origin/main` aun no la tiene).

Encargo (2026-08-28): *"un curso en vertical completamente experimental, que
lleve a otro nivel las animaciones que hemos hecho hasta ahora; es un
experimento del uso de Fable: total libertad creativa. Debe ser relevante
para subir a Instagram y que la gente lo disfrute: aunque sea un curso
completo, cada clip tiene que poder subirse por separado y mostrar el poder
y el avance tecnologico que tenemos para animar con Python. Si hace falta
crear librerias nuevas, hazlas."*

## Que es este curso y en que se diferencia

Tercer curso del formato 9:16 (tras Fractales 26 y Satelites 28). Idea
rectora: cada clip parte de dos o tres reglas que caben en una etiqueta HUD
y, delante del espectador, esas reglas producen un mundo entero — una
bandada, una galaxia, un rio, un cristal. Se enseña la EMERGENCIA; se
exhibe que **todo el fotograma sale de una simulacion numpy calculada en el
render**.

Lo que "otro nivel" significa aqui (y se mide al final):

| Medida | Hasta ahora | Aqui |
|---|---|---|
| Fotograma | objetos vectoriales sobre fondo | **el fondo ES el sistema**: campos, densidades, miles de agentes; los vectores quedan para cifra, HUD y enfasis |
| Escala | decenas de mobjects | 2000-4000 agentes o mallas de 130k celdas por frame, a 60 fps |
| Camara/tiempo | plano fijo | zoom, seguimiento de un agente, camara lenta en el instante en que nace el patron |
| Pieza suelta | parte de un curso | **cada clip vive solo en Instagram**: gancho en los 2 primeros segundos, cifra medida, cierre limpio, audio propio |

Lo que NO cambia: tema `code_brand`, cifras calculadas en el render (cian) o
declaradas de literatura (gris), sin subtitulos, revision de frames uno a uno.

## Reglas del formato vertical (duras, heredadas del 26 y 28)

1. Sin subtitulos: solo CIFRA, etiqueta HUD (1-3 palabras) e identificador
   de pieza. HUD a fs 18-20: **19 caracteres** con espacios; cifra a fs 104:
   **6 caracteres**. El guardian `cabe()` aborta el render.
2. La voz remata, no explica (1-2 frases por pieza, alineadas a `t_inicio`).
3. Zona segura `promo.SEGURA["vertical"]`; el fondo-simulacion llena el
   lienzo entero, lo que importa cabe dentro.
4. Piezas de 30-45 s; empiezan y terminan en fondo limpio.
5. Sin acentos en texto renderizado. `cambiar()` para relevar rotulos.
6. Pie de cifra en los tres renglones fijos (`Y_ETIQUETA`, `Y_NUMERO`, `Y_SUB`).

## Paleta por ROL (un rol = un significado; las LUT de la libreria la respetan)

| Rol | Color | Uso |
|---|---|---|
| Cifra medida | cian `#22d3ee` | TODO numero calculado en este render; agentes "medidos" |
| Regla / instrumento | ambar `#f59e0b` | la regla en accion, el generador, el agente seguido por la camara |
| Lo ordenado / atrapado | violeta `#7c3aed` | el patron que emerge, el dominio, la cuenca |
| Energia / lo que escapa | naranja `#ea580c` | vorticidad, avalancha, temperatura, lo que se dispara |
| Lo vivo | verde `#34d399` | bandada, moho, celulas vivas |
| Mobiliario | `#31414f` | rejilla, cajas, ejes |
| Dato externo | gris `#94a0b0` | lo que NO calcula la libreria |

## Mapa del curso (14 clips + intro + cierre)

### M1 · Reglas que caminan

| # | Clip | La imagen | La cifra medida |
|---|---|---|---|
| 1 | `01-la-bandada` | 2500 agentes con tres reglas (separacion, alineacion, cohesion); del ruido nace una bandada; la camara sigue a un agente ambar | polarizacion del enjambre (0 → ~0.9) |
| 2 | `02-el-moho` | Physarum: agentes que depositan estela y la siguen; sobre puntos de comida nace una red | longitud de la red frente al arbol minimo (veces) |
| 3 | `03-la-pila-de-arena` | pila abeliana: un millon de granos cayendo en el centro; la mandala fractal y las avalanchas | granos y tamaño de la avalancha mayor |
| 4 | `04-el-canon` | Life: el cañon de Gosper dispara planeadores; camara lenta al nacer uno | planeadores por minuto (periodo 30) |

### M2 · Campos que se organizan

| # | Clip | La imagen | La cifra medida |
|---|---|---|---|
| 5 | `05-manchas-y-rayas` | Gray-Scott: de una mancha, manchas; cambian f,k y salen rayas | longitud de onda del patron (px y celdas) |
| 6 | `06-el-tanque-de-ondas` | FDTD 2D: una fuente, una pared con dos rendijas, franjas | separacion de franjas medida vs lambda·L/d |
| 7 | `07-la-placa-que-canta` | Chladni: arena sobre la placa vibrando; sube la frecuencia y cambia el modo | modo (m,n) y frecuencia relativa |
| 8 | `08-el-iman-que-decide` | Ising: enfriar desde T alta; en Tc dominios de todos los tamaños; abajo, uno gana | magnetizacion |M| y T/Tc |

### M3 · El caos con forma

| # | Clip | La imagen | La cifra medida |
|---|---|---|---|
| 9 | `09-doscientos-pendulos` | 200 pendulos dobles a 1e-6; primero uno, luego un abanico de colores | tiempo hasta separarse 1 rad |
| 10 | `10-las-cuencas` | pendulo magnetico sobre 3 imanes: cada pixel se colorea por donde acaba; zoom a la frontera | % por iman; dimension de la frontera |
| 11 | `11-los-epiciclos` | epiciclos de Fourier trazando la silueta CO.DE | circulos para 1 px de error |

### M4 · Mundos enteros

| # | Clip | La imagen | La cifra medida |
|---|---|---|---|
| 12 | `12-el-rio` | lattice-Boltzmann D2Q9: flujo tras un cilindro, la calle de vortices; vorticidad naranja/violeta | Reynolds y Strouhal medido |
| 13 | `13-dos-galaxias` | N cuerpos: dos discos que chocan, brazos de marea | energia conservada (%) |
| 14 | `14-el-mundo-en-una-regla` | mosaico vivo 3x4+1 de las simulaciones anteriores a la vez | reglas totales del curso |

Intro `00-intro`: la identidad CO.DE con el titulo naciendo de una bandada
que se posa en las letras. Cierre `15-cierre`: la marca del curso 28.

## Contrato de la libreria (`studio/content/manim_extensions/emergencia/`)

Paquete (un modulo por simulador para escribirlos en paralelo sin pisarse):

```
emergencia/__init__.py      nucleo: paletas/LUT, Pelicula, camara, ritmo, guard de memoria
emergencia/bandada.py       boids con rejilla espacial (O(n))
emergencia/moho.py          Physarum
emergencia/arena.py         pila abeliana
emergencia/vida.py          Life + cañon de Gosper
emergencia/turing.py        Gray-Scott (envuelve naturaleza.py si sirve)
emergencia/ondas.py         FDTD 2D doble rendija
emergencia/chladni.py       placa
emergencia/ising.py         Metropolis con tablero de ajedrez vectorizado
emergencia/pendulos.py      RK4 de N pendulos dobles
emergencia/cuencas.py       pendulo magnetico
emergencia/epiciclos.py     DFT de un contorno
emergencia/rio.py           LBM D2Q9
emergencia/galaxias.py      N cuerpos con softening
```

Interfaz comun de un simulador (obligatoria):

```
simular(..., semilla=1, pasos=P, res=(W, H)) -> dict(
    frames  = uint8 (T, H, W, 3)  |  campo float32 (T, H, W) + "rango"
    cifras  = {nombre: valor, ...}   # lo que el clip enseña; medido AQUI
    extra   = {...}                  # posiciones de agentes, etc. (opcional)
)
medir(**kw) -> dict                  # solo cifras, para la sonda
```

- Resolucion base **270x480** (relacion 9:16 exacta) para fotograma
  completo; 360x640 si el clip hace zoom. `Pelicula` reescala a 1080x1920.
- **Presupuesto**: simulacion ≤ 90 s en el contenedor; pila ≤ 1 GB uint8
  (900 frames x 480 x 270 x 3 = 350 MB); render qh ≤ 35 min.
- Determinista: `np.random.default_rng(semilla)`.
- Un simulador no importa manim: numpy puro (la sonda corre sin manim).

`Pelicula` (nucleo): recibe la pila de frames, crea un `ImageMobject` a
pantalla completa, y `reproducir(scene, run_time, desde, hasta, ritmo,
encuadre)` lo anima con `UpdateFromAlphaFunc` cambiando `pixel_array`
(RGBA: manim exige 4 canales). Medido en el contenedor: 0.10 s/frame en
ql y 0.29 s/frame en qh (35 s = ~2 min ql, ~10 min qh).

## Herramientas

Las cuatro del formato (`render_vertical.py`, `alinear_voz.py`,
`unir_vertical.py`, `sfx.py`) valen tal cual. Nueva:
`studio/tools/sonda_emergencia.py` (corre en el contenedor, 0 fallos antes
de escribir clips).

## Tablero de estado

| Paso | Estado |
|---|---|
| 1 · Plan maestro | **hecho** (2026-08-28 06:10) |
| 2 · Nucleo de la libreria (`Pelicula`) medido en contenedor | **hecho** (0.10 s/frame ql, 0.29 qh) |
| 3 · Simuladores (13 modulos) + sonda 0 fallos | **hecho**: 13 modulos, sonda **36 ok, 0 fallos** (08:05) |
| 4 · Molde: curso.json, style_block, intro, clip 01, cierre | **hecho**: clip 01 34.87 s (frames revisados); intro 17.03 s con el titulo naciendo de un enjambre (`em.converger`); cierre 8.90 s |
| 5 · Esqueletos de las 16 piezas | **hecho** |
| 6 · Produccion clips 02-14 (subagentes) | **hecho** (12:05): 13 clips entregados por 6 Sonnet + 7 Opus, todos entre 31.4 y 39.9 s en ql; 3 bugs de libreria cazados por agentes (tabla de Ising, franja del LBM, alfa de Pelicula tras zoom) y corregidos |
| 7 · Revision de frames + pytest | frames ql revisados; **190 tests en verde**; revision final sobre los frames qh |
| 8 · Commit, push, PR (sin merge) | commits 89516c2 + el de cierre de clips; PR pendiente |
| 9 · qh (3 frentes) + duraciones a los manifiestos | **hecho** (11:57): 16/16 en 1080x1920 @60, 0 fallos; duraciones medidas escritas en los manifiestos. **502.76 s = 8 min 23 s** de curso |
| 10 · Voz (VPS, serial, alinear_voz.py) | en curso (11:57): 14 piezas con voz, intro y cierre sin ella |
| 11 · unir_vertical: piezas sueltas + montaje + verificacion | pendiente |
| 12 · PLAN.md, catalogo, memoria | pendiente |

## Al retomar (10:31 del 28-08): que hacer, en orden

1. `ls render_jobs/verticales/emergencia/*/video.mp4` y leer cada
   `clips/*/clip.json`: una pieza esta terminada si su `description` ya no
   dice "(esqueleto)" y su `duracion_objetivo` coincide con el video.
2. Para las piezas sin terminar, relanzar UN agente por pieza con el
   `contrato-clip.md` del scratchpad (si el scratchpad se perdio, el
   contrato esta resumido en este plan: secciones de reglas, paleta y
   formato) — Sonnet: 06, 07, 09; Opus: 02, 03, 08, 10, 12, 13, 14.
   Los informes de los simuladores estan en las docstrings de cada modulo.
3. **Velo de contraste** (pendiente de aplicar): el HUD gris pierde
   contraste cuando un campo claro llena el fotograma (visto en el 05). La
   prueba de `set_fill(opacity=[0, 0.85])` con `sheen_direction` en Cairo
   esta hecha (scratchpad/velo): añadir al `Scene.setup` del style_block dos
   velos degradados (arriba, detras de HUD+reglas; abajo, detras del pie de
   cifra) a z=-450, y re-renderizar todo en qh con ellos.
4. Revision de frames de TODAS las piezas (paso 7), pytest, commit, PR sin
   merge, qh en 3 frentes, voz en el VPS (serial), unir_vertical,
   verificacion, PLAN.md/catalogo/memoria (pasos 8-12).

## Costuras del montaje (medidas sobre los qh, 2026-08-28)

Ultimo frame de cada pieza contra el primero de la siguiente, en 1080x1920:

| Union | Diferencia |
|---|---|
| 14 -> cierre | **0.000**/255 |
| 03->04, 02->03, 13->14 | 4.8-5.0 |
| intro->01, 10->11, 04->05, 11->12 | 5.2-5.7 |
| 08->09, 12->13, 05->06 | 6.5-7.8 |
| 06->07 | 30.6 |
| 07->08 | 46.3 |
| 01->02 | 56.8 |
| 09->10 | **66.4** (la peor) |

**Es una consecuencia buscada, no un defecto**: el encargo manda que cada
clip se pueda subir SOLO a Instagram, y para eso el contrato exige
movimiento en los dos primeros segundos. Una pieza que arranca con su
simulacion ya viva no arranca en negro, asi que la union con la anterior es
un **corte seco de montaje**, no el empalme invisible del curso 26 (que
media 0.003/255 porque todas sus piezas nacian y morian en fondo limpio).
Todas las piezas SI terminan en fondo limpio (`cerrar_pieza`), que es lo que
evita el chasquido dentro de cada pieza.

Si algun dia se quiere el montaje con empalmes invisibles, la via es un
fundido corto al unir (re-encodeando: `unir_vertical.py` concatena con
`-c copy`), no quitarle el gancho a las piezas.

## Cifras medidas (informes de los simuladores, contenedor, 2026-08-28)

| Modulo | Cifra | Valor |
|---|---|---|
| bandada | polarizacion inicial / final; cruza 0.8 | 0.032 / 0.931; frame 351 (11.7 s) |
| moho | red geodesica / arbol minimo | 950 px / 806 px = **1.178**; malla entera 5.9x |
| arena | granos; avalancha mayor; exponente | 50 000 (1M no cabe: coste ~granos^1.8); 21 533 celdas; tau 1.279 (r2 0.993) |
| vida | periodo del cañon; planeadores | 30 (21 intervalos, dispersion 0); 22 emitidos, 30/min |
| turing | lambda manchas / rayas; manchas | 15.32 px / 13.34 px; 186 |
| ondas | franjas medido / Fresnel / lambda L/d | 46.12 / 45.56 / 44.55 px (zona de Fresnel: la formula simple se queda corta) |
| chladni | arena a <3 px del nodo por modo | 86.1 / 83.2 / 82.4 / 81.3 % |
| ising | \|M\| en T=3 / Tc / final; cruce 0.5 | 0.048 / 0.172 / 0.973; T=2.168 (Onsager E: -1.944 vs -1.953) |
| pendulos | t hasta 1 rad; Lyapunov; deriva E | 8.975 s; 1.19 /s; 4.9e-6 % |
| cuencas | reparto; D frontera; sin converger | 34.2/32.9/32.9 %; **1.626**; 60 de 230 400 |
| epiciclos | circulos para 1 px (RMS) | **100** (N=50: 2.50 px; N=200: 0.325 px) |
| rio | Re; Strouhal; vortices | 180; **0.2053** (lit. 0.19 cilindro libre); 16 |
| galaxias | deriva E nucleos; capturadas | 2.85e-4 %; 8.3 % cada disco |

## Cosecha de trampas

- **`ImageMobject.pixel_array` exige RGBA**: asignar un (h,w,3) revienta con
  "buffer is not large enough" al primer frame. La pila se guarda en RGB
  (memoria) y se le pega el canal alfa al vuelo.
- **Boids O(n²) no sirve**: 2000 agentes x 300 pasos = 112 s. Rejilla
  espacial con `np.bincount` por celda.
- **`import emergencia` no trae los submodulos**: `em.bandada` era
  AttributeError en el primer render. `__getattr__` (PEP 562) los importa
  bajo demanda.
- **numpy 2 promociona a float64 sin avisar** (`np.int64 * float32`): el
  LBM iba 5x mas lento por una tabla de enteros. `float(EX[i])`.
- **Dos `simular()` vivos en el mismo proceso** matan el contenedor (exit
  137): la sonda suelta la pila entre modulos; el clip 14 (mosaico) hace
  `del` de cada pila al meterla.
- **`salpicar` es aditivo y de un solo color**: 200 llamadas por frame
  (una por pendulo) cuestan mas que la fisica; se pinta por bandas de color.
  Y sobre una linea nodal con 20 granos/px cada canal satura por su cuenta:
  el ambar se vuelve BLANCO. Se acumula densidad y se colorea por LUT.
- **El millon de granos del plan no cabe** (medido: N=249/100k granos no
  termino en 800 s). La cifra en pantalla es la real: 50 000.
- **El final del Ising es un sorteo** con campo nulo: con semilla 1 uno
  gana (|M| 0.97); con otras, 30-40 % de las veces quedan dos dominios.
  Semilla fija y declarado.
- **Fresnel, no Fraunhofer**: con L < d²/lambda la separacion de franjas
  medida (46.1 px) NO cuadra con lambda·L/d (44.6) y SI con r1-r2 = m·lambda
  (45.6). Se cuenta, no se esconde.
- **La fraccion nodal de Chladni daba 100.0 %** sin un piso de ruido: un
  numero que no existe en ninguna placa. Con temblor de plato, 81-86 %.
- **La tabla de Metropolis de 5 entradas con `>>1` es incorrecta en un
  borde abierto** (celdas con 3 y 2 vecinas: s*nb impar, redondeo hacia
  abajo, el perimetro acepta volteos que suben la energia con probabilidad
  1). Lo cazo el agente del clip 08 comparando contra un Metropolis
  secuencial (0.992 vs 0.86-0.94 con saltos). Los "saltos de |M|" y la
  "inversion a T~1.9" del primer informe eran ese bug. Tabla de 9 entradas
  indexada por s*nb+4; con ella el toro da 0.9973 vs 0.997026 (Onsager).
- **El HUD gris se pierde sobre un campo claro** (Gray-Scott, arena,
  Ising): lo resuelve `velos_de_contraste()` en el style_block (banda
  solida + degradado de 1.1 detras del texto, arriba y abajo, z=-450). Un
  solo degradado largo se quedaba en 0.4 de opacidad a la altura del HUD.
- **Orbita parabolica => E0 = 0**: la deriva relativa "62 %" era dividir por
  ruido. Se normaliza con G·mA·mB/pericentro y se declara la escala.
