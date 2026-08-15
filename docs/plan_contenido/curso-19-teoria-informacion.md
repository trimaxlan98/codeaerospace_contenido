# Curso 21 · «Teoría de la información: los bits de Shannon» (archivo curso-19)

> **Numeración**: los archivos `curso-NN-*.md` van por orden de creación;
> la numeración REAL la lleva `PLAN.md`. Este es el **curso 21** (el 19 es
> Criptografía, el 20 la familia Metrología óptica).

## Tesis

La información **se mide**. Un bit es la sorpresa de una moneda justa; la
entropía de Shannon dice cuánto hay que decir para contar algo (y no
menos); un código bien hecho (Huffman) se acerca a ese mínimo; el idioma y
las imágenes están llenos de redundancia, y por eso un zip achica sin
perder y un jpg achica tirando lo que el ojo no ve. Del otro lado está el
canal con ruido: cada bit que se voltea borra información, pero Shannon
demostró en 1948 lo increíble — hasta un techo llamado **capacidad** se
puede transmitir SIN errores; y con ancho de banda y relación señal/ruido
ese techo tiene fórmula (Shannon–Hartley). Los códigos correctores
(Hamming) arreglan errores sin retransmitir, y los modernos (turbo, LDPC)
rozan el techo: cada bit que baja de un satélite hoy lo midió Shannon en
1948. Cierre: «La información no se adivina. / Se mide.»

Puentes: «Cerrar el enlace» (curso 13: C/N0, dB, MODCOD) y «Criptografía»
(curso 19: bits, XOR, la misma muestra de español).

## Los números (todos calculados por la librería, jamás a mano)

