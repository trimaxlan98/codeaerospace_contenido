---
title: Evaluación de agentes
level: avanzado
summary: Cómo se mide si un agente sirve: los benchmarks (SWE-bench, GAIA, tau-bench), las métricas más allá del acierto (coste, pasos, latencia), la evaluación por LLM-juez y sus sesgos, y la observabilidad de trazas en producción.
tags: [evaluacion, benchmarks, swe-bench, llm-juez, observabilidad, metricas]
minutes: 12
order: 5
---

## Objetivos

- Entender por qué evaluar agentes es más difícil que evaluar modelos.
- Conocer los benchmarks de referencia y qué mide cada uno.
- Ir más allá de la tasa de éxito: coste, pasos, latencia y fiabilidad.
- Comprender la evaluación por LLM-juez y sus sesgos característicos.
- Valorar las trazas y la observabilidad como evaluación continua en producción.

## Por qué evaluar agentes es tan difícil

Evaluar un LLM ya era complicado (lección de IA generativa); evaluar un **agente** lo es más, por razones acumulativas. Un agente ejecuta **muchos pasos**, así que un fallo puede estar en cualquiera y la causa raíz es difícil de aislar. Es **no determinista**: la misma tarea puede resolverse por caminos distintos y dar resultados distintos entre corridas, de modo que una sola ejecución no dice mucho —hay que promediar varias—. Interactúa con un **entorno** que puede cambiar (una web se actualiza, una API responde distinto), lo que dificulta reproducir. Y a menudo hay **varias soluciones válidas**, sin una única respuesta correcta contra la que comparar. Por todo esto, no basta un número: evaluar agentes es un problema de ingeniería en sí mismo.

## Los benchmarks de referencia

La comunidad ha creado bancos de prueba para medir agentes en tareas realistas y verificables:

- **SWE-bench**: tareas reales de ingeniería de software extraídas de repositorios de código abierto —issues de GitHub con su corrección conocida—. El agente recibe el problema y el código, y su solución se valida ejecutando la **suite de tests real** del proyecto. Es el referente de agentes de programación precisamente porque el criterio de éxito es objetivo: los tests pasan o no.
- **GAIA**: preguntas de asistente general que requieren razonamiento de varios pasos, uso de herramientas y navegación web para resolverse —fáciles para humanos, difíciles para IA—. Mide agentes de propósito general.
- **tau-bench** (τ-bench): interacciones de atención al cliente en las que el agente debe seguir políticas, usar herramientas y conversar con un usuario (simulado) para completar tareas —evalúa fiabilidad en flujos con reglas y estado—.

Todos comparten la virtud de la **verificabilidad** (un criterio automático de éxito) y sufren los males habituales: la **contaminación** (que las tareas hayan filtrado a los datos de entrenamiento), la **saturación** (los modelos alcanzan el techo y el benchmark deja de discriminar) y la brecha entre el banco y el trabajo real. Un buen resultado en un benchmark es indicativo, no una garantía de utilidad en producción.

## Más allá de la tasa de éxito

La métrica reflejo es la **tasa de éxito** (qué fracción de tareas completa), pero en agentes es insuficiente porque *cómo* se resuelve importa tanto como *si* se resuelve. Un cuadro de métricas útil:

| Métrica | Qué captura | Por qué importa |
|---------|-------------|-----------------|
| Tasa de éxito | Fracción de tareas resueltas | La utilidad base, pero no lo es todo |
| Coste (tokens/$) | Recursos gastados por tarea | Un agente que acierta pero cuesta 100× puede ser inviable |
| Número de pasos | Eficiencia del camino | Menos pasos = menos coste, latencia y superficie de error |
| Latencia | Tiempo hasta terminar | Determina si sirve interactivamente |
| Fiabilidad | Consistencia entre corridas | Un agente que acierta 1 de cada 3 veces no es desplegable |
| Intervención humana | Cuánta ayuda necesitó | Mide la autonomía real |

