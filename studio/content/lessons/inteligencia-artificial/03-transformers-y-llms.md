---
title: Transformers y grandes modelos de lenguaje
level: medio
summary: El mecanismo de atención, la arquitectura Transformer, la tokenización, las tres fases de entrenamiento de un LLM (pre-entrenamiento, ajuste fino, RLHF) y las leyes de escala que explican su capacidad.
tags: [transformers, atencion, llm, tokenizacion, rlhf, escala]
minutes: 13
order: 3
---

## Objetivos

- Entender qué problema resuelve el mecanismo de atención y leer la fórmula $\text{softmax}(QK^T/\sqrt{d_k})V$.
- Describir la arquitectura Transformer y por qué desplazó a las redes recurrentes.
- Explicar la tokenización y por qué el modelo "ve" fragmentos, no palabras ni letras.
- Distinguir las tres fases: pre-entrenamiento, ajuste fino y RLHF, y qué aporta cada una.
- Comprender las leyes de escala y el significado de la ventana de contexto.

## El problema que resolvió la atención

Antes de 2017, procesar lenguaje se hacía con **redes recurrentes** (RNN, LSTM): leían la frase palabra por palabra, arrastrando un estado que resumía lo visto. Dos defectos las lastraban. Primero, la **secuencialidad**: para procesar la palabra 100 hay que haber procesado las 99 anteriores, lo que impide paralelizar y hace lentísimo el entrenamiento sobre corpus enormes. Segundo, la **memoria corta**: la información de palabras lejanas se diluye en el estado, y frases con dependencias largas ("El *libro* que compré en aquella tienda que cerró el año pasado *estaba* descatalogado") confunden al modelo.

El **mecanismo de atención** resuelve ambos de un golpe. En lugar de comprimir el pasado en un estado, permite que cada palabra "mire" directamente a todas las demás y decida cuáles son relevantes para ella, sin importar la distancia. Y como cada palabra hace ese cálculo independientemente, todo se paraleliza. El artículo que lo formalizó, *Attention Is All You Need* (2017), llevó la idea al extremo: eliminó por completo la recurrencia y construyó una arquitectura hecha solo de atención y capas densas. La llamó **Transformer**.

## Cómo funciona la atención

La atención trabaja con tres vectores derivados de cada token, con nombres tomados de las bases de datos. La **consulta** (*query*, $Q$) representa "qué estoy buscando"; la **clave** (*key*, $K$), "qué ofrezco"; el **valor** (*value*, $V$), "qué información entrego si me eligen". Para cada token, se compara su query con las keys de todos los tokens (producto escalar: mide afinidad), se normalizan esas afinidades en pesos que suman 1 con softmax, y se produce una suma ponderada de los values. La fórmula compacta:

$$\text{Attention}(Q,K,V) = \text{softmax}\!\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

El término $QK^T$ es la matriz de todas las afinidades entre pares de tokens; la división por $\sqrt{d_k}$ (la dimensión de las keys) estabiliza la escala para que el softmax no se sature; el softmax convierte afinidades en pesos; y multiplicar por $V$ mezcla la información según esos pesos. Los Transformers usan **atención multi-cabeza**: varias atenciones en paralelo, cada una atendiendo a un tipo de relación distinto (una a la concordancia gramatical, otra a la correferencia, etc.), cuyos resultados se combinan.

## La arquitectura Transformer

Un Transformer apila **bloques** idénticos, cada uno con dos subcapas: la atención multi-cabeza y una red densa posición a posición, ambas envueltas en conexiones residuales y normalización que estabilizan el entrenamiento de redes muy profundas (decenas o cientos de bloques). Como la atención por sí sola no distingue el orden ("perro muerde hombre" y "hombre muerde perro" tendrían los mismos tokens), se añaden **codificaciones posicionales** que inyectan la posición de cada token.

El diseño original tenía dos mitades —un **codificador** que comprende la entrada y un **decodificador** que genera la salida—, ideal para traducción. Pero la familia dominante hoy, los GPT, usa **solo el decodificador**: son modelos **autorregresivos** que generan texto un token a la vez, cada uno condicionado por todos los anteriores, con atención *causal* (cada token solo mira hacia atrás, nunca al futuro que aún no existe). Generar una respuesta es repetir: predecir el siguiente token, añadirlo, volver a predecir.

## Tokenización: lo que el modelo realmente ve

