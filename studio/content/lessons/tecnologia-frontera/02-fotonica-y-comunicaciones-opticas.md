---
title: Fotónica y comunicaciones ópticas avanzadas
level: medio
summary: La fotónica de silicio que lleva la luz al chip, la comunicación óptica en espacio libre y los enlaces láser intersatelitales, la distribución cuántica de claves (QKD y BB84) con las redes cuánticas, y el LiFi.
tags: [fotonica, optica, fso, laser-intersatelital, qkd, lifi]
minutes: 12
order: 2
---

## Objetivos

- Entender qué es la fotónica de silicio y por qué la luz entra en los chips.
- Comprender la comunicación óptica en espacio libre y el enlace láser entre satélites.
- Explicar la distribución cuántica de claves (QKD) y la intuición de BB84.
- Situar las redes cuánticas y sus retos.
- Conocer el LiFi como comunicación por luz visible.

## Fotónica: computar y comunicar con luz

La **fotónica** usa **fotones** (luz) donde la electrónica usa electrones. La luz tiene ventajas notables como portadora de información: viaja rapidísimo, distintas longitudes de onda (colores) pueden compartir el mismo medio sin interferirse —lo que multiplica la capacidad—, y no genera el calor resistivo que limita a los circuitos eléctricos. Por eso las comunicaciones de larga distancia (la fibra óptica que sostiene Internet) son ópticas desde hace décadas.

La frontera actual es la **fotónica de silicio**: fabricar componentes ópticos —guías de onda, moduladores, detectores— sobre chips de silicio con las mismas técnicas que los circuitos electrónicos, integrando luz y electrónica en el mismo sustrato. Su motor es la demanda de los centros de datos y la IA: mover enormes volúmenes de datos entre chips y servidores con cobre consume demasiada energía y limita el ancho de banda, y los **interconectores ópticos** lo resuelven llevando la fibra hasta el borde del procesador (y, en desarrollo, dentro de él). Se investiga además la **computación fotónica** —hacer operaciones, en especial las multiplicaciones matriciales de la IA, directamente con luz—, prometedora en eficiencia energética aunque aún incipiente.

## Comunicación óptica en espacio libre (FSO)

La fibra guía la luz por un cristal; la **comunicación óptica en espacio libre** (*Free-Space Optics*, FSO) la envía como un **haz láser a través del aire o el vacío**, sin cable. Frente a la radio, ofrece anchos de banda enormes, haces muy estrechos (difíciles de interceptar y sin licencia de espectro) y equipos compactos. Su talón de Aquiles en la atmósfera es el clima: niebla, lluvia y turbulencia degradan o cortan el enlace, por lo que en tierra se usa en tramos cortos o como respaldo.

Donde FSO brilla es en el **espacio**, sin atmósfera que estorbe. Los **enlaces láser intersatelitales** (*optical inter-satellite links*, OISL) conectan satélites entre sí con haces ópticos, y son la columna vertebral de las megaconstelaciones LEO modernas: permiten enrutar datos de satélite a satélite por el espacio —a la velocidad de la luz en el vacío, mayor que en la fibra— sin bajar a una estación terrena en cada salto, reduciendo latencia y dependencia de infraestructura terrestre. Es la misma malla óptica que aparecía en las categorías de redes y de 6G/NTN, vista ahora desde la tecnología que la habilita. El reto de ingeniería es el **apuntamiento**: alinear un haz estrechísimo entre dos plataformas que se mueven a kilómetros por segundo exige un control de precisión extraordinaria —el problema de apuntamiento satelital llevado al límite—.

## Distribución cuántica de claves (QKD)

La fotónica también habilita una forma de seguridad basada en la física, no en la dificultad matemática: la **distribución cuántica de claves** (*Quantum Key Distribution*, QKD). Su objetivo es que dos partes compartan una clave secreta con una garantía única: **si alguien la intercepta, se nota**. La razón es un principio cuántico —medir un estado cuántico lo perturba—: un espía que intente leer los fotones en tránsito altera inevitablemente sus estados, introduciendo errores detectables que delatan su presencia.

El protocolo pionero, **BB84** (1984), da la intuición: el emisor envía fotones individuales polarizados eligiendo al azar entre dos bases (dos formas de codificar); el receptor los mide eligiendo también bases al azar; luego comparan públicamente *qué bases* usaron (no los valores) y conservan solo los casos en que coincidieron. Si un espía interceptó, sus mediciones a ciegas habrán introducido errores en una fracción de esos casos, que las partes detectan comparando una muestra. Sin espía, la tasa de error es baja y la clave es segura; con espía, lo descubren y descartan la clave. QKD ya funciona comercialmente por fibra en distancias limitadas (los fotones se pierden, y no se pueden amplificar sin destruirlos, lo que restringe el alcance) y por enlace satelital para saltos largos —el satélite chino Micius demostró QKD a escala intercontinental—.

## Redes cuánticas

QKD es el primer paso hacia una **internet cuántica** más ambiciosa: una red capaz de distribuir **entrelazamiento** (el recurso de la lección anterior) entre nodos distantes, para conectar ordenadores cuánticos, sincronizar relojes con precisión extrema o hacer sensado distribuido. El obstáculo central es que los estados cuánticos **no se pueden copiar ni amplificar** (el teorema de no-clonación), así que los repetidores clásicos no sirven; se necesitan **repetidores cuánticos**, que almacenan y "estiran" el entrelazamiento por tramos, y que siguen siendo en gran medida experimentales. Es una tecnología a más largo plazo que QKD, pero con potencial de transformar tanto la seguridad como la computación distribuida.

## LiFi: datos por luz visible

En el extremo cotidiano de la fotónica está el **LiFi**: transmitir datos modulando la intensidad de **luces LED** de iluminación a frecuencias imperceptibles para el ojo, de modo que una lámpara ilumina y comunica a la vez, y un receptor (fotodetector) recupera los datos. Frente al WiFi ofrece anchos de banda potencialmente enormes (el espectro de la luz visible es vastísimo y sin licencia), **seguridad física** (la luz no atraviesa paredes, así que la señal no se filtra fuera de la habitación) y ausencia de interferencia electromagnética —útil en hospitales, aviones o entornos industriales sensibles—. Sus límites son evidentes: necesita línea de visión y no funciona a través de obstáculos, por lo que se plantea como **complemento** del WiFi en interiores, no como sustituto. Ilustra bien el espíritu de la fotónica: exprimir la luz, de la escala del chip a la del cosmos, como portadora de información.

## Ideas clave

- La fotónica usa luz en lugar de electrones: alta velocidad, multiplexación por color y menos calor; la fotónica de silicio integra óptica y electrónica en el chip para los interconectores ópticos que demandan los centros de datos y la IA.
- FSO transmite por haz láser sin cable; en el espacio, los enlaces láser intersatelitales forman la malla óptica de las constelaciones LEO, con el apuntamiento de precisión como reto clave.
- QKD comparte claves con seguridad garantizada por la física: interceptar perturba los fotones y se detecta; BB84 lo logra comparando bases y midiendo errores; funciona por fibra (alcance limitado) y por satélite.
- Las redes cuánticas buscan distribuir entrelazamiento entre nodos, pero el no-clonado impide amplificar y exige repetidores cuánticos, aún experimentales.
- LiFi transmite datos por luz LED visible: gran ancho de banda y seguridad física (no atraviesa paredes) pero requiere línea de visión; complemento del WiFi en interiores.

## Para seguir

De mover información con luz pasamos a procesarla de formas nuevas y cerca de donde se genera: la próxima lección trata la *computación neuromórfica y el edge*.
