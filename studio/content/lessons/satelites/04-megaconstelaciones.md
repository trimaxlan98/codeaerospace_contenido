---
title: Megaconstelaciones LEO
level: medio
summary: Starlink, OneWeb y Kuiper en cifras, los enlaces inter-satelitales láser, el handover entre satélites y sus retos regulatorios y astronómicos.
tags: [megaconstelaciones, starlink, isl, handover, latencia]
minutes: 9
order: 4
---

## Objetivos

- Conocer las cifras clave (número de satélites, altitud, capacidad) de las principales megaconstelaciones LEO.
- Entender el propósito y funcionamiento de los enlaces inter-satelitales (ISL) láser.
- Explicar cómo funciona el handover entre satélites en una constelación en movimiento constante.
- Comparar cuantitativamente la latencia de LEO frente a GEO.
- Identificar los principales retos regulatorios y de astronomía observacional que plantean estas constelaciones.

## Starlink, OneWeb y Kuiper en cifras

Las megaconstelaciones de banda ancha en órbita baja han transformado la escala de la industria satelital en menos de una década:

| Constelación | Operador | Altitud típica | Satélites (aprox., 2025-2026) | Objetivo final autorizado |
|---|---|---|---|---|
| Starlink | SpaceX | ~340-570 km (múltiples capas) | > 7000 activos | Hasta 12 000 (fase 1-2), solicitud de hasta 42 000 |
| OneWeb (Eutelsat OneWeb) | Eutelsat | ~1200 km | ~630 (constelación inicial completa) | Ampliaciones en evaluación |
| Project Kuiper | Amazon | ~590-630 km | Despliegue inicial en curso | 3236 autorizados por la FCC |

Estas cifras contrastan radicalmente con la era anterior de comunicaciones satelitales, dominada por unas pocas docenas de satélites GEO grandes y costosos. La lógica de las megaconstelaciones es inversa: muchos satélites relativamente pequeños y económicos (producidos en serie, a un ritmo de varias unidades por día en el caso de Starlink), reemplazados con más frecuencia (vida útil de diseño de 5-7 años frente a 15-20 años en GEO), que en conjunto ofrecen baja latencia y cobertura casi global, incluyendo regiones oceánicas y polares donde la infraestructura terrestre es inviable.

## Enlaces inter-satelitales (ISL) láser

Un satélite LEO individual solo está en contacto directo con una estación terrena mientras esta se encuentra dentro de su huella de visibilidad, un intervalo de pocos minutos por pasada. Para ofrecer conectividad continua sin depender de una estación terrena en cada punto de la ruta, las constelaciones modernas incorporan **enlaces inter-satelitales (ISL)** que permiten a un satélite retransmitir tráfico a otro satélite vecino directamente en el espacio, sin bajar la señal a tierra en cada salto.

Los ISL de generación actual usan **enlaces láser ópticos** en vez de radiofrecuencia, por varias razones: (1) el vacío del espacio no tiene atmósfera que atenúe o disperse la luz, eliminando el problema de rain fade que limita los enlaces de radio en banda Ka; (2) la frecuencia óptica (cientos de THz) permite anchos de banda enormes —del orden de decenas a cientos de Gbps por enlace— con antenas (telescopios) mucho más compactas que las requeridas por RF equivalente; (3) al no usar espectro radioeléctrico regulado, evitan la necesidad de coordinación de frecuencias entre operadores. Starlink ha desplegado láseres ISL capaces de enlazar satélites separados por miles de kilómetros, incluyendo enlaces entre planos orbitales distintos, formando efectivamente una red troncal óptica en órbita que permite rutear tráfico de un lado del planeta al otro (por ejemplo, sobre el océano o regiones polares) sin tocar tierra en el trayecto intermedio.

## Handover entre satélites

Como cada satélite LEO se mueve a ~7.5 km/s respecto a la superficie terrestre, un terminal de usuario en tierra debe cambiar de satélite servidor cada pocos minutos conforme el satélite actual se aleja del horizonte y uno nuevo aparece. Este proceso de **handover** debe ser transparente para el usuario final, similar en espíritu al handover celular entre torres de telefonía móvil, pero mucho más frecuente (cada 2-4 minutos en vez de ocasional).

El terminal de usuario (una antena electrónicamente orientable, sin partes móviles, que forma un haz mediante arreglo en fase) mantiene simultáneamente el rastreo de la posición predicha de varios satélites candidatos usando efemérides transmitidas por la red, y conmuta al siguiente satélite antes de que el enlace actual se degrade por bajo ángulo de elevación. La constelación en su conjunto gestiona este ballet mediante un sistema de gestión de red centralizado que decide, en tiempo casi real, qué satélite sirve a qué celda de cobertura en cada instante, coordinando también los ISL para mantener rutas de extremo a extremo coherentes mientras la topología física cambia constantemente.

