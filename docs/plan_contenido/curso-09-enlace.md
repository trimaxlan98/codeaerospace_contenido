# Curso 09 — Cerrar el enlace: la cuenta en decibelios

- **Proyecto**: name `Cerrar el enlace: la cuenta en decibelios`,
  quality `qh`.
- **Fuente**: Academy, curso Redes satelitales M2 (presupuesto de
  enlace: FSPL, PIRE, C/N0, G/T, Eb/N0), M7 (Shannon-Hartley, MODCOD
  DVB-S2X, ACM) y pinceladas de M1 (distancia y latencia) y M5
  (elevacion y atenuacion atmosferica).
- **Slug**: `cerrar-el-enlace-la-cuenta-en-decibelios`.
- **Publico**: divulgacion; conecta con los cursos publicados de
  SDR, El espectro y Señales y espectro.
- **Hilo narrativo**: la pregunta (¿llega algo?) → el decibelio como
  idioma → la PIRE (potencia que apunta) → la caida del espacio libre
  → el ruido que nunca se apaga → la cascada completa → el techo de
  Shannon → el margen y la lluvia.

## Que NO entra (para no canibalizar cursos ya publicados)

- **Mapa de bandas, lluvia como fenomeno, UIT**: son el curso 10 (El
  espectro). Aqui la lluvia aparece SOLO como los dB que se comen el
  margen en el clip 8, sin curva de atenuacion ni tabla de bandas.
- **IQ, FFT, waterfall, demodulacion, diagrama de ojo**: son el curso
  8 (SDR). Las constelaciones de aqui son peldaños de eficiencia
  (bits/simbolo), no un ejercicio de deteccion.
- **Fourier y el espectro de la señal**: curso 4 (publicado).

## Paleta del curso

| Constante | Valor | Rol |
|-----------|-------|-----|
| `C_SENAL` | `#f59e0b` ambar | la señal, la potencia util, la PIRE |
| `C_GANANCIA` | `#34d399` verde | todo lo que SUMA: ganancia de antena, G/T |
| `C_PERDIDA` | `#f43f5e` rojo | todo lo que RESTA: FSPL, atmosfera, lluvia |
| `C_RUIDO` | `#a78bfa` violeta | el ruido, N0, kTB, la temperatura |
| `C_MARGEN` | `#22d3ee` cian | el resultado, el margen, el enlace que cierra |
| `C_EJE` | `#31414f` | mobiliario (ejes, guias, reglas) |

Regla de color, la columna vertebral del curso: **verde suma, rojo
resta, cian es lo que sobra al final**. El espectador debe poder leer
cualquier cascada sin oir la narracion. No mezclar roles.

## Contrato de la libreria `studio/content/manim_extensions/enlace.py`

Determinista, sin red, sin archivos (`np.random.default_rng(semilla)`
donde hace falta azar: nube de simbolos y piso de ruido). Mismo estilo
que `espectro.py` / `radio.py`: subclases de `VGroup` con localizadores
que leen la geometria ACTUAL del mobject, validos tras mover o escalar.
Topes duros que levantan `ValueError`: `TERMINOS_MAX = 8`,
`PELDANOS_MAX = 6`, `SIMBOLOS_MAX = 256`, `MUESTRAS_MAX = 400`.

