---
title: Tiempo, relojes y orden de eventos
level: medio
summary: Por qué los relojes físicos no bastan para ordenar eventos distribuidos, la relación happened-before, relojes lógicos y vectoriales, y TrueTime de Spanner.
tags: [relojes, lamport, ntp, orden, spanner]
minutes: 11
order: 2
---

## Objetivos

- Explicar por qué los relojes físicos de máquinas distintas no pueden usarse directamente para ordenar eventos.
- Describir cómo NTP y PTP sincronizan relojes y qué precisión alcanza cada uno.
- Definir la relación *happened-before* de Lamport y su papel como noción de causalidad.
- Construir y aplicar relojes lógicos de Lamport y relojes vectoriales con un ejemplo trabajado.
- Explicar la idea de TrueTime de Google Spanner y cómo convierte la incertidumbre del reloj en una garantía.

## El problema: relojes que mienten

Cada computadora mide el tiempo con un oscilador de cuarzo cuya frecuencia real difiere ligeramente de la nominal. Esa **deriva** (*drift*) es típicamente de 10 a 100 partes por millón: un reloj que deriva 50 ppm se desvía unos **4.3 segundos por día** si nadie lo corrige. Peor aún, la deriva varía con la temperatura, así que dos máquinas del mismo rack divergen a ritmos distintos e impredecibles. La consecuencia es directa: si el servidor A registra un evento a las 10:00:00.500 y el servidor B registra otro a las 10:00:00.400, **nada garantiza que el evento de B ocurrió antes** —la diferencia puede estar enteramente dentro del error de sincronización de ambos relojes. Ordenar eventos distribuidos por su marca de tiempo local es uno de los errores más clásicos y sutiles del área: produce sistemas que funcionan en pruebas y corrompen datos en producción, donde las condiciones de carrera dependen de milisegundos.

**NTP** (*Network Time Protocol*) mitiga la deriva sincronizando cada máquina contra servidores de referencia organizados en estratos (el estrato 0 son relojes atómicos y GPS; el estrato 1, servidores conectados directamente a ellos). NTP estima el desfase descontando la mitad del RTT medido, lo que funciona bien cuando la ruta es simétrica; en Internet abierta logra precisiones de **1 a 50 ms**, y en una LAN bien administrada, de decenas a centenas de microsegundos. Para necesidades mayores existe **PTP** (*Precision Time Protocol*, IEEE 1588), que con soporte de hardware en las tarjetas de red y switches que compensan sus propios retardos alcanza precisión **sub-microsegundo**; se usa en trading de alta frecuencia, telecomunicaciones (las redes celulares TDD lo requieren) y metrología. Pero incluso PTP deja una incertidumbre residual: la sincronización perfecta es físicamente imposible, y todo diseño correcto debe convivir con un error de reloj acotado pero no nulo.

## Happened-before: causalidad sin relojes

En 1978, Leslie Lamport propuso en *"Time, Clocks, and the Ordering of Events in a Distributed System"* —quizá el artículo más influyente del área— abandonar el tiempo físico y definir el orden a partir de la **causalidad potencial**. La relación **happened-before**, escrita $a \rightarrow b$, se define por tres reglas:

1. Si $a$ y $b$ ocurren en el mismo proceso y $a$ precede a $b$ en su ejecución local, entonces $a \rightarrow b$.
2. Si $a$ es el envío de un mensaje y $b$ es su recepción, entonces $a \rightarrow b$.
3. Transitividad: si $a \rightarrow b$ y $b \rightarrow c$, entonces $a \rightarrow c$.

Si ni $a \rightarrow b$ ni $b \rightarrow a$, los eventos son **concurrentes** ($a \parallel b$): ninguno pudo haber influido en el otro, y ningún observador tiene derecho a afirmar cuál "ocurrió primero". Esta es la observación profunda: en un sistema distribuido el orden total de eventos no existe por defecto; solo existe un **orden parcial** inducido por los mensajes, y cualquier orden total que el sistema necesite debe construirse explícitamente.

## Relojes lógicos y relojes vectoriales

Un **reloj de Lamport** materializa happened-before con un simple contador entero $L$ por proceso: se incrementa antes de cada evento local, se adjunta a cada mensaje enviado, y al recibir un mensaje con marca $t$ el receptor hace $L \leftarrow \max(L, t) + 1$. La garantía resultante es unidireccional: si $a \rightarrow b$ entonces $L(a) < L(b)$. La recíproca **no** vale: que $L(a) < L(b)$ no implica causalidad —dos eventos concurrentes pueden tener cualquier par de valores. Los relojes de Lamport bastan para construir un orden total arbitrario pero consistente con la causalidad (desempatando por identificador de proceso), útil por ejemplo para ordenar operaciones en una cola de exclusión mutua distribuida.

