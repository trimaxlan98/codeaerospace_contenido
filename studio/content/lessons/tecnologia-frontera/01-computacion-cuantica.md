---
title: Computación cuántica
level: medio
summary: El qubit y la superposición, el entrelazamiento, las puertas y circuitos, los algoritmos que prometen ventaja (Shor y Grover), el problema de la corrección de errores, la era NISQ y el estado real de la industria.
tags: [cuantica, qubit, superposicion, entrelazamiento, shor, nisq]
minutes: 12
order: 1
---

## Objetivos

- Entender qué es un qubit y qué significa la superposición $|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$.
- Comprender el entrelazamiento como recurso sin análogo clásico.
- Ver cómo puertas y circuitos manipulan la información cuántica.
- Distinguir qué prometen los algoritmos de Shor y Grover, y qué no.
- Situar el estado real: corrección de errores, era NISQ y madurez industrial.

## El qubit y la superposición

La computación clásica se construye sobre el **bit**: 0 o 1. La cuántica se construye sobre el **qubit**, que puede estar en una **superposición** de ambos estados a la vez:

$$|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$$

Aquí $\alpha$ y $\beta$ son **amplitudes** (números complejos) y $|0\rangle$, $|1\rangle$ son los dos estados base. La superposición no significa "no sabemos cuál es" ni "es un valor intermedio": el qubit está genuinamente en una combinación de ambos hasta que se **mide**. Al medir, colapsa a 0 o a 1 con probabilidades $|\alpha|^2$ y $|\beta|^2$ (que suman 1). La consecuencia clave: $n$ qubits en superposición representan simultáneamente $2^n$ combinaciones —10 qubits, 1024 estados a la vez; 300 qubits, más estados que átomos en el universo observable—. Ahí reside la promesa: manipular esa multiplicidad de golpe.

Pero hay una trampa fundamental. No se puede *leer* toda esa información: al medir se obtiene una sola combinación, colapsando el resto. La computación cuántica no es "probar todas las respuestas y leerlas todas"; es el arte de **orquestar interferencias** entre amplitudes para que, al medir, la respuesta correcta salga con alta probabilidad y las incorrectas se cancelen. Diseñar algoritmos cuánticos es diseñar esa coreografía de interferencia.

## Entrelazamiento

El segundo recurso, sin equivalente clásico, es el **entrelazamiento** (*entanglement*): dos o más qubits pueden quedar correlacionados de modo que el estado del conjunto no se puede describir como el de cada uno por separado. Medir uno determina instantáneamente el resultado del otro, sin importar la distancia —lo que Einstein llamó "acción fantasmal a distancia"—. El entrelazamiento no permite enviar información más rápido que la luz (el resultado de cada medida es aleatorio), pero es un recurso computacional esencial: buena parte de la ventaja cuántica proviene de crear y explotar correlaciones entrelazadas que un ordenador clásico no puede representar eficientemente. También es la base de la comunicación cuántica (QKD, en la lección de fotónica).

## Puertas y circuitos

Igual que un circuito clásico aplica puertas lógicas (AND, OR, NOT) a bits, un **circuito cuántico** aplica **puertas cuánticas** a qubits. Las puertas cuánticas son **reversibles** y rotan el estado en su espacio: la puerta de Hadamard crea superposición (convierte $|0\rangle$ en mezcla de $|0\rangle$ y $|1\rangle$); la puerta CNOT entrelaza dos qubits; otras rotan las amplitudes en ángulos precisos. Un algoritmo cuántico es una secuencia de puertas —un circuito— que parte de qubits inicializados, teje superposición y entrelazamiento, orquesta la interferencia y termina en una medida. La diferencia con lo clásico: entre la entrada y la medida, la información vive en un estado cuántico frágil que no se puede inspeccionar sin destruirlo.

## Algoritmos: Shor y Grover

Dos algoritmos ilustran qué tipo de ventaja se busca:

- **Shor** (1994): factoriza números enteros grandes en tiempo **exponencialmente** menor que el mejor algoritmo clásico conocido. Su relevancia es enorme porque la criptografía de clave pública actual (RSA) se apoya en que factorizar es intratable clásicamente. Un ordenador cuántico suficientemente grande la rompería —de ahí la carrera por la **criptografía post-cuántica**, algoritmos clásicos resistentes a ataques cuánticos que ya se están estandarizando y desplegando de forma preventiva—.
- **Grover** (1996): busca en una base de datos no estructurada de $N$ elementos en $\sqrt{N}$ pasos, frente a los $N$ clásicos. Es una aceleración **cuadrática**, más modesta que la exponencial de Shor pero de aplicación amplia (optimización, búsqueda).

Es crucial el matiz: la ventaja cuántica **no es universal**. Solo ciertos problemas con la estructura adecuada admiten aceleración; para la inmensa mayoría de tareas cotidianas, un ordenador cuántico no aporta nada frente a uno clásico. La computación cuántica es un acelerador especializado para problemas concretos —simular moléculas y materiales, optimización, ciertos problemas criptográficos—, no un reemplazo general del ordenador.

## El gran obstáculo: la corrección de errores

Los estados cuánticos son extraordinariamente **frágiles**: la más mínima interacción con el entorno —calor, vibración, un campo parásito— destruye la superposición y el entrelazamiento, un proceso llamado **decoherencia**. Los qubits físicos actuales mantienen su estado apenas microsegundos a milisegundos y cometen errores con frecuencia miles de veces mayor que un transistor clásico. Sin remedio, ningún cálculo largo sobreviviría.

La solución teórica es la **corrección cuántica de errores**: combinar muchos qubits físicos ruidosos en un **qubit lógico** protegido, redundante y estable. El coste es brutal: según el esquema, hacen falta del orden de cientos o miles de qubits físicos por cada qubit lógico útil. Por eso un ordenador cuántico *tolerante a fallos* de valor práctico requiere millones de qubits físicos, cuando hoy los mayores tienen cientos o pocos miles. Cerrar esa brecha es el reto central del campo, y en 2024-2025 se han logrado hitos importantes de corrección (qubits lógicos que mejoran al añadir físicos), aunque la meta sigue a años de distancia.

## Era NISQ y estado de la industria

El presente se conoce como era **NISQ** (*Noisy Intermediate-Scale Quantum*): procesadores de decenas a cientos de qubits, **ruidosos** y **sin corrección de errores** completa. Son útiles para investigación, para explorar algoritmos y quizá para nichos concretos, pero **no** para las aplicaciones transformadoras (romper RSA, simular química compleja), que exigen la era tolerante a fallos aún no alcanzada. Existen varias plataformas físicas en competencia —superconductores (enfriados a casi el cero absoluto), iones atrapados, fotónica, átomos neutros—, cada una con ventajas e inconvenientes y sin un ganador claro.

El consejo de realismo: la computación cuántica es un campo con fundamentos sólidos y avances reales, pero rodeado de exageración. No es "el próximo ordenador de tu bolsillo" ni una IA superpoderosa; es un acelerador especializado, todavía experimental, cuyo impacto práctico —enorme en su dominio— llegará por etapas a lo largo de la próxima década o más. Distinguir la promesa genuina del bombo es parte de la alfabetización tecnológica.

## Ideas clave

- Un qubit puede estar en superposición $|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$; $n$ qubits representan $2^n$ estados a la vez, pero medir colapsa a uno solo: la computación cuántica orquesta interferencias para que salga la respuesta correcta.
- El entrelazamiento correlaciona qubits sin análogo clásico y es un recurso computacional esencial (y la base de la comunicación cuántica).
- Los circuitos cuánticos aplican puertas reversibles (Hadamard, CNOT…) que tejen superposición e interferencia; el estado intermedio es frágil e ininspeccionable.
- Shor factoriza en tiempo exponencialmente menor (amenaza a RSA, de ahí la criptografía post-cuántica) y Grover da aceleración cuadrática en búsqueda; la ventaja no es universal, solo para problemas estructurados.
- La decoherencia hace los qubits frágiles; la corrección de errores exige cientos-miles de qubits físicos por qubit lógico. Estamos en la era NISQ (ruidosa, sin corrección plena): avances reales, pero el impacto transformador aún está a años.

## Para seguir

De la información cuántica en el procesador pasamos a moverla y a manipular luz: la próxima lección trata la *fotónica y las comunicaciones ópticas avanzadas*, incluida la distribución cuántica de claves.
