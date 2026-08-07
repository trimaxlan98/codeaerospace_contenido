# Curso 06 — El espectro: la guerra invisible por las ondas

- **Proyecto**: name `El espectro: la guerra invisible por las ondas`,
  quality `qh`.
- **Fuente**: Academy, curso Espectro y regulacion satelital L1 (recurso
  finito), L2 (mapa de bandas UHF→Q/V), L3 (propagacion, lluvia,
  ventanas atmosfericas), L4 (UIT y Reglamento), L6 (NGSO-GSO, 22.2,
  epfd) y pincelada de L8 (CMR-27).
- **Slug**: `el-espectro-la-guerra-invisible-por-las`.
- **Publico**: divulgacion; conecta con los cursos publicados de
  Señales y espectro y SDR.
- **Hilo narrativo**: el recurso que no se fabrica → el mapa de bandas
  → el impuesto de la lluvia → las ventanas atmosfericas → la UIT como
  arbitro → el anillo lleno (NGSO vs GSO) → epfd: medir el daño donde
  duele → CMR-27 y cierre.

## Paleta del curso

| Constante | Valor | Rol |
|-----------|-------|-----|
| `C_ONDA` | `#f59e0b` ambar | la señal, el espectro util, las bandas |
| `C_GSO` | `#22d3ee` cian | el GSO, lo establecido, la victima protegida |
| `C_NGSO` | `#a78bfa` violeta | las constelaciones NGSO, lo nuevo que llega |
| `C_PERDIDA` | `#f43f5e` rojo | lluvia, absorcion, interferencia |
| `C_OK` | `#34d399` verde | ventana atmosferica, coexistencia lograda |
| `C_EJE` | `#31414f` | mobiliario |

Regla de color: la ONDA/banda es ambar, el GSO cian, el NGSO violeta,
la PERDIDA/interferencia roja, la VENTANA/solucion verde.

## Contrato de la libreria `studio/content/manim_extensions/espectro.py`

Determinista, sin red, sin archivos. Armoniza con radio.py/apuntado.py
(mismo estilo: subclases VGroup con localizadores que leen la geometria
actual). Topes: `BANDAS_MAX = 10`, `SATS_MAX = 48`.