Los **relojes vectoriales** (Fidge y Mattern, 1988) recuperan la información que Lamport pierde: cada proceso $i$ de un sistema de $n$ procesos mantiene un vector $V_i[1..n]$, incrementa su propia componente $V_i[i]$ en cada evento, y al recibir un mensaje toma el máximo componente a componente y luego incrementa la suya. Con vectores, la equivalencia es completa: $a \rightarrow b$ **si y solo si** $V(a) < V(b)$ (menor o igual en toda componente y estrictamente menor en alguna); si ninguno domina al otro, los eventos son concurrentes con certeza.

Ejemplo trabajado con tres procesos:

```
P1: a[1,0,0] ──── b[2,0,0] ─────────────── envía m2 ──→ f[3,0,0]
                     │
                     └─ envía m1 a P2
P2: ───────── c[2,1,0] (recibe m1) ── d[2,2,0] ──────────────────
P3: e[0,0,1] ────────────────────────── g[3,0,2] (recibe m2)
```

Aquí $b \rightarrow c$ (el mensaje m1 lo establece) y efectivamente $[2,0,0] < [2,1,0]$. En cambio $d$ con $[2,2,0]$ y $g$ con $[3,0,2]$ no se dominan mutuamente (la segunda componente favorece a $d$, la primera y tercera a $g$): son concurrentes, y el sistema lo sabe. Esta detección de concurrencia es exactamente lo que usan sistemas como Amazon Dynamo para detectar escrituras conflictivas en réplicas distintas y presentarlas ambas al cliente en lugar de perder una silenciosamente. El costo es el tamaño: el vector crece con el número de participantes, lo que motiva variantes acotadas (*dotted version vectors*) en la práctica.

## TrueTime: comprar certeza con incertidumbre explícita

Google Spanner, la base de datos distribuida global de Google, tomó en 2012 una ruta distinta y notable: en vez de renunciar al tiempo físico, **hizo la incertidumbre explícita y la acotó con hardware**. Su API **TrueTime** no devuelve un instante, sino un intervalo: $TT.now() = [earliest, latest]$, con la garantía de que el tiempo real verdadero está dentro del intervalo. Manteniendo relojes GPS y relojes atómicos en cada datacenter, Google acota el semiancho del intervalo (ε) a típicamente **1–7 ms**.

Con esa garantía, Spanner implementa *commit wait*: al confirmar una transacción, el coordinador le asigna la marca $latest$ del intervalo actual y **espera deliberadamente** hasta que $TT.now().earliest$ supere esa marca antes de reportar el commit al cliente. Esa espera —de unos pocos milisegundos— garantiza que cualquier transacción que empiece después del commit reportado verá una marca de tiempo estrictamente mayor, lo que da a Spanner **consistencia externa** (linealizabilidad entre transacciones a escala global) usando tiempo físico. La lección conceptual trasciende a Spanner: no se necesita un reloj perfecto, se necesita un reloj con **error acotado y conocido**; la certeza se puede comprar pagando con latencia proporcional a la incertidumbre.

## Ideas clave

- Los relojes físicos derivan (decenas de ppm) y ni NTP (~1–50 ms en WAN) ni PTP (sub-µs con hardware) eliminan el error: ordenar eventos por timestamp local es incorrecto por diseño.
- Happened-before define el único orden objetivo que existe en un sistema distribuido: un orden parcial inducido por la secuencia local y los mensajes; lo demás es concurrencia.
- Los relojes de Lamport garantizan $a \rightarrow b \Rightarrow L(a) < L(b)$ pero no la recíproca; sirven para construir órdenes totales consistentes con la causalidad.
- Los relojes vectoriales caracterizan la causalidad exactamente ($a \rightarrow b \Leftrightarrow V(a) < V(b)$) y detectan concurrencia con certeza, al costo de un vector de tamaño proporcional al número de procesos.
- TrueTime de Spanner expone el error del reloj como un intervalo acotado por GPS y relojes atómicos, y con una espera de commit del tamaño de esa incertidumbre logra consistencia externa global.

## Para seguir

La siguiente lección, *Consistencia y el teorema CAP*, usa este vocabulario de orden y simultaneidad para clasificar las garantías que un almacén de datos replicado puede —y no puede— ofrecer.
