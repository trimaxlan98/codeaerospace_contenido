---
title: Uso de herramientas (tool use)
level: medio
summary: Cómo un modelo llama funciones externas mediante esquemas JSON, cómo elige la herramienta correcta, cómo se manejan errores y reintentos, por qué hace falta sandboxing y el patrón ReAct de razonar-actuar-observar con una traza de ejemplo.
tags: [tool-use, function-calling, react, json-schema, sandboxing, permisos]
minutes: 12
order: 2
---

## Objetivos

- Entender qué es *function calling* y cómo el modelo pide ejecutar una herramienta.
- Leer un esquema JSON de herramienta y saber qué comunica al modelo.
- Comprender cómo el agente selecciona la herramienta adecuada y maneja fallos.
- Justificar por qué toda ejecución de herramientas necesita sandboxing y permisos.
- Seguir el patrón ReAct en una traza concreta de razonar-actuar-observar.

## Dar manos al modelo

Un LLM solo produce texto. El **uso de herramientas** (*tool use*) es el mecanismo que convierte ese texto en acciones sobre el mundo. La idea: al modelo se le presenta un catálogo de funciones que puede invocar —buscar en la web, ejecutar código, leer un archivo, consultar una base de datos, enviar un correo— y, cuando lo necesita, en vez de responder al usuario emite una **petición de llamada** a una de ellas con sus argumentos. Un sistema externo (el bucle del agente) ejecuta realmente la función y le devuelve el resultado, que el modelo incorpora para seguir razonando.

Es crucial entender el reparto: el modelo *decide* qué herramienta usar y con qué argumentos, pero **no ejecuta nada** él mismo. Solo genera una petición estructurada; el andamiaje del agente es quien de verdad corre el código, con todas las implicaciones de seguridad que eso conlleva. Esta separación es la que permite superar dos límites del LLM: acceder a **información fresca** (que no estaba en su entrenamiento) y **actuar** con efectos reales.

## Esquemas: el contrato con el modelo

Para que el modelo sepa qué herramientas existen y cómo llamarlas, cada una se describe con un **esquema JSON** que declara su nombre, qué hace y qué parámetros acepta. Por ejemplo:

```json
{
  "name": "get_weather",
  "description": "Devuelve el clima actual de una ciudad.",
  "parameters": {
    "type": "object",
    "properties": {
      "city":  { "type": "string", "description": "Nombre de la ciudad" },
      "units": { "type": "string", "enum": ["celsius", "fahrenheit"] }
    },
    "required": ["city"]
  }
}
```

La **descripción** es más importante de lo que parece: es lo que el modelo lee para decidir *cuándo* usar la herramienta, así que una buena descripción (clara sobre qué hace y cuándo aplica) mejora directamente la fiabilidad. El esquema de parámetros restringe la forma de la llamada —tipos, valores permitidos (`enum`), campos obligatorios— y los modelos modernos generan salidas que respetan esa estructura (*structured outputs*), reduciendo errores de formato. El modelo responde con algo como `get_weather(city="Bogotá", units="celsius")`, el agente lo ejecuta y devuelve el resultado.

## Elegir bien y fallar bien

Con un catálogo de herramientas, el agente enfrenta dos retos continuos:

**Selección.** Elegir la herramienta correcta entre muchas —o decidir que ninguna hace falta y responder directamente—. Cuantas más herramientas, más difícil: descripciones solapadas confunden, y catálogos enormes saturan el contexto y la atención del modelo. Buenas prácticas: pocas herramientas bien diferenciadas, nombres y descripciones inequívocos, y agrupar o cargar herramientas según la fase de la tarea en vez de exponerlas todas siempre.

**Errores y reintentos.** Las herramientas fallan: una API caduca, un argumento es inválido, un archivo no existe, la red se cae. Un agente robusto trata el error como una **observación más**, no como un final: recibe el mensaje de error, razona sobre su causa y decide —reintentar con otros argumentos, probar otra herramienta, o rendirse y avisar—. Devolver mensajes de error *informativos* al modelo (qué falló y por qué) es lo que le permite corregir; un error opaco lo deja a ciegas. Conviene además limitar reintentos para no entrar en bucles y aplicar esperas crecientes ante fallos transitorios.

## Sandboxing y permisos: no es opcional

Aquí reaparece la advertencia de seguridad. Como el agente ejecuta acciones reales que un LLM falible eligió —y que un usuario o un documento malicioso podrían haber manipulado (inyección de prompts)—, **toda ejecución de herramientas debe estar contenida**:

- **Sandboxing**: correr las acciones en un entorno aislado (contenedor, máquina virtual, permisos restringidos) donde un comando erróneo o malicioso no pueda dañar el sistema anfitrión ni acceder a lo que no debe.
- **Permisos y aprobación**: distinguir acciones seguras y reversibles (leer un archivo, buscar) de las peligrosas o irreversibles (borrar datos, enviar dinero, publicar), y exigir confirmación humana para estas últimas —el *human-in-the-loop* aplicado a la acción concreta—.
- **Principio de mínimo privilegio**: dar al agente solo las herramientas y accesos que su tarea requiere, nada más.
- **Auditoría**: registrar cada acción para poder revisar qué hizo el agente y por qué.

La regla mental: nunca conceder a un agente un poder cuyo peor uso posible no estés dispuesto a asumir. La categoría de IA Agéntica dedica una lección entera a estos guardarraíles en producción.

## El patrón ReAct

El patrón que estructura el uso de herramientas se llama **ReAct** (*Reasoning + Acting*): intercalar pasos de **razonamiento** (pensar en voz alta qué hacer) con pasos de **acción** (llamar una herramienta) y **observación** (leer su resultado), en bucle, hasta resolver. Explicitar el razonamiento antes de cada acción mejora las decisiones y, de paso, deja una traza legible para depurar. Un ejemplo para "¿Qué temperatura hará mañana en la capital de Francia?":

```
Pensamiento: Necesito la capital de Francia y luego su clima. La capital la sé: París.
Acción: get_weather(city="París", units="celsius")
Observación: { "temp": 18, "condition": "parcialmente nublado" }
Pensamiento: Tengo el dato. Puedo responder.
Respuesta: Mañana en París se esperan unos 18 °C, parcialmente nublado.
```

El mismo esquema escala a tareas largas: cada vuelta añade una observación al contexto, el agente reevalúa y sigue. Variantes lo enriquecen —planificar primero y luego ejecutar, o reflexionar sobre fallos para corregir—, temas de la lección de planificación. Pero ReAct es el ladrillo básico sobre el que se construyen casi todos los agentes actuales.

## Ideas clave

- El uso de herramientas convierte el texto del LLM en acciones: el modelo *pide* llamar una función con argumentos, pero es el agente quien la ejecuta —una separación clave para la seguridad.
- Cada herramienta se declara con un esquema JSON (nombre, descripción, parámetros con tipos y obligatoriedad); la descripción guía *cuándo* usarla y es determinante para la fiabilidad.
- El agente debe elegir bien entre herramientas (pocas y diferenciadas) y fallar bien: tratar los errores como observaciones informativas sobre las que razonar y reintentar con límites.
- Ejecutar acciones reales exige sandboxing, permisos con aprobación humana para lo irreversible, mínimo privilegio y auditoría: nunca dar un poder cuyo peor uso no aceptes.
- ReAct —razonar, actuar, observar en bucle— es el patrón base; explicitar el razonamiento mejora decisiones y deja traza depurable.

## Para seguir

Actuar genera información que hay que recordar. La próxima lección aborda la *memoria y gestión del contexto*: la ventana como recurso escaso, RAG y la memoria persistente que sostiene tareas largas.
