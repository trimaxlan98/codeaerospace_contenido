---
title: Modulación y codificación
level: medio
summary: De AM/FM/PM analógicas a ASK/FSK/PSK/QAM digitales, con constelaciones, BER frente a Eb/N0, códigos correctores y modulación adaptativa.
tags: [modulacion, qam, fec, ber, modcod]
minutes: 9
order: 2
---

## Objetivos

- Distinguir la modulación analógica clásica (AM, FM, PM) de sus contrapartes digitales (ASK, FSK, PSK, QAM).
- Interpretar un diagrama de constelación y relacionarlo con la eficiencia espectral de una modulación.
- Explicar la curva de tasa de error de bit (BER) frente a $E_b/N_0$ y su relación con el límite de Shannon.
- Describir el papel de la corrección de errores hacia adelante (FEC) y el concepto de tasa de código.
- Explicar la modulación adaptativa (MODCOD) como estrategia práctica para maximizar el throughput bajo condiciones variables.

## De la modulación analógica a la digital

La **modulación** es el proceso de imprimir información sobre una onda portadora de alta frecuencia, variando alguno de sus parámetros: amplitud, frecuencia o fase. En el mundo analógico clásico, **AM** (modulación de amplitud) varía la amplitud de la portadora proporcionalmente a la señal moduladora (la radio comercial de AM); **FM** (modulación de frecuencia) varía la frecuencia instantánea (la radio FM y la mayoría de los enlaces de voz analógicos, más robusta al ruido porque este afecta principalmente a la amplitud); y **PM** (modulación de fase) varía la fase, un pariente cercano de FM.

Las telecomunicaciones digitales modernas heredan directamente estos tres grados de libertad, pero modulando entre un conjunto **finito** y discreto de valores en lugar de una variación continua: **ASK** (*Amplitude Shift Keying*) transmite bits variando la amplitud entre niveles discretos; **FSK** (*Frequency Shift Keying*) los transmite conmutando entre frecuencias discretas (usado, por ejemplo, en los módems más antiguos y en RFID); y **PSK** (*Phase Shift Keying*) los transmite conmutando entre fases discretas de la portadora, con **BPSK** (2 fases, 1 bit/símbolo) y **QPSK** (4 fases, 2 bits/símbolo) como las variantes más comunes. **QAM** (*Quadrature Amplitude Modulation*) combina simultáneamente amplitud y fase, transmitiendo dos señales moduladas en amplitud sobre dos portadoras de la misma frecuencia pero en cuadratura (desfasadas 90°), lo que permite empaquetar más bits por símbolo que PSK puro para la misma tasa de error, a costa de mayor sensibilidad al ruido.

## Diagramas de constelación

Un **diagrama de constelación** representa cada símbolo posible como un punto en el plano complejo, con la componente en fase ($I$) en el eje horizontal y la componente en cuadratura ($Q$) en el eje vertical. BPSK tiene 2 puntos (1 bit/símbolo); QPSK tiene 4 puntos dispuestos en las diagonales (2 bits/símbolo); 16-QAM tiene 16 puntos en una rejilla cuadrada (4 bits/símbolo); 256-QAM tiene 256 puntos (8 bits/símbolo). Cuantos más puntos tiene la constelación, mayor es la eficiencia espectral (bits por símbolo, y por tanto por hercio de ancho de banda), pero los puntos están más cercanos entre sí en el plano $I/Q$, de modo que una cantidad dada de ruido tiene más probabilidad de desplazar el símbolo recibido hacia el punto vecino incorrecto: **cada bit adicional de eficiencia espectral exige una relación señal-ruido sustancialmente mayor** para mantener la misma tasa de error. En la práctica, un receptor mide el punto $I/Q$ recibido (con ruido) y lo asigna al punto de la constelación ideal más cercano; el ruido del canal, en un canal AWGN (ruido blanco gaussiano aditivo, el modelo estándar de análisis), dispersa cada punto recibido en una nube gaussiana alrededor del punto ideal, y esa dispersión —comparada con la distancia entre puntos vecinos— determina directamente la tasa de error.

## BER frente a Eb/N0

La **tasa de error de bit** (BER, *Bit Error Rate*) es la fracción de bits recibidos incorrectamente, y se caracteriza típicamente en función de $E_b/N_0$: la energía por bit ($E_b$) dividida entre la densidad espectral de potencia de ruido ($N_0$), una normalización que permite comparar esquemas de modulación de forma independiente de la tasa de bits y del ancho de banda concretos. Para BPSK en un canal AWGN, la relación exacta es

$$P_b = Q\left(\sqrt{\frac{2E_b}{N_0}}\right)$$

