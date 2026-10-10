# Serie «Caos y gravedad» — reels de divulgación (2026-10-09)

Diez reels de unos 26 s, solo texto y sonido sintético (sin voz), en formato película (título → cuerpo → logo de Co.De → loop).
Tema Caos con fondo vertical propio (el diagrama de bifurcación del mapa logístico como horizonte). Escena `46-reels-caos.py`, datos
`datos_co.py`. **Casi todo es simulación real** (`caos_gravedad.py`, integrador DOP853 con tolerancias estrictas y pruebas de
conservación; resultados congelados por `studio/tools/caos_congelar.py` en `studio/content/datos_caos/`) o dato real (catálogo de
asteroides de la NASA/JPL, consulta del 2026-10-09). Varios sonidos también salen de la simulación (encuentros cercanos, batido que
crece con la separación, giro de Hiperión). Sin mediciones propias, sin tesis ni clientes.

---

## 1 · ReelCOOcho — «Tres cuerpos, ninguna fórmula»
**Pie:** Con dos cuerpos, la gravedad es predecible. Con tres, casi nunca se repite: la «figura ocho» es una rara excepción. Tres masas quietas de 3, 4 y 5 (el problema pitagórico, de 1913) bailan sin patrón hasta que una sale disparada. No hay fórmula: solo se puede simular.
**Hashtags:** #ProblemaDeTresCuerpos #Caos #Gravedad #Física #CoDeAerospace
⚠️ Simulación de N cuerpos (G = 1). Figura ocho: condiciones de C. Moore (1993), demostrada por Chenciner y Montgomery (2000); es
estable ante perturbaciones pequeñas. Problema pitagórico (Burrau, 1913; resuelto numéricamente por Szebehely y Peters, 1967): masas
3, 4, 5 en los vértices de un triángulo 3-4-5, en reposo. Se usó un suavizado de 0.001 en la fuerza para atravesar encuentros muy
cercanos; el desenlace exacto (qué cuerpo sale y hacia dónde) depende de ese detalle y de la precisión, que es justamente el punto.
«Sin fórmula»: no hay solución general en términos de funciones simples (Sundman encontró una serie en 1912, inútil en la práctica).

## 2 · ReelCOMariposa — «Una millonésima cambia el final»
**Pie:** Dos copias del mismo baile de tres cuerpos; una empieza movida una millonésima. Durante un rato son idénticas… luego la diferencia se multiplica sin parar y terminan con destinos distintos. Es el efecto mariposa de la gravedad.
**Hashtags:** #EfectoMariposa #Caos #Gravedad #Simulación #CoDeAerospace
⚠️ Mismo problema pitagórico, dos simulaciones; la copia B empieza con el cuerpo de masa 3 movido 10⁻⁶ (unidades de la simulación).
La gráfica es la separación máxima entre cuerpos correspondientes, en escala logarítmica. El integrador también comete errores de
redondeo (~10⁻¹¹ por paso); la diferencia inicial es 100 000 veces mayor que esa tolerancia.

## 3 · ReelCOLagrange — «Cinco lugares para quedarse quieto»
**Pie:** En el marco que gira con la Tierra alrededor del Sol hay cinco puntos donde las fuerzas se equilibran. El telescopio Webb vive cerca de L2, a 1.5 millones de km: unas 4 veces la distancia a la Luna. Y en L4 y L5 de Júpiter se juntan más de 16 000 asteroides troyanos.
**Hashtags:** #PuntosDeLagrange #TelescopioWebb #Troyanos #Astronomía #CoDeAerospace
⚠️ Curvas de nivel del potencial efectivo del problema restringido de tres cuerpos con la masa del planeta EXAGERADA (μ = 0.02) para
que se vean; con el Sol y la Tierra reales (μ = 3×10⁻⁶) L1 y L2 están pegados a la Tierra a esta escala. L2 Sol–Tierra calculado:
1.50 millones de km (Webb orbita en un halo alrededor de L2, no en el punto). Troyanos: 16 406 objetos de la clase TJN en la base
de datos de cuerpos menores de la NASA/JPL, consulta del 2026-10-09 (el número crece con los descubrimientos). Las órbitas de
renacuajo alrededor de L4/L5 están simuladas con μ = 0.02.

