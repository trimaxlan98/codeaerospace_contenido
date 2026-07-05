---
title: CubeSats y NewSpace
level: medio
summary: El estándar CubeSat, el uso de componentes COTS, el rideshare, las arquitecturas distribuidas y la cadena de valor NewSpace.
tags: [cubesat, newspace, rideshare, cots, mision-distribuida]
minutes: 9
order: 5
---

## Objetivos

- Conocer el estándar CubeSat en unidades U y sus dimensiones y masas normalizadas.
- Entender qué son los componentes COTS y por qué han abaratado el acceso al espacio.
- Explicar el modelo de lanzamiento compartido (rideshare) y su impacto en el costo de acceso.
- Describir arquitecturas de misión distribuidas frente al satélite monolítico tradicional.
- Identificar casos de estudio (Planet, Spire) y la estructura de la cadena de valor NewSpace.

## El estándar CubeSat

El estándar **CubeSat**, desarrollado a finales de los años 90 por la Universidad Politécnica Estatal de California (Cal Poly) y la Universidad de Stanford, define una unidad modular de construcción satelital: **1U** equivale a un cubo de 10 × 10 × 10 cm con una masa máxima de aproximadamente **1.33 kg**. Los satélites se construyen combinando múltiplos de esta unidad:

| Formato | Dimensiones aproximadas | Masa máxima típica |
|---|---|---|
| 1U | 10 × 10 × 10 cm | 1.33 kg |
| 3U | 10 × 10 × 34 cm | 4-6 kg |
| 6U | 10 × 20 × 34 cm | 8-14 kg |
| 12U | 20 × 20 × 34 cm | ~20-24 kg |

Esta estandarización resolvió un problema estructural de la industria: antes de los CubeSats, cada satélite pequeño requería un adaptador de despliegue e integración a medida con el cohete, lo cual era costoso y lento. El estándar CubeSat definió una interfaz mecánica única —el desplegador P-POD y sus sucesores— que cualquier cohete con la interfaz adecuada puede acomodar, independientemente de quién construyó el satélite o qué lleva dentro. Esta interoperabilidad es la base que permitió el modelo de rideshare descrito más abajo.

## Componentes COTS

El segundo pilar que abarató drásticamente el costo de construir un satélite pequeño es el uso de componentes **COTS** (*Commercial Off-The-Shelf*): microcontroladores, sensores, memorias y otros componentes electrónicos diseñados originalmente para electrónica de consumo o industrial terrestre, en vez de componentes "rad-hard" (endurecidos a radiación) certificados específicamente para uso espacial, que pueden costar entre 10 y 100 veces más que su equivalente comercial.

El uso de COTS implica un compromiso consciente de riesgo: estos componentes son más susceptibles a eventos de radiación (SEU, latch-up, ver la lección de clima espacial) y tienen menor garantía de supervivencia a largo plazo en el ambiente espacial. Las misiones que los usan mitigan el riesgo mediante redundancia a nivel de sistema (en vez de a nivel de componente), diseño tolerante a fallos por software (reinicio watchdog, verificación de memoria), y aceptando misiones de vida útil más corta (meses a pocos años) donde el riesgo acumulado de degradación por radiación es manejable. Esta filosofía de "aceptar riesgo por costo" es una de las señas de identidad culturales de NewSpace frente a la aproximación tradicional de la industria espacial gubernamental, que privilegia la fiabilidad sobre el costo casi sin excepción.

## Rideshare

El modelo de **lanzamiento compartido** (*rideshare*) permite que decenas de satélites pequeños de distintos operadores compartan un mismo cohete, repartiendo el costo del lanzamiento entre todos ellos según su masa. Programas como el Transporter de SpaceX (lanzamientos dedicados a rideshare, varias veces al año, en órbita heliosíncrona) han reducido el costo de poner un CubeSat de 3U en órbita a cifras del orden de decenas de miles de dólares, frente a los cientos de miles o millones de dólares que costaba un lanzamiento dedicado en la década anterior.

El rideshare introduce restricciones propias: todos los satélites de una misión Transporter comparten la misma órbita objetivo (altitud, inclinación, hora local del nodo), lo que limita la flexibilidad orbital de cada operador individual frente a un lanzamiento dedicado. Los operadores que necesitan una órbita muy específica deben esperar una misión rideshare compatible o pagar el sobrecosto de propulsión propia a bordo del satélite para ajustar su órbita tras la separación.

## Arquitecturas de misión distribuidas

