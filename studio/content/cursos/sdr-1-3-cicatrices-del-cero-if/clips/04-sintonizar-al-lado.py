class Clip4(Scene):
    """1.3.4 - Sintonizar al lado: retunear el LO 250 kHz aparta el canal
    de la fuga de DC (que sigue en 0 Hz); el NCO en software trae el canal
    de vuelta a cero, y la cicatriz de DC queda fuera de la banda. Cierre
    de la leccion. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Sintonizar al lado"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        # --- estado 1: LO retuneado, el canal cae en +250 kHz ---------------
        ruido = XN - XL
        canal = S.tono(OFFSET, FS, len(XN)) + ruido
        y1 = S.con_dc(canal, -12.0)
        y2 = S.desplazar(y1, OFFSET, FS)
        f, db1 = S.espectro_db(y1, FS, nfft=2048)
        _, db2 = S.espectro_db(y2, FS, nfft=2048)
        fr, dbr1 = S.para_dibujar(f, db1, puntos=900, f_lo=-4.5e5,
                                  f_hi=4.5e5)
        _, dbr2 = S.para_dibujar(f, db2, puntos=900, f_lo=-4.5e5, f_hi=4.5e5)

        esp = S.Espectro(fr, dbr1, piso=-85.0, techo=3.0, ancho=11.6,
                         alto=4.0, color=C_SENAL)
        esp.move_to(ORIGIN)
        ticks = esp.marcas([-4e5, -2e5, 0.0, 2e5, 4e5],
                           ["-400", "-200", "0", "200", "400"])
        u = tag_junto(ticks[-1], "kHz", RIGHT, buff=0.2, font_size=20)
        self.play(Create(esp.ejes), FadeIn(ticks), FadeIn(u), run_time=0.8)
        self.play(Create(esp.curva), FadeIn(esp.area), run_time=1.8)
        self.wait(0.6)

        banda1 = esp.banda(OFFSET - 1e5, OFFSET + 1e5, color=C_OK,
                           opacidad=0.16)
        marca1 = esp.marca_f(0.0, color=C_RUIDO)
        tag_marca = tag_junto(marca1, "fuga del LO", UP, buff=0.16,
                              font_size=20, color=C_RUIDO)
        self.play(FadeIn(banda1), run_time=0.7)
        self.play(Create(marca1), FadeIn(tag_marca), run_time=0.6)
        self.wait(1.4)
        rot.mostrar(dato_pie("LO desplazado 250 kHz"), zona="abajo",
                    run_time=0.5)
        self.wait(3.2)

        # --- el NCO trae el canal a cero en software -------------------------
        nco = Circle(radius=0.22, color=C_LO, stroke_width=2.4)
        nco.move_to(esp.en(OFFSET, 1.6) + UP * 0.62)
        xs = np.linspace(-0.14, 0.14, 26)
        onda = VMobject(stroke_color=C_LO, stroke_width=2.0)
        onda.set_points_smoothly([nco.get_center() + np.array(
            [x, 0.08 * math.sin(x / 0.14 * 2 * math.pi), 0]) for x in xs])
        et_nco = tag_junto(nco, "NCO", RIGHT, buff=0.18, font_size=20,
                           color=C_LO)
        flecha = Arrow(esp.en(OFFSET, 1.6), esp.en(0.0, 1.6), color=C_LO,
                       buff=0.08, stroke_width=3.2)
        self.play(FadeIn(nco), Create(onda), FadeIn(et_nco), run_time=0.7)
        self.wait(0.5)
        self.play(GrowArrow(flecha), run_time=0.8)
        self.wait(0.8)

        esp2 = esp.con_db(dbr2, color=C_SENAL)
        banda2 = esp.banda(-1e5, 1e5, color=C_OK, opacidad=0.16)
        marca2 = esp.marca_f(-OFFSET, color=C_RUIDO)
        tag_marca2 = tag_junto(marca2, "fuga del LO", UP, buff=0.16,
                               font_size=20, color=C_RUIDO)
        self.play(Transform(esp.curva, esp2.curva),
                  Transform(esp.area, esp2.area),
                  Transform(banda1, banda2),
                  Transform(marca1, marca2),
                  Transform(tag_marca, tag_marca2),
                  FadeOut(flecha), run_time=2.0)
        self.wait(1.2)
        rot.mostrar(cifra_pie(f"canal: +{OFFSET / 1e3:.0f} kHz -> 0"),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        cierre_leccion(self, rot, "El hardware barato deja cicatrices.",
                       "El software las cura.", esp.ejes, ticks, u,
                       esp.curva, esp.area, banda1, marca1, tag_marca,
                       nco, onda, et_nco)
