---
title: Figuras de investigación
level: avanzado
summary: API de figura.py (lienzo IEEE en pulgadas, tipografía medida en puntos, sello de proveniencia, datos adjuntos) y de ntn.py (pase LEO, Doppler, handover, quórum PBFT, margen adaptativo y gates con IC95 %), con las cifras medidas y las trampas que costaron encontrar.
tags: [figura, ntn, paper, tesis, ieee, proveniencia, leo, pbft, gates, primitivas]
minutes: 14
order: 6
---

Estas dos primitivas no son para el canal: son para la **tesis** y para las
**figuras citables** de un artículo. La diferencia no está en el dibujo, está
en la disciplina: el lienzo se declara en pulgadas y puntos por pulgada, la
tipografía se mide en puntos impresos, los datos entran de un archivo y toda
figura sale con su commit, su semilla y su fecha.

Las dos tienen sonda de invariantes, y hay que correrla antes de dibujar:

```bash
docker run --rm --network none --user $(id -u):$(id -g) -v "$PWD":/workspace \
  -w /workspace codeaerospace_contenido-manim python3 studio/tools/sonda_figura.py
docker run --rm --network none --user $(id -u):$(id -g) -v "$PWD":/workspace \
  -w /workspace codeaerospace_contenido-manim python3 studio/tools/sonda_ntn.py
```

## figura.py — el lienzo es físico

```python
import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")
import figura as fg

fg.Figura(tema="paper", columnas=1)      # <- a nivel de MÓDULO, no en construct

class FiguraA(Scene):
    def construct(self):
        fg.fondo(self)
        ax = fg.ejes_paper((0, 60), (0, 400), "tiempo (s)", "RTT (ms)")
        self.add(ax, fg.curva(ax, t, rtt), fg.sello(semilla=42))

fg.sellar_escenas(globals())             # <- si no, le cae la marca del canal
```

El lienzo **se fija en el módulo** porque la cámara se construye antes de que
corra `construct`: tocar `config` dentro de la escena llega tarde.

| | 1 columna | 2 columnas |
|---|---|---|
| plantilla IEEE | 3.5 in | 7.16 in |
| a 300 dpi | **1050 × 652 px** | **2148 × 1332 px** |
| frame de escena | 14.00 × 8.69 u | 28.64 × 17.76 u |
| 1 unidad de escena | **18 pt** | **18 pt** |

Que una unidad valga 18 puntos en las dos es lo que hace que un `font_size`
signifique el mismo tamaño físico en una columna y en dos.

- `fg.Figura(tema, columnas, ancho_in, alto_in, dpi)` — `tema` es `"paper"`
  (blanco, tinta #111, paleta Okabe-Ito, fuente por defecto de manim, que sí
  trae acentos) o `"marca"` (el tema oscuro de `code_brand`, Rajdhani y Space
  Mono: aquí **sin acentos**).
- `fg.Figura.pantalla(tema="marca")` — el mismo dibujo dentro de un clip de
  vídeo: respeta los píxeles que puso `-ql` / `-qh` y solo declara el tamaño
  físico equivalente.
- `fg.texto(cadena, puntos)` / `fg.alto_pt(mob)` / `fg.fs_para_pt(puntos)` —
  tipografía en **puntos impresos**, no en `font_size`. Medido en el PNG con
  PIL: un texto de 8 pt sale con 34 px de tinta a 300 dpi (lo exacto son
  33.33).
- `fg.exigir_legible(grupo, minimo_pt=4.5)` — aborta el render si algo se
  pinta por debajo del suelo; `fg.exigir_dentro(grupo)` si algo se sale del
  cuadro; `fg.encajar(grupo, reservar_abajo_pt=8)` escala, centra y vuelve a
  comprobar.
- `fg.ejes_paper(x_rango, y_rango, xlabel, ylabel)` — marco dibujado a mano en
  el borde izquierdo e inferior (no el `Axes` de manim, ver trampas), rejilla,
  marcas numeradas y línea de cero **solo si el cero cae dentro del rango**.
