# Curso 19 · «Criptografía: el arte de guardar secretos» (archivo curso-17)

> **Numeración**: los archivos `curso-NN-*.md` van por orden de creación;
> la numeración REAL la lleva `PLAN.md`. Este es el **curso 19**.

## Tesis

Un secreto no se guarda escondiéndolo: se guarda con **matemáticas que
cualquiera puede leer**. César cae ante la estadística del idioma; la
llave perfecta (XOR de un solo uso) existe pero es impráctica; el gran
truco del siglo XX es que dos desconocidos, gritando en público, acaben
con un secreto que nadie más tiene (Diffie–Hellman); multiplicar es
fácil y factorizar difícil (RSA); un hash convierte cualquier cosa en
una huella que cambia a la mitad si tocas un bit; y firmar es cifrar al
revés. Todo eso junto es el candado del navegador — y también el enlace
con el satélite. Cierre honesto: la computadora cuántica lo amenaza y ya
hay relevo (post-cuántica). «Un secreto no se esconde: se calcula.»

## Los números (todos calculados por la librería, jamás a mano)

| Cantidad | Valor | Fuente |
|---|---|---|
| Llaves de César | 25 útiles (26 con la trivial) | `len(ALFABETO) - 1` |
| Letra más frecuente del español (Quijote I, cap. VIII, 502 letras) | **E** 13.55 %, luego A 11.55, O 10.16, S 9.56 | `frecuencias(TEXTO_ES)` MEDIDO |
| Desplazamiento recuperado del cifrado | **3** (chi-cuadrado mínimo) | `desplazamiento_estimado(cifrado)` |
| Llaves posibles de un pad de 24 bits | 2^24 = **16 777 216** | `2 ** n_bits` |
| Llaves secretas para n personas | 10 → 45; 100 → 4 950; 1000 → **499 500** | `llaves_por_pares(n)` = n(n−1)/2 |
| Diffie–Hellman p=23, g=5, a=6, b=15 | A=**8**, B=**19**, secreto **2** en los dos lados | `diffie_hellman(23, 5, 6, 15)` |
| RSA de juguete p=61, q=53, e=17 | n=**3233**, φ=3120, d=**2753** | `rsa_juguete(61, 53, 17)` |
| Cifrar m=65 / descifrar | c=**2790** → 65 | `rsa_cifrar`, `rsa_descifrar` |
| Primos probados para romper 3233 por fuerza bruta | **16** (2…53, incluido el que divide) — MEDIDO | `divisiones_hasta_factor(3233)` |
| Bits que cambian en SHA-256 entre "hola" y "Hola" | **138** de 256 (53.9 %) — MEDIDO | `bits_distintos(sha256_bits("hola"), sha256_bits("Hola"))` |
| Firma RSA del hash (juguete) | s = h^d mod n; verificación s^e mod n == h | `firmar`, `verificar` |
| Bit alterado en el mensaje → hash distinto | verificación **falla** — MEDIDO | `verificar` sobre el hash nuevo |

## Reglas de honestidad

- El texto de muestra es un párrafo real en español (dominio público),
  normalizado a 26 letras ASCII (sin tildes, ñ→n) — se rotula «texto de
  muestra»; las frecuencias son las MEDIDAS en ese texto, no las de una
  tabla.
- El one-time pad es «secreto perfecto» SOLO si la llave es aleatoria,
  tan larga como el mensaje y de un solo uso — el clip lo dice y ahí
  entra el problema de repartir llaves.
- Diffie–Hellman y RSA van con números de juguete (se rotula «juguete»):
  los reales tienen 2048 bits (~617 dígitos). Lo que se muestra es la
  aritmética real, no una metáfora de colores.
- «Factorizar es difícil» se muestra con la cuenta de divisiones de
  prueba (medida) y su crecimiento ~10^(d/2) — se dice que hay
  algoritmos mejores que la fuerza bruta, pero ninguno rápido conocido
  para computadora clásica.
- El hash SHA-256 es el real (`hashlib`): la avalancha se MIDE contando
  bits, no se cita.
- La firma de juguete firma el hash reducido módulo n (se rotula); en la
  práctica se usa relleno (PSS) — se menciona.
- Cierre cuántico: Shor (1994) rompe RSA y DH **si** hay una computadora
  cuántica grande — hoy no la hay; el relevo post-cuántico (ML-KEM,
  estándar NIST 2024) ya se está desplegando.

