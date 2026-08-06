# Curso 04 — SDR: la radio hecha software

- **Proyecto**: name `SDR: la radio hecha software`, quality `qh`.
- **Fuente**: Academy, curso Estaciones terrenas y SDR L3 (muestreo IQ,
  aliasing, rango dinamico), L4 (FFT, ventaneo, waterfall, firma
  Doppler), L5 (demodulacion AM/FM), L6 (demodulacion digital, BPSK,
  constelacion, diagrama de ojo, efecto acantilado).
- **Slug**: `sdr-la-radio-hecha-software`.
- **Publico**: divulgacion; continua el curso publicado «Señales y
  espectro» (el espectador ya vio Fourier y el espectro).
- **Hilo narrativo**: el hardware se vuelve codigo → I y Q → la ventana
  del espectro y el aliasing → la FFT y su compromiso → leer el
  waterfall → demodular con modulo y fase → decidir bits (BPSK,
  constelacion, acantilado) → el diagrama de ojo y cierre.

## Paleta del curso

| Constante | Valor | Rol |
|-----------|-------|-----|
| `C_SENAL` | `#f59e0b` ambar | LA SEÑAL: ondas, picos, trazas, fasor |
| `C_I` | `#22d3ee` cian | componente I, envolvente, lo digital "uno" |
| `C_Q` | `#a78bfa` violeta | componente Q, FM, lo digital "cero" |
| `C_RUIDO` | `#f43f5e` rojo | ruido, alias fantasma, bits errados |
| `C_OK` | `#34d399` verde | mensaje recuperado, enlace vivo |
| `C_EJE` | `#31414f` | mobiliario: ejes, ventanas, cortes |

Regla de color: la SEÑAL es ambar, I cian, Q violeta, el RUIDO y sus
fantasmas rojos, lo RECUPERADO verde. No mezclar roles.

## Contrato de la libreria `studio/content/manim_extensions/radio.py`

Determinista (numpy con semilla explicita), sin red, sin archivos.
Armoniza con senal.py / bloques.py. Topes: `TRAZAS_MAX = 60`,
`PUNTOS_MAX = 80`. El waterfall es raster (`ImageMobject`): en los clips
va SIEMPRE en `Group`, nunca en `VGroup`.