| Cantidad | Valor esperado | Fuente |
|---|---|---|
| Sorpresa de la moneda justa | **1 bit** | `sorpresa(0.5)` |
| Bits de un dado / una carta de 52 | **2.58** / **5.70** | `bits_para(6)`, `bits_para(52)` |
| Moneda trucada p=0.9: sorpresa de cara / de cruz | **0.15** / **3.32** bits | `sorpresa(0.9)`, `sorpresa(0.1)` |
| 20 preguntas sí/no distinguen | 2^20 = **1 048 576** objetos | `2 ** N_PREGUNTAS`, `preguntas_para(1_048_576)` = 20 |
| Entropía de la moneda trucada p=0.9 | **0.469** bits (vs 1 de la justa) | `entropia_binaria(0.9)` |
| Entropía del español MEDIDA (27 símbolos: letras + espacio; Quijote I cap. I, ~500 letras) | **3.96** bits/símbolo (MEDIDO; 714 símbolos, 580 letras) frente a log2 27 = **4.75** uniforme | `entropia_texto(TEXTO_ES)`, `bits_para(27)` |
| Símbolo más frecuente / letra más frecuente | espacio (18.8 %); letra **A** (12.2 %), la E segunda (MEDIDO) | `frecuencias(TEXTO_ES)` |
| Huffman de «ABRACADABRA» (A5 B2 R2 C1 D1) | H = **2.04** bits, longitud media **2.09**, **23** bits frente a **33** con 3 bits fijos | `huffman`, `longitud_media`, `bits_codificados` |
| Huffman del español (27 símbolos) | longitud media **3.99** MEDIDA frente a H = 3.96 y 5 bits fijos / 8 ASCII (2851 / 3570 / 5712 bits para el texto) | `longitud_media(huffman(FREC_ES), FREC_ES)` |
| Redundancia de orden 0 del español | 1 − H/log2 27 = **16.8 %** (MEDIDO) | `redundancia(H_ES, 27)` |
| Redundancia con contexto (Shannon 1951, inglés) | ~**75 %** (~1 bit/letra) — se rotula «cita» | `REDUNDANCIA_SHANNON_1951 = 0.75` |
| Icono binario 24×16 (planeta con anillo): crudo vs RLE | 384 bits vs **175** MEDIDO con `bits_rle` (25 tramos; 33 % de unos) | `icono_bits(24, 16)`, `bits_rle` |
| Imagen gris 24×16 de una esfera: 8 bits vs 2 bits por píxel | **3072** vs **768** bits (÷4) — se sigue viendo la esfera | `imagen_esfera`, `cuantizar(img, 4)`, `bits_imagen` |
| Canal BSC p=0.1: bits volteados en 64 (semilla 3) | **5** (MEDIDO) | `simular_bsc(bits, 0.1, 3)` |
| Capacidad del BSC p=0.1 / 0.01 / 0.5 | **0.531** / **0.919** / **0** bits por uso | `capacidad_bsc(p)` = 1 − h(p) |
| Shannon–Hartley, transpondedor 36 MHz, C/N = 10 dB / 20 dB | **124.5** / **239.7** Mb/s (10× la potencia, ×1.9 la capacidad) | `capacidad_shannon(36e6, db_a_lineal(10))` |
| Eficiencia espectral a 10 dB / 13 dB | **3.46** / **4.39** b/s/Hz (+3 dB ≈ +1 bit) | `eficiencia_espectral(db)` |
| Límite de Shannon (B → ∞) | Eb/N0 mín = 10·log10(ln 2) = **−1.59 dB** | `ebn0_minimo_db()` |
| Hamming(7,4): datos 1011 → palabra de 7; error en la posición 5 → síndrome **5** → corregido | 7 bits, síndrome = posición | `hamming_codificar`, `hamming_sindrome`, `hamming_corregir` |
| Tasas: repetición ×3 = **1/3**, Hamming(7,4) = **4/7 = 0.571** | | `TASA_REP3`, `TASA_HAMMING` |
| BER medida en el BSC p=0.05 (4000 bloques, semilla 11): sin código / repetición ×3 / Hamming(7,4) | **0.0506 / 0.0076 / 0.0204** (MEDIDOS) | `simular_codigos(0.05, 4000, 11)` |
| DVB-S2 (ETSI EN 302 307-1, tabla 13, «cita»): QPSK 1/2 η=0.99 @ 1.0 dB; 8PSK 3/4 2.23 @ 7.9; 16APSK 3/4 2.97 @ 10.2; 32APSK 9/10 4.45 @ 16.1 | distancia al techo de Shannon **1.1 – 2.9 dB** (CALCULADA) | `MODCODS_DVBS2`, `snr_para_eficiencia(eta)` |
| BER sin codificar (BPSK) a 0 / 4 / 8 dB de Eb/N0 | 0.079 / 0.0125 / 1.9e-4 | `ber_bpsk(db)` |

## Reglas de honestidad

- «Bit» se define como unidad de sorpresa/incertidumbre (−log2 p), no como
  «un 0 o un 1»; el clip 1 lo dice explícitamente.
- La entropía del español es la de ORDEN 0 (símbolos independientes) MEDIDA
  en un texto real de dominio público (Quijote, capítulo I) — se rotula
  «texto de muestra». La estimación con contexto (~1 bit/letra, Shannon
  1951, para el inglés) se rotula «cita».
- Huffman se construye de verdad (fusiones de los dos pesos menores; empate
  → orden alfabético, determinista) y la longitud media se MIDE. Se dice que
  Huffman es óptimo símbolo a símbolo y que H es la cota inferior.
- «zip» = sin pérdida (RLE aquí, como ejemplo del principio); «jpg» = con
  pérdida (cuantización aquí, como ejemplo del principio). No se pretende
  reproducir DEFLATE ni la DCT: se rotula «el principio».
- El BSC es un modelo; los volteos son sembrados y CONTADOS. La capacidad
  1 − h(p) es la del BSC con entrada uniforme (se dice «capacidad»).
- Shannon–Hartley usa C/N (no C/N0): B = 36 MHz es el ancho clásico de un
  transpondedor Ku; los 10 y 20 dB son ejemplos rotulados. Se explica que
  «capacidad» es un techo teórico, no lo que da un módem real.
