"""Divulgacion (20-30 s), v2 -- casi sin texto: un pase LEO sobre una estacion.

Rehecho a partir de PROMPT_MANIM_REHACER_VISUAL_2026-09-17.md (tesis-doctorado
-6g): la v1 (commit anterior de esta rama) tenia titulo, subtitulo, un
statement completo y tres lineas de cifras -- "texto de figura de paper, no
de video de 20 s" (feedback textual del doctorando: "no me gusto que tuvieran
tanto texto las animaciones ... mas visuales, con mejor estructura, sin
textos"). Esta version NO tiene titulo ni subtitulo (los pone
`deck_seminario.js` en la diapositiva) y como maximo UNA etiqueta corta
("LEO-600"): el resto se cuenta con movimiento, con primitivas que YA
existian en `manim_extensions/` y no se habian usado en la v1:

  - `satelites.ConstelacionWalker` / `AnimarWalker`: un plano de fondo --
    "hay una red de satelites" -- antes de acercarse a un pase concreto.
  - `transiciones.transicion_zoom`: el paso de esa vista de red al mapa de
    una estacion, en vez de un corte seco.
  - `ntn.handover(n_sats=3, solape=-0.5)`: TRES satelites del MISMO tren
    (no uno), con un hueco deliberado entre sus ventanas de servicio.
    `solape` negativo es un parametro de PUESTA EN ESCENA para que el hueco
    se vea claro en ~16 s de video -- no es una cifra medida, igual que
    `rodeo`/`fraccion_c` en `satelites.latencia_fibra` se declaran como
    supuestos de ingenieria y no como medicion. El brillo de cada satelite
    sube y baja con SU PROPIA elevacion medida (`h["elev"]`, de
    `satelites.ventana_visibilidad` via `ntn.handover`), no con un
    cronometro de guion: el patron encendido-apagado-encendido que se ve ES
    el dato, no una animacion decorativa encima de el.
  - Un casquete de visibilidad alrededor de la estacion: radio angular de
    `satelites.angulo_cobertura` (funcion YA existente, no nueva), proyectado
    con la formula estandar de "punto destino sobre una esfera" (`_huella`,
    abajo) -- se dibuja UNA vez y los satelites brillan cuando su traza cae
    dentro, se apagan cuando salen.
  - `brillo.con_brillo` / `punto_brillante`: halo en la estacion y en los
    tres satelites del tren.
  - `particulas.materializar`: la estacion aparece como polvo que converge,
    no con un FadeIn plano.

No hay kepler.py aqui a proposito: `ntn.pase_leo` asume orbita CIRCULAR (e=0,
`satelites.periodo_orbital`), y en una orbita circular la velocidad angular
es constante -- ahi el `MoveAlongPath`/interpolacion a alpha constante que
usa este script YA es fisicamente correcta. `kepler.py` (excentricidad > 0,
barrido de areas iguales) es para otra figura, no para esta.

Ninguna cifra de geometria esta escrita a mano ni cambio respecto de la v1:
sigue siendo `ntn.pase_leo(600, 53, 19.43, -99.13)` (escenario ilustrativo,
LEO-600 del banco de pruebas, no NTNEnv-v2 real -- ver GUIA_CIFRAS.md de esta
carpeta, esa tabla no cambio, solo el tratamiento visual) y `ntn.handover(...)`
sobre la MISMA geometria (mismo RAAN).

    manim render -qh --media_dir media 06-pase-ntn-seminario.py PaseNtnSeminario
"""
import sys

sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import (Create, DecimalNumber, FadeIn, FadeOut, Scene,
                   UpdateFromAlphaFunc, VGroup, VMobject, linear)

import brillo
import figura as fg
import ntn
import particulas
import satelites as sat
import transiciones

fg.Figura.pantalla(tema="marca")      # 1920x1080 en -qh, respeta -ql al iterar

ALTURA_KM = ntn.ALTURA_LEO600_KM      # 600.0 -- banco de pruebas, no NTNEnv-v2
INCLINACION_DEG = 53.0
LAT_GS, LON_GS = 19.43, -99.13        # Ciudad de Mexico
SOLAPE_ESCENA = -0.5                  # puesta en escena (hueco visible), NO medido


def _huella(lat_c, lon_c, psi_deg, n=96):
    """Borde del casquete de radio angular `psi_deg` alrededor de (lat_c,lon_c).

    Formula estandar del "punto destino" sobre una esfera dado rumbo y
    distancia angular (la inversa de lo que mide
    `satelites.ventana_visibilidad`): no es una aproximacion de mapa plano,
    por eso el casquete sale como un ovalo al proyectarse en el mapa
    equirrectangular cerca del ecuador, no como un circulo perfecto.
    """
    la = np.radians(lat_c)
    lo = np.radians(lon_c)
    psi = np.radians(psi_deg)
    rumbo = np.linspace(0.0, 2.0 * np.pi, n)
    lat2 = np.arcsin(np.sin(la) * np.cos(psi)
                     + np.cos(la) * np.sin(psi) * np.cos(rumbo))
    lon2 = lo + np.arctan2(np.sin(rumbo) * np.sin(psi) * np.cos(la),
                           np.cos(psi) - np.sin(la) * np.sin(lat2))
    return np.stack([np.degrees(lon2), np.degrees(lat2)], axis=1)


