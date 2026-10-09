# Serie «Electrónica espacial» — reels de divulgación (2026-10-09)

Diez reels de unos 26 s, solo texto y sonido sintético (sin voz), en formato película (título → cuerpo → logo de Co.De → loop).
Tema Electrónica con fondo vertical propio (canto de una placa de circuito con conector dorado, pistas y un chip QFP). Escena
`44-reels-electronica.py`, datos `datos_el.py` (cuentas de `electronica_espacio.py`, con sus pruebas: `python3 electronica_espacio.py`).
**No hay mediciones propias**: son cálculos de libro y cifras públicas, con supuestos declarados abajo. Sin tesis ni clientes.

---

## 1 · ReelELBit — «Un rayo cósmico cambia un 0 por un 1»
**Pie:** Una sola partícula del espacio puede cruzar un chip de memoria y cambiar un 0 por un 1. No rompe nada: deja una chispa de carga eléctrica, unas 100 veces más de lo que basta para voltear un bit. En órbita pasa una y otra vez.
**Hashtags:** #Electrónica #RayosCósmicos #Satélites #Radiación #CoDeAerospace
⚠️ Ilustración del «single event upset» (SEU). Ion con LET 10 MeV·cm²/mg que cruza 1 µm de silicio: Q = LET·ρ·L·e/3.6 eV ≈ 104 fC
(regla: LET 97 ≈ 1 pC/µm; CREME, Vanderbilt). Carga crítica de una celda SRAM moderna: ~1 fC (65 nm: 1.0–1.5 fC en publicaciones)
→ «unas 100 veces» es orden de magnitud: no toda la carga se recoge en el nodo sensible y depende de la geometría.

## 2 · ReelELVoto — «Tres computadoras que votan»
**Pie:** Tres copias hacen la misma cuenta y una cuarta pieza compara. Si una se equivoca, gana la mayoría. Para fallar, tendrían que equivocarse dos al mismo tiempo: unas 300 veces menos probable.
**Hashtags:** #Electrónica #TolerantesAFallos #Satélites #Ingeniería #CoDeAerospace
⚠️ Triple redundancia modular (TMR). Con p = 1/1000 por copia e independientes: P(voto falla) = 3p² − 2p³ ≈ 3×10⁻⁶ → ~333 veces
menos. Supone fallas independientes y un votante perfecto (el votante también puede fallar; las fallas de causa común no se reducen).

## 3 · ReelELHamming — «Un código que encuentra el error»
**Pie:** A 4 bits de dato se les suman 3 de control. Si un bit cambia en el camino, las revisiones que fallan dicen exactamente cuál fue… y se corrige solo. Así se protege la memoria de muchos satélites (y la de muchos servidores).
**Hashtags:** #Hamming #CorrecciónDeErrores #Electrónica #Satélites #CoDeAerospace
⚠️ Código de Hamming (7,4): corrige 1 bit por palabra y no 2 a la vez. Dato 1011 → palabra 0110011; se voltea el bit 6; las
revisiones 2 y 3 (paridades de las posiciones 2 y 4) fallan → 2 + 4 = 6. Las memorias reales usan variantes (SECDED) con barrido
periódico («scrubbing») para que no se junten dos errores.

## 4 · ReelELDosis — «La radiación que se acumula»
**Pie:** Cada partícula deja un poco de daño y se suma año tras año. Un chip común aguanta unas 10 veces la dosis que mataría a una persona; uno endurecido, cientos de veces más. Se diseñan, se prueban y se blindan para eso.
**Hashtags:** #Radiación #Electrónica #Satélites #Espacio #CoDeAerospace
⚠️ Órdenes de magnitud, escala logarítmica. Persona: ~5 Gy de cuerpo entero ≈ 0.5 krad (dosis letal media aproximada). Chips
comerciales: muchos ~5 krad(Si), algunos fallan antes de 1 krad. Endurecidos: 100 krad a 1 Mrad (se dibuja 300 krad). Comparar Gy
de tejido con rad(Si) es una simplificación. En órbita baja, detrás de ~1–2.5 mm de aluminio, del orden de 1 krad/año (NASA NEPP,
ejemplo a 780 km); varía mucho con la altura, la inclinación y el ciclo solar.

## 5 · ReelELLatch — «El cortocircuito que se dispara solo»
**Pie:** Una partícula puede abrir dentro del chip un camino de corriente que no se apaga solo (latch-up). Si nadie lo corta, el chip se quema. Por eso un limitador vigila la corriente: si pasa del límite, apaga y vuelve a encender.
**Hashtags:** #Electrónica #Radiación #Satélites #Ingeniería #CoDeAerospace
⚠️ Ilustración cualitativa del «single event latch-up» (SEL): un tiristor parásito de CMOS se dispara; la corriente queda alta
hasta quitar la alimentación. La gráfica no tiene escala real (la detección y el corte toman de microsegundos a milisegundos según el
diseño). Hay chips inmunes por proceso (p. ej., SOI); el limitador no evita daños si actúa tarde.

