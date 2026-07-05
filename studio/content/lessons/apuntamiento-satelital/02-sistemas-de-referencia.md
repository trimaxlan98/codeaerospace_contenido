---
title: Sistemas de referencia y actitud
level: medio
summary: ECI, ECEF, topocéntrico y LVLH sitúan un satélite en el espacio; cuaterniones y ángulos de Euler describen hacia dónde apunta su estructura.
tags: [eci-ecef, lvlh, cuaterniones, actitud, gimbal-lock]
minutes: 9
order: 2
---

## Objetivos

- Distinguir los sistemas de referencia ECI, ECEF, topocéntrico y LVLH y su uso característico.
- Explicar en qué consiste la transformación entre un sistema inercial y uno fijo a la Tierra.
- Comparar la representación de actitud por ángulos de Euler con la representación por cuaterniones.
- Explicar qué es el bloqueo de cardán (gimbal lock) y por qué los cuaterniones lo evitan.
- Definir apuntamiento nadir, apuntamiento a blanco (target) y apuntamiento inercial.

## Cuatro sistemas, cuatro propósitos

Ningún sistema de referencia único sirve para todo en mecánica orbital y apuntamiento; se usan al menos cuatro, cada uno adaptado al problema que resuelve.

El sistema **ECI** (Earth-Centered Inertial, centrado en la Tierra pero no rotando con ella) fija sus ejes respecto a direcciones estelares —por convención, el eje $X$ apunta hacia el equinoccio vernal en una época de referencia estándar como J2000— y no gira con la rotación terrestre. Es el sistema natural para propagar órbitas: las leyes de Newton que se usaron en las lecciones de Dinámica Orbital solo son válidas, sin términos ficticios adicionales, en un sistema inercial (o aproximadamente inercial, como ECI, que ignora la traslación de la Tierra alrededor del Sol, despreciable para la dinámica orbital de un satélite terrestre).

El sistema **ECEF** (Earth-Centered Earth-Fixed, como el estándar WGS84 que también usa el GPS) sí rota junto con la Tierra: sus ejes están fijos a puntos geográficos (el eje $X$ pasa por el meridiano de Greenwich en el ecuador). Es el sistema natural para expresar la posición de una estación terrena, cuyas coordenadas de latitud y longitud son constantes en ECEF pero varían continuamente en ECI a medida que la Tierra gira debajo. La transformación entre ambos es, en su forma más simple, una rotación alrededor del eje polar cuyo ángulo es el tiempo sidéreo de Greenwich (GST), que crece linealmente con el tiempo a la tasa de rotación terrestre; en aplicaciones de precisión se añaden correcciones menores de movimiento del polo y variación de la duración del día.

El sistema **topocéntrico** (introducido de forma práctica en la lección anterior como azimut/elevación) está centrado en la estación terrena misma, con ejes típicamente orientados este-norte-arriba (ENU) o equivalentes. Se obtiene de ECEF mediante una rotación que depende de la latitud y longitud de la estación, seguida de una traslación al punto de observación; es el sistema natural para todo lo que un operador de antena necesita: hacia dónde apuntar, ahora mismo, desde este punto concreto de la superficie terrestre.

El sistema **LVLH** (Local-Vertical-Local-Horizontal, también llamado orbital u órbita-fijo), por último, está centrado en el propio satélite y se mueve con él: un eje apunta radialmente hacia (o desde) el centro de la Tierra, otro a lo largo de la dirección del movimiento orbital, y el tercero completa la tríada perpendicular al plano orbital. Es el sistema natural para describir la actitud de un satélite respecto a su propia órbita (por ejemplo, "la cara +Z del satélite apunta siempre hacia la Tierra") y para maniobras de proximidad y rendezvous, donde interesa la posición relativa entre dos vehículos cercanos más que su posición absoluta en ECI.

## Representación de actitud: ángulos de Euler

La **actitud** —la orientación de la estructura del satélite respecto a un sistema de referencia dado— es, matemáticamente, una rotación en tres dimensiones, y existen varias formas equivalentes de parametrizarla. La más intuitiva son los **ángulos de Euler**: tres rotaciones sucesivas alrededor de ejes especificados (por ejemplo, la secuencia 3-2-1, comúnmente llamada *yaw-pitch-roll* en vehículos aeroespaciales) que, aplicadas en orden, llevan un sistema de referencia a coincidir con otro. Su ventaja es la interpretación física directa: cada ángulo corresponde a un giro reconocible (guiñada, cabeceo, alabeo).

