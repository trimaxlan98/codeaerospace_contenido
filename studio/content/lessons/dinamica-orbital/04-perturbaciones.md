---
title: Perturbaciones orbitales
level: avanzado
summary: El achatamiento terrestre, el arrastre atmosférico, la presión de radiación solar y el tercer cuerpo apartan toda órbita real de la elipse kepleriana ideal.
tags: [perturbaciones, j2, arrastre-atmosferico, sgp4, precesion-nodal]
minutes: 9
order: 4
---

## Objetivos

- Explicar por qué ninguna órbita real es una elipse kepleriana perfectamente cerrada e invariable.
- Calcular la precesión nodal inducida por $J_2$ y relacionarla con el diseño de órbitas heliosíncronas.
- Describir el efecto del arrastre atmosférico sobre el decaimiento orbital en LEO.
- Explicar cualitativamente la presión de radiación solar y las perturbaciones de tercer cuerpo.
- Comparar el propagador analítico SGP4 con la integración numérica de alta precisión.

## Por qué las órbitas reales no son keplerianas

Todo lo desarrollado en las lecciones anteriores asume un modelo de dos cuerpos puntuales bajo gravitación pura del inverso del cuadrado, que produce elipses cerradas y estáticas. Ninguna órbita real cumple exactamente esas condiciones: la Tierra no es una esfera perfecta ni homogénea, tiene atmósfera, y comparte el sistema solar con la Luna, el Sol y presión de radiación. Cada una de estas desviaciones se trata como una **perturbación**: una aceleración adicional, pequeña frente a la gravitación kepleriana dominante, que se suma a la ecuación de movimiento y hace que los elementos orbitales —supuestamente constantes— varíen lentamente (perturbaciones seculares, que crecen sin límite con el tiempo) o periódicamente (que oscilan sin tendencia neta). Ignorarlas produce errores de predicción de posición que, en LEO, alcanzan kilómetros en cuestión de días.

## El término $J_2$ y la precesión nodal

La perturbación dominante para casi cualquier satélite terrestre es el achatamiento de la Tierra: el planeta no es una esfera sino un elipsoide, con un radio ecuatorial (~$6378.137$ km) unos $21$ km mayor que el polar, resultado de la rotación. Este exceso de masa en el ecuador se captura en el desarrollo en armónicos esféricos del potencial gravitacional terrestre mediante el coeficiente $J_2 \approx 1.08263 \times 10^{-3}$, con diferencia el mayor de todos los términos de achatamiento (los siguientes, $J_3$, $J_4$, etc., son varios órdenes de magnitud menores).

El efecto secular más importante de $J_2$ es la **precesión nodal**: el plano orbital completo gira lentamente alrededor del eje polar, a una tasa

$$\dot\Omega = -\frac{3}{2}J_2\, n \left(\frac{R_\oplus}{p}\right)^2\cos i$$

donde $n = \sqrt{\mu/a^3}$ es el movimiento medio y $p = a(1-e^2)$ el semilatus rectum. El signo y la magnitud dependen críticamente de la inclinación: para órbitas prógradas de baja inclinación ($i < 90°$), $\cos i > 0$ y la precesión es hacia el oeste (retrógrada); para órbitas retrógradas ($i > 90°$), $\cos i < 0$ y la precesión es hacia el este.

Esta última posibilidad es la que hace posible la **órbita heliosíncrona (SSO)**: eligiendo la combinación adecuada de altitud e inclinación retrógrada, se puede lograr que $\dot\Omega$ coincida exactamente con la tasa de traslación aparente del Sol, $360°/365.2422\ \text{días} \approx 0.9856°/\text{día}$. El resultado es que el plano orbital mantiene una orientación fija respecto al Sol, y el satélite sobrevuela cualquier latitud siempre a la misma hora solar local —crucial para constelaciones de observación óptica. Para altitudes típicas de SSO, la inclinación necesaria ronda los $97°$–$99.5°$ (por ejemplo, aproximadamente $97.4°$ a $500$ km y $98.6°$ a $800$ km): valores que crecen con la altitud porque un $p$ mayor reduce la magnitud del término $(R_\oplus/p)^2$, exigiendo un $\cos i$ más negativo para compensar.

$J_2$ también induce una precesión secular del argumento del perigeo $\dot\omega$, nula exactamente en la inclinación crítica de $63.4°$ (o su suplemento $116.6°$), usada por las órbitas Molniya para mantener el apogeo fijo sobre un hemisferio sin corrección activa.

## Arrastre atmosférico

Por debajo de unos $1000$ km, la atmósfera residual —extremadamente tenue, pero no nula— ejerce una fuerza de arrastre sobre cualquier satélite, opuesta a su velocidad relativa al aire:

$$F_D = \frac{1}{2}\rho v^2 C_D A$$

donde $\rho$ es la densidad atmosférica local (que varía varios órdenes de magnitud con la altitud y con la actividad solar, siendo mucho mayor durante máximos solares que calientan y expanden la atmósfera superior), $C_D$ el coeficiente de arrastre (típicamente entre $2.0$ y $2.2$ para satélites), y $A$ el área frontal expuesta. El arrastre extrae energía orbital de forma continua, reduciendo el semieje mayor: el efecto neto es un **decaimiento** que circulariza progresivamente la órbita (el arrastre es más intenso cerca del perigeo, donde la densidad y la velocidad relativa son mayores, así que erosiona primero el apogeo) y finalmente provoca reentrada. El parámetro clave que determina la susceptibilidad de un satélite al arrastre es el coeficiente balístico, $BC = m/(C_D A)$: un satélite masivo y compacto decae mucho más lentamente que uno ligero y con gran área expuesta (como una vela solar o un CubeSat con paneles desplegados). En LEO bajo (por debajo de $400$ km), el decaimiento puede ser cuestión de meses; a $800$ km, de siglos.

## Presión de radiación solar y tercer cuerpo

La luz solar transporta momento, y al reflejarse o absorberse sobre la superficie de un satélite ejerce una presión —del orden de $4.6\ \mu\text{N/m}^2$ a la distancia de la Tierra al Sol (una unidad astronómica)— proporcional al área expuesta e inversamente proporcional a la masa. Su efecto es despreciable en LEO frente al arrastre, pero domina en GEO y en órbitas de gran superficie expuesta (satélites con paneles solares grandes o velas), donde introduce oscilaciones periódicas en la excentricidad y requiere maniobras de mantenimiento en estación (station-keeping) para compensar la deriva acumulada.

Las **perturbaciones de tercer cuerpo**, principalmente de la Luna y el Sol, surgen de que su atracción gravitatoria no es exactamente igual en el satélite que en el centro de la Tierra (efecto de marea): la diferencia introduce aceleraciones adicionales que afectan sobre todo a órbitas altas (GEO, y especialmente órbitas muy elípticas con apogeo lejano), causando derivas seculares en inclinación y otros elementos que también exigen correcciones periódicas.

## Propagadores: SGP4 frente a integración numérica

Existen dos familias de herramientas para predecir la posición futura de un satélite perturbado. Los **propagadores analíticos**, de los cuales el más usado con diferencia es **SGP4** (Simplified General Perturbations 4), incorporan modelos aproximados de $J_2$ (y armónicos superiores) y de arrastre atmosférico directamente en fórmulas cerradas, calibradas para trabajar exclusivamente con los elementos de un TLE. Su ventaja es la velocidad: pueden propagar miles de objetos en milisegundos, razón por la cual son el estándar del catálogo público de objetos en órbita. Su desventaja es la precisión limitada (típicamente kilómetros de error tras unos días) y que solo son válidos con TLEs generados específicamente para ellos, no con elementos osculantes arbitrarios.

La **integración numérica** de alta precisión, en cambio, integra paso a paso la ecuación de movimiento completa, sumando explícitamente todas las aceleraciones perturbadoras relevantes (armónicos gravitacionales de alto grado, arrastre con modelos atmosféricos detallados, radiación solar, terceros cuerpos) mediante métodos como Runge-Kutta de orden alto. Ofrece precisión muy superior —submétrica, en aplicaciones de determinación de órbita de precisión— a costa de un coste computacional mucho mayor y de requerir un modelo de fuerzas mucho más detallado y datos de entrada (como el estado atmosférico) que no siempre están disponibles con la exactitud necesaria.

## Ideas clave

- Toda órbita real se desvía de la elipse kepleriana ideal por perturbaciones seculares y periódicas; ignorarlas produce errores de kilómetros en pocos días.
- $J_2$, resultado del achatamiento terrestre, causa precesión nodal $\dot\Omega \propto -\cos i$; elegir inclinaciones retrógradas apropiadas hace posible la órbita heliosíncrona.
- El arrastre atmosférico circulariza y decae la órbita, con una tasa que depende del coeficiente balístico $m/(C_D A)$ y de la actividad solar.
- La presión de radiación solar y las perturbaciones de tercer cuerpo (Luna, Sol) dominan en órbitas altas como GEO, no en LEO.
- SGP4 es rápido pero limitado a TLE con precisión de kilómetros; la integración numérica es precisa pero costosa y exige un modelo de fuerzas detallado.

## Para seguir

La siguiente lección, *Determinación y propagación de órbitas*, cierra la categoría explicando cómo se obtienen esos elementos orbitales en primer lugar a partir de observaciones reales (radar, óptico, GNSS) y cómo se estima su incertidumbre.