## 4 · ReelCOHerradura — «Dos lunas que cambian de lugar»
**Pie:** Jano y Epimeteo, lunas de Saturno, comparten casi la misma órbita: se separan apenas 50 km. Cuando una alcanza a la otra, se jalan y cambian de órbita sin tocarse. Se turnan cada 4 años; simulado con sus masas reales, sale lo mismo.
**Hashtags:** #Saturno #Lunas #Gravedad #Simulación #CoDeAerospace
⚠️ Simulación de tres cuerpos (Saturno, Jano 1.90×10¹⁸ kg, Epimeteo 5.27×10¹⁷ kg) en el plano, órbitas iniciales circulares
separadas 50 km a 151 460 km, 9 años. Resultado: cambios a los 3.3 y 7.3 años (cada 3.99 años); acercamiento mínimo ~14 000 km en la
simulación (las fuentes citan ~10 000 km). Intercambios reales observados en enero de 2006, 2010, 2014, 2018 y 2022; el de 2026
tocaba este año. Marco que gira con Jano; la diferencia de radios está exagerada unas 400 veces para que se vea la «herradura».
Jano también se mueve (4 veces menos, por ser 4 veces más masiva); aquí solo se dibuja la posición relativa.

## 5 · ReelCOHiperion — «La luna que da tumbos»
**Pie:** La Luna siempre nos da la misma cara: gira al mismo ritmo que da la vuelta. Hiperión, luna de Saturno, es alargada y su órbita es ovalada: en la simulación su giro cambia sin parar. Así lo predijo un modelo en 1984; un estudio de 2024 lo discute. La ciencia sigue.
**Hashtags:** #Hiperión #Saturno #Caos #Ciencia #CoDeAerospace
⚠️ Modelo de Wisdom, Peale y Mignard (1984): θ'' = −(ω₀²/2r³)·sen 2(θ − f) con ω₀ = 0.89 y e = 0.1 (Hiperión) y, para comparar, una
luna poco alargada en órbita casi circular (ω₀ = 0.2, e = 0.055). En 40 órbitas el ritmo de giro de Hiperión va de 0.23 a 1.58 veces
el de su órbita. Observaciones (Voyager, Cassini) apoyan un giro irregular; un preprint de 2024 propone que no es caótico sino casi
regular (resonancia de nutación), aún en discusión. El dibujo pone el giro sobre una órbita en cámara lenta (orientación respecto
del planeta).

## 6 · ReelCOKirkwood — «Huecos en el cinturón de asteroides»
**Pie:** Entre Marte y Júpiter hay casi 1.5 millones de asteroides con órbita conocida. Si los cuentas por distancia al Sol aparecen huecos justo donde darían 3 vueltas por cada 1 de Júpiter (y 5:2, 7:3, 2:1): Júpiter los jala siempre en el mismo punto y con el tiempo los saca. Son los huecos de Kirkwood.
**Hashtags:** #Asteroides #Júpiter #HuecosDeKirkwood #NASA #CoDeAerospace
⚠️ DATOS REALES: semiejes mayores de 1 473 671 asteroides de las clases IMB, MBA y OMB de la NASA/JPL Small-Body Database (consulta del
2026-10-09), histograma de 0.01 UA. Resonancias calculadas con la tercera ley de Kepler (a = 5.2026·(q/p)^(2/3) UA): 3:1 → 2.50, 5:2 →
2.82, 7:3 → 2.96, 2:1 → 3.28 UA. La vista del cinturón sortea 1 800 puntos con esa distribución (posiciones ilustrativas, vista
inclinada, sin inclinaciones ni excentricidades). La 2:1 marca el borde exterior del cinturón principal.