El abaratamiento del hardware y del lanzamiento ha impulsado un cambio de paradigma: en vez de construir un único satélite grande y muy capaz (arquitectura monolítica, con una única falla posible que compromete toda la misión), muchas misiones modernas optan por **arquitecturas distribuidas**: constelaciones de decenas a cientos de satélites pequeños, cada uno con capacidad individual modesta, que en conjunto logran una capacidad de misión igual o superior.

Las ventajas de este enfoque incluyen: tolerancia a fallos a nivel de flota (la pérdida de un satélite individual degrada marginalmente la capacidad total, en vez de terminar la misión); revisita temporal mucho más frecuente (más satélites cubriendo el globo significa pasar sobre cualquier punto con mayor frecuencia); y la posibilidad de iterar el diseño de hardware entre lotes de fabricación sucesivos, incorporando mejoras de forma incremental en vez de congelar el diseño años antes del lanzamiento como exige un satélite monolítico grande. La contrapartida es una mayor complejidad de operación de flota y de procesamiento de datos (fusionar información de muchas fuentes pequeñas en vez de una sola fuente grande).

## Casos de estudio y la cadena de valor NewSpace

**Planet Labs** opera la constelación de observación de la Tierra más grande del mundo en términos de número de satélites: cientos de satélites CubeSat de 3U ("Doves") que capturan imágenes ópticas de todo el territorio emergido del planeta a resolución de 3-5 metros, en teoría con revisita diaria completa. Su modelo de negocio se apoya precisamente en la arquitectura distribuida: en vez de un satélite de altísima resolución que revisita un punto cada varios días, ofrece resolución moderada pero con frecuencia temporal diaria, útil para agricultura, monitoreo ambiental e inteligencia.

**Spire Global** opera una constelación de CubeSats especializados en recolección de datos de radio-ocultación GNSS (para meteorología), seguimiento de embarcaciones marítimas (AIS) y aeronaves (ADS-B), demostrando que el modelo CubeSat no se limita a imágenes ópticas sino que sirve como plataforma general para sensores de radiofrecuencia distribuidos globalmente.

Ambos casos son posibles gracias a la cadena de valor especializada y modular que ha desarrollado el ecosistema NewSpace, en contraste con los programas espaciales gubernamentales tradicionales, verticalmente integrados:

- **Fabricantes de bus estándar**: empresas que venden plataformas CubeSat o small-sat listas para integrar carga útil, reduciendo el tiempo de desarrollo de años a meses.
- **Proveedores de componentes COTS espacializados**: fabricantes que califican componentes comerciales para el ambiente espacial sin llegar al costo de calificación rad-hard completa.
- **Operadores de lanzamiento rideshare**: SpaceX (Transporter), Rocket Lab y otros que agregan demanda de múltiples clientes en misiones compartidas.
- **Operadores de constelación**: empresas como Planet o Spire que poseen y operan la flota, vendiendo datos o servicios (no hardware) como producto final.
- **Plataformas de análisis de datos**: capas de software que procesan los datos crudos de la constelación (imágenes, señales) en productos de información específicos para cada industria cliente (agricultura, seguros, defensa, logística).

Esta desagregación ha permitido que empresas pequeñas participen en nichos específicos de la cadena sin necesidad de replicar la capacidad completa de una agencia espacial, acelerando la innovación y reduciendo las barreras de entrada a la industria espacial de forma más significativa que cualquier avance tecnológico aislado.

## Ideas clave

- El estándar CubeSat (1U = 10×10×10 cm, ~1.33 kg) creó una interfaz mecánica universal que hizo posible el rideshare y la producción en serie de satélites pequeños.
- Los componentes COTS reducen drásticamente el costo de un satélite a cambio de mayor riesgo de radiación, mitigado con redundancia de sistema y vidas útiles más cortas.
- El rideshare reparte el costo de lanzamiento entre muchos operadores, a costa de restringir la órbita objetivo a la de la misión compartida.
- Las arquitecturas distribuidas cambian tolerancia a fallos y frecuencia de revisita por complejidad de operación de flota y fusión de datos.
- Planet y Spire ejemplifican dos aplicaciones distintas del mismo modelo: imágenes ópticas de alta frecuencia y recolección de datos de radiofrecuencia distribuida, respectivamente.

## Para seguir

Esta lección cierra la categoría *Satélites*. Los conceptos de órbita, enlace y arquitectura de misión aquí introducidos se retoman con mayor profundidad matemática en la categoría *Dinámica Orbital*, y las técnicas de apuntamiento fino necesarias para las cargas útiles de estos satélites se desarrollan en *Apuntamiento Satelital*.
