# Curso 38 — Radio definida por software (familia «SDR»)

## Cómo reanudar

- Worktree `~/Documentos/github/codeaerospace_contenido-sdr`, rama `curso/sdr-completo` (enlaces `render_jobs` y `exports` al segundo disco ya hechos).
- Tablero de estado: §12 de este archivo. Librería `studio/content/manim_extensions/sdr.py`, sonda `studio/tools/sonda_sdr.py`.
- El dueño reanuda con: «continuamos con el curso de SDR».
- Molde de la familia: `studio/content/cursos/sdr-1-1-de-la-antena-al-numero/` (lo escribe el orquestador).

## 1. Encargo (2026-09-24)

«Vamos a lanzar un curso ya completo de comunicaciones por SDR; tenemos ya una pequeña versión pero se queda corta. Vamos a lanzarlo a YouTube.»

La versión pequeña es el curso 8 (`sdr-la-radio-hecha-software`, 8 clips de divulgación). Decisiones del dueño, mismo día:
- **24 lecciones** (8 módulos × 3, 96 clips, ~55 min).
- Enfoque **radio real + señales reales**: cada técnica se justifica con una señal que el espectador puede captar con un RTL-SDR de 30 dólares; los casos prácticos llevan el peso.

Por defecto (lo mismo que el curso 37, que también fue a YouTube): horizontal **CONSOLA**, **narrado sin subtítulos**, **sin «Modulo 0N»**, voz edge sintetizada en local, montajes en `exports/sdr-*/curso_narrado.mp4`. Subirlo al VPS/ManimStudio queda a decisión del dueño.

## 2. Formato

- Familia horizontal 16:9, estilo **CONSOLA**, 8 módulos × 3 lecciones = **24 proyectos, 96 clips**.
- Nombre `SDR · N.M <Título>` (clave de `subir_curso.py`: no cambiar después de subir). Slug `sdr-N-M-<tema>`.
- **Narrado sin subtítulos** (formato mudo). La voz se escribe después, sobre los `.secciones.json`, con `voz_curso.py`/`guiones.py --proveedor edge`.
- **SIN «Modulo 0N»**: `hud_modulo()` existe en el `style_block` solo para ABORTAR. Lo único fijo en pantalla es la marca de agua y las escuadras de la marca.

Lo que puede haber en pantalla (el guardián `_vigilar()` aborta el render si un rótulo se vuelve frase):

| Elemento | Helper | Límite |
|---|---|---|
| Título del clip (arriba) | `titulo_curso()` | ≤ 6 palabras |
| Rótulo de mobiliario (ejes, `I`, `Q`, `LNA`, `MHz`) | `tag_junto()` | ≤ 4 palabras |
| **Cifra calculada aquí** (cian) | `cifra_pie()` / `tag_hud()` | ≤ 5 palabras |
| Columna de cifras | `panel_cifras()` | ≤ 5 por línea |
| Dato de norma / hoja de datos / parámetro elegido (gris) | `dato_pie()` / `tag_dato()` | ≤ 5 palabras |
| Bits y bytes decodificados | `S.bits(...)` / `tag_hud(color=C_OK)` | ASCII |
| Fórmula | `formula_pie()` | una línea |
| Cierre del clip 4 | `cierre_leccion()` | 2 líneas |

## 3. Ángulo editorial

**Una radio es una cadena de aritmética, y cada eslabón deja una huella que se puede medir.** El curso sigue la señal desde la antena hasta el dato decodificado: el hardware (lo que el aparato barato hace mal), el canal (cómo se aísla una emisora del flujo), la sincronización (cómo se le quita al receptor su propio error) y, al final, señales reales de punta a punta —la FM estéreo con su RDS, los aviones, los barcos, los sensores LoRa, el satélite meteorológico, el GPS—.

Arco: empieza con «38.4 megabits por segundo salen de un aparato de 30 dólares» (1.1) y termina con la estación completa, que convierte ese caudal en una imagen del planeta (8.3).

## 4. Público y qué asume

Público general de YouTube con curiosidad técnica: sabe qué es una onda y una frecuencia, ha oído «megahercio» y quizá tiene un RTL-SDR en un cajón. **No** asume que vio ningún curso previo de la colección, pero no re-explica lo que ya explicaron (ver §5): lo **usa** con un dibujo de un segundo y sigue.

- Cada término (mezclador, cero-IF, figura de ruido, NCO, diezmar, Costas) se **enseña con el dibujo antes de nombrarse**.
- Nada de marcas en pantalla más allá del nombre genérico del hardware (RTL-SDR, HackRF, que son nombres de proyecto) como `dato_pie`.
- **Transmitir tiene reglas**: la lección 8.1 lo dice con un `dato_pie` («requiere licencia»), sin sermón.

