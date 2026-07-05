---
title: Redes no terrestres (NTN) en 6G
level: medio
summary: La integración satélite-celular desde 3GPP Rel-17 hasta 6G, direct-to-device, la arquitectura en capas LEO-HAPS-terrestre y los retos de Doppler y timing.
tags: [ntn, satelites, direct-to-device, leo, 3gpp]
minutes: 12
order: 5
---

## Objetivos

- Explicar qué son las redes no terrestres (NTN) y por qué 6G las integra como capa estructural.
- Describir la estandarización 3GPP NTN desde Rel-17 (NR-NTN e IoT-NTN) y su evolución hacia 6G.
- Comparar los enfoques de direct-to-device: espectro celular reutilizado (Starlink, AST) frente a espectro satelital (MSS).
- Analizar la arquitectura tridimensional LEO/HAPS/terrestre y los papeles de cada capa.
- Cuantificar los retos de capa física de NTN: Doppler, retardo, timing advance y presupuestos de enlace.

## De dos mundos separados a una sola red

Durante cinco décadas, las redes celulares y las satelitales evolucionaron como industrias paralelas con estándares, terminales y economías distintas: la telefonía satelital clásica (Iridium, Inmarsat, Thuraya) exigía terminales dedicados y costaba órdenes de magnitud más que la celular. Esa separación está terminando por convergencia de dos fuerzas. Desde el espacio, las megaconstelaciones LEO (vistas en la categoría de Satélites) abarataron radicalmente la capacidad en órbita: cientos de satélites con antenas de apertura grande y procesamiento a bordo, a 500–600 km en vez de 36 000. Desde tierra, el 3GPP decidió que el estándar celular hablaría también con satélites: las **redes no terrestres** (*Non-Terrestrial Networks*, NTN) entraron formalmente en la **Release 17** (2022), que adaptó NR (la radio de 5G) y NB-IoT/eMTC para funcionar a través de satélites GEO y LEO. Para 6G, la visión de IMT-2030 eleva la apuesta: la conectividad ubicua es uno de los seis escenarios de uso, y la integración terrestre-no terrestre deja de ser un complemento para volverse **principio de arquitectura** —una red tridimensional donde la capa que sirve a cada usuario en cada momento es una decisión del sistema, no una elección de suscripción.

El motivo económico es simple de enunciar: las redes terrestres cubren menos del 20% de la superficie del planeta (y ~40% de la población mundial carece aún de banda ancha significativa); extender fibra y torres a océanos, desiertos, montañas y zonas de baja densidad no tiene retorno. El satélite invierte la ecuación de costos: su cobertura es casi gratuita por km² adicional, y cara por bit por segundo —el complemento exacto de la red terrestre. Los casos que tiran de la demanda: eliminación de zonas muertas para mensajería y emergencias, IoT global (contenedores, agricultura, monitoreo ambiental), respaldo ante desastres que tumban la infraestructura terrestre, y conectividad marítima y aérea.

## La estandarización: Rel-17 a 6G

Rel-17 definió dos ramas. **NR-NTN**: el acceso 5G NR sobre satélites transparentes (el satélite es un repetidor curvado; el gNB queda en tierra tras la estación pasarela), en bandas satelitales L/S para terminales de mano y Ka para terminales con antena (VSAT, movilidad). **IoT-NTN**: NB-IoT/eMTC por satélite para sensores de baja tasa. Las adaptaciones esenciales fueron temporales: los temporizadores y ventanas de NR asumían distancias de decenas de km, no de miles (se introdujeron offsets de programación, el parámetro *K-offset*, y HARQ deshabilitable o ampliado). **Rel-18/19** (5G-Advanced) añadieron cobertura mejorada para terminales de mano, movilidad entre celdas satelitales y terrestres, satélites regenerativos en estudio y posicionamiento vía NTN. La hoja de ruta hacia **6G NTN** (Rel-20/21 en adelante) apunta a la integración plena: gestión de radio unificada multi-capa, satélites regenerativos con gNB a bordo y enlaces intersatelitales como *backhaul* espacial, y la promesa de que el usuario no sepa —ni le importe— qué capa lo sirve.

En paralelo corre la vía **direct-to-device (D2D)** con espectro celular reutilizado: satélites LEO que emiten en las bandas del operador móvil terrestre (con su acuerdo), hablando con teléfonos **sin modificar**. Starlink direct-to-cell (con T-Mobile en EE.UU. y operadores en varios países) inició servicio comercial de mensajería en 2024–2025; AST SpaceMobile demostró llamadas y datos con smartphones ordinarios con sus antenas desplegables de 64+ m². El contraste técnico con la vía 3GPP-NTN de banda satelital: reutilizar espectro celular exige del satélite antenas enormes (el presupuesto de enlace debe cerrar contra la antena diminuta y los ~200 mW del teléfono) y coordinación regulatoria fina (la FCC creó en 2024 el marco *Supplemental Coverage from Space*); a cambio, el mercado son los miles de millones de teléfonos existentes. Ambas vías convergerán en 6G: el estándar aspira a absorber el D2D como un modo más de la red tridimensional.

## La arquitectura en capas: LEO, HAPS y tierra

La red tridimensional de 6G se organiza por altitud, con cada capa aportando una combinación distinta de cobertura, latencia y capacidad:

