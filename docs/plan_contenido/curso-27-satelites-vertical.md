# Curso 27 — Satelites: la maquina que no se cae (FORMATO VERTICAL)

Rama `curso/satelites-vertical` (worktree
`~/Documentos/github/codeaerospace_contenido-satelites`), basada en
`curso/fractales-vertical` porque de ahi vienen el lienzo 9:16 (`promo.py`) y
las cuatro herramientas del formato (`render_vertical.py`, `alinear_voz.py`,
`unir_vertical.py`, `sfx.py` vertical), ya con sus arreglos.

Encargo (2026-08-27, 18:00): *"un nuevo curso en vertical, este sera sobre
satelites"*.

## Que es este curso y en que se diferencia

El **curso 2 de la coleccion, "Satelites e IA: la red que aprende a
gobernarse"** (horizontal, 8 clips, solo en la DB de produccion) y la mitad
divulgativa del **curso 3, "Mecanica orbital: el ballet de la gravedad"**, se
quedan cortos para el telefono: son de 2026-07, con pies de texto, y el
enjambre aparece ya montado, sin explicar por que hace falta.

Este los **releva** con el mismo movimiento que el curso 26 hizo con el 1:
14 clips, cuatro modulos, y el arco entero va de **por que un satelite no se
cae** a **cuantos hay ahora mismo sobre tu cabeza**.

| | Curso 2 (horizontal) | Curso 27 (vertical) |
|---|---|---|
| Formato | 16:9 | **9:16 real** (1080x1920 @60) |
| Piezas | 8 clips | **14 clips + intro + cierre** |
| Texto | pies de 5 s, rotulos | **ningun subtitulo**: solo la CIFRA y su etiqueta HUD |
| Audio | narracion TTS sobre el pie | **voz escrita a mano y alineada** al instante visual + cama de SFX |
| Alcance | constelacion + IA, ya montadas | caida libre, Kepler, huella, traza, pase, enjambre, malla, enlace, la red que se gobierna |
| Entrega | `curso_narrado.mp4` | **un solo vertical** intro+14+cierre unidos |

**Lo que este curso NO re-explica** (y a que altura lo toca, cuando lo toca):

| Ya publicado | Aqui |
|---|---|
| 9 · Apuntar a un satelite (Az/El, Doppler, PID) | el clip 06 enseña **el pase visto desde el suelo**, no el lazo de control |
| 13 · Cerrar el enlace (PIRE, C/N0, G/T, Shannon) | el clip 11 enseña **una sola cifra**: la perdida de camino, y por que la antena mira |
| 20 · Metrologia optica (ISL opticos) | el clip 10 enseña **la malla como topologia**, no la optica del haz |
| 24 · Comunicaciones digitales (muestreo, MODCOD, ACM) | no se toca |
| 16 · Relatividad y el GPS | no se toca (se menciona en el cierre, en gris) |
| 17 · Tsiolkovsky (subir hasta alli) | no se toca: aqui empieza el arco **cuando ya esta arriba** |

Lo que NO cambia: tema `code_brand`, **toda cifra en pantalla la calcula la
libreria** con numpy y semilla fija, y la revision de frames uno a uno.

## Reglas del formato vertical (duras, heredadas del curso 26)

1. **Sin subtitulos.** Prohibido el pie de frase. Se permite: una **cifra**
   grande, su **etiqueta HUD** de 1-3 palabras en MAYUSCULAS, y el
   identificador de la pieza. Si una idea necesita una frase para
   entenderse, el clip esta mal diseñado: se rehace la imagen.
2. **La voz no lleva la leccion sola.** Mucha gente mira en silencio: la
   imagen enseña, la voz remata.
3. **Zona segura** `promo.SEGURA["vertical"]` (10 % arriba, 20 % abajo,
   14 % a la derecha). El guardian `cabe()` ABORTA el render si un rotulo
   pasa de 5.76 unidades. No se negocia: en el curso 26 cazo nueve.
4. **1 unidad = 135 px** igual que en horizontal: los `font_size` valen tal
   cual; solo hay que RECOLOCAR (columna, no fila).