Un LLM no procesa letras ni palabras, sino **tokens**: fragmentos de texto de tamaño intermedio producidos por un algoritmo como *Byte-Pair Encoding*. Palabras comunes son un token ("casa"); palabras raras o largas se parten en varios ("anticonstitucionalmente" → varios tokens); un espacio suele ir pegado al token siguiente. Un vocabulario típico ronda los 100 000 tokens, y como regla de bolsillo, en inglés un token equivale a ~0,75 palabras (en español algo menos, por su morfología más rica).

Esto explica varias rarezas prácticas. Que un modelo tropiece al contar las letras de una palabra: no las ve, ve el token entero. Que el coste de la API se mida en tokens, no en palabras. Y que el "tamaño" de lo que un modelo puede leer se exprese en tokens: la **ventana de contexto**.

## Las tres fases de un asistente

Un LLM útil no sale de una sola fase de entrenamiento, sino de tres encadenadas:

1. **Pre-entrenamiento.** Sobre billones de tokens de texto de Internet, el modelo aprende una única tarea autosupervisada: predecir el siguiente token. Es la fase carísima (semanas de miles de GPUs) y de ella emerge, como subproducto de predecir bien, un vasto conocimiento del mundo, gramática, razonamiento y estilo. El resultado es un **modelo base**: sabe mucho pero solo sabe *continuar* texto, no conversar ni obedecer.
2. **Ajuste fino supervisado** (*SFT*). Se entrena el modelo base sobre miles de ejemplos de instrucción-respuesta escritos por humanos, enseñándole el formato de "asistente que responde a lo que se le pide". Convierte un continuador de texto en un modelo que sigue instrucciones.
3. **Aprendizaje por refuerzo con retroalimentación humana** (*RLHF*). Humanos comparan respuestas y marcan cuál prefieren; con esas preferencias se entrena un modelo de recompensa, y con él se afina la política del asistente para producir respuestas más útiles, honestas e inofensivas. Es la fase que dio a ChatGPT su tono y su alineación (y reaparece en la lección de ética). Variantes recientes reemplazan parte de esto por preferencias directas (DPO) o refuerzo sobre tareas verificables para potenciar el razonamiento.

## Leyes de escala y ventana de contexto

El hallazgo que ordenó la última década se llama **leyes de escala** (*scaling laws*): el rendimiento de un LLM mejora de forma predecible, siguiendo una ley de potencia, al aumentar tres factores acopladamente —el número de **parámetros**, la cantidad de **datos** y el **cómputo** de entrenamiento—. Predecible es la palabra clave: se puede estimar el rendimiento de un modelo gigante entrenando modelos pequeños, lo que convirtió la construcción de LLMs en una disciplina de ingeniería con presupuesto calculable. De aquí surgieron las **habilidades emergentes**: capacidades (aritmética de varios pasos, razonamiento) ausentes en modelos pequeños que aparecen al cruzar cierta escala. El trabajo de Chinchilla (2022) refinó la receta: para un cómputo dado, conviene equilibrar parámetros y datos, no solo agrandar el modelo.

La **ventana de contexto** es cuántos tokens puede considerar el modelo a la vez —su "memoria de trabajo"—: todo lo que exceda queda fuera. Ha crecido de ~2 000 tokens (GPT-3) a cientos de miles o millones en modelos recientes, lo que habilita leer libros o bases de código enteras. Pero no es gratis: el coste de la atención crece cuadráticamente con la longitud, y "tener" un contexto enorme no garantiza usarlo bien (el fenómeno de "perderse en el medio"). Gestionar ese recurso finito es, precisamente, el corazón de los agentes de IA que vienen después.

## Ideas clave

- La atención deja que cada token mire directamente a todos los demás y pondere su relevancia; elimina la secuencialidad y la memoria corta de las RNN y se paraleliza masivamente.
- $\text{softmax}(QK^T/\sqrt{d_k})V$: afinidades query-key normalizadas que mezclan los values; la versión multi-cabeza atiende a varios tipos de relación en paralelo.
- Los GPT son Transformers de solo decodificador, autorregresivos y causales: generan texto un token a la vez condicionados por lo anterior.
- El modelo ve tokens (fragmentos), no palabras; eso explica el conteo de coste, la ventana de contexto y ciertos errores de deletreo.
- Un asistente se forja en tres fases —pre-entrenamiento autosupervisado, SFT y RLHF— y su capacidad escala de forma predecible con parámetros, datos y cómputo, con habilidades que emergen al crecer.

## Para seguir

El Transformer no solo genera texto: la próxima lección lo extiende a imágenes, audio, video y código —la IA generativa multimodal— y examina cómo se evalúa y por qué alucina.
