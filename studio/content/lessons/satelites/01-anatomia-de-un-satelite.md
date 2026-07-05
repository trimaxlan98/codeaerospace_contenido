---
title: Anatomía de un satélite
level: intro
summary: La distinción entre bus y carga útil, los subsistemas esenciales de una nave y cómo se reparten sus presupuestos de masa y potencia.
tags: [satelite, bus, subsistemas, adcs, presupuesto-masa]
minutes: 8
order: 1
---

## Objetivos

- Distinguir el bus (plataforma) de la carga útil (payload) en un satélite.
- Describir la función de cada subsistema esencial: EPS, TT&C, ADCS, propulsión, térmico, estructura y OBC.
- Entender cómo se elabora un presupuesto de masa y de potencia en la fase de diseño.
- Reconocer las interdependencias entre subsistemas que hacen del diseño satelital un ejercicio de compromisos (trade-offs).

## Bus vs. carga útil

Todo satélite se divide conceptualmente en dos partes con propósitos muy distintos:

- La **carga útil (payload)** es el conjunto de instrumentos que cumplen el propósito de la misión: una cámara óptica, un radar de apertura sintética, un transpondedor de comunicaciones, un receptor científico. Es lo que "vende" la misión.
- El **bus** (o plataforma) es todo lo demás: la infraestructura que mantiene viva, orientada, alimentada y comunicada a la carga útil. Incluye estructura, energía, control térmico, control de actitud, propulsión, y la computadora de a bordo con su enlace de telemetría y comando.

En satélites pequeños, la frontera entre bus y payload puede ser difusa (comparten computadora, por ejemplo); en misiones grandes, ambos se diseñan y a veces se contratan de forma independiente, con una interfaz mecánica y eléctrica bien definida entre ellos. El bus suele representar entre el 40% y el 70% de la masa total del satélite, dependiendo de cuán exigente sea la carga útil en potencia, apuntamiento o refrigeración.

## Los subsistemas del bus

**EPS (Electrical Power Subsystem)**: genera, almacena y distribuye energía. Se compone de paneles solares (fotovoltaicos, con celdas de triple unión de arseniuro de galio de eficiencias del 28-32% en misiones modernas), baterías (predominantemente de ion-litio hoy en día, que almacenan energía para los periodos de eclipse) y electrónica de regulación y distribución de potencia (PCDU). El dimensionamiento debe cubrir tanto la potencia pico durante operaciones de la carga útil como la carga de batería suficiente para sobrevivir el eclipse más largo de la misión.

**TT&C (Telemetry, Tracking & Command)**: el enlace de radio que permite al centro de control conocer el estado de salud del satélite (telemetría), determinar su posición (tracking, mediante medidas de rango y Doppler) y enviarle instrucciones (comandos). Opera típicamente en bandas S o X con antenas de baja ganancia (casi omnidireccionales) para garantizar contacto incluso si el satélite pierde el apuntamiento fino, siendo el enlace más crítico de todos: sin TT&C, no hay forma de recuperar una anomalía.