- Hamming(7,4) corrige UN error por bloque; se dice. Las BER de los códigos
  se MIDEN por simulación sembrada, comparando a igual p del canal (no a
  igual energía por bit — se dice que la comparación justa es por Eb/N0 y
  se remite al clip 8).
- Los puntos DVB-S2 son valores publicados (Es/N0 ideal, tabla 13 de la
  norma) — «cita». La distancia al techo se CALCULA con la curva de
  Shannon; parte de esa distancia es de la constelación, no del código, y
  se dice que el LDPC solo está a <1 dB de su techo (cita).
- El límite −1.59 dB es el de Eb/N0 con B → ∞ (se dice).

## Paleta (regla semántica)

- `C_BIT` ámbar `#f59e0b` — el bit, la información, la sorpresa, lo que
  se mide.
- `C_FUENTE` cian `#22d3ee` — la fuente, los símbolos, las probabilidades,
  el mensaje.
- `C_CODIGO` verde `#34d399` — códigos, compresión, corrección, lo que
  funciona.
- `C_RUIDO` rojo `#f43f5e` — el ruido, los bits volteados, la pérdida,
  el error.
- `C_LIMITE` violeta `#a78bfa` — la entropía, la capacidad, el techo de
  Shannon.
- `C_EJE` gris azulado `#31414f` — mobiliario.

## Los 8 clips (28–45 s duros; pies ≥5 s; pie cambia ANTES del transform)

### 1 · Un bit es una sorpresa
Tres fuentes en fila: una moneda (2 caras), un dado (6), una baraja (52).
Cada una «habla» y su sorpresa sube en la `curva_sorpresa` (−log2 p): 1
bit, 2.58, 5.70. Definición: un bit es la sorpresa de una moneda justa;
lo improbable informa más. Moneda trucada p=0.9: cara casi no informa
(0.15), cruz sí (3.32). Y las 20 preguntas: un `arbol_preguntas` de
profundidad 4 que se parte a la mitad en cada «sí/no» y el tag «20
preguntas → 1 048 576 objetos». Cierre: información = incertidumbre que
se despeja, y se mide en bits. Final: la curva con los tres puntos y el
árbol pequeño con «2^20 = 1 048 576».

### 2 · La entropía: cuánto hay que decir
La sorpresa promedio de una fuente es su entropía H. Curva `h(p)` de la
moneda: máximo 1 bit en p=0.5, 0.469 en 0.9, 0 en 1 (una moneda que
siempre sale cara no dice nada). Fuente real: histograma de 27 símbolos
del texto de muestra (español, Quijote) MEDIDO; H_ES = 3.96 bits/símbolo
frente a los 4.75 de una fuente uniforme de 27: el idioma es predecible
y por eso «pesa» menos. Cierre: H es lo mínimo que hay que decir, en
promedio, por símbolo. Final: histograma con «H = 4.1 bits/símbolo» y la
línea de 4.75 uniforme arriba (la cifra es la medida: 3.96).

### 3 · Huffman: decir lo justo
Con «ABRACADABRA» (A5 B2 R2 C1 D1) se construye el árbol de Huffman en
vivo: se funden los dos pesos menores (C+D=2, luego B+CD... hasta la
raíz), las ramas llevan 0/1 y cada letra recibe su código: A=0, R=10,
B=110, C=1110, D=1111 (los que dé la librería). El mensaje se codifica
como tira de segmentos de colores: 23 bits frente a 33 con 3 bits fijos;
longitud media 2.09 frente a H = 2.04 — casi el mínimo. Salto al texto
de muestra: 27 símbolos, longitud media 3.99 vs H 3.96 vs 5 fijos vs 8
ASCII (todo medido). Cierre: un buen código gasta casi exactamente la
entropía, nunca menos. Final: árbol con códigos y la comparación de bits.

