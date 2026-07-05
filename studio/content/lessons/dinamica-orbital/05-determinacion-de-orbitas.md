---
title: Determinación y propagación de órbitas
level: avanzado
summary: Radar, óptica y GNSS aportan las observaciones que, ajustadas por mínimos cuadrados o filtros secuenciales, alimentan los catálogos públicos de objetos en órbita.
tags: [determinacion-de-orbitas, minimos-cuadrados, filtro-de-kalman, space-track]
minutes: 9
order: 5
---

## Objetivos

- Enumerar las principales fuentes de observación usadas para determinar órbitas: radar, óptica y GNSS.
- Explicar conceptualmente el ajuste por mínimos cuadrados de un conjunto de observaciones.
- Describir la idea central del filtro de Kalman como estimador secuencial y su ventaja frente al ajuste por lotes.
- Identificar los catálogos públicos de objetos en órbita y su origen institucional.
- Interpretar qué significa la precisión y la covarianza de una órbita determinada.

## De observaciones dispersas a una órbita

Las lecciones anteriores asumieron que los elementos orbitales —o un TLE— ya estaban disponibles. En la práctica, un satélite no "declara" su propia órbita: esta debe **determinarse** a partir de mediciones externas, discretas y ruidosas, tomadas en instantes distintos y típicamente desde ubicaciones distintas. La determinación de órbitas (Orbit Determination, OD) es el proceso de convertir ese conjunto de observaciones en un estado orbital completo —posición, velocidad, y en la práctica también una estimación de cuán bien se conoce ese estado.

## Observables: radar, óptico y GNSS

El **radar** ilumina activamente el objeto con un pulso de radiofrecuencia y mide el retardo de la señal reflejada (dando el rango, o distancia, con gran precisión) y, mediante arreglos de antenas o el desplazamiento Doppler de la portadora, también ángulos y velocidad radial. Es el método dominante para el catálogo de objetos en LEO, donde no depende de condiciones de iluminación ni de clima despejado (aunque su alcance efectivo decae fuertemente con la distancia, lo que lo hace menos práctico en GEO). Grandes radares de vigilancia espacial (como los de la red de vigilancia espacial de EE. UU.) proporcionan la mayoría de las observaciones que alimentan el catálogo público.

La **óptica** usa telescopios (terrestres o, cada vez más, en órbita) para medir la posición angular del satélite —como un punto de luz reflejando el Sol— proyectada contra el fondo de estrellas fijas, de las cuales se conocen las coordenadas con enorme precisión gracias a catálogos astrométricos. Este método no mide rango directamente (solo ángulos), requiere que el objeto esté iluminado por el Sol y el observador en penumbra (por eso las observaciones ópticas se concentran al amanecer y al atardecer, y son especialmente valiosas para objetos en GEO, demasiado lejanos para el radar convencional pero perfectamente visibles ópticamente por su brillo relativamente constante).

Los receptores **GNSS** (GPS, Galileo y equivalentes) a bordo del propio satélite, cuando están disponibles, dan la solución más directa: el satélite calcula su propia posición y velocidad con una precisión de metros o mejor, sin depender de observadores externos. Su limitación es que solo funciona por debajo de la constelación GNSS (típicamente hasta MEO alto, aunque existen receptores especializados para GEO que aprovechan señales laterales de los lóbulos de las antenas GNSS) y que requiere que el satélite lleve el receptor y transmita telemetría con su solución.

## Ajuste por mínimos cuadrados

Dado un conjunto de observaciones —digamos, docenas de mediciones de rango y ángulo de un radar a lo largo de varios pasos orbitales— el problema de determinación de órbita consiste en encontrar el estado orbital inicial (posición y velocidad, o equivalentemente los seis elementos) que, propagado hacia adelante mediante un modelo de fuerzas, mejor reproduce todas esas observaciones simultáneamente. "Mejor" se define, en el enfoque clásico de **mínimos cuadrados por lotes** (batch least squares), como el estado que minimiza la suma de los cuadrados de los residuos —la diferencia entre cada observación real y la que predice el modelo con ese estado propuesto. Como el modelo de propagación es no lineal, el ajuste se resuelve iterativamente: se parte de una estimación inicial aproximada, se linealiza el problema alrededor de ella (calculando cómo cambiaría cada observación predicha ante pequeños cambios en el estado, la llamada matriz de sensibilidad o Jacobiana), se resuelve el sistema lineal resultante para una corrección al estado, y se repite hasta que la corrección es despreciable.

