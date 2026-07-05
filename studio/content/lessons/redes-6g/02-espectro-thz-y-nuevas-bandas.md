---
title: "Espectro: sub-THz y nuevas bandas"
level: medio
summary: Las bandas candidatas de 6G, del rango centimétrico 7-15 GHz al sub-THz de 100-300 GHz, con su física de propagación, absorción molecular y retos de RF.
tags: [espectro, sub-thz, fr3, propagacion, fotonica]
minutes: 11
order: 2
---

## Objetivos

- Mapear las bandas candidatas de 6G y el papel esperado de cada rango.
- Explicar por qué la banda centimétrica de 7–15 GHz (FR3) es la favorita para la capacidad de área en 6G.
- Cuantificar la propagación en sub-THz: pérdida de espacio libre, absorción molecular y bloqueo.
- Describir los retos de implementación de RF en sub-THz: amplificadores, ruido de fase, ADCs y arreglos de antenas.
- Explicar el papel de la fotónica integrada en la generación y el procesamiento de señales sub-THz.

## El mapa de bandas de 6G

Cada generación celular se expandió hacia frecuencias más altas en busca de ancho de banda: 4G vivió por debajo de 3 GHz, 5G añadió la banda media (FR1, hasta 7.125 GHz) y las milimétricas (FR2, 24–71 GHz). Para 6G, el espectro se organiza en tres capas con papeles distintos:

| Rango | Nombre | Papel en 6G | Ancho de banda típico |
|-------|--------|-------------|----------------------|
| < 1 GHz | Banda baja | Cobertura amplia e interiores profundos, IoT | 5–20 MHz |
| 1–7 GHz | Banda media (FR1) | Capa de capacidad actual (3.5 GHz) | 50–100 MHz |
| **7–15 (24) GHz** | **FR3 / centimétrica** | **Nueva capa de capacidad de 6G** | 200–400+ MHz |
| 24–71 GHz | FR2 / mmWave | Puntos calientes, backhaul, recintos | 400 MHz–2 GHz |
| **92–300 GHz** | **Sub-THz (W, D, G)** | **Enlaces cortos de tasa extrema, fronthaul, ISAC fino** | 2–20+ GHz |
| 0.3–3 THz | THz "verdadero" | Investigación; sensado/espectroscopía | >10 GHz |

La conclusión estratégica sorprende a quien espera que 6G sea "la generación terahertz": el grueso de la capacidad comercial de 6G se jugará en **FR3 (7–15 GHz)**, mientras el sub-THz aporta capacidades de nicho. La WRC-23 ya identificó porciones del rango (p. ej. 7.125–8.4 GHz en varias regiones) para estudio hacia IMT, y la WRC-27 decidirá atribuciones clave.

## Por qué FR3 es la banda favorita

FR3 ofrece el mejor compromiso disponible entre capacidad y cobertura. Por debajo de 15 GHz, la propagación sigue siendo "amable": la difracción existe, la penetración en edificios es viable, y una macrocelda urbana puede seguir cubriendo cientos de metros —lo que permite **reutilizar la malla de emplazamientos existente**, el factor de costo dominante de cualquier despliegue (la lección de mmWave en 5G: una capa que exige densificar sitios nuevos avanza lentamente). A la vez, hay mucho más espectro contiguo disponible que en la banda de 3.5 GHz: canales de 200–400 MHz por operador son plausibles.

El déficit de presupuesto de enlace respecto a 3.5 GHz (unos 6–12 dB de pérdida adicional de propagación, más peor penetración) se compensa con **MIMO extremadamente masivo** (*Gigantic/Extreme MIMO*, XL-MIMO): a 10 GHz, la longitud de onda de 3 cm permite empaquetar arreglos de 1024–4096 elementos en paneles del tamaño de los actuales de 64 elementos, con haces proporcionalmente más finos y mayor ganancia. El reto técnico es que FR3 está densamente ocupado por servicios incumbentes —enlaces fijos, servicios por satélite y sistemas de defensa (radares)—, por lo que su uso exigirá coordinación y, en algunos mercados, **compartición dinámica del espectro** asistida por sensado y bases de datos, un área donde el propio ISAC de 6G puede ayudar a verificar la coexistencia.

## La física del sub-THz: presupuesto de enlace cuesta arriba

En 92–300 GHz el ancho de banda es enorme (canales de varios GHz; el estándar IEEE 802.15.3d ya define canales de hasta 69 GHz de ancho en 252–325 GHz), pero la física cobra caro. La pérdida de espacio libre crece con el cuadrado de la frecuencia para aperturas de ganancia fija:

$$L_{FS} = \left(\frac{4\pi d f}{c}\right)^2 \;\Rightarrow\; L_{FS}\text{[dB]} = 92.45 + 20\log_{10} f_{\text{GHz}} + 20\log_{10} d_{\text{km}}$$