```python
# --- el idioma: decibelios -------------------------------------------
regla_db(ancho=6.4, alto=0.9, font_size=15)
    # -> ReglaDB(VGroup): dos escalas alineadas verticalmente sobre el
    #    mismo eje. Arriba, factores lineales (1, 2, 10, 100, 10^6...);
    #    abajo, su equivalente en dB (0, 3, 10, 20, 60...). Las marcas
    #    de una y otra caen en la MISMA x: el mensaje visual es que
    #    multiplicar arriba es sumar abajo. Metodos .marca_lineal(i) y
    #    .marca_db(i) -> np.array (posicion de la muesca i), y
    #    .par(i) -> VGroup(etiqueta_lineal, etiqueta_db) para Indicate.
    #    Atributos .eje, .lineales, .decibelios.

# --- la potencia que apunta ------------------------------------------
patron_ganancia(ganancia_db=0.0, escala=1.6, color="#f59e0b",
                muestras=180)
    # -> PatronGanancia(VMobject): curva polar cerrada apuntando a la
    #    DERECHA cuyo estrechamiento depende de `ganancia_db`: con 0 dB
    #    es una circunferencia (isotropica), y al subir se estira en un
    #    lobulo cada vez mas largo y estrecho, a AREA VISUAL
    #    aproximadamente constante (la misma potencia, mejor repartida
    #    — esa es la idea que debe leerse). Metodo .con_ganancia(g_db)
    #    -> nuevo PatronGanancia del mismo centro y escala, para
    #    Transform. Metodo .punta() -> np.array (extremo del lobulo).

# --- la caida del espacio libre --------------------------------------
frente_esferico(radios=(0.6, 1.2, 1.8, 2.4), origen=ORIGIN,
                color="#f59e0b", puntos=42, semilla=7)
    # -> FrenteEsferico(VGroup): anillos concentricos punteados desde
    #    `origen`, cada uno con `puntos` marcas cuya OPACIDAD cae como
    #    1/r^2 respecto al primero: la misma energia repartida en una
    #    esfera que crece. Metodo .anillo(i) -> VGroup y .en(i, deg) ->
    #    np.array (punto del anillo i en ese angulo, para colgar el
    #    receptor). Atributo .anillos.
curva_fspl(f_ghz=(2.0, 12.0, 30.0), d_km=(300.0, 40000.0), ancho=5.8,
           alto=2.6, color_ejes="#31414f", font_size=14)
    # -> CurvaFspl(VGroup): ejes (distancia km en log ->, FSPL dB ^)
    #    con una curva por frecuencia dada, rotuladas "2 GHz", "12 GHz",
    #    "30 GHz" (etiqueta al final de cada curva, alturas separadas
    #    para no encimarse). Formula exacta 20log10(d)+20log10(f)+92.45.
    #    Metodos .punto_de(d_km, f_ghz) -> np.array y .db(d_km, f_ghz)
    #    -> float (el numero que el clip rotula: coherencia visual y
    #    numerica garantizada). Atributos .curvas, .ejes.

# --- el ruido ---------------------------------------------------------
piso_ruido(ancho=5.6, alto=2.2, nivel=0.28, cima_rel=0.85, semilla=11,
           color="#a78bfa", color_senal="#f59e0b", muestras=300)
    # -> PisoRuido(VGroup): un piso de ruido (linea densa y erizada,
    #    determinista) sobre el que asoma un lobulo de señal centrado.
    #    `nivel` y `cima_rel` son alturas ABSOLUTAS relativas a la caja
    #    (0-1): el suelo y la punta de la señal. Metodos .con_nivel(v) y
    #    .con_senal(v) -> nuevo PisoRuido de la misma caja para
    #    Transform: subir el ruido acerca el suelo a una señal que NO se
    #    mueve, que es la lectura que pide el clip 5. Metodos .cima() ->
    #    np.array y .margen_rel() -> float. Atributos .ruido, .senal,
    #    .ejes.
termometro_ruido(t_kelvin=150.0, t_max=600.0, alto=2.2, ancho=0.42,
                 color="#a78bfa", font_size=15)
    # -> TermometroRuido(VGroup): barra vertical tipo termometro con la
    #    temperatura de ruido del sistema, con su rotulo "T = 150 K"
    #    debajo. Metodo .a_temperatura(t) -> Animation que reescala la
    #    columna Y reescribe el rotulo (una sola animacion: el numero y
    #    la barra jamas se desincronizan). Atributos .columna, .rotulo.

# --- la cascada: el corazon del curso --------------------------------
cascada_db(terminos, ancho=7.0, alto=3.0, font_size=15,
           color_ganancia="#34d399", color_perdida="#f43f5e",
           color_saldo="#22d3ee")
    # -> CascadaDB(VGroup): diagrama de cascada (waterfall) del balance.
    #    `terminos` es una lista de (etiqueta, valor_db); positivo sube
    #    en verde, negativo baja en rojo, y cada barra arranca donde
    #    acabo la anterior, con guia punteada entre una y la siguiente.
    #    La barra final (saldo acumulado) se dibuja en cian desde cero.
    #    Etiquetas HUD bajo cada barra, alternando dos alturas para no
    #    encimarse, y el valor con signo encima de la barra.
    #    Construccion progresiva: .aparecer(i) -> Animation de la barra
    #    i (para LaggedStart o beat a beat), .barra(i) -> VGroup,
    #    .acumulado(i) -> float (dB tras aplicar el termino i) y
    #    .nivel(i) -> np.array (punto del extremo de la barra i, para
    #    colgar llaves). Tope: 8 terminos.

# --- el techo del canal ----------------------------------------------
curva_shannon(snr_db=(-5.0, 25.0), ancho=5.6, alto=2.8,
              color="#22d3ee", color_ejes="#31414f", font_size=14)
    # -> CurvaShannon(VGroup): ejes (SNR dB ->, eficiencia espectral
    #    bits/s/Hz ^) con la curva log2(1+SNR) rotulada como "limite de
    #    Shannon". La region SOBRE la curva es la zona prohibida (patron
    #    tenue rojizo, opacity 0 al inicio para FadeIn). Metodos
    #    .punto_de(snr_db) -> np.array, .eficiencia(snr_db) -> float y
    #    .punto_modcod(snr_db, eficiencia) -> np.array (coloca un
    #    MODCOD real bajo la curva, en sus coordenadas). Atributos
    #    .curva, .ejes, .prohibida.
nube_simbolos(orden=4, dispersion=0.06, escala=1.1, semilla=3,
              color="#f59e0b")
    # -> NubeSimbolos(VGroup): constelacion de `orden` simbolos (4 =
    #    QPSK, 8 = 8PSK, 16 y 32 = APSK en anillos) como nubes de 24
    #    puntos deterministas alrededor de cada simbolo ideal, con
    #    `dispersion` proporcional al ruido. Metodos .con_orden(n) y
    #    .con_dispersion(d) -> nueva NubeSimbolos de la misma caja para
    #    Transform. Tope 256 simbolos totales.

# --- el margen --------------------------------------------------------
escalera_modcod(peldanos, ancho=4.6, alto=2.6, font_size=14,
                color="#22d3ee")
    # -> EscaleraModcod(VGroup): escalera ascendente donde cada peldaño
    #    es un MODCOD (etiqueta corta tipo "QPSK 3/4") colocado a la
    #    altura de su eficiencia; `peldanos` es una lista de
    #    (etiqueta, snr_db, bits_hz). Metodos .peldano(i) -> VGroup,
    #    .centro_de(i) -> np.array y .marcador(i) -> Dot cian sobre el
    #    peldaño activo (uno solo, reutilizable con .mover_a(i) ->
    #    Animation). Tope 6 peldaños.
barra_margen(margen_db=6.0, tope_db=12.0, alto=2.6, ancho=0.5,
             font_size=15, color="#22d3ee", color_perdida="#f43f5e")
    # -> BarraMargen(VGroup): barra vertical con el margen disponible en
    #    cian sobre una linea de umbral ("cierra / no cierra") marcada
    #    en el cero. Metodo .comer(db) -> Animation que pinta de rojo,
    #    DESDE ARRIBA, los `db` que se lleva la lluvia y actualiza el
    #    rotulo numerico en la misma animacion. Metodo .valor() -> float
    #    del margen restante. Atributos .columna, .umbral, .rotulo.
```

