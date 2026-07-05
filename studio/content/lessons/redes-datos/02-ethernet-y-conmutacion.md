---
title: Ethernet y conmutación LAN
level: intro
summary: Tramas, direccionamiento MAC, switches con tabla CAM, VLAN y STP organizan la red local desde 10 Mbit/s hasta 800 Gbit/s.
tags: [ethernet, vlan, switch, stp, mac]
minutes: 10
order: 2
---

## Objetivos

- Describir la estructura de una trama Ethernet y el papel del direccionamiento MAC.
- Distinguir el dominio de colisión del dominio de difusión y explicar cómo el switch reduce el primero.
- Explicar el aprendizaje y uso de la tabla CAM en un switch Ethernet.
- Explicar VLAN, el etiquetado 802.1Q (trunking) y el propósito conceptual de STP.
- Situar la evolución de velocidades Ethernet desde 10 Mbit/s hasta 800 Gbit/s.

## La trama Ethernet y el direccionamiento MAC

**Ethernet** es, con enorme margen, la tecnología de capa de enlace dominante en redes locales cableadas. Su unidad de transmisión es la **trama** (*frame*), con una estructura fija que incluye un preámbulo de sincronización, la **dirección MAC de destino** (6 bytes), la **dirección MAC de origen** (6 bytes), un campo de tipo/longitud (EtherType), la carga útil (46 a 1500 bytes en Ethernet estándar, hasta 9000 bytes en tramas *jumbo*), y una secuencia de verificación de trama (FCS, una suma de verificación CRC-32 que detecta errores de transmisión).

La **dirección MAC** (*Media Access Control*) es un identificador de 48 bits, asignado típicamente de forma fija por el fabricante de la interfaz de red (los primeros 24 bits identifican al fabricante, el OUI), que actúa como dirección física local: única en principio para cada interfaz de red del mundo, y usada exclusivamente para el direccionamiento dentro del mismo segmento de enlace local, a diferencia de la dirección IP (capa 3), que es jerárquica y sirve para enrutar entre redes distintas. Una trama Ethernet nunca sale de un enlace local sin ser reencapsulada: cuando un paquete IP cruza un router hacia otra red, sus direcciones MAC de trama se reescriben en cada salto, mientras las direcciones IP origen y destino permanecen inalteradas de extremo a extremo.

## Dominio de colisión frente a dominio de difusión

Un **dominio de colisión** es el conjunto de dispositivos que comparten el mismo medio físico de tal forma que una transmisión simultánea de dos de ellos provoca una colisión eléctrica detectable —el problema central que resolvía el protocolo CSMA/CD de la Ethernet original sobre cable coaxial compartido o sobre un hub, donde todos los puertos formaban un único dominio de colisión. Un **switch**, a diferencia de un hub, conmuta cada trama únicamente hacia el puerto de destino correcto (no la retransmite a todos los puertos indiscriminadamente), lo que convierte cada puerto del switch en su propio dominio de colisión independiente: con un switch, dos dispositivos conectados a puertos distintos pueden transmitir simultáneamente sin colisionar entre sí, eliminando en la práctica el problema de colisión que dominaba el diseño de Ethernet en sus primeras décadas (y volviendo obsoleto, para efectos prácticos, el propio CSMA/CD en redes conmutadas full-duplex modernas).

El **dominio de difusión** (*broadcast domain*), en cambio, es el conjunto de dispositivos que reciben una trama de difusión (dirigida a la dirección MAC de difusión `FF:FF:FF:FF:FF:FF`) enviada por cualquiera de ellos; un switch, a diferencia de lo que hace con el dominio de colisión, *no* segmenta el dominio de difusión por defecto: una trama de difusión enviada por cualquier puerto se reenvía a todos los demás puertos del switch (y de cualquier switch conectado a él), de modo que una LAN plana completa —potencialmente cientos de dispositivos y muchos switches interconectados— constituye un único dominio de difusión, salvo que se segmente deliberadamente mediante VLAN o mediante routers, que sí detienen el tráfico de difusión en su frontera.

## La tabla CAM

Un switch Ethernet aprende dinámicamente qué dirección MAC está conectada a cada uno de sus puertos observando el campo de dirección MAC origen de cada trama que recibe, y almacena esa asociación en su **tabla CAM** (*Content-Addressable Memory*, también llamada tabla de direccionamiento MAC o tabla de reenvío), una estructura optimizada en hardware para búsquedas de coincidencia muy rápidas. Cuando llega una trama con destino a una dirección MAC ya presente en la tabla, el switch la reenvía únicamente por el puerto asociado; si la dirección de destino no está aún en la tabla (por ejemplo, la primera trama enviada a un dispositivo del que el switch nunca ha visto tráfico), el switch recurre a una **inundación** (*flooding*): reenvía la trama por todos los puertos excepto el de entrada, exactamente como haría un hub, hasta que el dispositivo de destino responda y el switch aprenda finalmente en qué puerto reside. Las entradas de la tabla CAM expiran tras un tiempo de inactividad (típicamente 300 segundos), lo que permite que el switch se adapte automáticamente si un dispositivo cambia de puerto físico, a costa de una breve inundación mientras se reaprende la nueva ubicación.

