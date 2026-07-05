---
title: Fundamentos y las 8 falacias
level: intro
summary: Qué define a un sistema distribuido, las ocho falacias de la computación distribuida y los modelos de fallo y sincronía que gobiernan su diseño.
tags: [distribuidos, falacias, fallos, sincronia, fundamentos]
minutes: 10
order: 1
---

## Objetivos

- Definir qué es un sistema distribuido y qué lo distingue de un programa concurrente en una sola máquina.
- Enumerar y comentar las ocho falacias de la computación distribuida y sus consecuencias prácticas.
- Distinguir los modelos de fallo: caída (*crash*), omisión y bizantino.
- Contrastar los modelos de sincronía (síncrono, asíncrono, parcialmente síncrono) y entender por qué importan.
- Reconocer por qué la incertidumbre —no la escala— es la dificultad esencial de los sistemas distribuidos.

## Qué es un sistema distribuido

Un **sistema distribuido** es un conjunto de procesos que se ejecutan en computadoras independientes, se comunican únicamente mediante el paso de mensajes por una red, y cooperan para presentarse ante el usuario como un sistema único y coherente. La definición clásica de Leslie Lamport lo captura con ironía precisa: *"un sistema distribuido es aquel en el que el fallo de una computadora que ni siquiera sabías que existía puede dejar tu propia computadora inutilizable"*. Lo esencial no es que haya varias máquinas, sino que **no existe estado global observable de forma instantánea**: cada proceso solo conoce su propio estado y lo que otros le han contado mediante mensajes que tardan un tiempo variable —y a veces no llegan.

Esta ausencia de estado global compartido separa radicalmente lo distribuido de lo meramente concurrente. En un programa multihilo sobre una máquina, dos hilos comparten memoria y un reloj de hardware común: la coordinación es un problema de exclusión mutua. En un sistema distribuido, en cambio, tres incertidumbres son irreducibles: **la latencia es variable** (un mensaje puede tardar microsegundos o segundos), **los fallos son parciales** (una parte del sistema puede morir mientras el resto sigue funcionando, algo imposible en un proceso único que simplemente se cae completo), y **no hay forma de distinguir con certeza un proceso lento de uno muerto** —la ausencia de respuesta es ambigua por naturaleza. Todo el edificio teórico y práctico de los sistemas distribuidos (consenso, replicación, transacciones distribuidas) existe para construir garantías útiles sobre este suelo inestable.

## Las ocho falacias de la computación distribuida

Entre 1994 y 1997, ingenieros de Sun Microsystems (Peter Deutsch y James Gosling, entre otros) codificaron las suposiciones erróneas que los programadores novatos en sistemas distribuidos hacen una y otra vez. Se conocen como las **ocho falacias**, y cada una tiene consecuencias concretas cuando se asume sin cuestionarla:

| # | Falacia | Realidad y consecuencia |
|---|---------|------------------------|
| 1 | La red es fiable | Los paquetes se pierden, los switches se reinician, los cables se cortan. Todo mensaje necesita timeout, reintento e idempotencia. |
| 2 | La latencia es cero | Un viaje de ida y vuelta dentro de un datacenter cuesta ~0.5 ms; entre continentes, 100–300 ms. Las llamadas remotas encadenadas en serie suman latencias. |
| 3 | El ancho de banda es infinito | Serializar objetos enormes o hacer *chatty protocols* satura enlaces; el ancho de banda por nodo es finito y compartido. |
| 4 | La red es segura | Todo enlace puede ser interceptado o suplantado: cifrado (TLS) y autenticación mutua son obligatorios, no opcionales. |
| 5 | La topología no cambia | Nodos aparecen, desaparecen y cambian de dirección (autoescalado, contenedores). El descubrimiento de servicios debe ser dinámico. |
| 6 | Hay un solo administrador | Sistemas reales cruzan equipos, empresas y proveedores de nube; los cambios no se coordinan globalmente. |
| 7 | El costo de transporte es cero | Serializar/deserializar consume CPU; el tráfico entre zonas y regiones de nube se factura por gigabyte. |
| 8 | La red es homogénea | Conviven MTU distintas, versiones de protocolo diferentes, enlaces rápidos y lentos; el diseño debe tolerar heterogeneidad. |

