---
title: De agentes a sistemas agénticos
level: intro
summary: La diferencia entre un agente único y un sistema agéntico, cuándo conviene un flujo de trabajo determinista frente a agencia plena, y los niveles de autonomía con supervisión humana (human-in-the-loop).
tags: [agentico, orquestacion, workflows, autonomia, human-in-the-loop]
minutes: 10
order: 1
---

## Objetivos

- Distinguir un agente individual de un sistema agéntico.
- Entender qué aporta la orquestación por encima de un solo agente.
- Decidir entre un flujo de trabajo determinista y agencia plena según la tarea.
- Situar los niveles de autonomía y dónde insertar supervisión humana.
- Sentar el marco que desarrollan las lecciones siguientes de la categoría.

## Del agente al sistema

La categoría anterior construyó el **agente**: un LLM en un bucle, con herramientas y memoria, persiguiendo un objetivo. La **IA agéntica** da el siguiente paso: pasar de un agente que hace todo a un **sistema** de componentes agénticos coordinados —varios agentes, flujos, herramientas y controles— diseñado como una arquitectura, no como un único bucle. Igual que en software se pasa de un script a un sistema con módulos, aquí se pasa del agente monolítico a un sistema donde el trabajo se reparte, se orquesta y se gobierna.

¿Por qué no un solo agente para todo? Porque un agente único tiene límites que la categoría de agentes ya señaló: su contexto se satura en tareas grandes, su fiabilidad por paso se compone y hunde en horizontes largos, y mezclar muchas responsabilidades en un solo bucle lo hace confuso y difícil de depurar. Repartir el trabajo —en fases, en subagentes especializados, en pasos verificables— recupera control, claridad y fiabilidad. Ese reparto y su coordinación son el objeto de esta categoría.

## Orquestación

La **orquestación** es la capa que coordina los componentes hacia el objetivo global: decide qué se ejecuta, en qué orden, quién hace qué, cómo fluye la información entre partes y qué ocurre ante un fallo. Puede ser tan simple como una secuencia fija de pasos o tan compleja como un orquestador que delega dinámicamente en subagentes (la lección de sistemas multiagente lo detalla). La idea clave: separar el **qué** (el objetivo y la lógica de coordinación) del **quién/cómo** (los agentes y herramientas que ejecutan cada parte). Una buena orquestación hace el sistema comprensible, testeable y seguro, frente a un agente-caja-negra que "de algún modo" resuelve todo.

## Flujo de trabajo o agencia plena

La decisión de diseño más importante —y la más malentendida— es *cuánta* agencia dar. Hay dos polos:

- **Flujo de trabajo** (*workflow*): los pasos y su orden están **predefinidos** por un desarrollador; el LLM ejecuta tareas concretas dentro de una estructura fija (clasificar, extraer, redactar en cada casilla). Es **predecible, barato, fácil de testear y depurar**, y suficiente para la mayoría de problemas reales, que son repetitivos y de estructura conocida.
- **Agencia plena** (*agent*): el LLM **decide dinámicamente** los pasos, las herramientas y el camino. Es **flexible y potente** para problemas abiertos donde el camino no se puede prever, pero más caro, menos predecible y más difícil de controlar.

La regla práctica, hoy consenso en la industria: **usa el mínimo de agencia que resuelva el problema**. Empieza por un flujo determinista y reserva la agencia plena para las partes que de verdad la necesiten —lo abierto, lo impredecible—. Muchos "sistemas de IA agéntica" exitosos son en realidad flujos deterministas con pequeños bolsillos de agencia en los puntos que lo requieren. Sobredimensionar la autonomía añade coste, fragilidad y riesgo sin ganancia.

| | Flujo de trabajo | Agencia plena |
|---|---|---|
| Camino | Predefinido | Decidido en ejecución |
| Predecibilidad | Alta | Baja |
| Coste | Bajo | Alto |
| Depuración | Fácil | Difícil |
| Cuándo usarlo | Tareas estructuradas y repetitivas | Problemas abiertos e impredecibles |

## Niveles de autonomía y human-in-the-loop

La autonomía no es un interruptor sino una escala, y a cada nivel corresponde una forma de supervisión humana:

1. **Humano en el bucle** (*human-in-the-loop*): el agente propone y el humano **aprueba cada acción** relevante antes de ejecutarla. Máximo control, máxima fricción; adecuado para acciones irreversibles o de alto impacto.
2. **Humano sobre el bucle** (*human-on-the-loop*): el agente actúa de forma autónoma pero el humano **supervisa y puede intervenir o detenerlo**. Equilibrio para tareas de riesgo medio.
3. **Humano fuera del bucle**: el agente opera solo dentro de límites fijados, con revisión posterior. Máxima eficiencia, reservado a tareas acotadas, reversibles y de bajo riesgo.

El diseño consiste en **ubicar la supervisión donde el error es caro** y dejar autonomía donde es barato y reversible. No es "cuánto confío en el agente" en abstracto, sino "qué pasa si esta acción concreta sale mal": un agente puede tener plena autonomía para leer y buscar, y requerir aprobación humana para borrar, pagar o publicar. Este principio —autonomía graduada por el coste del error— recorre toda la categoría, y su implementación práctica (guardarraíles, permisos, sandboxing) es el tema de la lección de producción.

## Ideas clave

- La IA agéntica pasa del agente único a un sistema de componentes agénticos coordinados, para superar los límites de contexto, fiabilidad y claridad de un solo bucle.
- La orquestación coordina qué se ejecuta, en qué orden y cómo fluye la información, separando el objetivo/coordinación de los agentes que ejecutan; hace el sistema comprensible y seguro.
- La decisión central es cuánta agencia dar: el flujo determinista (predecible, barato, testeable) frente a la agencia plena (flexible pero cara y difícil de controlar); usa el mínimo de agencia que resuelva el problema.
- La autonomía es una escala con supervisión asociada: humano en el bucle (aprueba cada acción), sobre el bucle (supervisa y puede intervenir) y fuera del bucle (revisión posterior).
- El principio rector es graduar la autonomía por el coste del error: supervisión donde el fallo es caro o irreversible, autonomía donde es barato y reversible.

## Para seguir

Cuando el sistema reparte el trabajo entre varios agentes, aparecen nuevas topologías y nuevos fallos. La próxima lección aborda los *sistemas multiagente*: orquestador-trabajadores, jerarquías, debate, delegación y sus riesgos.
