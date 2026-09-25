from comunicaciones import Onda  # noqa: E402


class Clip1(Scene):
    """6.1.1 - La magnitud |IQ| de una captura ADS-B a 2 MS/s: la rafaga de
    pulsos del preambulo y el mensaje. Zoom a los primeros 8 bits (DF+CA):
    se lee directo, muestra contra muestra, si el par es alto-bajo (1) o
    bajo-alto (0). (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Pulsos a 1090"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        fs_mhz = 2.0
        t_us = np.arange(len(MAG)) / fs_mhz
        techo = float(MAG.max()) * 1.15

        vista = Onda(t_us, MAG, rango_y=(-0.15, techo), ancho=11.6,
                     alto=2.0, color=C_SENAL, grosor=2.0)
        vista.move_to(UP * 1.6)
        u_top = tag_junto(vista.ejes[0], "us", RIGHT, buff=0.18,
                          font_size=18, color=C_TENUE)
        self.play(Create(vista.ejes), run_time=0.5)
        self.wait(0.2)
        self.play(Create(vista.curva), FadeIn(u_top), run_time=2.0)
        self.wait(2.8)

        rot.mostrar(dato_pie("SNR 12 dB"), zona="abajo", run_time=0.5)
        self.wait(2.6)

        # --- banda que marca los 8 bits que se amplian ----------------
        i0 = OFF + 16   # tras el preambulo de 8 us (16 muestras)
        i1 = i0 + 16    # 8 bits, 2 muestras cada uno
        xa = vista.en(t_us[i0], 0.0)[0]
        xb = vista.en(t_us[i1 - 1], 0.0)[0]
        banda = Rectangle(width=abs(xb - xa) + 0.22, height=vista.alto,
                          stroke_color=C_CALCULO, stroke_width=2.0,
                          fill_color=C_CALCULO, fill_opacity=0.16)
        banda.move_to(np.array([(xa + xb) / 2.0, vista.get_center()[1],
                                0.0]))
        self.play(FadeIn(banda), run_time=0.7)
        self.wait(2.2)

        # --- el zoom: 8 bits en microsegundos relativos -----------------
        t_rel = np.arange(i1 - i0) / fs_mhz
        zoom = Onda(t_rel, MAG[i0:i1], rango_y=(-0.15, techo), ancho=9.4,
                    alto=1.8, color=C_SENAL, grosor=3.4)
        zoom.move_to(DOWN * 0.9)
        flecha = Arrow(banda.get_bottom(), zoom.ejes.get_top(), buff=0.08,
                       color=C_CALCULO, stroke_width=2.6,
                       max_tip_length_to_length_ratio=0.22)
        self.play(GrowArrow(flecha), run_time=0.5)
        self.play(Create(zoom.ejes), run_time=0.4)
        self.play(Create(zoom.curva), run_time=1.3)
        self.wait(1.8)

        et_0 = tag_hud("0", font_size=18, color=C_TENUE)
        et_0.next_to(zoom.en(0.0, -0.15), DOWN, buff=0.14)
        et_8 = tag_hud("8", font_size=18, color=C_TENUE)
        et_8.next_to(zoom.en(float(i1 - i0) / fs_mhz - 0.5, -0.15), DOWN,
                     buff=0.14)
        u_zoom = tag_junto(zoom.ejes[0], "us", RIGHT, buff=0.16,
                           font_size=18, color=C_TENUE)
        self.play(FadeIn(et_0), FadeIn(et_8), FadeIn(u_zoom), run_time=0.5)
        self.wait(1.6)

        bits8 = [int(b) for b in BITS[:8]]
        digitos = VGroup()
        for k, b in enumerate(bits8):
            tm = (t_rel[2 * k] + t_rel[2 * k + 1]) / 2.0
            d = tag_hud(str(b), font_size=20, color=C_CALCULO)
            d.move_to(zoom.en(tm, -0.15) + DOWN * 0.42)
            digitos.add(d)
        self.play(FadeIn(digitos, lag_ratio=0.12), run_time=1.6)
        self.wait(5.6)

        self.play(FadeOut(banda), FadeOut(flecha), run_time=0.6)
        self.wait(3.0)
