---
title: Qué es un agente de IA
level: intro
summary: El salto del chatbot que responde al agente que actúa, el bucle percepción-razonamiento-acción sobre un entorno, los grados de autonomía y los ejemplos reales que ya funcionan.
tags: [agentes, autonomia, bucle-agente, tool-use, coding-agents]
minutes: 10
order: 1
---

## Objetivos

- Distinguir un modelo que responde de un agente que actúa.
- Describir el bucle agente-entorno: percepción → razonamiento → acción → observación.
- Entender la autonomía y la agencia como propiedades graduales, no binarias.
- Reconocer los componentes que convierten un LLM en un agente.
- Situar ejemplos actuales de agentes que funcionan hoy.

## Del chatbot al agente

Un chatbot clásico es una función: entra un mensaje, sale una respuesta, fin. No recuerda entre turnos más que lo que cabe en su contexto, no puede hacer nada en el mundo y no persigue ningún objetivo propio más allá de responder. Es reactivo y de un solo paso.

Un **agente de IA** rompe ese molde. En lugar de producir una respuesta y terminar, un agente recibe un **objetivo** ("arregla este bug", "planifica este viaje", "investiga este tema y redacta un informe") y trabaja hacia él en **varios pasos**, decidiendo qué hacer a continuación, ejecutando acciones que afectan a un entorno, observando los resultados y ajustando su plan. El LLM deja de ser el producto final y pasa a ser el *motor de razonamiento* que dirige un bucle. La diferencia no es de grado sino de naturaleza: de *responder* a *actuar*. Es la tercera frontera que anunciaba la primera lección de Inteligencia Artificial —percibir, generar, actuar—.

## El bucle agente-entorno

La estructura de todo agente es un ciclo tomado de la teoría clásica de agentes, adaptado a los LLM:

1. **Percepción.** El agente observa el estado del entorno: el mensaje del usuario, el resultado de la última acción, el contenido de un archivo, la respuesta de una API. Esa observación entra en su contexto.
2. **Razonamiento.** El LLM, dado el objetivo y lo percibido, decide el siguiente paso: ¿qué falta?, ¿qué herramienta usar?, ¿con qué argumentos?, ¿ya terminé?
3. **Acción.** El agente ejecuta lo decidido: llama a una herramienta, escribe un archivo, lanza un comando, consulta una base de datos. La acción cambia el entorno.
4. **Observación.** Recoge el resultado de la acción —éxito, error, datos devueltos— y vuelve al paso 1.

El bucle se repite hasta que el objetivo se cumple, se agota un presupuesto (de pasos, de tiempo, de dinero) o el agente pide ayuda. Este lazo cerrado —actuar y *observar la consecuencia* antes de decidir de nuevo— es lo que distingue a un agente de una simple cadena de instrucciones predefinida: el camino no está fijado de antemano, se construye en respuesta a lo que ocurre. El **entorno** puede ser digital (un sistema de archivos, un navegador, una API, un terminal) o, con robótica, físico.

## Autonomía y agencia son graduales

Es tentador preguntar "¿es esto un agente, sí o no?", pero la pregunta útil es *cuánta* agencia tiene. La autonomía es un continuo:

- En un extremo, el **flujo de trabajo** (*workflow*): los pasos están predefinidos por un programador y el LLM solo rellena huecos concretos. Predecible y fiable, pero rígido.
- En el medio, agentes que **eligen entre herramientas** y deciden cuántos pasos dar, pero dentro de límites acotados y con puntos de control humanos.
- En el otro extremo, agentes de **horizonte largo** que descomponen objetivos complejos, planifican y ejecutan durante muchos pasos con mínima intervención.

Más autonomía da más capacidad pero también más riesgo: más margen para desviarse, para acumular errores, para actuar sobre el mundo de forma indeseada. El diseño de un buen agente no es maximizar la autonomía sino *calibrarla* a la tarea y al coste del error —cuánta supervisión humana insertar y dónde—, tema que la categoría de IA Agéntica desarrolla con los patrones de *human-in-the-loop*.

## Qué convierte un LLM en agente

Un LLM por sí solo razona pero no actúa; se vuelve agente al rodearlo de:

- **Herramientas** (*tools*): funciones que le dan manos —buscar, ejecutar código, leer y escribir archivos, llamar APIs—. Son cómo el agente afecta al mundo y percibe información fresca (lección 2).
- **Memoria**: un modo de retener información más allá de la ventana de contexto, tanto durante la tarea como entre sesiones (lección 3).
- **Un bucle de control**: el andamiaje que ejecuta el ciclo percibir-razonar-actuar, parsea las decisiones del modelo, invoca las herramientas y realimenta los resultados.
- **Un objetivo y criterios de parada**: qué se busca y cómo saber que se logró o que hay que detenerse.

El LLM aporta el razonamiento; el resto es la ingeniería que lo convierte en un sistema que hace cosas.

## Ejemplos que ya funcionan

Los agentes no son especulación: en 2024-2025 varias clases funcionan de forma útil.

- **Agentes de programación** (*coding agents*): el caso de éxito más maduro. Reciben una tarea ("implementa esta función", "corrige este fallo"), exploran la base de código, editan archivos, ejecutan pruebas y depuran hasta que pasan. Funcionan bien porque el código es verificable —los tests dan una señal objetiva de éxito— y operan en un entorno acotado.
- **Asistentes operativos**: agentes que orquestan tareas de oficina —consultar sistemas internos, rellenar formularios, coordinar herramientas de trabajo— con supervisión.
- **Investigación profunda** (*deep research*): agentes que buscan en la web durante muchos pasos, leen múltiples fuentes, contrastan y sintetizan un informe con citas.
- **Automatización de navegador y computadora**: agentes que operan una interfaz gráfica como lo haría una persona, aún incipientes y frágiles pero avanzando rápido.

El patrón común de los que funcionan: entorno acotado, señal de éxito verificable y presencia de supervisión humana en los puntos críticos.

## Ideas clave

- Un chatbot responde en un solo paso; un agente persigue un objetivo en varios, decidiendo y ejecutando acciones que cambian un entorno y observando sus resultados.
- El bucle agente-entorno —percepción, razonamiento, acción, observación— repetido hasta cumplir el objetivo o agotar un presupuesto es la firma de un agente; el camino se construye, no se predefine.
- La autonomía es gradual (del workflow rígido al agente de horizonte largo); más autonomía da más capacidad y más riesgo, y el diseño consiste en calibrarla con supervisión adecuada.
- Un LLM se vuelve agente al rodearlo de herramientas, memoria, un bucle de control y un objetivo con criterios de parada.
- Ya funcionan los agentes de programación (los más maduros, por ser el código verificable), los asistentes operativos, la investigación profunda y la automatización de interfaces.

## Para seguir

El componente que da manos a un agente merece su propia lección: la siguiente cubre el *uso de herramientas* —function calling, esquemas, reintentos y el patrón ReAct de razonar, actuar y observar—.