## 5. Qué NO pisa

| Curso vecino | Qué queda allí | Qué hace este |
|---|---|---|
| 8 · SDR: la radio hecha software | la idea de SDR, I/Q como fasor, aliasing, elegir N, leer un waterfall, AM/FM en una línea, BPSK y el ojo **a nivel divulgación** | lo **usa**: el waterfall y el plano IQ son herramientas, no temas. Donde el 8 dijo «la FM se demodula con la fase», aquí se construye el discriminador y se mide |
| 24 · Comunicaciones digitales | modulaciones, BER, códigos (Viterbi, LDPC), Doppler de un pase LEO como cifra, PN | lo **usa**: Viterbi es una caja en 7.2; el Doppler de 7.1 se CORRIGE en el receptor, no se explica su origen |
| 27 · Procesamiento de señales | filtros FIR/IIR, CIC, polifase, PLL genérico, FFT | lo **usa**: 3.2 aplica la cadena de diezmado a un canal real sin rediseñar filtros; 5.2 construye el lazo de Costas, que es lo específico |
| 9 · Apuntado / 30 · Sistemas ATP | seguir el satélite con la antena | no se toca el apuntado |
| 25 · Protocolos de Internet | tramas y CRC como concepto | el CRC se usa para validar paquetes (ADS-B, AIS), sin explicar su álgebra |

## 6. Principio visual no negociable

1. **El espectro está vivo.** Casi toda lección tiene un espectro o un waterfall que REACCIONA a lo que se hace: sintonizar lo desliza, filtrar lo recorta, diezmar lo estrecha, un error de reloj lo corre. Se dibuja siempre desde arrays calculados (`S.espectro_db`), nunca como campana decorativa.
2. **El plano IQ es la vista nativa del receptor.** Los desbalances, los desfases y los relojes se ven como deformaciones de una constelación: elipse, giro, nube.
3. **La cadena**: la lección que toca un eslabón lo enseña encendido dentro de la cadena `S.Cadena` (antena → LNA → mezclador → filtro → ADC → software) en su clip 1, una vez, sin volverla un rótulo fijo.
4. **La señal real se construye a norma y se decodifica en pantalla**: el resultado (el nombre de la emisora, el ICAO del avión, la posición del barco, la línea de imagen) aparece en **verde** al final de la cadena. Si la librería decodifica mal, el clip no existe.
5. **Cian = medido aquí; gris = la norma** (19 kHz del piloto, 1090 MHz, 9600 baudios). Nunca al revés.

## 7. Mapa de lecciones

| Lección | Proyecto | 4 clips |
|---|---|---|
| **Módulo 1 · El receptor por dentro** |||
| 1.1 | De la antena al número | la cadena · una ventana que se mueve · ocho bits · el caudal |
| 1.2 | Mezclar es multiplicar | suma y diferencia · la frecuencia imagen · el mezclador complejo · I y Q separan los lados |
| 1.3 | Las cicatrices del cero-IF | el pico del centro · I y Q desiguales · corregir el desbalance · sintonizar al lado |
| **Módulo 2 · Ganancia y ruido** |||
| 2.1 | El piso de ruido | kTB · la cascada de Friis · la sensibilidad · el LNA en la antena |
| 2.2 | La ganancia justa | poca ganancia · demasiada ganancia · el punto dulce · el control automático |
| 2.3 | Señales que saturan | intermodulación · la recta de 3 a 1 · el bloqueo · el filtro de banda |
| **Módulo 3 · Del flujo al canal** |||
| 3.1 | Sintonizar en software | el oscilador numérico · mover el espectro · tres receptores en uno · la fase continua |
| 3.2 | Filtrar y diezmar | el filtro de canal · diezmar sin filtro · la cascada · de 2.4 M a 48 k |
| 3.3 | El reloj que miente | las ppm · medir el error · la deriva · corregir |
| **Módulo 4 · FM de radiodifusión** |||
| 4.1 | El discriminador | la velocidad del fasor · el discriminador polar · Carson · el deénfasis |
| 4.2 | El múltiplex estéreo | el espectro del MPX · el piloto · L y R · el precio del estéreo |
| 4.3 | RDS: el texto escondido | 57 kHz · la fase que salta · bloques y síndrome · el nombre de la emisora |
| **Módulo 5 · Sincronizar** |||
| 5.1 | La constelación que gira | el giro · a la cuarta potencia · la estimación · lo que queda |
| 5.2 | El lazo de Costas | el detector · enganchar · el ancho del lazo · la ambigüedad de 180 |
| 5.3 | El reloj de símbolo | muestrear a destiempo · el detector de Gardner · el lazo converge · la nube se aprieta |
| **Módulo 6 · Paquetes en el aire** |||
| 6.1 | ADS-B: aviones | pulsos a 1090 · el preámbulo · 112 bits · el avión |
| 6.2 | AIS: barcos | GMSK a 9600 · NRZI · la bandera y el relleno · el barco |
| 6.3 | LoRa: chirps | el chirp · quitar el chirp · el factor de dispersión · bajo el ruido |
| **Módulo 7 · Satélites** |||
| 7.1 | El Doppler de un pase | la curva · el receptor la sigue · la tasa · lo que queda |
| 7.2 | Meteor: del QPSK a la imagen | 72 k símbolos · la palabra de sincronía · Viterbi · la imagen |
| 7.3 | GPS bajo el ruido | la señal no se ve · el código C/A · la rejilla · el pico |
| **Módulo 8 · Más allá de escuchar** |||
| 8.1 | Transmitir | el DAC · las imágenes · la máscara · la licencia |
| 8.2 | Dos antenas: de dónde viene | la diferencia de fase · el ángulo · la ambigüedad · el barrido |
| 8.3 | La estación completa | la cadena entera · el presupuesto · el pase · la imagen |