donde $Q(\cdot)$ es la función de cola de la distribución normal estándar. Al graficar $\log(BER)$ frente a $E_b/N_0$ (en dB) para distintas modulaciones se obtienen las llamadas **curvas de cascada** (waterfall curves): la BER cae abruptamente por debajo de cierto umbral de $E_b/N_0$, y ese umbral se desplaza hacia la derecha (exige más $E_b/N_0$) cuanto más densa es la constelación —QPSK necesita menos $E_b/N_0$ que 16-QAM para la misma BER objetivo, y 16-QAM necesita menos que 64-QAM. El diseño de cualquier enlace real —satelital, celular, Wi-Fi— consiste en elegir el punto de operación en estas curvas que maximice el throughput sin exceder una BER tolerable, dado el $E_b/N_0$ que efectivamente ofrece el presupuesto de enlace disponible.

## Corrección de errores hacia adelante (FEC)

La **corrección de errores hacia adelante** (FEC, *Forward Error Correction*) añade redundancia calculada al flujo de bits *antes* de la transmisión, de modo que el receptor puede detectar y corregir un número limitado de errores sin necesidad de retransmisión. Los códigos **convolucionales**, introducidos en los años 60, procesan el flujo de bits de forma continua con registros de desplazamiento y se decodifican eficientemente con el algoritmo de Viterbi; fueron el estándar dominante durante décadas (usados en GSM, en las primeras misiones espaciales de la NASA). Los **turbo códigos**, de los años 90, combinan dos codificadores convolucionales en paralelo con un entrelazador entre ellos y se decodifican iterativamente, acercándose sorprendentemente cerca del límite de Shannon; se adoptaron en 3G/4G. Los **códigos LDPC** (*Low-Density Parity-Check*), redescubiertos en los años 90 tras haber sido propuestos en los 60, ofrecen un rendimiento comparable o superior a los turbo códigos con menor complejidad de decodificación en hardware moderno, y son el estándar en Wi-Fi 802.11n/ac/ax, DVB-S2 y 5G NR.

La **tasa de código** $r = k/n$ cuantifica cuánta redundancia se añade: de cada $n$ bits transmitidos, solo $k$ son información útil (los $n-k$ restantes son paridad/redundancia). Una tasa de código baja (por ejemplo $r=1/2$) añade mucha redundancia, tolerando canales muy ruidosos a costa de reducir el throughput útil a la mitad; una tasa alta (por ejemplo $r=8/9$) añade poca redundancia, maximizando el throughput pero exigiendo un canal ya relativamente limpio. La combinación de una modulación (que fija bits/símbolo) y una tasa de código (que fija qué fracción de esos bits es información útil) determina la **eficiencia espectral neta** del enlace.

## Modulación adaptativa: MODCOD

Los sistemas modernos —desde el Wi-Fi hasta los satélites de televisión digital DVB-S2X— no operan con una combinación fija de modulación y código, sino que seleccionan dinámicamente, enlace a enlace y a veces símbolo a símbolo, la combinación óptima de **mod**ulación y **cod**ificación (**MODCOD**) para las condiciones instantáneas del canal. Cuando el canal es favorable (alta SNR, poca lluvia atenuando un enlace Ka-band, por ejemplo), el sistema conmuta a una constelación densa (256-QAM) con tasa de código alta, maximizando el throughput; cuando el canal se degrada, conmuta a una constelación más robusta (QPSK) con tasa de código baja, sacrificando throughput por robustez y manteniendo el enlace operativo en vez de perderlo por completo. DVB-S2X define hasta más de 80 combinaciones MODCOD distintas, seleccionadas mediante un canal de retorno que informa al transmisor de las condiciones medidas en el receptor, permitiendo que un mismo transpondedor satelital sirva simultáneamente a terminales con condiciones de enlace muy distintas (por ejemplo, afectadas de forma desigual por lluvia local), cada una recibiendo la MODCOD más agresiva que su enlace concreto puede sostener con fiabilidad.

## Ideas clave

- ASK, FSK y PSK son las contrapartes digitales de AM, FM y PM; QAM combina amplitud y fase para empaquetar más bits por símbolo.
- Un diagrama de constelación visualiza los símbolos posibles en el plano $I/Q$; constelaciones más densas dan mayor eficiencia espectral pero exigen mayor $E_b/N_0$ para la misma BER.
- La curva BER frente a $E_b/N_0$ caracteriza el rendimiento de una modulación de forma independiente de la tasa de bits concreta, y define el punto de operación práctico de cualquier enlace.
- El FEC (convolucional, turbo, LDPC) añade redundancia para corregir errores sin retransmisión; la tasa de código $r=k/n$ cuantifica el compromiso entre robustez y throughput útil.
- La modulación adaptativa (MODCOD) selecciona dinámicamente la combinación de modulación y código óptima para las condiciones instantáneas del canal, maximizando el throughput promedio de sistemas como DVB-S2X.

## Para seguir

La siguiente lección, *Medios de transmisión*, examina los canales físicos concretos —cobre, fibra y radioenlace— sobre los que se aplican estas técnicas de modulación y codificación, y cómo cada medio impone su propio balance de capacidad, alcance y costo.
