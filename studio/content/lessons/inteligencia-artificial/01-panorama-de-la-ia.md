---
title: Panorama de la IA moderna
level: intro
summary: De la IA simbólica al aprendizaje profundo y la IA generativa, las tareas fundamentales, el ciclo de vida datos-entrenamiento-inferencia y los hitos de 2012 a 2025.
tags: [ia, machine-learning, deep-learning, historia, generativa]
minutes: 10
order: 1
---

## Objetivos

- Distinguir la IA simbólica del aprendizaje automático y ubicar ML, DL y GenAI como subconjuntos anidados.
- Clasificar las tareas fundamentales: clasificación, regresión y generación, con sus paradigmas de aprendizaje.
- Describir el ciclo de vida completo: datos → entrenamiento → evaluación → inferencia.
- Recorrer los hitos que definieron la década 2012–2025 y qué demostró cada uno.
- Adquirir el vocabulario base que usan el resto de lecciones de esta categoría y las de agentes.

## Dos tradiciones: reglas contra aprendizaje

La inteligencia artificial nació en 1956 (la conferencia de Dartmouth) con una apuesta que hoy llamamos **IA simbólica**: la inteligencia como manipulación de símbolos mediante reglas explícitas. Sus frutos —sistemas expertos con miles de reglas si-entonces, planificadores lógicos, el ajedrez de Deep Blue (1997)— compartían una virtud y un techo. La virtud: transparencia total, cada conclusión es rastreable a sus reglas. El techo: alguien tiene que *escribir* las reglas, y las tareas más humanas —reconocer un rostro, entender una frase ambigua— resultaron imposibles de reglamentar a mano, porque nuestro propio conocimiento de cómo las hacemos es tácito (la llamada paradoja de Polanyi: sabemos más de lo que podemos decir).

El **aprendizaje automático** (*machine learning*, ML) invierte el enfoque: en lugar de programar la solución, se programa un modelo con parámetros ajustables y un procedimiento que los ajusta automáticamente a partir de **ejemplos**. El programa ya no contiene el conocimiento; contiene la maquinaria para extraerlo de los datos. El **aprendizaje profundo** (*deep learning*, DL) es el subconjunto del ML que usa redes neuronales de muchas capas, capaces de aprender no solo la decisión final sino las *representaciones intermedias* (rasgos, conceptos) que la sustentan —eliminando la ingeniería manual de características que el ML clásico requería. Y la **IA generativa** (GenAI) es el subconjunto del DL cuyos modelos no se limitan a clasificar o predecir un valor, sino que **producen contenido nuevo**: texto, imágenes, audio, código. La relación es de muñecas rusas: GenAI ⊂ DL ⊂ ML ⊂ IA, y conviene resistir el uso periodístico de "IA" como sinónimo del círculo más interno.

## Las tareas y los paradigmas de aprendizaje

Casi todo el ML aplicado se reduce a unas pocas formas de tarea. La **clasificación** asigna una entrada a una de $k$ categorías discretas (¿este correo es spam?, ¿qué dígito es esta imagen?); su salida típica es una distribución de probabilidad sobre las clases. La **regresión** predice un valor continuo (el precio de una vivienda, la demanda eléctrica de mañana). La **generación** produce objetos estructurados completos —una frase, una imagen, una molécula— y puede verse como una cascada de clasificaciones (un modelo de lenguaje genera texto eligiendo el siguiente token entre ~100 000 opciones, una y otra vez). Tareas aparentemente distintas se reducen a estas: detectar objetos en una imagen combina clasificación (qué es) y regresión (dónde está); traducir es generación condicionada.

Los paradigmas de entrenamiento se distinguen por la señal disponible. En el **aprendizaje supervisado**, cada ejemplo trae su respuesta correcta (imagen + etiqueta); es el más eficaz y el más caro, porque etiquetar cuesta trabajo humano. En el **no supervisado**, solo hay datos sin etiquetas y el objetivo es descubrir estructura (agrupamientos, dimensiones latentes). El **autosupervisado** —el motor de la era actual— fabrica la supervisión desde los propios datos: ocultar la siguiente palabra de un texto y entrenar al modelo para predecirla convierte todo el texto de Internet en ejemplos etiquetados gratis. Y en el **aprendizaje por refuerzo** (RL), un agente aprende actuando: recibe recompensas por resultados y ajusta su política para maximizarlas —el paradigma de AlphaGo, y también de la fase final del entrenamiento de los asistentes de lenguaje modernos.

## El ciclo de vida: datos, entrenamiento, inferencia

Todo sistema de ML real recorre el mismo ciclo. Primero, los **datos**: recolección, limpieza, deduplicación y filtrado —la parte menos glamorosa y más determinante; el principio *garbage in, garbage out* no tiene excepciones, y los sesgos del dato se heredan al modelo (tema de la última lección de esta categoría). El conjunto se divide en **entrenamiento**, **validación** (para elegir hiperparámetros sin hacer trampa) y **prueba** (tocado una sola vez, al final, para estimar el rendimiento real).

