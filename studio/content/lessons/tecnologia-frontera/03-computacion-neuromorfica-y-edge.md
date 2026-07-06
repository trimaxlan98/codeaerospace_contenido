---
title: Computación neuromórfica y edge
level: avanzado
summary: Los chips que imitan al cerebro con redes neuronales de picos, la computación en el borde frente a la nube (latencia, privacidad, energía), TinyML en dispositivos diminutos y los aceleradores de IA (GPU, TPU, NPU) comparados.
tags: [neuromorfico, spiking, edge, tinyml, gpu, tpu, npu]
minutes: 12
order: 3
---

## Objetivos

- Entender qué imita la computación neuromórfica y qué son las redes de picos.
- Comparar el borde (edge) con la nube en latencia, privacidad y energía.
- Conocer TinyML y su idea de IA en dispositivos diminutos.
- Distinguir GPU, TPU y NPU y para qué sirve cada acelerador.
- Ver cómo se conectan estas ideas con la IA de las categorías anteriores.

## Computación neuromórfica

Los ordenadores actuales separan memoria y procesador (la **arquitectura de von Neumann**), y mover datos entre ambos constantemente consume la mayor parte de la energía —el "cuello de botella de von Neumann"—. El cerebro no funciona así: es eficientísimo (unos 20 vatios para lo que a un superordenador le costaría megavatios) porque **integra memoria y cómputo** en las mismas neuronas y sinapsis, procesa en paralelo masivo y solo gasta energía cuando hay actividad. La **computación neuromórfica** intenta llevar esos principios al hardware: chips cuya arquitectura física imita la del cerebro.

Su modelo de cómputo son las **redes neuronales de picos** (*spiking neural networks*, SNN), más cercanas a la biología que las redes de la categoría de IA. En lugar de propagar valores continuos en cada paso, las neuronas de una SNN acumulan carga y **disparan un pico** (un pulso breve) solo cuando cruzan un umbral, comunicándose con **eventos discretos** en el tiempo. La información está en *cuándo* y *con qué frecuencia* se dispara, no en un número por ciclo. La ventaja es la eficiencia: como solo consumen energía al disparar y gran parte del tiempo están en silencio, procesan información dispersa con un gasto ínfimo. Chips de investigación como Loihi (Intel) o los de IBM materializan estas ideas. El obstáculo: entrenar SNN es más difícil que las redes convencionales (los picos no son diferenciables como las activaciones suaves), y el ecosistema de software es aún inmaduro. Es un campo prometedor sobre todo para sensado siempre activo y de muy baja potencia, todavía lejos de desplazar a las GPU en el grueso de la IA.

## El borde frente a la nube

Dónde ocurre el cómputo define una tensión central de la tecnología moderna. En la **nube** (*cloud*), el procesamiento se hace en centros de datos remotos y potentes; en el **borde** (*edge*), en el propio dispositivo donde se generan los datos —un teléfono, una cámara, un sensor, un coche—. Cada enfoque compra cosas distintas:

| | Nube | Borde |
|---|---|---|
| Potencia de cómputo | Enorme | Limitada |
| Latencia | Alta (ida y vuelta a la red) | Muy baja (local) |
| Privacidad | Los datos salen del dispositivo | Los datos no salen |
| Conectividad | Requiere red | Funciona sin conexión |
| Energía por dispositivo | El dispositivo solo transmite | El dispositivo procesa (gasta más) |

El borde gana cuando importan la **latencia** (un coche autónomo o un robot no pueden esperar a la nube para frenar), la **privacidad** (procesar voz o vídeo sin enviarlos fuera —el aprendizaje federado de la lección de ética de IA vive aquí—), la **conectividad** intermitente o su ausencia, o el **coste y ancho de banda** de transmitir datos masivos. La nube gana cuando hace falta potencia bruta que no cabe en un dispositivo (entrenar modelos grandes, la lección de IA). En la práctica se combinan: inferencia ligera en el borde para lo urgente y privado, y la nube para lo pesado —un continuo *edge-nube* más que una elección tajante—. Esta distribución es también la que motivaba llevar cómputo al borde de la red en 6G.

