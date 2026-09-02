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
| L0 | `lienzo.py` + `esp32.py` + sonda | pendiente |
| L1 | intro + clips 01-04 (molde: el 01) | pendiente |
| L2 | clips 05-08 | pendiente |
| L3 | clips 09-11 | pendiente |
| L4 | clips 12-14 + cierre | pendiente |
| L5 | qh local, narracion en el VPS, mux y entrega | pendiente |

## 5. Cosecha de trampas

(se llena durante la produccion)
