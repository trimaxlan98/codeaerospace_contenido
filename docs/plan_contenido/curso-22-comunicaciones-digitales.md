# Curso 24 — Comunicaciones digitales (familia de lecciones)

- **Formato**: familia de lecciones, como Álgebra lineal (curso 22) y
  Cálculo vectorial (curso 23). Un proyecto de ManimStudio = una
  **lección** de 4 clips; cada clip = una idea. **6 módulos × 3 lecciones
  = 18 proyectos, 72 clips** (curso extenso, pedido del dueño).
- **Título de la familia**: `Comunicaciones digitales`.
- **Ángulo editorial**: **la voz que cruza el vacío**. Cómo un bit sale
  de una sonda, sobrevive al ruido y llega a la Tierra. Los ejemplos son
  de MAYORÍA espacial/satelital (cubesats, DSN, Voyager, DVB-S2,
  constelaciones LEO, enlace a Marte) **excepto los necesariamente
  terrestres** — la fibra óptica aparece como lo que es: el canal
  terrestre por excelencia, imposible de tender al espacio. El curso
  termina en **sistemas avanzados** (ACM, acceso múltiple, óptica) y en
  **cómo la IA entra al enlace** (demodulador aprendido, autoencoder del
  canal, enlace cognitivo): módulos 5 y 6 enteros.
- **Público**: divulgación técnica; asume la idea de onda (curso 16), de
  bit y entropía (curso 21) y de dB (curso 13). Las fórmulas se muestran,
  pero lo que se explica es lo que DICEN.
- **No pisa** cursos publicados — este curso es la CAPA DE SÍMBOLOS:
  - Electromagnetismo (16) puso la onda en el aire; aquí la onda ya
    existe y lo que importa es QUÉ dice (fase, amplitud, símbolo).
  - Teoría de la información (21) prometió el techo de Shannon con
    Hamming como aperitivo; aquí se construye la máquina que se acerca
    al techo (convolucional/Viterbi/LDPC — NADA de repetir Hamming).
  - Cerrar el enlace (13) hizo la cuenta en dB; aquí se cita el
    presupuesto en un clip y la moneda es Eb/N0, no se repite el curso.
  - Metrología óptica (20) hizo el interferómetro y el ISL; aquí la
    óptica aparece por su papel de SISTEMA (PPM de fotones, fibra).
- **La marca sonora ya es ley**: el mux usa el intro/cierre con SFX
  (validado en el curso 23, picos −6 dB); es posproducción, nada que
  hacer en los clips.

```
familia            ManimStudio
-----------------  ----------------------------------------
módulo   (6)   →   —  (agrupación editorial, no existe en la DB)
lección  (18)  →   proyecto  "Comunicaciones digitales · N.M <título>"
idea     (72)  →   clip      "MODULO 0K" en el HUD (K = número de clip)
```

Slugs `comunicaciones-digitales-N-M-<tema>`. Clips de 28–45 s (tope
duro), pies ≥ 5 s legibles, el pie cambia ANTES de la animación que
ilustra. Un solo cierre a pantalla limpia por lección (clip 4).

## Principio visual no negociable

1. **La señal se VE como forma de onda y como punto en la constelación**,
   y las dos vistas conviven cuando se puede: el mismo símbolo es una
   onda con fase y un punto en el plano IQ.
2. **El ruido es real**: nubes gaussianas con semilla fija, bits
   volteados CONTADOS, curvas BER medidas por Monte Carlo con numpy —
   nunca "aproximadamente". La curva teórica (Q) se dibuja al lado de los
   puntos medidos y coinciden en pantalla.
3. **Todo número sale de la librería o de la tabla de números del
   style_block** (`fmt`), nunca escrito a mano. La constelación dibujada
   y la BER contada salen del MISMO array de símbolos.
4. Los decodificadores se ven DECIDIR: el trellis de Viterbi ilumina el
   camino ganador con sus métricas; el grafo LDPC pasa mensajes y el
   síndrome baja a cero; la frontera aprendida se dibuja tras entrenar
   DE VERDAD (numpy, semilla fija, entrenamiento en la validación).
5. En cada clip hay un ancla espacial cuando el tema lo da (la sonda, el
   pase del satélite, la antena de la DSN) — pero el protagonista es la
   SEÑAL, no la nave. Escalas exageradas se declaran en el pie.
6. Un solo cierre a pantalla limpia por lección (dos líneas, la segunda
   en cian), como en las familias anteriores.

## Mapa de las 18 lecciones