## 8. Paleta por ROL

| Alias (style_block) | Color | Papel |
|---|---|---|
| `C_CALCULO` | `#22d3ee` cian | **cifra calculada aquí** (medida sobre la señal que se dibuja) |
| `C_SENAL` | `#f59e0b` ámbar | LA SEÑAL que se quiere recibir: su espectro, su traza, su fasor |
| `C_I` / `C_Q` | `#3b82f6` azul / `#a78bfa` violeta | componentes I y Q |
| `C_LO` | `#e879f9` fucsia | lo que PONE el receptor: oscilador local, NCO, reloj, lazo |
| `C_RUIDO` | `#f43f5e` rojo | ruido, imagen, espurio, interferente, error, bit equivocado |
| `C_OK` | `#34d399` verde | lo recuperado: audio, bits correctos, el dato decodificado |
| `C_DATO` | `#94a0b0` gris | norma, hoja de datos o parámetro ELEGIDO de la simulación |
| `C_TITULO` / `C_TENUE` | tinta / gris | texto y mobiliario |

Regla: **el cian es solo lo medido aquí**. Una frecuencia de norma (1090 MHz) va en gris aunque aparezca junto a una cifra medida.

## 9. Contrato de la librería `sdr.py`

Sustrato que reutiliza (no duplica): `algebra_lineal` (`_Anclada`, `fmt`), `comunicaciones` (`PlanoIQ`, `Onda`, `DiagramaOjo`, constelaciones, `awgn`), `dsp` (`Escalera`, `Espectrograma`, `pll`), `bloques` (`bloque`, `conectar`, `flujo`). `scipy.signal` solo como ORÁCULO en la sonda, nunca como implementación de lo que el clip enseña funcionando.

Convenciones: señales complejas en banda base `np.complex128`; `fs` en Hz; espectros con `espectro_db(x, fs, nfft, ventana)` → `(f, db)` con `f` centrada (fftshift) y `db` relativo al máximo o a una referencia dada. Semillas fijas en todas partes.

Funciones y piezas por lote (se amplía al empezar cada lote; lo que está aquí es lo que la sonda ya validó):

### Lote 1 (módulos 1–2)

Numérica:
- `RTL` — dict de la hoja de datos (gris): `fs=2.4e6`, `bits=8`, `rango=(24e6, 1766e6)`.
- `caudal_bps(fs, bits, canales=2)` → 38.4e6; `caudal_audio()` → 0.768e6; `reduccion()` → 50.
- `banda_fm(semilla)` → emisoras sintéticas de 88–108 MHz (frecuencias en múltiplos de 200 kHz y niveles); `emisoras_en(ventana_centro, fs)` → las que caen dentro.
- `sqnr_adc(bits, n, semilla)` → SQNR MEDIDA de un seno a fondo de escala (≈ 6.02 b + 1.76).
- `mezclar_real(f1, f2, fs, n)` / `mezclar_complejo(...)` → espectros con las líneas medidas en suma/diferencia.
- `imagen_real(f_lo, f_if)` → las dos frecuencias que caen en la misma FI.
- `desbalance_iq(x, eps, phi)`, `irr_db(eps, phi)` (fórmula) y `irr_medida(x)` (sobre el espectro de un tono: lado/imagen) — deben coincidir.
- `corregir_iq(x)` → estimación ciega por momentos (Gram-Schmidt); IRR medida después.
- `dc_spike(x, nivel)` y `quitar_dc(x, alfa)`.
- `ktb_dbm(b_hz, t=290)` → −174 dBm/Hz + 10 log B; `friis(etapas)` → NF de la cascada; `sensibilidad_dbm(b, nf, snr_min)`.
- `snr_vs_ganancia(ganancias_db, ...)` → curva medida por simulación (ruido térmico + cuantización a 8 bits + recorte); `punto_dulce(...)`.
- `im3(a, iip3)`, `recta_ip3(...)` medida simulando un amplificador polinómico con dos tonos; `bloqueo(...)`.

