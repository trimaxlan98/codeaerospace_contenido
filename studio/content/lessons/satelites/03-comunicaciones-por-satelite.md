---
title: Comunicaciones por satélite
level: medio
summary: Bandas de frecuencia, transpondedores, esquemas de acceso múltiple, la ecuación de enlace y las tecnologías VSAT y HTS.
tags: [comunicaciones, bandas, transpondedores, ecuacion-enlace, vsat]
minutes: 9
order: 3
---

## Objetivos

- Ubicar las bandas de frecuencia satelital (L, S, C, X, Ku, Ka) y sus compromisos de propagación.
- Entender la función de un transpondedor y los esquemas de acceso múltiple FDMA y TDMA.
- Aplicar la ecuación de enlace para estimar la calidad de una comunicación satelital.
- Diferenciar terminales VSAT tradicionales de los satélites de alto rendimiento (HTS) con beam-hopping.

## Bandas de frecuencia

Las comunicaciones satelitales se organizan en bandas normalizadas por la UIT, cada una con un compromiso distinto entre ancho de banda disponible, sensibilidad a la lluvia y tamaño de antena requerido:

| Banda | Rango de frecuencia (downlink típico) | Características |
|---|---|---|
| L | 1–2 GHz | Muy robusta ante lluvia; usada en GPS, telefonía satelital (Iridium, Inmarsat) |
| S | 2–4 GHz | Robusta; TT&C, algunos sistemas móviles |
| C | 4–8 GHz (downlink ~3.7-4.2 GHz) | Muy resistente a la lluvia; enlaces troncales, zonas tropicales |
| X | 8–12 GHz | Uso principalmente militar y gubernamental |
| Ku | 12–18 GHz (downlink ~10.7-12.75 GHz) | TV directa al hogar (DTH), VSAT; antenas pequeñas, más sensible a lluvia |
| Ka | 26.5–40 GHz (downlink ~17.7-21.2 GHz) | Gran ancho de banda, HTS, muy sensible a lluvia (atenuación por precipitación) |

La regla general es clara: a mayor frecuencia, mayor ancho de banda disponible (y por tanto mayor capacidad de datos) y menor tamaño de antena requerido para una ganancia dada, pero también mayor atenuación por lluvia (*rain fade*). La banda Ka puede sufrir desvanecimientos de más de 10-20 dB durante tormentas intensas, lo que obliga a los sistemas modernos a implementar márgenes de enlace generosos y técnicas de compensación adaptativa (ACM, *Adaptive Coding and Modulation*) que reducen dinámicamente la tasa de datos para mantener el enlace durante mal tiempo.

## Transpondedores y acceso múltiple

Un **transpondedor** es el subsistema de carga útil que recibe la señal en la frecuencia de subida (uplink), la amplifica, la traslada en frecuencia (típicamente unos cientos de MHz o unos pocos GHz por debajo, para evitar interferencia entre el uplink y el downlink) y la retransmite hacia la Tierra. Un satélite GEO de comunicaciones típico porta entre 24 y 48 transpondedores, cada uno con un ancho de banda de 36 o 72 MHz.

Cuando múltiples usuarios comparten el mismo transpondedor, se necesita un esquema de **acceso múltiple**:

- **FDMA (Frequency Division Multiple Access)**: cada usuario recibe una subbanda de frecuencia exclusiva dentro del transpondedor, transmitiendo de forma continua. Simple de implementar, pero requiere que el amplificador de tubo de ondas viajeras (TWTA) del transpondedor opere con back-off (reducción de potencia respecto a saturación) para evitar productos de intermodulación entre portadoras, sacrificando eficiencia de potencia.
- **TDMA (Time Division Multiple Access)**: todos los usuarios comparten la misma frecuencia pero transmiten en ráfagas ("bursts") en intervalos de tiempo asignados sincronizadamente, de modo que solo una señal ocupa el transpondedor en cada instante. Permite operar el amplificador cerca de saturación (máxima eficiencia), a costa de mayor complejidad de sincronización temporal entre terminales.

Los sistemas VSAT y los HTS modernos suelen combinar ambos esquemas (por ejemplo, FDMA entre haces o portadoras y TDMA dentro de cada portadora) según el patrón de tráfico.

## La ecuación de enlace

El parámetro fundamental para evaluar la calidad de un enlace de comunicaciones satelital es la relación densidad de portadora a densidad de ruido, $C/N_0$, expresada en dB-Hz:

$$\frac{C}{N_0} = \text{EIRP} - L_p + \frac{G}{T} - k$$

donde:

- **EIRP** (*Equivalent Isotropically Radiated Power*, en dBW) es la potencia efectiva irradiada por la antena transmisora, combinando la potencia del amplificador y la ganancia de la antena.
- $L_p$ es la pérdida de propagación en espacio libre (en dB), dada por $L_p = 20\log_{10}\left(\frac{4\pi d}{\lambda}\right)$, que crece con el cuadrado de la distancia $d$ y es inversamente proporcional al cuadrado de la longitud de onda $\lambda$ (es decir, crece con la frecuencia); para un enlace GEO típico en banda Ku, $L_p$ ronda los 205-206 dB.
- $G/T$ (en dB/K) es la **figura de mérito** del receptor: la ganancia de su antena dividida entre la temperatura de ruido del sistema (que incluye ruido térmico, ruido de la electrónica y ruido captado del entorno), y es el parámetro clave que determina la sensibilidad de una estación terrena o de un satélite receptor.
- $k$ es la constante de Boltzmann (-228.6 dBW/K/Hz), que aparece como término aditivo negativo por convención logarítmica.

El $C/N_0$ resultante se compara contra el requerido por el esquema de modulación y codificación elegido (que exige un $E_b/N_0$ mínimo para una tasa de error de bit objetivo) para determinar el margen de enlace disponible. Este margen es el "colchón" que absorbe degradaciones como la lluvia, apuntamiento imperfecto o envejecimiento del hardware.

## VSAT

Los terminales **VSAT** (*Very Small Aperture Terminal*), con antenas típicamente de 0.75 a 2.4 metros de diámetro, popularizaron el acceso satelital para redes corporativas, cajeros automáticos remotos, estaciones meteorológicas y conectividad rural desde los años 80. Operan generalmente vía un satélite GEO, con arquitectura en estrella (todos los terminales remotos se comunican con un hub central) o, en sistemas más modernos, en malla (comunicación directa terminal-a-terminal a través del satélite). Su ancho de banda por terminal es modesto (desde cientos de kbps hasta unas pocas decenas de Mbps) comparado con los estándares actuales de banda ancha terrestre.

## HTS y beam-hopping

Los satélites de alto rendimiento (**HTS**, *High Throughput Satellites*) representan la evolución moderna de la capacidad satelital: en vez de unos pocos haces amplios que cubren continentes enteros, un HTS genera decenas o cientos de **haces puntuales** (*spot beams*) estrechos, cada uno cubriendo un área geográfica pequeña con alta densidad de potencia, y reutilizando las mismas frecuencias en haces suficientemente separados geográficamente (reúso de frecuencia espacial). Esto puede multiplicar la capacidad total del satélite por un factor de 20 a 100 respecto a un satélite de haz amplio convencional con el mismo espectro asignado.

El **beam-hopping** lleva esta idea un paso más allá: en vez de iluminar todos los haces de forma simultánea y continua, el satélite conmuta electrónicamente la potencia y el ancho de banda disponibles entre haces en una secuencia temporal rápida (microsegundos a milisegundos por salto), dedicando recursos dinámicamente a donde hay más demanda de tráfico en cada instante, en vez de repartir capacidad fija entre regiones que pueden tener demanda muy desigual (por ejemplo, una ciudad densa frente a una zona rural dentro de la misma huella). Esta flexibilidad, gestionada por un procesador digital de a bordo, es una de las características distintivas de la generación más reciente de satélites de comunicaciones (como los de la serie Eutelsat Quantum o los HTS de nueva generación de SES y Hughes).

## Ideas clave

- La elección de banda es un compromiso entre ancho de banda disponible, tamaño de antena y sensibilidad a la lluvia: L/C son robustas pero limitadas; Ku/Ka ofrecen capacidad a costa de rain fade.
- FDMA reparte frecuencia entre usuarios (simple, menos eficiente en potencia); TDMA reparte tiempo (más eficiente, más complejo de sincronizar).
- La ecuación de enlace $C/N_0 = \text{EIRP} - L_p + G/T - k$ resume en cuatro términos toda la física de un enlace satelital.
- $G/T$ es la figura de mérito que caracteriza la sensibilidad de un receptor, combinando ganancia de antena y temperatura de ruido del sistema.
- Los HTS con beam-hopping multiplican la capacidad efectiva de un satélite reutilizando frecuencias entre haces puntuales y asignando recursos dinámicamente según demanda.

## Para seguir

La siguiente lección, *Megaconstelaciones LEO*, aplica estos conceptos —bandas, enlaces, capacidad— al caso de sistemas con miles de satélites en órbita baja, incluyendo los enlaces inter-satelitales que no existían en el modelo GEO clásico descrito aquí.