5. **Duracion por clip: 30-45 s.** Empieza y termina en **fondo limpio**
   para que el `concat -c copy` no chasquee.
6. Sin acentos en texto renderizado (Rajdhani / Space Mono). Los acentos
   viven en los `.json` — salvo el texto de la **voz**, que si los lleva.
7. El pie de cifra en los tres renglones FIJOS (`Y_ETIQUETA`, `Y_NUMERO`,
   `Y_SUB`) y los relevos con `cambiar()`, nunca con fundido cruzado.

## Paleta por ROL (un rol = un significado en TODO el curso)

| Rol | Color | Uso |
|---|---|---|
| Cifra medida | cian `#22d3ee` | TODO numero calculado por la libreria en este render |
| El satelite | ambar `#f59e0b` | el objeto que se mueve, su orbita, su traza |
| La Tierra / el suelo | verde `#34d399` | el planeta, la estacion, el usuario |
| El enlace / el haz | violeta `#7c3aed` | radio, huella, ISL, cobertura |
| Lo que se pierde | naranja `#ea580c` | el disparo que cae, el hueco sin cobertura, el corte |
| Mobiliario | `#31414f` | ejes, reticula, mapa base |
| Dato externo | gris `#94a0b0` | lo que NO calcula la libreria (se declara SIEMPRE) |

Regla de honestidad: **el cian solo aparece si la libreria calculo esa cifra
en este render**. Constantes fisicas (mu, radio terrestre, dia sidereo) y
datos de mision reales (Iridium 66, altitud Starlink) van en gris.

## Mapa del curso

### M1 · Caerse sin llegar al suelo

| # | Clip | La imagen | La cifra medida |
|---|---|---|---|
| 1 | `01-el-canon` | el cañon de Newton: el mismo disparo, cada vez mas rapido; las balas caen y caen hasta que una falla el suelo y da la vuelta | velocidad de circularizacion a 400 km; caida en 1 s frente a la curvatura de la Tierra en esa misma distancia |
| 2 | `02-alto-es-lento` | cuatro alturas compitiendo en la misma pantalla: LEO, MEO, GPS, GEO; el de arriba parece parado | periodo orbital a 550 / 2000 / 20200 / 35786 km (3ª de Kepler, resuelta) |
| 3 | `03-la-elipse` | orbita eliptica real (Kepler por Newton-Raphson): barre areas iguales en tiempos iguales; corre en el perigeo y se arrastra en el apogeo | cociente v_perigeo/v_apogeo y las dos areas barridas, medidas sobre la trayectoria dibujada |

### M2 · La Tierra gira debajo

| # | Clip | La imagen | La cifra medida |
|---|---|---|---|
| 4 | `04-la-huella` | el casquete que un satelite ve: el cono baja al mapa y pinta una tapa; con 10 grados de elevacion minima | radio de la huella en km y **% de la superficie terrestre** que ve UNO |
| 5 | `05-la-traza` | el ground track: la sinusoide que no cierra, porque la Tierra se ha girado debajo mientras el satelite daba la vuelta | corrimiento hacia el oeste por vuelta (grados y km en el ecuador) |
| 6 | `06-el-pase` | desde el suelo: la boveda polar, el satelite entra por el horizonte, culmina y se va | duracion del pase y elevacion maxima, medidas de la ventana de visibilidad |

### M3 · Por eso son muchos

| # | Clip | La imagen | La cifra medida |
|---|---|---|---|
| 7 | `07-uno-no-basta` | el mapa se va pintando: 1 satelite, 6, 24, 66; los huecos se cierran a ojo mientras la cifra sube | **% de la Tierra cubierta** por N satelites (barrido medido sobre la malla) |
| 8 | `08-los-planos` | la Walker-delta por dentro: planos con su RAAN repartido y la fase entre planos; se gira la camara | latitud maxima cubierta con inclinacion 53 grados: **los polos se quedan fuera** (medido) |
| 9 | `09-el-relevo` | un punto en el suelo y el enjambre encima: la linea salta de un satelite al siguiente antes de que el primero se ponga | tiempo medio entre relevos y numero de relevos en 90 minutos |
| 10 | `10-la-malla` | un paquete cruza el oceano saltando de satelite en satelite; al lado, la ruta por fibra | longitud del camino por la malla (suma de saltos reales) y su latencia frente a la de la fibra |
| 11 | `11-por-que-la-antena-mira` | la esfera de energia que crece: la misma potencia repartida en una superficie cada vez mayor | perdida de camino a 550 km y a 35786 km en 12 GHz, y la diferencia en veces |

