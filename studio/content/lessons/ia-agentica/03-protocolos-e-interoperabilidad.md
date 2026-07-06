---
title: Protocolos e interoperabilidad (MCP y más)
level: medio
summary: Por qué los agentes necesitan protocolos estándar, qué es el Model Context Protocol (recursos, herramientas, prompts), la comunicación agente-a-agente, el descubrimiento de capacidades y la seguridad de la cadena de herramientas.
tags: [protocolos, mcp, interoperabilidad, a2a, seguridad, descubrimiento]
minutes: 12
order: 3
---

## Objetivos

- Entender qué problema resuelven los protocolos en el ecosistema de agentes.
- Conocer el Model Context Protocol y sus tres primitivas: recursos, herramientas y prompts.
- Distinguir la integración agente-herramienta de la comunicación agente-a-agente.
- Comprender el descubrimiento dinámico de capacidades.
- Reconocer los riesgos de seguridad de conectar herramientas de terceros.

## El problema de la integración N×M

Cada agente necesita conectarse a muchas herramientas y fuentes de datos —archivos, bases de datos, APIs, servicios—. Sin un estándar, cada conexión es un adaptador a medida: con $N$ agentes (o aplicaciones) y $M$ herramientas, se acaban escribiendo del orden de $N\times M$ integraciones específicas, cada una frágil y no reutilizable. Es el mismo problema que en su día resolvieron los estándares de conectores en hardware o los protocolos web: un **protocolo común** reduce ese producto a $N+M$ —cada agente habla el protocolo una vez, cada herramienta lo expone una vez, y todos se entienden—. La interoperabilidad no es un lujo: es lo que permite un ecosistema donde las herramientas se comparten y se reutilizan en lugar de reescribirse.

## Model Context Protocol (MCP)

El **Model Context Protocol** (MCP), presentado por Anthropic a finales de 2024 y adoptado ampliamente después, es un estándar abierto para conectar agentes con herramientas y datos. Su arquitectura es cliente-servidor: la aplicación de IA actúa como **cliente** MCP y cada integración (un servidor de archivos, uno de GitHub, uno de una base de datos) es un **servidor** MCP que expone capacidades de forma estándar. Un servidor escrito una vez sirve a cualquier cliente MCP; un cliente puede conectarse a cualquier servidor. MCP define tres **primitivas**:

- **Recursos** (*resources*): datos que el servidor pone a disposición del modelo como contexto —el contenido de un archivo, filas de una base, una página—. Son de solo lectura desde la óptica del modelo: información para nutrir el contexto.
- **Herramientas** (*tools*): funciones que el modelo puede **invocar** para actuar —crear un issue, ejecutar una consulta, enviar un mensaje—. Son el *tool use* de la categoría de agentes, ahora expuesto por un protocolo estándar con sus esquemas.
- **Prompts** (*prompts*): plantillas de interacción predefinidas que el servidor ofrece —flujos reutilizables que empaquetan una forma probada de usar sus recursos y herramientas—.

La virtud de MCP es desacoplar la aplicación de IA de sus integraciones: añadir una capacidad nueva es conectar un servidor, no modificar el agente. Así florece un mercado de servidores reutilizables.

## Agente-herramienta frente a agente-agente

Conviene separar dos capas de interoperabilidad:

- **Agente ↔ herramienta/datos**: cómo un agente accede a capacidades externas. Es el territorio de MCP: estandarizar la conexión de un agente con el mundo de recursos y herramientas.
- **Agente ↔ agente** (*A2A*): cómo dos agentes **autónomos**, posiblemente de organizaciones distintas y construidos por equipos distintos, se descubren, negocian y colaboran. Es un problema más difícil —no es un cliente usando una herramienta pasiva, sino dos entidades que razonan— y motiva protocolos específicos de comunicación entre agentes (como los esfuerzos A2A). Aquí se estandarizan cosas como: qué sabe hacer cada agente, cómo delegarle una tarea, cómo reportar progreso y resultado, y cómo manejar identidad y confianza entre partes que no se conocen.

