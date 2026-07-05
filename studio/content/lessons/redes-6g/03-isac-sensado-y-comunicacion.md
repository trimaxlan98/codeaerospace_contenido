---
title: "ISAC: sensado y comunicación integrados"
level: avanzado
summary: La red 6G como radar distribuido, formas de onda de doble función, casos de uso de sensado, métricas de estimación con la cota de Cramér-Rao y privacidad.
tags: [isac, sensado, radar, formas-de-onda, privacidad]
minutes: 12
order: 3
---

## Objetivos

- Explicar el concepto de ISAC y por qué 6G lo incorpora como escenario de uso de primera clase.
- Describir los modos de sensado (monoestático, biestático, multistático) sobre una red celular.
- Analizar las formas de onda de doble función y el compromiso comunicación-sensado.
- Interpretar las métricas del sensado: resolución en distancia y velocidad, y la cota de Cramér-Rao como límite de precisión.
- Examinar los casos de uso y los problemas de privacidad que plantea una red que percibe.

## La red como radar: por qué ahora

**ISAC** (*Integrated Sensing and Communication*) designa el uso de una misma infraestructura, un mismo espectro y —en su forma más ambiciosa— una misma señal para transmitir datos *y* percibir el entorno físico: posición, velocidad, forma y hasta microactividad de objetos y personas que no llevan ningún dispositivo. La convergencia es natural porque radar y comunicaciones llevan décadas acercándose tecnológicamente: ambos usan hoy arreglos de antenas con conformación digital de haz, anchos de banda de cientos de MHz a GHz y procesamiento OFDM o similar. Lo que hace de 6G el punto de encuentro son tres tendencias simultáneas: **más ancho de banda** (la resolución en distancia mejora en proporción directa), **más antenas** (la resolución angular mejora con la apertura del arreglo, y los arreglos XL-MIMO de FR3 y sub-THz son enormes en términos de longitudes de onda) y **más densidad de estaciones** (una malla urbana de celdas es, geométricamente, un radar multistático ya desplegado con vistas desde múltiples ángulos). La ITU-R consagró ISAC como uno de los seis escenarios de IMT-2030, y 3GPP inició en Rel-19 el estudio de canal para sensado —el primer paso formal hacia su estandarización.

Los modos de operación se heredan del radar clásico, adaptados a la topología celular. En modo **monoestático**, la estación base transmite y escucha sus propios ecos; es el modo conceptualmente más simple pero exige *full-duplex* o una cancelación de autointerferencia formidable (la señal transmitida es ~100 dB más fuerte que los ecos). En modo **biestático**, una estación transmite y otra —o un terminal— recibe los ecos, evitando el problema de autointerferencia a cambio de exigir sincronización fina entre nodos separados. El modo **multistático** generaliza a múltiples transmisores y receptores que fusionan sus vistas, y es donde la red celular brilla: la misma escena observada desde varias geometrías resuelve ambigüedades y sombras que un radar único no puede. A ellos se suma el sensado *asistido por el terminal* (el móvil reporta mediciones del canal, base del posicionamiento actual) y el sensado *del canal mismo* (variaciones del CSI que delatan presencia y movimiento, sin hardware nuevo).

## Formas de onda de doble función

El corazón técnico de ISAC es la **forma de onda**: ¿puede una señal servir bien a dos amos? El radar quiere señales con autocorrelación impulsiva (para separar ecos cercanos), envolvente constante (para amplificar sin retroceso) y estructura conocida; la comunicación quiere maximizar información por hercio, lo que produce señales aleatorias de envolvente fluctuante. Las tres estrategias:

**Centrada en comunicación**: usar la señal de comunicación tal cual —OFDM con sus datos— y estimar el canal de ecos correlacionando contra los símbolos conocidos (que el propio transmisor conoce todos). OFDM resulta sorprendentemente competente como radar: el procesamiento en la rejilla tiempo-frecuencia entrega mapas distancia-Doppler con complejidad razonable. Sus debilidades: alto PAPR y sensibilidad al Doppler intercarrier a velocidades altas. Es la ruta de menor resistencia para 3GPP, porque reutiliza la infraestructura de señal existente (incluidas las señales de referencia ya definidas, como los CSI-RS y PRS del posicionamiento).

**Centrada en radar**: incrustar bits en una forma de onda de radar (chirps FMCW con modulación de índice, por ejemplo); maximiza el sensado pero su tasa de datos es pobre —útil en nichos vehiculares, no como interfaz celular.

**Diseño conjunto**: optimizar la señal para un compromiso explícito. Aquí aparecen alternativas como **OTFS** (*Orthogonal Time Frequency Space*), que modula la información directamente en el dominio retardo-Doppler —el dominio natural del sensado— y se comporta mejor que OFDM con Doppler alto, y los esquemas de precodificación MIMO que reparten grados de libertad espaciales entre haces de datos y haces de sondeo. El compromiso fundamental se formaliza como una frontera de Pareto entre tasa de información (bits/s/Hz) y precisión de estimación: cada grado de libertad —potencia, subportadora, haz— asignado a iluminar la escena es capacidad de comunicación cedida, y viceversa.