## VLAN, trunking 802.1Q y STP

Una **VLAN** (*Virtual LAN*) segmenta lógicamente un dominio de difusión físico único en múltiples dominios de difusión independientes, sin necesidad de cableado ni switches físicos separados: los puertos de un switch se asignan a una VLAN u otra por configuración, y el tráfico de difusión de una VLAN no llega jamás a los puertos de otra VLAN, incluso si comparten el mismo switch físico. Esto permite separar lógicamente, por ejemplo, el tráfico de distintos departamentos de una empresa o distintos tipos de tráfico (datos, voz, gestión) sobre la misma infraestructura física, mejorando tanto la seguridad (aislamiento de tráfico) como el rendimiento (dominios de difusión más pequeños generan menos tráfico de difusión innecesario por segmento).

Cuando el tráfico de múltiples VLAN debe atravesar un único enlace físico entre dos switches (un **enlace troncal** o *trunk*), el estándar **802.1Q** inserta una etiqueta (*tag*) de 4 bytes dentro de la cabecera de la trama Ethernet, que incluye un identificador de VLAN (VLAN ID, de 12 bits, permitiendo hasta 4094 VLAN utilizables), de modo que el switch receptor sepa a qué VLAN pertenece cada trama que llega por el enlace troncal compartido, y pueda reenviarla únicamente a los puertos de esa VLAN en el otro extremo.

El **STP** (*Spanning Tree Protocol*) resuelve un problema distinto: en topologías con enlaces redundantes entre switches (deseables por tolerancia a fallos), una trama de difusión puede circular indefinidamente en un bucle, multiplicándose exponencialmente y saturando la red en cuestión de segundos (una **tormenta de difusión**). STP construye conceptualmente un árbol lógico sin bucles sobre la topología física redundante: elige un switch raíz, calcula la ruta de menor costo de cada switch hacia la raíz, y bloquea administrativamente (sin desconectar físicamente) los puertos redundantes que crearían un bucle, dejándolos en reserva para activarse automáticamente solo si el enlace primario falla.

## Evolución de velocidades Ethernet

Ethernet ha escalado su velocidad nominal varios órdenes de magnitud desde su origen sin cambiar su formato de trama fundamental, manteniendo una compatibilidad conceptual notable a través de generaciones: 10 Mbit/s (Ethernet original, coaxial o par trenzado), 100 Mbit/s (Fast Ethernet, años 90), 1 Gbit/s (Gigabit Ethernet, estándar de facto en LAN de escritorio desde los 2000), 10 Gbit/s (backbone de campus y centros de datos), y hoy 25, 40, 100, 400 y hasta **800 Gbit/s** en los enlaces troncales de los centros de datos hiperescala más exigentes, típicamente sobre fibra óptica con múltiples carriles ópticos o eléctricos en paralelo (por ejemplo, 800GBASE se implementa habitualmente como ocho carriles de 100 Gbit/s combinados). Esta escalada de cinco órdenes de magnitud en velocidad, sostenida durante más de cuatro décadas, es lo que ha permitido que Ethernet desplace prácticamente cualquier tecnología de red local competidora (Token Ring, FDDI, ATM en LAN) y se convierta en el estándar prácticamente universal de interconexión, tanto en la oficina como en el centro de datos.

## Ideas clave

- La trama Ethernet usa direcciones MAC de 48 bits para direccionamiento local; a diferencia de IP, no es jerárquica ni sirve para enrutar entre redes.
- Un switch segmenta el dominio de colisión por puerto, pero no el dominio de difusión, que abarca toda la LAN plana salvo segmentación explícita.
- La tabla CAM aprende dinámicamente la asociación MAC-puerto observando el origen de las tramas, e inunda cuando desconoce el destino.
- VLAN segmenta lógicamente los dominios de difusión sobre la misma infraestructura física; 802.1Q etiqueta las tramas para transportar múltiples VLAN sobre un enlace troncal.
- STP previene tormentas de difusión en topologías redundantes bloqueando lógicamente los puertos que crearían bucles, sin sacrificar la redundancia física subyacente.

## Para seguir

La siguiente lección, *IP y enrutamiento*, sube a la capa de red: direccionamiento IPv4/IPv6, subneteo, tablas de rutas y los protocolos que permiten que el tráfico cruce, más allá de la LAN local vista aquí, cualquier número de redes intermedias hasta su destino.
