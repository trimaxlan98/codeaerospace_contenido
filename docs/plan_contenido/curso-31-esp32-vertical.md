# Curso 31 — ESP32: el chip por dentro (VERTICAL 9:16)

**Encargo (2026-09-01)**: *"un nuevo curso, del microcontrolador ESP32, en
formato vertical, pero con un estilo distinto: pantalla lisa con fondo azul
marino perfectamente coloreada, la informacion encima de forma estilizada,
nada encimado, filosofia menos es mas, limpio y bello, la maxima resolucion
para subir ya a Instagram, sin ruido visual, que cada clip pueda ser un reel
por si solo. Solo una marca de agua de Co.De Academy y la numeracion de
modulo tipo 01, 03, que no invada ni arruine el estilo. Total libertad para
hacer librerias nuevas."*

Decisiones cerradas con el dueño antes de escribir una linea:

| Pregunta | Respuesta |
|---|---|
| Angulo | **El chip por dentro + lo que hace** (mixto silicio/perifericos) |
| Extension | **16 piezas**: intro + 14 clips + cierre |
| Resolucion | **1080x1920 @60 nativo** (el techo real de Instagram Reels) |
| Composicion | **"Un objeto, un dato"**: el dibujo manda, la cifra abajo, nada mas |

- Rama **`curso/esp32-vertical`** sobre `main` (`15ba708`). No hace falta
  worktree: el checkout principal esta limpio y las tres ramas verticales
  anteriores ya estan en `main`.
- Curso en `studio/content/verticales/esp32/`.
- **Cuarto curso vertical** (tras 26 Fractales, 28 Satelites, 29 Emergencia)
  y **el primero con el estilo LIENZO**: es un lenguaje visual nuevo, no una
  variante del HUD de consola de los tres anteriores.

---

## 1. El estilo LIENZO (lo que hace distinto a este curso)

Los tres verticales anteriores usan la estetica de consola de vuelo de la
marca: fondo casi negro `#05070a`, escuadras HUD en las esquinas, telemetria
en Space Mono por todos lados, cifra + pie de tres renglones. Es densa a
proposito. **Este curso va al reves**: el fotograma es una superficie lisa y
casi vacia, y en el vive UNA cosa y UN dato.

Vive en `studio/content/manim_extensions/lienzo.py` — modulo nuevo, no toca
`promo.py` ni `code_brand.py` (los tres cursos anteriores siguen igual).

### Reglas del lienzo (las cumple el codigo, no la disciplina)

1. **Fondo liso azul marino.** `AZUL = "#0B1B33"`, plano, sin degradado, sin
   viñeta, sin textura. Es el 100 % del fotograma cuando no hay nada.
2. **Cuatro carriles y ni uno mas.** `numero` (arriba izq), `escena`
   (centro-alto), `dato` (cifra + unidad, abajo), `marca` (pie). Cada carril
   admite **un solo ocupante**: meter algo en un carril ocupado apaga primero
   lo que habia. Nada se encima porque no hay donde encimarlo.
3. **Paleta de cuatro colores.** Fondo, tinta (`#EAF1F8`), apagado
   (`#7C8FA6`) y **un** acento ambar (`#F5A31B`). Un quinto tono (cian
   `#5AC8D8`) solo cuando hay que distinguir DOS señales a la vez, y nunca
   los dos acentos en el mismo objeto.
4. **Provenencia por el color de la ETIQUETA, no del numero.** La cifra
   siempre es tinta (es la heroina). La etiqueta de debajo es **ambar** si el
   numero sale de medir o calcular EN ESTE RENDER, y **apagada** si esta
   DADO: hoja de datos, literatura o un parametro elegido de la simulacion
   (el periodo de un bucle, la constante dielectrica del FR4). Un parametro
   elegido no es una medida por mucho que este escrito en el codigo. Asi el
   cian no tiene que significar "medido" y el fotograma se queda con menos
   colores.
