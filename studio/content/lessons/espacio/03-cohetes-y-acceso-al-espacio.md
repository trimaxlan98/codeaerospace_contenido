---
title: Cohetes y acceso al espacio
level: medio
summary: La ecuación de Tsiolkovsky, el diseño por etapas, las ventanas de lanzamiento y el impacto de la reutilización en el costo por kilogramo.
tags: [cohetes, tsiolkovsky, lanzamiento, reutilizacion, delta-v]
minutes: 8
order: 3
---

## Objetivos

- Derivar e interpretar la ecuación del cohete de Tsiolkovsky.
- Entender por qué los cohetes se construyen por etapas y qué ganancia ofrece esa arquitectura.
- Explicar cómo la inclinación orbital objetivo y la latitud del sitio de lanzamiento determinan la ventana de lanzamiento.
- Comparar el costo por kilogramo a órbita entre cohetes desechables y reutilizables.

## La ecuación de Tsiolkovsky

Toda la física de un cohete se resume en una sola expresión, derivada por Konstantín Tsiolkovsky en 1903 a partir de la conservación del momento en un sistema de masa variable:

$$\Delta v = v_e \ln\left(\frac{m_0}{m_f}\right)$$

donde $\Delta v$ es el cambio de velocidad que el cohete puede lograr, $v_e$ es la velocidad efectiva de escape de los gases (relacionada con el impulso específico $I_{sp}$ por $v_e = I_{sp} \cdot g_0$, con $g_0 = 9.81\ \text{m/s}^2$), $m_0$ es la masa inicial (con propelente) y $m_f$ es la masa final (sin propelente, es decir, estructura más carga útil).

La relación es logarítmica, no lineal: duplicar el $\Delta v$ requiere elevar al cuadrado la relación de masas $m_0/m_f$. Esto explica por qué un cohete orbital es, en masa, mayormente propelente: para alcanzar los ~9.4 km/s de $\Delta v$ que efectivamente se requieren para llegar a LEO (incluyendo pérdidas por gravedad y arrastre, aunque la velocidad orbital circular en sí es de ~7.8 km/s), con motores de queroseno/oxígeno líquido ($I_{sp} \approx 300$ s, $v_e \approx 2940$ m/s), se necesita una relación de masas $m_0/m_f = e^{9400/2940} \approx 24$. Es decir, más del 95% de la masa inicial del cohete debe ser propelente.

Los combustibles importan: el hidrógeno líquido con oxígeno líquido alcanza $I_{sp} \approx 450$ s (motores como el RS-25 del Shuttle/SLS), muy superior al queroseno, pero el hidrógeno líquido tiene densidad mucho menor, lo que obliga a tanques más grandes y pesados. Los motores de metano líquido (como el Raptor de SpaceX, $I_{sp} \approx 330$–380 s) buscan un punto intermedio, con la ventaja adicional de facilitar la producción in-situ de propelente en Marte.

## Diseño por etapas

Si la ecuación de Tsiolkovsky exige relaciones de masa tan extremas, ¿por qué no se construye un cohete monoetapa gigantesco? El problema es que, al quemar el propelente de las primeras fases del vuelo, el cohete sigue cargando el peso muerto de tanques y motores ya vacíos, lo que penaliza el rendimiento. La solución es el **diseño por etapas**: al agotar una etapa, esta se desprende y el cohete continúa acelerando con menos masa muerta, típicamente reiniciando la ecuación con una nueva $v_e$ y relación de masas propias de la siguiente etapa.

El $\Delta v$ total de un cohete de $n$ etapas es la suma de los $\Delta v$ individuales de cada etapa:

$$\Delta v_{total} = \sum_{i=1}^{n} v_{e,i} \ln\left(\frac{m_{0,i}}{m_{f,i}}\right)$$

La mayoría de lanzadores orbitales usan 2 o 3 etapas. Un cohete típico como el Falcon 9 usa dos etapas: la primera (con 9 motores Merlin) opera en la atmósfera densa donde la eficiencia de la tobera se ve limitada por la presión ambiente, y la segunda (un solo motor Merlin optimizado para vacío) completa la inserción orbital. Los propulsores de refuerzo laterales (*boosters*) de cohetes como el Ariane 5 o el SLS son, en efecto, una "etapa 0" que añade empuje inicial y se desprende tras el ascenso atmosférico.

## Ventanas de lanzamiento e inclinación