Demo obligatoria:
`studio/content/animations/experimentacion/19-enlace.py` con
`DemoEnlace(Scene)` (~15 s): regla_db con un par resaltado,
patron_ganancia transformando de 0 a 30 dB, frente_esferico,
curva_fspl con un punto rotulado, piso_ruido subiendo el nivel,
termometro_ruido, cascada_db de 4 terminos, curva_shannon con dos
MODCOD, nube_simbolos QPSK -> 16APSK, escalera_modcod y barra_margen
comiendose 8 dB.

## Reglas duras para los clips

Identicas a los cursos 01-08: solo `class ClipN(Scene)`; `Rotulos`
para todo texto narrativo; un fenomeno por clip; **28-45 s** (tope
INVIOLABLE, fusionar pies si no caben); determinismo; MathTex raw
corto; solo paleta del curso; comentario `# --- momento: ... ---` por
beat; cada pie visible >= 5 s; **el pie cambia ANTES del transform que
ilustra**. Validacion con
`studio/tools/render_local.py <curso> --todos --frames 8`.

Ademas, propia de este curso: **todo numero que se rotule sale de la
libreria** (`curva_fspl.db(...)`, `cascada_db.acumulado(...)`,
`curva_shannon.eficiencia(...)`), nunca escrito a mano en el clip. Un
curso sobre una cuenta no puede tener la cuenta mal.

