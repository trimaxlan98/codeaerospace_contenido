---
title: "Consenso: Paxos y Raft"
level: avanzado
summary: El problema del consenso y la imposibilidad FLP, quórums mayoritarios, Raft paso a paso con elección de líder y replicación de log, y Paxos en una página.
tags: [consenso, raft, paxos, quorum, etcd]
minutes: 13
order: 4
---

## Objetivos

- Formular el problema del consenso y sus tres propiedades: acuerdo, validez y terminación.
- Explicar qué demuestra el resultado de imposibilidad FLP y cómo lo esquivan los sistemas reales.
- Justificar por qué los quórums mayoritarios son el mecanismo central de los protocolos de consenso.
- Describir Raft paso a paso: términos, elección de líder y replicación de log con sus invariantes.
- Resumir Paxos de un solo valor y ubicar dónde se usa el consenso en la infraestructura real (etcd, ZooKeeper).

## El problema y la imposibilidad FLP

El **consenso** es el problema de lograr que un conjunto de procesos, algunos de los cuales pueden fallar, acuerden un único valor. Formalmente exige tres propiedades: **acuerdo** (ningún par de procesos correctos decide valores distintos), **validez** (el valor decidido fue propuesto por alguien —prohíbe la solución trivial de decidir siempre cero) y **terminación** (todo proceso correcto decide eventualmente). Las dos primeras son propiedades de *seguridad* (nunca pasa nada malo); la tercera, de *vivacidad* (eventualmente pasa algo bueno). Su importancia es práctica y no solo teórica: replicar una máquina de estados —una base de datos, un registro de configuración— equivale a resolver consenso repetidamente, una vez por cada posición del log de operaciones.

En 1985, Fischer, Lynch y Paterson demostraron el resultado más célebre del área, conocido como **FLP**: *en un sistema puramente asíncrono, ningún protocolo determinista resuelve consenso con garantía de terminación si un solo proceso puede fallar por caída*. La intuición: como no hay cotas de tiempo, es imposible distinguir un proceso muerto de uno lento, y para cualquier protocolo existe una secuencia de retrasos de mensajes —tejida por un adversario— que lo mantiene indefinidamente en un estado indeciso. FLP no dice que el consenso sea imposible en la práctica; dice que **la terminación no puede garantizarse incondicionalmente**. Los sistemas reales lo esquivan exactamente como sugiere el modelo parcialmente síncrono visto en la primera lección: usan *timeouts* (una forma débil de detección de fallos) y garantizan seguridad siempre, con progreso asegurado solo durante los periodos —en la práctica, casi todo el tiempo— en que la red se comporta bien.

## Quórums: la aritmética de la intersección

Todos los protocolos de consenso prácticos comparten un mecanismo: ninguna decisión es válida sin el respaldo de un **quórum mayoritario**. Con $n = 2f + 1$ nodos se toleran $f$ caídas, porque una mayoría de $f+1$ sigue alcanzable. La propiedad que hace funcionar todo es la **intersección**: dos mayorías cualesquiera de un conjunto de $n$ nodos comparten al menos un miembro. Por tanto, si una decisión fue aceptada por una mayoría, *cualquier* mayoría futura contiene al menos un nodo que la conoce —la información decidida no puede perderse ni contradecirse mientras no falle más de $f$ nodos. De aquí salen los números canónicos de la infraestructura: los clústeres de etcd y ZooKeeper son de 3 nodos (tolera 1 fallo) o 5 (tolera 2); un clúster de 4 no tolera más fallos que uno de 3 (la mayoría de 4 es 3), por lo que los tamaños pares no aportan y se evitan.

## Raft paso a paso

**Raft** (Ongaro y Ousterhout, 2014) fue diseñado explícitamente para ser comprensible, descomponiendo el consenso en tres subproblemas: elección de líder, replicación de log y seguridad. Cada nodo está en uno de tres estados —**líder**, **seguidor** o **candidato**— y el tiempo se divide en **términos** (*terms*), enteros crecientes que actúan como reloj lógico del protocolo: cada término tiene a lo sumo un líder, y todo mensaje lleva el término de su emisor; un nodo que ve un término mayor que el suyo se actualiza y vuelve a seguidor de inmediato.

**Elección de líder.** Los seguidores esperan latidos (*heartbeats*) del líder. Si un seguidor no recibe nada durante su *election timeout* —aleatorizado, típicamente 150–300 ms—, asume que el líder murió: incrementa su término, se vuelve candidato, vota por sí mismo y pide votos al resto (`RequestVote`). Cada nodo otorga **a lo sumo un voto por término** (persistido en disco), por orden de llegada pero con una restricción crucial que se verá abajo. El candidato que reúne mayoría se proclama líder y empieza a enviar latidos. Si dos candidatos dividen el voto y nadie logra mayoría, el timeout aleatorio hace improbable que vuelvan a chocar: el que expire primero en el término siguiente gana normalmente. La aleatorización del timeout es todo el mecanismo anti-empate —simple y suficiente.