class PaseNtnSeminario(Scene):
    def construct(self):
        fg.fondo(self)
        ppu = fg.activa().puntos_por_unidad()

        # --- momento 1: una red, de lejos --------------------------------
        constelacion = sat.ConstelacionWalker(
            planos=4, sats_por_plano=6, inclinacion_deg=INCLINACION_DEG,
            altitud_km=ALTURA_KM, frames=140, vueltas=0.12, tilt_deg=18.0,
            escala=1.9)
        constelacion.move_to([0.0, 0.3, 0.0])
        self.play(FadeIn(constelacion), run_time=0.8)
        self.play(sat.AnimarWalker(constelacion), run_time=2.4,
                  rate_func=linear)

        # --- geometria del pase y del tren (reusada, no recalculada) ----
        pase = ntn.pase_leo(ALTURA_KM, INCLINACION_DEG, LAT_GS, LON_GS)
        h = ntn.handover(n_sats=3, h_km=ALTURA_KM, inc_deg=INCLINACION_DEG,
                         lat_gs=LAT_GS, lon_gs=LON_GS,
                         raan_deg=pase["raan_deg"], solape=SOLAPE_ESCENA)
        ref = h["pase_ref"]
        t0 = ref["aos_abs_s"] - 0.15 * ref["duracion_s"]
        t_abs = h["t_s"] + t0

        grupo_mapa = ntn.traza_tierra(pase, alto_escena=fg.activa()
                                      .frame_height * 0.78)
        grupo_mapa.shift([0.0, -0.35, 0.0])
        mapa, traza_dim, _visible_sin_usar, estacion = grupo_mapa
        fg.exigir_dentro(mapa, margen_pt=4.0, que="mapa")

        # --- momento 2: una estacion, de cerca ---------------------------
        self.play(transiciones.transicion_zoom(constelacion, mapa))
        self.play(Create(traza_dim), run_time=1.0)
        self.play(particulas.materializar(estacion), run_time=0.8)

        psi_deg = sat.angulo_cobertura(ALTURA_KM, ref["elev_min_deg"])
        huella_lonlat = _huella(LAT_GS, LON_GS, psi_deg)
        huella_xyz = sat.puntos_en_mapa(mapa, huella_lonlat)
        huella = VMobject(stroke_color=fg.tema()["apagado"], stroke_width=1.0,
                          stroke_opacity=0.55, fill_opacity=0.0)
        huella.set_points_smoothly([np.array([p[0], p[1], 0.0])
                                    for p in huella_xyz])
        huella_glow = brillo.con_brillo(huella, color=fg.tema()["apagado"],
                                        capas=3, ancho_max=6, opacidad=0.15)
        halo_estacion = brillo.con_brillo(estacion, color=fg.tema()["tinta"],
                                          capas=4, ancho_max=9, opacidad=0.3)
        etiqueta = fg.texto("LEO-600", 9.0, fg.tema()["apagado"])
        fg.poner(etiqueta, [-fg.activa().frame_width / 2 + 12.0 / ppu,
                            -fg.activa().frame_height / 2 + 12.0 / ppu, 0.0],
                anclaje=fg.IZQ + fg.ABJ)
        fg.exigir_dentro(etiqueta, margen_pt=4.0, que="etiqueta LEO-600")
        self.play(FadeIn(huella_glow), FadeIn(halo_estacion),
                  FadeIn(etiqueta), run_time=0.6)

        # --- el tren: brillo que sube y baja con la elevacion real -------
        n_sats = h["n_sats"]
        posiciones = [sat.puntos_en_mapa(
            mapa, sat._subsat_uno(t_abs, ALTURA_KM, INCLINACION_DEG,
                                  ref["raan_deg"],
                                  fase0=ntn.fase0_k(k, h["paso_fase"])))
            for k in range(n_sats)]
        elevaciones = h["elev"]
        visibilidad = np.clip(elevaciones / 18.0, 0.0, 1.0) ** 1.4
        # 0.12 = la misma opacidad de "satelite oculto" de ConstelacionWalker:
        # nunca invisible del todo, apenas insinuado cuando no sirve.
        opacidades = 0.12 + 0.88 * visibilidad
        T = t_abs.size

        puntos = VGroup(*[brillo.punto_brillante(color=fg.color(1),
                                                  radio=0.045, capas=5)
                          for _ in range(n_sats)])
        numero = DecimalNumber(0, num_decimal_places=0,
                               font_size=fg.fs_para_pt(10.0), color=fg.color(1))
        movil = VGroup(puntos, numero)

        def _actualizar(mob, alpha):
            i = int(round(alpha * (T - 1)))
            for k in range(n_sats):
                puntos[k].move_to(posiciones[k][i])
                puntos[k].set_opacity(float(opacidades[k, i]))
            numero.move_to(posiciones[0][i] + fg.ARR * (11.0 / ppu))
            numero.set_value(max(0, int(round(elevaciones[0, i]))))
            numero.set_opacity(float(opacidades[0, i]))

        _actualizar(movil, 0.0)
        self.add(movil)
        self.play(UpdateFromAlphaFunc(movil, _actualizar), run_time=15.5,
                  rate_func=linear)

        # --- cierre: sin statement, el hueco ya se vio -------------------
        self.play(FadeOut(movil), FadeOut(traza_dim), FadeOut(huella_glow),
                  FadeOut(halo_estacion), FadeOut(estacion), FadeOut(mapa),
                  FadeOut(etiqueta), run_time=1.0)
        self.wait(0.2)
        self.add(fg.sello(extra="LEO-600 ilustrativo, tren con hueco puesto en escena"))
        self.wait(1.3)
