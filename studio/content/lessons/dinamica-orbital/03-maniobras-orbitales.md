---
title: Maniobras orbitales
level: medio
summary: La ecuación de vis-viva y las transferencias de Hohmann, bielíptica y de cambio de plano cuantifican el coste en delta-v de moverse entre órbitas.
tags: [maniobras-orbitales, hohmann, delta-v, vis-viva, rendezvous]
minutes: 8
order: 3
---

## Objetivos

- Deducir y aplicar la ecuación de vis-viva para calcular velocidad orbital en cualquier punto de una órbita.
- Calcular el $\Delta v$ total de una transferencia de Hohmann entre dos órbitas circulares coplanares.
- Calcular el coste en $\Delta v$ de un cambio de plano orbital puro.
- Explicar cuándo una transferencia bielíptica resulta más eficiente que una Hohmann directa.
- Describir las fases básicas de un rendezvous orbital.

## La ecuación de vis-viva

Toda maniobra orbital se diseña en torno a una sola relación, la ecuación de **vis-viva** ("fuerza viva", nombre histórico del siglo XVIII para la energía cinética), que da la velocidad instantánea de un cuerpo en cualquier punto de una órbita kepleriana conociendo solo su distancia radial $r$ y el semieje mayor $a$ de la órbita:

$$v^2 = \mu\left(\frac{2}{r} - \frac{1}{a}\right)$$

Esta ecuación se deriva directamente de la conservación de la energía mecánica específica, $\varepsilon = v^2/2 - \mu/r = -\mu/(2a)$, que es constante a lo largo de toda órbita cerrada. Su utilidad práctica es enorme: permite calcular la velocidad en el perigeo, en el apogeo, o en cualquier punto intermedio, de cualquier órbita elíptica, sin necesidad de resolver la ecuación de Kepler. Para una órbita circular ($r = a$ constante), se reduce al resultado ya conocido $v = \sqrt{\mu/r}$. Para una órbita parabólica de escape ($a \to \infty$), da la velocidad de escape $v_{esc} = \sqrt{2\mu/r}$.

Toda maniobra impulsiva —un encendido de motor que se modela como un cambio instantáneo de velocidad, razonable cuando la duración de la quema es mucho menor que el periodo orbital— se analiza comparando la velocidad vis-viva antes y después del impulso, en el mismo punto $r$ pero con distinto semieje mayor $a$ (porque la maniobra cambia la energía orbital).

## Transferencia de Hohmann

La transferencia de Hohmann, propuesta por Walter Hohmann en 1925 —antes de que existiera ningún vehículo capaz de realizarla—, es la maniobra de dos impulsos que conecta dos órbitas circulares coplanares con el mínimo $\Delta v$ total, cuando no hay restricción de tiempo. Consiste en una elipse de transferencia tangente a ambas órbitas circulares: su perigeo coincide con la órbita interior (radio $r_1$) y su apogeo con la exterior (radio $r_2$), de modo que el semieje mayor de la transferencia es $a_t = (r_1+r_2)/2$.

El primer impulso, aplicado en $r_1$, eleva la velocidad circular $v_1 = \sqrt{\mu/r_1}$ hasta la velocidad de la elipse de transferencia en su perigeo, $v_{t1} = \sqrt{\mu(2/r_1 - 1/a_t)}$:

$$\Delta v_1 = v_{t1} - v_1$$

El satélite viaja media elipse (la mitad del periodo de la transferencia) hasta llegar a $r_2$, donde un segundo impulso circulariza la órbita, elevando la velocidad de la elipse en su apogeo, $v_{t2} = \sqrt{\mu(2/r_2 - 1/a_t)}$, hasta la velocidad circular exterior $v_2 = \sqrt{\mu/r_2}$:

$$\Delta v_2 = v_2 - v_{t2}$$

El coste total es $\Delta v_{Hohmann} = \Delta v_1 + \Delta v_2$. Para elevar un satélite de una órbita LEO típica ($r_1 \approx 6778$ km) a GEO ($r_2 \approx 42\,164$ km), este cálculo da aproximadamente $\Delta v_1 \approx 2.40$ km/s y $\Delta v_2 \approx 1.46$ km/s, unos $3.86$ km/s en total —la razón por la que la mayoría de los lanzamientos a GEO usan una etapa superior o un motor de apogeo dedicado, en lugar de intentar la inserción directa.

## Cambio de plano orbital

