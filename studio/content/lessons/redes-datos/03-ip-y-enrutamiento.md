---
title: IP y enrutamiento
level: medio
summary: IPv4/IPv6, subneteo CIDR, la coincidencia de prefijo más largo, los protocolos IGP y BGP, y el porqué y los problemas de NAT.
tags: [ip, cidr, bgp, ospf, nat]
minutes: 10
order: 3
---

## Objetivos

- Comparar IPv4 e IPv6 y explicar la motivación del segundo.
- Aplicar subneteo CIDR a ejemplos concretos de división de una red.
- Explicar la coincidencia de prefijo más largo (*longest prefix match*) en una tabla de rutas.
- Distinguir un IGP (con OSPF como ejemplo) de BGP y su rol respectivo en el enrutamiento de Internet.
- Explicar NAT y los problemas estructurales que introduce.

## IPv4 e IPv6

**IPv4**, definida en 1981, usa direcciones de 32 bits, escritas convencionalmente como cuatro octetos decimales separados por puntos (por ejemplo, `192.168.1.1`), lo que da un espacio teórico de $2^{32}\approx 4.3$ mil millones de direcciones. Ese espacio, que parecía inagotable en los años 80, se agotó efectivamente a nivel de asignación regional durante la década de 2010 (IANA distribuyó sus últimos bloques principales en 2011), presionado por el crecimiento explosivo de dispositivos conectados a Internet en todo el mundo, muy por encima de cualquier estimación original.

**IPv6**, estandarizada desde 1998 y en despliegue creciente desde entonces, usa direcciones de 128 bits, escritas como ocho grupos hexadecimales de 16 bits separados por dos puntos (por ejemplo, `2001:0db8:85a3:0000:0000:8a2e:0370:7334`, comprimible omitiendo ceros iniciales y colapsando un grupo de ceros consecutivos con `::`), un espacio de $2^{128}$ direcciones tan vasto (más de $3\times10^{38}$) que elimina de raíz el problema de agotamiento para cualquier escala previsible de dispositivos conectados, incluyendo el crecimiento masivo de IoT. Además de resolver el espacio de direcciones, IPv6 simplifica la cabecera del paquete (eliminando campos de uso poco frecuente en IPv4 y moviendo funciones opcionales a cabeceras de extensión encadenadas), incorpora la autoconfiguración de direcciones sin necesidad de DHCP (SLAAC), y elimina la necesidad estructural de NAT que IPv4 arrastra por su escasez de direcciones —aunque la adopción de IPv6 ha sido considerablemente más lenta que su propia especificación, precisamente porque NAT (ver más abajo) extendió la vida útil práctica de IPv4 mucho más de lo previsto originalmente.

## Subneteo CIDR

El **CIDR** (*Classless Inter-Domain Routing*), introducido en 1993, reemplazó el esquema original de clases de dirección fijas (A, B, C) por una notación de **longitud de prefijo variable**: una dirección IP se acompaña de una barra y un número que indica cuántos bits, contados desde el más significativo, identifican la parte de **red** (el resto identifica el **host** dentro de esa red). Así, `192.168.1.0/24` denota una red cuyos primeros 24 bits (los tres primeros octetos) son fijos, dejando 8 bits ($2^8=256$ direcciones, de las cuales 254 son asignables a hosts, descontando la dirección de red y la de difusión) para hosts individuales.

El subneteo consiste en dividir un bloque CIDR más grande en bloques más pequeños ajustando la longitud de prefijo. Por ejemplo, partiendo de `10.0.0.0/16` (65 536 direcciones), se puede dividir en cuatro subredes `/18` de 16 384 direcciones cada una (`10.0.0.0/18`, `10.0.64.0/18`, `10.0.128.0/18`, `10.0.192.0/18`), o en 256 subredes `/24` de 256 direcciones cada una. La **máscara de subred** equivalente a un prefijo `/24` es `255.255.255.0`; a un `/26` (64 direcciones, útil para segmentos pequeños de oficina) es `255.255.255.192`. La regla general es que un prefijo `/n` deja $32-n$ bits para hosts, produciendo $2^{32-n}$ direcciones totales en el bloque (de las cuales típicamente se descuentan 2 para red y difusión en subredes de host).

## Longest Prefix Match

Cuando un router recibe un paquete, consulta su **tabla de rutas** para decidir el siguiente salto hacia el destino. Esa tabla contiene, típicamente, múltiples entradas cuyo prefijo coincide parcialmente con la dirección de destino —por ejemplo, una ruta por defecto `0.0.0.0/0` (que coincide con *cualquier* dirección), una ruta más específica `10.0.0.0/8`, y una aún más específica `10.0.1.0/24`—, y la regla que resuelve la ambigüedad es la **coincidencia de prefijo más largo** (*longest prefix match*): el router siempre elige, entre todas las entradas cuyo prefijo coincide con la dirección de destino, la que tiene el prefijo **más específico** (el número mayor tras la barra), no la primera que encuentre ni la de menor costo administrativo. Así, un paquete destinado a `10.0.1.5` se enruta según la entrada `10.0.1.0/24` si existe, aunque también coincidan `10.0.0.0/8` y `0.0.0.0/0`, precisamente porque `/24` es más específico que `/8`, que a su vez es más específico que `/0`. Este mecanismo es lo que permite anunciar una ruta agregada amplia por defecto (por ejemplo, hacia todo un bloque de un proveedor) mientras se anuncian excepciones más específicas para subredes concretas que requieren un tratamiento distinto, sin ambigüedad en la decisión de reenvío.