## Métricas: resolución, precisión y la cota de Cramér-Rao

Dos familias de métricas gobiernan el sensado. La **resolución** es la capacidad de separar dos objetos próximos, y depende de los recursos de señal de forma directa:

$$\Delta R = \frac{c}{2B}, \qquad \Delta v = \frac{\lambda}{2T_{obs}}, \qquad \Delta\theta \approx \frac{\lambda}{D}$$

Con $B = 400$ MHz (canal FR3 generoso), $\Delta R = 37.5$ cm; con $B = 2$ GHz en sub-THz, 7.5 cm. La resolución en velocidad mejora con el tiempo de observación $T_{obs}$, y la angular con la apertura $D$ del arreglo en longitudes de onda —de ahí que XL-MIMO y sub-THz sean multiplicadores directos del sensado.

La **precisión** de la estimación de un parámetro (no separar dos objetos, sino ubicar uno con exactitud) está limitada por la **cota de Cramér-Rao** (CRB): ningún estimador insesgado puede tener varianza menor que el inverso de la información de Fisher, $\text{var}(\hat\theta) \ge I^{-1}(\theta)$. Su lectura conceptual para ISAC: la CRB de la distancia decrece con el SNR y con el *ancho de banda cuadrático medio* de la señal (cuánta energía pone la señal en los bordes del espectro), y la del ángulo con el SNR y la apertura efectiva. La CRB es la herramienta de diseño estándar del área: las fronteras tasa-precisión de la literatura enfrentan capacidad de Shannon contra CRB, y permiten responder cuantitativamente preguntas como cuántas subportadoras dedicar a sensado para lograr 10 cm de precisión sin ceder más del 5% de la tasa. Con muchas estaciones cooperando, la fusión multistática reduce además la dilución geométrica: la precisión final depende de la geometría de las vistas tanto como de cada enlace individual.

## Casos de uso y el problema de la privacidad

Los casos de uso maduran en tres anillos. El más cercano: **posicionamiento centimétrico** de terminales (extensión directa de lo que 5G ya hace con precisión métrica) para logística, fábricas y AGVs. El segundo: **percepción de objetos pasivos** —drones no cooperativos cerca de aeropuertos, peatones y vehículos en cruces (complementando los sensores a bordo con la vista elevada de la red), mapeo 3D urbano continuo para gemelos digitales. El tercero y más delicado: **sensado de personas** —detección de presencia y caídas en el hogar (teleasistencia sin cámaras ni wearables), reconocimiento de gestos, e incluso monitorización de respiración y ritmo cardiaco por micro-Doppler, capacidades ya demostradas con WiFi sensing (el estándar IEEE 802.11bf normaliza el equivalente en WLAN).

Ese tercer anillo hace inevitable la pregunta de **privacidad**: una red ISAC percibe a quien no lleva dispositivo, no firmó términos de servicio y no puede optar por salir —la asimetría fundamental respecto a toda la telefonía anterior, donde ser observado requería portar un terminal. Los vectores de riesgo son concretos: seguimiento de personas a través de paredes, inferencia de actividad doméstica, identificación por la forma de andar (*gait*). Las líneas de defensa en investigación: minimización en origen (extraer solo el parámetro necesario —"hay una caída"— y descartar los datos crudos del canal), agregación y anonimización espacial, distorsión deliberada de la información sensible (formas de onda que degradan el micro-Doppler humano fuera de zonas autorizadas), marcos de consentimiento por zonas, y auditoría regulatoria —el AI Act europeo y los reglamentos de protección de datos aplicarán a estos sistemas. La postura honesta del campo: ISAC no será socialmente viable sin resolver esto *por diseño*, y la estandarización 3GPP incluye la exposición de servicios de sensado con control de acceso como parte del problema, no como añadido posterior.

## Ideas clave

- ISAC convierte la red en un radar distribuido reutilizando espectro, hardware y señal; converge en 6G porque ancho de banda, apertura de antenas y densidad de celdas crecen a la vez.
- Los modos monoestático (autointerferencia dura), biestático (sincronización dura) y multistático (fusión de vistas, el punto fuerte de una red celular) definen las geometrías de sensado.
- OFDM con símbolos conocidos es la forma de onda pragmática; OTFS y la precodificación conjunta exploran el compromiso; la frontera tasa-precisión formaliza que cada recurso sirve a un amo.
- Resolución: $\Delta R = c/2B$, $\Delta v = \lambda/2T_{obs}$, $\Delta\theta \approx \lambda/D$; precisión: acotada por Cramér-Rao, que mejora con SNR, ancho de banda cuadrático medio y apertura.
- Los usos van del posicionamiento centimétrico al sensado de personas sin dispositivo; esto último crea un problema de privacidad estructural (no hay opt-out) que exige minimización y control por diseño.

## Para seguir

La siguiente lección, *Superficies inteligentes reconfigurables (RIS)*, presenta la tecnología que puede dar a ISAC y al sub-THz lo que la física les niega: control sobre el propio canal de propagación.