## Paleta (regla semántica)

- `C_CLARO` ámbar `#f59e0b` — el mensaje en claro, lo secreto, lo que se
  protege.
- `C_CIFRADO` cian `#22d3ee` — lo cifrado, lo público, lo que viaja por
  el canal.
- `C_LLAVE` verde `#34d399` — las llaves (y lo que se verifica bien).
- `C_ATAQUE` rojo `#f43f5e` — Eva, la fuerza bruta, la alteración, lo
  que falla.
- `C_HUELLA` violeta `#a78bfa` — hash, firma, integridad.
- `C_EJE` gris azulado `#31414f` — mobiliario.

## Los 8 clips (28–45 s duros; pies ≥5 s; pie cambia ANTES del transform)

### 1 · La rueda de César
Un mensaje ámbar («NOS VEMOS AL AMANECER») y la rueda de César: dos
anillos con el alfabeto; el exterior gira 3 posiciones y cada letra se
convierte en la de enfrente (cifrado cian, letra a letra con lag). Eva
(rojo) no necesita ingenio: solo hay 25 llaves. La rueda gira las 25 y
una columna de intentos pasa rápido: en el desplazamiento 3 aparece el
texto legible resaltado en verde. Cierre: una llave que se puede
enumerar no es una llave. Final: rueda en 3, mensaje claro y cifrado
alineados, tag «25 llaves · fuerza bruta».

### 2 · El idioma delata
Aunque la llave fuera enorme, César tiene otra grieta: la estadística.
Histograma de frecuencias del español MEDIDO en el texto de muestra
(E la más alta, luego A, O, S). Debajo, el histograma del texto cifrado:
la misma silueta, corrida. Los picos se alinean con un deslizamiento
del histograma cifrado hasta encajar (chi-cuadrado mínimo → 3). Cierre:
el idioma tiene huella; el cifrado bueno tiene que borrarla. Final: los
dos histogramas encajados con «desplazamiento = 3» rotulado.

### 3 · La llave perfecta
Bits. Mensaje de 24 bits (tres letras ASCII) en tira ámbar; llave
aleatoria de 24 bits en verde; XOR bit a bit → tira cifrada cian que
parece ruido. Lo mágico: XOR con la llave otra vez devuelve el mensaje.
Y lo perfecto (Shannon 1949): con OTRA llave, el mismo cifrado da OTRO
mensaje válido — se muestra que una llave distinta produce «SOL» en vez
de «MAR» — el atacante no puede saber cuál: 2^24 = 16 777 216 llaves,
16 777 216 mensajes. Cierre honesto: la llave debe ser aleatoria, tan
larga como el mensaje y de un solo uso — perfecto e impráctico. Final:
las tres tiras (mensaje/llave/cifrado) con «2^24 llaves = 2^24 mensajes».

### 4 · Gritar en público (Diffie–Hellman)
El problema: n personas necesitan n(n−1)/2 llaves secretas — grafo
completo que crece: 10 → 45, 100 → 4 950, 1000 → 499 500 aristas. 1976:
Ana y Beto acuerdan un secreto hablando SOLO en público. Números de
juguete: p=23, g=5 (públicos, cian). Ana elige a=6 (ámbar, privado) y
grita A = 5^6 mod 23 = 8; Beto elige b=15 y grita B = 5^15 mod 23 = 19.
Ana calcula 19^6 mod 23 = 2; Beto 8^15 mod 23 = 2. **El mismo 2**, que
nunca viajó. Eva ve 23, 5, 8, 19 y necesitaría el logaritmo discreto:
fácil con 23, imposible con 2048 bits. Final: esquema con los dos
secretos ámbar «2» a cada lado, el canal cian con 8 y 19, y Eva roja
en medio con «?».

### 5 · Multiplicar es fácil, factorizar no (RSA)
1977. Ana publica un candado que cualquiera cierra y solo ella abre.
Juguete: p=61, q=53 (secretos, ámbar) → n=3233 (público, cian), φ=3120,
e=17 (público), d=2753 (privado). Beto cifra m=65: 65^17 mod 3233 =
2790; Ana descifra 2790^2753 mod 3233 = 65. Eva conoce 3233 y 17: para
hallar d necesita p y q. Fuerza bruta: 3233 cae en 16 primos probados
(MEDIDO, se ve el contador); la curva 10^(d/2) muestra que un n de 617
dígitos (2048 bits) exige ~10^308 — «más divisiones que átomos en el
universo». Final: la caja n=3233 con la llave pública (n, e) cian y la
privada d ámbar; contador «16 primos probados» y la curva con 10^308.

