---
title: Geometría de apuntamiento
level: intro
summary: Azimut, elevación, ángulo de elevación mínimo y radio de huella determinan cuándo y hacia dónde apuntar una estación terrena a un satélite visible.
tags: [azimut-elevacion, huella, visibilidad, pases]
minutes: 7
order: 1
---

## Objetivos

- Definir azimut y elevación como coordenadas topocéntricas que ubican un satélite desde una estación terrena.
- Explicar por qué existe un ángulo de elevación mínimo operativo y qué lo determina.
- Calcular el radio de la huella (footprint) visible desde un satélite a una altitud dada.
- Estimar la duración típica de un pase en órbita baja.
- Relacionar la geometría de apuntamiento con el diseño de una constelación de cobertura.

## Azimut y elevación: coordenadas topocéntricas

Desde el punto de vista de una antena en tierra, la posición de un satélite se describe de forma más natural no con coordenadas orbitales (como en las lecciones de Dinámica Orbital) sino con un sistema **topocéntrico**, centrado en la propia estación: el **azimut** ($Az$), el ángulo medido en el plano horizontal desde el norte geográfico hacia el este (0° = norte, 90° = este, 180° = sur, 270° = oeste) hasta la proyección del satélite sobre el horizonte, y la **elevación** ($El$), el ángulo entre el horizonte local y la línea de vista al satélite (0° = en el horizonte, 90° = en el cénit, directamente sobre la estación). Junto con el rango (la distancia en línea recta), estas dos coordenadas angulares bastan para apuntar físicamente cualquier antena direccional: es exactamente lo que mueve un rotor de seguimiento o lo que un operador introduce manualmente en una montura azimut-elevación.

Estas coordenadas se calculan a partir de la posición del satélite (en un sistema inercial o terrestre) y de la posición geográfica de la estación mediante rotaciones esféricas estándar, un procedimiento que se detalla en la lección de sistemas de referencia; aquí basta con asumir que, para cualquier instante, existe una transformación bien definida órbita → (Az, El, rango).

## El ángulo de elevación mínimo

Ningún sistema de seguimiento apunta hasta $El = 0°$ en la práctica. Existe siempre un **ángulo de elevación mínimo operativo** $\varepsilon$, típicamente entre $5°$ y $10°$, por varias razones físicas simultáneas: cerca del horizonte, la señal atraviesa un espesor de atmósfera mucho mayor (la masa de aire crece aproximadamente como $1/\sin\varepsilon$), lo que incrementa la atenuación atmosférica y el ruido; los obstáculos del terreno circundante (edificios, colinas, vegetación) suelen bloquear físicamente la línea de vista a baja elevación; y el multitrayecto —la señal reflejada en el suelo o en estructuras cercanas, que interfiere con la señal directa— es mucho más severo a baja elevación. Bandas de frecuencia más altas (Ka, por ejemplo), más sensibles a la atenuación atmosférica y a la lluvia, suelen operar con elevaciones mínimas mayores que las bandas más bajas (S o L). Este ángulo mínimo, no la línea de visión geométrica pura, es el que en la práctica determina si un satélite es "visible y utilizable" desde una estación dada en un instante concreto.

## Radio de la huella (footprint)

La región de la superficie terrestre desde la cual un satélite es visible por encima de un ángulo de elevación mínimo $\varepsilon$ se llama **huella** o *footprint*, y su extensión se puede calcular con geometría esférica simplificada (Tierra esférica, sin relieve). Definiendo $R_\oplus$ como el radio terrestre y $h$ la altitud del satélite, el radio angular de la huella, medido como ángulo central geocéntrico $\lambda$ desde el punto subsatelital, es

$$\lambda = \arccos\left(\frac{R_\oplus}{R_\oplus+h}\cos\varepsilon\right) - \varepsilon$$

y el radio de la huella medido sobre la superficie terrestre (distancia de arco) es simplemente $\rho = R_\oplus\,\lambda$, con $\lambda$ expresado en radianes:

$$\rho = R_\oplus\left[\arccos\left(\frac{R_\oplus}{R_\oplus+h}\cos\varepsilon\right) - \varepsilon\right]$$

Como ejemplo numérico, para un satélite LEO a $h = 550$ km (la altitud típica de constelaciones como Starlink) y una elevación mínima de $\varepsilon = 10°$: con $R_\oplus = 6378$ km, la razón $R_\oplus/(R_\oplus+h) = 0.9206$; multiplicando por $\cos 10° = 0.9848$ se obtiene $0.9067$, cuyo arco coseno es aproximadamente $25.0°$ ($0.436$ rad); restando $\varepsilon = 10°$ ($0.175$ rad) queda $\lambda \approx 15.0°$ ($0.262$ rad), y el radio de huella resulta $\rho \approx 6378 \times 0.262 \approx 1670$ km. Nótese que exigir una elevación mínima más alta (por ejemplo $\varepsilon = 25°$ para enlaces Ka más exigentes) reduce considerablemente esta huella, porque el término $\varepsilon$ resta directamente y el arco coseno también se reduce.

## Duración de un pase en órbita baja

La combinación de la velocidad angular orbital (un satélite LEO recorre $360°$ en apenas 90–100 minutos) con el radio de huella limitado en LEO produce **pases** de corta duración: el intervalo en que el satélite permanece por encima del ángulo de elevación mínimo desde una estación dada. Para $h = 550$ km y $\varepsilon = 10°$, un pase que pasa cerca del cénit de la estación dura entre unos 8 y 12 minutos; un pase que apenas roza el horizonte a baja elevación máxima puede durar solo 2–4 minutos. En GEO, por contraste, un satélite es —por definición— visible de forma continua las 24 horas del día desde cualquier punto dentro de su huella, siempre que la elevación resultante supere el mínimo operativo (lo que en la práctica descarta las latitudes muy altas, donde un satélite GEO aparece por debajo del horizonte o a elevación demasiado baja para uso confiable).

Esta brevedad de los pases en LEO es la razón estructural detrás de dos decisiones de diseño recurrentes en la industria: por un lado, las constelaciones de comunicaciones LEO necesitan decenas o cientos de satélites para garantizar que, en todo momento, al menos uno esté visible desde cualquier punto; por otro, las estaciones terrenas que dan servicio a satélites LEO individuales (por ejemplo, de observación de la Tierra) deben transferir todos sus datos durante esa ventana de pocos minutos, lo que impone requisitos estrictos de velocidad de enlace descendente.

## Ideas clave

- Azimut y elevación son las coordenadas topocéntricas naturales para apuntar una antena; junto con el rango, ubican completamente un satélite desde una estación.
- El ángulo de elevación mínimo operativo (típicamente 5°–10°) no es arbitrario: refleja atenuación atmosférica, obstrucción del terreno y multitrayecto, y crece con la frecuencia de operación.
- El radio de huella $\rho = R_\oplus[\arccos((R_\oplus/(R_\oplus+h))\cos\varepsilon) - \varepsilon]$ crece con la altitud del satélite y se reduce al exigir mayor elevación mínima.
- Un pase LEO típico dura entre 2 y 12 minutos, mientras que un satélite GEO es visible continuamente dentro de su huella.
- La brevedad de los pases LEO obliga a constelaciones numerosas para cobertura continua y a enlaces descendentes de alta velocidad para aprovechar la ventana disponible.

## Para seguir

La siguiente lección, *Sistemas de referencia y actitud*, formaliza la transformación entre los sistemas de coordenadas orbitales y topocéntricos usados aquí, y añade los sistemas de referencia necesarios para describir la orientación (actitud) del propio satélite.