| Lección | Proyecto | Modelo | Clips |
|---|---|---|---|
| 1.1 | El mensaje digital: muestrear y cuantizar | molde (Fable) | muestreo, alias, cuantización, PCM |
| 1.2 | El pulso y su eco: ISI y Nyquist | Opus | pulso que se ensancha, ISI, coseno alzado, ojo |
| 1.3 | El espectro: el precio en hercios | Sonnet | PSD, ancho de banda vs símbolos, bandas del espacio |
| 2.1 | La fase que habla: BPSK y QPSK | Sonnet | portadora, BPSK, QPSK, el mapa IQ |
| 2.2 | Más bits por símbolo: QAM y APSK | Sonnet | 16-QAM, energía vs distancia, amplificador, APSK |
| 2.3 | El ruido decide: la curva BER | Opus | nube AWGN, regiones, BER medida, cascada |
| 3.1 | El precio de la distancia | Sonnet | FSPL, LEO→Marte→Voyager, lluvia en Ka, fibra |
| 3.2 | Doppler: la frecuencia que se corre | Sonnet | pase LEO, curva S, corrección |
| 3.3 | Sincronía: encontrar la señal | Opus | correlación, secuencia PN, pico, adquisición |
| 4.1 | El código con memoria | Sonnet | repetir no basta, registro, estados, salida |
| 4.2 | Viterbi: el camino más probable | Opus | trellis, métricas, poda, corrección real |
| 4.3 | LDPC: el murmullo que corrige | Opus | grafo bipartito, mensajes, síndrome→0, techo |
| 5.1 | Compartir el cielo: acceso múltiple | Sonnet | TDMA/FDMA, códigos Walsh, CDMA, haces LEO |
| 5.2 | El enlace que se adapta: ACM | Sonnet | lluvia real, umbrales, conmutación, throughput |
| 5.3 | Luz: láser espacial y fibra | Sonnet | PPM de fotones, LCRD, fibra terrestre, comparación |
| 6.1 | El demodulador que aprende | Opus | distorsión, frontera ideal, entrenar, frontera aprendida |
| 6.2 | La constelación inventada | Opus | autoencoder, gradiente en pantalla, constelación nueva, BER |
| 6.3 | El enlace cognitivo | Opus | agente, explorar/explotar, el pase completo, cierre de familia |

## Paleta de la familia (por ROL)

Sobre la paleta de `code_brand`/`algebra_lineal`; **el color dice el
papel**, coherente con los cursos vecinos (violeta = techo de Shannon
como en el 21):

| Alias | Color | Papel |
|---|---|---|
| `C_BIT` | ámbar | el bit, el dato, el mensaje que viaja |
| `C_CIFRA` | cian | TODA cifra calculada (regla de la familia) |
| `C_SENAL` | azul | la forma de onda, la portadora, el canal físico |
| `C_RUIDO` | rojo | ruido, errores, bits volteados, distorsión |
| `C_COD` | verde | códigos, lo corregido, lo que funciona |
| `C_TECHO` | violeta | el techo de Shannon, lo óptimo |
| `C_IA` | fucsia | lo aprendido: pesos, fronteras, constelaciones nuevas |
| `C_BANDA` | naranja | espectro, energía, regiones/ranuras asignadas |
| mobiliario | `C_EJE` gris | ejes, rejillas, cajas |

## Librería `manim_extensions/comunicaciones.py` (contrato)

Importa el sustrato de `algebra_lineal.py` (plano, grafica, vector,
flecha_libre, fmt, paleta) como el curso 23. Numpy puro, determinista
(azar solo con `default_rng(semilla)` fija). Los entrenamientos de IA
son pequeños (cientos de pasos, redes de decenas de pesos) y con semilla:
mismo script → mismo render.

**Números** (validados en el contenedor antes de escribir clips):
    muestrear(f, fs, t1)        instantes y valores de muestreo
    alias_de(f, fs)             la frecuencia alias que aparece
    cuantizar(x, bits)          niveles, señal cuantizada y error
    snr_cuantizacion(x, bits)   SNR medida (≈ 6.02·b + 1.76 dB)
    pulso_rc(beta, span, sps)   coseno alzado (h, t) normalizado
    conformar(bits, h, sps)     tren de pulsos conformado
    isi_en(y, sps, k)           interferencia medida en el instante k
    psd_de(x, fs)               densidad espectral (Welch simple)
    ancho_banda(psd, f, frac)   ancho que contiene `frac` de la energía
    constelacion_(bpsk|qpsk|qam16|qam64|apsk16)   puntos + bits Gray
    energia_media / d_min       de un set de puntos
    awgn(simbolos, ebn0_db, bits_por_simbolo, semilla)
    demodular(rx, puntos)       vecino más cercano
    ber_montecarlo(mod, ebn0_db, n, semilla)   BER contada
    ber_teorica_(bpsk|qpsk|qam16)(ebn0_db)     con Q(x)
    q_de(x)                     la función Q (erfc)
    fspl_db(d_km, f_ghz)        92.45 + 20log d + 20log f
    saleh(r)                    AM/AM del amplificador saturado
    pase_leo(h_km, elev_max)    geometría del pase, t, elevación, d(t)
    doppler_de(pase, f_mhz)     la curva S medida en kHz
    secuencia_pn(n=31)          m-secuencia LFSR x^5+x^2+1
    correlacion_circular(a, b)  el pico 31 / resto −1
    buscar_preambulo(rx, pn)    offset del máximo en señal ruidosa
    conv_codificar(bits)        K=3, G=(7,5) octal, tasa 1/2
    trellis_caminos(recibido)   métricas de rama y acumuladas
    viterbi(recibido)           bits decodificados + camino ganador
    ldpc_pequeno()              H (9×12, Steiner S(2,3,9)), grafo bipartito
    ldpc_decodificar(rx, H)     bit-flipping; síndromes por iteración
    walsh(n=8)                  matriz de Hadamard, filas ortogonales
    cdma_mezclar / cdma_extraer superposición y despreading exactos
    lluvia_serie(semilla)       atenuación Ka con memoria (Markov)
    acm_conmutar(att, umbrales) modcod elegido y throughput acumulado
    ppm_fotones(m, semilla)     ranuras y cuentas de fotones
    entrenar_frontera(rx, etiquetas, semilla)   MLP 2-8-M numpy; pesos
    frontera_de(red, malla)     campo de decisión muestreado
    autoencoder_constelacion(m, pasos, semilla) puntos aprendidos por época
    bandido_acm(episodios, semilla)             recompensas por política