La lectura conjunta revela compromisos: subir la tasa de éxito a base de más pasos y más cómputo puede no compensar. La frontera relevante es **éxito por unidad de coste**, y la fiabilidad (baja varianza entre corridas) suele ser más decisiva para producción que un pico de rendimiento en el mejor caso.

## El LLM como juez

Para tareas sin criterio automático de éxito (¿es buena esta redacción?, ¿es correcta esta respuesta abierta?), evaluar a mano no escala. La alternativa extendida es el **LLM-juez**: usar un modelo potente para puntuar o comparar las salidas de otro contra una rúbrica. Es barato, rápido y sorprendentemente correlacionado con el juicio humano —pero arrastra **sesgos sistemáticos** que hay que conocer para no engañarse:

- **Sesgo de posición**: tiende a preferir la primera (o última) opción presentada; se corrige alternando el orden.
- **Sesgo de verbosidad**: premia respuestas largas y elaboradas aunque no sean mejores.
- **Sesgo de autoafinidad**: favorece salidas de su propia familia de modelos o de su propio estilo.
- **Sesgo de complacencia**: puede dejarse llevar por respuestas seguras y bien presentadas aunque sean incorrectas.

Buenas prácticas: rúbricas claras y específicas, aleatorizar posiciones, usar varios jueces o varias corridas, y **calibrar el juez contra juicio humano** en una muestra antes de confiar en él a gran escala. El LLM-juez es una herramienta valiosa siempre que se trate como lo que es —un evaluador imperfecto y sesgado—, no como una verdad objetiva.

## Trazas y observabilidad en producción

Los benchmarks miden antes de desplegar; en producción, la evaluación se vuelve **continua** y se apoya en la **observabilidad**. La unidad básica es la **traza**: el registro completo de una ejecución —cada paso de razonamiento, cada llamada a herramienta con sus argumentos, cada observación, coste y latencia—. Las trazas permiten **depurar** (¿en qué paso se torció?), **auditar** (qué hizo exactamente el agente, requisito de seguridad de la lección 2) y **descubrir modos de fallo** que ningún benchmark previó.

Sobre las trazas se construye la evaluación en vivo: métricas agregadas (tasa de éxito, coste, latencia por tipo de tarea), detección de regresiones cuando cambia el modelo o el prompt, **conjuntos de evaluación** propios que reflejan los casos reales de la aplicación, y realimentación de usuarios (pulgares arriba/abajo, correcciones) como señal. Un patrón sano es cerrar el ciclo: los fallos observados en producción se convierten en nuevos casos del conjunto de evaluación, que protege contra reintroducirlos. La lección de fondo: un agente no se evalúa una vez y se olvida; se *monitoriza* mientras vive, porque el mundo, los modelos y los usuarios cambian —el mismo espíritu del MLOps que cerraba la primera lección de Inteligencia Artificial, ahora aplicado a sistemas que actúan—.

## Ideas clave

- Evaluar agentes es más duro que evaluar modelos: muchos pasos, no determinismo, entornos cambiantes y varias soluciones válidas obligan a promediar varias corridas y a analizar trazas, no un solo número.
- Benchmarks clave: SWE-bench (programación, validado con tests reales), GAIA (asistente general con herramientas) y tau-bench (atención al cliente con políticas); todos verificables pero expuestos a contaminación y saturación.
- La tasa de éxito no basta: hay que medir coste, pasos, latencia, fiabilidad e intervención humana; la frontera útil es éxito por unidad de coste, y la baja varianza importa más que un pico.
- El LLM-juez escala la evaluación de tareas abiertas pero tiene sesgos (posición, verbosidad, autoafinidad, complacencia); exige rúbricas claras, aleatorización y calibración contra humanos.
- En producción se evalúa de forma continua con observabilidad: las trazas permiten depurar, auditar y hallar fallos, y los casos reales realimentan un conjunto de evaluación que evita regresiones.

## Para seguir

Cierra la categoría de Agentes de IA. La siguiente, *IA Agéntica*, escala de un agente a **sistemas** de agentes: orquestación, multiagente, protocolos de interoperabilidad y el despliegue seguro en producción.