### M4 · La red que se gobierna sola

| # | Clip | La imagen | La cifra medida |
|---|---|---|---|
| 12 | `12-el-trafico-no-esta-repartido` | la constelacion pasa y la mayor parte del tiempo esta sobre agua; los haces fijos riegan el oceano | **% del tiempo-satelite sobre el mar** (mascara de tierra propia) y capacidad desperdiciada con haces fijos |
| 13 | `13-la-red-aprende` | el asignador de haces: primero reparte a ciegas, luego aprende a seguir la demanda; la tabla de decision se colorea sola | demanda servida antes y despues del aprendizaje, **medida sobre la matriz de cobertura del propio enjambre** |
| 14 | `14-sobre-tu-cabeza` | se apaga el mapa y queda el cielo de un patio: los satelites que en ESTE instante estan sobre el horizonte de un punto del suelo | cuantos hay sobre tu cabeza ahora mismo, contados con la propagacion del enjambre |

Intro (`00-intro`) y cierre (`15-cierre`): la identidad CO.DE Academy
recompuesta para 9:16, con su cama sonora (las mismas piezas de marca del
curso 26, con el texto del curso).

## Contrato de la libreria (`studio/content/manim_extensions/satelites.py`)

`satelites.py` YA EXISTE (513 lineas, escrita para el curso 2 y reusada por
el 9) y trae: `ConstelacionWalker`, `AnimarWalker`, `enlaces_walker`,
`posiciones_walker`, `subsatelites_walker`, `mapa_tierra` / `imagen_mapa` /
`mascara_tierra`, `puntos_en_mapa`, `angulo_cobertura`, `conteo_cobertura`,
`colorear_cobertura`, `animar_cobertura`, `traza_terrestre`,
`ventana_visibilidad`, `curva_aprendizaje`, `heatmap_q`. Los topes duros
(`SATS_MAX=240`, `FRAMES_MAX=260`, `RES_MAX_MAPA=1920`) se respetan.

Se **AMPLIA sin tocar lo existente** (los clips del curso 2 y del 9 en la DB
siguen valiendo) con:

```
# --- caida libre y Kepler (M1) ---
MU_TIERRA = 398600.4418            # km^3/s^2  (constante: va en GRIS)
velocidad_circular(h_km)           -> km/s
periodo_orbital(h_km)              -> dict(segundos, minutos, horas)
canon_newton(v0_km_s, ...)         -> (n,2) trayectoria balistica/orbital desde una montaña
caida_vs_curvatura(h_km, t_s)      -> dict(caida_m, curvatura_m, distancia_km)
elipse_kepler(a, e, muestras)      -> (n,2) puntos + velocidades por punto
areas_barridas(pts, vels, t0, dt)  -> dict(area_perigeo, area_apogeo, cociente_v)

# --- geometria de la cobertura (M2) ---
radio_huella_km(h_km, el_min)      -> km sobre la superficie (usa angulo_cobertura)
fraccion_visible(h_km, el_min)     -> fraccion de la esfera que ve UNO
corrimiento_traza(h_km)            -> dict(grados_por_vuelta, km_ecuador)
pase(lat, lon, h_km, ...)          -> dict(duracion_s, el_max, t_entrada, t_salida)

# --- el enjambre (M3) ---
cobertura_vs_n(lista_n, h_km, ...) -> [(N, fraccion_cubierta)] medido en la malla
latitud_maxima_cubierta(incl, h_km, el_min) -> grados
relevos(lat, lon, trazas, h_km)    -> dict(n_relevos, intervalo_medio_s, huecos_s)
ruta_malla(origen, destino, lonlat, h_km) -> dict(saltos, km, latencia_ms)
latencia_fibra(origen, destino)    -> dict(km, latencia_ms)   # 1.4x gran circulo, 2c/3
fspl_db(d_km, f_ghz)               -> dB   (misma formula que enlace.py, reusada)

# --- la red que se gobierna (M4) ---
tiempo_sobre_mar(trazas)           -> fraccion del tiempo-satelite sobre agua
demanda_por_celda(res, semilla)    -> matriz de demanda (sintetica pero DECLARADA)
asignar_haces_fijo(cobertura, demanda, n_haces)    -> demanda servida
asignar_haces_aprendido(...)       -> (curva de mejora, demanda servida final)
sobre_el_horizonte(lat, lon, lonlat_sats, h_km)    -> cuantos y cuales
```