Dibujo:
- `Cadena(eslabones, encendido=None)` — la cadena de bloques; `.encender(i)`.
- `Espectro(f, db, piso, ancho, alto, color)` — curva + área sobre marco propio (no `Axes`); gemela `.con_db(db2)`; `.en(f, db)`, `.marca_f(f)`, `.banda(f0, f1)`.
- `Waterfall(filas_db, ancho, alto)` — raster (Group, nunca VGroup).
- `Medidor(ancho, alto)` — barra de nivel dBFS con zona de recorte.

## 10. Lotes

| Lote | Módulos | Lecciones | Aporta a la librería | Estado |
|---|---|---|---|---|
| 1 | 1–2 | 1.1–2.3 | hardware, mezcla, IQ, ruido, ganancia, IM3 | ~ en curso |
| 2 | 3–4 | 3.1–4.3 | NCO, diezmado, ppm, FM, MPX, RDS | — |
| 3 | 5–6 | 5.1–6.3 | Costas, Gardner, ADS-B, AIS, LoRa | — |
| 4 | 7–8 | 7.1–8.3 | Doppler, LRPT, GPS C/A, TX, DOA, cierre | — |

## 11. Receta de lote

1. Ampliar `sdr.py` y la sonda; sonda verde en el contenedor (invariante + contraejemplo por función; scipy como oráculo).
2. Molde (lote 1: 1.1 del orquestador; lotes siguientes: la primera lección del lote también del orquestador si trae pieza de dibujo nueva).
3. Stubs de las lecciones del lote (`curso.json` + `style_block.py` del molde con su cabecera y su bloque de números + 4 stubs).
4. Subagentes **Sonnet** (Opus para 5.2, 5.3, 7.2, 7.3 y 8.3), olas de 2–3, contrato en el scratchpad.
5. Revisión de frames del orquestador; otra vuelta si hace falta.
6. `pytest -q`, PR, merge.
7. `qh` local ×3 → `render_jobs/qh/`; guion de voz; síntesis edge local; mux con la marca; picos.

## 12. Tablero de estado

Leyenda: — pendiente · ~ en curso · ✔ hecho.

| Lección | plan | clips | ql ✔ frames | PR | qh | voz | mux |
|---|---|---|---|---|---|---|---|
| 1.1 | ✔ | ✔ | ✔ | — | — | — | — |
| 1.2 | ✔ | — | — | — | — | — | — |
| 1.3 | ✔ | — | — | — | — | — | — |
| 2.1 | ✔ | — | — | — | — | — | — |
| 2.2 | ✔ | — | — | — | — | — | — |
| 2.3 | ✔ | — | — | — | — | — | — |
| 3.1 | ~ | — | — | — | — | — | — |
| 3.2 | ~ | — | — | — | — | — | — |
| 3.3 | ~ | — | — | — | — | — | — |
| 4.1 | ~ | — | — | — | — | — | — |
| 4.2 | ~ | — | — | — | — | — | — |
| 4.3 | ~ | — | — | — | — | — | — |
| 5.1 | ~ | — | — | — | — | — | — |
| 5.2 | ~ | — | — | — | — | — | — |
| 5.3 | ~ | — | — | — | — | — | — |
| 6.1 | ~ | — | — | — | — | — | — |
| 6.2 | ~ | — | — | — | — | — | — |
| 6.3 | ~ | — | — | — | — | — | — |
| 7.1 | ~ | — | — | — | — | — | — |
| 7.2 | ~ | — | — | — | — | — | — |
| 7.3 | ~ | — | — | — | — | — | — |
| 8.1 | ~ | — | — | — | — | — | — |
| 8.2 | ~ | — | — | — | — | — | — |
| 8.3 | ~ | — | — | — | — | — | — |

(`plan ~` = storyboard en borrador; se cierra al abrir su lote, cuando la sonda ya dio las cifras.)

## 13. Storyboard