```python
# --- el mapa de bandas ------------------------------------------------
barra_bandas(ancho=6.8, alto=0.8, font_size=15)
    # -> BarraBandas(VGroup): barra horizontal segmentada con las 8
    #    bandas satelitales (UHF, L, S, C, X, Ku, Ka, Q/V) a escala
    #    logaritmica de frecuencia, cada segmento con su etiqueta HUD
    #    encima y su rango en GHz debajo (font pequeño). Alturas de
    #    segmento proporcionales al ancho de banda tipico (visual: los
    #    segmentos altos "ofrecen mas"). Metodo .segmento(nombre) ->
    #    VGroup del segmento (para Indicate/colorear) y
    #    .centro_de(nombre) -> np.array.

# --- propagacion ------------------------------------------------------
curva_gases(ancho=6.0, alto=2.6, color="#f43f5e", color_ejes="#31414f",
            font_size=14)
    # -> CurvaGases(VGroup): ejes (frecuencia 1-100 GHz log ->,
    #    atenuacion ^) con la curva de absorcion gaseosa: crecimiento
    #    suave + pico de H2O en 22 GHz + muro de O2 en 60 GHz.
    #    Metodo .punto_de(f_ghz) -> np.array sobre la curva. Atributos
    #    .curva, .ejes y .ventanas: lista de 2 zonas verdes translucidas
    #    (las ventanas atmosfericas bajo la curva, inicialmente
    #    opacity 0 para FadeIn).
curva_lluvia(ancho=5.6, alto=2.4, color="#f43f5e", color_ejes="#31414f",
             font_size=14)
    # -> CurvaLluvia(VGroup): ejes (frecuencia ->, dB/km ^) con DOS
    #    curvas de atenuacion especifica por lluvia (R=20 mm/h tenue y
    #    R=60 mm/h plena) creciendo con la frecuencia. Metodo
    #    .punto_de(f_ghz, intensa=True) -> np.array. Atributos .suave,
    #    .intensa, .ejes.
gotas_y_onda(lambda_rel=1.0, ancho=3.0, alto=1.6, color="#f59e0b",
             semilla=5)
    # -> VGroup: una senoidal horizontal (longitud de onda visual
    #    proporcional a lambda_rel) atravesando un campo de ~14 gotas
    #    (Dots azul-gris deterministas). Con lambda_rel=1.0 la onda es
    #    larga frente a las gotas; con 0.15 es comparable (choca).
    #    Atributos .onda, .gotas.

# --- la geometria orbital --------------------------------------------
tierra_y_anillos(radio_tierra=0.85, radio_gso=2.75, radio_ngso=1.55,
                 sats_gso=14, sats_ngso=10, font_size=14)
    # -> TierraAnillos(VGroup): disco terrestre (circulo azul-gris con
    #    meridianos sugeridos), anillo GSO punteado con sats_gso puntos
    #    cian equiespaciados, anillo NGSO punteado con sats_ngso puntos
    #    violeta. Metodos .pos_gso(deg) / .pos_ngso(deg) -> np.array
    #    (0 = derecha, antihorario) y .estacion(deg) -> np.array sobre
    #    la superficie terrestre. Atributos .tierra, .anillo_gso,
    #    .anillo_ngso, .sats_gso, .sats_ngso (VGroups).
haz(origen, destino, semiancho=0.16, color="#22d3ee")
    # -> VMobject cono translucido (Polygon suave) desde `origen` que
    #    se abre hasta `destino` con semiancho relativo en el extremo.
    #    Para dibujar el enlace estacion->GSO y el cruce NGSO.

# --- el patron de antena ---------------------------------------------
patron_antena(ancho=3.4, color="#22d3ee", font_size=14)
    # -> PatronAntena(VGroup): patron polar estilizado de una antena
    #    parabolica apuntando a la DERECHA: lobulo principal grande +
    #    4 lobulos laterales pequenos, dibujado como curva polar
    #    cerrada. Metodo .direccion(deg) -> np.array unitario rotado
    #    (0 = eje del lobulo principal). Atributos .principal (VMobject
    #    del contorno del lobulo mayor), .laterales.

# --- regulacion -------------------------------------------------------
linea_tiempo(hitos, ancho=6.4, color="#f59e0b", font_size=16)
    # -> LineaTiempo(VGroup): linea horizontal con len(hitos) muescas
    #    equiespaciadas; cada hito es (etiqueta_corta, sub_etiqueta) y
    #    se rotula alternando arriba/abajo para no encimarse. Metodo
    #    .muesca(i) -> np.array. Tope 6 hitos.
```

Demo obligatoria:
`studio/content/animations/experimentacion/18-espectro.py` con
`DemoEspectro(Scene)` (~15 s): barra_bandas con un segmento resaltado,
curva_gases con ventanas en verde y un punto sobre el pico de 60 GHz,
curva_lluvia, gotas_y_onda larga vs corta, tierra_y_anillos con un haz
estacion→GSO y un sat NGSO cruzandolo, patron_antena, linea_tiempo de
3 hitos.

## Reglas duras para los clips

Identicas a los cursos 01-05: solo `class ClipN(Scene)`; Rotulos para
todo texto narrativo; un fenomeno por clip; 28-45 s (tope INVIOLABLE,
fusionar pies si no caben); determinismo; MathTex raw corto; solo
paleta; `# --- momento ---` por beat; cada pie visible >= 5 s.

## Storyboard clip a clip

### Clip 1 — `1 · Un recurso que no se fabrica` (escena `Clip1`, ~35 s)
Portada: `titulo_marca("El espectro", 46)` + subtitulo ambar «la guerra
invisible por las ondas». HUD `Modulo 01`. Titulo «Un recurso que no se
fabrica». `barra_bandas` centrada (y≈+0.3). Pie: «Todo lo inalámbrico
—radio, GPS, satélites, tu teléfono— cabe en una sola recta.» Varios
segmentos pulsan en secuencia rapida (Indicate). Pie: «No se puede
fabricar más: solo repartirla mejor.» Acto 2: sobre la barra caen 5-6
mini-etiquetas HUD («TV», «5G», «WIFI», «SAT», «RADAR») apuntando a
segmentos distintos con lineas finas — aparecen en 2 tandas para no
saturar y las lineas NO se cruzan. Pie: «Y todos la quieren al mismo
tiempo.» Pie gancho: «Esta es la historia de cómo se reparte el cielo.»
**final_state**: barra de bandas con las mini-etiquetas de usos encima.

