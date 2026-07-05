---
title: Medios de transmisión
level: intro
summary: Par trenzado, coaxial, fibra óptica y radioenlace ofrecen compromisos distintos de capacidad, alcance y costo para transportar señales.
tags: [fibra-optica, cobre, radioenlace, wdm, atenuacion]
minutes: 10
order: 3
---

## Objetivos

- Describir el par trenzado y sus categorías normalizadas de cableado estructurado.
- Describir el cable coaxial y sus aplicaciones características frente al par trenzado.
- Explicar la fibra óptica monomodo y multimodo, su atenuación en dB/km y el multiplexado por longitud de onda (WDM).
- Explicar el concepto de radioenlace y su balance de potencia.
- Comparar cuantitativamente capacidad, alcance y costo de los cuatro medios.

## Par trenzado

El **par trenzado** (*twisted pair*) es el medio de cableado más común en redes de datos y telefonía: dos conductores de cobre trenzados entre sí, un diseño que cancela en gran medida el ruido electromagnético inducido por fuentes externas (porque el ruido induce una tensión casi idéntica en ambos hilos, que se cancela al medir la diferencia entre ellos) y reduce la diafonía (*crosstalk*) entre pares adyacentes dentro del mismo cable. La norma TIA/EIA-568 define **categorías** de cable UTP (*Unshielded Twisted Pair*) con ancho de banda y prestaciones crecientes: Cat 5e soporta hasta 1 Gbit/s a 100 MHz de ancho de banda certificado; Cat 6 soporta 1 Gbit/s con más margen (y 10 Gbit/s hasta 55 m) a 250 MHz; Cat 6A soporta 10 Gbit/s a 100 m con 500 MHz; y Cat 8, pensada para centros de datos con enlaces cortos, soporta hasta 40 Gbit/s a distancias de apenas 30 m con 2000 MHz de ancho de banda. El par trenzado es económico, fácil de instalar y terminar en campo, pero su alcance práctico sin repetidores está limitado a unos 100 m por las especificaciones Ethernet estándar, y su inmunidad al ruido, aunque buena, es inferior a la de la fibra.

## Cable coaxial

El **cable coaxial** consiste en un conductor central rodeado por un dieléctrico aislante, una malla o lámina conductora de blindaje, y una cubierta exterior, geometría que confina el campo electromagnético casi por completo dentro del cable, ofreciendo mucha mejor inmunidad al ruido y a la interferencia que el par trenzado, y anchos de banda considerablemente mayores. Fue el medio dominante en las primeras redes Ethernet (10BASE2, 10BASE5) y sigue siendo el medio de las redes de televisión por cable (CATV) y de acceso a Internet por cable (DOCSIS), donde un único cable coaxial troncal, alimentado por fibra óptica hasta un nodo local (arquitectura HFC, *Hybrid Fiber-Coax*), distribuye cientos de megahercios de espectro de RF compartido entre decenas de canales de televisión y de datos a los hogares de un vecindario. Su desventaja frente a la fibra es la atenuación, mucho mayor por unidad de longitud a frecuencias altas, y frente al par trenzado, un costo y una rigidez mecánica mayores que dificultan su instalación en distribución horizontal masiva dentro de edificios.

## Fibra óptica: monomodo, multimodo y atenuación

La **fibra óptica** transporta información como pulsos de luz (típicamente infrarroja, en las ventanas de 850, 1310 o 1550 nm) guiados por reflexión interna total dentro de un núcleo de vidrio de índice de refracción ligeramente mayor que el del revestimiento circundante. La **fibra multimodo** (MMF) tiene un núcleo relativamente ancho (50 o 62.5 µm) que permite que la luz se propague por múltiples trayectorias (modos) simultáneamente; esto es más barato de fabricar y de acoplar a fuentes de luz económicas (LED o VCSEL), pero introduce **dispersión modal** —los distintos modos recorren longitudes de camino ligeramente distintas y llegan en instantes distintos— que ensancha los pulsos y limita el producto ancho de banda × distancia, restringiendo su uso práctico a enlaces cortos (típicamente cientos de metros a pocos kilómetros) dentro de centros de datos o campus. La **fibra monomodo** (SMF) tiene un núcleo mucho más estrecho (~9 µm), suficientemente angosto para que solo se propague un único modo, eliminando la dispersión modal y permitiendo distancias de decenas a cientos de kilómetros sin repetidor, a costa de requerir fuentes láser más precisas y costosas (y tolerancias de acoplamiento más estrictas). Es el medio universal de las redes troncales de larga distancia y de los cables submarinos intercontinentales.

