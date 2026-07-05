---
title: Elementos orbitales clásicos
level: medio
summary: Los seis elementos keplerianos fijan forma, orientación y posición de una órbita, y las anomalías indican dónde está el satélite en cada instante.
tags: [elementos-orbitales, anomalia, ecuacion-de-kepler, tle]
minutes: 8
order: 2
---

## Objetivos

- Identificar los seis elementos orbitales clásicos y qué aspecto geométrico define cada uno.
- Distinguir entre anomalía verdadera, excéntrica y media, y saber cuándo se usa cada una.
- Resolver la ecuación de Kepler $M = E - e\sin E$ de forma conceptual (por qué es trascendente).
- Leer un conjunto de elementos de dos líneas (TLE) e identificar cada campo con su elemento orbital.
- Explicar por qué se necesitan exactamente seis números para describir una órbita.

## Los seis elementos keplerianos

Una órbita kepleriana ideal (dos cuerpos, sin perturbaciones) queda completamente determinada por seis números independientes, ni uno más ni uno menos: la solución de las ecuaciones de movimiento de dos cuerpos tiene seis grados de libertad (tres de posición y tres de velocidad en el instante inicial), y los elementos orbitales son simplemente una reparametrización de esos seis números en cantidades con significado geométrico directo, mucho más útiles para el diseño de misiones que un vector de posición y velocidad crudo.

Tres elementos fijan la **forma y el tamaño** de la elipse, en su propio plano:

- **Semieje mayor $a$**: el "tamaño" de la órbita, la mitad de la distancia entre perigeo y apogeo. Junto con $\mu$, fija el periodo mediante la tercera ley de Kepler.
- **Excentricidad $e$**: qué tan alargada es la elipse, de $0$ (círculo) a valores cercanos a $1$ (muy alargada). Aparece directamente en la ecuación de la cónica $r = a(1-e^2)/(1+e\cos\nu)$.
- **Anomalía verdadera $\nu$**: la posición instantánea del satélite dentro de su órbita, medida como ángulo desde el perigeo. Es el único de los seis elementos que cambia rápida y continuamente con el tiempo; los otros cinco son (idealmente) constantes.

Otros tres fijan la **orientación** del plano orbital y de la elipse dentro de él, respecto a un sistema de referencia inercial (típicamente el ecuador terrestre y el punto vernal, o equinoccio de Aries, como origen de ángulos):

- **Inclinación $i$**: el ángulo entre el plano orbital y el plano ecuatorial, de $0°$ (ecuatorial, prógrada) a $180°$ (ecuatorial, retrógrada), pasando por $90°$ (polar).
- **Ascensión recta del nodo ascendente $\Omega$** (a veces llamada RAAN): el ángulo, medido en el plano ecuatorial desde el punto vernal, hasta el punto donde el satélite cruza el ecuador de sur a norte (el nodo ascendente).
- **Argumento del perigeo $\omega$**: el ángulo, medido dentro del plano orbital desde el nodo ascendente, hasta el perigeo.

El siguiente diagrama conceptual resume la geometría:

```
                     Z (eje polar)
                      |
                      |        * satelite
                      |       /|
                      |      / | nu (anomalia verdadera,
                      |     /  |  medida desde perigeo)
                      |    * Perigeo
                      |   /
                      |  /  omega (arg. del perigeo,
                      | /    dentro del plano orbital)
                      |/
      ----------------+------------------- nodo ascendente
                      /|
                     / | i (inclinacion entre
                    /  |  plano orbital y ecuatorial)
                   /   |
                  /    +------------------- X (direccion vernal, Aries)
                 /    /
                /    / Omega (RAAN: angulo en el plano
               /    /   ecuatorial desde Aries al nodo)
              /    /
      Plano ecuatorial (referencia inercial, ej. J2000)
```

Con estos seis números —$a$, $e$, $i$, $\Omega$, $\omega$, $\nu$ (o, equivalentemente, alguna otra anomalía en lugar de $\nu$)— la posición y velocidad del satélite en cualquier instante quedan definidas sin ambigüedad, dentro de la aproximación de dos cuerpos.

## Las tres anomalías

Especificar "dónde está" el satélite dentro de su órbita admite tres descripciones equivalentes, cada una útil en un contexto distinto.

