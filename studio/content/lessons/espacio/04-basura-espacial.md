---
title: Basura espacial y sostenibilidad orbital
level: medio
summary: La población de escombros orbitales, el síndrome de Kessler, las maniobras de evasión de colisión y las reglas de desorbitado.
tags: [basura-espacial, kessler, cola, desorbitado, tracking]
minutes: 9
order: 4
---

## Objetivos

- Cuantificar la población de escombros orbitales por tamaño y su distribución en altitud.
- Explicar el mecanismo del síndrome de Kessler y por qué es una amenaza sistémica.
- Describir cómo se ejecuta una maniobra de evasión de colisión (COLA).
- Conocer las reglas de mitigación vigentes (desorbitado a 25/5 años) y su implementación práctica.
- Entender el papel del tracking terrestre en la gestión del riesgo orbital.

## Población de escombros por tamaño

La Oficina de Basura Espacial de la ESA y la Red de Vigilancia Espacial de EE. UU. (SSN) estiman la población de objetos en órbita terrestre en distintas bandas de tamaño:

| Tamaño del objeto | Cantidad estimada | Rastreable individualmente |
|---|---|---|
| > 10 cm | ~40 500 | Sí (catálogo público, ~30 000 activamente rastreados) |
| 1–10 cm | ~1 100 000 | No (estadístico) |
| 1 mm–1 cm | ~130 millones | No |

Solo los objetos mayores a unos 10 cm en LEO (y mayores en órbitas más altas, donde la resolución de los radares y telescopios es menor) pueden catalogarse individualmente y recibir un elemento orbital (TLE) actualizado. El resto se modela estadísticamente mediante entornos de flujo de escombros como el ORDEM de la NASA o el MASTER de la ESA. Pese a su tamaño diminuto, un fragmento de 1 cm a velocidades orbitales relativas de 7–15 km/s porta energía cinética comparable a una granada de mano; por eso incluso los escombros no catalogables representan un riesgo de perforación de trajes espaciales, paneles solares y blindajes.

La distribución en altitud no es uniforme: se concentra fuertemente entre 700 y 1000 km (zona de muchas misiones de observación de la Tierra y de eventos de fragmentación históricos) y presenta un segundo máximo cerca de GEO (35 786 km), donde no hay arrastre atmosférico que limpie la región de forma natural.

## El síndrome de Kessler

En 1978, Donald Kessler (NASA) formuló el escenario que lleva su nombre: si la densidad de objetos en una banda orbital supera un umbral crítico, las colisiones entre ellos generan nuevos fragmentos, que a su vez aumentan la probabilidad de colisiones futuras, en una **reacción en cadena autosostenida**. El resultado a largo plazo sería una capa de escombros tan densa que ciertas altitudes se volverían progresivamente más riesgosas o inutilizables para nuevas misiones, incluso sin nuevos lanzamientos.

Dos eventos reales ilustran el mecanismo:

- **Colisión Iridium 33 / Cosmos 2251 (2009)**: la primera colisión accidental entre dos satélites intactos, a ~789 km de altitud, generó más de 2000 fragmentos rastreables.
- **Prueba antisatélite china (2007)**: la destrucción deliberada del satélite meteorológico Fengyun-1C con un misil generó más de 3000 fragmentos catalogados, muchos de los cuales siguen en órbita más de 15 años después y continúan generando alertas de conjunción.

Ambos eventos, por sí solos, aumentaron la población catalogada de objetos en LEO en un porcentaje de dos dígitos, y sus fragmentos siguen contribuyendo al riesgo de colisión en las bandas de 700-900 km donde operan muchas misiones de observación terrestre.

## Maniobras de evasión de colisión (COLA)

Cuando el análisis de conjunción (*Conjunction Assessment*, CA) identifica que dos objetos catalogados pasarán peligrosamente cerca —típicamente cuando la probabilidad de colisión supera un umbral operativo de $10^{-4}$ y la distancia de aproximación mínima (miss distance) cae por debajo de unos cientos de metros a 1 km—, el operador del satélite activo puede ejecutar una **maniobra de evasión de colisión** (COLA, *Collision Avoidance*).