5. **Escala tipografica cerrada**: 128 / 46 / 30 / 22 / 18. No hay tamaños
   intermedios; si algo no cabe se acorta el texto, no se baja el cuerpo.
6. **Aire.** Margen lateral de 0.9 unidades, y la escena nunca pasa de 6.2
   de ancho ni de 7.0 de alto. El guardian `cabe()` **aborta el render** si
   una pieza se sale de la zona que la app no tapa.
7. **Un movimiento a la vez.** Nada de dos `play` simultaneos en carriles
   distintos: entra el dibujo, luego el dato. El ritmo lo pone el silencio.
8. **La marca no invade**: wordmark `co.de academy` en minusculas, cuerpo 18,
   opacidad 0.30, centrado en el pie sobre el suelo util. Y el numero de
   modulo `01` a la izquierda arriba, apagado, cuerpo 30. Nada mas de marca:
   sin escuadras, sin logotipo, sin barra de progreso.

### Zona segura

La hereda de `promo.SEGURA["vertical"]` (arriba 10 %, abajo 20 %, izq 5 %,
der 14 %): la columna de botones de Instagram y la franja de texto de abajo.
El ancho seguro de una pieza centrada son **5.76 unidades**.

---

## 2. Contrato de la libreria `esp32.py`

`studio/content/manim_extensions/esp32.py`. Dos mitades, como en toda la
casa: **piezas de dibujo** (devuelven mobjects, no animan) y **funciones
numericas** (numpy puro, `default_rng(semilla)`, sin manim). Toda cifra en
pantalla sale de la segunda mitad **durante el render**.

Lo que viene de la hoja de datos de Espressif (240 MHz, 520 KB, 34 GPIO,
corrientes de consumo) se declara con etiqueta APAGADA; lo que calcula la
libreria, con etiqueta AMBAR.

Sonda: `studio/tools/sonda_esp32.py` — invariantes de cada funcion numerica,
corre en el contenedor. **Correrla antes de tocar la libreria.**

---

## 3. Mapa de las 14 lecciones

| # | Modulo | Titulo | La cosa | El dato (y de donde sale) |
|---|---|---|---|---|
| 01 | 01 El silicio | Siete mil millones de ciclos | el encapsulado se abre en bloques | ciclos de reloj transcurridos durante el propio clip — **calculado** |
| 02 | 01 | Dos nucleos | dos columnas de tareas repartiendose | speedup del reparto greedy 1 vs 2 nucleos — **calculado** |
| 03 | 01 | Lo que cabe en 520 KB | el mapa de memoria llenandose | cuantos fotogramas 240x240 RGB565 caben — **calculado** |
| 04 | 01 | Un ciclo son 1.25 metros | el cristal de 40 MHz y el PLL x6 | distancia que recorre la luz en 4.17 ns — **calculado** |
| 05 | 02 Tocar el mundo | Un pin es un bit | el registro de 32 bits y los pines | tiempo de subida sobre una carga capacitiva — **calculado** |
| 06 | 02 | Voltajes que no existen | PWM y el filtro RC | media y rizado medidos sobre la ventana dibujada — **calculado** |
| 07 | 02 | El mundo entra en escalones | la rampa que se vuelve escalera | error de cuantizacion RMS y SNR de 12 bits — **calculado** |
| 08 | 02 | Dos cables o cuatro | trama I2C contra trama SPI | tiempo de mover 1 KB por cada bus — **calculado** |
| 09 | 03 La radio | Doce centimetros y medio | la onda de 2.4 GHz sobre la placa | longitud de onda y el cuarto de onda de la antena — **calculado** |
| 10 | 03 | Lo que de verdad viaja | anatomia de una trama Wi-Fi | eficiencia util del aire con cabeceras y ACK — **calculado** |
| 11 | 03 | Hablar poco para durar mucho | los anuncios BLE cada 100 ms | ciclo de trabajo y corriente media — **calculado** |
| 12 | 04 Tiempo y energia | La linea que se interrumpe | sondeo contra interrupcion | latencia del peor caso en las dos — **calculado** |
| 13 | 04 | El planificador | tareas con prioridad sobre dos nucleos | jitter de la tarea periodica con y sin acaparador — **calculado** |
| 14 | 04 | La vida de una pila | los cuatro estados de consumo | autonomia de 2000 mAh segun el ciclo de trabajo — **calculado** |