---

## Clip 1 · ¿Llega algo? (~35 s)

**Intencion**: plantear la pregunta del curso con una cifra que
duele, y prometer la herramienta que la responde.

**Visual**: portada («Cerrar el enlace» / «la cuenta en decibelios»).
Sale la portada, entra HUD `MODULO 01`. Un satelite chico arriba a la
derecha y una antena abajo a la izquierda, unidos por un haz ambar
tenue. Junto al satelite, `20 W`. El haz recorre la distancia y al
llegar a la antena aparece el numero recibido: `0.000000000004 W`,
que se encoge y se reescribe como `4 \times 10^{-12}\ \text{W}`.

**Rotulos**
- Titulo: «¿Llega algo?»
- Pie 1: «Un satelite geoestacionario transmite con 20 vatios. Menos
  que un foco de refrigerador.»
- Pie 2: «A 36 000 kilometros, lo que llega a tu antena es esto.»
- Formula: `4 \times 10^{-12}\ \text{W}`
- Pie 3: «Cuatro billonesimas de vatio. Y aun asi, el enlace
  funciona.»

**final_state**: satelite y antena unidos por el haz, la cifra
`4 \times 10^{-12}\ \text{W}` en la zona de pie y HUD `MODULO 01`.

## Clip 2 · Un idioma para numeros absurdos (~33 s)

**Intencion**: el decibelio no es jerga; es lo que hace la cuenta
posible. Multiplicar se vuelve sumar.

**Visual**: `regla_db` al centro. Se resaltan tres pares en secuencia
(`Indicate` sobre `.par(i)`): ×2 → +3 dB, ×10 → +10 dB, ×1 000 000 →
+60 dB. Despues, la cifra del clip 1 (`4e-12 W`) baja desde el pie,
se posa sobre la regla y se transforma en `-113.6\ \text{dBW}`.

**Rotulos**
- Titulo: «Un idioma para numeros absurdos»
- Pie 1: «Cada vez que la señal se divide o se multiplica, la cuenta
  se vuelve impronunciable.»
- Pie 2: «El decibelio cambia multiplicar por sumar.»
- Formula: `-113.6\ \text{dBW}`
- Pie 3: «Aquel numero de once ceros cabe ahora en cuatro cifras.»

**final_state**: `regla_db` al centro con el par ×10/+10 dB
resaltado y la conversion `-177 dBW` bajo ella; HUD `MODULO 02`.