**Piezas** (VGroup con localizadores, patrón `_Anclada` del sustrato):
    onda                 forma de onda en caja de ejes; `.con_muestras()`,
                         `.con_fase(bits)` (gemela para Transform)
    tren_bits            celdas 0/1 estilo tira; `.marcar(i)`, `.con_bits()`
    plano_iq             plano I/Q cuadrado con círculo unidad tenue;
                         `.punto(s)`, `.puntos(set)`, `.nube(rx)`,
                         `.regiones(puntos)` (Voronoi de decisión)
    diagrama_ojo         trazas superpuestas del pulso conformado;
                         `.con_apertura(ebn0)` gemela
    curva_ber            eje semilog (10^0..10^-5, ticks MathTex);
                         `.curva(f)`, `.puntos_medidos(pares)`, `.en(x,y)`
    espectro_barras      PSD como área/escalera; `.con_psd(otra)`
    banda_espacio        regla de frecuencias S/X/Ka con marcas DSN
    enlace_tierra        Tierra + arco + nave a escala declarada;
                         `.paquete()`, `.con_distancia(d)`
    pase_cielo           bóveda del pase LEO: horizonte, trayecto,
                         `.sat_en(t)`, `.elevacion(t)`
    registro_conv        el codificador K=3 (cajas + XOR); `.con_bit(b)`
    trellis              rejilla estados×tiempo; `.rama(t,s,s2)`,
                         `.camino(bits)`, `.metrica(t,s)`, `.podar(...)`
    grafo_ldpc           bits abajo, checks arriba; `.mensaje(i,j)`,
                         `.con_estado(vec)`, `.sindrome()`
    rejilla_acceso       tiempo×frecuencia; `.ranura(u,k)`, `.con_plan()`
    mapa_haces           celdas de una constelación sobre un arco de
                         Tierra; `.haz(k)`, `.con_asignacion()`
    linea_lluvia         serie temporal de atenuación + umbrales modcod
    ranuras_ppm          M ranuras con cuentas de fotones; `.con_simbolo()`
    frontera_decision    campo de decisión coloreado por regiones sobre
                         plano_iq (a partir de `frontera_de`)
    perceptron_mini      esquema 2-8-M con pesos como grosor; `.con_pesos()`

Regla de piezas mutantes: TODO lo que cambia tiene gemela `con_*` y se
anima con Transform entre estructuras IDÉNTICAS (trampa heredada).

## Contrato para los subagentes (una lección por agente)

Igual que en los cursos 22/23: contrato en un .md del scratchpad con
rutas, reglas duras, validación `render_local.py --clip N --frames 8` y
revisión de los 8 frames UNO A UNO; máximo 1 render simultáneo por
agente; los agentes NO tocan librería ni git; informe final con
`LECCION N.M APROBADA`. Molde a imitar: lección 1.1.

## Tablero de estado

| Lección | plan | clips | ql ✔ frames | PR | subida | qh | narrada | mux |
|---|---|---|---|---|---|---|---|---|
| 1.1 | ✔ | ✔ | ✔ 29/28/29/28 s | — | — | — | — | — |
| 1.2 | ✔ | ✔ | ✔ 31/37/40/34 s | — | — | — | — | — |
| 1.3 | ✔ | ✔ | ✔ 31/33/31/32 s | — | — | — | — | — |
| 2.1 | ✔ | ✔ | ✔ 30/31/30/30 s | — | — | — | — | — |
| 2.2 | ✔ | ✔ | ✔ 32/29/31/34 s | — | — | — | — | — |
| 2.3 | ✔ | ✔ | ✔ 31/31/31/33 s | — | — | — | — | — |
| 3.1 | ✔ | ✔ | ✔ 29/30/29/32 s | — | — | — | — | — |
| 3.2 | ✔ | ✔ | ✔ 30/29/30/30 s | — | — | — | — | — |
| 3.3 | ✔ | ✔ | ✔ 33/30/33/39 s | — | — | — | — | — |
| 4.1 | ✔ | ✔ | ✔ 31/32/32/34 s | — | — | — | — | — |
| 4.2 | ✔ | ✔ | ✔ 32/38/39/34 s | — | — | — | — | — |
| 4.3 | ✔ | ✔ | ✔ 34/34/34/42 s | — | — | — | — | — |
| 5.1 | ✔ | ✔ | ✔ 29/29/28/31 s | — | — | — | — | — |
| 5.2 | ✔ | ✔ | ✔ 34/30/30/35 s | — | — | — | — | — |
| 5.3 | ✔ | ✔ | ✔ 33/33/31/34 s | — | — | — | — | — |
| 6.1 | ✔ | ✔ | ✔ 31/33/30/36 s | — | — | — | — | — |
| 6.2 | ✔ | ✔ | ✔ 34/31/33/40 s | — | — | — | — | — |
| 6.3 | ✔ | ✔ | ✔ 34/31/39/37 s | — | — | — | — | — |

## Módulo 1 — Del dato al símbolo

