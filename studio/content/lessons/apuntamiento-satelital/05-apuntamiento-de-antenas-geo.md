---
title: Apuntamiento de antenas a GEO
level: intro
summary: Azimut, elevación y polarización hacia un satélite geoestacionario se calculan desde la latitud y longitud de la estación, y se afinan según el ancho de haz de la antena.
tags: [geo, vsat, ancho-de-haz, alineacion-de-antenas]
minutes: 9
order: 5
---

## Objetivos

- Calcular el azimut y la elevación hacia un satélite geoestacionario desde la latitud y longitud de una estación.
- Calcular el ángulo de polarización (skew) necesario para una antena de polarización lineal.
- Aplicar la fórmula aproximada del ancho de haz de una antena parabólica y relacionarla con la pérdida por desapuntamiento.
- Describir el procedimiento práctico de alineación de una antena VSAT.
- Explicar por qué el apuntamiento a GEO, a diferencia de LEO, no requiere seguimiento continuo.

## Por qué GEO simplifica el apuntamiento

A diferencia de todo lo visto en las lecciones anteriores para satélites en movimiento relativo respecto a la estación, un satélite geoestacionario —por definición, en una órbita circular ecuatorial con el periodo exacto de un día sidéreo, como se dedujo en la lección de leyes de Kepler— permanece, idealmente, en una posición fija en el cielo respecto a cualquier observador terrestre. Esto convierte el problema de apuntamiento de un cálculo dinámico y continuo (como el seguimiento de un pase LEO) en un cálculo **estático**, que se realiza una sola vez durante la instalación de la antena: encontrar el azimut, la elevación y la polarización correctos, fijarlos mecánicamente, y no volver a tocarlos salvo pequeñas correcciones periódicas por el movimiento residual del satélite dentro de su caja de mantenimiento en estación (station-keeping), típicamente de una fracción de grado.

## Cálculo de azimut y elevación

Dado un satélite GEO en la longitud $\lambda_S$ (su posición nominal sobre el ecuador) y una estación terrena en latitud $\varphi$ y longitud $\lambda_E$, el primer paso es calcular la diferencia de longitud $B = \lambda_S - \lambda_E$. La **elevación**, el ángulo sobre el horizonte local al que hay que apuntar, se obtiene de

$$El = \arctan\left(\frac{\cos B\cos\varphi - \dfrac{R_\oplus}{R_\oplus+h}}{\sqrt{1-\cos^2 B\cos^2\varphi}}\right)$$

donde $R_\oplus$ es el radio terrestre y $h=35\,786$ km la altitud geoestacionaria (de modo que $R_\oplus/(R_\oplus+h) \approx 0.1512$). El **azimut** se obtiene de una relación trigonométrica esférica equivalente que involucra los mismos ángulos $B$ y $\varphi$, con la salvedad de que su cuadrante final depende del hemisferio de la estación y del signo de $B$ (si el satélite está al este u oeste de la estación): en el hemisferio norte, por ejemplo, un satélite al este de la estación se busca hacia el sureste, y uno al oeste hacia el suroeste, mientras que en el hemisferio sur el patrón se invierte hacia el norte. Cualquier calculadora de look angles (ampliamente disponible en operadores de VSAT y en software de planificación de enlaces) automatiza este cálculo completo a partir simplemente de las coordenadas de la estación y la longitud orbital del satélite deseado.

Como consecuencia directa de esta geometría, cuanto mayor es la diferencia de longitud $B$ o mayor la latitud $\varphi$ de la estación, menor resulta la elevación calculada; para $\varphi$ y $B$ suficientemente grandes (aproximadamente por encima de los $81°$ de latitud, o combinaciones de latitud y longitud que empujan la elevación por debajo de cero), el satélite queda directamente bajo el horizonte y resulta inalcanzable —la razón estructural por la que la cobertura GEO se degrada severamente en latitudes polares, y por la que sistemas como Molniya o Tundra (vistos en la lección «Órbitas y familias de satélites») existen específicamente para cubrir esas regiones.

## Ángulo de polarización (skew)

Además de azimut y elevación, una antena de polarización lineal (común en bandas C y Ku) requiere un tercer ajuste: el **ángulo de polarización** o *skew*, la rotación del alimentador (feed) de la antena alrededor de su propio eje de puntería, necesaria porque el plano de referencia de polarización del transpondedor satelital (definido respecto al ecuador, visto desde el propio satélite) no coincide, en general, con la vertical local de la estación terrena una vez que esta mira en una dirección oblicua. El ángulo de skew se calcula, de forma aproximada, mediante

$$\tan(\psi) = \frac{\sin B}{\tan\varphi}$$