### 4 · Redundancia: por qué comprime un zip (y un jpg)
Frase «LA INFORMACION SE MIDE» → sin vocales «L NFRMCN S MD»: se sigue
leyendo. El idioma repite: redundancia de orden 0 medida 16.8 %; con
contexto, Shannon estimó ~75 % (cita, inglés, ~1 bit/letra). Un
compresor sin pérdida quita esa redundancia: icono binario 24×16
(planeta con anillo) crudo 384 bits → RLE (tramos) 175 bits (medido) y vuelve intacto — «el principio de un zip». Con pérdida: la
esfera en gris 8 bits/píxel (3072 bits) cuantizada a 4 niveles (768
bits) — se sigue viendo la esfera: «el principio de un jpg: tirar lo
que el ojo no ve». Cierre: comprimir es no repetir; y a veces, no decir.
Final: las dos imágenes lado a lado con sus bits y el tag «÷4».

### 5 · El canal con ruido
Un canal binario simétrico: 64 bits salen (cian), el ruido voltea cada
uno con p=0.1 (los volteados se marcan en rojo y se CUENTAN: 5). El
esquema del BSC con sus cuatro flechas (1−p, p). Cuánto queda de
información: I = 1 − h(p) — `curva_capacidad_bsc`: p=0 → 1 bit; p=0.1 →
0.531; p=0.5 → 0 (puro azar, no dice nada). Y el teorema (1948): hasta
esa capacidad se puede transmitir con tan pocos errores como se quiera —
no reduciendo el ruido, sino codificando. Final: la tira con los
volteados marcados, el esquema BSC y la curva con «C(0.1) = 0.531
bits/uso».

### 6 · Shannon–Hartley: el techo del enlace
Para un canal real con ancho de banda B y relación señal/ruido S/N:
C = B·log2(1 + S/N). Transpondedor de 36 MHz: C/N 10 dB → 124.5 Mb/s;
20 dB → 239.7 Mb/s: diez veces la potencia y ni el doble de capacidad.
Curva C vs C/N con dos perillas: doblar B dobla C; +3 dB de potencia
suma ~1 bit/s/Hz (3.46 → 4.39). Y el muro: con B infinito, Eb/N0 no
baja de −1.59 dB — el límite de Shannon. Puente con «Cerrar el enlace»:
C/N0 = C/N + 10 log10 B. Cierre: el enlace tiene un techo, y sale de
una fórmula de 1948. Final: la curva con los dos puntos y la fórmula.

### 7 · Corregir sin volver a preguntar: Hamming
Repetir tres veces cada bit corrige un error pero gasta 3×. Hamming
(1950): 4 bits de datos + 3 de paridad, en el diagrama de tres círculos
(`venn_hamming`): cada círculo tiene un número par de unos. Un rayo
voltea el bit 5: dos círculos quedan impares — la intersección delata
el bit → se corrige. Síndrome = posición (MEDIDO). Tasas: 1/3 vs 4/7. En
un BSC p=0.05 (4000 bloques, semilla 11): BER sin código 0.051,
repetición 0.0076, Hamming 0.020 — Hamming corrige menos que repetir
pero manda casi el doble de datos por bit gastado. Cierre: la
comparación justa es por energía por bit — y ahí Shannon puso el techo.
Final: el diagrama corregido (círculos verdes) y la tabla de tasas/BER.

### 8 · El techo de Shannon
El plano SNR (dB) vs eficiencia (b/s/Hz) con la curva de Shannon
log2(1+SNR): nada por encima. Puntos reales de DVB-S2 (cita): QPSK 1/2,
8PSK 3/4, 16APSK 3/4, 32APSK 9/10 — a 1.1–2.9 dB del techo (calculado).
Línea de tiempo: 1948 el teorema (sin decir cómo), 1950 Hamming, 1993
turbo códigos, 2003 LDPC en DVB-S2, 2018 LDPC/polares en 5G: cincuenta
años para rozar el techo. Miniaturas: sorpresa, entropía, Huffman, BSC,
Shannon–Hartley, Hamming. Puente: cada bit que baja del satélite lo mide
esta curva. Pantalla final: «La información no se adivina.» / «Se
mide.» Final: pantalla limpia con las dos frases.

