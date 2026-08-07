import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import *
from code_brand import FUENTE_HUD, registrar_fuentes
from control import (COLOR_CTRL, COLOR_MAL, COLOR_OK, COLOR_REF, COLOR_SIS,
                     barras_metricas, curva_windup, lazo_cerrado, masa_resorte,
                     plano_s, polo, rampa_con_rezago, respuesta_escalon)


class DemoControl(Scene):
    """Demo de control.py: la masa-resorte que se estira y rebota, el plano s
    con un par de polos que cruzan al semiplano inestable, la respuesta al
    escalon de zeta 0.056 transformada a 0.7, el lazo cerrado con su flujo,
    la rampa con rezago que se funde a cero, el windup con su exceso rojo y
    su remedio, y las barras de metricas hundiendose al sintonizar.

    Todo es geometrico y determinista: mismo script, mismo render. Los
    localizadores (.punto, .punto_en, .brecha_en, .re/.im) se leen de la
    geometria actual, asi que los tags caen solos donde deben.
    """

    def construct(self):
        registrar_fuentes()
        titulo = Text("Control", font_size=28, color=COLOR_REF)
        titulo.to_edge(UP, buff=0.3)
        self.add(titulo)

        # --- acto 1: el sistema de segundo orden, estirado y suelto ---
        mr = masa_resorte(ancho=3.0).move_to(DOWN * 0.3)
        tag_mr = Text("m x'' + b x' + k x = F", font=FUENTE_HUD, font_size=16,
                      color=COLOR_CTRL)
        tag_mr.next_to(mr, DOWN, buff=0.45)
        self.play(FadeIn(mr), FadeIn(tag_mr), run_time=0.5)
        self.play(mr.animate.estirar(0.9), run_time=0.6)
        for dx in (-0.55, 0.34, -0.2, 0.1, 0.0):
            self.play(mr.animate.estirar(dx), run_time=0.24,
                      rate_func=rate_functions.ease_in_out_sine)
        self.play(FadeOut(VGroup(mr, tag_mr)), run_time=0.3)

        # --- acto 2: el plano s y el caracter de la respuesta ---
        plano = plano_s(ancho=4.2, alto=2.9).move_to(LEFT * 3.5 + DOWN * 0.35)
        p1 = polo(plano, -1.6, 0.9)
        p2 = polo(plano, -1.6, -0.9)
        resp = respuesta_escalon(zeta=0.056, wn=2.24, ancho=4.4, alto=2.15)
        resp.move_to(RIGHT * 3.3 + DOWN * 0.35)

        self.play(FadeIn(plano), FadeIn(p1), FadeIn(p2),
                  Create(resp.ejes), Create(resp.linea_ref),
                  FadeIn(resp.etiquetas), run_time=0.7)
        self.play(Create(resp.curva), run_time=0.6)

        calmada = respuesta_escalon(zeta=0.7, wn=2.24, ancho=4.4, alto=2.15,
                                    color=COLOR_OK)
        calmada.move_to(resp.get_center())
        self.play(ReplacementTransform(resp, calmada),
                  p1.animate.move_to(plano.punto(-3.0, 0.5)),
                  p2.animate.move_to(plano.punto(-3.0, -0.5)), run_time=0.8)

        self.play(p1.animate.set_color(COLOR_MAL).move_to(plano.punto(1.6, 0.9)),
                  p2.animate.set_color(COLOR_MAL).move_to(plano.punto(1.6, -0.9)),
                  run_time=0.7)
        lectura = Text(f"s = {p1.re:+.1f} {p1.im:+.1f}j", font=FUENTE_HUD,
                       font_size=15, color=COLOR_MAL)
        lectura.next_to(plano, DOWN, buff=0.2)
        self.play(FadeIn(lectura), Indicate(plano.zona_inestable,
                                            color=COLOR_MAL, scale_factor=1.0),
                  run_time=0.4)
        self.play(FadeOut(VGroup(plano, p1, p2, calmada, lectura)), run_time=0.3)

        # --- acto 3: cerrar el lazo y ver correr la señal ---
        lazo = lazo_cerrado(ancho=6.6).move_to(UP * 0.15)
        self.play(FadeIn(lazo.etiquetas), FadeIn(lazo.control),
                  FadeIn(lazo.planta), FadeIn(lazo.sumador),
                  GrowArrow(lazo.flecha_r), GrowArrow(lazo.flecha_control),
                  GrowArrow(lazo.flecha_planta), GrowArrow(lazo.flecha_y),
                  run_time=0.7)
        self.play(Create(lazo.trazo_retro), FadeIn(lazo.punta_retro),
                  FadeIn(lazo.nodo), run_time=0.5)
        self.play(Succession(*[
            ShowPassingFlash(tramo.copy().set_stroke(color=COLOR_REF, width=6,
                                                     opacity=1).set_fill(opacity=0),
                             time_width=0.5, run_time=0.20)
            for tramo in lazo.camino()]))
        eti_error = Text("e = r - y", font=FUENTE_HUD, font_size=17,
                         color=COLOR_REF)
        eti_error.next_to(lazo, DOWN, buff=0.3)
        self.play(FadeIn(eti_error), run_time=0.3)
        self.play(FadeOut(VGroup(lazo, eti_error)), run_time=0.3)

        # --- acto 4: la rampa que nunca alcanzas ---
        rampa = rampa_con_rezago(ancho=5.2, alto=2.2, rezago=0.14)
        rampa.move_to(DOWN * 0.35)
        p_ref, p_sis = rampa.brecha_en(0.62)
        # Doble punta: la brecha es estrecha (0.14 de rezago sobre un alto de
        # 2.2 son apenas 0.27 unidades) y una sola cabeza se lee como un
        # borron. El tag va ABAJO a la derecha, en el hueco libre bajo la
        # curva cian: al lado cruzaba las dos rectas y no se leia.
        flecha = DoubleArrow(p_sis, p_ref, buff=0.0, color=COLOR_MAL,
                             stroke_width=3.0, tip_length=0.1,
                             max_tip_length_to_length_ratio=0.5)
        tag_rezago = Text("rezago", font=FUENTE_HUD, font_size=15,
                          color=COLOR_MAL)
        tag_rezago.next_to(flecha, DOWN + RIGHT, buff=0.22)
        self.play(FadeIn(rampa.ejes), FadeIn(rampa.etiquetas),
                  Create(rampa.ref), Create(rampa.sis), run_time=0.7)
        self.play(GrowArrow(flecha), FadeIn(tag_rezago), run_time=0.4)

        alcanza = rampa_con_rezago(ancho=5.2, alto=2.2, rezago=0.0,
                                   color_sis=COLOR_OK)
        alcanza.move_to(rampa.get_center())
        self.play(ReplacementTransform(rampa, alcanza),
                  FadeOut(flecha), FadeOut(tag_rezago), run_time=0.8)
        self.play(FadeOut(alcanza), run_time=0.3)

        # --- acto 5: windup y su remedio ---
        wu = curva_windup(ancho=5.2, alto=2.2).move_to(DOWN * 0.35)
        self.play(FadeIn(wu.ejes), FadeIn(wu.etiquetas), Create(wu.linea_ref),
                  Create(wu.curva), run_time=0.7)
        self.play(Indicate(wu.exceso, color=COLOR_MAL, scale_factor=1.0),
                  run_time=0.4)
        limpia = curva_windup(ancho=5.2, alto=2.2, con_antiwindup=True,
                              color=COLOR_OK)
        limpia.move_to(wu.get_center())
        self.play(ReplacementTransform(wu, limpia), run_time=0.8)
        eti_clamp = Text("CLAMPING", font=FUENTE_HUD, font_size=15,
                         color=COLOR_OK)
        eti_clamp.next_to(limpia, UP, buff=0.15)
        self.play(FadeIn(eti_clamp), run_time=0.3)
        self.play(FadeOut(VGroup(limpia, eti_clamp)), run_time=0.3)

        # --- acto 6: sintonizar hasta que las metricas se hundan ---
        metricas = barras_metricas([0.9, 0.85, 0.95], ancho=4.0, alto=2.0)
        metricas.move_to(DOWN * 0.2)
        self.play(FadeIn(metricas), run_time=0.5)
        finas = barras_metricas([0.15, 0.1, 0.12], ancho=4.0, alto=2.0,
                                color=COLOR_OK)
        finas.move_to(metricas.get_center())
        self.play(ReplacementTransform(metricas, finas), run_time=0.8)
        self.wait(0.6)