Convenciones: «cian» = `cifra_pie`/`tag_hud` con una función de `S`; «gris» = `dato_pie`/`tag_dato`. Los números citados aquí son los que devuelve hoy la librería: en el clip **se leen de la librería, nunca se escriben**. Duración 28–45 s. Cada clip 4 cierra a pantalla limpia con dos líneas (la segunda cian).

### Módulo 1 · El receptor por dentro

#### 1.1 De la antena al número
Intención: el espectador sale sabiendo que un SDR es una ventana de ancho `fs` que se desliza por el espectro y la convierte en un chorro de números de 8 bits, y cuántos son.
1. **La cadena** — `S.Cadena` entra eslabón a eslabón: ANTENA → LNA → MEZCLADOR (con su LO fucsia) → FILTRO → ADC → USB. Todo lo que está a la derecha del ADC se tiñe: «software». Gris: `24-1766 MHz`, `2.4 MS/s`, `8 bits` (hoja de datos del RTL-SDR).
2. **Una ventana que se mueve** — el espectro de la banda FM (88–108 MHz, emisoras sintéticas de `banda_fm`) a todo el ancho; una ventana de 2.4 MHz (fucsia) se desliza al cambiar el LO; las emisoras dentro se encienden. Cian: «ancho = fs = 2.4 MHz» (con I y Q la ventana mide fs entero, no fs/2) y «N emisoras en la ventana».
3. **Ocho bits** — un seno entra al ADC y sale en escalera de 256 niveles (`Escalera` de `dsp`); el error de cuantización debajo. Cian: SQNR medida (`sqnr_adc(8)`) ≈ 49.9 dB; `formula_pie` 6.02 b + 1.76. Comparación con 12 bits (gemela) en el mismo cuadro.
4. **El caudal** — un contador cian sube hasta 38.4 Mbit/s (`caudal_bps`); abajo, el audio que sale al final: 0.768 Mbit/s; barra de 50× (`reduccion`). Cierre: «La radio termina en el ADC.» / «Lo demas es aritmetica.»

#### 1.2 Mezclar es multiplicar
Intención: mezclar es multiplicar y multiplicar mueve el espectro; con una sola rama (real) aparece la imagen; con I y Q, no.
1. **Suma y diferencia** — dos ondas (señal ámbar 100.3 MHz, LO fucsia 89.6 MHz, gris) se multiplican: se ven las dos ondas y su producto (tres `Onda` apiladas o una sola con el producto). Espectro del producto de 0 a 250 MHz (`S.mezclar_real()` + `S.para_dibujar`): dos rayas. Cian: `189.9 MHz` (suma) y `10.7 MHz` (diferencia) medidas. `formula_pie` cos a · cos b = ½[cos(a−b) + cos(a+b)]. La FI de 10.7 MHz es un dato (gris).
2. **La frecuencia imagen** — eje de RF con el LO (fucsia, 89.6) en medio y dos emisoras a ±10.7 MHz: la deseada 100.3 (ámbar) y la imagen 78.9 (rojo) (`S.imagen_real()`). Dos flechas bajan las dos a la MISMA raya de 10.7 MHz. Cian: la potencia de cada una en +FI (`S.mezcla_imagen(complejo=False)`): la imagen llega entera (−12.0 dB, su nivel de emisión −6 dB por debajo; lo que se rotula es «llega igual»: la diferencia medida 6.0 dB = su diferencia de origen).
3. **El mezclador complejo** — un fasor fucsia girando (el LO complejo, e^{-jωt}); el espectro de una captura compleja (`S.captura_banda(96.4e6)`) se DESLIZA entero con `S.desplazar` (gemelas `Espectro.con_db`): no aparece copia. Cian: el desplazamiento medido.
4. **I y Q separan los lados** — con LO complejo (`S.mezcla_imagen(complejo=True)`): la deseada cae en +10.7 y la imagen en −10.7; dos rayas en lados distintos del cero, frente al caso real donde las dos caen en ambos lados. Cierre: «Mezclar es mover el espectro.» / «Con I y Q, hacia un solo lado.»

