# Curso 31 · ESP32 — guion de voz

Generado el 2026-09-02 desde los `clip.json` del curso, o sea que **los tiempos son los del render que ya esta en el disco** (1080x1920 @60). 16 piezas, 8.48 min, **65 frases** y 423 palabras en total.

## Como se graba esto

El curso es **mudo por diseño**: la pantalla enseña la cosa y su cifra, y la voz
solo **apunta**. No hay que describir lo que se ve ni leer las etiquetas en voz
alta — si la frase repite el rótulo, sobra.

- **El minuto de entrada de cada frase es su sitio exacto.** Cada frase se graba
  suelta y se coloca en ese instante; el silencio entre frases es parte del
  clip, no un hueco que haya que rellenar.
- **Ritmo medido**: la voz de referencia (Charon) lee entre 1.2 y 1.7 palabras
  por segundo. La columna «dura» es la estimación a 1.3 palabras/s más 0.4 s de
  aire. Si al grabar te sale bastante más larga, **acorta el texto** antes que
  acelerar la lectura.
- **Tono**: afirmativo y sin prisa. Son frases cortas a propósito; la pausa
  después de cada una hace el trabajo.
- Deja **0.8 s de silencio** al final de cada pieza.
- La intro y el cierre **no llevan voz**: son marca y cama de sonido.

Si vas a montar tú el audio, la ruta que espera la herramienta de montaje es
`exports/verticales/esp32/voz/<pieza>.wav`, un wav por pieza con las frases ya
colocadas en su instante. Con eso, `unir_vertical.py` (sin `--sin-voz`) rehace
las piezas sonorizadas y el montaje.

---

## Intro

`00-intro` · 11.23 s · **sin voz** (pieza de marca)


## 01 · El reloj que no para

`01-el-reloj-que-no-para` · 30.30 s · 5 frases

| Entra | Frase | Dura | Qué se ve |
|---|---|---|---|
| **0:01.30** | Esto es un ESP32. | 3.5 s | el encapsulado se dibuja solo |
| **0:04.90** | Doscientos cuarenta megahercios. | 2.7 s | 240 megahercios (hoja de datos, etiqueta gris) |
| **0:09.40** | Mientras lo miras, ya lleva miles de millones de ciclos. | 8.1 s | el chip se abre en sus ocho bloques |
| **0:18.40** | Dos nucleos, medio mega de memoria, radio propia. | 6.6 s | el tren de pulsos: el latido que lo mueve todo |
| **0:25.40** | Todo eso, aqui dentro. | 3.5 s | vuelve el encapsulado, con el contador todavia subiendo |

Cola de silencio al final: **1.42 s**

## 02 · Dos nucleos

`02-dos-nucleos` · 31.25 s · 5 frases