**Cambio de honestidad respecto al curso 2**: `curva_aprendizaje()` es una
curva RL **sintetica**. En un curso sin subtitulos no se puede matizar de
palabra, asi que **no se usa como cifra**: el clip 13 mide la demanda servida
sobre la matriz de cobertura REAL del enjambre (la que sale de
`conteo_cobertura`), y la curva sintetica se queda, como mucho, de adorno de
fondo y en gris. La matriz de demanda tambien es sintetica: se declara en el
pie, en gris, y lo que se compara es la MEJORA relativa, que si es real.

Todo determinista (`default_rng(semilla)`), topes duros, y **cero cifras
inventadas**.

## Herramientas

Ninguna nueva: las cuatro del curso 26 valen tal cual
(`render_vertical.py`, `alinear_voz.py`, `unir_vertical.py`, `sfx.py`). Lo
unico que cambia es el directorio: `studio/content/verticales/satelites/`.

## Tablero de estado

| Paso | Estado |
|---|---|
| 1 · Plan maestro | **hecho** (2026-08-27) |
| 2 · Libreria ampliada + sonda de validacion en contenedor | **hecho**: `studio/tools/sonda_satelites.py`, **0 fallos** |
| 3 · Molde: intro + clip 01 escritos, renderizados y revisados | **hecho**: intro 12.43 s, clip 01 35.43 s (ql), frames revisados |
| 4 · Esqueletos de las 16 piezas (`curso.json` + stubs) | **hecho**: las 16 componen; el cierre (heredado) renderiza a 8.90 s |
| 5 · Produccion de los clips 02-14 | pendiente (13 piezas) |
| 6 · Revision de frames uno a uno + `pytest -q` del Studio | pendiente |
| 7 · `qh` de las 16 (3 en paralelo, desde un `.sh`) | pendiente |
| 8 · Voz (VPS, SERIAL, `alinear_voz.py`) | pendiente |
| 9 · Mux + union + picos + costuras | pendiente |
| 10 · PLAN.md, catalogo, cosecha de trampas y memoria | pendiente |

**Decision abierta que hereda del curso 26**: la rama sale de
`curso/fractales-vertical`, que a su vez sale de `exp/promos-redes`. Un PR a
`main` arrastraria los promos Y el curso de fractales. Hay que decidirlo con
el dueño antes del paso 7 (no bloquea nada hasta entonces).

## Cifras ya medidas (sonda del 2026-08-27, 0 fallos)

Ninguna de estas se vuelve a calcular a mano: el clip llama a la libreria y
la imprime. Se anotan para poder escribir el storyboard sin adivinar.