### 1.1 El mensaje digital: muestrear y cuantizar  (slug `comunicaciones-digitales-1-1-muestreo`)
La temperatura de una sonda es una curva continua; para radiarla hay que
volverla números. Molde de la familia.
1. **La señal continua** — telemetría (seno lento + armónico, semilla
   fija) dibujada como `onda`; la sonda al margen. Pie: medir no es
   copiar la curva: es preguntarle su valor de vez en cuando.
2. **Muestrear: cada cuánto preguntar** — muestras cayendo sobre la
   curva (fs alta → reconstruye; fs baja → **alias**: un seno de 7 Hz
   muestreado a 10 Hz se disfraza de 3 Hz, `alias_de` MEDIDO, las dos
   curvas pasan por los mismos puntos). Nyquist: fs > 2·f_max.
3. **Cuantizar: cuántos escalones** — la vertical se parte en 2^b
   niveles; el error de redondeo como banda roja; SNR MEDIDA con
   `snr_cuantizacion`: b=3 → ~19.8 dB áspero, b=8 → ~49.9 dB limpio;
   la regla 6.02·b + 1.76 en el pie.
4. **PCM: la curva hecha bits** — la muestra cuantizada se escribe en
   binario y sale como `tren_bits` hacia la antena. Cierre: "La voz de
   la sonda no es la curva. / Son los bits que la cuentan."

### 1.2 El pulso y su eco: ISI y Nyquist  (slug `comunicaciones-digitales-1-2-pulsos`)
Un bit no puede ser un rectángulo perfecto: el canal lo ensancha.
1. **El rectángulo imposible** — un pulso cuadrado pasa por un canal de
   banda limitada y sale redondeado y con colas (conformado real). Pie:
   el canal no deja cambiar de golpe.
2. **El eco sobre el vecino (ISI)** — tres símbolos seguidos: las colas
   del primero caen sobre el instante de decisión del tercero;
   `isi_en` MEDIDA en pantalla; con pulsos torpes el símbolo vecino
   miente.
3. **El pulso de Nyquist** — el coseno alzado (β=0.35, el de DVB-S2):
   sus colas cruzan CERO exactamente en los instantes de los demás
   símbolos (ceros marcados, medidos ~0.00). Interferir sin estorbar.
4. **El diagrama de ojo** — `diagrama_ojo` con muchas trazas: el ojo
   abierto (sin ruido) y cerrándose al bajar Eb/N0 (gemelas
   `con_apertura`). Apertura MEDIDA. Cierre: "El símbolo perfecto no es
   el más cuadrado. / Es el que calla cuando hablan los demás."

### 1.3 El espectro: el precio en hercios  (slug `comunicaciones-digitales-1-3-espectro`)
Cada símbolo por segundo cuesta ancho de banda, y el espectro está
repartido.
1. **La señal vista en frecuencia** — la misma señal de bits como onda
   y como `espectro_barras` (PSD de Welch): el lóbulo sinc². Pie: toda
   señal ocupa un trozo de espectro.
2. **Más rápido = más ancho** — duplicar la velocidad de símbolos
   ensancha el lóbulo al doble (dos PSD medidas, `ancho_banda` al 90%
   rotulado). El tiempo y la frecuencia se compran uno al otro.
3. **El conformado ahorra espectro** — rectangular vs coseno alzado:
   las colas espectrales caen; el ancho ocupado (99%) baja de ~2/T a
   ~(1+β)/T. Por eso nadie transmite rectángulos.
4. **Las bandas del espacio** — `banda_espacio`: S (2.3 GHz), X (8.4),
   Ka (32) con las marcas de la DSN; más arriba cabe más pero llueve
   peor (adelanto del 3.1). Cierre: "El espectro es la tierra firme de
   las comunicaciones. / Y está toda repartida."

## Módulo 2 — La constelación

### 2.1 La fase que habla: BPSK y QPSK  (slug `comunicaciones-digitales-2-1-fase`)
La portadora no cambia de forma: cambia de fase, y la fase dice bits.
1. **La portadora vacía** — un coseno puro (`onda`) y su punto quieto en
   `plano_iq`: una onda sin mensaje. Las dos vistas conviven.
2. **BPSK: un bit por vuelco** — bits 0/1 voltean la fase 180°; en la
   onda se ven los saltos; en el plano IQ dos puntos (±1). Un bit por
   símbolo.
3. **QPSK: dos bits por fase** — cuatro fases a 90°, mapa de Gray
   rotulado (00/01/11/10); la onda salta entre cuatro formas; el
   cubesat de ejemplo baja el doble de bits en el mismo espectro.
4. **El mapa IQ es el idioma** — la constelación como plano de todo el
   curso: cada punto un mensaje, la distancia entre puntos la
   resistencia al ruido (d_min MEDIDA). Cierre: "La onda es la misma. /
   El mensaje vive en su fase."

### 2.2 Más bits por símbolo: QAM y APSK  (slug `comunicaciones-digitales-2-2-qam`)
Amplitud y fase juntas: más densidad, menos margen.
1. **16-QAM: la retícula** — 16 puntos, 4 bits por símbolo; comparación
   con QPSK a la MISMA energía media (medida): d_min baja de 1.414 a
   0.632 — el precio de la densidad.
2. **64-QAM y la escalera de densidades** — 6 bits/símbolo; d_min
   medida otra vez; regla: cada doblez de densidad cuesta ~6 dB. La
   escalera QPSK→16→64 con sus d_min rotuladas.