```python
# --- plano IQ y fasor -------------------------------------------------
plano_iq(radio=1.7, color=C_EJE, font_size=16)
    # -> VGroup: ejes I (horizontal) / Q (vertical) con circulo unitario
    #    punteado y etiquetas "I", "Q". Atributo .radio_u (float, radio
    #    del circulo en unidades de escena) y metodo
    #    .punto(angulo, r=1.0) -> np.array en coords de escena.
fasor(plano, angulo=0.0, r=1.0, color="#f59e0b")
    # -> VGroup flecha desde el centro del plano hasta
    #    plano.punto(angulo, r) + punto brillante en la punta.
    #    Atributos .plano y .angulo (se actualiza al girar).
girar_fasor(fasor_, hasta, run_time=2.0)
    # -> Animation: lleva el fasor de su angulo actual a `hasta`
    #    (radianes; el signo de la diferencia da el sentido de giro),
    #    rotando alrededor del centro de su plano.

# --- ondas ------------------------------------------------------------
onda_senoidal(ancho=4.4, alto=0.5, ciclos=3.0, fase=0.0,
              color="#f59e0b", muestras=0)
    # -> VGroup curva senoidal; si muestras>0 añade esa cantidad de
    #    puntitos equiespaciados sobre la curva. Atributos .curva,
    #    .puntos (VGroup, vacio si muestras=0).
onda_am(ancho=5.6, alto=1.1, ciclos_portadora=26.0, ciclos_mensaje=2.0,
        indice=0.55, color="#f59e0b", color_envolvente="#22d3ee")
    # -> VGroup portadora modulada en amplitud + curva de envolvente
    #    superior. Atributos .portadora, .envolvente.
onda_fm(ancho=5.6, alto=1.1, ciclos_base=18.0, desviacion=0.65,
        ciclos_mensaje=1.5, color="#a78bfa")
    # -> VGroup onda de frecuencia instantanea variable (mas apretada
    #    donde el mensaje sube). Atributo .onda.
flujo_en_bloques(ancho=6.6, alto=0.65, bloques=5, ciclos=11.0,
                 color="#f59e0b", color_corte="#31414f")
    # -> VGroup onda continua + (bloques-1) lineas de corte verticales
    #    punteadas equiespaciadas. Atributos .onda, .cortes (VGroup).

# --- espectro ---------------------------------------------------------
ventana_espectro(ancho=6.8, alto=2.3, color="#31414f", font_size=15)
    # -> VGroup: eje horizontal de frecuencia con zona sombreada
    #    [-fs/2, +fs/2], marcas y etiquetas "-fs/2", "sintonia" (marca
    #    central punteada), "+fs/2". Metodo .x_de(f_rel) -> coordenada x
    #    de escena para f_rel en [-1, 1]; atributo .base_y (float).
pico_espectral(ventana, f_rel=0.0, altura=1.5, ancho_rel=0.06,
               color="#f59e0b")
    # -> VMobject campana suave (gaussiana) apoyada en el eje de la
    #    ventana, centrada en f_rel. Se anima con .move_to usando
    #    ventana.x_de().
barras_espectro(alturas, ancho=2.9, alto=1.8, color="#f59e0b",
                separacion_rel=0.25)
    # -> VGroup linea base + barras verticales (alturas en [0, 1]).
    #    Atributo .barras. Sirve para comparar N chico (pocas barras
    #    anchas) vs N grande (muchas finas).

# --- waterfall (raster) -----------------------------------------------
waterfall_imagen(ancho=6.2, alto=3.3, columnas=220, filas=120, semilla=7)
    # -> ImageMobject de un waterfall sintetico: fondo de ruido azul
    #    oscuro con 4 firmas embebidas y colormap negro->azul->ambar->
    #    blanco. Firmas (f_rel en [-1, 1], t_rel en [0, 1] top->down):
    #      CW: linea vertical fina en f_rel=-0.55
    #      FM ancha: banda con textura, centro -0.12, semiancho ~0.10
    #      AFSK: rafagas intermitentes cortas en +0.32
    #      Doppler: traza inclinada de (f_rel +0.72, t_rel 0) a
    #               (+0.38, 1), cruzando +0.55 a media altura
    #    El mobject expone .pos_de(f_rel, t_rel) -> np.array de escena
    #    (sigue al mobject si se mueve), para colocar tags y recuadros.

# --- digital ----------------------------------------------------------
constelacion_bpsk(plano, separacion=1.05, ruido=0.06, puntos=26,
                  semilla=3, color_uno="#22d3ee", color_cero="#a78bfa")
    # -> VGroup dos nubes de puntos gaussianas centradas en
    #    (+separacion, 0) y (-separacion, 0) del plano (unidades del
    #    plano). Atributos .nube_uno, .nube_cero y .errados: lista de
    #    puntos (Dots) cuya I cruzo el cero con ese ruido/semilla.
curva_acantilado(ancho=3.2, alto=2.2, umbral_rel=0.45, color="#f59e0b")
    # -> VGroup ejes minimos (SNR ->, errores ^) + curva monotona que se
    #    desploma alrededor del umbral. Atributos .ejes, .curva y metodo
    #    .punto_en(x_rel) -> np.array sobre la curva (x_rel en [0, 1]).
diagrama_ojo(ancho=4.8, alto=2.5, trazas=22, ruido=0.05, semilla=5,
             color="#f59e0b")
    # -> VGroup trazas superpuestas de 2 simbolos de ancho (transiciones
    #    coseno alzado entre bits pseudoaleatorios + ruido). Atributo
    #    .trazas. Con ruido ~0.05 el ojo esta abierto; con ~0.30 se
    #    cierra. Determinista via semilla.
```

