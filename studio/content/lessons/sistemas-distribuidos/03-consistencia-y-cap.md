---
title: Consistencia y el teorema CAP
level: medio
summary: Linealizabilidad, serializabilidad y consistencia eventual; el enunciado correcto del teorema CAP, sus malentendidos frecuentes y la extensión PACELC.
tags: [cap, consistencia, linealizabilidad, pacelc, replicacion]
minutes: 11
order: 3
---

## Objetivos

- Definir con precisión linealizabilidad, serializabilidad y consistencia eventual, y no confundirlas entre sí.
- Enunciar correctamente el teorema CAP y delimitar qué demuestra y qué no.
- Identificar los malentendidos más comunes alrededor de CAP.
- Aplicar el marco PACELC para razonar sobre el compromiso latencia-consistencia en operación normal.
- Clasificar bases de datos reales según las garantías que ofrecen por defecto y por configuración.

## Los modelos de consistencia: qué promete el sistema

Cuando un dato se replica en varios nodos, el sistema debe decidir qué versión ve cada lector, y esa decisión define su **modelo de consistencia**: el contrato entre el almacén y sus clientes sobre qué resultados son posibles.

**Linealizabilidad** (consistencia fuerte para operaciones individuales): cada operación parece ejecutarse de forma atómica en algún instante entre su inicio y su fin, y ese orden aparente respeta el tiempo real. Consecuencia práctica: si una escritura terminó (el cliente recibió el OK) y después —en tiempo real— alguien lee, esa lectura ve el valor escrito o uno más nuevo, sin excepciones, lea de la réplica que lea. Es la garantía que hace que un registro replicado se comporte "como si hubiera una sola copia", y la que se necesita para primitivas de coordinación: cerraduras distribuidas, elección de líder, unicidad de nombres de usuario.

**Serializabilidad** pertenece a otro eje: es una garantía de **aislamiento entre transacciones** (grupos de operaciones), no de recencia. Promete que el resultado de ejecutar transacciones concurrentes equivale a *alguna* ejecución en serie de ellas —pero ese orden serial no tiene por qué respetar el tiempo real. Un sistema puede ser serializable y aún así devolver datos viejos. La combinación de ambas —orden serial que además respeta el tiempo real— se llama **serializabilidad estricta** (o consistencia externa, la que ofrece Spanner, como se vio en la lección anterior). Confundir linealizabilidad con serializabilidad es el error terminológico más frecuente del área: la primera habla de un objeto y del tiempo real; la segunda, de transacciones multi-objeto y de equivalencia con algún orden serial.

**Consistencia eventual** es la promesa débil: si dejan de llegar escrituras, todas las réplicas convergen *eventualmente* al mismo valor. No dice nada de cuánto tarda ni de qué se ve mientras tanto: un lector puede ver valores viejos, ver un valor nuevo y luego uno viejo (retroceso), o ver órdenes distintos en réplicas distintas. Entre ambos extremos hay modelos intermedios con utilidad práctica: **read-your-writes** (un cliente siempre ve sus propias escrituras), **lecturas monotónicas** (un cliente nunca retrocede en el tiempo), y **consistencia causal** (las escrituras relacionadas por happened-before se ven en orden causal; las concurrentes, en cualquier orden), el modelo más fuerte alcanzable sin sacrificar disponibilidad bajo partición.

## El teorema CAP, bien enunciado

Conjeturado por Eric Brewer en 2000 y demostrado por Gilbert y Lynch en 2002, el teorema CAP dice: un sistema de datos replicado en red no puede garantizar simultáneamente las tres propiedades siguientes:

- **C** — Consistencia, en el sentido específico de **linealizabilidad** (no "consistencia" en el sentido difuso ni en el sentido ACID).
- **A** — **Disponibilidad total**: toda petición que llega a un nodo *no caído* recibe respuesta (no un error, no un timeout).
- **P** — **Tolerancia a particiones**: el sistema sigue operando aunque la red pierda mensajes arbitrariamente entre grupos de nodos.

El argumento de imposibilidad es casi trivial: con la red partida en dos mitades, si un cliente escribe en una mitad y otro lee en la otra, el sistema debe elegir —responder la lectura con datos posiblemente viejos (sacrifica C) o rechazarla/esperar (sacrifica A). No hay tercera opción, porque la información físicamente no cruzó la partición.