3. **El amplificador de a bordo** — `saleh`: el amplificador saturado
   comprime los puntos exteriores de 16-QAM (AM/AM en pantalla, la
   retícula se deforma de verdad). En un satélite la potencia es oro y
   el amplificador trabaja al borde.
4. **APSK: anillos para el espacio** — 16-APSK (4+12): anillos que
   sufren menos la compresión; es la constelación de DVB-S2 (la TV por
   satélite real). Cierre: "En tierra, la retícula. / En órbita, los
   anillos."

### 2.3 El ruido decide: la curva BER  (slug `comunicaciones-digitales-2-3-ruido-ber`)
El ruido térmico empuja cada símbolo; a veces lo empuja al vecino.
1. **La nube AWGN** — QPSK con `awgn` a Eb/N0 = 12 dB: nubes apretadas
   alrededor de cada punto (semilla fija). El receptor decide por
   cercanía (`.regiones` de Voronoi tenues).
2. **Cuando la nube cruza la frontera** — a 4 dB las nubes se solapan;
   los símbolos caídos en región ajena se pintan rojos y se CUENTAN
   (errores/total en pantalla).
3. **La curva BER medida** — `curva_ber` semilog: puntos Monte Carlo
   (`ber_montecarlo`, n=2·10^5 por punto) cayendo SOBRE la curva
   teórica Q (QPSK: ~1.2·10^-2 a 4 dB, ~1.9·10^-4 a 8 dB, medidos). La
   cascada: cada dB regala casi un orden de magnitud.
4. **La cascada compara familias** — QPSK vs 16-QAM en el mismo eje:
   la densa paga ~4 dB por sus 2 bits extra. Elegir modulación es
   elegir dónde vivir en esta gráfica. Cierre: "El ruido no se
   negocia. / Se mide, y se le hace sitio."

## Módulo 3 — El canal espacial

### 3.1 El precio de la distancia  (slug `comunicaciones-digitales-3-1-distancia`)
El vacío no absorbe la señal: la diluye en la esfera que crece.
1. **La esfera que se reparte** — `enlace_tierra` con la potencia
   repartida en la esfera; FSPL = 92.45 + 20log d + 20log f en el pie;
   cada duplicación de distancia son 6 dB (medido con `fspl_db`).
2. **La escalera de los enlaces** — LEO 550 km a 12 GHz: 168.8 dB; GEO
   35 786 km: 205.1 dB; Marte 2.25·10^8 km a 8.4 GHz: ~278 dB; Voyager
   24.6·10^9 km: ~319 dB (todos `fspl_db`). Y aun así se oye: el
   presupuesto del curso 13 (antenas + códigos) citado en un pie.
3. **La lluvia cobra en Ka** — la banda alta paga lluvia: serie
   `lluvia_serie` sobre el margen; en X apenas, en Ka decenas de dB
   (adelanto del ACM de 5.2).
4. **La fibra: el canal terrestre** — 0.2 dB/km parece poco… hasta
   multiplicar por la distancia a Marte; la fibra vive de poner
   amplificadores cada ~80 km, y en el vacío no hay dónde ponerlos. Por
   eso la Tierra habla por fibra y el espacio por radio. Cierre: "En la
   Tierra, la luz viaja acompañada. / En el espacio, la señal va sola."

### 3.2 Doppler: la frecuencia que se corre  (slug `comunicaciones-digitales-3-2-doppler`)
El satélite no está quieto: su velocidad corre la frecuencia.
1. **El pase** — `pase_cielo`: el satélite LEO cruza la bóveda en ~10
   min (`pase_leo` con h=550 km, elev. máx. 60°); la distancia baja y
   sube (curva medida).
2. **La curva S** — `doppler_de` a 437 MHz (cubesat UHF): de +11 kHz a
   −11 kHz, con la pendiente máxima justo en el cénit. La frecuencia
   recibida NO es la transmitida.
3. **Perder al satélite** — el receptor sintonizado fijo pierde la
   señal cuando el corrimiento sale del ancho del filtro (franja
   naranja); los segundos de enganche CONTADOS.
4. **Corregir: perseguir la frecuencia** — el receptor corrige con la
   curva S conocida (predicción de efemérides): la señal corregida
   queda plana en 0 (medida). Cierre: "El cielo nunca da la frecuencia
   prometida. / Da la que hay que saber perseguir."

### 3.3 Sincronía: encontrar la señal  (slug `comunicaciones-digitales-3-3-sincronia`)
Antes de entender los símbolos hay que saber DÓNDE empiezan.
1. **El mar de ruido** — una señal enterrada (SNR bajo, semilla fija):
   a simple vista, nada. El receptor no sabe cuándo empezó el mensaje.
2. **La llave: una secuencia que solo se parece a sí misma** —
   `secuencia_pn` (m-secuencia de 31 chips): su autocorrelación
   (`correlacion_circular`) vale 31 en fase y −1 fuera (barras
   medidas). Ese pico es una huella digital.
3. **Deslizar y correlar** — el preámbulo se desliza sobre la señal
   ruidosa; la correlación va dibujándose y EXPLOTA en el offset
   correcto (`buscar_preambulo`, offset rotulado). Ahí empieza el
   mensaje.
