---
title: Memoria y gestión de contexto
level: medio
summary: La ventana de contexto como recurso finito, la memoria de corto y largo plazo, RAG (embeddings, chunking y recuperación), los resúmenes progresivos y la memoria persistente en archivos que da continuidad a un agente.
tags: [memoria, contexto, rag, embeddings, chunking, persistencia]
minutes: 12
order: 3
---

## Objetivos

- Ver la ventana de contexto como un presupuesto que hay que administrar, no un almacén infinito.
- Distinguir memoria de corto plazo (contexto) de memoria de largo plazo (externa).
- Explicar RAG de principio a fin: embeddings, chunking, recuperación e inyección.
- Entender los resúmenes progresivos para tareas que exceden la ventana.
- Comprender la memoria persistente en archivos como continuidad entre sesiones.

## El contexto es un recurso finito

La **ventana de contexto** es todo lo que el modelo puede "ver" en un momento dado: la instrucción del sistema, el historial de la conversación, los resultados de herramientas, los documentos recuperados. Aunque las ventanas modernas sean grandes (cientos de miles de tokens), son **finitas**, tienen **coste** (más tokens, más dinero y más latencia) y —lo menos obvio— el modelo **no las aprovecha uniformemente**: tiende a prestar más atención al principio y al final que al medio (el fenómeno "perdido en el medio"). La consecuencia práctica: llenar el contexto hasta el tope no mejora, a veces empeora. Un agente que trabaja muchos pasos genera muchísima información —cada acción produce una observación— y desbordaría la ventana enseguida si la volcara toda.

Por eso la **gestión de contexto** es una disciplina central del diseño de agentes: decidir, en cada paso, qué información merece ocupar el espacio escaso del contexto y qué debe vivir fuera de él y traerse solo cuando haga falta. Es administrar un presupuesto, no acumular.

## Corto plazo y largo plazo

Conviene separar dos memorias por analogía con la humana:

- **Memoria de corto plazo (o de trabajo)**: es el propio contexto —lo que el agente tiene presente *ahora*: el objetivo, los últimos pasos, los datos recientes—. Es rápida y directa pero volátil y limitada; se pierde al cerrar la sesión y se satura en tareas largas.
- **Memoria de largo plazo**: información guardada *fuera* del modelo —en una base de datos, un almacén vectorial, archivos— que persiste indefinidamente y se recupera selectivamente para traerla al contexto cuando es relevante. Es el conocimiento del agente sobre el usuario, sobre tareas pasadas, sobre documentos que no caben todos a la vez.

El arte está en el flujo entre ambas: llevar de la memoria larga a la corta solo lo pertinente para el paso actual, y de la corta a la larga lo que valga la pena conservar. Ese flujo es lo que las dos secciones siguientes concretan.

## RAG: recuperar en lugar de recordar

La técnica dominante para dar a un agente acceso a conocimiento que no cabe en el contexto (ni estaba en su entrenamiento) es **RAG** (*Retrieval-Augmented Generation*, generación aumentada por recuperación). También es la principal mitigación de alucinaciones vista en Inteligencia Artificial: en vez de "recordar" un dato de sus parámetros, el agente lo *busca* en una fuente real y responde a partir de ella. El flujo, en cuatro pasos:

1. **Chunking** (troceado). Los documentos se parten en fragmentos manejables (párrafos, secciones). El tamaño importa: trozos muy grandes diluyen la relevancia y gastan contexto; muy pequeños pierden el hilo. A menudo se solapan un poco para no cortar ideas a la mitad.
2. **Embeddings** (incrustaciones). Cada fragmento se convierte en un **vector** —una lista de números que captura su *significado*—, usando un modelo de embeddings. La propiedad clave: textos de significado parecido dan vectores cercanos en el espacio, aunque usen palabras distintas. Todos los vectores se guardan en una **base de datos vectorial** indexada para búsqueda rápida por cercanía.
3. **Recuperación** (*retrieval*). Ante una consulta, se convierte también en vector y se buscan los fragmentos cuyos vectores están más cerca —los semánticamente más relevantes—. A menudo se combina esta búsqueda semántica con búsqueda por palabras clave (*búsqueda híbrida*) y un reordenamiento posterior para afinar.
4. **Aumento** (*augmentation*). Los fragmentos recuperados se **inyectan en el contexto** junto a la pregunta, y el modelo responde basándose en ellos, idealmente citando la fuente.