## Clip 3 · PIRE: la potencia que apunta (~36 s)

**Intencion**: la ganancia de antena no crea potencia, la reparte;
por eso se suma en dB.

**Visual**: `patron_ganancia(0)` — una circunferencia ambar — con la
antena en el centro. Transform a `.con_ganancia(20)` y luego a
`.con_ganancia(45)`: el circulo se estira en un lobulo largo y
estrecho hacia el satelite, que aparece a la derecha. Al fondo, la
suma `13\ \text{dBW} + 45\ \text{dB} = 58\ \text{dBW}` armada termino
a termino (los mismos 20 W del clip 1, ya en decibelios).

**Rotulos**
- Titulo: «PIRE: la potencia que apunta»
- Pie 1: «Una antena no fabrica potencia: decide hacia donde va.»
- Pie 2: «Toda la energia que deja de ir a los lados va al frente.»
- Formula: `\text{PIRE} = P_{tx} + G_{tx}`
- Pie 3: «Veinte vatios bien apuntados pesan como cincuenta y ocho
  decibelios.»

**final_state**: lobulo estrecho apuntando al satelite a la derecha y
la suma `PIRE = P + G` en la zona de pie; HUD `MODULO 03`.

## Clip 4 · La caida del espacio libre (~40 s)

**Intencion**: la perdida dominante no es un defecto del equipo, es
geometria pura.

**Visual**: `frente_esferico` expandiendose desde la antena: los
anillos crecen y sus puntos pierden opacidad como 1/r². Un receptor
(cuadrito ambar) fijo en un anillo lejano captura una fraccion
minuscula. Transicion a `curva_fspl`: tres curvas (2, 12, 30 GHz).
Un punto sobre 40 000 km @ 12 GHz se rotula con `.db(...)`
(≈ 206 dB). Se marca la regla del +6: doblar distancia o frecuencia
añade 6 dB, con dos flechas cortas sobre la curva.

**Rotulos**
- Titulo: «La caida del espacio libre»
- Pie 1: «Nada se pierde en el vacio: la misma energia se reparte en
  una esfera que no para de crecer.»
- Pie 2: «Tu antena solo recoge el trocito de esfera que tapa.»
- Formula: `\text{FSPL} = 20\log_{10} d + 20\log_{10} f + 92.45`
- Pie 3: «Doblar la distancia cuesta seis decibelios. Doblar la
  frecuencia, otros seis.»

**final_state**: `curva_fspl` con las tres curvas rotuladas y el punto
de 40 000 km a 12 GHz marcado con su valor en dB; HUD `MODULO 04`.

## Clip 5 · El ruido que nunca se apaga (~38 s)

**Intencion**: no basta con que llegue señal; tiene que llegar por
encima del ruido. Y el ruido tiene temperatura.

**Visual**: `piso_ruido` con la señal asomando comoda sobre el piso.
El piso SUBE (`Transform` a `.con_nivel(...)` mayor) hasta casi tapar
el pico: la señal no cambio, el ruido si. A la derecha entra
`termometro_ruido(150)` y sube a 400 K en una sola animacion
(barra + rotulo). Cierre: la figura de merito `G/T` aparece como
cociente, verde arriba (ganancia) y violeta abajo (temperatura).

**Rotulos**
- Titulo: «El ruido que nunca se apaga»
- Pie 1: «Todo lo que tiene temperatura emite ruido. Tu antena, el
  cielo, tu propio receptor.»
- Pie 2: «La señal no empeoro: subio el suelo.»
- Formula: `N_0 = k\,T`
- Pie 3: «Por eso un receptor no se juzga por su ganancia, sino por
  ganancia entre temperatura.»
- Formula final: `G/T`

**final_state**: piso de ruido alto con la señal apenas asomando, el
termometro a 400 K a la derecha y `G/T` en la zona de pie; HUD
`MODULO 05`.