**ADCS (Attitude Determination and Control Subsystem)**: determina y controla la orientación del satélite en el espacio. Usa sensores (giróscopos, sensores de Sol, sensores de estrellas/*star trackers*, magnetómetros) para determinar la actitud, y actuadores (ruedas de reacción, magnetopares, propulsores) para corregirla. La precisión de apuntamiento requerida varía enormemente: desde décimas de grado para un satélite de comunicaciones hasta milésimas de grado (o mejor) para un telescopio espacial o un satélite de observación de alta resolución.

**Propulsión**: provee el $\Delta v$ para maniobras de inserción orbital, mantenimiento de estación, desaturación de ruedas de reacción y desorbitado al fin de misión. Puede ser química (empuje alto, eficiencia moderada) o eléctrica (empuje muy bajo pero eficiencia varias veces mayor, medida en impulso específico), como se detalla en la lección de comunicaciones y en la de megaconstelaciones.

**Subsistema térmico**: mantiene todos los componentes dentro de sus rangos de temperatura operativos pese a los ciclos extremos de eclipse/iluminación descritos en la primera categoría de este curso. Combina elementos pasivos (mantas MLI, recubrimientos, radiadores) y activos (calentadores resistivos controlados por termostato o por software).

**Estructura**: el chasis mecánico que soporta todos los demás subsistemas y la carga útil, diseñado para sobrevivir las cargas dinámicas del lanzamiento (vibración, choque de separación de etapas, aceleración) sin transmitir esas cargas de forma dañina a los componentes sensibles.

**OBC (On-Board Computer)**: el "cerebro" del satélite, que ejecuta el software de vuelo: gestión de subsistemas, ejecución de secuencias autónomas, procesamiento de telemetría, y en misiones modernas, procesamiento de datos de la carga útil a bordo antes de transmitirlos a tierra.

## Presupuestos de masa y potencia

El diseño de un satélite se rige por dos "libros de contabilidad" que se iteran constantemente durante el desarrollo: el **presupuesto de masa** y el **presupuesto de potencia**.

Un presupuesto de masa típico para un satélite de tamaño mediano podría distribuirse así:

| Subsistema | % de masa típico |
|---|---|
| Estructura y mecanismos | 15-25% |
| EPS (paneles + baterías) | 15-25% |
| Propulsión (seca + propelente) | 10-30% (muy variable según misión) |
| ADCS | 5-10% |
| TT&C y OBC | 5-8% |
| Térmico | 3-6% |
| Carga útil | 15-40% |
| Margen de contingencia | 10-20% |

El margen de contingencia es crucial: en fases tempranas de diseño se reserva un margen alto (20-30%) sobre las estimaciones de masa de cada subsistema, que se reduce progresivamente conforme el diseño madura y se aproxima al lanzamiento, para absorber sorpresas de ingeniería sin comprometer la capacidad del lanzador contratado.

El presupuesto de potencia sigue una lógica similar, pero debe balancearse en el tiempo: la potencia generada por los paneles solares (que varía con el ángulo de incidencia solar y decae con la degradación por radiación a lo largo de la vida útil) debe cubrir la suma de consumos de todos los subsistemas en cada modo operativo (por ejemplo, "modo de imaging" puede exigir mucha más potencia que "modo de espera"), más las pérdidas de conversión y la recarga de batería necesaria para sobrevivir el siguiente eclipse.

## Interdependencias y compromisos de diseño

Ningún subsistema se diseña de forma aislada. Aumentar la potencia de un instrumento de carga útil incrementa el área de paneles solares necesaria, lo que aumenta la masa y el par de perturbación aerodinámico/de presión de radiación, lo que exige actuadores ADCS más capaces (o más propelente para desaturación), lo que a su vez consume masa que podría haberse asignado a la carga útil. Este tipo de ciclos de retroalimentación es la razón por la que el diseño de satélites es un proceso iterativo de ingeniería concurrente, donde los equipos de cada subsistema negocian constantemente presupuestos de masa, potencia, datos y apuntamiento en reuniones de integración de sistema.

## Ideas clave

- El bus sostiene a la carga útil: provee energía, orientación, comunicación, temperatura estable y estructura, pero no cumple por sí mismo el propósito de la misión.
- TT&C es el subsistema más crítico desde la perspectiva de recuperación de anomalías: sin él, no hay forma de diagnosticar ni comandar el satélite.
- ADCS combina sensores de determinación (giróscopos, star trackers, sensores de Sol) con actuadores de control (ruedas de reacción, magnetopares, propulsores).
- Los presupuestos de masa y potencia se iteran durante todo el desarrollo, con márgenes de contingencia que se reducen conforme madura el diseño.
- El diseño satelital es inherentemente interdependiente: un cambio en un subsistema se propaga en cascada al resto.

## Para seguir

La siguiente lección, *Órbitas y familias de satélites*, muestra cómo la órbita elegida condiciona directamente los requisitos de cada uno de estos subsistemas (por ejemplo, el perfil térmico y de radiación difiere radicalmente entre LEO y GEO). Más adelante, *Comunicaciones por satélite* profundiza en el diseño del enlace TT&C y de la carga útil de comunicaciones introducidos aquí.