Ambas capas son complementarias: MCP da a un agente sus manos; los protocolos A2A le dan colegas. Juntos habilitan la "internet de agentes" que se vislumbra, aún incipiente.

## Descubrimiento de capacidades

Un rasgo clave de estos protocolos es el **descubrimiento dinámico**: un cliente no necesita conocer de antemano y a mano qué ofrece cada servidor o agente; **pregunta** al conectarse y recibe la lista de recursos, herramientas y prompts disponibles, con sus esquemas. Esto permite sistemas que se **adaptan** a las capacidades presentes: si se añade un servidor con una herramienta nueva, el agente la descubre y puede empezar a usarla sin recompilarse. El descubrimiento convierte un catálogo estático de herramientas en uno **vivo**, y es lo que hace escalable el ecosistema —pero también amplía la superficie de ataque, como se ve enseguida—.

## Seguridad de la cadena de herramientas

Conectar un agente a servidores y herramientas de **terceros** introduce riesgos serios que esta categoría no puede pasar por alto. La confianza se traslada: al usar un servidor MCP ajeno, se le está concediendo acceso a datos o acciones. Los peligros concretos:

- **Herramientas maliciosas o comprometidas**: un servidor podría exfiltrar los datos que se le pasan, ejecutar acciones dañinas o mentir sobre lo que hace. Su descripción misma —que el modelo lee para decidir usarla— puede contener **inyección de prompts** que secuestre el comportamiento del agente.
- **Inyección indirecta**: datos aparentemente inocuos devueltos por una herramienta (el contenido de una página, un correo) pueden llevar instrucciones ocultas que el agente obedezca sin querer.
- **Escalada de permisos**: encadenar herramientas puede combinar accesos de formas no previstas (una que lee datos sensibles + otra que los envía fuera = fuga).
- **Cadena de suministro**: como en cualquier dependencia de software, un servidor popular comprometido afecta a todos sus usuarios.

Las defensas retoman y extienden las de la lección de tool use: **mínimo privilegio** (conectar solo lo necesario y con los permisos justos), **sandboxing** de la ejecución, **aprobación humana** para acciones sensibles, **verificación de la procedencia** (usar servidores de fuentes confiables y auditadas), **aislar datos no confiables** de las instrucciones, y **auditar** cada interacción. La regla de oro no cambia: tratar toda herramienta y todo dato externos como potencialmente hostiles, y no conceder al agente un poder cuyo peor uso no se esté dispuesto a asumir. La lección siguiente lleva estos guardarraíles al despliegue en producción.

## Ideas clave

- Sin estándares, conectar $N$ agentes con $M$ herramientas exige $N\times M$ integraciones a medida; un protocolo común lo reduce a $N+M$ y habilita un ecosistema de herramientas reutilizables.
- MCP es un estándar abierto cliente-servidor con tres primitivas: recursos (datos de contexto), herramientas (acciones invocables) y prompts (flujos reutilizables); desacopla la aplicación de sus integraciones.
- Hay dos capas: agente-herramienta (territorio de MCP) y agente-agente/A2A (comunicación entre agentes autónomos, con identidad, delegación y confianza); son complementarias.
- El descubrimiento dinámico permite a un agente preguntar qué capacidades hay y adaptarse a ellas sin reprogramarse, a costa de ampliar la superficie de ataque.
- Conectar herramientas de terceros traslada la confianza: riesgos de herramientas maliciosas, inyección indirecta, escalada de permisos y cadena de suministro; se defienden con mínimo privilegio, sandboxing, aprobación humana, procedencia verificada y auditoría.

## Para seguir

Con arquitectura, coordinación y protocolos vistos, falta desplegar todo esto de forma segura y sostenible. La próxima lección trata la *IA agéntica en producción*: guardarraíles, presupuestos, auditoría y patrones de despliegue.
