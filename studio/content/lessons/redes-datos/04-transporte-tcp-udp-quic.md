---
title: "Transporte: TCP, UDP y QUIC"
level: medio
summary: El handshake de tres vías, el control de flujo y congestión de TCP, las limitaciones de UDP y cómo QUIC resuelve el bloqueo de cabecera de línea.
tags: [tcp, udp, quic, congestion, http3]
minutes: 10
order: 4
---

## Objetivos

- Describir el establecimiento de conexión TCP mediante el three-way handshake.
- Explicar el control de flujo y los algoritmos de control de congestión: slow start, AIMD, CUBIC y BBR.
- Explicar el bloqueo de cabecera de línea (*head-of-line blocking*) y por qué afecta a TCP.
- Contrastar UDP con TCP y describir escenarios donde UDP es la elección correcta.
- Explicar QUIC y su adopción en HTTP/3 como solución a las limitaciones estructurales de TCP.

## El three-way handshake de TCP

**TCP** (*Transmission Control Protocol*) es un protocolo de transporte **orientado a conexión**: antes de intercambiar datos de aplicación, el cliente y el servidor establecen explícitamente un estado compartido de conexión mediante un intercambio de tres mensajes conocido como **three-way handshake**. El cliente envía un segmento con la bandera `SYN` (*synchronize*) y un número de secuencia inicial aleatorio; el servidor responde con `SYN-ACK`, confirmando el número de secuencia del cliente y proponiendo su propio número de secuencia inicial; el cliente responde finalmente con `ACK`, confirmando el número de secuencia del servidor, momento en el cual ambas partes consideran la conexión establecida y pueden empezar a intercambiar datos. Este intercambio, aunque breve, consume un **round-trip time** (RTT) completo antes de que pueda fluir el primer byte de datos de aplicación —un costo fijo de latencia que, sobre enlaces de alta latencia (un satélite GEO, por ejemplo, introduce ~240 ms de retardo de propagación por tramo, lo que se traduce en un RTT de ~480–560 ms), resulta significativo para conexiones cortas, y que ha motivado buena parte del diseño de QUIC, como se ve más abajo.

## Control de flujo y control de congestión

El **control de flujo** de TCP protege al *receptor* de ser desbordado: el receptor anuncia continuamente, en cada segmento, una **ventana de recepción** (*receive window*) que indica cuántos bytes adicionales está dispuesto a aceptar sin haberlos aún entregado a la aplicación, y el emisor nunca envía más allá de ese límite anunciado. El **control de congestión**, en cambio, protege a la *red* (no al receptor) de ser desbordada, y es enteramente responsabilidad del emisor, que debe inferir el estado de congestión de la red —normalmente invisible directamente— a partir de señales indirectas como la pérdida de segmentos o el aumento del RTT.

El algoritmo clásico combina varias fases: **slow start**, donde la ventana de congestión (*cwnd*) comienza pequeña y se **duplica** cada RTT (crecimiento exponencial) hasta alcanzar un umbral o detectar la primera señal de pérdida, con el objetivo de sondear rápidamente la capacidad disponible del enlace sin conocerla de antemano; y **AIMD** (*Additive Increase, Multiplicative Decrease*), donde, superada la fase de slow start, la ventana crece linealmente (aditivamente) mientras no hay pérdida, y se reduce drásticamente (multiplicativamente, típicamente a la mitad) en cuanto se detecta pérdida, un patrón en diente de sierra que converge, con múltiples flujos TCP competitivos compartiendo un cuello de botella, hacia un reparto razonablemente equitativo de la capacidad disponible entre ellos.

Los algoritmos modernos refinan esta base clásica: **CUBIC**, el algoritmo por defecto en Linux desde hace más de una década, hace crecer la ventana según una función cúbica del tiempo transcurrido desde la última reducción (en vez de linealmente), lo que le permite crecer más agresivamente en enlaces de alta capacidad y alta latencia (*long fat networks*) donde AIMD puro converge demasiado lentamente. **BBR** (*Bottleneck Bandwidth and Round-trip propagation time*), desarrollado por Google, abandona la premisa de que la pérdida de paquetes es necesariamente la señal principal de congestión (una premisa problemática en redes modernas con buffers grandes, el fenómeno de *bufferbloat*, donde la pérdida llega tarde y tras acumular latencia innecesaria) y en su lugar modela activamente el ancho de banda del cuello de botella y el RTT mínimo observado, ajustando su tasa de envío para operar cerca del punto óptimo teórico sin depender de inducir pérdida deliberadamente para sondear el límite.

## Bloqueo de cabecera de línea (Head-of-Line Blocking)

