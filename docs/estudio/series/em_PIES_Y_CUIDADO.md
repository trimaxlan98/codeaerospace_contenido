# Serie «Electromagnetismo en el espacio» — reels de divulgación (2026-10-09)

Diez reels de unos 26 s, solo texto y sonido sintético (sin voz), en formato película (título → cuerpo → logo de Co.De → loop).
Tema Electromagnetismo con fondo vertical propio (limbo de la Tierra, aurora y líneas de campo). Escena `43-reels-em.py`, datos
`datos_em.py` (cada cifra sale de una función de `electromagnetismo.py`, la física del curso, con sus pruebas). **No hay mediciones
propias**: son cálculos de libro con supuestos declarados abajo. Sin tesis ni clientes.

---

## 1 · ReelEMEscudo — «La Tierra es un imán gigante»
**Pie:** La Tierra se comporta como un imán enorme. Su campo desvía el viento solar y forma una burbuja que protege a los satélites y a la atmósfera. Es unas 150 veces más débil que un imán de refri… pero mide decenas de miles de kilómetros.
**Hashtags:** #CampoMagnético #ClimaEspacial #Física #Divulgación #CoDeAerospace
⚠️ Dipolo ideal: 31.2 µT en el ecuador (en los polos ~el doble; el campo real no es un dipolo perfecto y su eje está inclinado ~10°).
Imán de refrigerador: supuesto de ~5 mT (los hay de 1 a 10 mT) → «unas 150 veces» es orden de magnitud. El flujo del viento solar
es ilustrativo (flujo ideal alrededor de un obstáculo), no la forma real de la magnetopausa, que se comprime del lado del Sol y se
estira en una cola del lado nocturno. El origen del campo (geodinamo: hierro líquido en movimiento en el núcleo externo) está simplificado.

## 2 · ReelEMEspiral — «Atrapadas en espiral»
**Pie:** Una partícula con carga no puede cruzar un campo magnético: lo rodea en espiral. Donde el campo se aprieta, rebota. Así se forman los cinturones de Van Allen alrededor de la Tierra.
**Hashtags:** #VanAllen #Plasma #Física #Espacio #CoDeAerospace
⚠️ Cámara lenta. «≈ 840 000 vueltas por segundo»: girofrecuencia de un electrón en 30 µT (f = qB/2πm, no depende de la energía).
Los cinturones reales: interior ~600–10 000 km (sobre todo protones), exterior ~13 000–58 000 km (sobre todo electrones; cifras de divulgación de la NASA); la forma
dibujada (L = 1.5–2.3 y 3.2–5) es aproximada y varía con la actividad solar. El rebote (espejo magnético) está simplificado.

## 3 · ReelEMAurora — «¿De dónde sale la aurora?»
**Pie:** Partículas del Sol siguen las líneas del campo hasta los polos y chocan con el aire a 100–300 km de altura. Cada choque enciende un átomo: el oxígeno brilla verde y rojo; el nitrógeno, azul y violeta.
**Hashtags:** #Aurora #AuroraBoreal #ClimaEspacial #Física #CoDeAerospace
⚠️ Ilustración. Oxígeno atómico: verde 557.7 nm (~100–250 km) y rojo 630 nm (más arriba, >200 km); nitrógeno: azul/violeta en el
borde inferior. Las partículas que causan la aurora vienen sobre todo de la cola de la magnetosfera, no directo del Sol (simplificado).

## 4 · ReelEMTorque — «Girar un satélite sin combustible»
**Pie:** Una bobina con corriente se vuelve imán y, como una brújula, busca alinearse con el campo de la Tierra. Así se orientan muchos satélites pequeños: solo con electricidad de sus paneles.
**Hashtags:** #CubeSat #Satélites #Magnetorquer #Ingeniería #CoDeAerospace
⚠️ Cálculo ilustrativo: cubo de 10 cm (1U) con inercia 0.002 kg·m², momento 0.2 A·m², campo de dipolo a 550 km (24 µT): 90° desde el
reposo en ~36 s (cota optimista: par máximo constante, sin frenar al final). En geoestacionaria (0.11 µT) ~9 min, unas 15 veces más.
El movimiento dibujado (oscilación amortiguada) es cualitativo. Un magnetorquer solo genera par perpendicular al campo.