- `fg.curva`, `fg.serie_tiempo`, `fg.banda_ic`, `fg.cdf`, `fg.percentil`,
  `fg.gantt`, `fg.leyenda`, `fg.titulo`.
- `fg.sello(commit=None, semilla=None, extra=None)` — gris pequeño abajo a la
  derecha. Lee `MS_COMMIT`, `MS_SEMILLA` y `MS_FECHA`; sin commit escribe
  `sin-commit`, que es una afirmación honesta y no un hueco.
- `fg.leer_csv(nombre)` / `fg.leer_jsonl(nombre)` — leen de `MS_DATOS_DIR`
  (por defecto `datos/` relativo al cwd del render) y fallan diciendo dónde
  buscaron.

### Geometría honesta

`Text.width`, `.height`, `.get_center()`, `next_to()` y `move_to()` **mienten**
en cuanto el texto tiene un espacio y se mueve del origen (ver trampas). Por
eso `figura` posiciona y mide con `fg.caja`, `fg.ancho`, `fg.alto`,
`fg.centro`, `fg.borde`, `fg.poner(mob, punto, anclaje)` y
`fg.pegar(mob, ancla, direccion, hueco)`.

## ntn.py — la tesis 6G/NTN

No reimplementa nada: la mecánica orbital sale de `satelites.py` y el
presupuesto de enlace de `enlace.py`. Todo determinista
(`np.random.default_rng(semilla)`).

```python
import figura as fg, ntn
fg.Figura(tema="paper", columnas=1)

p = ntn.pase_leo(600.0, 53.0, lat_gs=19.43, lon_gs=-99.13)
grupo = ntn.curva_elevacion(p)            # AOS / TCA / LOS marcados
dop = ntn.resumen_doppler(p, 2.0e9)
```

- `pase_leo(h_km, inc_deg, lat_gs, lon_gs, elev_min_deg, raan_deg=None)` —
  con `raan_deg=None` barre el nodo y se queda con el pase más alto. Devuelve
  `t_s`, `elev_deg`, `dist_km`, `azim_deg`, `lonlat`, `aos_s`, `tca_s`,
  `los_s`, `duracion_s`, `elev_max_deg`, `dist_min_km`.
- `doppler(f_hz, t_s, dist_km)` y `resumen_doppler(pase, f_hz)`;
  `retardo_ida_ms(d_km)`; `distancia_oblicua_km(elev, h)` y su inversa
  `elevacion_de_distancia_deg`; `distancia_horizonte_km(h)`.
- `escenario_leo600()` — qué geometría implica cada tick del CSV del banco.
- `handover(n_sats, solape=0.25)` — cascada de cobertura de un tren, con
  `relevos_s`, `cobertura` y `hueco_s`.
- `f_max(n)` y `quorum_pbft(n)` — `f = (n-1)//3`, quórum
  `ceil((n+f+1)/2)`, mensajes por fase y total `2n(n-1)`.
- `margen_adaptativo(r_oraculo, r_best)` y `gate(muestras_por_semilla,
  umbral, ci=0.95)`; `banda_ic_por_x(series)` para la banda punto a punto.
- Dibujos: `curva_elevacion`, `curva_doppler`, `cascada_handover`,
  `diagrama_pbft`, `curva_ma`, `traza_tierra`. Todos sobre `figura`, así que
  valen igual en el tema `paper` y en el `marca`.

### Cifras medidas (sonda del 2026-09-03)

| | |
|---|---|
| FSPL a 600 km y 2 GHz | 154.03 dB (el 92.45 sobra 0.0022 dB) |
| horizonte geométrico a 600 km | 2829.35 km |
| pase sobre Ciudad de México | 89.63° máx., 530.1 s |
| distancia / retardo de ida | 1930 km (6.44 ms) en AOS, 600 km (2.00 ms) en TCA |
| Doppler de pico a 2 GHz | 43.60 kHz = 21.82 ppm |
| tick 0 del banco (12.9 ms) leído como RTT | 9.97° — la máscara de 10° |
| tren de 4 satélites, solape 0.25 | 100 % de cobertura, 3 relevos |
| quórum PBFT n=7 | f=2, quórum 5, 84 mensajes |
| quórum PBFT n=6 | f=1, quórum **4** (2f+1 daría 3) |