#### 1.3 Las cicatrices del cero-IF
Intención: el receptor barato convierte directo a 0 Hz y eso deja dos huellas medibles —el pico en el centro y la imagen espejo— que el software cura.
Números: `XL, XN = S.senal_iq_prueba()` (tono en +180 kHz, SNR 45 dB); `S.con_dc(XN, -12)`; `S.quitar_dc`; `S.desbalance_iq(x, 0.05, 3.0)`; `S.irr_db()` = **28.9 dB**; `S.irr_corregida_minima()` → **80** («más de 80 dB»; la cifra exacta depende de la malla: NO se rotula).
1. **El pico del centro** — espectro de la captura con DC: raya en 0 Hz que no es emisora + el tono en +180 kHz. Cian: «pico DC: −12 dBc» (`S.dc_dbc(xdc, p_ref)`). `quitar_dc` lo hunde: gemela sin el pico; cian «−73.8 dBc» (`S.dc_dbc(yb, p_ref, desde=4000)`). Se rotula en dBc (relativo al tono, coherente: no depende de la malla), NUNCA como altura sobre el piso.
2. **I y Q desiguales** — plano IQ: el círculo del tono (puntos de XL) se vuelve elipse inclinada con `desbalance_iq`; espectro: aparece la imagen espejo en −180 kHz (rojo). Gris: «5 % y 3 grados». Cian: «IRR = 28.9 dB» (la fórmula y la medida coinciden: `irr_db` / `irr_medida`).
3. **Corregir el desbalance** — `corregir_iq`: la elipse vuelve a círculo (Transform entre gemelas de igual número de puntos), la imagen se hunde bajo el piso. Cian: «IRR: 28.9 → más de 80 dB».
4. **Sintonizar al lado** — el LO se corre 250 kHz (gris, parámetro): en el espectro el pico de DC y el canal quedan separados; una banda verde marca el canal (±100 kHz) que ya no contiene el pico; el NCO (fucsia) trae el canal a cero en software (`S.desplazar`). Cierre: «El hardware barato deja cicatrices.» / «El software las cura.»

### Módulo 2 · Ganancia y ruido

#### 2.1 El piso de ruido
Números: `S.ktb_dbm(1)` **−174.0 dBm/Hz**; en 2.4 MHz **−110.2**, en 200 kHz **−121.0**, en 2 kHz **−141.0**; cascada (gris: cable −3 dB/NF 3, LNA 20 dB/NF 0.8, receptor NF 6): `S.friis([S.LNA, S.CABLE, S.RECEPTOR])` **1.04 dB**, `S.friis([S.CABLE, S.LNA, S.RECEPTOR])` **3.91 dB**, `S.friis([S.CABLE, S.RECEPTOR])` **9.0 dB**; `S.sensibilidad_dbm(200e3, 1.04, 12)` **−107.9 dBm** (FM, SNR 12 dB gris), `S.sensibilidad_dbm(2e3, 1.04, 6)` **−133.9 dBm** (baliza); `S.snr_medida(-125, 2e3, nf)`: **14.9 dB** (LNA en la antena) vs **12.0 dB** (en el escritorio).
1. **kTB** — una barra/escala vertical de dBm; el piso cae en −174 dBm/Hz (`formula_pie` kTB, cian el valor); al ensanchar el ancho de banda el piso SUBE: tres escalones 2 kHz / 200 kHz / 2.4 MHz con sus cifras cian.
2. **La cascada de Friis** — tres cajas (CABLE, LNA, RECEPTOR) con sus parámetros en gris; se reordenan (animación de swap): LNA primero 1.04 dB vs cable primero 3.91 dB vs sin LNA 9.0 dB (barras de NF, cian).
3. **La sensibilidad** — escalera: piso kTB+10logB → +NF → +SNR mínima = sensibilidad; dos columnas (FM 200 kHz y baliza 2 kHz). Cian −107.9 y −133.9 dBm.
4. **El LNA en la antena** — misma señal de −125 dBm (gris) en 2 kHz: dos espectros/barras con la SNR medida 14.9 vs 12.0 dB. Cierre: «El ruido lo pone el primer eslabon.» / «Amplifica antes de perder.»

#### 2.2 La ganancia justa
Números: `G, SINAD = S.snr_vs_ganancia()` (ganancia 0–75 dB, la señal entra a −60 dBFS con ganancia 0; SNR de entrada 30 dB, gris); `S.punto_dulce(G, SINAD)` → tramo **48–60 dB**, centro **54 dB**, SINAD máx **30.3 dB**; SINAD con ganancia 0 **6.3 dB**, con 75 dB **8.2 dB**; `S.niveles_usados(...)` a −60 dBFS: **2** de 256; `S.espurio_max_dbc(66)` **−12.9 dBc** (vs `espurio_max_dbc(40)` −41.0); AGC `S.agc(S.desvanecimiento())`: entrada **30.7 dB** de variación → salida **3.0 dB**.
1. **Poca ganancia** — la onda casi plana ocupa 2 niveles de 256 (escalones gruesos sobre una rejilla de niveles); `S.Medidor` en −60 dBFS. Cian «2 de 256 niveles» y «SINAD 6.3 dB».
2. **Demasiada ganancia** — la onda se recorta en el techo del ADC (rojo); el espectro muestra espurios; cian «espurio: −12.9 dBc»; el medidor entra en la zona roja.
3. **El punto dulce** — la curva SINAD vs ganancia completa (cuadro propio), tramo óptimo sombreado verde; cian «48 a 60 dB» y «SINAD max 30.3 dB»; un punto recorre la curva y el medidor lo acompaña.
4. **El control automático** — envolvente que se desvanece (30.7 dB de variación, la entrada es parámetro elegido: gris) y la salida del AGC en una franja (cian «3.0 dB» a la salida). Cierre: «Ni tanta que recorte,» / «ni tan poca que se hunda.»