## Contrato de la librería `informacion.py`

Núcleos python/numpy puros y deterministas (nada de red ni disco; todo
azar con `np.random.default_rng(semilla)`); capa Manim con localizadores
sobre geometría ACTUAL y anclas invisibles (mismo patrón que
`cripto.py`/`distribuido.py`: `_ancla`, piezas como `VGroup` con
atributos y métodos localizadores); números por funciones; topes duros con
`ValueError`. Los textos HUD en Space Mono son ASCII puro.

Constantes: `ALFABETO` (26 letras), `ESPACIO = " "`, `SIMBOLOS = ALFABETO +
ESPACIO` (27), `TEXTO_ES` (apertura del Quijote, cap. I, dominio
público, ~500 letras, sin tildes), `MENSAJE_HUFFMAN = "ABRACADABRA"`,
`FRASE_REDUNDANTE = "LA INFORMACION SE MIDE"`, `P_MONEDA_TRUCADA = 0.9`,
`N_PREGUNTAS = 20`, `REDUNDANCIA_SHANNON_1951 = 0.75`, `P_BSC = 0.1`,
`N_BITS_CANAL = 64`, `SEMILLA_CANAL = 3`, `B_TRANSPONDEDOR_HZ = 36e6`,
`CN_DB_1, CN_DB_2 = 10, 20`, `DATOS_HAMMING = [1, 0, 1, 1]`,
`POS_ERROR_HAMMING = 5` (1-based), `P_CODIGOS = 0.05`, `N_BLOQUES = 4000`,
`SEMILLA_CODIGOS = 11`, `TASA_REP3 = 1/3`, `TASA_HAMMING = 4/7`,
`NIVELES_JPG = 4`, `ANCHO_IMG, ALTO_IMG = 24, 16`, `MODCODS_DVBS2` (lista de
tuplas `(nombre, eta, esn0_db)`: ("QPSK 1/2", 0.989, 1.00), ("8PSK 3/4",
2.228, 7.91), ("16APSK 3/4", 2.967, 10.21), ("32APSK 9/10", 4.453, 16.05)
— ETSI EN 302 307-1 tabla 13, cita), `HITOS` (lista `(anio, texto)`:
(1948, "Shannon: el teorema"), (1950, "Hamming"), (1993, "turbo codigos"),
(2003, "LDPC en DVB-S2"), (2018, "LDPC y polares en 5G")).

Funciones (núcleo):
- `sorpresa(p)` = −log2 p (bits; p en (0,1]), `bits_para(n)` = log2 n,
  `preguntas_para(n)` = ceil(log2 n).
- `entropia(probs)` (lista/dict/array; ignora ceros; bits),
  `entropia_binaria(p)` = h(p) con h(0)=h(1)=0.
- `normalizar(texto)` → solo `SIMBOLOS` (mayúsculas, sin tildes, ñ→N,
  espacios múltiples → uno), `frecuencias(texto)` → dict de 27 claves →
  fracción (suma 1), `entropia_texto(texto)` = entropia(frecuencias),
  `redundancia(H, n_simbolos)` = 1 − H/log2 n.
- `huffman(frecs)` → dict símbolo→código (str de 0/1); determinista:
  fusiona los dos pesos menores, empate por orden alfabético; el hijo de
  menor peso recibe "0". `pasos_huffman(frecs)` → lista de fusiones
  `(izq, der, peso)` en orden (izq/der son etiquetas: símbolo o
  concatenación ordenada de símbolos), `longitud_media(codigo, frecs)`,
  `codificar(texto, codigo)` → str de bits, `bits_codificados(texto,
  codigo)` = len(codificar), `bits_fijos(n_simbolos)` = ceil(log2 n).