| Entra | Frase | Dura | Qué se ve |
|---|---|---|---|
| **0:01.00** | Doce tareas independientes. | 2.7 s | las doce tareas se dibujan en una fila, con hueco entre ba |
| **0:04.20** | Un nucleo, una detras de otra. | 5.0 s | dato: 148.6 milisegundos, el makespan de un nucleo |
| **0:11.00** | Dos nucleos se las reparten. | 4.2 s | relevo simultaneo: la fila se parte en dos (NUCLEO 0 ambar |
| **0:17.50** | Casi el doble de rapido. | 4.2 s | dato: x1.98, veces mas rapido |
| **0:24.50** | Porque las tareas no se parten. | 5.0 s | dato: 2, limite teorico (etiqueta gris, es teoria) |

Cola de silencio al final: **1.73 s**

## 03 · Lo que cabe en 520 KB

`03-lo-que-cabe-en-520-kb` · 30.95 s · 4 frases

| Entra | Frase | Dura | Qué se ve |
|---|---|---|---|
| **0:01.30** | Quinientos veinte kilobytes de memoria suenan a mucho. | 6.6 s | el contenedor vacio se dibuja (contorno, sin relleno) |
| **0:09.35** | Una imagen ya pesa más de cien kilobytes. | 6.6 s | 112.5, kilobytes de un fotograma (calculado) |
| **0:17.40** | Caben cuatro. El quinto no entra. | 5.0 s | caen el segundo, el tercero y el cuarto, con aire entre ca |
| **0:23.90** | Por eso aquí se piensa en bytes. | 5.8 s | el hueco de arriba: mas bajo que una pieza, no cabe un qui |

Cola de silencio al final: **1.27 s**

## 04 · Un ciclo son metro y cuarto

`04-un-ciclo-son-metro-y-cuarto` · 34.27 s · 4 frases

| Entra | Frase | Dura | Qué se ve |
|---|---|---|---|
| **0:01.50** | Ese latido no nace dentro del chip. | 5.8 s | se dibuja el tren del cristal: tres pulsos anchos en tinta |
| **0:09.60** | Ahí dentro, un lazo lo acelera. | 5.0 s | relevo: arriba el mismo tren en gris, abajo el de la CPU e |
| **0:16.40** | Cada uno de esos ciclos dura casi nada. | 6.6 s | relevo: el tren solo, en gris; bajo su primer periodo entr |
| **0:25.60** | En ese rato, la luz no cruza tu habitación. | 7.3 s | la luz cruza de un extremo al otro (2.2 s, a velocidad con |

Cola de silencio al final: **1.35 s**

## 05 · Un pin es un bit

`05-un-pin-es-un-bit` · 36.15 s · 4 frases

| Entra | Frase | Dura | Qué se ve |
|---|---|---|---|
| **0:00.90** | Escribir aqui es mover patas del chip. | 5.8 s | el registro de 32 bits aparece, unos pocos en ambar |
| **0:08.00** | Miles de millones de combinaciones posibles. | 5.0 s | el registro cambia de valor |
| **0:21.00** | Pero nada sube instantaneamente. | 3.5 s | zoom a un pin: la curva de carga, con el 10% y el 90% marc |
| **0:29.00** | El mundo real tiene inercia. | 4.2 s | con mas capacidad (cian) el mismo flanco se estira |

Cola de silencio al final: **2.90 s**

## 06 · Voltajes que no existen

`06-voltajes-que-no-existen` · 37.75 s · 5 frases

| Entra | Frase | Dura | Qué se ve |
|---|---|---|---|
| **0:01.50** | Solo hay dos alturas. Nada en medio. | 5.8 s | se dibuja el tren PWM al 50 % en TINTA, con la discontinua |
| **0:08.90** | No existe en ningún instante. Existe en la media. | 7.3 s | el tren pasa a APAGADO y encima entra en AMBAR lo que fabr |
| **0:16.90** | Menos tiempo encendido, menos media. | 4.2 s | mismo cuadro con el duty al 30 %: pulsos mas estrechos y l |
| **0:23.30** | De cerca, la línea no es plana. | 5.8 s | vuelta al 50 % y cambio de escala vertical: el cuadro mide |
| **0:30.20** | Diez veces menos condensador, diez veces más rizado. | 6.6 s | misma escala, dos salidas: en gris la de 1 microfaradio, e |

Cola de silencio al final: **1.00 s**

## 07 · El mundo entra en escalones

`07-el-mundo-en-escalones` · 36.50 s · 5 frases

| Entra | Frase | Dura | Qué se ve |
|---|---|---|---|
| **0:01.60** | El mundo es continuo. | 3.5 s | se dibujan el eje y la rampa continua, en tinta |
| **0:06.20** | El chip solo sabe contar. | 4.2 s | 3.3 voltios de fondo de escala (hoja de datos, etiqueta gr |
| **0:11.60** | Cuatro mil noventa y seis peldaños, y nada entre ellos. | 8.1 s | 4096 escalones en doce bits |
| **0:21.00** | Lo que cae en medio se pierde para siempre. | 7.3 s | relevo: el error, diente de sierra ambar sobre el cero dis |
| **0:30.40** | Aun así: setenta y cuatro decibelios. | 5.0 s | 74 decibelios sobre el ruido |

Cola de silencio al final: **1.08 s**

## 08 · Dos cables o cuatro

`08-dos-cables-o-cuatro` · 31.00 s · 4 frases

| Entra | Frase | Dura | Qué se ve |
|---|---|---|---|
| **0:00.90** | Hablar con un sensor: dos cables, o cuatro. | 6.6 s | se dibuja el byte I2C: ocho tramos de datos y el noveno, e |
| **0:09.50** | Cada byte por I2C paga un bit extra. | 6.6 s | se dibuja la fila I2C (rotulo ambar), a la escala real de  |
| **0:16.50** | SPI usa cuatro cables y no espera nada. | 6.6 s | relevo simultaneo: aparece la fila SPI (rotulo cian, un hi |
| **0:23.50** | Ciento trece veces mas rapido: cuestion de cables. | 6.6 s | dato: x113, veces mas rapido |

Cola de silencio al final: **0.95 s**

## 09 · Doce centimetros y medio

`09-doce-centimetros-y-medio` · 32.28 s · 4 frases

| Entra | Frase | Dura | Qué se ve |
|---|---|---|---|
| **0:01.00** | La radio del chip habla en centímetros. | 5.8 s | la onda de 2.437 GHz se dibuja sola, llenando la franja |
| **0:08.50** | De cresta a cresta. | 3.5 s | se marca una longitud de onda, de cresta a cresta |
| **0:15.40** | La antena quiere un cuarto de eso. | 5.8 s | el mismo trazo se encoge al cuarto de onda |
| **0:23.00** | Pero dentro del sustrato, la onda se acorta. | 6.6 s | la placa llena la franja, con el meandro grande en la esqu |

Cola de silencio al final: **2.73 s**

## 10 · Lo que de verdad viaja

`10-lo-que-de-verdad-viaja` · 36.50 s · 5 frases

| Entra | Frase | Dura | Qué se ve |
|---|---|---|---|
| **0:02.60** | La hoja promete sesenta y cinco megabits. | 5.8 s | 65 megabits por segundo (hoja de datos, etiqueta gris) |
| **0:09.90** | Antes de hablar hay que esperar. | 5.0 s | 370 microsegundos de aire por trama |
| **0:15.60** | Y solo la mitad lleva datos. | 5.0 s | 49.9 por ciento son datos |
| **0:22.60** | Con paquetes pequeños es mucho peor. | 5.0 s | 6.2 por ciento son datos |
| **0:29.90** | Eso es lo que de verdad viaja. | 5.8 s | 32.5 megabits útiles: lo que queda de los 65 |

Cola de silencio al final: **0.82 s**

## 11 · Hablar poco para durar mucho

`11-hablar-poco-para-durar` · 35.15 s · 5 frases

| Entra | Frase | Dura | Qué se ve |
|---|---|---|---|
| **0:00.90** | Transmitir es lo que mas gasta. | 5.0 s | arrancan los tres paquetes del anuncio BLE, uno por canal |
| **0:07.60** | Y casi siempre esta callado. | 4.2 s | relevo: diez anuncios sobre un segundo entero, casi todo s |
| **0:15.30** | Ciento treinta miliamperios mientras habla. | 4.2 s | dato: 130, miliamperios al hablar (hoja de datos, etiqueta |
| **0:20.90** | La media no es un promedio. | 5.0 s | relevo: barra habla/calla, la corriente media es una integ |
| **0:28.50** | Hablar menos baja la corriente. | 4.2 s | dato: 215, microamperios si el anuncio fuese cada segundo |

Cola de silencio al final: **2.40 s**

## 12 · La linea que se interrumpe

`12-la-linea-que-se-interrumpe` · 38.30 s · 5 frases

| Entra | Frase | Dura | Qué se ve |
|---|---|---|---|
| **0:01.90** | Un bucle pregunta una vez por vuelta. | 5.8 s | caen los cuatro sucesos, en ambar, entre pregunta y pregun |
| **0:09.20** | El suceso tiene que esperar su turno. | 5.8 s | relevo: el tren pasa a gris y el ambar se lo quedan las es |
| **0:16.40** | A veces, una vuelta entera. | 4.2 s | relevo: las 400 esperas ordenadas, una recta (la uniforme) |
| **0:23.40** | De media, medio periodo perdido. | 4.2 s | relevo: la linea del tiempo, sin bucle. Suceso arriba |
| **0:29.40** | La interrupcion no pregunta. Cuatro ordenes de magnitud. | 6.6 s | 2.7 microsegundos, el peor: la misma etiqueta, otra unidad |

Cola de silencio al final: **2.35 s**

## 13 · El planificador

`13-el-planificador` · 35.55 s · 5 frases

| Entra | Frase | Dura | Qué se ve |
|---|---|---|---|
| **0:01.50** | Una tarea que despierta cada diez milisegundos. | 5.8 s | se dibuja el cronograma: NUCLEO 0 con doce despertares reg |
| **0:09.20** | Sola en su núcleo, llega puntual. | 5.0 s | 6.9 microsegundos de jitter, medidos sobre esos doce despe |
| **0:15.20** | Otra tarea entra, y ya no llega igual. | 6.6 s | entra el acaparador: las marcas se desordenan y el renglon |
| **0:22.90** | El chip tiene otro núcleo libre. | 5.0 s | 2 nucleos en el chip (hoja de datos, etiqueta gris) |
| **0:29.00** | Anclada ahí, el jitter desaparece. | 4.2 s | 137 veces menos jitter |

Cola de silencio al final: **2.30 s**

## 14 · La vida de una pila

`14-la-vida-de-una-pila` · 40.95 s · 5 frases

| Entra | Frase | Dura | Qué se ve |
|---|---|---|---|
| **0:01.50** | El chip no gasta siempre lo mismo. | 5.8 s | la escalera de consumo en decadas: dormir, ligero, pensar, |
| **0:08.40** | Entre hablar y dormir hay dieciseis mil veces. | 6.6 s | se enciende la barra de dormir: 10 microamperios (gris) |
| **0:17.30** | La autonomia no la decide el pico: la decide el tiempo. | 8.9 s | la linea de tiempo: una rayita por despertar, y 99 microam |
| **0:29.00** | Despertar menos alarga la vida. | 4.2 s | la grafica: autonomia contra cada cuanto despierta, 21.7 a |
| **0:34.20** | Pero la pila se gasta sola. | 5.0 s | sin cifra abajo, se traza la curva de la pila real y se ap |

Cola de silencio al final: **1.73 s**

## Cierre

`15-cierre` · 10.62 s · **sin voz** (pieza de marca)