## 6 · ReelELPanel — «Menos energía que un cargador de celular»
**Pie:** Una cara de un cubesat de 10 cm lleva celdas solares que convierten ~28 % de la luz del Sol en electricidad: unos 2 watts. Menos que un cargador de celular… y con eso vive la radio, la computadora y los sensores.
**Hashtags:** #CubeSat #EnergíaSolar #Satélites #Electrónica #CoDeAerospace
⚠️ Cálculo ilustrativo: 2 celdas de triple unión de 26.5 cm² al 28 % (hoja de datos CESI CTJ, ~1 W por celda) × 1361 W/m² de
frente al Sol = 2.0 W. Al inicio de vida y a 25 °C; en órbita el promedio es menor (ángulo, temperatura, eclipse, degradación).
Cargador básico de celular: 5 W (los rápidos dan 20 W o más).

## 7 · ReelELBateria — «15 noches cada día»
**Pie:** A 550 km, un satélite da una vuelta a la Tierra en hora y media: unas 15 al día. Cada vuelta tiene su noche, de hasta 36 minutos, y entonces todo funciona con batería. Son unos 5 500 ciclos al año: 15 veces los de tu celular.
**Hashtags:** #Baterías #Satélites #Electrónica #Órbita #CoDeAerospace
⚠️ Órbita circular a 550 km: periodo 95.5 min (Kepler), 15.1 vueltas/día, ~5 500 ciclos/año. Noche máxima 35.6 min con el Sol en el
plano de la órbita (β = 0, sombra cilíndrica); con otros ángulos es menor o no hay eclipse. Celular: supuesto de ~1 ciclo al día.
Dibujo sin escala (la órbita real está mucho más pegada a la Tierra); la batería dibujada es ilustrativa.

## 8 · ReelELCalor — «Sin aire, el calor no tiene a dónde ir»
**Pie:** En la Tierra, el aire se lleva el calor de los chips. En el vacío no hay aire: el calor solo sale como luz infrarroja. Al Sol, una placa oscura llega a unos 120 °C; para tirar 1 watt a 20 °C hace falta un radiador de unos 5 × 5 cm.
**Hashtags:** #Termodinámica #Satélites #Electrónica #Espacio #CoDeAerospace
⚠️ Cálculos ideales. Placa con absortancia = emisividad, de frente al Sol y trasera aislada: T = (S/σ)^¼ = 393 K ≈ 120 °C. Radiador
con ε = 0.9 hacia el espacio frío, sin Sol ni Tierra: A = P/(εσT⁴) ≈ 27 cm² por watt a 20 °C. Los satélites reales usan pinturas y
recubrimientos (α/ε), conducción a la estructura y calefactores; «se enfría muchísimo» depende de la masa térmica.

## 9 · ReelELBajada — «Bajar una foto toma varios pases»
**Pie:** Un cubesat solo puede hablar con la antena mientras pasa por encima, unos 10 minutos. A 9 600 bits por segundo, una foto de 3 MB tarda 42 minutos: necesita unos 4 pases. Por eso a bordo se elige qué vale la pena bajar.
**Hashtags:** #CubeSat #Radio #Telecomunicaciones #Satélites #CoDeAerospace
⚠️ Cálculo ilustrativo: 3 MB × 8 / 9 600 bit/s = 2 500 s ≈ 42 min, sin cabeceras, reintentos ni pérdidas (en la práctica tarda más).
9 600 bit/s es típico de enlaces UHF de aficionado (AX.25); otros satélites bajan Mbit/s en banda S o X. Duración de pase ~10 min
(órbita baja, pase alto); los pases bajos duran menos. Foto procedural, no es una imagen real.

## 10 · ReelELLento — «Computadoras lentas a propósito»
**Pie:** Los rovers Curiosity y Perseverance piensan con un RAD750 de hasta 200 MHz; tu celular va unas 15 veces más rápido por núcleo. Pero el RAD750 aguanta la radiación y tiene años de pruebas. El helicóptero Ingenuity, en cambio, voló 72 veces con un chip de celular.
**Hashtags:** #Marte #Perseverance #Ingenuity #Electrónica #CoDeAerospace
⚠️ Datos públicos: RAD750 (BAE Systems, arquitectura PowerPC 750) a hasta 200 MHz en Curiosity y Perseverance (NASA). Celular:
~3 GHz por núcleo (orden de magnitud) → «unas 15 veces» compara frecuencia de reloj, NO rendimiento (el celular tiene además varios
núcleos y arquitectura más moderna). Ingenuity: Qualcomm Snapdragon 801 (procesador de celulares de 2014), 72 vuelos (2021–2024).
Ondas cuadradas ilustrativas, sin escala.
