# Serie «Robótica» — reels de divulgación (2026-10-08)

Diez reels de 24 a 27 s, solo texto y sonido sintético (sin voz), en formato película: título → cuerpo a ritmo de lectura → logo de
Co.De → el logo se disuelve en el título (loop sin corte). Tema **Robótica** con **fondo vertical propio** (`fondos_reel.py`,
generador «robotica»): hilera de engranes de metal como horizonte, borde y resplandor naranja de seguridad, cielo grafito.

**De qué trata:** la ciencia aplicada de la robótica, contada a partir del **rover planetario** y la plataforma **ROS 2** del
`ros2-workspace` (la misma que la Estación ATP): suspensión, tracción, navegación, seguridad, operación a distancia, cómo se valida
un resultado y cómo se arma un robot con piezas que se hablan. Todo **simulado** (chip en pantalla); **ninguna cifra es medida con
hardware** y los suelos de Marte, Titán y Ceres son supuestos del modelo. Fuente: `ros2-workspace` commit 498eb6f, `docs/ROVER.md`
(R1–R10), `docs/ROS2_CONTROL.md`. Pocas cifras, cada una con una comparación; los detalles están aquí. Sin tesis ni clientes.
Máximo 5 hashtags. Decir siempre «en simulación».

**Orden sugerido:** Seis ruedas → Gira igual, avanza menos → Misma orden, cinco mundos → ¿Por dónde se va? → Un robot que sabe parar →
¿Por qué no se maneja con joystick? → ¿Cuánto avanza en un día? → Mejoró, hasta que lo pusimos a prueba → Un robot es una conversación
→ El mismo cerebro, otro cuerpo.

| Reel | Duración | Idea | Fuente |
|---|---|---|---|
| ReelRobBogie | 24.6 s | Rocker-bogie: el cuerpo sube ⅓ de lo que sube una rueda | `ROVER.md` R6 §1 (reparto 1/6 por rueda) |
| ReelRobPatina | 24.6 s | Deslizamiento: la rueda gira igual y avanza menos | `ROVER.md` R1 (Bekker–Wong), R6 §3 |
| ReelRobMundos | 25.6 s | La misma orden en cinco mundos (8.5 / 8.7 / 7.8 / 7.0 / 4.0 de 10 m) | `ROVER.md` R1, tabla «Misma orden, distinto cuerpo» |
| ReelRobRuta | 25.6 s | Planificar una ruta (A*) rodeando una colina | `ROVER.md` R2 |
| ReelRobAlarmas | 25.6 s | Alarmas de pendiente (25°) y vuelco (35°); ≈ 6× más lejos con alarmas | `ROVER.md` R2, R8 |
| ReelRobRetardo | 25.6 s | Retardo de luz: 1 s a la Luna, minutos a Marte | `ROVER.md` R7–R8 |
| ReelRobAutonomo | 25.6 s | Metros por día en Marte: teleoperado vs autónomo | `ROVER.md` R8 (tabla «Distancia útil») |
| ReelRobValidacion | 26.6 s | Mejoró en pruebas conocidas; empeoró en casos nuevos (94 → 69) y se corrigió (93) | `ROVER.md` R10 |
| ReelRobROS | 26.6 s | Un robot como piezas que se mandan mensajes (ROS 2) y un reloj común | `ROVER.md` R9; `CONTRATO.md` §18 |
| ReelRobCerebro | 26.6 s | Un controlador, varios cuerpos: se cambia el «enchufe» | `ROS2_CONTROL.md` |

---

