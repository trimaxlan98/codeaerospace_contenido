---
title: El entorno espacial
level: intro
summary: Dónde empieza el espacio, sus capas atmosféricas, el vacío, la radiación y los ciclos térmicos que enfrenta una nave.
tags: [espacio, atmosfera, radiacion, van-allen, termico]
minutes: 8
order: 1
---

## Objetivos

- Ubicar la línea de Kármán y entender por qué "el espacio" no tiene un borde físico tajante.
- Describir las capas de la atmósfera terrestre y su efecto sobre satélites en órbita baja.
- Explicar el origen y la estructura de los cinturones de Van Allen.
- Comprender los ciclos térmicos que sufre una nave por la alternancia de luz solar y eclipse.
- Reconocer el riesgo de micrometeoritos y basura como amenaza estructural.

## Dónde empieza el espacio

No existe una frontera física entre la atmósfera y el espacio: la densidad del aire decae exponencialmente con la altitud sin cortes abruptos. Por convención, la Federación Aeronáutica Internacional (FAI) fija la **línea de Kármán a 100 km** de altitud como el límite oficial del espacio. Este valor no es arbitrario: fue propuesto por Theodore von Kármán al notar que, por encima de esa altura, una aeronave necesitaría volar a velocidad orbital para generar suficiente sustentación aerodinámica, ya que el aire es demasiado tenue. En la práctica esto significa que "volar" pierde sentido: cualquier objeto que quiera sostenerse ahí debe hacerlo por velocidad orbital, no por portancia.

Otros organismos usan criterios distintos. La NASA y la Fuerza Aérea de EE. UU. han otorgado alas de astronauta a pilotos que superaron los 80 km (50 millas), y el investigador Jonathan McDowell propuso en 2018, con datos de decaimiento orbital real de satélites, que el límite físicamente más consistente está cerca de **80 km**, porque es ahí donde el arrastre atmosférico empieza a dominar sobre las fuerzas gravitacionales en la dinámica orbital de corto plazo. La discrepancia entre 80 y 100 km ilustra que el "borde del espacio" es una convención útil, no una ley física.

## Capas de la atmósfera y arrastre residual

La atmósfera terrestre se divide en capas según su perfil de temperatura:

| Capa | Altitud aproximada | Característica principal |
|---|---|---|
| Troposfera | 0–12 km | Clima, convección, 80% de la masa atmosférica |
| Estratosfera | 12–50 km | Capa de ozono, temperatura creciente con altura |
| Mesosfera | 50–85 km | Capa más fría de la atmósfera (~-90 °C); aquí se queman meteoritos |
| Termosfera | 85–600 km | Temperatura muy alta (hasta 2000 K) pero densidad ínfima; aquí orbita la ISS y la mayoría de satélites LEO |
| Exosfera | 600–10 000 km | Transición gradual al vacío interplanetario |

Aunque a 400 km (altitud típica de la Estación Espacial Internacional) la densidad atmosférica es billones de veces menor que al nivel del mar, no es cero. Ese arrastre residual frena progresivamente a los satélites en órbita baja, reduciendo su energía orbital y obligándolos a maniobras periódicas de reimpulso ("reboost"). La ISS pierde entre 50 y 150 metros de altitud por día dependiendo de la actividad solar (que expande la termosfera al calentarla), y requiere reimpulsos regulares con los motores de las naves Progress o el módulo Zvezda. Satélites sin propulsión en órbitas por debajo de 600 km reentran en cuestión de años; por encima de 1000 km, el arrastre es prácticamente despreciable y las órbitas pueden persistir siglos o milenios.

## Vacío y radiación: los cinturones de Van Allen

Por encima de la termosfera, la densidad de partículas es tan baja que se considera vacío técnico (presiones inferiores a $10^{-9}$ Pa en el espacio profundo). Pero "vacío" no significa "vacío de radiación": el campo magnético terrestre atrapa partículas cargadas del viento solar y los rayos cósmicos, formando los **cinturones de Van Allen**, descubiertos en 1958 por el primer satélite estadounidense, Explorer 1.

Hay dos cinturones principales:

