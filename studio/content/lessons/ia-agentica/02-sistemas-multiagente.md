---
title: Sistemas multiagente
level: medio
summary: Las topologías para coordinar varios agentes (orquestador-trabajadores, jerárquico, debate), la delegación en subagentes, cómo se comunican, los fallos típicos (bucles, deriva de objetivo) y el compromiso entre coste y paralelismo.
tags: [multiagente, orquestador, subagentes, delegacion, paralelismo]
minutes: 12
order: 2
---

## Objetivos

- Entender por qué y cuándo conviene repartir el trabajo entre varios agentes.
- Comparar las topologías principales: orquestador-trabajadores, jerárquica y de debate.
- Explicar la delegación en subagentes y su ventaja sobre el contexto único.
- Reconocer los fallos característicos de los sistemas multiagente.
- Sopesar el compromiso entre coste, paralelismo y fiabilidad.

## Por qué varios agentes

Un solo agente que lo hace todo acumula problemas: su contexto se llena de información de subtareas heterogéneas, mezcla responsabilidades que confunden su razonamiento y no puede trabajar en paralelo. Un **sistema multiagente** reparte el trabajo entre varios agentes, cada uno con un rol, herramientas y contexto propios. Las ventajas: **especialización** (un agente afinado para investigar, otro para escribir código, otro para revisar), **aislamiento de contexto** (cada uno ve solo lo suyo, sin saturarse) y **paralelismo** (varios avanzan a la vez). El precio —coste, coordinación y nuevos modos de fallo— es lo que hay que gestionar, y no siempre compensa: un multiagente no es automáticamente mejor que un agente bien diseñado.

## Topologías de coordinación

Cómo se conectan los agentes define el sistema. Las tres formas base:

- **Orquestador-trabajadores** (*orchestrator-workers*): un agente **coordinador** descompone la tarea, reparte subtareas a varios **trabajadores** (a menudo en paralelo) y **sintetiza** sus resultados. Es la topología más común y versátil —un jefe que delega y agrega—. Encaja cuando la tarea se parte en piezas relativamente independientes (investigar varios subtemas, procesar varios archivos).
- **Jerárquica**: los trabajadores pueden a su vez ser orquestadores de sus propios subagentes, formando un árbol de delegación de varios niveles. Escala a problemas muy grandes, a costa de más coordinación y latencia acumulada.
- **Debate / roles adversarios**: varios agentes abordan el mismo problema desde posturas distintas —un generador y un crítico, o varios que argumentan y contrastan— para mejorar la calidad por confrontación. Útil cuando la corrección importa más que la velocidad (revisión, verificación, decisiones delicadas); más caro por definición.

Otros patrones combinan estos: una **cadena** (*pipeline*) donde cada agente pasa su salida al siguiente (investigar → redactar → revisar), o un **enrutador** que dirige cada petición al agente adecuado. La elección depende de si las subtareas son independientes (paralelo), secuenciales (cadena) o requieren contraste (debate).

## Delegación en subagentes

El mecanismo que hace práctico el multiagente es la **delegación**: un agente principal lanza **subagentes** para tareas acotadas y recibe de vuelta solo su **resultado**, no todo su proceso. La ventaja es de contexto: el subagente explora, prueba, falla y razona en *su propia* ventana —que puede llenar libremente— y devuelve al principal un resumen limpio. El principal se ahorra el ruido intermedio y conserva su contexto para la coordinación global. Es la aplicación multiagente del principio de gestión de contexto de la categoría anterior: aislar el trabajo sucio en un contexto desechable y quedarse solo con la conclusión.

Esto encaja de forma natural con tareas de **búsqueda amplia** o exploración: lanzar varios subagentes que barren fuentes o rutas distintas en paralelo y consolidar hallazgos. El coste es que cada subagente es una invocación completa del modelo —más tokens, más dinero— y que el principal depende de la calidad del resumen que recibe.

## Comunicación entre agentes

Los agentes coordinan intercambiando **mensajes** —en la práctica, texto o datos estructurados—. El diseño de esa comunicación es delicado. Pasar **demasiado** contexto entre agentes anula la ventaja del aislamiento (se vuelve a saturar todo); pasar **demasiado poco** deja a los agentes sin la información que necesitan y produce trabajo descoordinado o duplicado. Las buenas prácticas: interfaces claras (qué recibe y qué devuelve cada agente, casi como una función), mensajes estructurados en vez de conversación libre, y objetivos explícitos y acotados por subagente para que no divaguen. Cuando la comunicación cruza organizaciones o sistemas distintos aparece la necesidad de **protocolos** estandarizados —el tema de la lección siguiente—.

## Fallos típicos

Los sistemas multiagente introducen modos de fallo propios que conviene anticipar:

- **Bucles**: dos agentes que se pasan el trabajo mutuamente sin converger, o uno que reintenta indefinidamente. Se contienen con límites de pasos, presupuestos y detección de repetición.
- **Deriva de objetivo** (*goal drift*): a través de varias delegaciones, el objetivo original se distorsiona —cada agente reinterpreta un poco— hasta que el resultado no responde a lo pedido. Se mitiga reanclando el objetivo explícito en cada nivel.
- **Errores que se componen**: un fallo de un subagente contamina a los que dependen de él; sin verificación entre etapas, se propaga.
- **Coordinación costosa**: si los agentes pasan más tiempo comunicándose que trabajando, el sistema es puro *overhead*.
- **Difícil depuración**: con múltiples agentes concurrentes, localizar dónde y por qué falló algo es más duro —de ahí la importancia de las trazas y la observabilidad vistas en evaluación—.

## Coste contra paralelismo

La tentación de "más agentes = mejor" choca con la economía. Cada agente y subagente consume tokens; un sistema multiagente puede costar varias veces más que un solo agente resolviendo lo mismo. El paralelismo compra **velocidad** (varias ramas a la vez) y a veces **calidad** (especialización, debate), pero **no reduce el coste total** —lo aumenta—. La decisión racional: usar multiagente cuando la tarea de verdad se beneficia de paralelismo o especialización (exploración amplia, subtareas independientes, revisión crítica) y quedarse con un agente único cuando la tarea es esencialmente secuencial o pequeña, donde la coordinación solo añade coste y fragilidad. Como en la lección anterior: la respuesta por defecto es la arquitectura *más simple* que resuelva el problema, y se sube en complejidad solo cuando se justifica.

## Ideas clave

- Repartir el trabajo entre varios agentes aporta especialización, aislamiento de contexto y paralelismo, a cambio de coste, coordinación y nuevos fallos; no es automáticamente mejor que un buen agente único.
- Topologías base: orquestador-trabajadores (un coordinador delega y sintetiza, la más común), jerárquica (delegación en árbol) y debate (roles adversarios para más calidad); además cadenas y enrutadores.
- La delegación en subagentes aísla el trabajo sucio en un contexto desechable y devuelve solo el resultado, preservando el contexto del agente principal —gestión de contexto aplicada al multiagente.
- La comunicación entre agentes debe equilibrar demasiado y demasiado poco contexto, con interfaces claras y objetivos acotados; los fallos típicos son bucles, deriva de objetivo, errores compuestos y coordinación costosa.
- El paralelismo compra velocidad y a veces calidad, pero aumenta el coste total; usa multiagente solo cuando la tarea lo justifica y, por defecto, la arquitectura más simple que funcione.

## Para seguir

Para que agentes y herramientas de distintos orígenes trabajen juntos hacen falta estándares. La próxima lección trata los *protocolos e interoperabilidad*, con MCP como caso central.
