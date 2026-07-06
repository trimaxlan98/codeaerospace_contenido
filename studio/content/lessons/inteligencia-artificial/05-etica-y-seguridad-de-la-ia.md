---
title: Ética y seguridad de la IA
level: intro
summary: De dónde vienen los sesgos, cómo se protege la privacidad, qué significa alinear un modelo, por qué importa la interpretabilidad y cómo regula la ley (con el AI Act y sus niveles de riesgo) el uso de la IA.
tags: [etica, sesgo, alineacion, privacidad, regulacion, interpretabilidad]
minutes: 11
order: 5
---

## Objetivos

- Identificar el origen de los sesgos en los datos y por qué el modelo los amplifica.
- Entender los riesgos de privacidad propios de los modelos entrenados con datos masivos.
- Explicar qué es la alineación y comparar RLHF con la IA constitucional.
- Comprender por qué la interpretabilidad importa y qué tan lejos está.
- Situar el marco regulatorio, en especial el enfoque por niveles de riesgo del AI Act.

## Sesgos: el espejo de los datos

Un modelo de IA aprende de datos, y los datos son un retrato del mundo tal como es —con sus prejuicios históricos incluidos—. Si un corpus refleja que ciertos puestos los ocuparon mayoritariamente hombres, un modelo de selección de personal aprenderá esa correlación y la reproducirá al recomendar candidatos; si los datos médicos provienen sobre todo de una población, el modelo funcionará peor en las demás. El **sesgo** no es un error de programación que se pueda "arreglar" con un parche: es una propiedad heredada de los datos, y a menudo *amplificada*, porque el modelo optimiza la regularidad estadística y las minorías, por definición, aportan menos ejemplos.

Los sesgos entran por varias puertas: **de muestreo** (grupos infrarrepresentados en los datos), **histórico** (los datos codifican decisiones injustas del pasado), **de etiquetado** (los prejuicios de quienes anotaron), y **de agregación** (un modelo único que no sirve igual a poblaciones distintas). Casos reales —sistemas de reincidencia penal que penalizaban a minorías, reconocimiento facial con tasas de error muy dispares por tono de piel y género— mostraron el daño concreto. Mitigar exige trabajo en todo el ciclo: auditar la composición de los datos, medir el rendimiento *desagregado* por subgrupos (no solo la exactitud global, que puede ocultar disparidades), y elegir explícitamente una definición de equidad —porque, matemáticamente, no se pueden satisfacer todas a la vez—.

## Privacidad

Entrenar con datos masivos raspados de Internet plantea riesgos de privacidad nuevos. El más directo es la **memorización**: un modelo grande puede retener literalmente fragmentos raros de su entrenamiento —una dirección, un número de tarjeta, código propietario— y regurgitarlos si se le induce, filtrando datos que nunca debieron salir. A esto se suman los **ataques de inferencia de pertenencia** (deducir si un dato concreto estuvo en el entrenamiento) y la tensión con normativas como el RGPD, cuyo "derecho al olvido" choca con la dificultad técnica de *desaprender* un dato ya absorbido por miles de millones de parámetros.

Las defensas son activas: **privacidad diferencial** (añadir ruido matemáticamente calibrado durante el entrenamiento para que ningún individuo influya de forma detectable), **aprendizaje federado** (entrenar sin centralizar los datos, que nunca salen del dispositivo), filtrado y anonimización de los corpus, y controles sobre qué se registra en producción. En el uso de asistentes, la regla práctica para el usuario es no pegar información sensible que no querría ver expuesta.

## Alineación: que el modelo quiera lo que queremos

La **alineación** (*alignment*) es el problema de lograr que un sistema de IA persiga los objetivos y valores que sus operadores pretenden, en vez de una aproximación literal y contraproducente. La dificultad de fondo es que es imposible *especificar* completamente lo que queremos: un modelo optimizado a rajatabla por una métrica encontrará atajos que la cumplen violando su espíritu (el *reward hacking*). A escala de sistemas muy capaces, esto pasa de ser una molestia a una preocupación de seguridad.

Hoy la alineación práctica se hace, sobre todo, con las técnicas vistas en la lección de Transformers:

- **RLHF** (refuerzo con retroalimentación humana): humanos comparan respuestas, se entrena un modelo de recompensa con sus preferencias y se afina al asistente para maximizarlo. Es eficaz pero hereda los sesgos de los anotadores y es caro de escalar.
- **IA constitucional**: en lugar de (solo) juicio humano caso a caso, se le da al modelo un conjunto explícito de principios —una "constitución"— y se usa al propio modelo para criticar y revisar sus respuestas contra esos principios. Reduce la dependencia de etiquetado humano masivo y hace los valores auditables, porque están escritos.