- **Cinturón interior**: entre 1000 y 6000 km de altitud (~1.2 a ~2 radios terrestres, medidos desde el centro de la Tierra), compuesto principalmente por protones de alta energía (hasta cientos de MeV), relativamente estable en el tiempo.
- **Cinturón exterior**: entre 13 000 y 60 000 km de altitud (3 a 10 radios terrestres), dominado por electrones relativistas, mucho más dinámico y variable con la actividad solar.

Entre ambos existe una "zona de ranura" (*slot region*) de menor flujo, alrededor de 2–3 radios terrestres, que en ocasiones se llena temporalmente tras tormentas geomagnéticas intensas. Los satélites GEO (35 786 km) orbitan cerca del borde exterior del cinturón exterior y reciben dosis de radiación significativas a lo largo de su vida útil, por lo que su electrónica requiere blindaje y componentes tolerantes a radiación (rad-hard). Las órbitas MEO usadas por constelaciones de navegación como GPS (~20 200 km) atraviesan de lleno el cinturón interior, lo que obliga a diseños electrónicos especialmente robustos.

## Temperatura, ciclos térmicos y micrometeoritos

En órbita baja, un satélite típico completa una vuelta a la Tierra cada 90–100 minutos, de los cuales pasa entre 30 y 40 minutos en la sombra de la Tierra (eclipse). Esto genera un ciclo térmico extremo: la cara iluminada de una nave puede alcanzar +120 °C mientras la cara en sombra desciende a -100 °C o menos, con transiciones que ocurren en minutos al entrar o salir del eclipse. Este ciclo se repite entre 5000 y 6000 veces al año, y el estrés térmico resultante (dilatación y contracción cíclica de materiales con distintos coeficientes de expansión) es una de las principales causas de fatiga estructural y fallas en soldaduras, paneles solares y recubrimientos ópticos. Por eso el subsistema térmico de un satélite usa mantas multicapa (MLI), radiadores, calentadores resistivos y recubrimientos con propiedades ópticas específicas (alta reflectividad solar, alta emisividad infrarroja) para mantener la electrónica dentro de rangos operativos, típicamente entre -20 °C y +50 °C.

A esto se suma el riesgo de impactos de **micrometeoritos** y desechos orbitales (MMOD, *micrometeoroid and orbital debris*). Aunque las partículas de milímetros son las más numerosas, su velocidad relativa —hasta 20 km/s para meteoritos de origen cometario, y 7–15 km/s para restos de basura espacial en LEO— les confiere una energía cinética enorme: un fragmento de aluminio de 1 cm a 10 km/s porta energía comparable a una bola de bolos lanzada a cientos de km/h. Para mitigar el daño se usan blindajes Whipple: una lámina delgada separada de la estructura principal que fragmenta y dispersa el proyectil antes de que llegue al casco, reduciendo drásticamente la energía transferida.

## Ideas clave

- La línea de Kármán (100 km) es la convención oficial para el "borde del espacio", aunque el arrastre atmosférico ya domina la dinámica orbital desde altitudes menores (~80 km según McDowell).
- La atmósfera no termina abruptamente: el arrastre residual en la termosfera (300–600 km) obliga a reimpulsos periódicos en satélites LEO como la ISS.
- Los cinturones de Van Allen (interior: protones, 1000–6000 km; exterior: electrones, 13 000–60 000 km) exigen electrónica rad-hard en satélites que los atraviesan o permanecen cerca.
- Los ciclos térmicos por eclipse (miles al año, con saltos de +120 °C a -100 °C) son una fuente crítica de fatiga estructural.
- El blindaje Whipple mitiga el riesgo de micrometeoritos y basura orbital fragmentando el impacto antes de que alcance el casco.

## Para seguir

La siguiente lección, *El sistema solar como escenario de misiones*, sitúa este entorno dentro del contexto más amplio de regiones orbitales (LEO/MEO/GEO/cislunar/interplanetario), puntos de Lagrange y clima espacial. Más adelante, *Cohetes y acceso al espacio* explica cómo se llega a estas órbitas, y *Basura espacial y sostenibilidad orbital* junto con *Clima espacial y sus efectos* profundizan en dos de los riesgos mencionados aquí: los desechos y las tormentas solares.