### Clip 2 — `2 · El mapa de las bandas` (escena `Clip2`, ~37 s)
Titulo «El mapa: de UHF a Q/V». `barra_bandas` arriba (y≈+1.3). Pie:
«Ocho barrios con nombres heredados de la guerra: L, S, C, X, Ku, Ka...»
Acto 2: el segmento C pulsa; `formula_pie` NO — pie: «Subir en
frecuencia compra ancho de banda: C ofrece 1.7 GHz...» → segmento Ka
pulsa → «...Ka ofrece 5. Tres veces más capacidad.» Acto 3: debajo
(y≈-1.2) aparece a la izquierda una parabola grande (Arc) cian con tag
«60 cm · Ku» y a la derecha una chica con tag «35 cm · Ka»;
`formula_pie("G \\approx (\\pi D / \\lambda)^2")`. Pie: «Y la antena se
encoge: la misma ganancia con la mitad de plato.» Pie cierre: «¿El
precio de subir? Lo cobra la atmósfera.» (gancho al clip 3).
**final_state**: barra de bandas arriba, dos parabolas con sus tags
abajo.

### Clip 3 — `3 · El impuesto de la lluvia` (escena `Clip3`, ~37 s)
Titulo «El impuesto de la lluvia». Izquierda (x≈-3.3, y≈+0.9)
`gotas_y_onda(lambda_rel=1.0)` con tag «banda L»; pie: «Para una onda
larga, una gota es nada: pasa de largo.» Debajo (x≈-3.3, y≈-1.1)
`gotas_y_onda(lambda_rel=0.15)` con tag «banda Ka»; pie: «A 20 GHz la
onda mide como la gota: choca, se absorbe, se dispersa.» Acto 2:
derecha (x≈+2.9, y≈-0.1) `curva_lluvia` con sus dos curvas; pie: «La
industria lo modela con una ley simple...»
`formula_pie("\\gamma_R = k\\,R^{\\alpha}")`. Dos puntos brillantes
sobre la curva intensa en f=12 y f=20 con tags «2.7 dB/km» y
«6.8 dB/km» (en relevo). Pie: «La misma tormenta: en Ku molesta, en Ka
manda.» Pie cierre: «Por eso la banda se elige ANTES de construir.»
**final_state**: dos campos de gotas a la izquierda con sus tags,
curva de lluvia a la derecha con el punto en 20 GHz.

### Clip 4 — `4 · Las ventanas atmosfericas` (escena `Clip4`, ~35 s)
Titulo «Las ventanas atmosféricas». `curva_gases` centrada (y≈-0.1) se
dibuja. Pie: «El aire también cobra: dos moléculas con sus rabietas.»
Punto brillante sobre el pico de 22 GHz + tag «H₂O · 22 GHz» (usar
"H2O" si el subindice falla). Pie: «El vapor de agua resuena a 22
gigahertz...» Relevo: punto al muro de 60 GHz + tag «O₂ · 60 GHz»;
pie: «...y el oxígeno levanta un muro de 15 dB por kilómetro en 60.»
Acto 2: las `.ventanas` verdes hacen FadeIn; pie: «Entre pico y muro
quedan las ventanas: ahí viven las bandas comerciales.» Pie cierre:
«Hasta el muro sirve: en 60 GHz la señal muere pronto... y eso permite
reusarla en la esquina siguiente.»
**final_state**: curva de gases con los dos picos marcados y las
ventanas verdes visibles.

### Clip 5 — `5 · El arbitro del cielo` (escena `Clip5`, ~36 s)
Titulo «La UIT: el árbitro del cielo». Tres `bloque` en fila (y≈+0.8):
«API» → «COORDINACIÓN» → «NOTIFICACIÓN» (violeta→ambar→verde) con
`conectar` y `flujo`. Pie: «Nadie enciende un satélite sin pasar por la
ventanilla: tres trámites ante la UIT.» Acto 2: `llave` bajo la cadena:
«7 años máximo». Pie: «Siete años para pasar del papel al satélite en
órbita, o la prioridad se pierde.» Acto 3: la llave se retira; bajo la
cadena (y≈-1.4) `linea_tiempo` de 3 hitos («API», «PUESTA EN SERVICIO»,
«CADUCIDAD») con un punto recorriendola. Pie: «El orden de llegada es
la moneda: quien registra primero, cobra protección primero.» Pie
cierre: «El espectro no se compra: se tramita, se usa... o se pierde.»
**final_state**: cadena de 3 bloques arriba y linea de tiempo abajo.