Ninguna resuelve el problema de fondo para sistemas futuros más capaces que sus supervisores —la **supervisión escalable** es investigación abierta—, pero ambas mejoran de forma tangible el comportamiento de los modelos actuales.

## Interpretabilidad: abrir la caja negra

Una red con miles de millones de parámetros es opaca: acierta, pero no podemos leer *por qué* decidió lo que decidió. Esa opacidad es un problema práctico (no se puede depurar lo que no se entiende), legal (normativas que exigen explicar decisiones automatizadas) y de seguridad (no se puede confiar plenamente en lo que no se comprende). La **interpretabilidad** busca revertir esa opacidad. La *mecanicista* intenta descifrar qué computan neuronas y circuitos internos —con avances recientes en identificar "características" interpretables dentro de los modelos—; otras aproximaciones son *post-hoc*: explicar una decisión concreta señalando qué entradas la motivaron. Es un campo joven y las explicaciones actuales son parciales, pero es una de las vías más prometedoras hacia una IA en la que se pueda confiar de forma justificada, no solo empírica.

## Regulación: el enfoque por riesgo

Frente al vacío normativo inicial, la regulación se ha organizado en torno a una idea sensata: **regular por nivel de riesgo del uso**, no la tecnología en abstracto. El referente es el **AI Act** de la Unión Europea (en vigor desde 2024, con aplicación escalonada), que clasifica los sistemas en cuatro niveles:

| Nivel | Ejemplos | Trato |
|-------|----------|-------|
| Riesgo inaceptable | Puntuación social, manipulación subliminal | Prohibidos |
| Alto riesgo | Selección de personal, crédito, dispositivos médicos, justicia | Permitidos con requisitos estrictos (transparencia, supervisión humana, gestión de riesgos, calidad de datos) |
| Riesgo limitado | Chatbots, contenido generado | Obligación de transparencia (avisar de que es IA) |
| Riesgo mínimo | Filtros de spam, videojuegos | Sin obligaciones específicas |

Otras jurisdicciones toman enfoques distintos —más sectoriales en EE. UU., con órdenes ejecutivas y guías; propios en Reino Unido, China y otros—, lo que crea un mosaico regulatorio que las organizaciones globales deben navegar. Al margen de la ley, han proliferado marcos voluntarios de gobernanza (gestión de riesgos, tarjetas de modelo que documentan capacidades y límites, evaluaciones de seguridad previas al despliegue).

## Uso responsable

Para quien construye o usa IA, la ética se traduce en hábitos concretos: conocer los límites del modelo y no delegarle decisiones de alto impacto sin supervisión humana; **verificar** las salidas donde la verdad importa (recordando las alucinaciones de la lección anterior); ser transparente sobre cuándo se está usando IA; proteger los datos que se le entregan; y considerar el impacto sobre las personas afectadas por sus decisiones. La tecnología es una herramienta poderosa y falible: el juicio, la responsabilidad y la rendición de cuentas siguen siendo humanos —una idea que la categoría de agentes y la de IA agéntica vuelven a poner a prueba cuando la IA pasa de aconsejar a actuar—.

## Ideas clave

- El sesgo es una propiedad heredada de los datos (y amplificada por el modelo), no un bug; se mitiga auditando datos, midiendo el rendimiento desagregado por subgrupos y eligiendo una definición explícita de equidad.
- Los modelos pueden memorizar y filtrar datos de entrenamiento; se defienden con privacidad diferencial, aprendizaje federado y filtrado, y el usuario no debe entregar información sensible.
- Alinear es lograr que el modelo persiga los valores pretendidos pese a no poder especificarlos del todo; RLHF usa preferencias humanas y la IA constitucional, principios explícitos auto-aplicados.
- La interpretabilidad busca explicar el porqué de las decisiones de una caja negra; es clave para confianza, depuración y cumplimiento, y aún es incipiente.
- La regulación se organiza por nivel de riesgo del uso: el AI Act de la UE prohíbe lo inaceptable, exige requisitos al alto riesgo y transparencia al riesgo limitado; el uso responsable mantiene el juicio humano en el centro.

## Para seguir

Cierra la categoría de Inteligencia Artificial. La siguiente, *Agentes de IA*, da el salto de modelos que responden a sistemas que actúan: perciben, razonan, usan herramientas y persiguen objetivos —con todo lo que eso implica para la seguridad que aquí hemos visto—.
