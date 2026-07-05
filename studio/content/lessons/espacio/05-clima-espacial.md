---
title: Clima espacial y sus efectos
level: avanzado
summary: Fulguraciones, eyecciones de masa coronal, los índices Kp y Dst, y sus efectos en electrónica, comunicaciones y arrastre atmosférico.
tags: [clima-espacial, fulguraciones, cme, kp-dst, carrington]
minutes: 9
order: 5
---

## Objetivos

- Diferenciar fulguraciones solares y eyecciones de masa coronal (CME) como fenómenos físicos distintos con efectos distintos.
- Interpretar los índices Kp y Dst como medidas cuantitativas de la actividad geomagnética.
- Explicar los mecanismos de daño a electrónica espacial: eventos de un solo bit (SEU) y efecto de enclavamiento (latch-up).
- Entender la scintilación ionosférica y su impacto en comunicaciones y navegación satelital.
- Analizar el evento Carrington de 1859 como referencia histórica de un evento extremo.

## Fulguraciones solares y eyecciones de masa coronal

Aunque suelen mencionarse juntas, las **fulguraciones solares** (*solar flares*) y las **eyecciones de masa coronal** (CME, *coronal mass ejections*) son fenómenos físicamente distintos, con dinámicas y efectos diferentes:

- Una **fulguración** es una liberación súbita de energía electromagnética almacenada en el campo magnético coronal, típicamente por reconexión magnética sobre una región activa (mancha solar). Se clasifica por su intensidad de rayos X en clases A, B, C, M y X (cada letra representa un orden de magnitud), siendo las de clase X las más intensas. La radiación viaja a la velocidad de la luz, por lo que sus efectos sobre la ionosfera terrestre (absorción de ondas de radio de alta frecuencia, apagones de radio de onda corta) llegan en **8 minutos**, sin previo aviso posible.
- Una **CME** es la expulsión física de plasma magnetizado (miles de millones de toneladas de materia coronal) hacia el espacio interplanetario, a velocidades de 300 a más de 3000 km/s según su intensidad. Si está dirigida hacia la Tierra, tarda entre **15 horas y 3-4 días** en llegar, dando cierto margen de alerta temprana mediante observación coronográfica (misiones como SOHO y el más reciente DSCOVR en L1).

No toda fulguración va acompañada de una CME, ni viceversa, aunque las fulguraciones de clase X suelen coincidir con CME rápidas. El impacto geomagnético sobre la Tierra depende críticamente de la orientación del campo magnético dentro de la CME: si es predominantemente sur (opuesto al campo terrestre en el punto subsolar), la reconexión con la magnetosfera es mucho más eficiente y la tormenta resultante, mucho más intensa.

## Índices Kp y Dst

Para cuantificar la actividad geomagnética de forma estandarizada, se usan dos índices complementarios:

- **Índice Kp**: escala de 0 a 9 (con subdivisiones de tercios), derivada de mediciones de perturbación del campo magnético en una red global de ~13 observatorios terrestres, promediada en intervalos de 3 horas. Kp ≥ 5 marca el umbral de "tormenta geomagnética" según la escala G de la NOAA (G1 = Kp5, menor, hasta G5 = Kp9, extrema).
- **Índice Dst** (*Disturbance Storm Time*): mide en nanoteslas (nT) la depresión del campo magnético horizontal en el ecuador, causada por la corriente de anillo (*ring current*) de partículas atrapadas que se intensifica durante una tormenta. Valores de Dst entre -50 y -100 nT indican tormenta moderada; por debajo de -100 nT, tormenta intensa; el evento de marzo de 1989 (que provocó el apagón de Quebec) alcanzó Dst ≈ -589 nT, y el evento Carrington de 1859 se estima retrospectivamente en Dst ≈ -900 a -1750 nT.

Ambos índices alimentan modelos operativos de predicción usados por agencias como la NOAA Space Weather Prediction Center para emitir alertas a operadores de red eléctrica, aerolíneas (rutas polares) y operadores de satélites.

## Efectos en electrónica: SEU y latch-up

Las partículas de alta energía —protones solares durante eventos de partículas energéticas solares (SEP) y rayos cósmicos galácticos de fondo— pueden depositar suficiente carga en un transistor de un circuito integrado como para alterar su estado lógico, sin necesariamente destruir el componente. Dos mecanismos son especialmente relevantes en electrónica espacial:

- **SEU (Single Event Upset)**: un bit de memoria cambia de estado (de 0 a 1 o viceversa) por el paso de una partícula ionizante a través de una celda de memoria. Es un error "blando" (no destructivo): se corrige reescribiendo el dato, típicamente mediante códigos de corrección de errores (ECC) o *memory scrubbing* periódico. En satélites, la tasa de SEU aumenta notablemente durante eventos de partículas solares y al atravesar la Anomalía del Atlántico Sur (SAA), una región donde el cinturón de radiación interior desciende anómalamente cerca de la superficie terrestre debido a la inclinación del eje magnético terrestre respecto al de rotación.
- **Latch-up (SEL, Single Event Latch-up)**: una partícula dispara una estructura parásita tipo tiristor dentro del semiconductor (típicamente en tecnología CMOS), creando un cortocircuito de baja impedancia entre las líneas de alimentación. A diferencia del SEU, el latch-up es potencialmente **destructivo**: si no se interrumpe la alimentación rápidamente (mediante circuitos limitadores de corriente y ciclos de apagado/encendido), la corriente sostenida puede quemar el circuito por disipación térmica. Por esto, los componentes "rad-hard" (endurecidos a radiación) para uso espacial usan procesos de fabricación específicos (como silicio sobre aislante, SOI) que suprimen la estructura parásita causante del latch-up.

## Scintilación ionosférica

La ionosfera terrestre —la capa parcialmente ionizada entre ~60 y 1000 km de altitud— introduce irregularidades de densidad electrónica que, al atravesarlas, distorsionan la fase y amplitud de las señales de radiofrecuencia que la cruzan, un fenómeno llamado **scintilación ionosférica**. Es más intensa en la región ecuatorial (por la anomalía ecuatorial de ionización) y en latitudes aurorales/polares, y se agrava significativamente durante tormentas geomagnéticas.

Sus efectos prácticos incluyen: pérdida temporal de bloqueo de señal (*loss of lock*) en receptores GNSS (GPS, Galileo), degradando la precisión de posicionamiento de metros a decenas de metros durante eventos intensos; fading profundo en enlaces satelitales en bandas L y S; y errores de corrección ionosférica en sistemas de aumentación como WAAS/EGNOS, que pueden verse forzados a suspender temporalmente sus garantías de integridad durante tormentas severas. Los receptores de doble frecuencia mitigan parte del efecto porque el retardo ionosférico es proporcional a $1/f^2$, permitiendo estimar y restar la contribución ionosférica comparando dos frecuencias portadoras.

## El evento Carrington (1859)

El 1-2 de septiembre de 1859, el astrónomo Richard Carrington observó una fulguración solar excepcionalmente intensa, seguida (en solo ~17 horas, un tránsito inusualmente rápido) por la CME más intensa jamás documentada en registros históricos. El evento indujo corrientes tan fuertes en los cables telegráficos —la única infraestructura eléctrica de la época— que algunos operadores recibieron descargas y ciertos telégrafos funcionaron brevemente sin batería, alimentados por la corriente inducida. Se observaron auroras hasta latitudes tropicales, visibles en el Caribe.

Un evento de magnitud comparable hoy, con la infraestructura eléctrica, satelital y de telecomunicaciones moderna dependiente de electrónica sensible, se estima que podría causar daños económicos de cientos de miles de millones a más de un billón de dólares, con apagones eléctricos regionales prolongados (por daño a transformadores de alto voltaje, que no son fáciles de reemplazar rápidamente), pérdida o degradación de satélites por radiación y latch-up, e interrupción de GNSS y comunicaciones HF durante días. Este escenario motiva los planes de contingencia de organismos como la NOAA y la inclusión del clima espacial extremo en los registros nacionales de riesgo de varios países.

## Ideas clave

- Las fulguraciones (efecto en 8 minutos, vía radiación electromagnética) y las CME (efecto en 15 horas a varios días, vía plasma físico) son fenómenos distintos con ventanas de alerta muy diferentes.
- Kp (0-9, actividad geomagnética global) y Dst (nT, intensidad de la corriente de anillo) son los índices operativos estándar para cuantificar tormentas geomagnéticas.
- El SEU es un error de bit corregible; el latch-up es un cortocircuito potencialmente destructivo que requiere interrupción activa de la alimentación.
- La scintilación ionosférica degrada GNSS y enlaces satelitales, siendo más severa en regiones ecuatoriales y aurorales durante tormentas.
- El evento Carrington de 1859 sigue siendo la referencia de peor caso para dimensionar el riesgo de un evento de clima espacial extremo sobre la infraestructura tecnológica moderna.

## Para seguir

Esta lección cierra la categoría *El Espacio* profundizando en un riesgo introducido en *El entorno espacial* (radiación, cinturones de Van Allen) y en *El sistema solar como escenario de misiones* (viento solar). Para ver cómo estos riesgos se traducen en el diseño concreto de una nave, continúa con la categoría *Satélites*, empezando por *Anatomía de un satélite*.