### Clip 6 — `6 · El anillo lleno` (escena `Clip6`, ~38 s)
Titulo «NGSO contra GSO: el anillo lleno». `tierra_y_anillos` centrada
(x≈-0.6, y≈-0.1). Pie: «A 36 000 km, un anillo único: el arco
geoestacionario. Casi todo asignado.» Los puntos GSO pulsan cian. Acto
2: `haz` cian de `.estacion(-35)` al sat GSO mas cercano; pie: «Cada
estación lleva décadas apuntando a su posición... bajo promesa de que
nadie se cruce.» Acto 3: los sats NGSO violeta orbitan (Rotate del
VGroup .sats_ngso, ~40°) y uno queda DENTRO del haz; el haz parpadea
rojo (2 pulsos). Pie: «Una constelación cruza ese haz varias veces por
minuto. El conflicto es geométrico: inevitable.» Acto 4: etiqueta_hud
junto a la tierra: «REGLA 22.2»; pie: «La regla es asimétrica: el que
llega después, se aparta. Sin importar cuántos satélites traiga.»
**final_state**: tierra con ambos anillos, haz cian a un sat GSO y la
etiqueta REGLA 22.2.

### Clip 7 — `7 · Medir el daño donde duele` (escena `Clip7`, ~36 s)
Titulo «epfd: medir el daño donde duele». `patron_antena` a la
izquierda (x≈-2.9, y≈-0.1) apuntando a la derecha. Pie: «Una antena no
escucha igual en todas direcciones: un lóbulo principal y muchos
laterales.» Acto 2: flecha ambar entrando EXACTAMENTE por el eje del
lobulo principal (desde la derecha); el patron pulsa rojo. Pie: «La
misma potencia por el eje: devastadora.» Relevo: la flecha se
desvanece; otra flecha ambar entra a ~35° (por un lobulo lateral); el
patron apenas reacciona (Indicate suave verde). Pie: «...por un lóbulo
lateral: casi irrelevante.» Acto 3: `formula_pie` NO tiene formula
larga — etiqueta_hud «EPFD: POTENCIA + GEOMETRÍA» centrada abajo del
patron... mejor: pie: «La epfd pesa cada emisor por dónde entra. Es el
número que vigila la UIT.» Acto 4: a la derecha (x≈+2.9) mini
`tierra_y_anillos(radio_gso=2.0, radio_ngso=1.15, sats_gso=8,
sats_ngso=6)` escala 0.85: un sat NGSO se acerca al haz y su punto se
APAGA (opacity 0.2) justo antes de cruzarlo, reencendiendo despues.
Pie: «Por eso las constelaciones apagan el haz al cruzar el arco: la
guerra se gana cediendo el paso.»
**final_state**: patron de antena a la izquierda, tierra con anillos a
la derecha con un sat NGSO apagado cerca del haz.

### Clip 8 — `8 · CMR-27: la proxima batalla` (escena `Clip8`, ~38 s)
Titulo «CMR-27: la próxima batalla». `linea_tiempo` de 4 hitos
(«CMR-19», «CMR-23», «CMR-27», «CMR-31») centrada (y≈+0.6) con el
punto avanzando hasta CMR-27 (que pulsa ambar). Pie: «Cada cuatro años
el mundo entero se sienta a repartir las ondas de nuevo.» Acto 2: bajo
la linea (y≈-1.2) tres etiquetas HUD en fila, espaciadas: «MAS IMT»,
«D2D», «NUEVAS BANDAS NGSO» — aparecen una a una. Pie: «Sobre la mesa:
más espectro móvil, teléfonos que hablan con satélites, nuevas bandas
para constelaciones.» Pie: «Lo que ahí se firme decidirá qué misiones
existen en 2035.» Acto final: todo se desvanece → tarjeta de cierre:
`titulo_marca("El espectro", 46)` + subtitulo ambar «la guerra
invisible por las ondas» + subrayado `con_brillo`. `self.wait(2)`.
**final_state**: tarjeta de cierre del curso centrada, pantalla limpia
salvo esquinas HUD y marca de agua.

## Descripcion del proyecto (campo description)

Curso de divulgación en 8 clips sobre el espectro radioeléctrico y su
regulación: el recurso finito y su mapa de bandas de UHF a Q/V, el
costo de subir en frecuencia (lluvia y absorción atmosférica), las
ventanas donde viven las bandas comerciales, la UIT y el trámite de
las redes satelitales, el conflicto NGSO-GSO con la regla 22.2, la
epfd como métrica del daño y la agenda de la CMR-27. Estilo
3Blue1Brown en español.
