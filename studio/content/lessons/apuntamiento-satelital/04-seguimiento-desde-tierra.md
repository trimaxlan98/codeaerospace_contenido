---
title: Seguimiento desde estaciones terrenas
level: medio
summary: SGP4 predice curvas de azimut y elevación para cada pase, mientras el efecto Doppler y el problema del keyhole condicionan cómo un rotor sigue al satélite.
tags: [seguimiento-de-pases, sgp4, doppler, keyhole, rotores]
minutes: 9
order: 4
---

## Objetivos

- Explicar cómo se predice un pase visible combinando un TLE con el propagador SGP4.
- Interpretar una curva de azimut/elevación a lo largo de un pase.
- Describir el funcionamiento de un sistema de seguimiento automático con rotores.
- Calcular el desplazamiento Doppler de una señal satelital y explicar su compensación.
- Explicar el problema del keyhole en monturas azimut-elevación y sus soluciones.

## Predicción de pases con TLE y SGP4

Antes de poder apuntar una antena a un satélite, hay que saber cuándo y por dónde va a pasar. El procedimiento estándar combina el elemento de dos líneas (TLE) más reciente del objeto —descrito en la lección de elementos orbitales, y obtenido típicamente de Space-Track o de un repositorio derivado— con el propagador **SGP4** (introducido en la lección de perturbaciones) para calcular la posición del satélite en ECI en una malla de instantes futuros, normalmente con un paso de unos pocos segundos. Cada posición se transforma después a ECEF y finalmente al sistema topocéntrico de la estación (azimut, elevación, rango), tal como se describió en la lección de geometría de apuntamiento, produciendo la secuencia completa (Az, El, rango) en función del tiempo.

De esa secuencia se extraen los parámetros que interesan al operador: el instante de **adquisición de señal** (AOS, *Acquisition of Signal*, cuando la elevación cruza el mínimo operativo hacia arriba), el instante de **máxima elevación** (el punto más alto del pase, y normalmente el de mejor relación señal-ruido, por ser el de menor rango), y el instante de **pérdida de señal** (LOS, *Loss of Signal*, cuando la elevación vuelve a cruzar el mínimo hacia abajo). Software de seguimiento ampliamente usado (como los múltiples derivados de bibliotecas SGP4 de código abierto) automatiza este cálculo para toda una lista de satélites y una estación dada, produciendo un calendario de pases futuros con antelación de horas o días —aunque la precisión de esa predicción se degrada cuanto más viejo esté el TLE de partida, por las razones de precisión discutidas en la lección de perturbaciones.

## La curva de azimut y elevación de un pase

Cada pase tiene una forma característica cuando se grafica azimut y elevación en función del tiempo. La elevación sigue siempre una curva en forma de arco: cero en AOS, creciente hasta un máximo (que puede ir desde unos pocos grados, en un pase que apenas roza el horizonte, hasta $90°$ en un pase que cruza exactamente el cénit de la estación), y decreciente de vuelta a cero en LOS. El azimut, en cambio, varía de forma mucho más irregular: en un pase típico que no pasa por el cénit, el azimut cambia lentamente al principio y al final del pase (cuando el satélite está lejos, cerca del horizonte) y mucho más rápido cerca del punto de máxima elevación (cuando el satélite, aunque más lento en términos angulares absolutos vistos desde el centro de la Tierra, está mucho más cerca de la estación, así que su velocidad angular *aparente* vista desde tierra es mayor). Esta aceleración angular aparente cerca del cénit es la raíz del problema del keyhole, descrito más abajo.

## Seguimiento automático con rotores

Un **rotor de seguimiento** (o rotator) es un par de motores —uno de azimut, uno de elevación— que orientan físicamente una antena direccional según los comandos de un programa de seguimiento, que le indica en tiempo real (o con pocos segundos de anticipación) las coordenadas Az/El calculadas para el instante actual del pase. El seguimiento puede ser en lazo abierto (el rotor simplemente sigue la trayectoria precalculada, confiando en la precisión de la predicción y en la calibración mecánica del propio rotor) o en lazo cerrado con seguimiento automático activo (*autotrack*), donde la propia antena mide la intensidad de la señal recibida —a menudo mediante una técnica de escaneo cónico o monopulso, que compara la señal en direcciones ligeramente desplazadas del apuntamiento nominal— y ajusta su orientación para maximizarla en tiempo real, corrigiendo errores de predicción, de montaje o de calibración del propio rotor.

## Efecto Doppler y su compensación