## Demos

Viven en `studio/content/animations/investigacion/` y salen en la pestaña
**Animaciones** bajo «Investigación»:

| id | escena | qué enseña | tema |
|---|---|---|---|
| `investigacion/01-margen-adaptativo-con-ic` | `FiguraMA` | curva MA con banda IC95 %, umbral y sello | paper, 1 col |
| `investigacion/02-gantt-de-disponibilidad` | `FiguraGantt` | Gantt de 4 nodos desde `disponibilidad.jsonl` | paper, 2 col |
| `investigacion/03-cdf-de-recuperacion` | `FiguraCDF` | CDF empírica desde `recuperacion.csv` | paper, 1 col |
| `investigacion/04-pase-leo-600` | `PaseLeo600` | traza, elevación con AOS/TCA/LOS y Doppler | marca, vídeo |
| `investigacion/05-quorum-pbft` | `QuorumPbft` | las tres fases, el quórum y el contraejemplo n=6 | marca, vídeo |

Las tres de paper se exportan además a PNG con `-s`, que es lo que se cita:

```bash
manim render -s --media_dir <dir> 01-margen-adaptativo-con-ic.py FiguraMA
```

Ojo con el título que verás en la pestaña: sin una lección con el mismo id,
`animations.py` lo deriva del slug con `.capitalize()`, así que las siglas
salen en minúscula («Cdf de recuperacion»). Es el mismo comportamiento que ya
tienen «De 5g a 6g» o «Isac sensado y comunicacion»; no es cosa de estas demos.

### Comprobado contra la tubería real, no contra el archivo del repo

Lo que corre en la app no es el archivo tal cual: `branding.aplicar()` le anexa
`code_brand.marcar_escenas(globals())` a todo script que no mencione
`code_brand`, y las cinco demos entran en ese caso. Se renderizaron **con el
bloque anexado** para ver lo que de verdad se pinta:

- las tres figuras de paper salen **idénticas**: fondo blanco, sin marca de
  agua y sin esquinas HUD. `sellar_escenas(globals())` funciona porque marca
  las escenas con el mismo `_code_brand` que la marca usa para ser idempotente;
- las dos de vídeo sí reciben la marca de agua y las esquinas, y el wordmark de
  la esquina inferior derecha **no toca** los pies centrados de ninguna de las
  dos (medido en los fotogramas: el pie más largo del Doppler acaba unos 45 px
  antes de donde empieza el wordmark a 480p).

## Trampas (todas medidas, ninguna supuesta)

- **El espacio infla la caja.** Un `Text` con un espacio crea un submobject
  **vacío**, y `Mobject.reduce_across_dimension` devuelve `0` para un
  submobject sin puntos: la caja del texto se come el origen en cuanto lo
  mueves. `Text("RTT (ms)")` mide 0.2539 de alto recién nacido y **2.1270**
  después de un `shift`; sin espacios no pasa. `.width`, `.height`,
  `.get_center()`, `next_to()` y `move_to()` quedan inservibles con texto de
  más de una palabra: usa `fg.caja` / `fg.poner` / `fg.pegar`.
- **Un lado impar de píxeles rompe el vídeo.** 3.5 × 2.17 in a 300 dpi son
  1050 × 651 px, y el render moría con
  `avcodec_open2("libx264") -> Generic error in an external library` sin
  nombrar el 651. El PNG de `-s` salía perfecto: el fallo aparecía solo al
  pedir el clip. `Figura` sube el lado al par siguiente (652).
- **`frame_width` y `frame_height` son independientes en manim 0.20.1.**
  Fijar uno no recalcula el otro; hay que escribir los dos o la figura sale
  deformada respecto de la imagen, sin aviso.
- **`Axes` no siempre cruza por el origen, pero tampoco por donde quieres.**
  Con un rango de fase de −190 a −85, `Axes._origin_shift` pega el eje X al
  borde de **arriba**, con sus números encima de la curva. `ejes_paper` dibuja
  su marco a mano en el borde izquierdo e inferior, y el cero (si cae dentro)
  va como raya de referencia aparte.
