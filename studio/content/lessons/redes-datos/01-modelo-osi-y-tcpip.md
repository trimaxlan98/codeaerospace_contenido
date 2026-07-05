---
title: Modelos OSI y TCP/IP
level: intro
summary: Las siete capas OSI y las cuatro de TCP/IP organizan la comunicación de datos en unidades encapsuladas, con virtudes y límites prácticos distintos.
tags: [osi, tcpip, encapsulacion, pdu, capas]
minutes: 8
order: 1
---

## Objetivos

- Enumerar las siete capas del modelo OSI y describir la función de cada una con un ejemplo concreto.
- Explicar la encapsulación y la unidad de datos de protocolo (PDU) característica de cada capa.
- Mapear las capas OSI sobre las cuatro capas del modelo TCP/IP realmente implementado en Internet.
- Evaluar críticamente las limitaciones prácticas de ambos modelos frente a los protocolos reales.

## Las siete capas del modelo OSI

El modelo **OSI** (*Open Systems Interconnection*), publicado por la ISO en 1984, organiza la comunicación de datos en siete capas apiladas, cada una ofreciendo servicios a la capa inmediatamente superior y consumiendo servicios de la inmediatamente inferior, sin que ninguna capa necesite conocer los detalles internos de las demás. De abajo hacia arriba:

**Capa 1 — Física**: transmite bits crudos como señales físicas (tensión eléctrica, luz, radiofrecuencia) sobre el medio; especifica conectores, niveles de voltaje, y la codificación de línea. Es el objeto de estudio de los medios de transmisión vistos en la categoría anterior.

**Capa 2 — Enlace de datos**: organiza los bits en **tramas** (*frames*), añade direccionamiento local (direcciones MAC), detecta (y a veces corrige) errores de transmisión mediante sumas de verificación, y controla el acceso al medio compartido. Ethernet y Wi-Fi operan en esta capa; se estudia en detalle en la siguiente lección.

**Capa 3 — Red**: enruta **paquetes** entre redes distintas mediante direccionamiento lógico jerárquico (direcciones IP) y algoritmos de enrutamiento que determinan el siguiente salto hacia el destino. IP es el protocolo dominante de esta capa.

**Capa 4 — Transporte**: entrega **segmentos** (TCP) o **datagramas** (UDP) de extremo a extremo entre procesos concretos (identificados por puertos), gestionando opcionalmente fiabilidad, orden de entrega y control de congestión.

**Capa 5 — Sesión**: establece, coordina y termina sesiones de comunicación entre aplicaciones, gestionando aspectos como puntos de sincronización para reanudar transferencias interrumpidas.

**Capa 6 — Presentación**: se encarga del formato, la codificación de caracteres, la compresión y el cifrado de los datos, de modo que la capa de aplicación reciba la información en un formato que puede interpretar directamente.

**Capa 7 — Aplicación**: la más cercana al usuario, donde residen los protocolos que las aplicaciones usan directamente: HTTP, DNS, SMTP, FTP.

## Encapsulación y PDU por capa

Cada capa del modelo añade su propia cabecera (y, ocasionalmente, un remolque o *trailer*) a los datos que recibe de la capa superior, un proceso llamado **encapsulación**, sin modificar el contenido que ya traía. La unidad resultante en cada capa tiene un nombre específico —su **PDU** (*Protocol Data Unit*)—: en la capa de transporte se llama **segmento** (TCP) o **datagrama** (UDP); en la capa de red, **paquete**; en la capa de enlace, **trama**; y en la capa física, simplemente **bits**. Así, un mensaje de aplicación (por ejemplo, una petición HTTP) se convierte, al descender por la pila del emisor, en un segmento TCP (con cabecera de puertos y control de flujo), luego en un paquete IP (con cabecera de direcciones IP origen y destino), luego en una trama Ethernet (con cabecera de direcciones MAC), y finalmente en una secuencia de bits físicos sobre el cable o el aire. En el receptor, el proceso se invierte exactamente: cada capa retira su propia cabecera (**desencapsulación**) y entrega el contenido restante a la capa superior correspondiente, hasta reconstruir el mensaje de aplicación original. Este mecanismo es lo que permite que cada capa opere con total independencia de las demás: un switch de capa 2 solo necesita leer la cabecera de trama Ethernet, sin nunca inspeccionar ni entender el contenido IP, TCP o de aplicación que transporta encapsulado en su interior.