La primera y la segunda falacia son las más costosas en la práctica. Asumir red fiable produce sistemas que se cuelgan esperando respuestas que nunca llegarán; asumir latencia cero produce arquitecturas de microservicios donde una petición del usuario dispara decenas de llamadas remotas en serie y la latencia total se vuelve inaceptable. Una regla de diseño derivada directamente de las falacias: **toda llamada remota debe tener timeout explícito, y toda operación que se reintenta debe ser idempotente** (ejecutarla dos veces debe producir el mismo efecto que una), porque ante un timeout es imposible saber si la operación se ejecutó o no.

## Modelos de fallo

Para razonar con rigor sobre tolerancia a fallos hay que especificar *cómo* pueden fallar los componentes. Los tres modelos canónicos, en orden creciente de severidad:

**Fallo de caída (*crash failure*)**: el proceso funciona correctamente hasta un instante en que se detiene por completo y no vuelve a enviar mensajes. Es el modelo más benigno y el más usado en la práctica: los protocolos de consenso como Raft y Paxos (que se estudian más adelante en esta categoría) toleran fallos de caída. Una variante importante es *crash-recovery*, donde el proceso puede reiniciarse y volver, habiendo perdido su estado volátil pero conservando lo que escribió en disco.

**Fallo de omisión**: el proceso sigue vivo pero omite enviar o recibir algunos mensajes —por buffers llenos, congestión o pérdida en la red. Desde fuera es frecuentemente indistinguible de una caída intermitente, y suele modelarse junto con la caída.

**Fallo bizantino**: el proceso se comporta de forma arbitraria —envía mensajes contradictorios a distintos destinatarios, miente sobre su estado, o actúa maliciosamente. El nombre viene del problema de los *generales bizantinos* formulado por Lamport, Shostak y Pease en 1982. Tolerar $f$ fallos bizantinos exige al menos $3f+1$ réplicas (frente a $2f+1$ para caídas), y protocolos mucho más costosos (PBFT y sucesores). En infraestructura interna de una empresa se asume normalmente el modelo de caída; el modelo bizantino se reserva para entornos sin confianza mutua, como las cadenas de bloques públicas.

## Sincronía y asincronía

El segundo eje de modelado es el tiempo. En un **sistema síncrono** existen cotas conocidas para el retardo máximo de un mensaje y para la diferencia de velocidad entre procesos: si un mensaje no llega en el plazo acotado, se puede *concluir* que el emisor falló. En un **sistema asíncrono** no existe ninguna cota: un mensaje puede tardar arbitrariamente, y por tanto **es imposible distinguir un proceso muerto de uno lento** —el corazón de la dificultad teórica del área, y la hipótesis bajo la cual se demuestra el resultado de imposibilidad FLP que se verá en la lección de consenso.

Las redes reales no son ni lo uno ni lo otro: la mayor parte del tiempo se comportan casi síncronamente (latencias estables y pequeñas), pero atraviesan periodos de asincronía (congestión, pausas de recolección de basura de decenas de segundos, particiones de red). El modelo **parcialmente síncrono** (Dwork, Lynch y Stockmeyer, 1988) captura esto: el sistema es asíncrono durante un tiempo finito pero desconocido, tras el cual se vuelve síncrono. Es el modelo bajo el que se diseñan los sistemas de consenso prácticos: garantizan **seguridad siempre** (nunca dan una respuesta incorrecta, ni siquiera durante la asincronía) y **progreso solo cuando la red se estabiliza**. Esta separación —seguridad incondicional, vivacidad condicional— es uno de los patrones de diseño más profundos del área.

## Ideas clave

- Un sistema distribuido no tiene estado global instantáneo: cada proceso solo sabe lo que le han contado mensajes con retardo variable y entrega incierta.
- El fallo parcial y la imposibilidad de distinguir lento de muerto son las dificultades esenciales, no la escala.
- Las ocho falacias (red fiable, latencia cero, ancho de banda infinito, red segura, topología estable, administrador único, transporte gratis, red homogénea) resumen las suposiciones que arruinan diseños distribuidos.
- Todo mensaje necesita timeout y toda operación reintentable debe ser idempotente, porque un timeout no dice si la operación se ejecutó.
- Los modelos de fallo (caída < omisión < bizantino) y de sincronía (síncrono, asíncrono, parcialmente síncrono) definen qué garantías puede dar un protocolo; los sistemas prácticos garantizan seguridad siempre y progreso solo con red estable.

## Para seguir

La siguiente lección, *Tiempo, relojes y orden de eventos*, ataca la primera consecuencia concreta de este panorama: sin reloj global, ¿qué significa que un evento ocurrió "antes" que otro en máquinas distintas?
