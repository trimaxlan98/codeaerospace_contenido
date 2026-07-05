---
title: Fundamentos de señales y espectro
level: intro
summary: Señal, ancho de banda, decibelios y los límites de Nyquist y Shannon establecen cuánta información puede transportar cualquier canal físico.
tags: [señales, ancho-de-banda, shannon, nyquist, decibelios]
minutes: 9
order: 1
---

## Objetivos

- Definir señal, ancho de banda y su relación con el contenido en frecuencia mediante la idea de Fourier.
- Manejar el decibelio (dB) y el dBm como escalas logarítmicas de relación y de potencia absoluta.
- Enunciar el límite de Nyquist para la tasa de símbolo máxima sin interferencia entre símbolos.
- Enunciar el límite de Shannon para la capacidad máxima de un canal con ruido.
- Calcular numéricamente la capacidad de un canal típico y compararla con su tasa de símbolo.

## Qué es una señal y qué es el ancho de banda

Una **señal** de telecomunicaciones es una función que varía en el tiempo —típicamente una tensión eléctrica, una intensidad óptica o un campo electromagnético— y que se modula deliberadamente para transportar información. Toda señal real y de energía finita admite una representación equivalente en el dominio del tiempo, $s(t)$, y en el dominio de la frecuencia, $S(f)$, relacionadas por la **transformada de Fourier**: cualquier señal, por complicada que parezca en el tiempo, se puede descomponer en una suma (o integral) de senoides puras de distintas frecuencias, amplitudes y fases. Esta dualidad es la herramienta conceptual central de todas las telecomunicaciones, porque el medio de transmisión (un cable, una fibra, el aire) no trata igual a todas las frecuencias: atenúa unas más que otras, y el diseño del sistema completo —del filtro al amplificador— se razona casi siempre en el dominio de la frecuencia.

El **ancho de banda** $B$ de una señal o de un canal es el rango de frecuencias que ocupa o que puede transportar, medido en hercios (Hz). Una señal de voz telefónica clásica ocupa aproximadamente 300–3400 Hz (unos 3.1 kHz de ancho de banda); un canal de televisión analógica NTSC ocupaba 6 MHz; un canal Wi-Fi 802.11ac puede llegar a 160 MHz. El ancho de banda no es una propiedad abstracta: está directamente ligado, como se verá con Nyquist y Shannon, a cuánta información por segundo puede transportar el canal. Un principio de incertidumbre análogo al de Fourier impone además que una señal más corta en el tiempo (un pulso más estrecho) necesita, inevitablemente, más ancho de banda para representarse fielmente, y viceversa: no se puede comprimir arbitrariamente una señal en el tiempo sin pagar el precio en espectro.

## Decibelios (dB) y dBm

Las relaciones de potencia en telecomunicaciones —ganancias de amplificador, atenuaciones de cable, pérdidas de propagación— abarcan típicamente muchos órdenes de magnitud, lo que hace incómodo trabajar en unidades lineales. El **decibelio** resuelve esto expresando una *razón* de potencias en escala logarítmica:

$$dB = 10\log_{10}\left(\frac{P_2}{P_1}\right)$$

Así, duplicar la potencia equivale a $+3$ dB (porque $10\log_{10}2 \approx 3.01$); una atenuación a la décima parte equivale a $-10$ dB; un factor de mil equivale a $+30$ dB. Esta propiedad —que multiplicar factores en unidades lineales se convierte en *sumar* decibelios— es la razón práctica de su uso universal: la ganancia total de una cadena de amplificadores y pérdidas en cascada se calcula sumando y restando dB, en vez de multiplicar y dividir factores lineales.

El **dBm** es una variante que fija la referencia $P_1 = 1$ mW, convirtiendo el dB de una razón adimensional en una unidad de potencia *absoluta*:

$$P_{dBm} = 10\log_{10}\left(\frac{P_{mW}}{1\ \text{mW}}\right)$$

Así, 0 dBm equivale a 1 mW, 30 dBm equivale a 1 W, y −30 dBm equivale a 1 µW. Un transmisor Wi-Fi típico opera alrededor de 20 dBm (100 mW); la sensibilidad de un receptor de fibra óptica puede rondar los −25 dBm. La combinación de ambas convenciones —dB para razones, dBm para potencias absolutas— permite construir un **presupuesto de enlace** (link budget) completo sumando algebraicamente potencia de transmisión, ganancias de antena y pérdidas de cable, propagación y conector, todo en la misma unidad aditiva.

## El límite de Nyquist: tasa de símbolo máxima

En 1928, Harry Nyquist demostró que un canal de ancho de banda $B$ (en Hz), libre de ruido, permite transmitir símbolos a una tasa máxima sin **interferencia entre símbolos** (ISI) dada por:

$$R_s = 2B$$

símbolos por segundo. Si cada símbolo puede tomar uno de $M$ niveles distintos (por ejemplo, $M=4$ en una modulación de 4 niveles), cada símbolo transporta $\log_2 M$ bits, y la tasa de bits resultante —el llamado **criterio de Nyquist**— es:

$$C = 2B\log_2 M$$

Este resultado es puramente geométrico: describe cuántos pulsos distinguibles caben por segundo en un canal de ancho $B$ sin que se superpongan destructivamente entre sí, sin decir nada todavía sobre el ruido. Es el límite que importa, por ejemplo, al diseñar un módem de línea telefónica clásico: con $B \approx 3$ kHz y una modulación de $M=16$ niveles, la tasa de Nyquist da $C = 2\times3000\times\log_2 16 = 24\,000$ bit/s, un techo que solo el ruido térmico real del canal telefónico impedía alcanzar en la práctica sin las técnicas más sofisticadas de los módems modernos (que se apoyan, además, en ecualización adaptativa y codificación).

## El límite de Shannon: capacidad con ruido

Claude Shannon, en 1948, extendió el problema incorporando el ruido inevitable de todo canal físico. El **teorema de Shannon-Hartley** establece la capacidad máxima teórica $C$, en bits por segundo, de un canal con ancho de banda $B$ y una relación señal-ruido $S/N$ (en unidades lineales, de potencia):

$$C = B\log_2\left(1 + \frac{S}{N}\right)$$

Este es, a diferencia de Nyquist, un límite *fundamental e infranqueable*: ninguna técnica de modulación o codificación, por avanzada que sea, puede superar $C$ con una tasa de error arbitrariamente baja; y, crucialmente, el teorema también garantiza —de forma no constructiva— que existen esquemas de codificación capaces de *acercarse* arbitrariamente a $C$ con probabilidad de error tan pequeña como se desee, siempre que la tasa de transmisión se mantenga por debajo de ese límite. Las décadas posteriores de investigación en códigos correctores de errores (turbo códigos, LDPC, vistos en la siguiente lección) son, en esencia, la búsqueda práctica de esa promesa teórica.

La relación señal-ruido $S/N$ suele expresarse en decibelios como $SNR_{dB} = 10\log_{10}(S/N)$, y conviene recordar convertirla a unidades lineales antes de aplicarla dentro del logaritmo de la fórmula de Shannon.

## Ejemplo numérico: capacidad de un canal ADSL

Considérese un par de cobre con un ancho de banda utilizable de $B = 1$ MHz y una relación señal-ruido de $SNR_{dB} = 30$ dB. Convirtiendo a lineal: $S/N = 10^{30/10} = 1000$. Aplicando Shannon:

$$C = 10^6 \times \log_2(1+1000) \approx 10^6 \times 9.97 \approx 9.97\ \text{Mbit/s}$$

Este cálculo explica de forma directa por qué el ADSL clásico, operando sobre pares de cobre con SNR moderado y anchos de banda del orden del megahercio, entrega tasas del orden de varios a diez megabits por segundo: no es una limitación de la tecnología del módem, sino un techo físico impuesto por el ancho de banda disponible y el ruido del medio. Aumentar la tasa de datos exige, según esta fórmula, o bien más ancho de banda (la estrategia de VDSL y de la fibra óptica, que operan con $B$ mucho mayor) o bien mejor SNR (reduciendo ruido o acortando la distancia del cable, que atenúa menos la señal y por tanto sube $S$ relativo a $N$).

## Ideas clave

- Toda señal admite una representación dual tiempo-frecuencia (Fourier); el ancho de banda $B$ cuantifica el rango de frecuencias que ocupa o transporta un canal.
- El decibelio convierte productos de razones de potencia en sumas, facilitando presupuestos de enlace; el dBm fija una referencia absoluta de 1 mW.
- Nyquist, $C=2B\log_2 M$, acota la tasa de símbolo sin interferencia entre símbolos en un canal sin ruido, en función del ancho de banda y del número de niveles de modulación.
- Shannon, $C=B\log_2(1+S/N)$, es el límite fundamental e infranqueable de capacidad de cualquier canal real con ruido, y motiva toda la teoría de codificación correctora de errores.
- Aumentar la capacidad de un canal exige más ancho de banda, mejor SNR, o ambos; no existe una tercera vía que evada estos dos parámetros.

## Para seguir

La siguiente lección, *Modulación y codificación*, retoma estos límites teóricos para explicar cómo las técnicas reales de modulación (ASK, FSK, PSK, QAM) y de codificación (FEC) se diseñan precisamente para acercarse, en la práctica, al límite de Shannon.