#### 2.3 Señales que saturan
Números: amplificador `y = 10x − x³` (gris, parámetros); `S.dos_tonos_im(a)`: tonos en 98.1/98.5 MHz (gris), productos en **97.7** y **98.9 MHz**; `S.recta_ip3()`: pendientes **1.00** y **3.00**, IIP3 **11.2 dB** (y `S.iip3_teorico()` 11.25, coinciden); `S.ganancia_debil(S.AMP_BLOQUEADOR) − S.ganancia_debil(0)` = **−11.2 dB** (desensibilización de una señal débil en 137.1 MHz), tras el filtro de 40 dB (`S.ATEN_FILTRO_DB`, gris): **0.0 dB**.
1. **Intermodulación** — espectro 96–100.5 MHz: dos tonos ámbar; al subir la entrada aparecen dos rayas rojas a los lados (gemelas del mismo `f`). Cian «97.7 MHz» y «98.9 MHz»; `formula_pie` 2f1 − f2.
2. **La recta de 3 a 1** — cuadro entrada (dB) vs salida (dB): puntos medidos de la fundamental y del IM3 (`recta_ip3`), las rectas ajustadas se prolongan hasta cruzarse (IIP3). Cian «pendiente 1.00», «pendiente 3.00», «IIP3 = 11.2 dB».
3. **El bloqueo** — una emisora de FM fuerte (98.1, ámbar grande) y un satélite débil en 137.1 MHz (verde); al encender la emisora, la raya del satélite baja: cian «−11.2 dB».
4. **El filtro de banda** — un filtro (rechaza 88–108, gris «40 dB») delante del amplificador; la emisora baja y el satélite vuelve: cian «0.0 dB de perdida». Cierre: «Lo fuerte tambien estorba.» / «Filtra antes de amplificar.»

### Módulo 3 · Del flujo al canal (borrador; se cierra con la sonda del lote 2)

- **3.1 Sintonizar en software** — el NCO como fasor fucsia; el espectro se desliza hasta poner la emisora en 0; tres NCO sobre la misma captura = tres receptores; un acumulador de fase que se reinicia por bloque deja un espurio (rojo) medido. Cierre: «Sintonizar ya no es girar un dial.» / «Es multiplicar por un fasor.»
- **3.2 Filtrar y diezmar** — filtro de canal sobre 2.4 MS/s; diezmar sin filtro pliega emisoras vecinas (rojo, medidas); la cascada CIC + FIR y su coste en MAC por muestra frente a un FIR único (cian); de 2.4 M a 48 k (×50). Cierre: «Primero se recorta,» / «despues se tira lo que sobra.»
- **3.3 El reloj que miente** — ppm → Hz a 100 MHz, 437 MHz y 1090 MHz (cian); medir el error con un tono conocido (interpolación parabólica de la FFT); la deriva térmica en un waterfall inclinado; corregir. Cierre: «El cristal miente un poco.» / «Una señal conocida lo delata.»

### Módulo 4 · FM de radiodifusión (borrador)

- **4.1 El discriminador** — la frecuencia es la velocidad del fasor; `angle(x[n]·conj(x[n−1]))` recupera el tono (cian: error medido); Carson para mono y estéreo (gris 75 kHz, cian el ancho); deénfasis 75 µs (gris) y el ruido de alta que baja (cian). Cierre: «La FM se oye en el angulo.» / «Una resta de fases basta.»
- **4.2 El múltiplex estéreo** — espectro del MPX sintetizado a norma (L+R, piloto 19 k, L−R en 38 k, RDS en 57 k, gris) medido; PLL al piloto ×2; matriz L/R y separación medida (cian); el estéreo cuesta SNR (cian). Cierre: «El estereo viaja escondido,» / «colgado de un piloto.»
- **4.3 RDS: el texto escondido** — 57 = 3×19 y 1187.5 = 57000/48 (gris); BPSK bifase; bloques de 26 bits con palabra de comprobación y síndrome medido; el nombre de la emisora decodificado en verde (`CODE FM`, sintético). Cierre: «La radio de siempre» / «lleva datos desde 1984.»