### 6 · La huella digital (hash)
Un hash convierte cualquier mensaje en 256 bits: rejilla 16×16 de bits
violeta para SHA-256("hola"). Cambia una letra («Hola»): rejilla nueva —
los bits que cambiaron se marcan en rojo y se CUENTAN: 138 de 256, la
mitad (avalancha). Y no hay vuelta atrás: de la huella no se recupera el
mensaje. Aplicaciones: contraseñas guardadas como huella; integridad de
un archivo. Final: dos rejillas con la diferencia marcada y la cifra
medida «138 de 256 bits cambian».

### 7 · Firmar sin pluma
Firmar es RSA al revés: Ana toma la huella h del mensaje (violeta), la
cifra con su llave PRIVADA d (ámbar) → firma s; cualquiera con la
pública (n, e) verifica s^e mod n == h. Eva altera un bit del mensaje:
la huella cambia, la firma ya no coincide → **falla** en rojo. Todo con
los números de juguete del clip 5 (h reducido mod n, rotulado). Cierre:
la firma prueba autor e integridad. Final: cadena mensaje → huella →
firma con la verificación en verde y, debajo, la alterada en rojo.

### 8 · El candado del navegador
Recapitulación en un apretón de manos TLS: (1) Diffie–Hellman acuerda la
llave de sesión, (2) la firma RSA prueba quién es el servidor, (3) AES
(simétrico, rápido) cifra el volumen, (4) el hash cuida la integridad.
Miniaturas de los clips. Puente: el mismo candado va en el enlace con
el satélite. Cierre honesto: Shor rompería RSA y DH con una computadora
cuántica grande — que aún no existe — y el relevo post-cuántico (ML-KEM,
NIST 2024) ya se despliega. Pantalla final: «Un secreto no se esconde.»
/ «Se calcula.» Final: pantalla limpia con las dos frases.

## Contrato de la librería `cripto.py`

Núcleos python/numpy puros y deterministas (nada de red, nada de disco;
todo azar con semilla; SHA-256 vía `hashlib`); capa Manim con
localizadores sobre geometría ACTUAL y anclas invisibles (mismo patrón
que `distribuido.py`: `_ancla`, piezas como `VGroup` con atributos y
métodos localizadores); números por funciones; topes duros con
`ValueError`. Los textos HUD en Space Mono son ASCII puro.

Constantes: `ALFABETO` ("ABCDEFGHIJKLMNOPQRSTUVWXYZ"), `TEXTO_ES`
(párrafo real en español, dominio público, ~300-500 letras),
`MENSAJE_CESAR = "NOS VEMOS AL AMANECER"`, `DESPLAZAMIENTO = 3`,
`P_DH, G_DH, A_DH, B_DH = 23, 5, 6, 15`, `P_RSA, Q_RSA, E_RSA = 61, 53,
17`, `M_RSA = 65`, `MENSAJE_HASH = "hola"`, `MENSAJE_HASH_2 = "Hola"`,
`MENSAJE_OTP = "MAR"`, `MENSAJE_OTP_2 = "SOL"`, `SEMILLA_OTP = 7`,
`N_BITS_OTP = 24`.

Funciones (núcleo):
- `normalizar(texto)` → solo letras de ALFABETO (sin tildes, ñ→N,
  mayúsculas), espacios conservados.
- `cesar(texto, k)`, `frecuencias(texto)` → dict letra→fracción (26
  claves, suma 1), `desplazamiento_estimado(cifrado, referencia=None)`
  → k con chi-cuadrado mínimo contra `frecuencias(TEXTO_ES)`.
- `texto_a_bits(texto)` (ASCII 8 bits por letra) / `bits_a_texto`,
  `llave_otp(n_bits, semilla)`, `xor_bits(a, b)`, `llave_que_da(cifrado,
  mensaje_deseado)` (llave = cifrado XOR deseado — la demostración de
  Shannon).
- `llaves_por_pares(n)` = n(n−1)/2.
- `potencia_mod(base, exp, mod)` (cuadrados sucesivos, entero puro),
  `diffie_hellman(p, g, a, b)` → dict {A, B, s_ana, s_beto}, y `pasos_potencia_mod`
  opcional para animar.