La **atenuación** de la fibra se mide en dB/km y depende fuertemente de la longitud de onda: la fibra monomodo estándar (ITU-T G.652) atenúa aproximadamente 0.35 dB/km en la ventana de 1310 nm y apenas 0.2 dB/km en la ventana de 1550 nm (el mínimo de atenuación de la sílice, la razón por la que las redes de larga distancia operan preferentemente en esa banda). Un enlace de 100 km a 0.2 dB/km acumula 20 dB de pérdida solo por atenuación de fibra, antes de sumar pérdidas de empalme y conector —cifra que un presupuesto de enlace óptico debe cubrir con la potencia del láser transmisor y la sensibilidad del receptor, o compensar con amplificadores ópticos (EDFA) intermedios.

El **multiplexado por división en longitud de onda** (WDM, *Wavelength Division Multiplexing*) multiplica la capacidad de una única fibra transmitiendo simultáneamente muchas longitudes de onda distintas, cada una modulada de forma independiente, sobre el mismo núcleo físico. **CWDM** (*Coarse* WDM) usa un espaciado ancho entre canales (20 nm), típicamente 8 a 18 canales, adecuado para redes metropolitanas de menor costo; **DWDM** (*Dense* WDM) usa espaciados muy estrechos (0.8, 0.4 o incluso 0.2 nm, según la rejilla ITU), permitiendo 40, 80 o más de 160 canales sobre la misma fibra, cada uno operando a decenas o cientos de gigabits por segundo, la tecnología que sostiene la capacidad agregada de terabits por segundo de los cables submarinos y las redes troncales globales.

## Radioenlace y su balance de potencia

Un **radioenlace** transmite información mediante ondas electromagnéticas radiadas por una antena, sin medio físico guiado, ya sea en enlaces punto a punto terrestres (microondas), enlaces satelitales o redes celulares y Wi-Fi. Su viabilidad se evalúa mediante un **presupuesto de enlace** (link budget), que suma en decibelios la potencia transmitida, las ganancias de las antenas transmisora y receptora, y resta las pérdidas de propagación (que crecen con la distancia y la frecuencia, según la ley de espacio libre) y de otros factores atmosféricos, para determinar la potencia que finalmente llega al receptor, comparada con su sensibilidad mínima requerida. A diferencia de un medio guiado, el radioenlace comparte el medio de propagación con cualquier otro transmisor en la misma banda y área geográfica, lo que exige una gestión regulada del espectro (asignación de bandas de frecuencia por parte de organismos como la UIT y los reguladores nacionales) para evitar interferencias mutuas, y su capacidad efectiva depende críticamente de las condiciones atmosféricas instantáneas (lluvia, especialmente en bandas Ku y Ka) de un modo que los medios guiados, protegidos dentro de un cable o una fibra, no experimentan.

## Comparativa de medios

| Medio | Capacidad típica | Alcance sin repetidor | Costo relativo | Inmunidad al ruido |
|---|---|---|---|---|
| Par trenzado (Cat 6A) | 10 Gbit/s | ~100 m | Bajo | Media |
| Coaxial (DOCSIS) | Hasta ~10 Gbit/s compartido | Varios km (con amplificadores) | Medio | Alta |
| Fibra monomodo + DWDM | Terabits/s agregados | Decenas a cientos de km | Medio-alto (instalación) | Muy alta |
| Radioenlace de microondas | Hasta unos Gbit/s por canal | Decenas de km (línea de vista) | Variable (sin obra civil) | Baja (afectada por clima e interferencia) |

Esta tabla resume el patrón estructural de la elección de medio en cualquier diseño de red real: la fibra domina en capacidad y alcance para troncales y backbone; el cobre (par trenzado o coaxial) domina la última milla de bajo costo hacia el usuario final donde la distancia es corta; y el radioenlace resuelve los casos donde tender un medio físico es costoso, lento o imposible —terreno difícil, movilidad del usuario, o el vacío del espacio entre una estación terrena y un satélite.

## Ideas clave

- El par trenzado, normado en categorías Cat 5e a Cat 8, domina el cableado estructurado de corto alcance por su bajo costo y facilidad de instalación.
- El cable coaxial ofrece mejor inmunidad al ruido y mayor ancho de banda que el par trenzado, y sigue siendo la base de las redes HFC de televisión y acceso por cable.
- La fibra monomodo elimina la dispersión modal de la multimodo y permite distancias de decenas a cientos de km, con atenuaciones tan bajas como 0.2 dB/km en la ventana de 1550 nm.
- El WDM (CWDM/DWDM) multiplica la capacidad de una fibra transmitiendo muchas longitudes de onda simultáneas, sosteniendo las redes troncales de capacidad terabit.
- El radioenlace evita la necesidad de un medio físico guiado a costa de compartir espectro, depender de condiciones atmosféricas, y requerir una gestión regulatoria de frecuencias.

## Para seguir

La siguiente lección, *Redes celulares: de 1G a 5G*, muestra cómo el radioenlace se organiza en un sistema celular completo, combinando reuso de frecuencia, arquitectura de red y evolución de las técnicas de modulación vistas en la lección anterior.
