---
title: IA generativa multimodal
level: medio
summary: Los modelos de difusión que crean imágenes a partir de ruido, los espacios compartidos tipo CLIP que unen texto e imagen, la generación de video, audio y código, y los límites de la evaluación y las alucinaciones.
tags: [generativa, difusion, clip, multimodal, alucinaciones, evaluacion]
minutes: 12
order: 4
---

## Objetivos

- Explicar, sin matemática pesada, cómo un modelo de difusión convierte ruido en una imagen.
- Entender qué es un espacio compartido texto-imagen (CLIP) y por qué habilita generar "a partir de una frase".
- Repasar el estado de la generación de video, audio y código.
- Reconocer por qué evaluar modelos generativos es intrínsecamente difícil.
- Comprender qué son las alucinaciones, por qué ocurren y cómo se mitigan.

## Generar es lo contrario de destruir: difusión

La familia dominante de generación de imágenes son los **modelos de difusión**, y su idea central es elegante por contraintuitiva. Durante el entrenamiento se toma una imagen real y se le añade ruido gaussiano poco a poco, en muchos pasos, hasta convertirla en estática pura —el proceso de **difusión hacia adelante**, que destruye información de forma controlada—. El modelo se entrena para la tarea inversa: dado un paso ruidoso, predecir el ruido que se añadió, es decir, dar un pequeño paso de *limpieza*.

Una vez entrenado, se genera partiendo de **ruido puro** y aplicando el modelo repetidamente: cada paso quita un poco de ruido, y tras decenas de iteraciones el ruido se ha organizado en una imagen coherente que nunca existió. Es "esculpir" una imagen a partir de estática. Los sistemas modernos (Stable Diffusion) hacen esto en un **espacio latente** comprimido en vez de sobre los píxeles, lo que abarata enormemente el cómputo. La difusión desplazó a las **GAN** (redes generativas adversarias, dos redes compitiendo) que dominaron 2014-2020, por ser más estables de entrenar y más diversas en sus resultados.

## El puente entre palabras e imágenes: CLIP

Falta explicar cómo una *frase* dirige la generación. La pieza es un modelo tipo **CLIP**, entrenado sobre cientos de millones de pares imagen-descripción extraídos de la web. CLIP aprende a mapear tanto imágenes como textos a un **espacio compartido** de vectores, de modo que la imagen de un gato y el texto "un gato" caen cerca, y lejos del texto "un coche". Es un espacio semántico común a dos modalidades.

Con ese puente, la generación condicionada por texto se vuelve natural: la frase del usuario se convierte en un vector en el espacio compartido, y ese vector *guía* cada paso de limpieza del modelo de difusión hacia imágenes cuya semántica coincide con la descripción. El mismo principio de "proyectar modalidades distintas a un espacio común" es la base de los **modelos multimodales** que aceptan imágenes como entrada junto al texto: la imagen se codifica en vectores que el Transformer procesa igual que tokens de texto, permitiéndole describir fotos, leer gráficos o razonar sobre diagramas.

## Video, audio y código

- **Video.** Extiende la difusión a la dimensión temporal: hay que generar fotogramas coherentes entre sí, no solo cada uno por separado. El reto es la consistencia (que un objeto no cambie de forma entre cuadros) y la física plausible (que las cosas se muevan de forma creíble). Los sistemas de 2024-2025 producen clips de segundos a decenas de segundos con calidad notable, y se investiga si estos modelos aprenden implícitamente un "modelo del mundo".
- **Audio.** Cubre tres frentes: **habla** (texto a voz de calidad casi humana, y clonación de voz —con sus riesgos—), **música** (generación de pistas a partir de una descripción) y **efectos**. Técnicamente combina tokenización del audio y difusión o modelos autorregresivos.
- **Código.** Un caso especialmente productivo, porque el código es texto con estructura estricta y —crucialmente— **verificable**: se puede ejecutar y probar. Los LLM entrenados con mucho código autocompletan, traducen entre lenguajes, explican y depuran, y son la base de los agentes de programación de la categoría siguiente. La verificabilidad permite entrenar con refuerzo sobre tests que pasan o fallan, una señal más limpia que el juicio humano.

