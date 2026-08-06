import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import *
from apuntado import (COLOR_ANTENA, COLOR_EJE, COLOR_OK, COLOR_PELIGRO,
                      COLOR_SAT, aguja_velocidad, antena, cono_keyhole,
                      curva_s_doppler, curvas_seguimiento, mascara_elevacion,
                      tarjeta_tle, traza_pase, vista_polar)
from code_brand import FUENTE_HUD, registrar_fuentes


class DemoApuntado(Scene):
    """Demo de apuntado.py: vista polar con mascara y pase, antena que sigue
    al satelite, keyhole, tarjeta TLE con un campo resaltado, la S del
    Doppler y el lazo de seguimiento con su aguja de velocidad.

    Todo es geometrico y determinista: mismo script, mismo render. Los
    localizadores (.punto_en, .el_en, .brecha_en, .pivote) se leen de la
    geometria actual, asi que los tags caen solos donde deben.
    """

    def construct(self):
        registrar_fuentes()
        titulo = Text("Apuntar a un satélite", font_size=28, color=COLOR_SAT)
        titulo.to_edge(UP, buff=0.3)
        self.add(titulo)

        # --- acto 1: la boveda, el pase y la antena que lo sigue ---
        vista = vista_polar(radio=2.05).move_to(LEFT * 3.7 + DOWN * 0.6)
        mascara = mascara_elevacion(vista, el_min=8.0)
        traza = traza_pase(vista, el_max=72.0, az_culminacion=25.0)
        keyhole = cono_keyhole(vista, radio_deg=8.0)
        ant = antena(escala=1.0).move_to(RIGHT * 3.6 + DOWN * 1.1)
        sat = Dot(traza.punto_en(0.0), radius=0.08, color=COLOR_SAT)
        sat.set_z_index(6)

        self.play(Create(vista.anillos), FadeIn(vista.cruces),
                  FadeIn(vista.cardinales), FadeIn(vista.grados),
                  run_time=0.9)
        self.play(FadeIn(mascara), FadeIn(ant), run_time=0.5)
        self.play(Create(traza), FadeIn(sat), run_time=0.8)

        vt = ValueTracker(0.0)
        sat.add_updater(lambda m: m.move_to(traza.punto_en(vt.get_value())))
        ant.add_updater(lambda m: m.orientar(traza.el_en(vt.get_value())))
        self.play(vt.animate.set_value(0.5), run_time=1.3, rate_func=linear)

        lectura = Text(f"EL {traza.el_en(0.5):.0f}°   AZ {traza.az_en(0.5):.0f}°",
                       font=FUENTE_HUD, font_size=17, color=COLOR_ANTENA)
        lectura.next_to(ant, DOWN, buff=0.3)
        self.play(FadeIn(keyhole), FadeIn(lectura), run_time=0.5)
        self.play(vt.animate.set_value(1.0), run_time=1.3, rate_func=linear)
        sat.clear_updaters()
        ant.clear_updaters()
        self.play(FadeOut(VGroup(vista, mascara, traza, keyhole, ant, sat,
                                 lectura)), run_time=0.4)

        # --- acto 2: el TLE y la S del Doppler ---
        tarjeta = tarjeta_tle().move_to(UP * 1.75)
        curva = curva_s_doppler(ancho=5.2, alto=2.2).move_to(DOWN * 1.35)
        campo = tarjeta.campos["movimiento_medio"]

        self.play(FadeIn(tarjeta), run_time=0.6)
        self.play(Indicate(campo, color=COLOR_OK, scale_factor=1.35),
                  run_time=0.8)
        campo.set_color(COLOR_OK)
        tag_campo = Text("movimiento medio: 15.5 vueltas/dia", font=FUENTE_HUD,
                         font_size=15, color=COLOR_OK)
        tag_campo.next_to(tarjeta, DOWN, buff=0.18)

        self.play(FadeIn(tag_campo), Create(curva.ejes),
                  Create(curva.linea_f0), FadeIn(curva.etiquetas),
                  run_time=0.6)
        self.play(Create(curva.curva), run_time=0.8)

        senal = Dot(curva.punto_en(0.0), radius=0.075, color=COLOR_SAT)
        senal.set_z_index(6)
        vs = ValueTracker(0.0)
        senal.add_updater(lambda m: m.move_to(curva.punto_en(vs.get_value())))
        self.add(senal)
        self.play(vs.animate.set_value(1.0), run_time=1.2, rate_func=linear)
        senal.clear_updaters()
        self.play(FadeOut(VGroup(tarjeta, tag_campo, curva, senal)),
                  run_time=0.4)

        # --- acto 3: el lazo que persigue y la aguja del keyhole ---
        seg = curvas_seguimiento(ancho=4.9, alto=2.1, retraso=0.18)
        seg.move_to(LEFT * 3.3 + DOWN * 0.5)
        medidor = aguja_velocidad(maximo=10.0, valor=1.0, ancho=2.6)
        medidor.move_to(RIGHT * 3.7 + DOWN * 0.9)

        self.play(Create(seg.ref), FadeIn(seg.ejes), FadeIn(seg.etiquetas),
                  FadeIn(medidor), run_time=0.9)
        self.play(Create(seg.ant), run_time=0.6)

        p_ref, p_ant = seg.brecha_en(0.6)
        flecha = Arrow(p_ant, p_ref, buff=0.0, color=COLOR_PELIGRO,
                       stroke_width=3.2, max_tip_length_to_length_ratio=0.35)
        tag_error = Text("error", font=FUENTE_HUD, font_size=15,
                         color=COLOR_PELIGRO)
        tag_error.next_to(flecha, RIGHT, buff=0.12)
        self.play(GrowArrow(flecha), FadeIn(tag_error), run_time=0.5)

        ang = medidor.a_valor(9.0)
        self.play(Rotate(medidor.aguja, ang - medidor.angulo,
                         about_point=medidor.pivote), run_time=0.9)
        lectura_v = Text(f"{medidor.valor:.1f} °/s", font=FUENTE_HUD,
                         font_size=17, color=COLOR_PELIGRO)
        lectura_v.next_to(medidor, DOWN, buff=0.25)
        self.play(FadeIn(lectura_v), run_time=0.3)

        enganchado = curvas_seguimiento(ancho=4.9, alto=2.1, retraso=0.0,
                                        color_ant=COLOR_OK)
        enganchado.move_to(seg.get_center())
        self.play(ReplacementTransform(seg, enganchado),
                  FadeOut(flecha), FadeOut(tag_error), run_time=1.0)
        tag_ok = Text("enganchado", font=FUENTE_HUD, font_size=16,
                      color=COLOR_OK)
        tag_ok.next_to(enganchado, DOWN, buff=0.2)
        self.play(FadeIn(tag_ok), run_time=0.3)
        self.wait(1.0)