**Replicación de log.** Toda escritura del cliente pasa por el líder, que la añade a su log local como entrada `(término, índice, comando)` y la difunde con `AppendEntries`. Cada `AppendEntries` incluye el índice y término de la entrada inmediatamente anterior; el seguidor **rechaza** la llamada si su log no coincide en ese punto, y el líder retrocede hasta encontrar el último punto de acuerdo y reenvía desde ahí, sobrescribiendo divergencias. Esta *comprobación de consistencia* garantiza por inducción el invariante central: si dos logs coinciden en índice y término de una entrada, coinciden en **todas** las anteriores. Cuando una entrada está replicada en la mayoría, el líder la marca **confirmada** (*committed*), la aplica a su máquina de estados, responde al cliente y comunica el avance del índice de commit en los siguientes latidos.

**Seguridad en la elección.** El eslabón que cierra el sistema: un candidato solo recibe el voto de un nodo si su log está **al menos tan actualizado** como el del votante (compara término de la última entrada; a igualdad, longitud). Como toda entrada confirmada vive en una mayoría, y toda elección exige otra mayoría, la intersección garantiza que **ningún candidato sin las entradas confirmadas puede ganar**: el nuevo líder siempre contiene todo lo confirmado, y nada decidido se pierde jamás en un cambio de líder.

```
        timeout sin latidos          gana mayoría de votos
SEGUIDOR ───────────────→ CANDIDATO ───────────────→ LÍDER
    ↑                        │  │                       │
    │   ve término mayor     │  │ ve término mayor      │
    └────────────────────────┴──┴───────────────────────┘
```

## Paxos en una página

**Paxos** (Lamport, 1998) resuelve el consenso sobre *un* valor en dos fases, con **proponentes** y **aceptadores**. Fase 1 (*prepare*): un proponente elige un número de propuesta $b$ único y creciente y pide a los aceptadores que prometan no aceptar nada con número menor; cada aceptador que promete responde además con el valor que ya hubiera aceptado, si alguno. Fase 2 (*accept*): con promesas de una mayoría, el proponente propone —**obligatoriamente el valor ya aceptado con número más alto que le reportaron**, o el suyo propio solo si nadie reportó nada— y el valor queda *elegido* cuando una mayoría lo acepta. La regla en cursiva es el corazón: garantiza que una vez que un valor pudo haber sido elegido, toda propuesta posterior lo transporta, y el acuerdo es irrevocable. Para replicar un log completo se ejecuta una instancia por posición (**Multi-Paxos**), con la optimización de un líder estable que salta la fase 1 en régimen —momento en el cual Multi-Paxos y Raft convergen en estructura, siendo Raft esencialmente un Multi-Paxos con líder fuerte y reglas de log prescritas en detalle.

## El consenso en producción

El consenso es caro —cada escritura cuesta al menos un viaje de ida y vuelta a la mayoría— así que la arquitectura estándar lo **concentra en un núcleo pequeño**: un clúster de 3–5 nodos que guarda solo metadatos críticos, mientras el plano de datos escala por otros medios. **etcd** (Raft) es la memoria de Kubernetes: todo el estado del clúster —pods, servicios, configuración— vive en él, y la elección de líder de los propios controladores se implementa con sus primitivas de comparar-e-intercambiar. **ZooKeeper** (con ZAB, un protocolo hermano de Raft) cumple el mismo papel para Kafka (hasta su reemplazo por KRaft, Raft embebido en los propios brokers), HBase y Hadoop. **Chubby**, el servicio de cerraduras de Google basado en Multi-Paxos, es el ancestro de todos ellos. El patrón se repite: consenso para lo pequeño y crítico (quién es el líder, dónde están los datos, qué configuración rige), y protocolos más baratos —replicación primario-réplica, quórums sin líder— para el volumen.

## Ideas clave

- Consenso = acuerdo + validez + terminación; las dos primeras son seguridad y se garantizan incondicionalmente, la tercera es vivacidad y depende de que la red coopere.
- FLP demuestra que en asincronía pura ningún protocolo determinista garantiza terminación con un solo fallo posible; los sistemas reales lo esquivan con timeouts y sincronía parcial.
- Con $n = 2f+1$ nodos se toleran $f$ fallos; la intersección de mayorías es lo que impide perder o contradecir decisiones (por eso los clústeres son de 3 o 5, nunca pares).
- Raft: términos como reloj lógico, elección con timeouts aleatorizados y voto único persistido, replicación con comprobación de consistencia del log, y la restricción de voto que garantiza que el nuevo líder contiene todo lo confirmado.
- Paxos elige un valor en dos fases (prepare/accept) con la regla de adoptar el valor aceptado más reciente; Multi-Paxos con líder estable converge estructuralmente con Raft.
- En producción el consenso se concentra en núcleos de metadatos (etcd para Kubernetes, ZooKeeper para Kafka/HBase); el plano de datos usa mecanismos más baratos.

## Para seguir

La última lección de la categoría, *Arquitecturas distribuidas modernas*, baja estos fundamentos al día a día: microservicios, colas de eventos, sagas, idempotencia y cuándo la respuesta correcta es no distribuir.