Demo obligatoria: `studio/content/animations/experimentacion/16-radio.py`
con `DemoRadio(Scene)` (~15 s): plano_iq + fasor girando, ventana con
pico movil, waterfall_imagen (en Group), constelacion limpia vs ruidosa
y diagrama de ojo abierto vs cerrado.

## Reglas duras para los clips

Identicas a los cursos 01-03 (ver `curso-01-redes-neuronales.md`): solo
`class ClipN(Scene)`; Rotulos para todo texto narrativo; un fenomeno por
clip; 28-45 s; determinismo; MathTex raw corto; solo paleta;
`# --- momento ---` por beat. El style_block ya importa todo el
contrato. El waterfall es ImageMobject: agrupar con `Group`, no
`VGroup`.

## Storyboard clip a clip

### Clip 1 — `1 · Una radio que es un programa` (escena `Clip1`, ~34 s)
Portada: `titulo_marca("SDR", 46)` + subtitulo ambar «la radio hecha
software». HUD `Modulo 01`. Titulo «Una radio que es un programa».
Arriba (y≈+1.0) cadena clasica: tres `bloque` grises-violeta en fila
«MEZCLADOR», «FILTRO», «DETECTOR» con `conectar`. Pie: «Antes: un
circuito para cada función. Cambiar de modo era cambiar el aparato.»
Acto 2: la cadena se desvanece; abajo (y≈-0.8) queda «ANTENA» →
`bloque("ADC", color=C_SENAL)` → `bloque("SOFTWARE", color=C_I,
ancho=2.6)`, con `flujo`. Pie: «La idea SDR: digitaliza lo antes
posible. El resto es código.» Acto 3: junto a SOFTWARE una
`etiqueta_hud` cambia en relevo (zona propia, misma posicion):
«137 MHz · METEO» → «437 MHz · CUBESAT» → «1090 MHz · AVIONES». Pie:
«El mismo aparato de 30 dólares. Solo cambia el programa.»
**final_state**: cadena ANTENA→ADC→SOFTWARE abajo con la etiqueta
1090 MHz; titulo y HUD.

### Clip 2 — `2 · I y Q: la señal hecha número` (escena `Clip2`, ~37 s)
Titulo «I y Q: la señal hecha número». Izquierda (x≈-3.2, y≈-0.2)
`plano_iq(radio=1.7)` con `fasor` en 35°. Derecha (x≈+3.0): dos
`onda_senoidal` apiladas — I cian (y≈+0.9, fase 0) y Q violeta
(y≈-0.9, fase pi/2), cada una con su etiqueta «I» / «Q» a la
izquierda. Pie: «El SDR entrega dos secuencias: la misma señal contra
dos relojes a 90 grados.» `formula_pie("z[n] = I[n] + j\\,Q[n]")`.
Acto 2: `girar_fasor` una vuelta lenta antihoraria; pie: «Cada pareja
(I, Q) es un número complejo: una flecha que gira.» Acto 3: el radio
del fasor pulsa (Indicate) → pie «Su largo es la amplitud...»; un Arc
ambar marca el angulo → «...su ángulo es la fase.» Acto 4:
`girar_fasor` media vuelta antihoraria con tag «sube» verde junto al
plano; luego media vuelta horaria con tag «baja» violeta (relevo).
Pie: «El sentido de giro separa lo que está encima de la sintonía de lo
que está debajo. Una sola onda no puede.»
**final_state**: plano IQ con fasor a la izquierda, ondas I y Q a la
derecha.

### Clip 3 — `3 · La ventana y el aliasing` (escena `Clip3`, ~33 s)
Titulo «Una ventana de 2.4 MHz». `ventana_espectro` centrada (y≈+0.1)
con etiquetas -fs/2 / sintonia / +fs/2; `pico_espectral` ambar en
f_rel=-0.25. Pie: «Muestrear abre una ventana: fs hertz de espectro
alrededor de la sintonía.» `formula_pie("B = f_s")`. Pie: «A 2.4
megamuestras por segundo: 2.4 MHz de radio de un solo vistazo.» Acto
2: el pico se desliza a la derecha (updater con ValueTracker sobre
f_rel −0.25→+0.85); al cruzar +1.0 su parte excedente REAPARECE por la
izquierda como pico rojo (segundo pico_espectral en f_rel equivalente
-1.15+2 = +0.85-2). Coreografia: pico real termina medio fuera del
borde derecho; fantasma rojo crece en -0.85..-0.95. Pie: «Lo que cae
fuera no desaparece: se pliega dentro. Eso es el aliasing.» El
fantasma pulsa (Indicate rojo). Pie cierre: «Filtra antes de
digitalizar... o verás señales que no existen.»
**final_state**: ventana con pico ambar medio salido por la derecha y
pico fantasma rojo plegado a la izquierda.

