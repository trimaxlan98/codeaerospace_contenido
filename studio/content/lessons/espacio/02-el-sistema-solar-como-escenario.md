---
title: El sistema solar como escenario de misiones
level: intro
summary: Las regiones orbitales de interés, los puntos de Lagrange y su uso, y el papel del viento solar en el clima espacial.
tags: [sistema-solar, lagrange, leo, geo, viento-solar]
minutes: 7
order: 2
---

## Objetivos

- Distinguir las principales regiones orbitales de interés para misiones espaciales.
- Entender qué son los puntos de Lagrange y por qué L2 es clave para observatorios como el JWST.
- Explicar el origen del viento solar y su relación con el clima espacial.
- Ubicar las órbitas cislunares e interplanetarias dentro del mapa general de misiones.

## Regiones de interés: LEO, MEO, GEO, cislunar e interplanetario

El espacio cercano a la Tierra se organiza en bandas orbitales con propiedades y usos muy distintos:

| Región | Altitud aproximada | Periodo orbital | Usos típicos |
|---|---|---|---|
| LEO (órbita baja) | 160–2000 km | 90–127 min | Observación de la Tierra, ISS, megaconstelaciones |
| MEO (órbita media) | 2000–35 786 km | 2–24 h | Navegación (GPS, Galileo, GLONASS) |
| GEO (geoestacionaria) | 35 786 km | 24 h (sincrónica con la Tierra) | Comunicaciones, meteorología, alerta temprana |
| Cislunar | hasta ~400 000 km (órbita lunar) | variable | Estaciones lunares (Gateway), tránsito a la Luna |
| Interplanetario | > 1.5 millones de km (más allá de la esfera de influencia terrestre) | años | Sondas planetarias, misiones a asteroides |

La órbita geoestacionaria es un caso particular de MEO/GEO: un satélite a 35 786 km de altitud sobre el ecuador, con inclinación cero, tiene un periodo orbital de exactamente un día sidéreo (23 h 56 min), por lo que permanece fijo respecto a un observador en tierra. Esto la hace ideal para comunicaciones y meteorología, pero la distancia introduce una latencia de señal notable (ver la lección de comunicaciones satelitales). Las órbitas cislunares —entre la órbita terrestre y la lunar— cobran relevancia con programas como Artemis y la estación Gateway, planeada en una órbita casi rectilínea de halo (NRHO) alrededor de la Luna.

## Puntos de Lagrange y sus usos

En el problema de los tres cuerpos restringido (por ejemplo, Sol-Tierra o Tierra-Luna), existen cinco puntos de equilibrio gravitacional donde la atracción combinada de los dos cuerpos masivos y la fuerza centrífuga del marco rotante se cancelan: los **puntos de Lagrange**, L1 a L5.

- **L1**: entre el Sol y la Tierra, a ~1.5 millones de km de la Tierra. Ofrece vista continua del Sol; usado por observatorios solares como SOHO y DSCOVR.
- **L2**: en dirección opuesta al Sol respecto a la Tierra, también a ~1.5 millones de km. Ofrece un ambiente térmico muy estable y el Sol, la Tierra y la Luna quedan detrás del observador, ideal para telescopios infrarrojos. El **James Webb Space Telescope (JWST)** orbita L2 en una órbita de halo, manteniendo su escudo solar siempre orientado hacia el Sol/Tierra/Luna para proteger sus instrumentos criogénicos (~40 K).
- **L3**: detrás del Sol, opuesto a la Tierra; de poco uso práctico por la dificultad de comunicación.
- **L4 y L5**: forman triángulos equiláteros con el Sol y la Tierra, 60° adelante y detrás en la órbita terrestre. Son puntos establemente estables (a diferencia de L1-L3, que son inestables y requieren correcciones de trayectoria periódicas) y acumulan naturalmente polvo interplanetario y, en el sistema Sol-Júpiter, los asteroides troyanos.

Los puntos L1 y L2 no son órbitas exactas alrededor de un punto vacío, sino que las naves orbitan alrededor de ellos en trayectorias llamadas **órbitas de halo** o Lissajous, que evitan apuntar instrumentos sensibles directamente a la línea Sol-Tierra y requieren pequeñas correcciones de mantenimiento de estación cada pocas semanas debido a la inestabilidad dinámica del punto.

## Viento solar y clima espacial

El Sol emite continuamente un flujo de partículas cargadas —principalmente protones y electrones— conocido como **viento solar**, con velocidades típicas de 300 a 800 km/s y densidades de unas pocas partículas por cm³ a la altura de la órbita terrestre. Este flujo, junto con el campo magnético interplanetario que arrastra consigo, moldea la magnetosfera terrestre: la comprime del lado diurno (a unos 10 radios terrestres) y la estira en una larga cola magnética del lado nocturno (cientos de radios terrestres).

Cuando el Sol libera fulguraciones (*solar flares*) o eyecciones de masa coronal (CME, *coronal mass ejections*) —explosiones de plasma magnetizado que pueden viajar a más de 2000 km/s— el impacto sobre la magnetosfera terrestre produce lo que se conoce como **clima espacial**. Sus efectos incluyen auroras polares, tormentas geomagnéticas que inducen corrientes en redes eléctricas terrestres, degradación de las señales de GPS por perturbaciones ionosféricas, aumento del arrastre atmosférico en LEO (al calentarse y expandirse la termosfera) y riesgo de daño a la electrónica de satélites por partículas de alta energía. El monitoreo de este fenómeno usa índices como el Kp (actividad geomagnética global, escala 0–9) y es objeto de estudio detallado en la lección dedicada a clima espacial más adelante en este curso.

## Trayectorias entre regiones

Moverse entre estas regiones tiene un costo energético (delta-v) creciente: de LEO a GEO se requieren maniobras de transferencia como la órbita de transferencia geoestacionaria (GTO), una elipse con perigeo en LEO (~200 km) y apogeo en GEO (~35 786 km), seguida de una maniobra de circularización en el apogeo. Llegar a la Luna o a puntos de Lagrange cislunares requiere delta-v adicional del orden de 3.1–3.2 km/s desde LEO, mientras que escapar por completo de la esfera de influencia terrestria hacia el espacio interplanetario exige superar la velocidad de escape local, típicamente sumando otros ~0.5–1 km/s adicionales a las trayectorias lunares dependiendo del destino final.

## Ideas clave

- LEO, MEO y GEO no son solo bandas de altitud: cada una impone un compromiso distinto entre cobertura, latencia y costo de acceso.
- L1 y L2 son puntos de equilibrio inestable útiles por su geometría (vista continua del Sol o sombra permanente del sistema Tierra-Luna-Sol), no por ser "estacionarios" en sentido estricto.
- El JWST usa L2 precisamente porque ahí el escudo solar puede bloquear simultáneamente Sol, Tierra y Luna mientras mantiene una temperatura operativa estable.
- El viento solar y las CME son la causa física del clima espacial, con efectos medibles en arrastre atmosférico, ionosfera y electrónica de satélites.
- Los puntos L4 y L5 son dinámicamente estables y acumulan naturalmente material (asteroides troyanos en el caso Sol-Júpiter).

## Para seguir

La lección *Cohetes y acceso al espacio* explica cómo se alcanzan físicamente estas órbitas mediante propulsión y maniobras orbitales, incluida la transferencia a GTO mencionada aquí. *Clima espacial y sus efectos*, al cierre de esta categoría, profundiza en los mecanismos del viento solar y las tormentas geomagnéticas introducidos en esta lección.