### Módulo 5 · Sincronizar (borrador)

- **5.1 La constelación que gira** — un desfase de frecuencia hace girar la QPSK; elevar a la cuarta potencia borra la modulación y deja una raya en 4Δf (cian: Δf estimado y error); lo que queda tras corregir, girando despacio.
- **5.2 El lazo de Costas** — detector I·Q para BPSK; transitorio de enganche medido; ancho del lazo: rápido y ruidoso vs lento y limpio (cian: tiempo de enganche y jitter); ambigüedad de 180° → codificación diferencial.
- **5.3 El reloj de símbolo** — muestrear a destiempo cuesta BER (cian, medido); curva S del detector de Gardner; el lazo converge (μ en el tiempo); EVM antes/después.

### Módulo 6 · Paquetes en el aire (borrador)

- **6.1 ADS-B** — PPM a 1 Mbit/s en 1090 MHz (gris), preámbulo de 8 µs por correlación, 112 bits con CRC-24 = 0 (cian), el ICAO y el indicativo decodificados en verde (sintéticos).
- **6.2 AIS** — GMSK a 9600 baudios en 161.975/162.025 MHz (gris), NRZI, bandera 0x7E y bits de relleno contados (cian), CRC-16 y la posición del barco en verde (sintética).
- **6.3 LoRa** — el chirp; multiplicar por el chirp conjugado lo vuelve un tono y la FFT da el símbolo; SF7→SF12 (cian: bits/símbolo, tiempo en el aire); decodificar a SNR negativa (cian: SNR medida y símbolo correcto).

### Módulo 7 · Satélites (borrador)

- **7.1 El Doppler de un pase** — la curva de Doppler de un pase a 437 MHz (se usa, no se explica: curso 24), el NCO la sigue desde la predicción, la tasa máxima (Hz/s), el residuo tras corregir (cian).
- **7.2 Meteor: del QPSK a la imagen** — Meteor-M N2-4, 137.9 MHz, 72 k símbolos/s (gris; NOAA APT se apagó en 2025, dato); Costas + reloj de 5.x; correlación con la palabra de sincronía 0x1ACFFC1D; Viterbi como caja; la imagen sintética se arma línea a línea en verde.
- **7.3 GPS bajo el ruido** — la señal C/A está ~20 dB bajo el piso (cian: SNR por muestra medida); código Gold de 1023 chips; rejilla Doppler × fase de código; el pico emerge (cian: ganancia de correlación).

### Módulo 8 · Más allá de escuchar (borrador)

- **8.1 Transmitir** — el DAC y sus imágenes a múltiplos de fs; el filtro de reconstrucción; la máscara espectral (gris); `dato_pie` «requiere licencia».
- **8.2 Dos antenas: de dónde viene** — diferencia de fase entre dos antenas a λ/2; ángulo de llegada medido; la ambigüedad si d > λ/2; barrido.
- **8.3 La estación completa** — la cadena del 1.1 entera, encendida eslabón a eslabón con la cifra que cada lección midió; presupuesto de enlace de Meteor; el pase y la imagen final. Cierre del curso.

## 14. Cosecha heredada (lo que más riesgo tiene aquí)

- **La malla decide** (curso 27): la profundidad de un nulo, el rechazo de una imagen ideal o un espurio que depende de nfft no se rotulan; se rotula lo que no se mueve al cambiar la malla (y la IRR con desbalance real sí es estable: se comprueba en la sonda con dos nfft).
- Espectros de la misma pieza con distinto número de bins **no son gemelos** (no Transform).
- `EspectroArea`/`Axes` cruzan por el origen: los espectros de esta familia se dibujan en marco propio (`S.Espectro`).
- `set_opacity` enciende el fill de las polilíneas: encender/apagar curvas con `set_stroke(opacity=)`.
- Los contadores con `become` fuera de `play`, ancho fijo.
- Rajdhani < 22 px junta palabras: rótulos de varias palabras con `tag_hud` o ≥ 22 px.
- Una demo que solo funciona con una semilla no es una demo: la sonda barre semillas en cada decodificador (RDS, ADS-B, AIS, LoRa, GPS).
- Los agentes Sonnet dibujan pequeño y arriba y aprueban su propio trabajo (curso 37): revisar SIEMPRE sus fotogramas; el contrato exige «llena el cuadro».

## 15. Cosecha de trampas del lote 1

(se escribe durante la producción)

## 16. Hitos globales

- 2026-09-24 · plan y rama `curso/sdr-completo`.
