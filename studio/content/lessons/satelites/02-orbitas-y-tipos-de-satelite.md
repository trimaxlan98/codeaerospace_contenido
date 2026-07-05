---
title: Órbitas y familias de satélites
level: intro
summary: Altitudes y periodos típicos de LEO, MEO, GEO y HEO, la órbita heliosíncrona, Molniya, y sus aplicaciones características.
tags: [orbitas, leo, geo, sso, molniya]
minutes: 8
order: 2
---

## Objetivos

- Conocer altitudes, periodos y características de LEO, MEO, GEO y HEO.
- Entender qué es una órbita heliosíncrona (SSO) y por qué se define por su hora local del nodo ascendente.
- Describir la órbita Molniya y el problema que resuelve para latitudes altas.
- Relacionar cada familia orbital con las aplicaciones para las que resulta óptima.
- Comparar cuantitativamente latencia y cobertura entre familias orbitales.

## Las cuatro grandes familias

| Familia | Altitud | Periodo orbital | Inclinación típica | Ejemplos |
|---|---|---|---|---|
| LEO | 300–2000 km | 90–127 min | Variable (0°–98°) | ISS, Starlink, satélites de observación |
| MEO | 2000–35 786 km | 2–24 h | ~55°–65° (navegación) | GPS (~20 200 km), Galileo (~23 222 km) |
| GEO | 35 786 km | 24 h (sidéreo) | 0° | Satélites de comunicaciones, meteorológicos (GOES) |
| HEO | Perigeo bajo, apogeo muy alto | 12 h (Molniya) o más | Alta (63.4° para Molniya) | Molniya, Tundra, satélites de alerta temprana |

**LEO (Low Earth Orbit)**: la más cercana a la Tierra, con periodos de hora y media aproximadamente. Ofrece baja latencia de señal y alta resolución para observación, pero un satélite individual solo ve una franja estrecha de la superficie a la vez y pasa sobre cualquier punto dado solo unos minutos por órbita, lo que exige constelaciones (múltiples satélites) para cobertura continua.

**MEO (Medium Earth Orbit)**: el rango intermedio, dominado por las constelaciones de navegación global (GNSS). GPS opera en 6 planos orbitales a ~20 200 km con periodo de 11 h 58 min (exactamente la mitad de un día sidéreo, lo que hace que cada satélite pase sobre el mismo punto de la Tierra dos veces al día). Galileo opera algo más alto (~23 222 km, periodo ~14 h).

**GEO (Geostationary Earth Orbit)**: a 35 786 km sobre el ecuador con inclinación 0°, un satélite orbita exactamente al ritmo de rotación de la Tierra y permanece fijo respecto a un observador terrestre. Ideal para comunicaciones fijas y meteorología (los satélites GOES de EE. UU. o Meteosat de Europa), a costa de mayor latencia y menor resolución angular para observación.

**HEO (Highly Elliptical Orbit)**: órbitas muy excéntricas con perigeo bajo (a veces solo unos cientos de km) y apogeo muy alto (decenas de miles de km). Se explican en detalle en la siguiente sección.

## Órbita heliosíncrona (SSO) y hora local del nodo

Una **órbita heliosíncrona** (SSO, *Sun-Synchronous Orbit*) es una órbita casi polar (inclinación retrógrada, típicamente entre 96° y 100°) diseñada para que el plano orbital precese exactamente al mismo ritmo que la Tierra se traslada alrededor del Sol: 360° por año, es decir, unos 0.9856°/día. Esta precesión ocurre naturalmente por el achatamiento de la Tierra (el término $J_2$ del potencial gravitacional), que perturba el plano orbital de forma predecible según la altitud e inclinación.

El resultado práctico es que el satélite sobrevuela cualquier latitud dada siempre a la **misma hora solar local**, lo que se especifica como la "hora local del nodo ascendente" (LTAN, *Local Time of Ascending Node*). Esto es enormemente valioso para observación de la Tierra: garantiza condiciones de iluminación solar consistentes entre pasadas, facilitando la comparación de imágenes tomadas en fechas distintas. Constelaciones ópticas como Planet o Sentinel-2 operan en SSO con LTAN cercano a las 10:30 de la mañana, un compromiso clásico entre buena iluminación (ángulo solar suficientemente alto) y baja cobertura de nubes convectivas típicas de la tarde.