### Clip 4 — `4 · La FFT: elegir N` (escena `Clip4`, ~36 s)
Titulo «La FFT: elegir N». Arriba (y≈+1.5) `flujo_en_bloques` (onda
continua cortada en 5 bloques por lineas punteadas); una `llave` abajo
del segundo bloque: «N muestras». Pie: «El flujo se corta en bloques
de N muestras; cada bloque, una FFT.»
`formula_pie("\\Delta f = f_s / N")`. Acto 2: abajo dos
`barras_espectro` lado a lado — izquierda (x≈-2.9, y≈-1.2) 5 barras
anchas, derecha (x≈+2.9, y≈-1.2) 20 barras finas — con tags «N
pequeño» / «N grande» debajo (tag_junto). Pie: «N grande: bins más
finos. Se distingue mejor en frecuencia...» Acto 3: bajo el flujo, el
segundo corte se ensancha (los cortes del flujo se separan:
Transform a flujo_en_bloques con bloques=2) — pie: «...pero cada
bloque abarca más tiempo: lo rápido se emborrona.» HUD numerico
(etiqueta_hud junto a las barras finas): «N=2048 → Δf ≈ 1.2 kHz». Pie
cierre: «Ni grande ni pequeño es mejor: N se elige según lo que
quieras ver.»
**final_state**: flujo de 2 bloques arriba, dos espectros de barras
abajo con sus tags.

### Clip 5 — `5 · Leer el waterfall` (escena `Clip5`, ~38 s)
Titulo «Leer el waterfall». `waterfall_imagen` centrado (y≈+0.1),
aparece con FadeIn (va en `Group` con sus tags). Pie: «Cada línea, una
FFT. El tiempo cae, la frecuencia cruza, el color es potencia.» Acto
2: cuatro identificaciones en relevo — cada una: un
`SurroundingRectangle`/Rectangle fino ambar sobre la zona de la firma
(usar .pos_de) + pie:
1. rect sobre f_rel=-0.55: «Línea fina e inmóvil: una portadora.»
2. rect sobre la banda -0.12: «Banda gruesa que respira: FM de
   radiodifusión.»
3. rect sobre +0.32: «Trazos cortos e intermitentes: ráfagas de un
   cubesat.»
4. rect inclinado (Line gruesa translucida siguiendo la traza) sobre
   la firma Doppler: «Y la línea que se inclina: el Doppler de un
   pase. La firma de un satélite.»
Cada rect se retira (FadeOut) antes de que entre el siguiente. Acto 3:
el rect Doppler vuelve y pulsa; pie: «Una interferencia terrestre
jamás deriva así.» Cierre: pie «Leer esto en dos segundos: eso es
operar una estación.»
**final_state**: waterfall centrado con la traza Doppler resaltada en
ambar.