4. **Adquisición** — con el inicio y la frecuencia (3.2), el receptor
   abre los relojes de símbolo: los instantes de decisión caen en el
   centro del ojo (1.2 citado). Cierre: "Oír no es lo difícil. / Lo
   difícil es saber cuándo empezó la frase."

## Módulo 4 — Códigos con memoria

### 4.1 El código con memoria  (slug `comunicaciones-digitales-4-1-convolucional`)
El curso 21 repetía bits; aquí cada bit de salida recuerda a los
anteriores.
1. **Repetir no basta** — repetición ×3 recordada en una tira (cara del
   curso 21): cara BER floja por bit gastado. Hace falta gastar mejor.
2. **El registro que recuerda** — `registro_conv` (K=3, G=7,5): el bit
   entra, dos salen, y cada salida mezcla el presente con dos pasados
   (XOR animados con un bit real recorriendo el registro).
3. **La máquina de estados** — los 4 estados (00,01,10,11) y sus
   flechas: la salida depende del camino, no solo del bit
   (`conv_codificar` de una ristra real en pantalla, entrada ámbar →
   salida verde).
4. **La memoria protege** — el mismo mensaje codificado: ahora un error
   aislado es INCOHERENTE con la memoria (se marca la incoherencia).
   Detectarlo es posible; corregirlo, lo que sigue. Cierre: "Un código
   sin memoria olvida. / Este recuerda por ti."

### 4.2 Viterbi: el camino más probable  (slug `comunicaciones-digitales-4-2-viterbi`)
Decodificar es encontrar el camino barato en el trellis.
1. **El trellis** — `trellis` (4 estados × 8 pasos): todos los caminos
   posibles del codificador; el mensaje verdadero es UNO de ellos
   (camino ámbar).
2. **El precio de cada rama** — llega la señal con 2 bits volteados
   (rojos); cada rama cuesta su distancia Hamming a lo recibido
   (`trellis_caminos`, métricas rotuladas en las ramas del primer
   tramo).
3. **Podar: quedarse con lo barato** — en cada nodo sobreviven solo los
   caminos de métrica mínima (los caros se apagan); las métricas
   acumuladas bajan por la rejilla.
4. **El superviviente** — `viterbi`: el camino ganador (verde) se
   ilumina de vuelta; los bits decodificados = los transmitidos, los 2
   errores CORREGIDOS (contador 2→0). Voyager llevó este decodificador
   (K=7) a los planetas exteriores. Cierre: "Entre todos los mensajes
   posibles, / gana el que menos ruido necesita."

### 4.3 LDPC: el murmullo que corrige  (slug `comunicaciones-digitales-4-3-ldpc`)
Miles de comprobaciones simples hablando entre sí rozan el techo de
Shannon.
1. **El grafo** — `grafo_ldpc` (12 bits, 9 comprobaciones — el sistema
   triple de Steiner S(2,3,9), plano afín de orden 3): cada check
   exige paridad par a sus vecinos; H en el panel. Un código es un
   sistema de vecindarios.
2. **El síndrome acusa** — llegan 2 bits volteados (un par de líneas
   paralelas: checks disjuntos): los 6 checks insatisfechos se encienden
   en rojo (`sindrome` medido); las cuentas H^T·s señalan a los dos.
3. **El murmullo (bit-flipping)** — `ldpc_decodificar` itera EN
   PANTALLA: voltea el más acusado, el síndrome baja (peso 6→3→0,
   medido por iteración); el grafo queda verde. El código chico es de
   tasa 1/4 (k=3): se declara, y el techo del clip 4 se rotula para la
   tasa 1/2 de DVB-S2.
4. **A un paso del techo** — `curva_ber`: sin código vs con LDPC
   (medida con el código pequeño) y la pared de Shannon (violeta,
   curso 21 citado): DVB-S2 opera a ~1 dB del techo con esta idea a
   escala 64 800. Cierre: "Nadie corrige solo. / El mensaje se corrige
   en comunidad."

## Módulo 5 — Sistemas avanzados

### 5.1 Compartir el cielo: acceso múltiple  (slug `comunicaciones-digitales-5-1-acceso`)
Mil terminales, un satélite: el enlace se reparte en tiempo, frecuencia
o código.
1. **La rejilla tiempo-frecuencia** — `rejilla_acceso`: FDMA corta en
   columnas, TDMA en filas (usuarios coloreados); el recurso es UNA
   sábana finita.
2. **CDMA: hablar a la vez** — códigos `walsh(8)`: ortogonales
   (producto punto 0 MEDIDO); dos usuarios suman sus chips en el mismo
   tiempo-frecuencia (`cdma_mezclar`, la suma se ve caótica).
3. **El despreading** — `cdma_extraer`: correlar con el código de cada
   usuario recupera SUS bits exactos (contador de aciertos 8/8); con el
   código equivocado, ruido plano (~0).
4. **Los haces de la constelación** — `mapa_haces`: una constelación
   LEO pinta celdas sobre la Tierra y reutiliza frecuencias en haces no
   vecinos (asignación coloreada); el espectro se multiplica por
   geografía. Cierre: "El cielo no se agranda. / Se reparte mejor."

### 5.2 El enlace que se adapta: ACM  (slug `comunicaciones-digitales-5-2-acm`)
El canal cambia con el clima; el enlace moderno cambia con él.
1. **El canal que respira** — `linea_lluvia` (serie Ka con memoria,
   semilla fija): el Eb/N0 disponible sube y baja decenas de dB en
   minutos.