## 7 · ReelCOHonda — «Robarle velocidad a Júpiter»
**Pie:** Vista desde Júpiter, una nave entra y sale igual de rápido: la gravedad solo le cambia la dirección. Pero vista desde el Sol sale más rápido: le «roba» un poco de velocidad a Júpiter. Así saltó la Voyager 2 de planeta en planeta.
**Hashtags:** #AsistenciaGravitatoria #Voyager #Júpiter #Física #CoDeAerospace
⚠️ Cálculo ilustrativo: hipérbola con v∞ = 10 km/s y periapsis a 5 radios de Júpiter → giro de 102.5°; velocidad orbital de Júpiter
13.07 km/s; con la salida alineada con el movimiento de Júpiter: llega a 14.6 km/s y sale a 23.1 km/s (+8.4 km/s respecto del Sol).
Júpiter pierde una cantidad de velocidad imperceptible (por su enorme masa). Voyager 2 (lanzada en 1977) pasó por Júpiter (1979),
Saturno (1981), Urano (1986) y Neptuno (1989); la alineación que lo permitió se repite cada ~175 años. El esquema de su ruta es
ilustrativo (distancias en raíz cuadrada).

## 8 · ReelCOKessler — «Choques que fabrican choques»
**Pie:** En 2009 chocaron los satélites Iridium 33 y Cosmos 2251: más de 2 000 fragmentos catalogados. En 2007, una prueba antisatélite destruyó el Fengyun-1C: más de 3 000. Cada fragmento puede romper a otro satélite y cada choque fabrica más. Pasado un umbral, la cascada sigue sola: es el síndrome de Kessler.
**Hashtags:** #BasuraEspacial #SíndromeDeKessler #Satélites #Espacio #CoDeAerospace
⚠️ Fragmentos catalogados (fuentes públicas: CelesTrak, NASA ODQN, catálogo de EE. UU.): Iridium 33 + Cosmos 2251 ≈ 2 300; Fengyun-1C
≈ 3 400–3 500 (muchos ya reingresaron). La animación de choques en cadena es ilustrativa. La gráfica es un MODELO DE JUGUETE
adimensional N' = −N/τ + k·N² (τ = 10, k = 0.001 → umbral N* = 100): por debajo del umbral los objetos se limpian solos, por encima
crecen sin freno. Kessler y Cour-Palais (1978) propusieron el efecto; dónde está el umbral real es tema de estudio.

## 9 · ReelCOPrediccion — «¿Hasta cuándo se puede predecir?»
**Pie:** El clima se predice unas dos semanas: los errores pequeños se duplican en pocos días. Los planetas, millones de años… pero su error también crece. Un error de 15 metros hoy se duplica cada 3.5 millones de años: en unos 100 millones de años ya no se sabe en qué parte de su órbita estará la Tierra.
**Hashtags:** #Caos #SistemaSolar #Predicción #Ciencia #CoDeAerospace
⚠️ Tiempo de Lyapunov del sistema solar interior ≈ 5 millones de años (Laskar, 1989; Mogavero, Hoang y Laskar, 2023) → se duplica
cada 5·ln 2 ≈ 3.5 millones de años. Ejemplo de Laskar: un error de 15 m crece a ~150 millones de km en ~100 millones de años (aquí,
con e^(t/5 Ma), sale ~115). Que sea caótico no quiere decir inestable: las órbitas siguen ahí miles de millones de años; lo que se
pierde es saber la posición exacta. «Dos semanas» del clima: límite práctico de predicción del tiempo, orden de magnitud. Los
puntos azules son una ilustración de esa incertidumbre.

## 10 · ReelCOAtajo — «El camino largo gasta menos»
**Pie:** Apolo llegó a la Luna en 3 días, en camino directo y con mucho combustible. GRAIL tardó tres meses y medio: se alejó 1.5 millones de km y dejó que el Sol y la Tierra la regresaran. Más lento, pero más barato: unos 130 m/s menos de combustible. CAPSTONE usó la misma idea en 2022.
**Hashtags:** #Luna #NASA #Órbitas #Ingeniería #CoDeAerospace
⚠️ GRAIL (NASA, 2011): transferencia de baja energía de ~3.5 meses vía el punto L1 Sol–Tierra, ~4 millones de km recorridos, ahorro
de ~130 m/s frente a una ruta directa (NASA/JPL). CAPSTONE (2022): transferencia balística lunar de ~4 meses, hasta ~1.5 millones de
km. Apolo: ~3 días. El trazo de la ruta es una ILUSTRACIÓN (no una trayectoria calculada); estas rutas aprovechan la dinámica de tres
y cuatro cuerpos (Tierra, Luna, Sol) cerca de regiones caóticas.
