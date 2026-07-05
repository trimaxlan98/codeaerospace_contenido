---
title: Leyes de Kepler y gravitación
level: intro
summary: Las tres leyes de Kepler y la ley de gravitación universal, unidas por el periodo orbital, explican por qué todo satélite traza una elipse.
tags: [kepler, gravitacion, mecanica-orbital, periodo-orbital]
minutes: 9
order: 1
---

## Objetivos

- Enunciar la ley de gravitación universal de Newton y su forma para dos cuerpos.
- Explicar las tres leyes de Kepler y su origen físico común.
- Calcular el periodo orbital de un satélite a partir de su semieje mayor mediante la tercera ley.
- Definir el parámetro gravitacional estándar $\mu$ y usarlo en cálculos reales.
- Aplicar estas relaciones a ejemplos concretos: la ISS y un satélite geoestacionario.

## La ley de gravitación universal

Toda la mecánica orbital moderna descansa sobre un único enunciado de Newton, publicado en 1687: dos cuerpos cualesquiera se atraen con una fuerza proporcional al producto de sus masas e inversamente proporcional al cuadrado de la distancia que los separa. Para un satélite de masa $m$ orbitando un cuerpo central de masa $M$ (la Tierra, en la mayoría de los casos que nos ocupan), la magnitud de la fuerza es

$$F = \frac{GMm}{r^2}$$

donde $G = 6.674 \times 10^{-11}\ \text{m}^3\,\text{kg}^{-1}\,\text{s}^{-2}$ es la constante de gravitación universal y $r$ es la distancia entre los centros de masa de ambos cuerpos. La fuerza siempre apunta a lo largo de la línea que une los dos centros, hacia el cuerpo central: es una fuerza central, y esa propiedad —no la ley del inverso del cuadrado en sí— es lo que garantiza que el movimiento quede confinado a un plano fijo en el espacio (el plano orbital), porque el momento angular respecto al centro de fuerza se conserva.

Para un satélite, $m \ll M$, así que la aceleración que experimenta es simplemente $a = GM/r^2$, independiente de su propia masa: una pluma y un martillo caerían igual en el vacío, y una cápsula de una tonelada y un CubeSat de un kilogramo siguen exactamente la misma trayectoria si parten del mismo punto con la misma velocidad. Esta independencia de la masa del satélite es la razón por la que el catálogo de constantes orbitales de un cuerpo central —el Sol, la Tierra, la Luna— se expresa siempre como el producto $GM$ combinado, llamado parámetro gravitacional estándar, y no como $G$ y $M$ por separado, cuyos valores individuales se conocen con mucha menor precisión.

## Las tres leyes de Kepler

Johannes Kepler formuló sus tres leyes empíricamente entre 1609 y 1619, a partir de las observaciones planetarias de Tycho Brahe, casi un siglo antes de que Newton demostrara que se derivan directamente de la gravitación universal. Su vigencia no ha cambiado: valen exactamente igual para un planeta alrededor del Sol que para un CubeSat alrededor de la Tierra.

**Primera ley (órbitas elípticas).** La trayectoria de un cuerpo bajo la atracción gravitatoria de otro es una cónica con el cuerpo central en uno de sus focos. Para las órbitas cerradas que nos interesan, esa cónica es una elipse, descrita en coordenadas polares centradas en el foco por la ecuación

$$r = \frac{p}{1 + e\cos\theta}$$

donde $r$ es la distancia instantánea al foco, $\theta$ es el ángulo medido desde el punto de máximo acercamiento (el periapsis), $e$ es la excentricidad ($0$ para un círculo, entre $0$ y $1$ para una elipse) y $p = a(1-e^2)$ es el semilatus rectum, con $a$ el semieje mayor. En $\theta = 0$ (periapsis) la distancia es mínima, $r_p = a(1-e)$; en $\theta = 180°$ (apoapsis) es máxima, $r_a = a(1+e)$. Un círculo es simplemente el caso degenerado $e=0$, donde $r$ es constante.

**Segunda ley (áreas iguales en tiempos iguales).** El segmento que une el cuerpo central con el satélite barre áreas iguales en intervalos de tiempo iguales. Esta ley es, en realidad, la conservación del momento angular disfrazada: como la fuerza gravitatoria es central, no genera torque respecto al foco, así que el momento angular específico $h = r^2\dot\theta$ es constante a lo largo de toda la órbita. La consecuencia práctica es que un satélite se mueve más rápido cerca del periapsis y más lento cerca del apoapsis; en una órbita muy excéntrica como una Molniya, el objeto puede pasar la mayor parte de su periodo cerca del apogeo.