Segundo, el **entrenamiento**: se define una función de pérdida que mide cuán mal predice el modelo, y un optimizador ajusta los parámetros para reducirla, iterando sobre los datos (la mecánica exacta —gradientes, backpropagation— es el tema de la siguiente lección). En los modelos grandes actuales, esta fase consume semanas de miles de GPUs y es la partida de costo dominante: de ahí la distinción moderna entre **pre-entrenamiento** (aprender de todo el corpus, una vez, carísimo) y **ajuste fino** (*fine-tuning*: especializar el modelo pre-entrenado con pocos datos propios, barato) que hace económicamente viable el ecosistema.

Tercero, la **inferencia**: el modelo entrenado, con sus parámetros congelados, responde a entradas nuevas en producción. Sus economías son opuestas a las del entrenamiento: costo pequeño por consulta pero multiplicado por millones de consultas, con requisitos de latencia que el entrenamiento no tiene. Optimizar inferencia (cuantización a menos bits, destilación a modelos menores, cachés) es hoy una disciplina en sí misma. Alrededor del ciclo completo orbita el **MLOps**: monitorizar la deriva de los datos reales respecto a los de entrenamiento, reentrenar, versionar y evaluar continuamente —porque un modelo desplegado se degrada en silencio cuando el mundo cambia y sus datos de entrenamiento envejecen.

## Hitos 2012–2025: la década que cambió todo

| Año | Hito | Qué demostró |
|-----|------|--------------| 
| 2012 | AlexNet gana ImageNet | Las redes profundas + GPUs + datos masivos baten a décadas de visión artificial manual; arranca la era DL |
| 2014 | GANs; seq2seq | Generación adversaria de imágenes; la traducción neuronal extremo a extremo |
| 2016 | AlphaGo vence a Lee Sedol | RL profundo + búsqueda supera al campeón humano en el juego considerado inabordable |
| 2017 | *Attention Is All You Need* | El Transformer: la arquitectura que unificará lenguaje, visión y más |
| 2018–19 | BERT, GPT-2 | Pre-entrenamiento autosupervisado sobre texto masivo + ajuste fino como paradigma universal del NLP |
| 2020 | GPT-3 (175 B); AlphaFold 2 | La escala produce habilidades emergentes (few-shot); la IA resuelve el plegamiento de proteínas |
| 2022 | Stable Diffusion, DALL·E 2; ChatGPT | Generación de imágenes abierta al público; el RLHF convierte un modelo de lenguaje en asistente conversacional — 100 M de usuarios en 2 meses |
| 2023 | GPT-4; LLaMA y los pesos abiertos | Multimodalidad y razonamiento de nivel profesional; la comunidad de modelos abiertos despega |
| 2024 | o1 y el razonamiento en inferencia; premios Nobel a Hinton/Hassabis | Escalar el *cómputo al pensar* (cadenas largas de razonamiento) como nueva palanca; consagración científica del campo |
| 2025 | Agentes que operan software y escriben código de forma sostenida | Del chat a la acción: modelos que ejecutan tareas de horizonte largo con herramientas |

Tres lecturas del conjunto. Primera: la palanca dominante de la década fue la **escala** (datos, parámetros, cómputo), formalizada en las leyes de escalamiento que se verán en la lección de Transformers. Segunda: el paradigma ganador fue el **autosupervisado sobre datos masivos** seguido de alineamiento con preferencias humanas. Tercera: la frontera se movió de *percibir* (2012–2016) a *generar* (2020–2023) y ahora a **actuar** (2024–), transición que motiva la categoría entera de Agentes de IA que sigue a esta.

## Ideas clave

- IA simbólica: conocimiento escrito como reglas, transparente pero limitada por lo que sabemos explicitar; ML: el conocimiento se extrae de ejemplos; DL: además se aprenden las representaciones; GenAI: además se produce contenido nuevo.
- Las tareas base son clasificación (categorías), regresión (valores continuos) y generación (objetos estructurados); los paradigmas —supervisado, no supervisado, autosupervisado, refuerzo— se distinguen por la señal de aprendizaje disponible.
- El ciclo real es datos → entrenamiento → evaluación → inferencia, con los datos como factor determinante, el pre-entrenamiento + fine-tuning como estructura económica, y la inferencia como el costo operativo que domina a escala.
- 2012–2025: de AlexNet al Transformer, de la escala emergente de GPT-3 al alineamiento de ChatGPT, y del chat a los agentes; la palanca constante fue escalar cómputo y datos.
- El campo se movió de percibir a generar y ahora a actuar — el contexto de todo lo que sigue en esta biblioteca.

## Para seguir

La siguiente lección, *Redes neuronales desde cero*, abre la caja: la neurona artificial, el descenso de gradiente y la retropropagación que hacen funcionar todo lo descrito aquí.