Su desventaja seria es el **bloqueo de cardán** (*gimbal lock*): cuando el ángulo de la rotación intermedia de la secuencia se acerca a $\pm 90°$, las otras dos rotaciones colapsan sobre el mismo eje efectivo, perdiendo un grado de libertad de forma instantánea (matemáticamente, la matriz de transformación entre las velocidades angulares y las derivadas de los ángulos de Euler se vuelve singular). En esa configuración, pequeños cambios de actitud real pueden requerir variaciones enormes y mal condicionadas de los ángulos de Euler, lo cual es inaceptable para un sistema de control que necesita calcular comandos de actitud de forma robusta en cualquier orientación, incluidas maniobras agresivas de reapuntamiento.

## Cuaterniones

La solución estándar en sistemas de determinación y control de actitud (ADCS) modernos es representar la actitud mediante **cuaterniones unitarios**: un número de cuatro componentes, $q = (q_0, q_1, q_2, q_3)$ con $q_0^2+q_1^2+q_2^2+q_3^2=1$, que codifica una rotación como un eje de giro (las tres componentes vectoriales, normalizadas) y un ángulo de giro alrededor de ese eje (codificado en la componente escalar $q_0$). A diferencia de los ángulos de Euler, el cuaternión no tiene ninguna orientación singular: toda rotación posible, incluidas las que atraviesan lo que sería un bloqueo de cardán en la representación de Euler, se representa de forma continua y bien condicionada. La composición de rotaciones sucesivas se reduce a un producto de cuaterniones (una operación algebraica simple y numéricamente estable), y la interpolación suave entre dos actitudes (usada, por ejemplo, en perfiles de reapuntamiento) tiene fórmulas cerradas bien establecidas. El coste es la falta de interpretación geométrica inmediata —nadie "piensa" en cuaterniones de forma intuitiva— por lo que casi todo software de vuelo convierte a ángulos de Euler solo para la visualización o el reporte a operadores humanos, mientras el cálculo interno del ADCS trabaja enteramente en cuaterniones.

## Tipos de apuntamiento

El objetivo de todo el sistema de determinación y control de actitud, en última instancia, es mantener una de tres estrategias de apuntamiento (o una combinación programada de ellas a lo largo de la misión):

**Apuntamiento nadir**: una cara fija del satélite (por convención, a menudo +Z o -Z) se mantiene siempre orientada hacia el centro de la Tierra, expresado de forma natural en LVLH. Es el modo característico de satélites de observación de la Tierra y de comunicaciones que necesitan que su antena o instrumento principal mire siempre hacia abajo, independientemente de en qué punto de la órbita se encuentren.

**Apuntamiento a blanco (target tracking)**: el satélite reorienta continuamente su eje de apuntamiento para seguir un punto específico —una estación terrena fija, otro satélite, o una región de interés en superficie— que en general no coincide con el nadir y cuya dirección relativa cambia a lo largo de la órbita. Requiere calcular en tiempo real el vector hacia el blanco (transformando entre ECI, ECEF y el marco del satélite) y ajustar la actitud dinámicamente.

**Apuntamiento inercial**: la orientación se mantiene fija respecto a las estrellas (en ECI), independiente de la posición orbital del satélite. Es el modo característico de telescopios espaciales y otros instrumentos científicos que necesitan observar un objetivo celeste fijo durante periodos prolongados, sin que la órbita del propio satélite introduzca ninguna rotación aparente del campo de visión.

## Ideas clave

- ECI es el sistema natural para propagar órbitas (inercial); ECEF, para posiciones geográficas fijas; topocéntrico, para apuntar desde una estación; LVLH, para actitud y proximidad relativas a la propia órbita.
- La transformación ECI-ECEF es, en su forma esencial, una rotación cuyo ángulo es el tiempo sidéreo de Greenwich.
- Los ángulos de Euler son intuitivos pero sufren bloqueo de cardán cuando el ángulo intermedio se acerca a ±90°.
- Los cuaterniones representan cualquier actitud sin singularidades y componen rotaciones mediante un simple producto algebraico, por lo que dominan el cálculo interno de los ADCS modernos.
- Nadir, blanco (target) e inercial son las tres estrategias fundamentales de apuntamiento, cada una natural en un sistema de referencia distinto.

## Para seguir

La siguiente lección, *ADCS: sensores y actuadores*, describe el hardware que hace posible medir y mantener estas actitudes en la práctica: star trackers, ruedas de reacción, magnetorquers y el presupuesto de precisión que las combina.