A 150 GHz y 100 m, $L_{FS} \approx 116$ dB —unos 26 dB más que a 7.5 GHz a la misma distancia. A esto se suma la **absorción molecular**: las moléculas de oxígeno y sobre todo de vapor de agua resuenan a frecuencias específicas y convierten energía de la onda en rotación molecular. El espectro queda dividido en *picos* de absorción (60 GHz por O₂ con ~15 dB/km; 119 GHz por O₂; 183 y 325 GHz por H₂O, con decenas a cientos de dB/km) y **ventanas de transmisión** entre ellos (alrededor de 94, 140, 220 y 300 GHz) donde la absorción cae a 1–10 dB/km —tolerable para enlaces de centenares de metros, no para kilómetros. La lluvia añade atenuación comparable a la de mmWave (varios dB/km a 10–20 mm/h), y el **bloqueo es casi óptico**: a estas longitudes de onda (1–3 mm) los muros, el follaje e incluso el cuerpo humano (10–30 dB) interrumpen el enlace, y la difracción apenas ayuda. La consecuencia arquitectónica: el sub-THz vive de **línea de vista o casi**, con haces extremadamente directivos y, como se verá dos lecciones más adelante, con superficies reconfigurables (RIS) como espejos programables para sortear obstáculos.

## Los retos de RF: donde la ingeniería duele

Generar y recibir señales de 100–300 GHz con anchos de banda de varios GHz tensiona cada bloque de la cadena:

**Amplificación de potencia.** La potencia de salida de los transistores cae abruptamente con la frecuencia (la barrera se resume en el producto potencia×frecuencia de cada tecnología). En CMOS, a >100 GHz se logran apenas ~10 mW por amplificador; tecnologías III-V (GaAs, y sobre todo **InP**, con frecuencias de corte >1 THz) rinden más pero cuestan más y se integran peor. La eficiencia de los amplificadores en estas bandas es de un dígito porcentual —un problema directo para el KPI de sostenibilidad de 6G. La respuesta arquitectónica es sumar potencia *en el aire*: cientos de elementos radiantes de baja potencia cuya combinación coherente logra la EIRP necesaria.

**Ruido de fase y conversión.** Los osciladores multiplicados hasta sub-THz arrastran un ruido de fase alto que degrada las constelaciones densas (por eso los enlaces sub-THz reales usan modulaciones modestas —QPSK a 16-QAM— y compensan con ancho de banda). Los **convertidores analógico-digital** son quizá el muro más duro: digitalizar varios GHz de banda con resolución suficiente dispara el consumo (la figura de mérito de los ADC empeora con la tasa de muestreo), lo que obliga a arquitecturas híbridas —conformación de haz analógica en RF con pocos convertidores— y a considerar resoluciones bajas (4–6 bits) con procesamiento que tolere la cuantización.

**Fotónica integrada.** Una vía complementaria genera el sub-THz *ópticamente*: dos láseres cuya diferencia de frecuencia es la portadora deseada baten sobre un fotodiodo de transporte unipolar (UTC-PD), produciendo señales de 100–600 GHz con gran pureza espectral y ancho de banda de modulación enorme. La fotónica de silicio permite integrar moduladores, filtros y detectores en el mismo chip, y conecta naturalmente el mundo sub-THz con la fibra (radio-over-fiber: la señal viaja por fibra hasta la antena y se convierte allí). Los récords de laboratorio de transmisión sub-THz (100+ Gbps a 300 GHz) provienen mayoritariamente de estos sistemas fotónicos, y la convergencia fibra-radio es candidata firme para el *fronthaul* de las redes densas de 6G.

## Ideas clave

- 6G usará un espectro en capas: FR3 (7–15 GHz) como nueva banda de capacidad principal, con sub-THz (92–300 GHz) para enlaces cortos de tasa extrema y sensado fino — no "la generación THz".
- FR3 permite reutilizar emplazamientos existentes y canales de 200–400 MHz, compensando su déficit de propagación con XL-MIMO de miles de elementos; su reto es la coexistencia con incumbentes (satélite, radar).
- En sub-THz mandan la pérdida de espacio libre ($+20\log f$), la absorción molecular de O₂/H₂O que define ventanas en ~94/140/220/300 GHz, y un bloqueo casi óptico que impone línea de vista.
- La RF sub-THz choca con límites de potencia (mW en CMOS, InP como alternativa cara), ruido de fase y ADCs de varios GHz; la EIRP se construye con cientos de elementos y beamforming híbrido.
- La generación fotónica (batido de láseres sobre UTC-PD) y la fotónica de silicio ofrecen portadoras sub-THz puras y anchas, y unen la radio con la fibra en el fronthaul.

## Para seguir

La siguiente lección, *ISAC: sensado y comunicación integrados*, muestra el uso más novedoso de estas bandas anchas y directivas: convertir la propia red en un radar distribuido.