2. **La ley del margen fijo** — diseñar para el peor caso = enlace
   lento SIEMPRE (línea plana bajo la serie; capacidad desperdiciada
   sombreada y MEDIDA en %).
3. **Conmutar el modcod** — `acm_conmutar`: umbrales de QPSK½ →
   8PSK¾ → 16APSK⅚ (escalera violeta); el enlace escala y baja
   SIGUIENDO la lluvia; cada tramo rotulado con su modcod.
4. **La cuenta final** — throughput acumulado ACM vs margen fijo
   (medido: ~2–3× más bits el mismo día) con outage contado (segundos
   sin enlace). DVB-S2 hace esto en cada lluvia real. Cierre: "El
   enlace de antes aguantaba el clima. / El de ahora lo aprovecha."

### 5.3 Luz: láser espacial y fibra  (slug `comunicaciones-digitales-5-3-luz`)
Los dos futuros de la luz: el fotón contado en el vacío y el río de
bits bajo el mar.
1. **Subir de banda una última vez** — de Ka (32 GHz) al láser (193
   THz): la regla de 1.3 llevada al extremo (`banda_espacio`
   extendida); haz estrecho, antena pequeña, sin espectro que pedir.
2. **PPM: el fotón que llega tarde dice qué bit era** — `ranuras_ppm`
   (M=16): el símbolo es la RANURA donde caen los fotones (cuentas
   medidas, semilla fija); con un puñado de fotones por bit, LCRD y
   DSOC hablan desde la Luna y desde 3·10^8 km.
3. **La fibra: la excepción terrestre** — el mismo láser DENTRO del
   vidrio: WDM (80 colores × 100 Gb/s en el panel), amplificado cada
   80 km; el 99% de los bits del planeta van bajo el mar, no por
   satélite. Es el canal que el espacio no puede tener (3.1 citado).
4. **Cada canal a lo suyo** — tabla comparada (alcance, dB/km, Gb/s,
   quién la usa): fibra para la Tierra, radio para llegar a cualquier
   parte, láser para el espacio profundo que viene. Cierre: "No hay un
   canal mejor. / Hay un canal para cada silencio."

## Módulo 6 — La IA en el enlace

### 6.1 El demodulador que aprende  (slug `comunicaciones-digitales-6-1-demodulador`)
Cuando el canal deforma la constelación, las fronteras de libro fallan.
1. **La constelación deformada** — 16-QAM tras `saleh` (2.2 citado) +
   AWGN: la retícula recibida está comprimida y girada en las esquinas
   (nube real, semilla fija).
2. **La frontera de libro falla** — regiones Voronoi IDEALES sobre la
   nube deformada: los errores se pintan rojos y se CUENTAN (BER
   ideal-sobre-deformado medida).
3. **Entrenar** — `entrenar_frontera` (MLP 2-8-16 numpy, semilla): la
   pérdida baja por época (curva medida); la `frontera_decision`
   aprendida se dibuja: fronteras CURVAS que abrazan la deformación
   (fucsia).
4. **El veredicto** — misma nube, dos demoduladores: errores contados,
   el aprendido corta la BER (dos cifras comparadas en pantalla). El
   receptor ya no presume el canal: lo aprende. Cierre: "La frontera
   de libro presume el canal. / La aprendida lo escucha."

### 6.2 La constelación inventada  (slug `comunicaciones-digitales-6-2-autoencoder`)
Si el demodulador puede aprender, ¿por qué no aprender también el
transmisor? El enlace entero como una sola red.
1. **El enlace como red** — `perceptron_mini` extendido: codificador →
   canal (ruido) → decodificador; entrenar EXTREMO A EXTREMO: la
   pérdida es la propia tasa de error.
2. **El gradiente mueve los puntos** — `autoencoder_constelacion`
   (M=8): las posiciones POR ÉPOCA se animan — de un amasijo inicial a
   un anillo/red que se separa solo (d_min por época MEDIDA subiendo).
3. **La constelación que nadie dibujó** — el resultado no es la QAM del
   manual: es la que ESTE canal prefiere (comparadas lado a lado,
   energía media igualada y medida).
4. **¿Mejor?** — BER medida: aprendida vs 8-PSK clásica en el mismo
   canal (la aprendida gana o empata, cifras en pantalla); en canales
   raros (no lineales) la ventaja crece — investigación viva de 6G y
   NASA. Cierre: "Cien años dibujando constelaciones. / La red dibujó
   la suya en mil pasos."

### 6.3 El enlace cognitivo  (slug `comunicaciones-digitales-6-3-cognitivo`)
Cierre de familia: un agente opera el enlace y la misión junta todas
las piezas.
1. **Decidir bajo el clima** — el pase con lluvia (5.2) visto como
   PROBLEMA de decisión: estados (cielo/lluvia), acciones (modcods),
   recompensa (bits que llegan). Nadie da la política: hay que
   aprenderla.
2. **Explorar y explotar** — `bandido_acm` (ε-greedy, semilla): las
   primeras decisiones son torpes (recompensa por episodio baja y
   ruidosa), la curva de aprendizaje sube y se estabiliza (medida).
3. **El agente contra las reglas fijas** — recompensa acumulada:
   agente vs conservador (siempre QPSK½) vs optimista (siempre
   16APSK): el agente los rebasa (cifras finales medidas). Los enlaces
   cognitivos reales (DVB-S2X, DSN) van hacia aquí.
