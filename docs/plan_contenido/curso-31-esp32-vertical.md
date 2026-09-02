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
   numero lo calcula la libreria en el render y **apagada** si viene de la
   hoja de datos de Espressif. Asi el cian no tiene que significar "medido" y
   el fotograma se queda con menos colores.
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
| L1 | intro, molde (clip 01) y cierre | **hecho**, validados en `ql` |
| L2 | clips 02-06 (5 agentes) | en produccion |
| L3 | clips 07-10 | pendiente |
| L4 | clips 11-14 | pendiente |
| L5 | qh local, narracion en el VPS, mux y entrega | pendiente |

### Estado pieza a pieza

| Pieza | Duracion ql | Estado |
|---|---|---|
| 00 intro | 10.70 s | validada |
| 01 el reloj que no para | 30.33 s | validada (MOLDE) |
| 02 dos nucleos | — | en produccion |
| 03 lo que cabe en 520 KB | — | en produccion |
| 04 un ciclo son metro y cuarto | — | en produccion |
| 05 un pin es un bit | — | en produccion |
| 06 voltajes que no existen | — | en produccion |
| 07-14 | — | esqueleto |
| 15 cierre | 9.80 s | validada |

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
- **El fundido final se lleva TAMBIEN la capa fija** (numero y marca). No es
  descuido: es lo que hace que toda pieza empiece y termine en el mismo azul
  exacto y la costura del montaje valga cero.