- `sin_vocales(texto)`.
- `imagen_esfera(ancho, alto)` → np.array uint8 (0..255) de una esfera
  iluminada desde arriba-izquierda sobre fondo 0; `cuantizar(imagen,
  niveles)` → np.array con los `niveles` valores representativos (0..255),
  `bits_imagen(imagen, bits_por_pixel)` = ancho·alto·bits;
  `icono_bits(ancho, alto)` → np.array 0/1 (planeta con anillo, la
  figura ocupa >30 % y <70 % de los píxeles); `rle(bits_1d)` → lista de
  `(valor, largo)`; `bits_rle(bits)` = n_tramos·(1 + ceil(log2(largo_max+1)))
  (documentado en el docstring), MEDIDO < 384/2 para el icono.
- `simular_bsc(bits, p, semilla)` → `(recibidos, n_volteados)`;
  `capacidad_bsc(p)` = 1 − h(p); `informacion_mutua_bsc(p)` alias.
- `db_a_lineal(db)`, `lineal_a_db(x)`, `capacidad_shannon(b_hz, snr_lineal)`
  (bit/s), `eficiencia_espectral(snr_db)` = log2(1+snr),
  `snr_para_eficiencia(eta)` → dB, `ebn0_minimo_db()` = 10 log10(ln 2),
  `cn0_desde_cn(cn_db, b_hz)` = cn_db + 10 log10 B.
- `hamming_codificar(datos4)` → 7 bits (orden estándar p1 p2 d1 p3 d2 d3 d4,
  1-based), `hamming_sindrome(palabra7)` → int 0..7 (posición del error,
  0 = sin error), `hamming_corregir(palabra7)` → `(corregida, pos)`,
  `hamming_decodificar(palabra7)` → 4 datos; `voltear(bits, pos_1based)`.
  Regiones del Venn (índice 1..7 → conjunto de círculos): p1∈{A}, p2∈{B},
  d1∈{A,B}, p3∈{C}, d2∈{A,C}, d3∈{B,C}, d4∈{A,B,C}; `paridades(palabra7)` →
  tupla de 3 bools (círculo par sí/no).
- `repeticion_codificar(bits, n=3)`, `repeticion_decodificar(bits, n=3)`
  (mayoría), `simular_codigos(p, n_bloques, semilla)` → dict
  `{"sin": ber, "rep3": ber, "hamming": ber}` MEDIDOS sobre `n_bloques`
  bloques de 4 bits de datos cada uno (sin código: 4 bits; rep3: 12 bits;
  hamming: 7 bits) por el mismo BSC.
- `ber_bpsk(ebn0_db)` = Q(sqrt(2·Eb/N0)) (con `math.erfc`).

Piezas Manim (cada una `VGroup` con localizadores; soportan `.scale()`,
`.shift()`, `.move_to()`):
- `icono_fuente(nombre, color)`: "moneda" (círculo con "1/2"), "dado"
  (cuadrado con puntos, "1/6"), "baraja" (rectángulo, "1/52"); `.tag`
  (texto HUD de la probabilidad), `.n` (2/6/52).
- `curva_sorpresa()`: ejes p (0.02..1) vs bits (0..6.5), curva −log2 p
  ámbar; `.en(p)` → punto; ticks HUD ("0", "0.5", "1"; "0", "2", "4",
  "6"); tamaño ~4.6×2.8.
- `arbol_preguntas(profundidad=4)`: árbol binario (raíz arriba) con
  ramas "si"/"no" HUD en el primer nivel; `.nivel(k)` (VGroup de nodos),
  `.hoja(i)`, `.camino(bits)` → VGroup de las ramas del camino (para
  resaltar); `.n_hojas` = 2^profundidad.
