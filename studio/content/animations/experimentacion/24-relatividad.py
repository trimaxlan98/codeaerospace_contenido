import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import *
from relatividad import (ALTURA_ISS, COLOR_ERROR, COLOR_EJE, COLOR_LUZ,
                         COLOR_SATELITE, COLOR_TIERRA, FREQ_GPS, RADIO_GPS,
                         RADIO_TIERRA, carita_reloj, curva_deriva,
                         curva_gamma, curvas_muones, derivas_gps,
                         fila_pulsos, frac_muones, frecuencia_fabrica,
                         gamma, mapa_error, orbita_gps, pozo_potencial,
                         reloj_luz, trilateracion)
from code_brand import FUENTE_HUD, registrar_fuentes


class DemoRelatividad(Scene):
    """Demo de relatividad.py: el reloj de luz en reposo contra beta=0.6
    con su hipotenusa MEDIDA, la curva gamma con ese mismo punto
    rotulado, el satelite GPS dando media vuelta junto a la carita de
    reloj reproducible, la trilateracion sin y con sesgo con su
    triangulo de error medido, las curvas de supervivencia de muones
    junto al pozo de potencial, y por ultimo la curva de deriva contra
    altura (con ISS y GPS marcados), el mapa de error creciendo y el
    tren de pulsos de fabrica contra el de orbita.

    Todo es determinista: mismo script, mismo render. Los numeros
    (gamma, derivas, fracciones, frecuencias) salen de las piezas,
    medidos o calculados por sus funciones, nunca a mano.
    """

    def construct(self):
        registrar_fuentes()
        titulo = Text("Relatividad y el GPS", font_size=26,
                      color=COLOR_SATELITE)
        titulo.to_edge(UP, buff=0.22)
        self.add(titulo)

        # --- acto 1: el reloj de luz y su gamma ---
        reloj = reloj_luz(beta=0.0, alto=1.3, tics=3, margen=0.3)
        reloj.move_to(LEFT * 4.3 + UP * 1.2)
        self.play(FadeIn(reloj.espejos), run_time=0.4)
        self.play(LaggedStart(*[Create(t) for t in reloj.camino],
                              lag_ratio=0.5), FadeIn(reloj.foton),
                  run_time=0.8)
        self.wait(0.2)

        reloj_mov = reloj.con_beta(0.6)
        self.play(Transform(reloj, reloj_mov), run_time=1.0)
        etiqueta_reloj = Text(
            f"camino/alto = {reloj_mov.longitud_camino():.2f}  "
            f"(gamma = {gamma(0.6):.2f})", font=FUENTE_HUD, font_size=13,
            color=COLOR_LUZ)
        etiqueta_reloj.next_to(reloj, DOWN, buff=0.25)
        self.play(FadeIn(etiqueta_reloj), run_time=0.4)
        self.play(UpdateFromAlphaFunc(
            reloj.foton, lambda m, al: m.move_to(reloj.punto_camino(al))),
            run_time=1.4, rate_func=linear)
        self.wait(0.3)

        curva = curva_gamma(beta_max=0.9, ancho=4.2, alto=2.4)
        curva.move_to(RIGHT * 3.2 + UP * 1.2)
        self.play(FadeIn(curva.ejes), run_time=0.3)
        self.play(Create(curva.curva), run_time=1.0)
        punto_g = Dot(curva.en(0.6), radius=0.07, color=COLOR_SATELITE)
        etiqueta_g = Text(f"gamma(0.6) = {gamma(0.6):.2f}", font=FUENTE_HUD,
                          font_size=13, color=COLOR_SATELITE)
        etiqueta_g.next_to(punto_g, UP, buff=0.15)
        self.play(FadeIn(punto_g), FadeIn(etiqueta_g), run_time=0.5)
        self.wait(0.4)
        self.play(FadeOut(reloj), FadeOut(etiqueta_reloj), FadeOut(curva),
                  FadeOut(punto_g), FadeOut(etiqueta_g), run_time=0.4)

        # --- acto 2: la orbita GPS y la carita de reloj ---
        orb = orbita_gps(radio_escena=2.2, alpha0=0.0)
        orb.move_to(LEFT * 3.6 + DOWN * 0.3)
        self.play(FadeIn(orb.tierra), FadeIn(orb.orbita),
                  FadeIn(orb.satelite), run_time=0.5)
        self.play(UpdateFromAlphaFunc(orb, lambda m, al: m.en(al * 0.5)),
                  run_time=2.2, rate_func=linear)
        self.wait(0.3)

        sr, gr, neta = derivas_gps()
        reloj_c = carita_reloj(radio=0.5)
        reloj_c.move_to(RIGHT * 3.4 + DOWN * 0.3)
        etiqueta_c = Text(f"neta = {neta:+.2f} us/dia", font=FUENTE_HUD,
                          font_size=13, color=COLOR_SATELITE)
        etiqueta_c.next_to(reloj_c, DOWN, buff=0.2)
        self.play(FadeIn(reloj_c), FadeIn(etiqueta_c), run_time=0.5)
        self.play(UpdateFromAlphaFunc(reloj_c, lambda m, al: m.en(al)),
                  run_time=1.6, rate_func=linear)
        self.wait(0.3)
        self.play(FadeOut(orb), FadeOut(reloj_c), FadeOut(etiqueta_c),
                  run_time=0.4)

        # --- acto 3: trilateracion, con y sin sesgo ---
        tri = trilateracion()
        tri.move_to(UP * 0.3)
        self.play(FadeIn(tri.receptor), FadeIn(tri.satelites), run_time=0.4)
        self.play(*[Create(c) for c in tri.circulos], run_time=0.8)
        self.wait(0.3)

        tri_sesgo = tri.con_sesgo(0.35)
        err = tri_sesgo.triangulo_error()
        self.play(Transform(tri, tri_sesgo), run_time=1.0)
        etiqueta_err = Text(f"lado medio del error = {err.lado_medio:.2f}",
                            font=FUENTE_HUD, font_size=13, color=COLOR_ERROR)
        etiqueta_err.next_to(tri, DOWN, buff=0.3)
        self.play(FadeIn(err), FadeIn(etiqueta_err), run_time=0.5)
        self.wait(0.4)
        self.play(FadeOut(tri), FadeOut(err), FadeOut(etiqueta_err),
                  run_time=0.4)

        # --- acto 4: muones y el pozo de potencial ---
        muones = curvas_muones(ancho=3.0, alto=2.6)
        muones.move_to(LEFT * 4.2)
        self.play(FadeIn(muones.ejes), FadeIn(muones.suelo), run_time=0.3)
        self.play(Create(muones.clasica), Create(muones.relativista),
                  run_time=1.4)
        cla, rel = frac_muones()
        etiqueta_mu = Text(f"clasica {cla:.0e}   relativista {rel:.2f}",
                           font=FUENTE_HUD, font_size=13, color=COLOR_EJE)
        etiqueta_mu.next_to(muones, DOWN, buff=0.25)
        self.play(FadeIn(etiqueta_mu), run_time=0.4)
        self.wait(0.3)

        pozo = pozo_potencial(ancho=4.0, profundo=2.0)
        pozo.move_to(RIGHT * 3.2 + DOWN * 0.2)
        self.play(FadeIn(pozo.tierra), Create(pozo.curva), run_time=1.0)
        self.wait(0.4)
        self.play(FadeOut(muones), FadeOut(etiqueta_mu), FadeOut(pozo),
                  run_time=0.4)

        # --- acto 5: la curva de deriva, el mapa y los pulsos ---
        deriva_curva = curva_deriva(ancho=5.0, alto=2.6)
        deriva_curva.move_to(LEFT * 3.6 + UP * 0.3)
        self.play(FadeIn(deriva_curva.ejes), Create(deriva_curva.cero),
                  run_time=0.5)
        self.play(Create(deriva_curva.curva), run_time=1.4)

        altura_gps = RADIO_GPS - RADIO_TIERRA
        p_iss = Dot(deriva_curva.en(ALTURA_ISS), radius=0.06,
                   color=COLOR_TIERRA)
        p_gps = Dot(deriva_curva.en(altura_gps), radius=0.06,
                   color=COLOR_SATELITE)
        lab_iss = Text("ISS", font=FUENTE_HUD, font_size=12,
                       color=COLOR_TIERRA)
        lab_iss.next_to(p_iss, DOWN, buff=0.1)
        lab_gps = Text("GPS", font=FUENTE_HUD, font_size=12,
                       color=COLOR_SATELITE)
        lab_gps.next_to(p_gps, UP, buff=0.1)
        self.play(FadeIn(p_iss), FadeIn(p_gps), FadeIn(lab_iss),
                  FadeIn(lab_gps), run_time=0.5)
        etiqueta_empate = Text(
            f"empate en {deriva_curva.altura_cero() / 1000:.0f} km",
            font=FUENTE_HUD, font_size=13, color=COLOR_EJE)
        etiqueta_empate.next_to(deriva_curva, DOWN, buff=0.3)
        self.play(FadeIn(etiqueta_empate), run_time=0.4)
        self.wait(0.3)

        mapa = mapa_error(lado=2.2)
        mapa.move_to(RIGHT * 3.6 + UP * 1.5)
        self.play(FadeIn(mapa.caja), FadeIn(mapa.calles), FadeIn(mapa.pin),
                  run_time=0.5)
        self.play(UpdateFromAlphaFunc(mapa, lambda m, al: m.en(al * 6.0)),
                  run_time=1.6, rate_func=linear)
        etiqueta_mapa = Text(f"radio a 6 h = {mapa.radio_km(6.0):.1f} km",
                             font=FUENTE_HUD, font_size=12,
                             color=COLOR_ERROR)
        etiqueta_mapa.next_to(mapa, DOWN, buff=0.18)
        self.play(FadeIn(etiqueta_mapa), run_time=0.4)

        pulsos_fab = fila_pulsos(n=14, ancho=3.0, desfase=0.0,
                                 color=COLOR_LUZ)
        pulsos_fab.move_to(RIGHT * 3.6 + DOWN * 1.0)
        pulsos_orb = fila_pulsos(n=14, ancho=3.0, desfase=0.4,
                                 color=COLOR_SATELITE)
        pulsos_orb.move_to(RIGHT * 3.6 + DOWN * 1.7)
        etiqueta_pulsos = Text(
            f"fabrica {frecuencia_fabrica():.2f} Hz  vs  "
            f"nominal {FREQ_GPS:.0f} Hz", font=FUENTE_HUD, font_size=11,
            color=COLOR_EJE)
        etiqueta_pulsos.next_to(pulsos_orb, DOWN, buff=0.2)
        self.play(FadeIn(pulsos_fab), FadeIn(pulsos_orb),
                  FadeIn(etiqueta_pulsos), run_time=0.5)
        self.wait(0.5)

        self.play(*[FadeOut(m) for m in (
            deriva_curva, p_iss, p_gps, lab_iss, lab_gps, etiqueta_empate,
            mapa, etiqueta_mapa, pulsos_fab, pulsos_orb,
            etiqueta_pulsos)], run_time=0.5)
