---
title: Arquitecturas distribuidas modernas
level: medio
summary: Microservicios frente a monolito, arquitecturas de eventos y colas, sagas e idempotencia, service mesh y observabilidad, y cuándo no conviene distribuir.
tags: [microservicios, eventos, sagas, observabilidad, service-mesh]
minutes: 12
order: 5
---

## Objetivos

- Contrastar el monolito y los microservicios con criterios técnicos y organizativos, no de moda.
- Explicar las arquitecturas dirigidas por eventos y el papel de las colas y los logs de eventos.
- Describir el patrón saga para transacciones distribuidas y por qué la idempotencia es su requisito.
- Situar el service mesh y los tres pilares de la observabilidad (métricas, logs, trazas) en una arquitectura real.
- Aplicar criterios claros para decidir cuándo NO distribuir.

## Monolito y microservicios: el compromiso real

Un **monolito** es una aplicación desplegada como una sola unidad: un proceso (o varias copias idénticas de él) que contiene toda la lógica de negocio y habla con una base de datos. Los **microservicios** parten esa lógica en servicios pequeños, cada uno con su propio despliegue, su propio almacén de datos y una interfaz de red (REST, gRPC, eventos). La comparación honesta no es "antiguo contra moderno", sino un intercambio de complejidades: el monolito concentra la complejidad *dentro* del proceso (acoplamiento entre módulos, despliegues que arrastran todo, un solo runtime que limita la elección tecnológica), mientras los microservicios la trasladan a la *red*, donde reaparecen todas las falacias de la primera lección: latencia variable, fallos parciales, versionado de contratos entre equipos, y la pérdida de las transacciones ACID locales —lo que dentro del monolito era una llamada a función con transacción de base de datos se convierte en una llamada remota que puede fallar a medias.

La motivación más sólida para microservicios es **organizativa** antes que técnica (la llamada ley de Conway: la arquitectura replica la estructura de comunicación de la organización): equipos autónomos que despliegan sin coordinarse, escalado independiente del componente caliente (el servicio de búsqueda necesita 40 réplicas; el de facturación, 3), y aislamiento de fallos con límites explícitos. Con pocos equipos y un dominio aún cambiante, el monolito —bien modularizado internamente, el llamado *monolito modular*— es casi siempre la elección correcta de partida; la propia industria acuñó "primero monolito" tras una década de sistemas fragmentados prematuramente en servicios cuyas fronteras hubo que redibujar, que es mucho más caro a través de APIs de red que dentro de un mismo código.

## Eventos y colas: desacoplar en el tiempo

La alternativa a que los servicios se llamen síncronamente (A llama a B y espera) es la comunicación **dirigida por eventos**: A publica un hecho consumado ("pedido 4412 creado") en un intermediario, y quien tenga interés lo consume cuando puede. El desacoplamiento es doble: A no conoce a sus consumidores (se pueden añadir sin tocarlo), y no depende de que estén vivos en ese momento —el intermediario absorbe picos y caídas, convirtiendo un fallo de disponibilidad en un simple retraso.

Dos familias de intermediarios dominan. Las **colas de mensajes** (RabbitMQ, Amazon SQS) entregan cada mensaje a un consumidor y lo borran al confirmarse: modelan *trabajo por hacer* (enviar este correo, generar esta factura). Los **logs de eventos** (Kafka, Pulsar) conservan los eventos en un registro ordenado, inmutable y particionado que múltiples grupos de consumidores leen cada uno a su propio ritmo, pudiendo releer desde el pasado: modelan *hechos ocurridos*, y habilitan patrones como reconstruir una vista materializada reprocesando el histórico (*event sourcing*). La diferencia práctica clave: en una cola, el mensaje consumido desaparece; en un log, el evento permanece según su política de retención y el "progreso" de cada consumidor es solo un desplazamiento (*offset*) que él mismo administra.

La garantía de entrega realista en ambos casos es **al-menos-una-vez**: el intermediario reintenta hasta la confirmación, y por tanto los duplicados son inevitables (la confirmación pudo perderse tras un procesamiento exitoso). La entrega *exactamente-una-vez* de extremo a extremo es, en general, inalcanzable entre sistemas independientes —lo alcanzable es el **procesamiento efectivamente-una-vez**, que se construye del lado del consumidor con idempotencia.

## Sagas e idempotencia: transacciones sin transacción

¿Cómo se ejecuta "cobrar el pago, reservar el inventario y programar el envío" cuando cada paso vive en un servicio distinto con su propia base de datos y no existe una transacción que los abarque? El patrón **saga** (Garcia-Molina y Salem, 1987, redescubierto por los microservicios): descomponer la operación en una secuencia de transacciones *locales*, cada una con una **compensación** definida —una acción que deshace semánticamente su efecto (reembolsar el cobro, liberar la reserva). Si el paso $k$ falla, se ejecutan las compensaciones de los pasos $1..k-1$ en orden inverso. La coordinación admite dos estilos: **orquestación**, con un coordinador central que invoca cada paso y decide compensar (flujo explícito y depurable, pero un componente más), y **coreografía**, donde cada servicio reacciona a los eventos del anterior (sin coordinador, pero el flujo global queda implícito y difícil de seguir). El precio conceptual de toda saga: los estados intermedios **son visibles** —no hay aislamiento— y el diseño debe aceptar, por ejemplo, que un pedido aparezca "pagado" unos segundos antes de cancelarse por falta de inventario.