## Clip 6 · La cascada (~42 s)

**Intencion**: el clip central. Todo lo anterior es una sola cuenta
que se lee de izquierda a derecha.

**Visual**: `cascada_db` construida termino a termino, uno por beat,
con `.aparecer(i)`: `PIRE +58`, `FSPL −205.2`, `atmosfera −1.5`,
`G/T +13.2`, `−k +228.6`. Cada barra cuelga de donde acabo la
anterior. Al final entra la barra cian del saldo:
`C/N_0 = 93.2\ \text{dBHz}`, tomada de `.acumulado(-1)`. Luego una
llave sobre el saldo y la conversion a `E_b/N_0` restando
`10\log_{10}(R_b)` con `R_b = 50` Mbps → `16.2 dB`.

**Rotulos**
- Titulo: «La cascada»
- Pie 1: «Todo el enlace cabe en una fila de sumas y restas.»
- Pie 2: «Verde suma, rojo resta.»
- Pie 3: «Lo que sobra al final es lo unico que importa.»
- Formula: `C/N_0 = \text{PIRE} - \text{FSPL} - L_{atm} + G/T - 10\log_{10} k`
- Pie 4: «Y repartido entre los bits por segundo, dice si el mensaje
  se entiende.»

**final_state**: cascada completa de cinco terminos con la barra cian
del saldo `C/N0` a la derecha y la formula del balance en la zona de
pie; HUD `MODULO 06`.

## Clip 7 · El techo de Shannon (~38 s)

**Intencion**: con la cuenta cerrada, ¿cuantos bits caben? Hay un
limite fisico, y la ingenieria vive pegada a el.

**Visual**: `curva_shannon` con la region prohibida apareciendo sobre
la curva. Tres MODCOD reales se posan bajo la curva con
`.punto_modcod(...)`: QPSK 1/2, 8PSK 3/4, 16APSK 3/4. A la izquierda,
`nube_simbolos` transforma de orden 4 a 8 a 16: mas simbolos, mas
bits por simbolo, nubes mas apretadas.

**Rotulos**
- Titulo: «El techo de Shannon»
- Pie 1: «Ninguna antena, ningun codigo, ningun truco pasa de esta
  curva.»
- Formula: `C = B\log_2(1 + \text{SNR})`
- Pie 2: «Mas simbolos caben mas bits, pero se estorban entre ellos.»
- Pie 3: «Los estandares modernos operan a menos de un decibelio del
  limite.»

**final_state**: curva de Shannon con la region prohibida sombreada y
tres MODCOD marcados debajo; a la izquierda la constelacion 16APSK;
HUD `MODULO 07`.

## Clip 8 · Margen: el dia que llueve (~40 s)

**Intencion**: cerrar el curso donde vive el ingeniero — no en el
caso nominal, sino en el mal dia. Y mostrar que el enlace moderno
degrada en vez de caerse.

**Visual**: `barra_margen(6)` a la izquierda, `escalera_modcod` a la
derecha con el marcador en el peldaño alto. Llega la tormenta:
`.comer(8)` pinta de rojo desde arriba y el margen se vuelve
negativo. El marcador BAJA dos peldaños (`.mover_a`), el margen
vuelve a cian y la eficiencia cae. Cierre: la marca del canal y el
pie final.

**Rotulos**
- Titulo: «El dia que llueve»
- Pie 1: «El enlace no se diseña para el buen dia: se diseña para el
  malo.»
- Pie 2: «Ocho decibelios de lluvia se comen el margen entero.»
- Pie 3: «El enlace no se corta: baja un peldaño y sigue.»
- Pie 4: «Cerrar el enlace no es tener suerte. Es haber hecho la
  cuenta.»

**final_state**: barra de margen recuperada en cian con la zona
comida en rojo arriba, escalera de MODCOD con el marcador dos
peldaños mas abajo y el pie de cierre; HUD `MODULO 08`.
