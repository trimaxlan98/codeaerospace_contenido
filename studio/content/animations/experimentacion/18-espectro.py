import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import *
from espectro import (COLOR_OK, COLOR_ONDA, COLOR_PERDIDA, barra_bandas,
                      curva_gases, curva_lluvia, gotas_y_onda, haz,
                      linea_tiempo, patron_antena, tierra_y_anillos)
from code_brand import FUENTE_HUD, registrar_fuentes


class DemoEspectro(Scene):
    """Demo de espectro.py: el mapa de bandas, el impuesto de la lluvia, las
    ventanas atmosfericas, el anillo lleno con su haz cruzado, el patron de
    antena y la linea de tiempo regulatoria.

    Todo es geometrico y determinista: mismo script, mismo render. Los
    localizadores (.centro_de, .punto_de, .estacion, .pos_gso, .direccion,
    .muesca) se leen de la geometria actual, asi que los tags y las flechas
    caen solos donde deben.
    """

    def construct(self):
        registrar_fuentes()
        titulo = Text("El espectro", font_size=28, color=COLOR_ONDA)
        titulo.to_edge(UP, buff=0.22)
        self.add(titulo)

        # --- acto 1: el mapa de bandas y el tamaño de la gota ---
        barra = barra_bandas(ancho=6.6, alto=0.75).move_to(UP * 1.65)
        self.play(FadeIn(barra.base), FadeIn(barra.huecos),
                  LaggedStart(*[FadeIn(g) for g in barra.grupos],
                              lag_ratio=0.08), run_time=1.0)
        self.play(Indicate(barra.segmento("Ka"), color=COLOR_OK,
                           scale_factor=1.12), run_time=0.7)
        tag_ka = Text("Ka: 13.5 GHz de sitio", font=FUENTE_HUD, font_size=15,
                      color=COLOR_OK)
        tag_ka.next_to(barra, UP, buff=0.16).shift(LEFT * 1.9)
        self.play(FadeIn(tag_ka), run_time=0.3)

        larga = gotas_y_onda(lambda_rel=1.0, ancho=2.9, alto=1.5)
        larga.move_to(LEFT * 3.6 + DOWN * 1.3)
        corta = gotas_y_onda(lambda_rel=0.15, ancho=2.9, alto=1.5)
        corta.move_to(RIGHT * 3.6 + DOWN * 1.3)
        tag_larga = Text("banda L", font=FUENTE_HUD, font_size=15,
                         color=COLOR_ONDA).next_to(larga, DOWN, buff=0.18)
        tag_corta = Text("banda Ka", font=FUENTE_HUD, font_size=15,
                         color=COLOR_PERDIDA).next_to(corta, DOWN, buff=0.18)
        self.play(FadeIn(larga.gotas), FadeIn(corta.gotas), run_time=0.4)
        self.play(Create(larga.onda), Create(corta.onda),
                  FadeIn(tag_larga), FadeIn(tag_corta), run_time=0.9)
        self.wait(0.2)
        self.play(FadeOut(VGroup(barra, tag_ka, larga, corta, tag_larga,
                                 tag_corta)), run_time=0.4)

        # --- acto 2: los gases con sus ventanas y el impuesto de la lluvia ---
        gases = curva_gases(ancho=5.4, alto=2.3)
        gases.move_to(LEFT * 3.5 + DOWN * 0.4)
        lluvia = curva_lluvia(ancho=4.6, alto=2.1)
        lluvia.move_to(RIGHT * 3.7 + DOWN * 0.4)
        self.play(Create(gases.ejes), FadeIn(gases.marcas),
                  FadeIn(gases.etiquetas), Create(lluvia.ejes),
                  FadeIn(lluvia.marcas), FadeIn(lluvia.etiquetas),
                  run_time=0.7)
        self.play(Create(gases.curva), run_time=0.9)

        pico = Dot(gases.punto_de(22.2), radius=0.07, color=COLOR_PERDIDA)
        muro = Dot(gases.punto_de(60.0), radius=0.08, color=COLOR_PERDIDA)
        for d in (pico, muro):
            d.set_z_index(6)
        tag_pico = Text("H2O · 22", font=FUENTE_HUD, font_size=14,
                        color=COLOR_PERDIDA).next_to(pico, LEFT, buff=0.10)
        tag_muro = Text("O2 · 60", font=FUENTE_HUD, font_size=14,
                        color=COLOR_PERDIDA).next_to(muro, UP, buff=0.10)
        self.play(FadeIn(pico), FadeIn(tag_pico), FadeIn(muro),
                  FadeIn(tag_muro), run_time=0.5)
        self.play(*gases.abrir_ventanas(), run_time=0.7)

        self.play(Create(lluvia.suave), Create(lluvia.intensa),
                  FadeIn(lluvia.tags), run_time=0.9)
        marca_20 = Dot(lluvia.punto_de(20.0), radius=0.07, color=COLOR_PERDIDA)
        marca_20.set_z_index(6)
        tag_20 = Text(f"{lluvia.db_km(20.0):.1f} dB/km", font=FUENTE_HUD,
                      font_size=14, color=COLOR_PERDIDA)
        tag_20.next_to(marca_20, UP + LEFT, buff=0.08)
        self.play(FadeIn(marca_20), FadeIn(tag_20), run_time=0.4)
        self.wait(0.25)
        self.play(FadeOut(VGroup(gases, pico, muro, tag_pico, tag_muro,
                                 lluvia, marca_20, tag_20)), run_time=0.4)

        # --- acto 3: el anillo lleno, el patron de antena y la regulacion ---
        tierra = tierra_y_anillos(radio_tierra=0.68, radio_gso=2.05,
                                  radio_ngso=1.22, sats_gso=12, sats_ngso=10)
        tierra.move_to(LEFT * 3.7 + UP * 0.55)
        patron = patron_antena(ancho=3.0).move_to(RIGHT * 3.5 + UP * 0.75)
        tiempo = linea_tiempo([("API", "2026"), ("EN SERVICIO", "2033"),
                               ("CADUCIDAD", "2033")], ancho=5.6)
        tiempo.move_to(DOWN * 2.55)

        self.play(FadeIn(tierra.tierra), Create(tierra.anillo_gso),
                  Create(tierra.anillo_ngso), FadeIn(tierra.rotulos),
                  run_time=0.7)
        self.play(LaggedStart(*[GrowFromCenter(d) for d in tierra.sats_gso],
                              lag_ratio=0.04),
                  LaggedStart(*[GrowFromCenter(d) for d in tierra.sats_ngso],
                              lag_ratio=0.05), run_time=0.6)

        estacion = Dot(tierra.estacion(-35.0), radius=0.06, color=COLOR_ONDA)
        estacion.set_z_index(7)
        objetivo = tierra.sat_gso_mas_cercano(tierra.pos_gso(-35.0))
        enlace = haz(estacion, objetivo, semiancho=0.13)
        self.play(FadeIn(estacion), FadeIn(enlace), run_time=0.45)

        # El grupo NGSO gira entero alrededor del centro de la Tierra: uno de
        # sus satelites entra en el haz (`.contiene` lo verifica sobre la
        # geometria ya rotada) y el enlace se pone rojo.
        self.play(Rotate(tierra.sats_ngso, np.deg2rad(4.0),
                         about_point=tierra.centro), run_time=0.6)
        dentro = [d for d in tierra.sats_ngso if enlace.contiene(d)]
        if dentro:
            self.play(enlace.animate.set_fill(color=COLOR_PERDIDA,
                                              opacity=0.32)
                      .set_stroke(color=COLOR_PERDIDA, opacity=0.9),
                      Indicate(dentro[0], color=COLOR_PERDIDA,
                               scale_factor=1.6), run_time=0.5)

        self.play(Create(patron.contorno), FadeIn(patron.eje),
                  FadeIn(patron.rotulo), Create(tiempo.linea),
                  FadeIn(tiempo.muescas), FadeIn(tiempo.puntos), run_time=0.8)

        eje = patron.direccion(0.0)
        flecha = Arrow(patron.punto_de(0.0) + eje * 1.25, patron.punto_de(0.0),
                       buff=0.0, color=COLOR_ONDA, stroke_width=3.2,
                       max_tip_length_to_length_ratio=0.3)
        self.play(GrowArrow(flecha),
                  LaggedStart(*[FadeIn(r) for r in tiempo.rotulos],
                              lag_ratio=0.25), run_time=0.6)
        self.play(Indicate(patron.principal, color=COLOR_PERDIDA,
                           scale_factor=1.0), run_time=0.4)

        lateral = patron.direccion(40.0)
        flecha_lat = Arrow(patron.punto_de(40.0) + lateral * 1.1,
                           patron.punto_de(40.0), buff=0.0, color=COLOR_ONDA,
                           stroke_width=2.4,
                           max_tip_length_to_length_ratio=0.3)
        recorre = Dot(tiempo.muesca(0), radius=0.08, color=COLOR_ONDA)
        recorre.set_z_index(8)
        self.play(FadeOut(flecha), GrowArrow(flecha_lat), FadeIn(recorre),
                  run_time=0.35)
        self.play(Indicate(patron.laterales, color=COLOR_OK, scale_factor=1.0),
                  recorre.animate.move_to(tiempo.muesca(2)), run_time=0.8)
        self.wait(0.6)