Las sagas y la entrega al-menos-una-vez convergen en el mismo requisito: **idempotencia**. Cada manejador debe poder ejecutarse dos veces con el efecto de una: se logra con claves de idempotencia (el productor asigna un identificador único a la operación; el consumidor registra los ya procesados y descarta repetidos) o con operaciones naturalmente idempotentes (fijar un estado absoluto en vez de aplicar un incremento). Junto a ella, el patrón **outbox transaccional** resuelve el problema hermano de la doble escritura: para publicar un evento *y* actualizar la base de datos atómicamente, el servicio escribe el evento en una tabla `outbox` dentro de su propia transacción local, y un proceso aparte lo publica después al intermediario —sustituyendo una atomicidad imposible entre dos sistemas por una local más una entrega garantizada con reintentos.

## Service mesh y observabilidad

Cuando decenas de servicios se llaman entre sí, las preocupaciones transversales de red —reintentos con retroceso exponencial, timeouts, *circuit breakers* que dejan de insistir a un servicio caído, TLS mutuo, balanceo— no deberían reimplementarse en cada lenguaje y cada equipo. El **service mesh** (Istio, Linkerd) las extrae a la plataforma: un proxy ligero (*sidecar*, típicamente Envoy) acompaña a cada instancia e intercepta todo su tráfico, y un plano de control distribuye la configuración; el código de negocio queda limpio de lógica de red y la política (¿cuántos reintentos? ¿qué servicios pueden hablarse?) se administra centralmente.

Operar esto exige **observabilidad**, tradicionalmente descrita por tres pilares. Las **métricas** (Prometheus) son series temporales agregadas —tasa de peticiones, errores, latencias p50/p99— baratas de retener y base de las alertas. Los **logs** estructurados registran eventos discretos con detalle. Las **trazas distribuidas** (estandarizadas hoy por OpenTelemetry) siguen una petición individual a través de todos los servicios que atraviesa: cada tramo (*span*) registra su duración y el identificador de traza se propaga en las cabeceras, de modo que la pregunta central de la depuración distribuida —¿*dónde* se gastaron los 900 ms de esta petición?— tiene respuesta gráfica directa. La traza es el pilar específicamente distribuido: métricas y logs por servicio no revelan la cadena causal entre servicios.

## Cuándo NO distribuir

La primera regla de los sistemas distribuidos sigue siendo: *no los construyas si no los necesitas*. Señales de que distribuir es prematuro: el equipo cabe en una sala; una sola base de datos aguanta la carga con réplicas de lectura (y el hardware moderno aguanta muchísimo: máquinas con cientos de GB de RAM y NVMe sirven decenas de miles de transacciones por segundo); los límites del dominio aún cambian cada mes; no existe todavía la plataforma de despliegue, observabilidad y guardias que los microservicios presuponen. Cada frontera de red que se introduce compra escalado y autonomía pagando con latencia, fallos parciales, sagas donde había transacciones y trazas donde había un depurador. La pregunta de diseño honesta nunca es "¿cómo partimos esto en servicios?" sino "¿qué problema concreto tenemos que una arquitectura más simple no resuelva?".

## Ideas clave

- Monolito y microservicios intercambian complejidades: interna y de despliegue contra complejidad de red (latencia, fallos parciales, contratos); la motivación sólida para partir es organizativa (equipos autónomos, ley de Conway).
- Los eventos desacoplan en el tiempo: colas para trabajo por hacer, logs tipo Kafka para hechos releíbles; la garantía realista es al-menos-una-vez y los duplicados son la norma.
- Las sagas sustituyen la transacción distribuida por transacciones locales más compensaciones, sin aislamiento entre pasos; orquestación y coreografía son sus dos estilos de coordinación.
- Idempotencia (claves únicas, estados absolutos) y outbox transaccional son los cimientos de la fiabilidad efectivamente-una-vez.
- El service mesh saca del código las preocupaciones de red (reintentos, mTLS, circuit breaking); la observabilidad se apoya en métricas, logs y, distintivamente, trazas distribuidas.
- Distribuir es un costo que se justifica con un problema concreto de escala o autonomía; el monolito modular es el punto de partida racional.

## Para seguir

Con esta lección cierra la categoría de Sistemas Distribuidos. La categoría *Redes 6G* retoma la infraestructura por debajo: la próxima generación de redes móviles que estos sistemas darán por sentada, empezando por *De 5G a 6G: visión y calendario*.