con signo y sentido de rotación (horario o antihorario visto desde detrás del reflector) dependientes, de nuevo, del hemisferio y del signo de $B$. Un desalineamiento de polarización no impide la recepción de la señal por completo, pero introduce una pérdida adicional (proporcional al coseno del error angular) y, más críticamente en sistemas que reutilizan la misma frecuencia en polarizaciones ortogonales para duplicar capacidad, incrementa la interferencia entre canales de polarización cruzada.

## Ancho de haz y pérdida por desapuntamiento

La precisión con la que hay que respetar estos tres ángulos calculados depende directamente del **ancho de haz** de la antena, que para un reflector parabólico se aproxima con la regla práctica

$$\theta_{3dB} \approx \frac{70\lambda}{D}\ \text{grados}$$

donde $\lambda$ es la longitud de onda de la señal y $D$ el diámetro del reflector, ambos en las mismas unidades. Esta fórmula captura la relación fundamental de toda antena de apertura: cuanto mayor la antena en relación con la longitud de onda, más estrecho (y por tanto más ganancia y más exigente en apuntamiento) resulta el haz. Una VSAT típica de $1.2$ m operando en banda Ku ($\lambda \approx 0.025$ m, correspondiente a unos $12$ GHz) tiene un ancho de haz de apenas $\theta_{3dB} \approx 70\times0.025/1.2 \approx 1.5°$; un radioenlace de banda C con antena mayor y longitud de onda más larga tiende a tener haces algo más anchos, más tolerantes al error de apuntamiento, pero de menor ganancia.

Un error de apuntamiento $\theta_e$ respecto al centro exacto del haz introduce una **pérdida por desapuntamiento** que, para el lóbulo principal de un reflector parabólico, se aproxima habitualmente como

$$L_p \approx 12\left(\frac{\theta_e}{\theta_{3dB}}\right)^2\ \text{dB}$$

Esta relación cuadrática explica por qué antenas de haz estrecho (grandes, o de frecuencias altas) exigen procedimientos de alineación mucho más cuidadosos: un error de apuntamiento que en banda C apenas penaliza el enlace puede, en banda Ku o Ka con la misma antena, introducir varios decibelios de pérdida —suficiente para degradar significativamente, o incluso interrumpir, un enlace con margen de potencia ajustado.

## Alineación práctica de una VSAT

En la instalación real de una VSAT, el procedimiento combina el cálculo teórico anterior con un ajuste fino guiado por la señal real recibida. Primero se calculan los valores esperados de azimut, elevación y skew a partir de la ubicación de la estación y del satélite objetivo, y se realiza un apuntamiento inicial aproximado con brújula (corrigiendo la declinación magnética local, que puede diferir del norte geográfico usado en el cálculo por varios grados) e inclinómetro. A partir de ahí, con un medidor de señal o el propio indicador de nivel del módem conectado (buscando la portadora piloto o baliza del satélite objetivo), se afina iterativamente: primero azimut, moviendo la antena lentamente de un lado a otro hasta hallar el máximo; después elevación, con el mismo criterio; y finalmente el skew, rotando el feed hasta maximizar la señal (o minimizar la interferencia de polarización cruzada, si se dispone de esa medición). Como el ancho de haz de una antena Ku o Ka típica es de apenas uno o dos grados, este ajuste fino final —no el cálculo teórico inicial, que solo aproxima— es habitualmente el que determina si el enlace opera con el margen de potencia esperado o con varios decibelios perdidos por un desapuntamiento residual imperceptible a simple vista.

## Ideas clave

- La geometría GEO es estática: se calcula una vez con las fórmulas de azimut, elevación y skew a partir de la latitud, longitud de la estación y la longitud orbital del satélite.
- La elevación decrece con la latitud y con la diferencia de longitud, hasta hacerse negativa (satélite inalcanzable) en latitudes suficientemente altas.
- El ángulo de polarización (skew) alinea el plano de polarización de la antena con el del transpondedor, y su error reduce señal e incrementa interferencia de polarización cruzada.
- El ancho de haz, $\theta_{3dB}\approx70\lambda/D$, se estrecha con antenas más grandes o frecuencias más altas, y la pérdida por desapuntamiento crece con el cuadrado del error relativo al ancho de haz.
- La alineación práctica de una VSAT combina un cálculo inicial aproximado con un ajuste fino iterativo guiado por la potencia de señal real, indispensable cuando el ancho de haz es de solo uno o dos grados.

## Para seguir

Esto cierra la categoría de Apuntamiento Satelital. La siguiente categoría de la biblioteca, *Redes de Telecomunicaciones*, retoma estos enlaces de antena para explicar cómo se diseña el enlace de radiofrecuencia completo: presupuesto de enlace, bandas de frecuencia y modulación.
