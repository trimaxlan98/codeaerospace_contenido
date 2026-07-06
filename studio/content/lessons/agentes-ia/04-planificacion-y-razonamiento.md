---
title: Planificación y razonamiento
level: avanzado
summary: Cómo un agente descompone tareas complejas, las cadenas y árboles de pensamiento, el ciclo planificar-ejecutar-verificar, la reflexión y autocorrección, y los límites reales del razonamiento agéntico en horizontes largos.
tags: [planificacion, razonamiento, chain-of-thought, reflexion, autocorreccion]
minutes: 12
order: 4
---

## Objetivos

- Entender por qué las tareas complejas exigen descomposición explícita.
- Distinguir cadena de pensamiento de árbol de pensamiento y cuándo aporta cada uno.
- Explicar el ciclo planificar-ejecutar-verificar como esqueleto de un agente robusto.
- Comprender la reflexión y la autocorrección como forma de aprender de los errores dentro de una tarea.
- Reconocer los límites actuales: horizonte largo, acumulación de errores y olvidos.

## Por qué descomponer

Un objetivo como "migra este servicio a la nueva API y verifica que todo sigue funcionando" no se resuelve en un salto: es demasiado grande para razonarlo de una vez y demasiado incierto para planificarlo entero de antemano. La **descomposición de tareas** —partir un objetivo grande en subtareas manejables— es la primera habilidad de un agente competente. Reduce la complejidad de cada paso (el modelo razona mejor sobre problemas pequeños), hace el progreso medible (se ve qué subtareas están hechas) y permite recuperarse de fallos localizados sin rehacer todo.

Hay dos estilos. La **planificación anticipada**: el agente traza al inicio un plan completo de subtareas y lo ejecuta. Es ordenada y auditable, pero frágil si el entorno sorprende (un paso falla y el plan queda obsoleto). Y la **planificación reactiva** (el ReAct de la lección 2): decidir el siguiente paso sobre la marcha según lo observado. Es flexible pero puede perder de vista el objetivo global. Los agentes maduros combinan ambas: un plan de alto nivel que da dirección, ejecutado paso a paso con capacidad de **replanificar** cuando la realidad se desvía de lo previsto.

## Cadenas y árboles de pensamiento

La observación que desbloqueó el razonamiento en LLMs es simple: **pedirle al modelo que piense paso a paso antes de responder mejora drásticamente los resultados** en tareas de varios pasos. Es la **cadena de pensamiento** (*chain-of-thought*, CoT): en lugar de saltar a la conclusión, el modelo escribe el razonamiento intermedio, y ese "pensar en voz alta" le da espacio de cómputo para no equivocarse. Los modelos de razonamiento recientes (la línea o1 y sucesores) internalizan esto: dedican más cómputo *en inferencia* a razonar largo antes de contestar —escalar el pensamiento, no solo el tamaño, como anticipaba la lección de hitos de IA—.

La cadena es lineal: una sola línea de razonamiento. Cuando un problema admite varios caminos y no está claro cuál funciona, el **árbol de pensamiento** (*tree-of-thought*) generaliza: el agente explora varias ramas de razonamiento en paralelo, evalúa cuáles prometen y poda las que no, como una búsqueda. Es más caro pero potente en problemas con espacio de soluciones amplio (puzzles, planificación combinatoria). En medio hay técnicas como la **autoconsistencia**: generar varias cadenas independientes y quedarse con la respuesta mayoritaria, que corrige errores aleatorios de una sola cadena.

## Planificar, ejecutar, verificar

El esqueleto de un agente robusto es un ciclo de tres tiempos que conviene hacer explícito:

1. **Planificar**: decidir el siguiente paso (o el plan) a la luz del objetivo y del estado actual.
2. **Ejecutar**: llevarlo a cabo con las herramientas (lección 2).
3. **Verificar**: comprobar que el paso logró lo que pretendía *antes* de seguir.