Intro (`00-intro`) y cierre (`15-cierre`) son piezas de marca, fuera del
rango de 30-45 s.

**Lo que este curso NO re-explica**: modulacion y espectro (cursos 8, 22 y
24), presupuesto de enlace (13), muestreo y cuantizacion en profundidad
(27). Aqui se tocan a la altura del aparato: cuanto cuesta, cuanto tarda y
cuanto gasta.

---

## 4. Lotes y tablero

| Lote | Piezas | Estado |
|---|---|---|
| L0 | `lienzo.py` + `esp32.py` + sonda | **hecho** (sonda 59 ok / 0 fallos) |
| L1 | intro, molde (clip 01) y cierre | **hecho** |
| L2 | clips 02-06 | **hecho** |
| L3 | clips 07-10 | **hecho** |
| L4 | clips 11-14 | **hecho** |
| L5 | qh local, mux y entrega | **hecho** |
| L6 | narracion | **BLOQUEADO** por facturacion de GCP (ver abajo) |

## Entrega (2026-09-02)

- `exports/verticales/esp32/esp32_vertical.mp4` — 1080x1920 @60,
  **507.44 s = 8 min 27 s**, 16 piezas, 18.2 MB, pico **-4.0 dB**.
- `exports/verticales/esp32/piezas/*.mp4` — **las 16 piezas sueltas
  sonorizadas**. ESAS son el producto para Instagram; el montaje es el extra.
- Costuras entre las quince uniones: **0.0000/255, exacto**. Es lo mejor de
  la coleccion (el 26 dio 0.003 y el 28 0.0048) y es consecuencia directa
  de que toda pieza empiece y termine en azul limpio con la capa fija
  apagada tambien.
- Picos por pieza: -4.0 dB los clips, -4.5 dB intro y cierre. Suelo de
  seguridad -0.5 dB.

### LO QUE FALTA: la voz

**La narracion esta bloqueada por algo ajeno al curso.** Vertex responde a
TODO con `403 PERMISSION_DENIED: Lightning dunning decision is deny for
project: projects/34992542254`. "Dunning" es cobro de morosidad: el proyecto
de GCP tiene la facturacion en mora y la API deniega cualquier peticion, TTS
incluido. No es cuota (eso seria 429) ni credenciales (la clave se lee bien).
Comprobado dos veces, la segunda con una sola frase directa contra el TTS.

Las 14 piezas con voz llevan su guion escrito y alineado en `clip.json`
(`voz.secciones` con `t_inicio`), y el verificador confirma que ninguna
frase pisa a la siguiente y que todas dejan cola. **En cuanto se arregle la
facturacion, solo faltan dos comandos** (no hay que re-renderizar nada):

```bash
bash studio/tools/narrar_esp32.sh    # serial, con sleep 45 entre piezas; se salta las ya bajadas
studio/backend/venv/bin/python studio/tools/unir_vertical.py     studio/content/verticales/esp32          # sin --sin-voz esta vez
```

El montaje entregado hoy lleva solo la cama de SFX. Es publicable tal cual
(el curso es mudo por diseño: la pantalla enseña y la voz solo remataria),
pero la version con voz es la buena.

### Estado pieza a pieza