## Latencia: LEO frente a GEO

La ventaja distintiva de las megaconstelaciones LEO es la latencia. El límite físico teórico para un solo salto (ida) es la distancia dividida entre la velocidad de la luz:

- **LEO (~550 km de altitud)**: distancia mínima (paso por el cenit) de ~550 km, hasta ~1500-2000 km en pasadas de bajo ángulo de elevación. Latencia de un salto de ida: aproximadamente **1.8-6 ms**. Sumando procesamiento en satélite y terminal, un RTT (ida y vuelta) típico observado en servicio real de Starlink es de **20-40 ms**.
- **GEO (35 786 km de altitud)**: distancia fija de la estación terrena al satélite. Latencia de un salto de ida: **~119 ms** ($35\,786\,000\ \text{m} / 3\times10^8\ \text{m/s} \approx 0.119\ \text{s}$). Un tramo de ida y vuelta entre tierra y satélite (usuario-satélite-tierra) introduce aproximadamente **~240 ms**. Un enlace completo de ida y vuelta a través de un satélite GEO (usuario-satélite-hub-satélite-usuario, si el hub está en tierra) requiere cuatro saltos, dando un **RTT teórico mínimo de aproximadamente 480 ms**, y en la práctica bordea o supera los 500-600 ms si se cuenta procesamiento y enrutamiento terrestre adicional.

Esta diferencia de un orden de magnitud es la razón por la que LEO ha capturado aplicaciones sensibles a la latencia (videollamadas, gaming en línea, trading financiero) que GEO estructuralmente no puede servir bien, sin importar cuánto mejore su ancho de banda o modulación: es una limitación de la velocidad de la luz, no de ingeniería.

## Retos regulatorios y astronómicos

El despliegue de decenas de miles de satélites plantea desafíos que van más allá de la ingeniería:

- **Coordinación de espectro y órbitas**: la UIT y los reguladores nacionales (como la FCC) deben arbitrar solicitudes de espectro que se superponen entre operadores competidores, y gestionar la coordinación de interferencia entre sistemas que comparten banda Ku/Ka.
- **Gestión de tráfico orbital**: la simple cantidad de objetos activos multiplica el número de conjunciones que deben evaluarse diariamente (ver la lección de basura espacial), obligando a sistemas de maniobra de evasión automatizados a escala.
- **Contaminación lumínica astronómica**: los satélites de estas constelaciones, especialmente poco después del lanzamiento y en las primeras horas tras el atardecer o antes del amanecer (cuando aún reflejan luz solar sobre un cielo ya oscuro en tierra), aparecen como rastros brillantes en observaciones astronómicas de larga exposición, degradando datos de sondeos como el Vera C. Rubin Observatory. SpaceX ha implementado mitigaciones como recubrimientos antirreflectantes y visores solares desplegables (*VisorSat*) para reducir el brillo aparente de sus satélites, con resultados parciales.
- **Radioastronomía**: las emisiones de banda Ku/Ka y, en menor medida, las bandas de ISL, requieren coordinación con observatorios de radioastronomía para evitar interferencia en bandas protegidas.

## Ideas clave

- Starlink supera ya los 7000 satélites activos, con autorización para escalar a decenas de miles; OneWeb y Kuiper operan en escalas de cientos a miles.
- Los ISL láser eliminan la dependencia de estaciones terrenas intermedias y evitan el rain fade, a cambio de requerir apuntamiento óptico de alta precisión entre satélites en movimiento relativo.
- El handover entre satélites ocurre cada 2-4 minutos por terminal, gestionado mediante antenas en fase sin partes móviles y coordinación de red centralizada.
- La latencia RTT de LEO (20-40 ms) es un orden de magnitud menor que la de GEO (~250-600 ms), una ventaja estructural insalvable para GEO en aplicaciones interactivas.
- El crecimiento de estas constelaciones exige nueva coordinación regulatoria de espectro y plantea un reto real, aún sin solución completa, para la astronomía de superficie.

## Para seguir

La última lección de esta categoría, *CubeSats y NewSpace*, explora el otro extremo de la miniaturización satelital: misiones aún más pequeñas y económicas que comparten muchas de las lógicas de producción en serie descritas aquí para las megaconstelaciones.