| Capa | Altitud | RTT propagación | Celda típica | Papel |
|------|---------|-----------------|--------------|-------|
| Terrestre | 0 | <1 ms | 0.1–30 km | Capacidad masiva, latencia mínima |
| HAPS | ~20 km | ~0.3–0.5 ms | 50–100 km diámetro | Cobertura regional persistente, refuerzo de eventos/desastres |
| LEO | 500–1200 km | 7–17 ms (una vía ~2.5–4 ms/tramo) | 20–1000 km (haces) | Cobertura global, D2D, backhaul remoto |
| MEO/GEO | 8 000–36 000 km | 60–540 ms | Regional/continental | Difusión, backhaul de alta capacidad, resiliencia |

Las **HAPS** (*High-Altitude Platform Stations*) —globos estratosféricos, dirigibles o aeronaves solares de larga permanencia a ~20 km— ocupan el hueco entre torre y satélite: la distancia de un enlace urbano grande con la vista de un satélite pequeño, sin lanzamiento y con retorno a tierra para mantenimiento. Tras el cierre del proyecto Loon de Google (2021), el interés renació enfocado a HAPS como **estaciones base voladoras** (HIBS, *HAPS as IMT Base Station*, con espectro IMT identificado en la WRC-23): Airbus Zephyr y NTT/Space Compass en Japón apuntan a servicios comerciales en la segunda mitad de la década. Su nicho: cobertura persistente de áreas del tamaño de una provincia, refuerzo temporal (desastres, grandes eventos) y relé entre tierra y LEO.

El pegamento del sistema son los **enlaces intersatelitales** ópticos (ISL, vistos en la lección de megaconstelaciones) que convierten la capa LEO en una red de transporte espacial, y una gestión de recursos multi-capa: decidir por capa el tráfico según latencia requerida, densidad local y costo energético por bit —un problema de orquestación que la IA nativa de 6G (lección primera de esta categoría) reclama como caso de uso propio.

## La física del enlace móvil-satélite: Doppler y tiempo

Un satélite LEO a 550 km se mueve a ~7.6 km/s respecto al suelo, y esa velocidad domina la capa física de NTN. El **desplazamiento Doppler** es $\Delta f = f_0 \, v_r/c$: con componente radial máxima de ~7 km/s en los extremos del pase, a $f_0 = 2$ GHz resulta $\Delta f \approx \pm 47$ kHz (24 ppm), y a 20 GHz, ±470 kHz —enorme frente a los offsets que tolera OFDM entre subportadoras de 15–120 kHz. Además el Doppler *varía* durante el pase (máxima tasa de cambio cerca del cénit, cientos de Hz/s en banda S). La solución estandarizada aprovecha que la órbita es predecible: el satélite difunde sus **efemérides** en la información de sistema, y el terminal —que conoce su propia posición por GNSS— **precompensa** Doppler y retardo antes de transmitir, dejando al receptor solo el residuo.

El **timing advance** (TA) sufre la misma ampliación: en una celda terrestre el TA corrige microsegundos; en NTN, el retardo de ida y vuelta al satélite alcanza ~2–13 ms en LEO y ~540 ms en GEO transparente (los ~240 ms por tramo vistos en la categoría de Redes de Datos, ida y vuelta por dos tramos). Rel-17 lo resolvió con un **TA común** por celda difundido por la red (la parte compartida del retardo) más la autocompensación del terminal por GNSS de su parte específica, y con la extensión de todas las ventanas de proceso (RACH, HARQ, programación con K-offset). Quedan los retos abiertos que 6G debe pulir: **handover masivo y frecuente** (con satélites que cruzan el cielo en minutos, todos los usuarios de un haz cambian de satélite a la vez, favoreciendo el *handover condicional* precalculado sobre la señalización individual), la dependencia de GNSS del esquema actual (vulnerable a interferencia y denegación), la gestión de haces móviles contra celdas fijas en tierra (*earth-fixed beams* que se reorientan durante el pase frente a *earth-moving beams*), y los presupuestos de enlace D2D que fuerzan tasas modestas hacia el teléfono de mano —mensajería y voz primero, banda ancha después.

## Ideas clave

- NTN integra satélites y HAPS en el estándar celular: Rel-17 adaptó NR y NB-IoT a GEO/LEO, Rel-18/19 mejoran terminal de mano y movilidad, y 6G eleva la integración a principio de arquitectura (conectividad ubicua de IMT-2030).
- Dos vías convergentes hacia el teléfono común: NTN 3GPP en bandas satelitales L/S y D2D en espectro celular reutilizado (Starlink direct-to-cell, AST SpaceMobile), este último a costa de antenas satelitales enormes.
- La red tridimensional reparte papeles por altitud: tierra (capacidad y latencia), HAPS a ~20 km (cobertura regional persistente, HIBS), LEO (cobertura global y backhaul con ISL ópticos), GEO (difusión y resiliencia).
- La física del LEO domina el diseño: Doppler de decenas de ppm y retardos de ms que se precompensan con efemérides difundidas + GNSS del terminal, TA común por celda y ventanas de protocolo extendidas.
- Retos abiertos para 6G: handovers masivos por el paso de satélites, dependencia de GNSS, haces fijos en tierra frente a haces móviles, y presupuestos de enlace D2D que limitan la banda ancha al teléfono.

## Para seguir

Con esta lección cierra la categoría de Redes 6G, enlazada con *Megaconstelaciones LEO* (categoría Satélites) y *Comunicaciones por satélite* para la física del enlace. La categoría *Inteligencia Artificial* abre el siguiente bloque de la biblioteca: los fundamentos de la IA moderna que 6G asume como componente nativo.
