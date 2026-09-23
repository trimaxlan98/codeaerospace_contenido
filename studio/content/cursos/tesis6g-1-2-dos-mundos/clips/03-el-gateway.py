class Clip3(Scene):
    """1.2.3 - La ruta terrestre no es refugio: el gateway se congestiona
    en un ciclo de 45 pasos que no coincide con la orbita de 60. El dibujo
    solo se repite cada 180 pasos, y con el jitter de la tesis, nunca igual.
    (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("El gateway se llena"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        n = REPITE
        t = np.arange(n)
        vis = T6.visibilidad_v2(n, E)[0]
        cg = T6.congestion_v2(n, E)
        ca = Cuadro((-6.0, 6.0, 0.55, 2.4), (0, n - 1), (0, 1))
        cb = Cuadro((-6.0, 6.0, -2.2, -0.35), (0, n - 1), (0, 1))
        ea = tag_hud(f"orbita: {E['orbita_periodo']} pasos", font_size=18, color=C_ADAPTA)
        ea.next_to(ca.p(0, 1), UP, buff=0.08).align_to(ca.p(0, 1), LEFT)
        eb = tag_hud(f"gateway: {E['gw_periodo']} pasos", font_size=18, color=C_NO)
        eb.next_to(cb.p(0, 1), UP, buff=0.08).align_to(cb.p(0, 1), LEFT)
        self.play(Create(ca.suelo()), Create(cb.suelo()), FadeIn(ea), FadeIn(eb), run_time=0.8)
        sv = ca.serie(t, vis, C_ADAPTA, 3.5, esquinas=False)
        sc = cb.serie(t, cg, C_NO, 3.5)
        self.play(Create(sv), Create(sc), run_time=5.0, rate_func=linear)
        self.wait(1.6)
        rot.mostrar(cifra_pie(f"pico = {fmt(100 * FRAC_CONG, 1)} % del ciclo"), zona="abajo",
                    run_time=0.5)
        self.wait(3.6)
        rot.mostrar(dato_pie(f"capacidad en pico {fmt(100 * E['gw_capacidad_pico'], 0)} %"),
                    zona="abajo", run_time=0.5)
        self.wait(3.4)

        # donde el dibujo vuelve a empezar igual: las dos fases alineadas
        marcas = VGroup(*[DashedLine(ca.p(k, 1.05), cb.p(k, -0.05), dash_length=0.1,
                                     stroke_color=CODE_INK, stroke_width=1.5)
                          for k in (0, n - 1)])
        self.play(Create(marcas), run_time=0.8)
        rot.mostrar(cifra_pie(f"se repite cada {REPITE} pasos"), zona="abajo", run_time=0.5)
        self.wait(3.6)

        # con el jitter de la tesis el pico se mueve en cada ciclo
        scj = cb.serie(t, T6.congestion_v2(n, E, semilla=42), C_NO, 3.5)
        self.play(Transform(sc, scj), run_time=1.6)
        rot.mostrar(dato_pie(f"jitter {fmt(100 * E['gw_jitter'], 0)} % del ciclo"),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)