| Pieza | Duracion qh | Frases de voz | SFX | Estado |
|---|---|---|---|---|
| Intro | 10.70 s | — | 8 | entregada |
| 01 · El reloj que no para | 30.30 s | 5 | 7 | entregada |
| 02 · Dos nucleos | 31.25 s | 5 | 6 | entregada |
| 03 · Lo que cabe en 520 KB | 30.95 s | 4 | 6 | entregada |
| 04 · Un ciclo son metro y cuarto | 34.27 s | 4 | 7 | entregada |
| 05 · Un pin es un bit | 36.15 s | 4 | 7 | entregada |
| 06 · Voltajes que no existen | 37.75 s | 5 | 7 | entregada |
| 07 · El mundo entra en escalones | 36.50 s | 5 | 7 | entregada |
| 08 · Dos cables o cuatro | 31.00 s | 4 | 7 | entregada |
| 09 · Doce centimetros y medio | 32.28 s | 4 | 6 | entregada |
| 10 · Lo que de verdad viaja | 36.50 s | 5 | 8 | entregada |
| 11 · Hablar poco para durar mucho | 35.15 s | 5 | 8 | entregada |
| 12 · La linea que se interrumpe | 38.30 s | 5 | 6 | entregada |
| 13 · El planificador | 35.55 s | 5 | 7 | entregada |
| 14 · La vida de una pila | 40.95 s | 5 | 10 | entregada |
| Cierre | 9.80 s | — | 6 | entregada |

## 5. Cosecha de trampas

Las de la casa siguen valiendo todas (`references/trampas.md`). Estas son las
de ESTE estilo y esta libreria, medidas, no supuestas:

- **El carril es la garantia, no la disciplina.** En los cursos anteriores
  "que nada se encime" era una regla que el autor tenia que recordar en cada
  `play`. Aqui hay CUATRO sitios y cada uno admite un ocupante: meter algo en
  un carril ocupado apaga primero lo que habia. Un subagente no puede
  encimar dos dibujos aunque quiera.
- **La cifra grande no cabe.** Medido en el contenedor a 1080x1920 con Space
  Mono BOLD: a cuerpo 128 cada caracter gasta **1.061 unidades** y la zona
  segura son 5.76 -> **5 caracteres**. "7 200 000 000" mide 14.10 y el
  guardian aborto el render. Por eso `cifra()` baja por una escala cerrada
  (128/112/96/80/72/64/56 = 5/6/7/8/9/10/12 caracteres) en vez de escalar el
  mobject: escalar rompe el paso monoespaciado entre estados de un contador.
  Editorialmente la leccion es otra: **el numero de un reel se escribe corto**
  (7 200 y la etiqueta "millones", no 7 200 000 000).
- **El espacio de una monoespaciada es un abismo**: "7 200" se leia como dos
  numeros distintos. Los grupos de miles van en Text sueltos separados a
  mano (`HUECO_MILES = 0.34` anchos de caracter).
- **La 'y' de "academy" descolgaba el wordmark entero.** Alinear los dos
  tokens por el borde INFERIOR sube la palabra con descendente media equis.
  Se alinean por el SUPERIOR, que es donde las dos tienen la 'd' ascendente.
- **Las unidades no sobreviven a las versalitas.** La etiqueta va en
  mayusculas, y "MHz" sale "MHZ", "ms" sale "MS" y "mV" sale "MV" (que es
  otra unidad). Se escriben con todas sus letras: "megahercios",
  "milisegundos", "milivoltios". Ademas queda mejor debajo de un numero
  grande.
- **Medir el transitorio no es medir.** La primera version del PWM daba
  0.74 V de media en vez de 1.65 y 372 mV de rizado en vez de 16.5: con
  tau = 10 ms y una ventana de 8 ms, el condensador todavia se estaba
  cargando. `pwm_filtrado` simula 8 constantes de tiempo que NO se dibujan y
  devuelve el indice donde empieza la ventana visible; se dibuja y se mide de
  ahi en adelante.