Los malentendidos son más famosos que el teorema. Primero: **"elige 2 de 3" es engañoso**, porque P no es opcional —las particiones ocurren en toda red real, y un sistema "CA" que deja de funcionar ante la primera partición simplemente no es tolerante a fallos. La elección real es una sola: **cuando hay partición, ¿C o A?** Segundo: la C de CAP es mucho más fuerte que lo que muchas aplicaciones necesitan, y la A es mucho más fuerte que lo que muchos sistemas "altamente disponibles" ofrecen (un sistema con quórum mayoritario no es A en el sentido CAP: la minoría partida no responde —y sin embargo es el diseño más común y razonable). Tercero: CAP habla solo del comportamiento *durante* una partición; no dice nada del 99.9% del tiempo restante, que es donde vive el compromiso realmente cotidiano.

## PACELC: el compromiso que opera todos los días

Daniel Abadi propuso en 2012 la extensión **PACELC** para capturar lo que CAP omite: *"if **P**artition, then **A** or **C**; **E**lse, **L**atency or **C**onsistency"*. Aun sin ninguna partición, un sistema replicado enfrenta una elección permanente: para garantizar linealizabilidad, cada escritura debe coordinarse síncronamente con otras réplicas (esperar un quórum, cruzar zonas de disponibilidad o regiones), lo que **cuesta latencia**; para responder rápido, hay que replicar asíncronamente y aceptar ventanas de inconsistencia. La replicación entre regiones lo hace tangible: esperar la confirmación de una réplica a 80 ms de RTT añade 80 ms a cada escritura, siempre, sin que ningún cable se haya cortado.

Así, los sistemas se clasifican en cuatro familias: **PA/EL** (disponibilidad ante partición, latencia en operación normal: Dynamo, Cassandra, Riak en sus configuraciones por defecto), **PC/EC** (consistencia siempre, pagando latencia y rechazando peticiones bajo partición: Spanner, etcd, ZooKeeper, la mayoría de los sistemas de consenso), **PC/EL** y **PA/EC** (híbridos menos comunes; MongoDB con sus valores por defecto se comporta aproximadamente PA/EC).

## Los sistemas reales en el mapa

| Sistema | Bajo partición | Sin partición | Garantía típica |
|---------|---------------|---------------|-----------------|
| etcd / ZooKeeper | C (la minoría no responde) | Consistencia | Linealizabilidad vía Raft/ZAB |
| Spanner | C | Consistencia | Serializabilidad estricta (TrueTime) |
| Cassandra | A (ajustable) | Latencia | Eventual; por consulta `QUORUM` la refuerza |
| DynamoDB | A | Latencia | Eventual por defecto; lectura fuerte opcional |
| PostgreSQL + réplicas asíncronas | — (primario único) | Latencia | Fuerte en el primario; réplicas retrasadas |
| MongoDB | ~A | Consistencia (primario) | Ajustable con write/read concern |

Dos observaciones prácticas sobre la tabla. Primera: en muchos sistemas la elección es **por operación**, no por producto —Cassandra con `QUORUM` en lecturas y escrituras ($R + W > N$, por ejemplo $R=W=2$ con $N=3$) da consistencia fuerte a costa de latencia y disponibilidad; DynamoDB cobra el doble por las lecturas fuertemente consistentes, un recordatorio comercial de que la consistencia cuesta. Segunda: la garantía que importa es la del **camino completo**: una base linealizable detrás de una caché que sirve datos viejos produce un sistema eventual, por más que el componente central sea perfecto. El modelo de consistencia se hereda del eslabón más débil de la cadena de lectura.

## Ideas clave

- Linealizabilidad ordena operaciones sobre un objeto respetando el tiempo real; serializabilidad aísla transacciones multi-objeto sin prometer recencia; son ejes distintos y su combinación es la serializabilidad estricta.
- La consistencia eventual solo promete convergencia final; modelos intermedios como read-your-writes y consistencia causal recuperan garantías útiles sin coordinación global.
- CAP, bien leído, plantea una sola pregunta: durante una partición, ¿respondes con datos posiblemente viejos (A) o rechazas/esperas (C)? La P no es negociable en redes reales.
- PACELC añade el compromiso cotidiano: sin partición alguna, la consistencia fuerte se paga en latencia de coordinación entre réplicas.
- En los sistemas reales la elección suele ser por operación (quórums, read/write concerns), y la garantía efectiva es la del eslabón más débil del camino de datos.

## Para seguir

La siguiente lección, *Consenso: Paxos y Raft*, muestra la maquinaria que hace posible el lado "C" del compromiso: cómo un conjunto de nodos falibles acuerda un único orden de operaciones.
