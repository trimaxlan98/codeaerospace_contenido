# Serie «Cálculo en el espacio» — reels de divulgación (2026-10-09)

Diez reels de unos 26 s, solo texto y sonido sintético (sin voz), en formato película (título → cuerpo → logo de Co.De → loop).
Tema Cálculo con fondo vertical propio (la gráfica de una función como horizonte, con rectángulos de Riemann, curvas de nivel y una
tangente). Escena `45-reels-calculo.py`, datos `datos_ca.py` (cuentas de `calculo_espacio.py`, con pruebas: `python3 calculo_espacio.py`).
Una idea del cálculo por reel. **No hay mediciones propias**: cálculos de libro y datos públicos, con supuestos abajo. Sin tesis ni clientes.

---

## 1 · ReelCADerivada — «La derivada: qué tan rápido cambia»
**Pie:** La derivada es la pendiente: de la gráfica de distancia sale la velocidad. La sombra de la Estación Espacial cruza México, de Tijuana a Cancún, en unos 7 minutos y medio: su pendiente es 260 veces la de un auto en carretera.
**Hashtags:** #Cálculo #Derivada #EstaciónEspacial #Matemáticas #CoDeAerospace
⚠️ ISS a 420 km (varía ~410–430 km), órbita circular: 7.66 km/s; su punto bajo ella avanza 7.19 km/s sobre el suelo (≈ 25 900 km/h;
sin contar la rotación de la Tierra). Tijuana–Cancún en línea recta: 3 235 km (haversine) → 7.5 min; la traza real casi nunca va de
una a otra en línea recta. El auto de la primera gráfica es ilustrativo (80 km en una hora, con velocidad variable).

## 2 · ReelCAIntegral — «La integral: sumar rebanadas»
**Pie:** El área bajo la gráfica de velocidad es la distancia recorrida, y se calcula sumando rebanadas cada vez más finas. En un minuto, la Estación Espacial avanza unos 460 km —como de la CDMX a Guadalajara—; un auto a 100 km/h, 1.7 km.
**Hashtags:** #Cálculo #Integral #EstaciónEspacial #Matemáticas #CoDeAerospace
⚠️ 7.66 km/s × 60 s = 460 km (velocidad orbital a 420 km). CDMX–Guadalajara en línea recta: 462 km (por carretera son ~540 km). La
curva de velocidad de arriba es ilustrativa; las rebanadas son sumas de Riemann con 4, 8, 16 y 48 rectángulos.

## 3 · ReelCAMaximo — «Saltar en la Luna»
**Pie:** En lo más alto de un salto la velocidad vale cero: la derivada se anula y ahí está el máximo. El mismo impulso que en la Tierra te sube medio metro, en la Luna te sube 3 metros y te deja casi 4 segundos en el aire.
**Hashtags:** #Cálculo #Luna #Gravedad #Matemáticas #CoDeAerospace
⚠️ Mismo impulso (v₀ = 3.1 m/s) y h = v₀²/2g: 0.5 m con 9.81 m/s², 3.0 m con 1.62 m/s²; tiempo en el aire 2v₀/g: 0.64 s y 3.9 s. Sin
traje espacial: con el traje (masa, rigidez) los astronautas saltaban mucho menos. Las curvas se dibujan en tiempo real.

## 4 · ReelCAPasos — «Una órbita a pasitos»
**Pie:** Una computadora no resuelve la órbita de un jalón: avanza a pasitos, siguiendo la flecha un momento y recalculando. Con pasos grandes el error crece y el satélite «se escapa»; con 10 veces más pasos, el error es 10 veces menor.
**Hashtags:** #Cálculo #MétodosNuméricos #Órbitas #Programación #CoDeAerospace
⚠️ Método de Euler explícito (de primer orden) en una órbita circular, una vuelta: 20 pasos → termina a 3.6 veces el radio; 2 000 →
error de 3.9 %; 20 000 → 0.39 %. Los simuladores reales usan métodos de orden alto (Runge-Kutta, simplécticos) con muchísimo menos
error por paso. La «fuga» con pasos grandes es un error numérico, no física.

## 5 · ReelCAGiro — «Gravedad de carrusel»
**Pie:** Girar es cambiar de dirección todo el tiempo, y esa derivada es una aceleración hacia el centro. Un anillo de 100 m de radio que da 3 vueltas por minuto haría sentir en los pies el peso de la Tierra. Más chico, tendría que girar más rápido… y marearía.
**Hashtags:** #Cálculo #GravedadArtificial #EstacionesEspaciales #Física #CoDeAerospace
⚠️ a = ω²r: 1 g a 100 m → 2.99 rpm (una vuelta cada 20 s; se dibuja en tiempo real); a 10 m → 9.5 rpm. Que «marea» arriba de unas pocas
rpm es un límite aproximado de estudios en tierra (se citan 2–4 rpm, con adaptación). Ninguna estación con gravedad artificial ha
volado; es un concepto.