## IGP frente a BGP

Un **IGP** (*Interior Gateway Protocol*) enruta el tráfico *dentro* de un único sistema autónomo (AS) —una red bajo una única administración técnica, típicamente la de un operador o una empresa grande—, optimizando rutas según métricas técnicas internas (ancho de banda, retardo, número de saltos). **OSPF** (*Open Shortest Path First*) es el IGP más extendido: cada router construye, mediante el intercambio de anuncios de estado de enlace (*Link-State Advertisements*) con todos sus routers vecinos dentro del área OSPF, un mapa completo e idéntico de la topología de la red, sobre el cual ejecuta localmente el **algoritmo de Dijkstra** para calcular la ruta de menor costo hacia cada destino conocido; como todos los routers OSPF comparten la misma vista topológica completa, el protocolo converge rápidamente tras un cambio de topología (un enlace que cae, por ejemplo) y evita bucles de enrutamiento por construcción.

**BGP** (*Border Gateway Protocol*), en cambio, es el único protocolo de enrutamiento que opera *entre* sistemas autónomos distintos, y es, en un sentido literal, el protocolo que mantiene unida a Internet como una red de redes: cada sistema autónomo anuncia a sus vecinos BGP los bloques de direcciones que puede alcanzar (los suyos propios y, transitivamente, los que ha aprendido de otros), junto con la secuencia completa de sistemas autónomos atravesados (el **AS-path**), y cada AS elige rutas no solo por métricas técnicas sino sobre todo por **políticas** administrativas y comerciales (acuerdos de peering, relaciones cliente-proveedor, preferencias de tránsito) que BGP expone explícitamente como atributos configurables de la ruta. Esta orientación a políticas, más que a optimalidad técnica pura, es la diferencia estructural fundamental frente a un IGP como OSPF: BGP no busca necesariamente la ruta "más corta" en ningún sentido técnico, sino la ruta que las políticas comerciales de cada operador prefieren usar.

## NAT y sus problemas

La **NAT** (*Network Address Translation*) traduce direcciones IP privadas (de los rangos reservados `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, no enrutables en Internet pública) a una o pocas direcciones IP públicas al cruzar la frontera de una red local hacia Internet, típicamente multiplexando muchas conexiones internas sobre una única IP pública distinguiéndolas por número de puerto (**PAT**, *Port Address Translation*, la variante más común en routers domésticos). NAT surgió como una solución pragmática y muy exitosa a la escasez de direcciones IPv4, permitiendo que redes enteras compartan una única dirección pública.

Sus problemas, sin embargo, son estructurales: NAT rompe el principio de **conectividad de extremo a extremo** en el que se diseñó originalmente Internet, porque un host detrás de NAT no tiene una dirección alcanzable directamente desde fuera sin configuración adicional (redirección de puertos), lo que complica protocolos que requieren conexiones entrantes no solicitadas (VoIP, videollamada peer-to-peer, servidores domésticos) y exige técnicas de travesía de NAT (STUN, TURN, ICE) añadidas específicamente para sortear el problema. NAT también complica el diagnóstico de red (una misma IP pública puede corresponder a decenas de dispositivos internos distintos, y su estado de traducción es efímero y depende del router específico) y, al requerir que el router mantenga estado por cada conexión traducida, introduce un límite práctico de conexiones simultáneas y un punto adicional de fallo. La migración a IPv6, con su espacio de direcciones ilimitado en la práctica, elimina la necesidad estructural de NAT (cada dispositivo puede tener su propia dirección pública), aunque muchas redes IPv6 mantienen cortafuegos con política por defecto restrictiva por razones de seguridad, incluso sin depender ya de NAT para ello.

## Ideas clave

- IPv6 resuelve el agotamiento de direcciones de IPv4 (32 bits) con un espacio de 128 bits, además de simplificar cabeceras y eliminar la necesidad estructural de NAT.
- CIDR reemplaza las clases fijas por prefijos de longitud variable (`/n`), permitiendo subneteo flexible ajustado al tamaño real de cada segmento de red.
- La coincidencia de prefijo más largo resuelve la elección entre rutas superpuestas en la tabla de rutas, siempre prefiriendo la entrada más específica.
- OSPF (IGP) construye un mapa topológico completo dentro de un AS y aplica Dijkstra; BGP enruta entre sistemas autónomos guiado por políticas comerciales, no solo por métricas técnicas.
- NAT resolvió pragmáticamente la escasez de IPv4 pero rompe la conectividad de extremo a extremo, complicando protocolos con conexiones entrantes y el diagnóstico de red.

## Para seguir

La siguiente lección, *Transporte: TCP, UDP y QUIC*, sube a la capa de transporte para examinar cómo se establece, controla y adapta la entrega de datos de extremo a extremo sobre las rutas IP calculadas en esta lección.
