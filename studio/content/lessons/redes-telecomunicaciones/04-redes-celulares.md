---
title: "Redes celulares: de 1G a 5G"
level: medio
summary: El reuso de frecuencia y la arquitectura RAN/core organizan la evolución de 1G a 5G, con OFDMA, mmWave y MIMO masivo como hitos clave.
tags: [celular, 5g, ofdma, mimo-masivo, generaciones-moviles]
minutes: 10
order: 4
---

## Objetivos

- Explicar el concepto celular y el reuso de frecuencia como solución al problema de la capacidad de espectro limitado.
- Describir la arquitectura general de una red móvil dividida en RAN (acceso radio) y núcleo (core).
- Recorrer los hitos técnicos de cada generación: GSM, UMTS, LTE y 5G NR.
- Explicar OFDMA como técnica de acceso múltiple de LTE y 5G, y las numerologías de 5G NR.
- Explicar mmWave y MIMO masivo como las palancas técnicas centrales del salto a 5G.

## El concepto celular y el reuso de frecuencia

El espectro de radiofrecuencia asignado a un operador móvil es un recurso finito y escaso; si un único transmisor de gran potencia cubriera una ciudad entera, todos los usuarios de esa ciudad competirían por el mismo bloque de espectro. El **concepto celular**, propuesto en Bell Labs en los años 40 y desplegado comercialmente desde los 80, resuelve esto dividiendo el área de cobertura en **celdas** pequeñas, cada una servida por una estación base de potencia moderada, y **reutilizando** las mismas frecuencias en celdas suficientemente separadas entre sí para que la interferencia mutua sea tolerable. Un patrón de reuso típico agrupa celdas en *clusters* de $N$ celdas (comúnmente $N=7$), donde cada celda del cluster usa un subconjunto distinto de canales, y el patrón completo se repite en el cluster adyacente; cuanto menor el tamaño de celda, más clusters caben en la misma área geográfica y mayor es la capacidad total del sistema —el motivo estructural detrás de la tendencia histórica hacia celdas cada vez más pequeñas (macroceldas, microceldas y hoy femtoceldas y small cells en 5G) para sostener la demanda de tráfico creciente por unidad de área.

## Arquitectura RAN y núcleo (core)

Toda red celular se divide conceptualmente en dos partes. La **RAN** (*Radio Access Network*), o red de acceso radio, comprende las estaciones base (BTS en GSM, NodeB en UMTS, eNodeB en LTE, gNodeB en 5G NR) y todo el equipo de radiofrecuencia y antenas que gestiona el enlace inalámbrico directo con los dispositivos de usuario. El **core** (núcleo de red) es la parte fija, típicamente basada en conmutación de paquetes IP en las generaciones modernas, que gestiona la autenticación de suscriptores, el enrutamiento del tráfico hacia Internet o hacia otras redes, la movilidad entre estaciones base (*handover*), la facturación y las políticas de calidad de servicio. Esta separación RAN/core ha sido una constante arquitectónica a través de las generaciones, aunque su implementación concreta ha evolucionado radicalmente: de un core basado en conmutación de circuitos en GSM (heredado directamente de la telefonía fija), a un core totalmente basado en paquetes IP en LTE (el *Evolved Packet Core*, EPC), hasta el core de 5G, diseñado desde el inicio con virtualización de funciones de red y una arquitectura de microservicios expuesta mediante APIs.

## Evolución generacional

**1G** (analógica, años 80) transmitía voz mediante FM analógica pura, sin cifrado ni capacidad de datos, con capacidad de espectro muy limitada. **2G/GSM** (años 90) digitalizó la voz usando TDMA (acceso múltiple por división de tiempo) sobre portadoras de 200 kHz, introdujo el cifrado y la itinerancia internacional estandarizada, y añadió datos de baja velocidad (GPRS, EDGE, hasta unas pocas centenas de kbit/s). **3G/UMTS** introdujo **CDMA de banda ancha** (W-CDMA), donde todos los usuarios comparten simultáneamente el mismo bloque de espectro (típicamente 5 MHz) distinguiéndose por códigos ortogonales únicos en vez de por tiempo o frecuencia, lo que mejoró sustancialmente la capacidad y permitió tasas de datos de cientos de kbit/s a pocos Mbit/s, habilitando el primer internet móvil de uso masivo.

**LTE** (4G, desde 2009) representó un salto arquitectónico: abandonó CDMA en favor de **OFDMA** (ver sección siguiente) para el enlace descendente y SC-FDMA para el ascendente, adoptó un core totalmente basado en IP (EPC, sin conmutación de circuitos ni siquiera para voz, que se transporta mediante VoLTE), y alcanzó tasas pico de cientos de Mbit/s a más de 1 Gbit/s en sus variantes avanzadas (LTE-Advanced, con agregación de portadoras). **5G NR** (*New Radio*, desde 2019) introduce numerologías OFDM flexibles, acceso a bandas de ondas milimétricas (mmWave) además del espectro sub-6 GHz tradicional, MIMO masivo, y un diseño explícito para tres perfiles de servicio distintos: **eMBB** (banda ancha móvil mejorada, para throughput masivo), **URLLC** (comunicación ultra confiable de baja latencia, para aplicaciones críticas como control industrial o vehículos autónomos) y **mMTC** (comunicación masiva tipo máquina, para IoT de altísima densidad de dispositivos con tráfico mínimo por dispositivo).