## 6 · ReelCATasas — «Marte cada 26 meses»
**Pie:** La Tierra da una vuelta al Sol en 12 meses y Marte en casi 23. Como sus velocidades de giro se restan, la Tierra «alcanza» a Marte cada 26 meses. Por eso las misiones a Marte salen en ventanas, cada 26 meses.
**Hashtags:** #Marte #Cálculo #Órbitas #Astronomía #CoDeAerospace
⚠️ Periodo sinódico 1/S = 1/T_T − 1/T_M = 780 días ≈ 25.6 meses. Órbitas circulares y coplanares (las reales son elípticas: cada ventana
es distinta). La ventana de lanzamiento NO es el momento de la alineación: para una transferencia de Hohmann se sale con Marte unos
44° adelante; pero esa configuración también se repite cada ~26 meses. Dibujo sin escala; 1 año = 3.6 s.

## 7 · ReelCAPlutonio — «La mitad cada 88 años»
**Pie:** El plutonio-238 pierde la mitad de su calor cada 88 años: siempre la misma fracción, eso es una exponencial. Las Voyager llevan 49 años viajando y su plutonio aún da 68 % del calor… pero su electricidad ya cayó a la mitad, porque las piezas que convierten el calor también se gastan.
**Hashtags:** #Voyager #Cálculo #Exponencial #NASA #CoDeAerospace
⚠️ Vida media del Pu-238: 87.7 años; 2^(−49/87.7) = 0.68. Electricidad de cada Voyager: ~470 W al lanzar (1977) y ~230 W en 2026 (cifras
públicas aproximadas; caen ~4 W por año). La diferencia se debe a la degradación de los termopares del RTG.

## 8 · ReelCAAire — «Cada 5.5 km, la mitad del aire»
**Pie:** La mitad del aire está por debajo de 5.5 km. Subes otros 5.5 km y vuelve a quedar la mitad: es una exponencial. En la cima del Everest respiras un tercio del aire, los aviones vuelan con un cuarto, y a 100 km —donde se dice que empieza el espacio— queda menos de una millonésima.
**Hashtags:** #Atmósfera #Cálculo #Exponencial #Espacio #CoDeAerospace
⚠️ Modelo de mitades cada 5.5 km (la mitad de la masa del aire está debajo de ~5.5–5.6 km): Everest 2^(−8.85/5.5) ≈ 0.33 (tabla
estándar ≈ 0.31); avión a 10–11 km ≈ 1/4. A 100 km: ~0.032 Pa ≈ 3×10⁻⁷ atm (Atmósfera Estándar de EE. UU., 1976); arriba de ~80 km la
exponencial simple ya no vale (cambia la temperatura). La línea de Kármán (100 km) es una convención. Los puntos dibujados se
reparten al azar con esa ley.

## 9 · ReelCAHorizonte — «¿Hasta dónde se ve?»
**Pie:** En la playa, el horizonte está a unos 5 km: la Tierra se curva y esconde lo demás. Desde un avión, a unos 360 km; desde la Estación Espacial, a 2 350 km, como de Tijuana a la Ciudad de México. La distancia crece como una raíz: d ≈ √(2·R·h).
**Hashtags:** #Horizonte #Cálculo #EstaciónEspacial #Geometría #CoDeAerospace
⚠️ Tangente a una esfera de 6 371 km: d = √(2Rh + h²); con ojos a 2 m: 5.0 km; a 10 km: 357 km; a 420 km: 2 351 km. Sin refracción
(la atmósfera alarga un poco el horizonte). Tijuana–CDMX en línea recta: 2 300 km. Dibujo sin escala: las alturas están muy
exageradas para que se vean.

## 10 · ReelCATunel — «Un túnel que atraviesa la Tierra»
**Pie:** Si cavaras un túnel recto a través de la Tierra y te dejaras caer, irías cada vez más rápido hasta el centro y llegarías al otro lado en 42 minutos. Y lo curioso: es el mismo ritmo de un satélite que diera vueltas a ras del suelo.
**Hashtags:** #Cálculo #EcuacionesDiferenciales #Física #Tierra #CoDeAerospace
⚠️ Experimento mental: Tierra de densidad uniforme, sin aire, sin fricción ni rotación, túnel imposible de construir. Dentro, g crece
con la distancia al centro → x'' = −(g/R)x, oscilación armónica de periodo 2π√(R/g) = 84.3 min (la misma de una órbita circular a ras
del suelo); medio periodo = 42.2 min. Con la densidad real (núcleo denso) sale ~38 min. Cámara rápida: 84 min = 8 s.