### Clip 6 — `6 · Demodular en una línea` (escena `Clip6`, ~36 s)
Titulo «Demodular en una línea». Arriba (y≈+1.2) `onda_am` (portadora
ambar, envolvente cian). Pie: «AM: el mensaje viaja en la amplitud.»
La envolvente se dibuja (Create) encima y pulsa. Pie: «Recuperarlo es
tomar el módulo de cada muestra.»
`formula_pie("|z| = \\sqrt{I^2 + Q^2}")`. Acto 2: abajo (y≈-1.3)
`onda_fm` violeta. Pie: «FM: el mensaje viaja en la frecuencia...»
`formula_pie("\\varphi[n] - \\varphi[n-1]")` — pie: «...y se recupera
restando la fase de muestras vecinas.» Acto 3: sobre la AM caen 3
picos rojos (Lines dentadas cortas sobre la envolvente) y la
envolvente se quiebra en esos puntos (segmentos rojos); sobre la FM
dos lineas horizontales punteadas verdes (el limitador) recortan la
onda. Pie: «El ruido golpea la amplitud: la AM lo sufre...» → «...la
FM lo recorta con un limitador y sigue limpia.» Tag verde «mensaje a
salvo» junto a la FM. **final_state**: AM arriba con quiebres rojos,
FM abajo con limitador verde y su tag.

### Clip 7 — `7 · Bits en el aire: decidir` (escena `Clip7`, ~36 s)
Titulo «Bits en el aire: decidir». Izquierda (x≈-2.9, y≈-0.1)
`plano_iq(radio=1.55)` + `constelacion_bpsk(ruido=0.05)`: nube cian en
+I con tag «1», nube violeta en -I con tag «0». Pie: «Digital no es
reproducir una onda: es decidir. ¿Cero o uno?» Linea de decision
vertical punteada por I=0 (DashedLine sobre el eje Q, ambar tenue).
Pie: «Dos puntos enfrentados — BPSK — y una frontera en medio.» Acto
2: ReplacementTransform a `constelacion_bpsk(ruido=0.28, semilla=3)`;
los puntos `.errados` se recolorean a rojo con Indicate. Pie: «El
ruido vuelve nubes los puntos. Cuando una muestra cruza la frontera,
ese bit muere.» Acto 3: derecha (x≈+3.1, y≈-0.1) `curva_acantilado` +
punto brillante que se desliza de x_rel 0.9 a 0.25 por la curva
(MoveAlongPath o updater con punto_en). Pie: «Sobre el umbral, casi
perfecto. Debajo, colapso: el efecto acantilado.» Cierre: pie «Por
eso el operador pelea por dos decibelios más, no por un waterfall
bonito.»
**final_state**: constelacion ruidosa con frontera a la izquierda,
curva acantilado con punto abajo del umbral a la derecha.

### Clip 8 — `8 · El diagrama de ojo` (escena `Clip8`, ~38 s)
Titulo «El ojo que vigila el enlace». `diagrama_ojo(ruido=0.05)`
centrado (y≈+0.3), construido con LaggedStart de sus trazas. Pie:
«Superpón todos los tramos de dos símbolos: aparece un ojo.» Acto 2:
`llave` vertical (direccion RIGHT) sobre la abertura central: «margen
contra el ruido»; se retira; `llave` horizontal (direccion DOWN) sobre
el ancho de la abertura: «margen contra el reloj» (relevo, nunca
ambas). Pies sincronizados: «Su altura: cuánto ruido tolera cada
decisión.» → «Su anchura: cuánto puede errar el instante de
muestreo.» Acto 3: ReplacementTransform a `diagrama_ojo(ruido=0.30)`:
el ojo se cierra. Pie: «Ojo cerrado: ningún decodificador te salva.»
Vuelve a abrirse (Transform de regreso a ruido=0.05, color final
C_OK). Pie: «Ojo abierto: el enlace vive.» Todo se desvanece →
tarjeta de cierre: `titulo_marca("SDR", 46)` + subtitulo ambar «la
radio hecha software» + subrayado `con_brillo`. `self.wait(2)`.
**final_state**: tarjeta de cierre del curso centrada, pantalla limpia
salvo esquinas HUD y marca de agua.

## Descripcion del proyecto (campo description)

Curso de divulgación en 8 clips sobre radio definida por software: de la
cadena de circuitos al código, el muestreo IQ y el fasor, la ventana de
espectro y el aliasing, la FFT y su compromiso tiempo-frecuencia, la
lectura del waterfall, la demodulación AM/FM con módulo y fase, la
decisión digital con BPSK y su constelación, y el diagrama de ojo.
Estilo 3Blue1Brown en español.