## Mapeo OSI-TCP/IP

El modelo **TCP/IP** (también llamado modelo DoD o modelo de Internet), descrito formalmente en el RFC 1122, es el modelo *realmente implementado* por Internet, y precede históricamente al propio OSI. Define típicamente cuatro capas: **acceso a la red** (que combina las capas física y de enlace de OSI en una sola), **internet** (equivalente a la capa de red de OSI, dominada por IP), **transporte** (equivalente directo a la capa 4 de OSI), y **aplicación** (que fusiona en una sola capa las capas de sesión, presentación y aplicación de OSI, delegando en cada protocolo concreto —HTTP, TLS, DNS— la responsabilidad de resolver, si la necesita, aspectos de sesión o presentación).

| Capa OSI | Capa TCP/IP equivalente | Protocolos de ejemplo |
|---|---|---|
| 7. Aplicación | Aplicación | HTTP, DNS, SMTP |
| 6. Presentación | Aplicación | TLS (cifrado), codificación de caracteres |
| 5. Sesión | Aplicación | Cookies de sesión, RPC |
| 4. Transporte | Transporte | TCP, UDP |
| 3. Red | Internet | IP, ICMP |
| 2. Enlace de datos | Acceso a la red | Ethernet, Wi-Fi (802.11) |
| 1. Física | Acceso a la red | Cableado, radiofrecuencia |

## Crítica práctica del modelo OSI

El modelo OSI es, ante todo, un modelo **de referencia conceptual**, no una especificación de protocolos reales: ningún conjunto de protocolos ampliamente desplegado implementa las siete capas de forma tan estrictamente separada como el modelo sugiere. TLS, por ejemplo, se suele describir como "capa de presentación" por su rol de cifrado, pero en la práctica opera técnicamente sobre TCP como un protocolo de transporte más, no como una capa distinta y universal por debajo de toda la capa de aplicación. Muchos protocolos de aplicación reales fusionan responsabilidades de sesión y presentación directamente en su propio diseño (HTTP/2 y HTTP/3, por ejemplo, gestionan su propia multiplexación de streams, un aspecto que en el modelo puro correspondería a la capa de sesión), sin un protocolo de sesión genérico y separado interpuesto. La utilidad perdurable del modelo OSI no es, por tanto, describir con precisión los protocolos de Internet, sino ofrecer un **vocabulario común y una forma de razonar** sobre dónde reside cada responsabilidad de una red —qué capa hace direccionamiento local frente a global, qué capa gestiona fiabilidad, qué capa es responsabilidad de la aplicación— que resulta indispensable para diagnosticar problemas de red metódicamente (determinar, por ejemplo, si un fallo de conectividad es un problema de capa 1 físico, de capa 3 de enrutamiento, o de capa 7 de la propia aplicación) incluso cuando ningún sistema real respeta sus fronteras al pie de la letra.

## Ideas clave

- OSI define siete capas conceptuales, de física a aplicación, cada una con una responsabilidad específica y bien delimitada.
- La encapsulación añade una cabecera por capa al descender la pila; cada capa produce su propia PDU (bits, trama, paquete, segmento).
- TCP/IP, el modelo realmente implementado en Internet, fusiona OSI en cuatro capas, combinando física+enlace en "acceso a la red" y sesión+presentación+aplicación en "aplicación".
- OSI es un modelo de referencia útil para razonar sobre responsabilidades de red, aunque ningún protocolo real respeta sus siete fronteras con precisión estricta.
- El valor práctico perdurable de ambos modelos es diagnóstico: ubicar en qué capa reside un fallo de red concreto.

## Para seguir

La siguiente lección, *Ethernet y conmutación LAN*, profundiza en la capa de enlace de datos: tramas, direccionamiento MAC, switches y VLAN, la base de toda red local moderna.