La **anomalía verdadera** $\nu$ es el ángulo geométrico real, medido en el foco, desde el perigeo hasta la posición del satélite. Es la más intuitiva, pero varía de forma no uniforme en el tiempo (rápido cerca del perigeo, lento cerca del apogeo, por la segunda ley de Kepler), lo que la hace incómoda para propagar en el tiempo.

La **anomalía excéntrica** $E$ es un ángulo auxiliar, definido geométricamente proyectando la posición del satélite sobre un círculo circunscrito a la elipse (de radio $a$, centrado en el centro geométrico de la elipse, no en el foco). Se relaciona con $\nu$ mediante $\tan(E/2) = \sqrt{\frac{1-e}{1+e}}\tan(\nu/2)$, y con la distancia radial mediante $r = a(1 - e\cos E)$.

La **anomalía media** $M$ es una construcción puramente matemática, no geométrica: se define como el ángulo que tendría el satélite si se moviera a velocidad angular constante (su movimiento medio $n = \sqrt{\mu/a^3} = 2\pi/T$) recorriendo $360°$ en un periodo completo. Su virtud es que **sí** avanza uniformemente: $M = M_0 + n(t - t_0)$, lo que la convierte en la variable natural para propagar una órbita en el tiempo.

El puente entre la anomalía media (fácil de propagar) y la posición real (anomalía verdadera, lo que importa físicamente) es la **ecuación de Kepler**:

$$M = E - e\sin E$$

Esta ecuación es trascendente: dado $M$, no existe una expresión algebraica cerrada para $E$, y debe resolverse iterativamente (típicamente con el método de Newton-Raphson, que converge en pocas iteraciones para excentricidades moderadas). Una vez obtenido $E$, se recupera $\nu$ con la relación mencionada arriba, y $r$ con $r = a(1-e\cos E)$. Este procedimiento —propagar $M$ linealmente, resolver Kepler para $E$, convertir a $\nu$ y $r$— es el núcleo de cualquier propagador kepleriano simple.

## Elementos orbitales de dos líneas (TLE)

En la práctica, el catálogo público de objetos en órbita terrestre (mantenido por la 18th Space Defense Squadron de EE. UU. y distribuido vía Space-Track.org) no publica $a$, $e$, $i$, $\Omega$, $\omega$, $\nu$ directamente, sino un formato compacto de texto llamado **Two-Line Element set (TLE)**, pensado para transmitirse en 1978 con recursos computacionales mínimos y que sigue siendo el estándar de facto hoy.

Un TLE típico luce así (para la ISS):

```
1 25544U 98067A   24045.52894176  .00016717  00000-0  10270-3 0  9994
2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.49560347436441
```

La segunda línea contiene directamente cuatro de los seis elementos clásicos y dos derivados: inclinación ($51.6416°$), RAAN ($247.4627°$), excentricidad (como decimal implícito, $0.0006703$), argumento del perigeo ($130.5360°$), anomalía media ($325.0288°$, no verdadera) y movimiento medio en revoluciones por día ($15.4956$, del cual se deriva $a$ invirtiendo la tercera ley de Kepler). La primera línea añade el identificador del objeto, la fecha de la observación (época) y coeficientes de arrastre atmosférico usados por el propagador SGP4, que se estudia en la lección de perturbaciones.

## Ideas clave

- Seis elementos —$a$, $e$, $i$, $\Omega$, $\omega$, $\nu$— bastan para describir por completo una órbita kepleriana, porque el problema de dos cuerpos tiene seis grados de libertad.
- $a$ y $e$ fijan forma y tamaño; $i$, $\Omega$ y $\omega$ fijan la orientación del plano orbital y de la elipse dentro de él.
- La anomalía verdadera es geométrica pero no uniforme en el tiempo; la anomalía media avanza uniformemente pero no tiene significado geométrico directo.
- La ecuación de Kepler, $M = E - e\sin E$, es trascendente y conecta ambas descripciones a través de la anomalía excéntrica $E$; se resuelve iterativamente.
- Los TLE son el formato universal de distribución de elementos orbitales, y codifican cinco de los seis elementos clásicos más el movimiento medio.

## Para seguir

La siguiente lección, *Maniobras orbitales*, usa estos elementos como punto de partida para estudiar cómo se cambia deliberadamente de una órbita a otra: transferencias de Hohmann, cambios de plano y sus costes en velocidad.