El movimiento relativo entre el satélite y la estación —que en un pase LEO cambia de acercamiento a alejamiento a una velocidad radial de varios kilómetros por segundo— desplaza la frecuencia recibida respecto a la transmitida, un fenómeno bien conocido como **efecto Doppler**:

$$\Delta f = f_0\,\frac{v_r}{c}$$

donde $f_0$ es la frecuencia nominal de la portadora, $v_r$ es la velocidad radial relativa (positiva al acercarse), y $c$ la velocidad de la luz. Para un satélite LEO típico con velocidad orbital de unos $7.5$ km/s, la componente radial máxima ronda ese mismo orden de magnitud en el instante de máxima tasa de cambio de rango (justo antes o después del punto de máxima elevación, no en el propio cénit, donde la velocidad radial instantánea es momentáneamente nula). En una banda VHF de $145$ MHz, esto produce desplazamientos de hasta unos $3.6$ kHz; en una banda de microondas de $10$ GHz, el desplazamiento correspondiente escala proporcionalmente y alcanza cientos de kHz — significativo frente al ancho de banda de canales estrechos.

Para enlaces de banda estrecha (radioaficionados, telemetría de baja velocidad), la compensación se hace habitualmente **reajustando la frecuencia del receptor (y a veces también del transmisor) de forma continua** durante todo el pase, siguiendo la curva Doppler predicha a partir de la misma propagación SGP4 usada para el apuntamiento —de hecho, el mismo software de seguimiento suele generar ambas curvas, Az/El y desplazamiento Doppler, a partir de un único cálculo de posición y velocidad relativa. Enlaces de banda ancha modernos, en cambio, a menudo delegan la compensación en el propio receptor digital (mediante lazos de seguimiento de frecuencia, PLL, que rastrean la portadora directamente), reduciendo la dependencia de una predicción externa perfecta.

## El problema del keyhole

Una montura de antena **azimut-elevación** (Az/El), la configuración mecánica más común y económica, tiene una limitación geométrica intrínseca cerca del cénit: como se señaló arriba, cuando un pase pasa muy cerca de $El = 90°$, la tasa de cambio de azimut requerida se dispara —en el límite matemático exacto de un pase que cruza el cénit perfecto, el azimut requerido saltaría instantáneamente $180°$. Ningún rotor físico puede girar en azimut a velocidad infinita, así que en la práctica el rotor se "queda atrás" de la posición ideal durante esos segundos críticos, perdiendo el apuntamiento preciso justo en el momento de mejor geometría del pase (rango mínimo, mejor señal). Esta región de incapacidad de seguimiento cerca del cénit se conoce como **keyhole** ("cerradura", por la forma cónica de la zona de exclusión efectiva sobre la estación).

Existen varias mitigaciones prácticas: monturas **X/Y** (con los dos ejes de giro horizontales en lugar de uno vertical y uno horizontal) no tienen esta singularidad cerca del cénit —a cambio de tener una limitación geométrica análoga cerca del horizonte, donde para la mayoría de las aplicaciones importa mucho menos—; software de seguimiento que detecta con antelación un pase cercano al keyhole y preposiciona el rotor con margen, o que acepta una breve pérdida de precisión de apuntamiento durante esos segundos como compromiso aceptable; y, para antenas de mayor ancho de haz (menos exigentes en precisión), simplemente ignorar el problema, porque el error de apuntamiento transitorio cae dentro del margen tolerable del haz.

## Ideas clave

- La predicción de pases combina un TLE con SGP4 para generar la secuencia completa de azimut, elevación y rango en el tiempo, de la que se extraen AOS, máxima elevación y LOS.
- El azimut cambia mucho más rápido cerca de la máxima elevación que al principio o al final del pase, por la proximidad geométrica del satélite en ese instante.
- El seguimiento automático (autotrack) corrige errores de predicción midiendo directamente la intensidad de señal recibida, no solo siguiendo coordenadas precalculadas.
- El desplazamiento Doppler, $\Delta f = f_0 v_r/c$, puede alcanzar varios kHz en VHF y cientos de kHz en microondas para satélites LEO, y se compensa reajustando la frecuencia durante el pase.
- El keyhole es la incapacidad de un rotor Az/El de seguir la tasa de azimut requerida cerca del cénit; las monturas X/Y lo evitan a costa de una limitación equivalente cerca del horizonte.

## Para seguir

La última lección de la categoría, *Apuntamiento de antenas a GEO*, aplica esta misma geometría de apuntamiento al caso particular —y mucho más simple, por ser estático— de una antena fija dirigida a un satélite geoestacionario.