## 1 · ReelRobBogie — «¿Por qué seis ruedas y no cuatro?»
**Pie:** Una suspensión de balancines hace que cada rueda suba por su cuenta cuando se topa con una roca: si una rueda sube 3, el
cuerpo sube solo 1, así que el robot sigue casi nivelado. Con seis ruedas, el peso se reparte en seis partes iguales. 🤖
#robotica #ingenieria #espacio #ROS2 #divulgacion
**⚠️ Cuidado:** en simulación. La geometría 2:1 del rocker-bogie hace que el cuerpo suba el promedio de las tres alturas (⅓ de la
subida de una sola rueda); dibujo esquemático. **Hallazgo del propio proyecto:** en el ensayo de escalón no se observó una ventaja del
rocker-bogie sobre la suspensión simple (el límite fue el mismo, 0.15 m en Marte); su aporte medido es el reparto de carga. El margen
de vuelco con rocas sigue sin validarse.

## 2 · ReelRobPatina — «Gira igual, avanza menos»
**Pie:** Dos ruedas giran exactamente lo mismo. En suelo firme avanzan casi todo lo que giran; en arena suelta, el suelo cede y la
rueda avanza menos (6 de cada 10 metros). A esa diferencia se le llama deslizamiento, y medirlo le dice al robot cuánto agarre tiene. 🛞
#robotica #fisica #espacio #ingenieria #divulgacion
**⚠️ Cuidado:** los porcentajes (96 % y 62 %) son ilustrativos. El modelo del proyecto usa tracción tipo Bekker–Wong simplificada; con
el rover real la velocidad lograda ≈ (1 − deslizamiento) × la orden.

## 3 · ReelRobMundos — «Misma orden, cinco mundos»
**Pie:** Le pedimos al mismo robot avanzar 10 metros en cinco mundos. Avanza 8.5 m en la Luna, 8.7 en Marte, 7.8 en la Tierra, 7.0 en
Titán… y solo 4 en Ceres: con tan poca gravedad, las ruedas casi no agarran. 🌍🌕
#robotica #espacio #planetas #fisica #divulgacion
**⚠️ Cuidado:** simulación; rover de 150 kg, ruedas de 0.25 m, 1 m/s durante 10 s, incluye el arranque. **Los suelos de Marte, Titán y
Ceres son supuestos** (no medidos). Cifras con la física corregida (`rodadura_en_motor: true`).

## 4 · ReelRobRuta — «¿Por dónde se va?»
**Pie:** Antes de moverse, el robot piensa la ruta: prueba caminos y los va descartando, porque cada cuadro del mapa tiene un costo
(subir cansa más). Elige el más barato que no sea peligroso y rodea la colina en vez de cruzarla. 🗺️
#robotica #IA #algoritmos #espacio #divulgacion
**⚠️ Cuidado:** mapa y costos ilustrativos; el planificador del proyecto es un A* de 8 vecinos con costo por pendiente y rugosidad y
celdas intransitables (≥ 20° de pendiente). Aquí se simplificó con una colina circular.

## 5 · ReelRobAlarmas — «Un robot que sabe cuándo parar»
**Pie:** El robot mide su propia inclinación; si pasa el límite, se detiene sola antes de volcar, sin esperar órdenes de la Tierra. En
una simulación en Marte, con alarmas locales avanza unas 6 veces más lejos que sin ellas. 🚨
#robotica #seguridad #espacio #ingenieria #divulgacion
**⚠️ Cuidado:** alarma de pendiente a 25° y de vuelco a 35° (parámetros del proyecto, supuestos). El «6 veces» sale de 2 040 m/sol
(con alarmas) frente a 312 m/sol (sin ellas) en Marte, llano, con **intervalos de confianza muy anchos** (3 semillas): es del orden de
magnitud, no una medida. La rampa y el robot del reel son esquemáticos.

## 6 · ReelRobRetardo — «¿Por qué no se maneja con joystick?»
**Pie:** A la Luna, una orden tarda 1 segundo en llegar. A Marte tarda minutos (de 3 a 22 según dónde estén los planetas). Con tanta
espera no se puede manejar en vivo: el robot tiene que decidir solo. 📡
#robotica #espacio #Marte #comunicaciones #divulgacion
**⚠️ Cuidado:** la escala de tiempo de la animación está exagerada (chip en pantalla). Retardo Tierra–Luna: 1.28 s; Marte: ≈ 11 min en
la fecha simulada (varía entre ≈ 3 y ≈ 22 min). Con ventanas reales del orbitador la entrega de una orden tarda más (el proyecto midió
45 min en un caso). En el modelo, la teleoperación rinde la mitad con ≈ 17 s de luz de una vía.

