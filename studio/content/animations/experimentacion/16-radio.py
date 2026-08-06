import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import *
from radio import (COLOR_EJE, COLOR_I, COLOR_OK, COLOR_Q, COLOR_RUIDO,
                   COLOR_SENAL, constelacion_bpsk, diagrama_ojo, fasor,
                   girar_fasor, onda_am, onda_fm, pico_espectral, plano_iq,
                   ventana_espectro, waterfall_imagen)


class DemoRadio(Scene):
    """Demo de radio.py: fasor IQ, ventana de espectro, AM/FM, waterfall,
    constelacion BPSK y diagrama de ojo.

    Todo es determinista (numpy con semilla): mismo script, mismo render.
    El waterfall es un ImageMobject, asi que sus tags viajan en `Group`.
    """

    def construct(self):
        titulo = Text("SDR: la radio hecha software", font_size=30,
                      color=COLOR_SENAL).to_edge(UP, buff=0.35)
        self.add(titulo)

        # --- acto 1: el fasor gira mientras el pico barre la ventana ---
        plano = plano_iq(radio=1.25).move_to(LEFT * 4.3 + DOWN * 0.5)
        f = fasor(plano, angulo=0.6)
        ventana = ventana_espectro(ancho=6.0, alto=2.1)
        ventana.move_to(RIGHT * 3.4 + DOWN * 0.4)
        pico = pico_espectral(ventana, f_rel=-0.6, altura=1.4)

        self.play(Create(plano), FadeIn(ventana), run_time=0.8)
        self.play(GrowFromPoint(f, plano.get_center()), FadeIn(pico),
                  run_time=0.5)

        vt = ValueTracker(-0.6)
        pico.add_updater(lambda m: m.move_to(
            np.array([ventana.x_de(vt.get_value()), m.get_center()[1], 0.0])))
        self.play(girar_fasor(f, 0.6 + 2 * PI, run_time=2.2),
                  vt.animate.set_value(0.75), run_time=2.2)
        pico.clear_updaters()
        marca = Text(f"fasor a {f.angulo:.2f} rad", font_size=18,
                     color=COLOR_EJE).next_to(plano, DOWN, buff=0.18)
        self.add(marca)
        self.wait(0.3)
        self.play(FadeOut(VGroup(plano, f, ventana, pico, marca)), run_time=0.4)

        # --- acto 2: AM arriba, FM abajo ---
        am = onda_am().move_to(UP * 1.5)
        fm = onda_fm().move_to(DOWN * 1.1)
        tag_am = Text("AM", font_size=20, color=COLOR_I)
        tag_am.next_to(am, LEFT, buff=0.25)
        tag_fm = Text("FM", font_size=20, color=COLOR_Q)
        tag_fm.next_to(fm, LEFT, buff=0.25)
        self.play(Create(am.portadora), FadeIn(tag_am), run_time=0.9)
        self.play(Create(am.envolvente), run_time=0.6)
        self.play(Create(fm.onda), FadeIn(tag_fm), run_time=0.9)
        self.wait(0.3)
        self.play(FadeOut(VGroup(am, fm, tag_am, tag_fm)), run_time=0.4)

        # --- acto 3: el waterfall y una firma marcada ---
        agua = waterfall_imagen().move_to(DOWN * 0.35)
        self.play(FadeIn(agua), run_time=0.7)
        centro_doppler = agua.pos_de(0.55, 0.5)
        marco = Rectangle(width=0.55, height=0.7, color=COLOR_SENAL,
                          stroke_width=2.5).move_to(centro_doppler)
        tag = Text("Doppler", font_size=18, color=COLOR_SENAL)
        tag.next_to(marco, RIGHT, buff=0.18)
        firmas = Group(agua, marco, tag)
        self.play(Create(marco), FadeIn(tag), run_time=0.6)
        self.wait(0.6)
        self.play(FadeOut(firmas), run_time=0.4)

        # --- acto 4: constelacion y ojo, limpios y con ruido ---
        plano2 = plano_iq(radio=1.15).move_to(LEFT * 3.6 + DOWN * 0.4)
        limpia = constelacion_bpsk(plano2, ruido=0.06)
        ojo = diagrama_ojo(ancho=4.4, alto=2.2).move_to(RIGHT * 3.3 + DOWN * 0.4)
        self.play(FadeIn(plano2), FadeIn(limpia),
                  LaggedStart(*[Create(t) for t in ojo.trazas],
                              lag_ratio=0.05, run_time=1.2),
                  run_time=1.2)
        self.wait(0.4)

        ruidosa = constelacion_bpsk(plano2, ruido=0.28, semilla=3)
        ojo_cerrado = diagrama_ojo(ancho=4.4, alto=2.2, ruido=0.30)
        ojo_cerrado.move_to(ojo.get_center())
        self.play(ReplacementTransform(limpia, ruidosa),
                  ReplacementTransform(ojo, ojo_cerrado), run_time=1.1)
        self.play(*[Indicate(d, color=COLOR_RUIDO, scale_factor=1.6)
                    for d in ruidosa.errados], run_time=0.8)
        for d in ruidosa.errados:
            d.set_color(COLOR_RUIDO)
        cuenta = Text(f"{len(ruidosa.errados)} bits errados", font_size=20,
                      color=COLOR_RUIDO).next_to(plano2, DOWN, buff=0.2)
        cerrado = Text("ojo cerrado", font_size=20, color=COLOR_RUIDO)
        cerrado.next_to(ojo_cerrado, DOWN, buff=0.2)
        self.play(FadeIn(cuenta), FadeIn(cerrado), run_time=0.5)
        self.wait(1.0)