Un caso especial de SSO es la órbita de "mediodía-medianoche" (LTAN 12:00), usada por algunos satélites que requieren visibilidad solar casi continua para paneles solares, o "amanecer-atardecer" (LTAN 06:00), usada por satélites de radar (que no dependen de iluminación solar) para maximizar la disponibilidad de energía solar al orbitar siempre cerca del terminador día/noche, minimizando el tiempo en eclipse.

## Órbita Molniya

Diseñada por la Unión Soviética para dar cobertura de comunicaciones a sus territorios de alta latitud (donde GEO ofrece ángulos de elevación muy bajos o directamente no es visible cerca del polo), la **órbita Molniya** es una HEO con periodo de 12 horas, perigeo bajo (~500-600 km) y apogeo muy alto (~40 000 km), e inclinación crítica de **63.4°**.

Esta inclinación no es arbitraria: es el único valor (junto a 116.6°) para el cual la perturbación por achatamiento terrestre ($J_2$) no causa rotación del argumento del perigeo, manteniendo el apogeo fijo sobre el hemisferio de interés indefinidamente sin necesidad de correcciones activas. Por la tercera ley de Kepler, un objeto en una órbita muy excéntrica pasa la mayor parte de su periodo cerca del apogeo (donde se mueve más lento) y muy poco tiempo cerca del perigeo (donde se mueve rápido); en una Molniya, el satélite permanece "útil" —alto sobre el horizonte del hemisferio norte, por ejemplo— durante unas 8 horas de cada órbita de 12. Se requieren típicamente 3 satélites en la misma constelación, desfasados en el tiempo, para dar cobertura continua 24/7 con al menos uno siempre en la fase útil de su órbita.

La órbita **Tundra**, variante con periodo de 24 horas (un ciclo completo por día en vez de dos), ofrece una geometría similar con menos satélites necesarios para cobertura continua, y es usada por sistemas modernos como el Sirius XM (radio satelital) para dar cobertura a Norteamérica con mejores ángulos de elevación que GEO en latitudes altas.

## Tabla comparativa: latencia y cobertura

| Parámetro | LEO (~550 km) | MEO (~20 000 km) | GEO (35 786 km) |
|---|---|---|---|
| Latencia de ida (un salto, luz) | ~1.8 ms | ~67 ms | ~119 ms |
| Latencia RTT típica (con procesamiento) | 20–40 ms | 120–150 ms | 240–280 ms |
| Satélites para cobertura global continua | Cientos a miles | Decenas (24-30 típico GNSS) | 3 (con superposición) |
| Huella de cobertura por satélite | Cientos a ~1000 km de radio | Miles de km | ~1/3 del globo |
| Vida útil típica | 5–10 años (LEO comercial) | 10–15 años | 15–20 años |

La latencia de un salto en GEO (~119 ms de ida, ~238 ms de ida y vuelta solo por la distancia recorrida a la velocidad de la luz) es una limitación física insalvable —no una limitación de ingeniería— que explica por qué las megaconstelaciones LEO han ganado terreno para aplicaciones sensibles a la latencia como videollamadas o gaming en línea, como se detalla en la lección de megaconstelaciones.

## Ideas clave

- LEO ofrece baja latencia y alta resolución a costa de cobertura instantánea limitada; GEO ofrece cobertura fija de un tercio del globo a costa de latencia alta.
- La órbita heliosíncrona (SSO) mantiene una hora solar local constante en cada pasada gracias a la precesión natural inducida por el achatamiento terrestre ($J_2$).
- La inclinación crítica de 63.4° en la órbita Molniya congela el argumento del perigeo, permitiendo cobertura estable de alta latitud sin corrección activa.
- GPS y Galileo operan en MEO con periodos de aproximadamente medio día sidéreo, repitiendo su traza terrestre cada 24 horas.
- La latencia por distancia en GEO (~240 ms de ida y vuelta) es un límite físico, no técnico, que ninguna mejora de ingeniería puede eliminar.

## Para seguir

La siguiente lección, *Comunicaciones por satélite*, retoma la latencia y las bandas de frecuencia introducidas aquí para explicar cómo se diseña el enlace de radio en cada una de estas familias orbitales. *Megaconstelaciones LEO* profundiza en el caso específico de constelaciones masivas en órbita baja y su comparación de latencia frente a GEO.