**Tercera ley (relación periodo-semieje).** El cuadrado del periodo orbital es proporcional al cubo del semieje mayor. Newton demostró que la constante de proporcionalidad depende del parámetro gravitacional del cuerpo central, dando la forma que usamos en ingeniería:

$$T = 2\pi\sqrt{\frac{a^3}{\mu}}$$

Esta es, con diferencia, la fórmula más usada en todo el diseño de misiones: conocido el semieje mayor deseado, se obtiene directamente el periodo, y viceversa.

## El parámetro gravitacional estándar y el periodo orbital

El parámetro gravitacional estándar se define como $\mu = GM$. Para la Tierra, su valor —determinado con mucha más precisión que $G$ y $M_\oplus$ por separado, a partir del seguimiento de satélites— es

$$\mu_\oplus = 398\,600.4\ \text{km}^3/\text{s}^2$$

Con este número y la tercera ley de Kepler se puede calcular el periodo de cualquier órbita terrestre conociendo solo su semieje mayor $a$ (en kilómetros, si se usa $\mu_\oplus$ en las mismas unidades). Nótese que el periodo depende únicamente de $a$, no de la excentricidad: una órbita circular de $7000$ km de radio y una órbita elíptica con semieje mayor de $7000$ km pero apogeo y perigeo muy distintos tienen exactamente el mismo periodo.

La velocidad orbital instantánea también se deriva de $\mu$ mediante la ecuación de vis-viva (que se explora en detalle en la lección de maniobras orbitales), pero conviene adelantar el caso circular más simple: en una órbita circular de radio $r$, la velocidad es constante e igual a $v = \sqrt{\mu/r}$, resultado de igualar la fuerza gravitatoria con la fuerza centrípeta necesaria, $GMm/r^2 = mv^2/r$.

## De la teoría a la práctica: ejemplos numéricos

Tomemos la Estación Espacial Internacional, que orbita a unos $400$ km de altitud. Su semieje mayor es aproximadamente $a = R_\oplus + h \approx 6378 + 400 = 6778$ km (asumiendo órbita casi circular). Aplicando la tercera ley:

$$T = 2\pi\sqrt{\frac{6778^3}{398\,600.4}} \approx 5551\ \text{s} \approx 92.5\ \text{minutos}$$

en excelente acuerdo con el valor real (~92.7 min), y su velocidad orbital es $v = \sqrt{398\,600.4/6778} \approx 7.67$ km/s, unos 27\,600 km/h.

El caso inverso —partir del periodo deseado para obtener la altitud— es exactamente el cálculo que define la órbita geoestacionaria. Se busca un periodo igual al día sidéreo, $T = 86\,164.1$ s (no el día solar de 24 h, porque lo que debe coincidir es la rotación de la Tierra respecto a las estrellas fijas, no respecto al Sol). Despejando $a$ de la tercera ley:

$$a = \left(\frac{\mu_\oplus T^2}{4\pi^2}\right)^{1/3} \approx 42\,164\ \text{km}$$

Restando el radio ecuatorial de la Tierra ($6378$ km) se obtiene la altitud característica de GEO: $35\,786$ km. Este único cálculo —tercera ley de Kepler, un despeje algebraico y una resta— es el origen de todo el negocio de las telecomunicaciones geoestacionarias.

## Ideas clave

- La gravitación de Newton, $F = GMm/r^2$, es una fuerza central: por eso el momento angular se conserva y toda órbita queda confinada a un plano fijo.
- La primera ley de Kepler describe la órbita como una cónica, $r = p/(1+e\cos\theta)$, con el cuerpo central en un foco, no en el centro geométrico.
- La segunda ley (áreas iguales) es la conservación del momento angular: los satélites aceleran cerca del perigeo y se frenan cerca del apogeo.
- La tercera ley, $T = 2\pi\sqrt{a^3/\mu}$, depende solo del semieje mayor, no de la excentricidad, y es la herramienta de diseño más usada en mecánica orbital.
- El parámetro gravitacional estándar $\mu_\oplus = 398\,600.4\ \text{km}^3/\text{s}^2$ se conoce con mucha más precisión que $G$ y $M_\oplus$ por separado.

## Para seguir

La siguiente lección, *Elementos orbitales clásicos*, retoma la ecuación de la cónica para introducir los seis parámetros que fijan por completo la posición y orientación de una órbita en el espacio, junto con las anomalías que describen dónde está el satélite en cada instante.