- `histograma_simbolos(frecs, color, alto=1.6, ancho=6.0)`: 27 barras
  en el orden de `SIMBOLOS` (el espacio rotulado "_"), etiquetas HUD 10,
  `.barra(sim)`, `.linea_base`, `.con_frecuencias(frecs)` (NUEVA pieza,
  misma geometría), `.linea_uniforme()` → línea punteada a la altura de
  1/27 (mismo escalado) — para el «uniforme».
- `curva_entropia_binaria()`: ejes p (0..1) vs h (0..1); `.en(p)`; ticks
  "0", "0.5", "1"; tamaño ~4.2×2.6.
- `arbol_huffman(frecs, colores=None)`: árbol construido con
  `pasos_huffman`: hojas en fila abajo (símbolo + peso HUD), nodos
  internos (círculo pequeño con el peso) arriba, ramas con "0"/"1"
  HUD; `.hoja(sim)`, `.nodo(k)` (k-ésima fusión), `.rama(k, lado)`,
  `.etiqueta_bit(k, lado)`, `.codigo(sim)` → VGroup de ramas del camino
  raíz→hoja; `.paso(k)` → VGroup (nodo k + sus dos ramas + etiquetas) para
  animar la construcción fusión a fusión; `.codigos` (dict = huffman(frecs)).
  Tamaño para 5 símbolos ~5.5×3.2.
- `tira_codigo(texto, codigo, colores)`: el mensaje codificado como
  segmentos contiguos (un rectángulo por símbolo, ancho ∝ bits, color
  por símbolo del dict `colores`, con el símbolo HUD dentro);
  `.segmento(i)`, `.n_bits`; ancho total configurable `ancho=6.0`.
- `imagen_gris(matriz, celda=0.16)`: rejilla de Squares con relleno gris
  proporcional (0..255); `.celda(f, c)`, `.con_matriz(m)` (NUEVA pieza,
  para Transform).
- `imagen_bits(matriz, color, celda=0.16)`: rejilla 0/1 (relleno del
  color op 0.9 si 1 / 0.06 si 0); `.celda(f, c)`, `.con_matriz(m)`.
- `esquema_bsc(p)`: dos nodos de entrada (0, 1) a la izquierda, dos de
  salida a la derecha, cuatro flechas con etiquetas HUD "1-p"/"p"
  (valores numéricos con `p`), las cruzadas rojas; `.entrada(b)`,
  `.salida(b)`, `.flecha(a, b)`, `.etiqueta(a, b)`.
- `tira_bits(bits, color, celda=0.26)`: celdas 0/1 (como cripto);
  `.celda(i)`, `.celdas`, `.con_bits(bits)`, `.marcar_distintos(otros,
  color)` → recolorea IN PLACE las que difieren y devuelve el conteo.
  Para 64 bits admite `filas=2` (dos filas de 32).
- `curva_capacidad_bsc()`: ejes p (0..0.5) vs C (0..1) con 1−h(p);
  `.en(p)`; ticks "0", "0.25", "0.5" / "0", "0.5", "1"; ~4.2×2.6.
- `curva_shannon_hartley(b_hz=36e6, db_max=25)`: ejes C/N (dB, 0..25)
  vs C (Mb/s); `.en(db)`; ticks HUD; `.con_ancho(b_hz)` (NUEVA curva
  con otro B, mismos ejes) para «doblar B dobla C»; ~5.0×2.8.
- `plano_shannon(db_min=-2, db_max=18, eta_max=5)`: ejes SNR (dB) vs
  eficiencia (b/s/Hz), curva violeta log2(1+snr), zona por encima
  sombreada tenue rojo (`.prohibido`); `.punto(db, eta)` → posición;
  `.marca(db, eta, color)` → Dot; ~5.6×3.0.