RAG transforma "el modelo tiene que saberlo" en "el modelo tiene que saber *buscarlo*", lo que permite conocimiento actualizado, verificable y específico de una organización sin reentrenar nada. Sus puntos débiles: si la recuperación falla (trae lo irrelevante o se pierde lo clave), la respuesta falla; de ahí que la calidad del *retrieval* sea a menudo el verdadero cuello de botella.

## Resúmenes progresivos

Cuando una tarea o conversación se alarga más allá de la ventana, la solución no es truncar sin criterio (se perdería información clave) sino **comprimir**. Los **resúmenes progresivos** condensan periódicamente la parte antigua del historial en un resumen compacto que preserva lo esencial —decisiones tomadas, hechos establecidos, estado actual— y descartan el detalle verboso. El contexto pasa a contener "el resumen de lo ocurrido + los últimos pasos en detalle", manteniéndose dentro del presupuesto sin perder el hilo. Los agentes de horizonte largo dependen de esto: sin compresión, una tarea de cientos de pasos sería imposible. El riesgo es que un resumen omita algo que luego resulte necesario, así que suele conservarse también un registro completo externo al que recurrir.

## Memoria persistente en archivos

La forma más simple y robusta de memoria de largo plazo es también una de las más potentes: **escribir en archivos**. Un agente puede mantener un archivo de notas, un registro de tareas, un documento con hechos aprendidos sobre el usuario o el proyecto, y **leerlo al empezar** cada sesión. Así la memoria sobrevive al cierre del contexto y da **continuidad entre sesiones**: el agente "recuerda" lo que aprendió ayer porque lo dejó escrito y lo relee hoy.

Ventajas frente a esquemas más sofisticados: es **legible y editable por humanos** (se puede inspeccionar y corregir lo que el agente cree saber), es **duradera** y no depende de infraestructura compleja, y funciona como memoria estructurada de la que se trae al contexto solo lo relevante. Es, en esencia, RAG sobre el propio cuaderno del agente. Este patrón —un índice de memoria que se carga al inicio y apunta a notas individuales— es la columna vertebral de los asistentes que mantienen conocimiento sobre un proyecto a lo largo del tiempo.

## Ideas clave

- La ventana de contexto es un presupuesto finito, costoso y aprovechado de forma desigual (se pierde en el medio); gestionarla —qué entra y qué vive fuera— es central en el diseño de agentes.
- Hay memoria de corto plazo (el contexto, rápida pero volátil y limitada) y de largo plazo (externa y persistente); el arte es mover a la corta solo lo relevante y guardar en la larga lo que valga.
- RAG recupera en vez de recordar: chunking → embeddings en una base vectorial → recuperación por cercanía semántica → inyección en contexto; da conocimiento actualizado y verificable y mitiga alucinaciones, con el retrieval como cuello de botella.
- Los resúmenes progresivos comprimen el historial antiguo para sostener tareas que exceden la ventana, conservando lo esencial y, a ser posible, un registro completo de respaldo.
- Escribir en archivos y releerlos da memoria persistente entre sesiones: duradera, legible y editable por humanos, y estructurada para traer solo lo relevante.

## Para seguir

Con herramientas y memoria resueltas, falta el cerebro que las orquesta hacia un objetivo complejo. La siguiente lección, *Planificación y razonamiento*, cubre la descomposición de tareas, las cadenas de pensamiento y la autocorrección.