## TinyML

Llevar la IA al borde en su forma extrema es **TinyML**: ejecutar modelos de aprendizaje automático en microcontroladores diminutos —chips de céntimos, con kilobytes de memoria y potencia de miliwatios, que pueden funcionar años con una pila de botón—. La idea desafía la imagen de la IA como algo que necesita centros de datos: un modelo suficientemente comprimido puede detectar una palabra clave ("oye, asistente"), reconocer un gesto, clasificar un sonido o detectar una anomalía en una máquina, todo localmente y con un consumo ínfimo. Se logra con las técnicas de optimización de inferencia de la categoría de IA llevadas al extremo: **cuantización** (usar 8 bits o menos en vez de 32), **poda** (eliminar conexiones prescindibles) y **destilación** (entrenar un modelo pequeño que imite a uno grande). TinyML habilita miles de millones de dispositivos inteligentes y siempre activos —el sensado ubicuo del Internet de las cosas— sin depender de la red ni de la batería.

## Aceleradores: GPU, TPU, NPU

La IA moderna no corre bien en un procesador de propósito general (CPU): su cómputo son sobre todo **multiplicaciones de matrices** masivamente paralelas, y para eso hacen falta chips especializados —**aceleradores**—:

- **GPU** (*Graphics Processing Unit*): nació para gráficos (millones de píxeles en paralelo) y resultó ideal para IA por ese mismo paralelismo masivo. Es el caballo de batalla del entrenamiento de modelos grandes; flexible y con un ecosistema de software maduro. Su límite es el consumo energético y el coste.
- **TPU** (*Tensor Processing Unit*): chip diseñado por Google **específicamente** para las operaciones de redes neuronales. Al renunciar a la flexibilidad de la GPU, gana eficiencia en su tarea concreta —más rendimiento por vatio para cargas de IA a escala—.
- **NPU** (*Neural Processing Unit*): acelerador de IA integrado en dispositivos de consumo (teléfonos, portátiles) para ejecutar **inferencia en el borde** con muy baja energía. Es lo que permite que un móvil procese fotos, voz o traducción localmente sin agotar la batería ni recurrir a la nube.

El patrón general es la **especialización**: a medida que una carga de cómputo se vuelve dominante y estable, migra de hardware general (CPU) a hardware dedicado (GPU → TPU/NPU), ganando eficiencia a cambio de flexibilidad. Los chips neuromórficos son el extremo especulativo de esa misma tendencia, apostando por una arquitectura radicalmente distinta para la eficiencia definitiva. Toda la IA de esta biblioteca —del entrenamiento en la nube a la inferencia en tu bolsillo— descansa sobre esta pirámide de silicio especializado.

## Ideas clave

- La computación neuromórfica imita al cerebro integrando memoria y cómputo y usando redes de picos que solo gastan energía al disparar; muy eficiente para sensado de baja potencia, pero difícil de entrenar y aún inmadura.
- El borde procesa en el dispositivo (baja latencia, privacidad, sin conexión, más gasto local) y la nube en centros remotos (potencia bruta); se combinan en un continuo según qué importe en cada tarea.
- TinyML lleva modelos a microcontroladores de miliwatios mediante cuantización, poda y destilación, habilitando miles de millones de dispositivos inteligentes siempre activos.
- La IA corre en aceleradores por su cómputo matricial paralelo: GPU (flexible, entrenamiento), TPU (dedicada a redes, más eficiente a escala) y NPU (inferencia de bajo consumo en el dispositivo).
- El patrón es la especialización creciente del hardware (CPU → GPU → TPU/NPU → neuromórfico), que gana eficiencia a costa de flexibilidad y sostiene toda la IA moderna.

## Para seguir

Estos chips y luces se fabrican con materiales, y los avances de frontera empiezan a menudo en el laboratorio de materiales. La próxima lección abre ese frente: *materiales avanzados y energía*.