Cambiar la inclinación o el nodo de una órbita —sin cambiar su forma ni tamaño— es, punto por punto, la maniobra más costosa en mecánica orbital, porque requiere rotar el vector velocidad completo sin cambiar su magnitud. Para un cambio de plano puro de ángulo $\Delta i$, ejecutado en un punto donde la velocidad orbital es $v$ (típicamente en una órbita circular, o en el nodo de intersección de ambos planos), el coste es

$$\Delta v = 2v\sin\left(\frac{\Delta i}{2}\right)$$

Esta fórmula surge de la geometría del triángulo de velocidades: dos vectores de igual magnitud $v$ separados por un ángulo $\Delta i$ tienen una diferencia vectorial de magnitud $2v\sin(\Delta i/2)$. Su implicación práctica es contundente: el coste crece con la velocidad orbital, así que los cambios de plano se realizan siempre donde $v$ es menor —en el apogeo de una órbita elíptica— y nunca cerca de GEO, donde incluso un cambio de inclinación de pocos grados exige cientos de metros por segundo. Es también la razón por la que los lanzamientos a GEO desde latitudes altas (Baikonur, a $\sim 46°$ de inclinación mínima) resultan más costosos que desde el ecuador (Kourou, cerca de $i=0°$): parte del $\Delta v$ de lanzamiento termina, en la práctica, pagando un cambio de plano parcial.

Cuando es necesario combinar un cambio de plano con un cambio de altitud, conviene ejecutar ambos en el mismo impulso, en el apogeo de la transferencia (donde $v$ es mínima), en lugar de en dos maniobras separadas: la suma vectorial de ambos $\Delta v$ es siempre menor o igual que la suma escalar.

## Transferencia bielíptica

Para ratios de radio muy grandes ($r_2/r_1 \gtrsim 11.94$), una variante de tres impulsos —la **transferencia bielíptica**— puede resultar más eficiente en $\Delta v$ total que la Hohmann directa, aunque tarda considerablemente más tiempo. Consiste en: (1) un primer impulso que eleva el apogeo mucho más allá de $r_2$, hasta un radio intermedio $r_b \gg r_2$; (2) al llegar a $r_b$, un segundo impulso (pequeño, porque la velocidad ahí es muy baja) que eleva el perigeo hasta $r_2$; (3) un tercer impulso en $r_2$ que circulariza. La ganancia de eficiencia proviene de que, cuanto mayor es $r_b$, menor es la velocidad en ese punto y más barato resulta el cambio de dirección necesario para el segundo impulso —a costa de un tiempo de tránsito mucho mayor y de un tercer motor encendido.

## Rendezvous orbital

El rendezvous —encontrarse con otro objeto en órbita, típicamente para acoplamiento, como en las misiones a la ISS— no es una única maniobra sino una secuencia de fases. Tras el lanzamiento a una órbita de fase con periodo ligeramente distinto al del objetivo (para cerrar o abrir la distancia angular lentamente), el vehículo ejecuta maniobras de corrección de fase hasta quedar en la misma órbita, desplazado por un ángulo pequeño. A partir de ahí, maniobras de aproximación sucesivas (a menudo a lo largo de la dirección radial o "V-bar"/"R-bar" del sistema de referencia LVLH del objetivo, que se define en la lección de sistemas de referencia) reducen la distancia relativa de kilómetros a metros, terminando en una aproximación final de baja velocidad controlada activamente hasta el contacto o captura.

## Ideas clave

- La vis-viva, $v^2 = \mu(2/r - 1/a)$, da la velocidad en cualquier punto de una órbita conociendo solo $r$ y $a$, y es la base de todo análisis de maniobras.
- La transferencia de Hohmann usa una elipse tangente a ambas órbitas circulares y es óptima en $\Delta v$ (sin restricción de tiempo) para transferencias de radio moderado.
- El cambio de plano puro, $\Delta v = 2v\sin(\Delta i/2)$, crece con la velocidad orbital, por lo que siempre conviene ejecutarlo donde $v$ es mínima.
- La transferencia bielíptica supera en eficiencia a la Hohmann para ratios de radio grandes, a costa de mucho más tiempo de tránsito.
- El rendezvous es una secuencia de fases —fase, corrección, aproximación— no una maniobra única, y las últimas fases se describen en el marco de referencia local del objetivo.

## Para seguir

La siguiente lección, *Perturbaciones orbitales*, explica por qué las órbitas reales se apartan de las elipses keplerianas ideales usadas aquí, y cómo efectos como el achatamiento terrestre ($J_2$) y el arrastre atmosférico obligan a corregir estas maniobras con combustible adicional a lo largo de la vida de la misión.