- `rsa_juguete(p, q, e)` → dict {n, phi, d} (d por Euclides extendido),
  `rsa_cifrar(m, e, n)`, `rsa_descifrar(c, d, n)`,
  `divisiones_hasta_factor(n)` → número de PRIMOS probados hasta hallar
  un factor (MEDIDO), `divisiones_estimadas(digitos)` = 10^(d/2) (float; desborda a inf en 617 dígitos, por eso `exponente_divisiones(digitos)` = d/2 es lo que se rotula),
  `DIGITOS_RSA_2048 = 617`.
- `sha256_bits(texto)` → np.array de 256 ints 0/1, `sha256_hex(texto)`,
  `bits_distintos(a, b)` → int MEDIDO.
- `firmar(h, d, n)` = h^d mod n, `verificar(s, e, n, h)` → bool,
  `hash_reducido(texto, n)` = int(sha256, 16) mod n.
- `alterar_bit(texto, indice)` → texto con un bit volteado (en una letra
  imprimible: si el resultado no es imprimible, voltea otro bit y lo dice
  en el docstring).

Piezas Manim (cada una `VGroup` con localizadores):
- `rueda_cesar(radio=1.6)`: dos anillos de letras (exterior claro ámbar,
  interior cifrado cian); `.girar(k)` devuelve la animación/estado del
  anillo exterior rotado k posiciones; `.letra_exterior(ch)`,
  `.letra_interior(ch)` localizadores.
- `tira_letras(texto, color, font_size=30)`: letras en fila con `.letra(i)`;
  espacios como huecos.
- `histograma_frecuencias(frecs, color, alto=1.6, ancho=5.2)`: 26 barras
  con etiquetas de letra abajo; `.barra(ch)`, `.con_frecuencias(frecs)`
  (nuevas alturas), `.desplazado(k)` (barras rotadas k posiciones).
- `tira_bits(bits, color, celda=0.28)`: celdas 0/1; `.celda(i)`,
  `.con_bits(bits)`; `etiqueta_bits` opcional.
- `grafo_llaves(n, radio=1.4)`: n nodos en círculo + todas las aristas;
  `.aristas` (VGroup), `.n_aristas` (= llaves_por_pares(n)).
- `esquema_dh()`: dos personajes (círculos con inicial "A"/"B") a los
  lados, canal cian en medio, Eva roja debajo del canal; `.ana`, `.beto`,
  `.eva`, `.canal`, `.punto_ana`, `.punto_beto` localizadores; `.mensaje(texto,
  desde="ana")` devuelve un `Text` HUD colocado sobre el canal (el clip
  lo anima).
- `caja_numero(etiqueta, valor, color, ancho=1.9)`: caja redondeada con
  etiqueta pequeña arriba y valor HUD grande; `.valor` mobject
  (para Transform), `.actualizar(valor)`.
- `curva_divisiones(d_max=620)`: ejes (dígitos vs divisiones, y en
  log10) con la curva 10^(d/2); `.en(digitos)`; ticks rotulados
  10^0..10^300 con MathTex (no Space Mono).
- `rejilla_hash(bits, color, celda=0.17)`: 16×16 celdas rellenas según
  bit; `.celda(i)`, `.marcar_distintos(otros_bits, color)` recolorea las
  que difieren y devuelve el conteo (MEDIDO).
- `candado(color, alto=1.0)`: icono de candado (arco + cuerpo);
  `.abierto()`/`.cerrado()` estados.
- `flujo(pasos, colores)`: cajas en fila unidas por flechas (mensaje →
  huella → firma), `.caja(i)`, `.flecha(i)`.

Topes: `LETRAS_MAX = 600`, `BITS_MAX = 512`, `NODOS_MAX = 40`.

## Producción

Igual que cursos 16–18: Opus escribe la librería contra este contrato y
la valida numérica y visualmente EN el contenedor (PIL) → yo valido el
style_block con stubs → 3 Opus (clips 1-2, 4-5, 7-8) + Sonnet (clips 3
y 6 + demo `27-criptografia.py`) → render_local ql + frames → tests →
PR con PLAN.md → qh local 3 procesos → adoptar en VPS → guiones.py →
mux local con `intro.mp4 + clips + cierre.mp4` (primer curso con la
marca nueva).
Proyecto: `studio/content/cursos/criptografia-el-arte-de-guardar-secretos/`, qh.