El proceso operativo típico sigue estos pasos: (1) recepción de un mensaje de efemérides de conjunción (CDM) del 18th Space Defense Squadron u otro proveedor de tracking; (2) propagación de ambas órbitas con mayor precisión y recálculo de la probabilidad de colisión; (3) si el riesgo se confirma, planificación de una pequeña maniobra (a menudo de solo unos cm/s a pocos m/s de $\Delta v$) que desplaza el punto de máxima aproximación fuera de la zona de riesgo sin alterar significativamente la misión operativa; (4) ejecución de la maniobra con horas o un día de anticipación. La Estación Espacial Internacional realiza en promedio 1 a 2 maniobras de este tipo por año, aunque constelaciones grandes como Starlink, al operar miles de satélites con propulsión eléctrica, ejecutan miles de maniobras de evasión autónomas anuales mediante sistemas automatizados de decisión a bordo.

## Mitigación: reglas de desorbitado

Las guías internacionales de mitigación de basura espacial (IADC, y adoptadas por la mayoría de agencias y reguladores nacionales) establecen que un satélite en LEO debe reentrar en la atmósfera dentro de los **25 años** posteriores al fin de su misión operativa (la llamada "regla de los 25 años"). En 2022, la FCC en Estados Unidos endureció este requisito para satélites bajo su jurisdicción, reduciéndolo a **5 años** tras el fin de misión, en respuesta al crecimiento explosivo de megaconstelaciones.

El cumplimiento se logra mediante dos estrategias:

- **Desorbitado activo**: uso del propelente remanente para bajar el perigeo hasta que el arrastre atmosférico complete la reentrada en el plazo objetivo, o reentrada controlada dirigida a una zona oceánica despoblada (para objetos grandes que podrían no desintegrarse completamente).
- **Órbita cementerio**: para satélites en GEO, donde no existe arrastre atmosférico que permita una reentrada natural, la práctica estándar es elevar la órbita unos 300 km por encima de GEO al final de la vida útil, liberando permanentemente la franja geoestacionaria operativa.

El cumplimiento voluntario de estas reglas ha sido históricamente parcial (con tasas de éxito de desorbitado post-misión en LEO reportadas por debajo del 50% en algunos periodos), lo que ha motivado el interés creciente en misiones de remoción activa de basura (ADR, *Active Debris Removal*), como la misión ClearSpace-1 de la ESA.

## Tracking terrestre

La vigilancia y catalogación de objetos orbitales depende de una red global de sensores: radares de gran potencia (como el sistema de radares de fase del Espacio de EE. UU.), telescopios ópticos terrestres (que solo pueden observar objetos iluminados por el Sol contra un cielo oscuro, típicamente al amanecer/atardecer) y, cada vez más, sensores espaciales dedicados. Esta información alimenta el catálogo público de elementos orbitales de dos líneas (TLE) que sustenta el software de propagación orbital usado por operadores de todo el mundo para el análisis de conjunción descrito arriba. La precisión de estos catálogos —típicamente de cientos de metros a kilómetros en la posición predicha, degradándose con el tiempo desde la última actualización— es la limitación fundamental que obliga a mantener márgenes de seguridad conservadores en las maniobras COLA.

## Ideas clave

- Solo se cataloga individualmente una fracción de la basura orbital (objetos > 10 cm); el resto —más de un millón de fragmentos entre 1 y 10 cm— se gestiona por riesgo estadístico.
- El síndrome de Kessler describe una reacción en cadena de colisiones autosostenida si la densidad orbital supera un umbral crítico; los eventos de 2007 y 2009 son ejemplos reales de generación masiva de fragmentos.
- Las maniobras COLA se activan cuando la probabilidad de colisión supera ~$10^{-4}$, con ajustes de $\Delta v$ típicamente pequeños pero decisivos.
- Las reglas de desorbitado exigen reentrada en 25 años (histórico) o 5 años (FCC, 2022) tras el fin de misión en LEO, y elevación a órbita cementerio en GEO.
- El tracking terrestre (radar y óptico) tiene precisión limitada, lo que obliga a mantener márgenes conservadores en la gestión del riesgo de colisión.

## Para seguir

La lección anterior, *Cohetes y acceso al espacio*, describió cómo llegan los objetos a estas órbitas; esta lección cierra el ciclo mostrando qué ocurre al final de su vida útil. La última lección de esta categoría, *Clima espacial y sus efectos*, muestra cómo la actividad solar también modula el arrastre atmosférico y, con ello, la velocidad natural de limpieza de estas órbitas.