## 7 · ReelRobAutonomo — «¿Cuánto avanza en un día?»
**Pie:** En una simulación en Marte, manejarlo desde la Tierra rinde unos 10 metros por día: cada orden espera al satélite y a la luz.
Si decide solo y se cuida, avanza unos 2 kilómetros; sin cuidarse, unos 300 m. 🏜️
#robotica #Marte #autonomia #espacio #divulgacion
**⚠️ Cuidado:** simulación de R8 (docs/ROVER.md): 9, 80, 312 y 2 040 m/sol (media de 3 semillas, **IC95 muy anchos**, p. ej. 2 040 ±
1 949); supuestos propios: 2 h de conducción por sol, 0.5 m/s, operador disponible 24 h, enlace con ventanas del relé MRO. Un rover real
recorre mucho menos; el «gemelo digital» no mostró ganancia medible. Se redondea a «≈» en pantalla.

## 8 · ReelRobValidacion — «Mejoró, hasta que lo pusimos a prueba»
**Pie:** Afinamos el robot con los casos de siempre y parecía igual de bueno que la versión simple. Con 150 casos nuevos, empeoró: de 94
a 69 de cada 100 llegaron a la meta. Encontramos la causa (una alarma demasiado nerviosa que se detenía ante cualquier borde) y quedó
en 93. Probar con casos nuevos evitó una falsa mejora. 🔬
#ciencia #robotica #datos #ingenieria #divulgacion
**⚠️ Cuidado:** R10 (docs/ROVER.md): conjuntos disjuntos y criterios fijados antes de correr; 141/150 (básica), 103/150 (la «completa» de R6),
140/150 (la corregida); los 87 y 83 «de 100» son 52/60 y 50/60 en el conjunto donde se afinó (escalados a 100). **La versión corregida
no supera a la simple**: recupera casi toda su llegada pero gasta ~15 % más de energía por metro y tuvo un vuelco; no se midió ninguna
ventaja de navegar con planificación. Los puntos de la animación son ilustrativos de esos conteos.

## 9 · ReelRobROS — «Un robot es una conversación»
**Pie:** Un robot no es un solo programa: es un cuerpo, un cerebro y una radio que se hablan mandándose mensajes («estado» y «orden»).
Eso es ROS 2, el idioma común de los robots. Con un reloj común, el resultado es idéntico cada vez: con y sin ROS, byte a byte. 🧩
#ROS2 #robotica #software #ingenieria #divulgacion
**⚠️ Cuidado:** R9: la cadena en ROS dio los mismos bytes de telemetría que el lazo sin ROS en todos los casos probados (6 escenas de
2 a 2 760 s), en simulación y en el mismo contenedor. Los nombres técnicos (`rover_dinamica`, `rover_navegador`, `rover_enlace`) son
los nodos reales; el diagrama de flechas es simplificado.

## 10 · ReelRobCerebro — «El mismo cerebro, otro cuerpo»
**Pie:** Con ros2_control, el mismo controlador puede mover una montura de antena simulada, una en un simulador 3D (Gazebo) o, en el
futuro, una real: se cambia el «enchufe» (una línea), no el cerebro. La montura real es el siguiente paso: aún no se ha probado. 🔌
#ROS2 #robotica #antenas #ingenieria #divulgacion
**⚠️ Cuidado:** `docs/ROS2_CONTROL.md`: el plugin de hardware `AtpMountSystem` (backends `sim` y `serial`) y Gazebo; **nada se ha probado
con hardware real** (el firmware «nunca se ha cargado en una placa», `docs/HARDWARE.md`). No afirmar que funciona en una antena real.