- `venn_hamming(palabra7)`: tres círculos (A, B, C) superpuestos con los
  7 bits en sus regiones (datos ámbar, paridad verde); `.region(i)`
  (Text del bit i, 1..7), `.circulo(k)` (k en "A","B","C"), `.con_bits(
  palabra7)` (NUEVA pieza), `.colorear_paridad()` (círculo verde si par,
  rojo si impar; devuelve la tupla de `paridades`), `.bits` actuales.
  Radio ~1.05, tamaño ~3.6×3.4.
- `caja_numero(etiqueta, valor, color, ancho=1.9)`: como cripto
  (`.etiqueta`, `.valor`, `.actualizar(valor)`).
- `linea_tiempo(hitos, ancho=9.0)`: línea horizontal con marcas por año
  (HUD) y texto display pequeño alternando arriba/abajo; `.hito(k)`,
  `.marca(k)`.
- `flujo(pasos, colores)`: cajas en fila con flechas (como cripto);
  `.caja(i)`, `.flecha(i)`.

Topes: `BITS_MAX = 512`, `PIXELES_MAX = 4096`, `SIMBOLOS_MAX = 64`,
`BLOQUES_MAX = 20000`, `PROFUNDIDAD_MAX = 6`.

## Producción

Igual que el curso 19: Opus escribe la librería contra este contrato y la
valida numérica y visualmente EN el contenedor (PIL) → yo valido el
style_block con stubs → 3 Opus (clips 1-2, 5-6, 7-8) + Sonnet (clips 3-4
+ demo `28-teoria-informacion.py`) → render_local ql + frames → tests →
PR con PLAN.md → qh local 3 procesos → (merge del usuario) → adoptar en
VPS → guiones.py → mux local con `intro.mp4 + clips + cierre.mp4`.
Proyecto: `studio/content/cursos/teoria-de-la-informacion-los-bits-de-shannon/`, qh.

## Cosecha de trampas (2026-08-15, produccion)

- Duraciones ql medidas: 32.3 / 31.8 / 40.9 / 36.6 / 40.9 / 40.3 / 41.4 /
  37.0 s (8/8 en rango; ~5:01 sin narración).
- `tag_hud(texto, font_size=15, color=None)`: el color va SIEMPRE por
  keyword (los contratos lo escribían posicional y reventaba).
- Piezas que MUTAN (`marcar_distintos`, `colorear_paridad`, `actualizar`)
  no animan: para verlas cambiar se construye la gemela (`con_bits`,
  `con_matriz`, `con_frecuencias`) ya marcada y se hace `Transform`.
- `linea_uniforme()` y `plano.marca()` devuelven mobjects que NO son
  submobjects de la pieza: añadirlos aparte y agruparlos a mano si la
  pieza se escala después.
- `arbol_huffman.paso(k)`/`.codigo(sim)` devuelven referencias: añadir
  solo `arbol.hojas` y hacer `FadeIn(arbol.paso(k))` fusión a fusión.
- `plano_shannon()` por defecto (eta_max=5) recorta la curva y muestra
  una MESETA falsa a partir de ~15 dB: usar `eta_max=6.5` con db_max=18.
- `curva_sorpresa`: la mitad derecha es plana y los rótulos de los puntos
  se pisan; van en posiciones absolutas sobre la curva con guías
  punteadas al punto.
- Las `curva_*` incluyen ticks y etiquetas en el bounding box: `move_to`
  centra más de la cuenta; los rótulos interiores se colocan con
  `.punto(x, y)` dejando ~0.35 de margen al eje y.
- El icono binario lleva el anillo HORIZONTAL a propósito: inclinado
  parte filas en tres tramos y el RLE sube por encima de 192 bits.
- `simular_bsc` con semilla 4 daba 2 volteados (legítimo, pero flojo
  para la narrativa): el style_block usa `SEMILLA_CANAL` (3) → 5.
- Los pies con muchas cifras se acortan a ~90 caracteres para que
  `pie_curso` no los encoja ilegibles; los pies y los tags dicen la
  MISMA cifra (124.5, no «125»).