| Clip | Cifra | Valor medido |
|---|---|---|
| 01 | velocidad de circularizacion a 400 km | **7.673 km/s** |
| 01 | caida en 1 s / curvatura bajo esa cuerda | **4.347 m / 4.347 m** |
| 01 | alcance de los disparos (50/65/80/92 %) | 11.8 / 17.5 / 27.4 / 49.2 grados |
| 02 | periodos a 550 / 2000 / 20200 / 35786 km | 95.50 min / 127.04 min / 11.973 h / **23.928 h** (dia sidereo) |
| 03 | cociente de areas barridas (e=0.65) | **1.0000**; v_peri/v_apo = 4.7143 |
| 04 | huella a 550 km con 10 grados | radio **1664 km**, **1.70 %** de la Tierra |
| 04 | GEO a 10 grados / a 0 grados | 34.09 % / 42.44 % (nunca medio planeta) |
| 05 | corrimiento de la traza a 550 km | **23.94 grados = 2662 km** por vuelta; 15.04 vueltas/dia |
| 06 | pase sobre CDMX (550 km, 53 grados) | **8.24 min**, elevacion maxima 88.9 grados |
| 07 | cobertura con 1 / 6 / 24 / 66 / 240 | 1.70 / 8.46 / 37.33 / 74.36 / **91.99 %** |
| 08 | latitud maxima con inclinacion 53 | **68.0 grados**: los polos fuera (86.4 si los cubre) |
| 09 | relevos sobre CDMX con 66 satelites | **14 en 90 min**, uno cada 6.43 min; 71 % del tiempo sin servicio a 25 grados |
| 10 | Nueva York - Londres | malla **4 saltos, 6977 km, 23.27 ms**; fibra 7802 km, 39.04 ms |
| 11 | FSPL a 12 GHz, 550 km y GEO | **168.84 y 205.11 dB** (36.27 dB = **4234 veces**) |
| 12 | tiempo-satelite sobre agua | **70.7 %** |
| 13 | demanda servida, fijo -> aprendido | 1.09 % -> **7.59 %** (x6.94), techo 7.59 % |
| 14 | sobre CDMX con 240 satelites | **4** por encima de 10 grados (Svalbard, 78N: 0) |

## Cosecha de trampas

*(Se llena durante la produccion. Se arranca con las del curso 26, que
aplican enteras: guardian de ancho, `Text` no escala continuo, `cambiar()` en
vez de fundido cruzado, `FadeOut` de VGroup deja sueltos los submobjects,
z_index de las cortinas, contadores con `become`, el tope de 2.5 s del
ensamblador de voz, y el `sorted()` de las carpetas de resolucion.)*

Especificas de este curso, previstas:

- El mapa equirrectangular **miente en las areas**: un casquete de cobertura
  cerca del polo se dibuja enorme y el % medido sale pequeño. La cifra se
  calcula por area de esfera (`fraccion_visible`), NUNCA contando pixeles del
  mapa plano sin pesar por `cos(lat)`.
- La traza se parte en el antimeridiano (`traza_terrestre` ya lo hace): una
  polilinea sin partir cruza la pantalla de lado a lado.
- **La fase de una orbita NO mueve su traza.** `pase()` barria `fase0` y
  ninguna fase acercaba el satelite a la estacion: desplazar el arranque
  recorre la MISMA curva desde otro punto, porque la rotacion terrestre se
  resta desde el instante inicial. Medido: la latitud sobre el meridiano de
  la estacion no se movia ni un grado en 72 fases. El knob es el **RAAN**.
- **Una ventana que cae en el borde del muestreo es media ventana.** El
  perigeo esta en t=0, o sea en el extremo del array: `areas_barridas` tomaba
  media ventana alli y entera en el apogeo, y el cociente salia 0.9958 con la
  fisica perfecta. Envolviendo la ventana da 1.0000.
- **Ambar y naranja son el mismo color a grosor 2.** El satelite (`C_SAT`
  `#f59e0b`) y lo que se pierde (`C_PERDIDO` `#ea580c`) no se distinguen en
  una linea fina sobre fondo oscuro. La diferencia la tiene que hacer el
  PESO: el disparo que falla va fino y al 50 % de opacidad; el que se queda
  arriba, grueso y opaco.
- **Dos rotulos HUD cortos en el mismo renglon se leen como una frase.**
  "CAE" y "SUELO", separados 0.80 unidades sobre sus barras, se leian "CAE
  SUELO". A 2.70 cada uno sobre su barra, ya no.
- `hud()` **espacia todos los caracteres**: una etiqueta de 16 letras ocupa
  el doble de lo que parece al escribirla. Medido tres veces con lo que el
  guardian rechazo ("por cada 1.50 del bajo" 6.42, "de horizonte a
  horizonte" 7.01, "y de ahi para arriba, nada" 7.64), sale
  **0.292 unidades por caracter a font_size 18**, o sea un tope de
  **19 caracteres contando los espacios**. Escribir los rotulos con esa
  regla ahorra una vuelta de render por clip.