- **La SNR de un cuantizador sale 2 dB de mas con un numero entero de
  periodos**: las muestras caen siempre en los mismos puntos de la onda y el
  error de cuantizacion queda correlacionado. `snr_medido` usa 101.0
  periodos a proposito.
- **Un dibujo que no llena su franja se ve como un error**, no como
  minimalismo: la cifra queda lejisimos y la composicion se parte en dos.
  Regla para los clips: el dibujo ocupa al menos el 60 % del alto de la
  banda (`lz.alto_banda()`, 5.59 unidades).
- **`barra_apilada` aborta si dos rotulos se encimarian.** En el primer
  render "DIFS" y "BACKOFF" salieron pegados leyendose "DIFBACKOFF", y en el
  frame de revision parecia una palabra rara, no un fallo. En este estilo se
  rotula uno o dos tramos, no todos.
- **Centrar el dibujo en su franja era lo natural y estaba mal.** Un dibujo
  mas bajo que la franja (una rejilla de bits, un tren de pulsos, dos filas
  de un gantt) se queda a dos unidades de su cifra: la composicion se parte
  en dos mitades sin relacion y el hueco se lee como un error de
  maquetacion, no como aire. El anclaje por defecto de `L.escena()` es
  **abajo**: dibujo y dato bajan juntos y el vacio se acumula arriba, que es
  donde vive el numero de pieza y donde el vacio SI es aire.
- **El ambar traslucido sobre el azul marino no existe.** Medido sobre
  #0B1B33: #F5A31B al 26-45 % da (72,62,45) o (116,88,40) — verde oliva
  sucio, que no es ninguno de los dos colores; al 14 % da (44,46,48), un
  gris que ya no es ambar. No hay ventana buena. Las piezas de area van con
  TRAZO y el fondo del lienzo dentro, opaco.
- **Doce barras que se tocan son una losa.** El primer gantt salio como un
  bloque macizo en el que era imposible contar las tareas. `gantt` separa
  ahora las barras un hueco que le quita al ANCHO, no al sitio: los centros
  y el total siguen en su instante exacto, asi que la escala de tiempo no
  miente.
- **`rstrip("0")` sobre un entero se come la cifra.** El formateador del
  bloque de estilo devolvia `"4"` para `medido(40.0, 0)`: sin punto decimal
  que detuviera el strip, el cero de las decenas desaparecia. Ningun render
  lo habria marcado como error — habria salido "4 MEGAHERCIOS DEL CRISTAL"
  en pantalla. Lo cazo el clip 04 formateando los 40 MHz. Ahora el strip
  solo se aplica si hay punto.
- **`Create` va con `rate_func=smooth` de fabrica y un contador va lineal.**
  Medido en el clip 04: la barra que representa la distancia iba por el 16 %
  del recorrido cuando la cifra ya decia el 33 %. La imagen y el numero son
  el MISMO dato y se contradecian medio segundo. Cuando una animacion y una
  cifra cuentan lo mismo, las dos van con el mismo ritmo (y aqui ademas el
  lineal es el fisico: la luz no acelera).
- **El guardian de legibilidad estuvo MUERTO medio curso.** Filtraba los
  rotulos con `Text.has_points()`, y un `Text` de manim no tiene puntos
  propios: los glifos son sus hijos. Medido sobre un rotulo del estilo: 14
  `Text` en la familia y **0** pasaban el filtro, asi que la lista salia
  vacia, `_minimo_legible` devolvia `None` y `ALTO_MINIMO` no se comprobaba
  nunca. Un `scale()` que dejara la letra a la mitad habria pasado sin
  avisar. Lo cazo el productor del clip 07 midiendo, no mirando. La leccion
  general: **un guardian que nunca ha abortado no esta demostrado que
  funcione** — hay que probarlo con un caso que TIENE que fallar.
- **El fundido final se lleva TAMBIEN la capa fija** (numero y marca). No es
  descuido: es lo que hace que toda pieza empiece y termine en el mismo azul
  exacto y la costura del montaje valga cero.