Este enfoque por lotes procesa todas las observaciones de una vez y da, típicamente, la mejor precisión posible para un arco de datos dado, pero exige esperar a tener todo el lote de observaciones antes de producir una solución, y recalcular todo el ajuste si llega una observación nueva.

## Filtro de Kalman: estimación secuencial

El **filtro de Kalman** resuelve la misma clase de problema con un enfoque conceptualmente distinto: en lugar de ajustar todo un lote de observaciones a la vez, mantiene una estimación del estado (y de su incertidumbre) que se actualiza secuencialmente, observación por observación, a medida que llegan. Cada ciclo tiene dos pasos: una **predicción**, que propaga el estado y su incertidumbre hacia adelante en el tiempo usando el modelo dinámico (creciendo la incertidumbre, porque el modelo nunca es perfecto), y una **actualización**, que combina esa predicción con la nueva observación, ponderando cada una según su propia incertidumbre relativa —si el modelo es muy confiable, la actualización confía más en la predicción; si la observación es muy precisa, confía más en ella.

La ventaja práctica del filtro de Kalman es que produce una estimación actualizada en tiempo casi real, tan pronto como llega cada observación nueva, sin necesidad de reprocesar todo el historial, lo que lo hace preferible para seguimiento operacional continuo (por ejemplo, de una constelación activa), mientras que el ajuste por lotes se prefiere para reconstrucciones de precisión de un arco de datos ya completo (por ejemplo, la órbita definitiva de una misión científica tras la fase de recolección de datos).

## Catálogos públicos

El catálogo autorizado de objetos en órbita terrestre —satélites activos, satélites muertos, cuerpos de cohete gastados y fragmentos de basura espacial rastreables— es mantenido por la **18th Space Defense Squadron** (18 SDS, antes 18th Space Control Squadron) de la Fuerza Espacial de EE. UU., que procesa observaciones de su red de vigilancia espacial y publica los elementos orbitales resultantes (como TLEs, y crecientemente en formatos más modernos como el conjunto de elementos OMM) a través del portal público **Space-Track.org**. Este catálogo es la fuente de la que derivan, directa o indirectamente, prácticamente todas las herramientas de seguimiento y predicción de pases usadas por operadores, radioaficionados y desarrolladores de software de seguimiento en todo el mundo, incluidas las que se estudian en la categoría de apuntamiento satelital.

## Precisión y covarianza

Ninguna determinación de órbita es exacta: siempre viene acompañada de una **matriz de covarianza**, que cuantifica la incertidumbre del estado estimado (y las correlaciones entre sus componentes: por ejemplo, un error en la posición a lo largo de la dirección de vuelo suele estar correlacionado con un error en el semieje mayor). La precisión típica de un TLE público, propagado con SGP4, es del orden de un kilómetro poco después de su época, degradándose a varios kilómetros tras una semana sin actualizar; las órbitas de precisión usadas en operaciones críticas (como maniobras de proximidad o evitación de colisiones) emplean determinación numérica con observaciones densas —a menudo GNSS a bordo combinado con seguimiento externo— alcanzando precisiones de centímetros a decímetros. Esta covarianza no es un detalle académico: es el insumo directo de cualquier análisis de riesgo de colisión, donde la probabilidad de conjunción depende tanto de la distancia mínima predicha como de cuán bien se conoce esa distancia.

## Ideas clave

- Radar, óptica y GNSS aportan tipos de observación complementarios: rango preciso (radar), ángulos contra estrellas sin depender de rango (óptico) y posición directa a bordo (GNSS).
- El ajuste por mínimos cuadrados encuentra el estado orbital que mejor reproduce todo un lote de observaciones simultáneamente, mediante linealización iterativa.
- El filtro de Kalman actualiza la estimación secuencialmente, observación por observación, ideal para seguimiento operacional en tiempo casi real.
- La 18th Space Defense Squadron mantiene el catálogo público de objetos en órbita terrestre, distribuido a través de Space-Track.org.
- Toda órbita determinada viene con una covarianza asociada, que cuantifica su incertidumbre y es esencial para evaluar riesgo de colisión.

## Para seguir

Esto cierra la categoría de Dinámica Orbital. La siguiente categoría, *Apuntamiento Satelital*, comienza con *Geometría de apuntamiento*, que retoma estas órbitas ya determinadas para calcular cuándo y en qué dirección exacta observarlas desde una estación en tierra.