El tercer tiempo es el que más se descuida y el más valioso. Un agente que actúa sin verificar acumula errores en silencio: da por bueno un paso fallido y construye sobre arena. La verificación cierra el lazo con la realidad —¿el archivo se escribió?, ¿el test pasa?, ¿la cifra cuadra?— y es lo que distingue a los agentes fiables. Cuando existe una **señal de verificación objetiva** (ejecutar un test, compilar, comparar con un resultado esperado), el agente puede autocorregirse con solidez; por eso los dominios verificables como la programación son donde los agentes rinden mejor. Donde no la hay, la verificación es más difícil y arriesgada.

## Reflexión y autocorrección

La **reflexión** lleva la verificación un paso más allá: no solo comprobar si un paso funcionó, sino, cuando *no* funcionó, razonar sobre *por qué* y ajustar la estrategia. El patrón: el agente intenta, observa el fallo, genera una crítica de lo que salió mal, y reintenta incorporando esa lección —un pequeño bucle de aprendizaje *dentro* de la misma tarea, sin reentrenar el modelo—. Aplicado a código: escribir una función, correr los tests, leer el error, entender la causa, corregir, repetir hasta verde. Esta autocorrección iterativa es una de las razones de que los agentes de programación funcionen tan bien.

La reflexión tiene límites: el modelo no siempre diagnostica bien su propio error (a veces "corrige" en la dirección equivocada), y una crítica errónea puede empeorar las cosas. Ayuda anclar la reflexión en señales externas (el mensaje de error real, no la opinión del modelo sobre él) y limitar los intentos para no caer en bucles de correcciones que van y vuelven.

## Los límites reales

Conviene el realismo sobre lo que estos agentes *no* hacen bien todavía:

- **Horizonte largo**: cuantos más pasos requiere una tarea, más probable es que algo se tuerza. La fiabilidad por paso, aunque alta, se **compone**: 99 % por paso son ~60 % de éxito a los 50 pasos. Las tareas de cientos de pasos siguen siendo frágiles.
- **Acumulación de errores**: sin verificación estricta, los fallos se propagan y amplifican; un dato equivocado temprano contamina todo lo que viene después.
- **Olvidos y deriva de objetivo**: en tareas largas el agente puede perder de vista la meta original, repetir trabajo o quedar atrapado en bucles —problemas que la gestión de contexto y memoria (lección 3) mitigan pero no eliminan—.
- **Confianza mal calibrada**: el agente puede estar seguro cuando yerra, igual que alucina un LLM; su seguridad no es garantía de acierto.

La conclusión de diseño: los agentes actuales brillan en tareas de horizonte medio, verificables y acotadas, con supervisión humana en los puntos de mayor riesgo. Empujar el horizonte, la fiabilidad y la autonomía sin perder control es, precisamente, la frontera que abre la categoría de IA Agéntica.

## Ideas clave

- Descomponer un objetivo grande en subtareas hace cada paso manejable y el progreso medible; los agentes maduros combinan un plan de alto nivel con ejecución reactiva y capacidad de replanificar.
- La cadena de pensamiento (razonar paso a paso) mejora mucho las tareas complejas; el árbol de pensamiento explora varias ramas y la autoconsistencia vota entre varias cadenas.
- Planificar-ejecutar-verificar es el esqueleto robusto; la verificación —a menudo omitida— cierra el lazo con la realidad y es sólida cuando hay una señal objetiva (como en código).
- La reflexión razona sobre *por qué* falló un paso y reintenta con la lección aprendida, un bucle de mejora dentro de la tarea; funciona mejor anclada en errores externos reales y con intentos limitados.
- Límites reales: la fiabilidad por paso se compone y hunde el éxito en horizontes largos; hay acumulación de errores, deriva de objetivo y confianza mal calibrada. Los agentes rinden en tareas acotadas, verificables y supervisadas.

## Para seguir

Si los agentes tienen tantos límites, ¿cómo saber si uno es bueno de verdad? La última lección de la categoría trata la *evaluación de agentes*: benchmarks, métricas, el LLM-juez y la observabilidad en producción.
