---
title: Conmutación y señalización
level: medio
summary: Circuitos frente a paquetes, la señalización SS7 de la PSTN, VoIP con SIP y las métricas de calidad que gobiernan la migración a redes all-IP.
tags: [conmutacion, ss7, voip, sip, qos]
minutes: 10
order: 5
---

## Objetivos

- Distinguir la conmutación de circuitos de la conmutación de paquetes y sus implicaciones para la voz.
- Describir la arquitectura de señalización SS7 de la red telefónica pública conmutada (PSTN).
- Explicar VoIP y el protocolo SIP como su mecanismo de señalización.
- Definir jitter, latencia y MOS como las métricas centrales de calidad de servicio (QoS) de voz.
- Explicar por qué y cómo la industria ha migrado hacia arquitecturas "all-IP".

## Conmutación de circuitos frente a conmutación de paquetes

La **conmutación de circuitos** establece, antes de que comience la comunicación, una ruta física o lógica dedicada de extremo a extremo, con un ancho de banda reservado y constante durante toda la duración de la llamada, independientemente de si hay datos que transmitir en cada instante (durante un silencio en una conversación, el circuito sigue reservado y ocioso). Es el paradigma histórico de la telefonía: cada llamada de voz ocupaba tradicionalmente un canal digital de 64 kbit/s (la tasa de la modulación PCM estándar, ver más abajo), multiplexado en el tiempo (TDM) junto con otros canales sobre el mismo enlace troncal. Su ventaja es una latencia y una calidad predecibles y constantes una vez establecido el circuito; su desventaja es la ineficiencia de reservar capacidad que a menudo queda sin usar.

La **conmutación de paquetes**, en cambio, divide la información en paquetes discretos, cada uno con su propia cabecera de direccionamiento, que se enrutan de forma independiente y comparten dinámicamente el enlace con el tráfico de otros usuarios: solo se consume ancho de banda cuando efectivamente hay datos que enviar, lo que multiplica la eficiencia estadística del enlace compartido (varios usuarios pueden compartir la misma capacidad física porque rara vez todos transmiten a máxima tasa simultáneamente), a costa de introducir **latencia variable** (jitter) y la posibilidad de pérdida de paquetes bajo congestión, ambos irrelevantes en un circuito dedicado tradicional. La migración de la telefonía, y de las telecomunicaciones en general, de circuitos a paquetes —el tema central de esta lección— es, en esencia, la historia de cómo la industria aprendió a domesticar esa variabilidad para ofrecer una calidad de voz aceptable sobre un medio fundamentalmente menos determinista.

## PSTN y señalización SS7

La **PSTN** (*Public Switched Telephone Network*, red telefónica pública conmutada) es la red de conmutación de circuitos clásica que interconecta los teléfonos del mundo. Su funcionamiento se divide conceptualmente en dos planos: el **plano de usuario** (la voz misma, digitalizada mediante PCM a 64 kbit/s según la ley µ o A, y transportada por los circuitos conmutados) y el **plano de señalización**, la infraestructura separada que gestiona el establecimiento, mantenimiento y liberación de las llamadas, así como servicios auxiliares (identificación de llamante, desvío de llamadas, portabilidad numérica).

**SS7** (*Signaling System No. 7*), desplegado desde los años 80, es el protocolo de señalización que hizo posible la PSTN moderna: en lugar de señalizar dentro del mismo canal de voz (señalización "en banda", vulnerable a fraude y limitada en funcionalidad), SS7 usa una **red de señalización separada** (fuera de banda), de modo que los conmutadores de una central telefónica se comunican entre sí mediante mensajes SS7 dedicados para negociar el establecimiento de una llamada —determinar si el destino existe, está libre, y por qué ruta encaminarla— *antes* de reservar cualquier circuito de voz. Esta separación es la que permite, por ejemplo, que una llamada internacional se enrute de forma óptima a través de múltiples operadores, que el identificador de llamante viaje de forma fiable, o que los servicios de red inteligente (números 800, portabilidad numérica) funcionen de forma transparente para el usuario. SS7 sigue operando hoy como la columna vertebral de señalización entre operadores de telefonía móvil y fija a nivel mundial, incluso a medida que el plano de voz subyacente migra hacia IP.

## VoIP y SIP

**VoIP** (*Voice over IP*) transporta la voz digitalizada como paquetes de datos sobre una red IP, típicamente comprimida con un códec de voz (G.711 sin compresión adicional a 64 kbit/s, o G.729/Opus con compresión, a tasas de 8–24 kbit/s o menos) y encapsulada en paquetes **RTP** (*Real-time Transport Protocol*) para el flujo de voz en sí. El establecimiento, modificación y terminación de la sesión de llamada —el equivalente funcional a lo que SS7 hace en la PSTN— lo gestiona el protocolo **SIP** (*Session Initiation Protocol*), un protocolo de texto plano inspirado deliberadamente en HTTP, con métodos como `INVITE` (iniciar una llamada), `ACK`, `BYE` (terminarla) y `REGISTER` (registrar la ubicación de un usuario), y códigos de respuesta análogos a los de HTTP (`180 Ringing`, `200 OK`, `486 Busy Here`). SIP permite negociar los parámetros de la sesión multimedia (códecs soportados, direcciones IP y puertos de los flujos RTP) mediante el protocolo **SDP** (*Session Description Protocol*) embebido en los mensajes SIP, y su diseño desacoplado de señalización (SIP) y medio (RTP) —análogo, de nuevo, a la separación de planos de SS7 y la PSTN— es lo que permite que servidores de señalización SIP centralicen el control de sesiones mientras el tráfico de voz real fluye por rutas potencialmente distintas, incluso directamente entre los dos terminales sin pasar por el servidor.