## OFDMA y las numerologías de 5G NR

**OFDMA** (*Orthogonal Frequency-Division Multiple Access*) divide el ancho de banda disponible en un gran número de subportadoras estrechas, mutuamente ortogonales (de modo que no interfieren entre sí pese a solaparse parcialmente en frecuencia), y asigna dinámicamente subconjuntos de esas subportadoras a distintos usuarios en distintos instantes de tiempo, formando una rejilla de recursos tiempo-frecuencia. Esta granularidad fina permite al planificador (*scheduler*) de la estación base asignar a cada usuario, en cada instante, precisamente los recursos que su condición de canal instantánea puede aprovechar mejor (combinándose naturalmente con la modulación adaptativa MODCOD vista en la lección anterior), y hace al sistema robusto frente al desvanecimiento selectivo en frecuencia, porque un desvanecimiento profundo en una porción del espectro solo afecta a las subportadoras de esa porción, no a la totalidad de la señal.

5G NR generaliza el OFDM de LTE (que usaba un único espaciado fijo de subportadora de 15 kHz) mediante **numerologías** múltiples: el espaciado entre subportadoras puede ser 15, 30, 60 o 120 kHz (y hasta 240 kHz para ciertos canales de control), donde un espaciado mayor acorta proporcionalmente la duración del símbolo OFDM, reduciendo la latencia por símbolo a costa de mayor sensibilidad al desvanecimiento por dispersión temporal y de exigir sincronización más precisa. Bandas de frecuencia bajas y medias (sub-6 GHz, *FR1*) suelen usar numerologías de 15–30 kHz, apropiadas para coberturas amplias; las bandas mmWave (*FR2*, por encima de 24 GHz) usan numerologías de 60–120 kHz, donde los símbolos más cortos ayudan a combatir el mayor Doppler y la mayor dispersión temporal típicos de esas frecuencias.

## mmWave y MIMO masivo

Las **ondas milimétricas** (mmWave, aproximadamente 24–100 GHz en el contexto 5G) ofrecen bloques de espectro contiguo enormemente más anchos que las bandas celulares tradicionales (cientos de MHz a varios GHz, frente a decenas de MHz típicos de sub-6 GHz), lo que por Shannon se traduce directamente en capacidades potenciales mucho mayores. Su costo es una propagación mucho más desfavorable: mayor pérdida de espacio libre, penetración muy pobre a través de paredes y obstáculos, y atenuación significativa por lluvia y hasta por el follaje de árboles, lo que restringe su alcance práctico a celdas pequeñas de unos pocos cientos de metros, típicamente en escenarios densos urbanos o de estadio.

El **MIMO masivo** (*massive Multiple-Input Multiple-Output*) equipa la estación base con decenas o cientos de elementos de antena (frente a los 2–4 típicos de 4G), lo que permite formar haces de radiofrecuencia muy estrechos y dirigidos (*beamforming*) hacia cada usuario individual, concentrando la energía radiada exactamente donde se necesita en vez de irradiarla omnidireccionalmente, y permite además el **multiplexado espacial multiusuario** (MU-MIMO): servir a múltiples usuarios simultáneamente en el mismo bloque de tiempo-frecuencia, distinguiéndolos únicamente por la geometría espacial de sus haces respectivos. Esta técnica es lo que hace viable, en la práctica, tanto compensar la propagación desfavorable de mmWave mediante ganancia de haz concentrada, como multiplicar la capacidad efectiva de una celda sub-6 GHz sin requerir más espectro.

## Ideas clave

- El concepto celular reutiliza el mismo espectro en celdas suficientemente separadas, y celdas más pequeñas permiten mayor capacidad total por unidad de área.
- La arquitectura RAN/core se mantiene a través de las generaciones, aunque el core ha migrado de conmutación de circuitos (GSM) a IP puro (LTE, 5G).
- La evolución 1G→5G combina saltos en la técnica de acceso (FM→TDMA→CDMA→OFDMA) con la migración completa del core a paquetes IP.
- OFDMA divide el espectro en subportadoras ortogonales asignables dinámicamente; las numerologías de 5G NR ajustan el espaciado de subportadora al escenario de despliegue.
- mmWave ofrece enorme ancho de banda contiguo a costa de propagación desfavorable; el MIMO masivo con beamforming es la técnica que la hace viable y que además multiplica capacidad mediante MU-MIMO.

## Para seguir

La siguiente lección, *Conmutación y señalización*, examina cómo el tráfico de voz y datos generado en esta capa de acceso radio se conmuta y enruta a través de la red, desde la telefonía de circuitos clásica hasta la señalización moderna de VoIP.