## Por qué evaluar es tan difícil

En clasificación, evaluar es trivial: acertó o no. En generación no hay una única respuesta correcta —hay infinitas imágenes válidas para "un atardecer"— y la calidad es en parte subjetiva. Esto hace la evaluación un problema abierto. Se usan varias aproximaciones, todas imperfectas:

- **Benchmarks automáticos**: bancos de preguntas con respuesta conocida (MMLU para conocimiento, HumanEval para código, etc.). Cómodos y reproducibles, pero con un defecto grave: la **contaminación**, cuando las preguntas del benchmark aparecieron en los datos de entrenamiento y el modelo las "recuerda" en vez de resolverlas. Además saturan: los modelos alcanzan el techo y el benchmark deja de discriminar.
- **Evaluación humana**: personas puntúan o comparan salidas. Es el patrón oro para calidad percibida pero es cara, lenta y ruidosa.
- **Arenas de preferencia**: usuarios votan a ciegas entre dos respuestas (estilo Elo). Capturan preferencia real pero premian el estilo agradable tanto como la corrección.
- **LLM como juez**: usar un modelo potente para evaluar a otro. Escalable y barato, pero hereda sesgos (favorece respuestas largas, o las de su propia familia) —un tema que la categoría de agentes retoma en profundidad—.

La moraleja: ningún número resume la calidad de un modelo generativo; hay que triangular varias medidas y desconfiar de las cifras redondas.

## Alucinaciones

La limitación más discutida de la IA generativa es la **alucinación**: producir contenido fluido y convincente pero **falso** —una cita inventada, un dato erróneo, un caso legal inexistente—. No es un fallo ocasional, es una consecuencia del diseño. Un LLM está entrenado para producir la continuación *más plausible*, no la más *verdadera*; no tiene un modelo separado de "lo que sé" frente a "lo que suena bien", y cuando no sabe algo, generar una respuesta verosímil es exactamente lo que su entrenamiento premia. La fluidez, que hace útiles a estos modelos, es también lo que hace sus errores peligrosos: suenan igual de seguros cuando aciertan que cuando inventan.

Las mitigaciones actúan en varios niveles: **anclar en fuentes** (RAG, recuperar documentos reales y pedir que responda solo con ellos —tema central de los agentes—), **uso de herramientas** (buscar, calcular o consultar una base en vez de "recordar"), **calibración** (entrenar al modelo para expresar incertidumbre y decir "no lo sé"), y **verificación** (comprobar afirmaciones contra fuentes). Ninguna las elimina; reducen su frecuencia. La conclusión práctica, que enlaza con la última lección de la categoría, es que la salida de un modelo generativo es un *borrador que requiere verificación humana* en cualquier contexto donde la verdad importe.

## Ideas clave

- La difusión genera aprendiendo a *quitar* ruido: se entrena destruyendo imágenes con ruido y se usa partiendo de ruido puro, limpiándolo paso a paso hasta una imagen nueva.
- CLIP mapea texto e imagen a un espacio compartido; ese puente permite dirigir la generación con una frase y es la base de los modelos multimodales que "ven".
- Video (consistencia temporal), audio (habla, música) y código (verificable, base de los agentes) extienden la generación, cada uno con sus retos.
- Evaluar generación es difícil porque no hay respuesta única: benchmarks (con riesgo de contaminación), evaluación humana, arenas de preferencia y LLM-juez, todos imperfectos.
- Las alucinaciones son inherentes: el modelo optimiza plausibilidad, no verdad; se mitigan con anclaje en fuentes, herramientas, calibración y verificación, pero no se eliminan.

## Para seguir

La última lección de esta categoría cierra con lo que rodea a toda esta potencia: los sesgos, la privacidad, la alineación y la regulación —la ética y seguridad de la IA— antes de pasar a los agentes que la ponen a actuar.