## Métricas de calidad de servicio: jitter, latencia y MOS

La conmutación de paquetes introduce tres desafíos característicos que la conmutación de circuitos, con su canal dedicado y constante, no sufre. La **latencia** (retardo de extremo a extremo) degrada la interactividad de la conversación por encima de ciertos umbrales: la UIT recomienda no superar 150 ms de latencia unidireccional para conversación bidireccional cómoda, y considera 400 ms el límite superior aceptable incluso en condiciones adversas (como un enlace satelital GEO, que por sí solo introduce cerca de 240–280 ms de latencia de ida y vuelta). El **jitter** es la variación en el tiempo de llegada de paquetes consecutivos: como la voz debe reproducirse a un ritmo constante, el jitter se compensa con un **buffer de jitter** (*jitter buffer*) en el receptor, que retiene brevemente los paquetes para reproducirlos a intervalos regulares, a costa de añadir esa retención como latencia adicional —un compromiso directo entre tolerar más jitter (buffer más grande, más latencia) o menos latencia (buffer más pequeño, más riesgo de que la variación exceda el buffer y provoque cortes audibles).

El **MOS** (*Mean Opinion Score*) es una escala subjetiva de 1 (pésimo) a 5 (excelente) que resume la calidad percibida de una llamada, obtenida originalmente mediante pruebas con oyentes humanos y hoy estimada algorítmicamente (por ejemplo, con el modelo E de la UIT, que combina latencia, jitter, pérdida de paquetes y códec empleado en una única puntuación predicha) para monitorear la calidad de redes VoIP en producción sin necesidad de paneles de oyentes. Un MOS de 4.0 o superior se considera "toll quality" (comparable a la telefonía fija tradicional); por debajo de 3.5 los usuarios empiezan a notar degradación perceptible.

## La migración hacia all-IP

Durante más de una década, los operadores de telecomunicaciones han migrado sus redes hacia arquitecturas **all-IP**, donde no solo los datos sino también la voz (mediante VoLTE en redes móviles, o VoIP corporativo y residencial) y en algunos casos incluso la señalización tradicional se transportan íntegramente sobre infraestructura IP, apagando progresivamente los conmutadores de circuitos TDM heredados. Las razones son fundamentalmente económicas y operativas: mantener dos redes paralelas (una de circuitos legacy y otra de paquetes moderna) duplica costos de infraestructura y de personal especializado; una red IP unificada permite convergencia de servicios (voz, video, datos sobre la misma infraestructura), aprovecha economías de escala del hardware de redes IP genérico frente al hardware propietario de conmutación de circuitos, y habilita servicios que la conmutación de circuitos no puede ofrecer nativamente (videollamada de alta definición, mensajería enriquecida). El reto técnico central de esta migración —y la razón por la que tomó tanto tiempo completarse con calidad aceptable— ha sido precisamente replicar, sobre una red de paquetes inherentemente menos determinista, la fiabilidad y la calidad de voz consistente que la conmutación de circuitos ofrecía de forma casi trivial por diseño.

## Ideas clave

- La conmutación de circuitos reserva capacidad dedicada y constante; la de paquetes comparte el enlace dinámicamente, ganando eficiencia a costa de latencia variable y jitter.
- SS7 señaliza fuera de banda en la PSTN, separando el establecimiento de llamada del canal de voz, y sigue siendo la columna vertebral de señalización entre operadores.
- SIP cumple el rol equivalente en VoIP, negociando sesiones con mensajes tipo HTTP mientras RTP transporta el audio; SDP describe los parámetros multimedia negociados.
- Latencia, jitter y MOS son las métricas centrales de calidad de voz sobre IP; el buffer de jitter compensa la variación de llegada a costa de latencia adicional.
- La migración all-IP unifica voz y datos sobre una única infraestructura de paquetes, motivada por costo y convergencia de servicios, pero exige replicar la fiabilidad determinista de la conmutación de circuitos.

## Para seguir

Esto cierra la categoría de Redes de Telecomunicaciones. La siguiente categoría de la biblioteca, *Redes de Datos*, retoma la conmutación de paquetes vista aquí para estudiar en profundidad los modelos de capas, Ethernet, IP y el transporte que sostienen toda comunicación de datos moderna, incluida la voz sobre IP recién estudiada.