4. **La misión completa** — UN paquete de Marte a la Tierra cruzando
   TODA la familia en cascada: muestreo (M1) → constelación (M2) → el
   vacío y la sincronía (M3) → Viterbi/LDPC (M4) → ACM (M5) → el
   agente que eligió el modcod (M6); cada etapa se ilumina al pasar.
   Cierre de FAMILIA: "El vacío sigue sin tener nada que decir. /
   Nosotros ya sabemos cruzarlo hablando."

## Cosecha heredada (cursos 22 y 23) — vigente para los agentes

Ver la sección "Cosecha de trampas" de `curso-21-calculo-vectorial.md`
y de `curso-20-algebra-lineal.md`: TODAS siguen vigentes (Transform
solo entre gemelas de estructura idéntica; Rajdhani sin superíndices ni
griegas — 10^-3 y ∈/Σ van en MathTex; `tag_hud` solo ASCII;
`set_opacity` enciende el fill; `Indicate` sobre `_con_fondo` apunta al
contenido; `render_local` muestrea 8 frames y puede caer en relevos de
pie; pies ≥ 5 s y ANTES de la animación; un cierre por lección).
Propias de esta familia se cosecharán al final.

## Cosecha de trampas de la familia (medida durante la produccion)

- pulso_lento: pico en t=+0.5 (canal causal); TAU=0.9 para el error literal.
- pulso_rect: borde |t|<=0.5 inclusivo -> picos 2.0 al conformar; NRZ con
  np.repeat (patron de valida_vis_com).
- ancho_banda con frac=0.9 (el 99% del sinc^2 satura cerca de Nyquist).
- DiagramaOjo sin localizador publico (usar ._en; candidato .en publico);
  con_apertura NO existe (la gemela es con_trazas); SNR medida entre series
  dibujadas en vez de Eb/N0.
- regiones de QPSK caen sobre los ejes I/Q (pintarlas C_BANDA + cuadrantes
  tenues); nube filtra por alcance ADEMAS de maximo (pre-filtrar y contar
  sobre lo visible); Transform de nubes: partir AMBAS con la misma mascara.
- awgn a 12 dB: empujon ~0.13 u (elegir la muestra de ruido maximo para la
  flecha).
- curva_ber: leyendas fuera de la caja (la zona interior derecha la ocupan
  las curvas); la llave de brecha cabe ARRIBA del recuadro.
- hud_modulo: K = numero de CLIP (el molde 1.1 nacio mal y se corrigio).
- RegistroConv: el cableado (taps 0,2) era el correcto; el bug era el
  encoder (arreglado). viterbi: np.bool_ + np.bool_ no suma (arreglado).
- El storyboard prometia trellis_caminos y .podar que no existen (la poda
  se reconstruye con RAMAS_CONV en el style_block de 4.2; docstrings ya
  corregidos).
- PaseCielo sin .horizonte/.cupula publicos (VGroup(*submobjects[1:4])).
- tag_hud: ~0.0094*font_size unidades por caracter (medir antes de anclar
  paneles); fmt no hace notacion cientifica (helpers fmt_exp/fmt_ber/sci
  locales en 3.1/4.3/2.3; candidato a libreria).
- Onda.muestras sirve de stem plot; _escalera(v) para chips cuadrados
  (style_block de 3.3; candidata a libreria).
- ldpc: H 9x12 Steiner, sindrome 6-3-0 con par (0,2); el codigo chico es
  tasa 1/4 (declararlo; el techo violeta se rotula para tasa 1/2 DVB-S2).
- grafo_ldpc con sindrome=None = "sin comprobar" (gris) para no mentir
  entre beats.
- Grafica(etiqueta_x/y) son hijos internos: no aparecen si animas
  .ejes/.curva por separado (rotulos propios).
- banda_espacio(0,6) para llegar al laser (193000 GHz); ticks >=1e3 en THz.
- interpolate_color exige ManimColor (las C_* de la familia son str).
- bandido_acm no exporta su entorno (ATT/snr_claro/epsilon): replicar en
  la tabla para explicar la politica; candidato a devolverlos en el dict.
- formula_pie con \sum o fracciones + llave hacia abajo = choque seguro
  (la formula sube a la franja libre bajo el titulo).
- Transform de cifras durante animaciones largas deja digitos a medio
  morfar en los frames: Succession(Transform corto, Wait) — la cifra
  salta y descansa; y ancho fijo (03d) para pasos.
- Onda siempre construye su curva: para dibujarla por tramos, remove(
  on.curva) y curva_de por segmentos.
- frontera_de/campo_vecino con el alcance COMPLETO del plano roza los
  rotulos I/Q: calcular el campo a ~0.9x el alcance (6.1 uso 1.58).
- perceptron_mini dibuja max 8 nodos por capa: rotular la arquitectura
  real + "(se dibujan N por capa)" con N leido de la pieza.
- Rotulos.mostrar de la familia cobra salida=0.25 extra en cada relevo:
  contarlo al estimar duraciones.
- Sector() de manim 0.20.1 no acepta outer_radius (solo radius).
- Los agentes de renderizado: extraer el ultimo frame real con ffmpeg
  para final_state (el frame 8 muestreado puede caer antes del cierre).