## 5 · ReelEMLuz — «La luz estaba escondida en un imán»
**Pie:** Dos constantes medidas en una mesa —una con imanes, otra con cargas— se combinan en 1/√(μ₀ε₀). Maxwell vio que daba la velocidad de la luz: la luz es electricidad y magnetismo viajando juntos.
**Hashtags:** #Maxwell #Luz #HistoriaDeLaCiencia #Física #CoDeAerospace
⚠️ 1/√(μ₀ε₀) = 299 792 km/s (hoy c está fijada por definición y μ₀, ε₀ se derivan de ella; en 1860 eran medidas de laboratorio, de
Weber y Kohlrausch, 1856). «7 vueltas y media a la Tierra en un segundo»: c / perímetro ecuatorial (40 030 km) = 7.49. Animación en cámara lenta.

## 6 · ReelEMBandas — «Mismo fenómeno, otro tamaño»
**Pie:** Radio, microondas y luz son lo mismo: ondas electromagnéticas de distinto tamaño. Los satélites eligen el suyo: UHF como un brazo, banda S como un lápiz, X como un dedo, Ka como una uña.
**Hashtags:** #Radio #Satélites #Microondas #Física #CoDeAerospace
⚠️ λ = c/f con frecuencias de ejemplo: UHF 437 MHz (69 cm, cubesats de aficionado), S 2.2 GHz (14 cm), X 8.4 GHz (3.6 cm, enlaces de
sondas de espacio profundo), Ka 30 GHz (1 cm). Las comparaciones con objetos son aproximadas. Luz visible ~0.55 µm; cabello humano
~50–100 µm → «unas 100 veces» (orden de magnitud). «La lluvia la frena más»: atenuación por lluvia crece con la frecuencia.

## 7 · ReelEMAntena — «¿Cómo una antena lanza ondas?»
**Pie:** Cargas que suben y bajan millones de veces por segundo sueltan ondas que se alejan. Una antena simple emite hacia los lados y casi nada por las puntas. Para un cubesat en 437 MHz, mide unos 34 cm.
**Hashtags:** #Antenas #Radio #CubeSat #Física #CoDeAerospace
⚠️ Cámara lenta. Patrón del dipolo elemental (|sen θ|), dibujado en un plano. Dipolo de media onda a 437 MHz: λ/2 = 34.3 cm (en la
práctica se recorta ~5 %). Muchos cubesats usan antenas de cinta desplegables; el tamaño exacto depende del diseño.

## 8 · ReelEMIonosfera — «Un espejo en el cielo»
**Pie:** Arriba, la luz del Sol arranca electrones al aire: la ionosfera. La radio de onda corta rebota en ella y da la vuelta al mundo; las frecuencias altas la cruzan. Por eso los satélites usan frecuencias altas.
**Hashtags:** #Ionosfera #RadioAficionados #OndaCorta #Satélites #CoDeAerospace
⚠️ Ilustración. Frecuencia de plasma con Ne = 10¹² m⁻³ (pico diurno de la capa F, orden de magnitud): ~9 MHz. El límite real depende
de la hora, la estación, el ciclo solar y el ángulo (con incidencia oblicua rebotan frecuencias de hasta ~3× más). Los satélites usan
VHF y más arriba también por el tamaño de antena y el ancho de banda, no solo por la ionosfera.

## 9 · ReelEMCable — «Un cable que genera electricidad en órbita»
**Pie:** Un cable largo que cruza el campo de la Tierra a 7.6 km por segundo funciona como un generador: aparecen unos 185 voltios por kilómetro. Esa corriente también lo frena, una idea para bajar satélites viejos sin combustible.
**Hashtags:** #BasuraEspacial #Física #Inducción #Espacio #CoDeAerospace
⚠️ Cálculo ilustrativo: fem = v·B·L con v = 7.59 km/s y B = 24 µT (dipolo a 550 km), cable perpendicular a ambos (cota superior; con
la geometría real es menor). Las amarras electrodinámicas se han probado en vuelo (p. ej. TSS-1R, 1996; misiones pequeñas
posteriores) y se estudian para desorbitar; no es una tecnología de uso común. Cerrar el circuito requiere intercambiar carga con
el plasma (simplificado).

## 10 · ReelEMSenal — «La señal llega casi apagada»
**Pie:** La señal se reparte en una esfera que crece: al doble de distancia, cuatro veces más débil. Un watt emitido a 1000 km llega como unas 3 milbillonésimas de watt. Por eso las antenas concentran la señal y los receptores escuchan casi en silencio.
**Hashtags:** #Telecomunicaciones #Satélites #Antenas #Física #CoDeAerospace
⚠️ Cálculo ilustrativo: pérdida de espacio libre a 437 MHz y 1000 km = 145 dB → 3×10⁻¹⁵ W con antenas ISÓTROPAS (sin ganancia) y sin
pérdidas atmosféricas. Con antenas directivas llega bastante más. Los cuadros de la animación ilustran el cuadrado inverso (1, 4, 9).