TCP garantiza **entrega ordenada**: la aplicación receptora nunca ve el byte $N+1$ antes que el byte $N$, incluso si el segmento que contiene $N+1$ llegó físicamente antes. Esta garantía, extremadamente conveniente para la aplicación, tiene un costo estructural conocido como **bloqueo de cabecera de línea** (*head-of-line blocking*, HOL blocking): si el segmento que contiene el byte $N$ se pierde en tránsito, *todos* los bytes posteriores ya recibidos y almacenados en el receptor (incluyendo $N+1, N+2$, etc.) quedan retenidos en el buffer de recepción, invisibles para la aplicación, hasta que el segmento perdido se retransmita y llegue exitosamente —incluso si esos bytes posteriores pertenecen, lógicamente, a un recurso de aplicación completamente independiente del que se perdió (como ocurre al multiplexar múltiples streams HTTP/2 sobre una única conexión TCP: la pérdida de un solo paquete bloquea *todos* los streams multiplexados, no solo el afectado). Este problema, invisible para conexiones TCP simples con un único flujo de datos, se volvió un cuello de botella de rendimiento significativo precisamente cuando HTTP/2 introdujo la multiplexación de múltiples recursos sobre una sola conexión TCP.

## UDP: cuándo usarlo

**UDP** (*User Datagram Protocol*) es deliberadamente minimalista: no establece conexión, no garantiza entrega, no garantiza orden, y no implementa control de congestión propio —simplemente entrega datagramas individuales lo mejor que puede (*best effort*), con apenas una cabecera de 8 bytes (puertos origen/destino, longitud y suma de verificación opcional). Esta ausencia deliberada de garantías es precisamente su virtud en escenarios donde las garantías de TCP son contraproducentes: en voz y video en tiempo real (VoIP, videollamada), un paquete de audio perdido o tardío es simplemente inútil —reproducirlo tarde, tras esperar su retransmisión al estilo TCP, es peor que descartarlo y continuar con el siguiente—, de modo que UDP (típicamente con RTP encima, como se vio en la lección de conmutación y señalización) permite a la aplicación decidir ella misma cómo tolerar la pérdida, sin la latencia añadida de retransmisiones TCP. UDP también domina en DNS (consultas cortas donde el costo del handshake TCP sería desproporcionado), en streaming de video con tolerancia a pérdida controlada, y en escenarios donde la propia aplicación implementa su propia fiabilidad y control de congestión a medida —precisamente lo que hace QUIC, construido sobre UDP.

## QUIC y HTTP/3

**QUIC** (*Quick UDP Internet Connections*), estandarizado por el IETF y desplegado a gran escala por Google desde 2013, es un protocolo de transporte moderno construido *sobre* UDP (no como reemplazo del núcleo del sistema operativo, sino como una biblioteca en espacio de usuario, lo que permite iterar su diseño mucho más rápido que un cambio al núcleo de TCP en millones de sistemas operativos desplegados) que reimplementa deliberadamente las garantías útiles de TCP —fiabilidad, control de flujo, control de congestión moderno tipo BBR/CUBIC— pero resolviendo sus dos limitaciones estructurales centrales. Primero, QUIC combina el establecimiento de la conexión de transporte con la negociación criptográfica TLS 1.3 en un único intercambio, reduciendo el costo de conexión de los tradicionales dos RTT separados (uno para TCP, otro para TLS) a un solo RTT, o incluso **cero RTT** para una reconexión a un servidor ya visitado previamente (reanudando parámetros criptográficos guardados). Segundo, y más importante estructuralmente, QUIC multiplexa múltiples streams **independientes** dentro de la misma conexión de forma nativa a nivel de transporte, de modo que la pérdida de un paquete perteneciente a un stream bloquea únicamente ese stream, no los demás —eliminando el HOL blocking entre streams que aquejaba a HTTP/2 sobre TCP.

**HTTP/3**, la versión más reciente del protocolo HTTP, adopta QUIC como su transporte subyacente en lugar de TCP, heredando directamente estas dos ventajas: conexión más rápida de establecer y ausencia de bloqueo de cabecera de línea entre recursos multiplexados, particularmente valioso en condiciones de red con pérdida de paquetes no trivial (redes móviles, Wi-Fi congestionado), donde HTTP/2 sobre TCP sufre más severamente el efecto cascada de un solo paquete perdido bloqueando toda la página.

## Ideas clave

- El three-way handshake de TCP (SYN, SYN-ACK, ACK) establece la conexión antes de cualquier dato de aplicación, consumiendo un RTT completo de latencia fija.
- El control de flujo protege al receptor mediante la ventana anunciada; el control de congestión protege a la red, con slow start exponencial y AIMD como base clásica, refinados por CUBIC y BBR.
- El HOL blocking de TCP retiene en el receptor todos los bytes posteriores a un segmento perdido, penalizando especialmente la multiplexación de streams de HTTP/2.
- UDP renuncia deliberadamente a fiabilidad, orden y control de congestión propio, adecuado para tiempo real (voz, video) y para protocolos que implementan su propia lógica a medida.
- QUIC, construido sobre UDP, combina handshake de transporte y criptográfico en un RTT (o cero) y multiplexa streams sin HOL blocking entre ellos, la base de HTTP/3.

## Para seguir

La siguiente lección, *SDN y virtualización de red*, cierra la categoría examinando cómo el plano de control se desacopla del plano de datos a escala de red completa, más allá del transporte extremo a extremo visto aquí.