- **Un guardián se prueba con lo que TIENE que fallar.** El de legibilidad se
  puede escribir mal de tres maneras, las tres medidas: filtrando con
  `has_points()` (queda muerto), midiendo glifo a glifo (el glifo más chico de
  unos ejes de 6 pt mide 1.73 pt y aborta unos ejes perfectos) o comparando la
  tinta del `Text` entero contra un suelo en puntos (castiga a las etiquetas
  cortas: un dígito no tiene descendente). Lo que se mide es el cuerpo
  **efectivo**: el nominal por el factor de escala real.
- **Un guardián de ancho no basta: hay que medir la caja COLOCADA.** Un
  bloque de 11 unidades cabe de sobra en un frame de 14.23 y aun así se sale
  por la izquierda si lo anclas a la derecha de unos ejes. Pasó en la demo del
  pase LEO.
- **`Create` sobre unos ejes dibuja los rótulos letra a letra.** A mitad de la
  animación el eje X decía "tie". Se traza solo el marco y lo escrito entra
  fundido.
- **Los rótulos de evento de un Gantt se enciman solos.** Tres eventos a 52,
  58 y 63 s de una ventana de 120 salían los tres centrados en la misma línea.
  `gantt` los reparte en niveles: cada uno va al primero donde no toca al
  anterior, y su raya sube hasta ahí.
- **El PNG de `-s` respeta la `config` del módulo, no el `-ql`.** Es lo que se
  quiere para una figura, pero explica que el vídeo de validación de una
  figura de paper salga a 652p y no a 480p.
- **`puntos_en_mapa` devuelve coordenadas, no un mobject.** La estación hay
  que dibujarla.
- **Los delays del CSV LEO-600 del banco son de ida y vuelta.** Leídos como de
  ida, 12.9 ms serían 3867 km y el horizonte a 600 km está en 2829: imposible.
  Leídos como RTT dan 9.97° de elevación, que es la máscara de 10° del propio
  escenario.
- **El quórum de PBFT no es 2f+1.** Es `ceil((n+f+1)/2)`, y solo coincide con
  2f+1 cuando `n = 3f+1`, que es el caso de todos los diagramas. Con n=6 y
  f=1, 2f+1 = 3 no es ni mayoría de 6: dos quórums de tres pueden no compartir
  ninguna réplica correcta. Lo cazó la sonda sobre la primera versión.
- **Un pase LEO es casi simétrico alrededor del TCA**, también uno oblicuo:
  los 2.2° que gira la Tierra en 530 s apenas rompen la simetría de la
  elevación (el que sí se tuerce es el azimut). Conviene tenerlo escrito para
  no «arreglar» una asimetría que la física no pide.
- **El TCA es un instante, no una muestra.** Cerca del cenit la elevación cae
  ~1° cada 1.5 s: sobre la rejilla del periodo entero un pase cenital rotulaba
  89.13° donde la geometría dice 90. `pase_leo` recentra la ventana, vuelve a
  muestrear solo el pase y afina el TCA por sección ternaria.
- **Con tres semillas el bootstrap solo tiene 10 remuestras distintas.** El
  IC95 % está cuantizado y dos semillas de bootstrap dan el mismo intervalo.
  No es un error: es el techo de resolución de tres corridas, y por eso un
  gate al borde del umbral sale **indeciso** por construcción.
- **Remuestrear muestras en vez de semillas hace pasar un gate indeciso.** Con
  tres semillas de ocho muestras, el IC honesto sale [0.221, 0.319]
  (indeciso, umbral 0.25) y el falso —remuestreando las 24 muestras sueltas—
  sale con el límite inferior en 0.254: pasaría.
- **El valor absoluto del denominador del MA decide el signo.** Con
  recompensas negativas (coste), `(−60 − (−80)) / |−80|` = **+0.25** y sin el
  valor absoluto sale −0.25: el gate leería «peor» donde el oráculo es mejor.