La **inclinación orbital** que un lanzador puede alcanzar directamente (sin maniobras de cambio de plano, que son extremadamente costosas en $\Delta v$) está limitada por la **latitud del sitio de lanzamiento**: un cohete no puede alcanzar, sin gasto adicional de energía, una inclinación menor que la latitud desde la que despega, porque la componente de velocidad que aporta la rotación terrestre apunta en la dirección este-oeste a lo largo del paralelo de lanzamiento.

Cabo Cañaveral (28.5° N) puede lanzar directamente a inclinaciones de 28.5° o mayores, aprovechando además la velocidad tangencial de la rotación terrestre (~408 m/s en esa latitud) al lanzar hacia el este, lo que reduce el $\Delta v$ necesario. El Centro Espacial Guayana en Kurú (5.2° N) tiene una ventaja aún mayor por su cercanía al ecuador (~463 m/s de asistencia rotacional), siendo un sitio preferido para lanzamientos a GEO. Baikonur (45.9° N) no puede lanzar directamente a inclinaciones bajas; por eso las misiones tripuladas rusas a la ISS (inclinación 51.6°) usan precisamente esa inclinación, que coincide con la latitud del cosmódromo.

Para órbitas heliosíncronas (SSO), que requieren inclinaciones retrógradas cercanas a 98°, el lanzamiento suele hacerse hacia el sur, y sitios como Vandenberg (California, 34.7° N) o el nuevo puerto espacial de Kourou son preferidos por evitar sobrevolar zonas pobladas en la trayectoria ascendente. La ventana de lanzamiento para una misión que debe encontrarse con una nave existente (rendezvous, como en misiones a la ISS) se reduce a minutos, porque el plano orbital objetivo pasa por la posición del sitio de lanzamiento solo una o dos veces al día.

## Costo por kilogramo y reutilización

Históricamente, el costo de poner un kilogramo en LEO ha sido uno de los mayores obstáculos para la exploración y explotación comercial del espacio:

| Lanzador (era) | Costo aproximado por kg a LEO (USD) |
|---|---|
| Transbordador espacial (1981-2011) | 18 000–30 000 |
| Ariane 5 (desechable, 2000s) | ~10 000 |
| Falcon 9 (desechable, 2010s) | ~2 700 |
| Falcon 9 (primera etapa reutilizada) | ~1 200–1 500 |
| Starship (objetivo de diseño, reutilización total) | 100–200 (proyectado) |

La reutilización de la primera etapa —mediante un descenso propulsado con reencendido de motores y aterrizaje vertical, ya sea en tierra o en una barcaza autónoma en el mar— evita fabricar de nuevo la parte más costosa del vehículo (motores, tanques, aviónica) en cada misión. El principal costo recurrente pasa a ser el propelente (una fracción menor del costo total) y la inspección/recertificación de la etapa recuperada. SpaceX ha demostrado reutilización de una misma primera etapa del Falcon 9 más de veinte veces. El objetivo de diseño de sistemas totalmente reutilizables (primera y segunda etapa, como busca Starship) es reducir el costo por kg en uno o dos órdenes de magnitud adicionales, acercándose a la meta histórica de "acceso rutinario al espacio".

## Ideas clave

- La ecuación de Tsiolkovsky ($\Delta v = v_e \ln(m_0/m_f)$) es logarítmica: pequeños aumentos de $\Delta v$ requieren aumentos exponenciales en la fracción de propelente.
- El diseño por etapas descarta masa muerta progresivamente, permitiendo alcanzar el $\Delta v$ orbital total (~9.4 km/s) que sería impráctico con una sola etapa.
- La inclinación orbital alcanzable sin penalización de $\Delta v$ está acotada por abajo por la latitud del sitio de lanzamiento.
- Lanzar hacia el este cerca del ecuador aprovecha la velocidad de rotación terrestre y reduce el costo energético a órbitas ecuatoriales o de baja inclinación.
- La reutilización de primeras etapas ha reducido el costo por kg a LEO en más de un orden de magnitud desde la era del transbordador.

## Para seguir

La siguiente lección, *Basura espacial y sostenibilidad orbital*, aborda qué ocurre después del lanzamiento: cómo se acumulan los desechos en las órbitas que estos cohetes ayudan a poblar y qué prácticas mitigan el riesgo. *Clima espacial y sus efectos*, al final de esta categoría, describe otro factor —la actividad solar— que también condiciona el diseño y la operación de estos vehículos y sus cargas útiles.
