class Clip3(Scene):
    """1.2.3 - El LO complejo es un fasor e^{-jwt}; multiplicar por el
    DESLIZA el espectro entero de una captura real (S.desplazar), sin
    copia. El eje es BANDA BASE (offset del propio LO, en kHz): el
    desplazamiento es digital, no una emisora que cambio de frecuencia en
    el aire. El NCO lleva la emisora mas fuerte (la de S.emisoras_captura
    con mayor nivel) a 0 Hz; el corrimiento se mide comparando S.pico
    antes y despues. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El mezclador complejo"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        # --- el fasor del LO complejo ------------------------------------
        centro_fasor = UP * 0.3
        radio = 1.9
        circ = Circle(radius=radio, color=C_LO, stroke_width=1.8,
                      stroke_opacity=0.55)
        circ.move_to(centro_fasor)
        angulo = ValueTracker(0.0)
        vector = always_redraw(lambda: Line(
            centro_fasor, centro_fasor + radio * np.array(
                [np.cos(-angulo.get_value()), np.sin(-angulo.get_value()),
                 0.0]), color=C_LO, stroke_width=3.4))
        punta = always_redraw(lambda: Dot(vector.get_end(), radius=0.08,
                                          color=C_LO))
        nombre = tag_junto(circ, "LO complejo", DOWN, buff=0.3,
                           font_size=22, color=C_LO)
        self.play(Create(circ), FadeIn(vector), FadeIn(punta),
                  FadeIn(nombre), run_time=0.9)
        rot.mostrar(formula_pie(r"e^{-j\omega t}"), zona="abajo",
                    run_time=0.5)
        self.play(angulo.animate.set_value(4 * TAU), run_time=5.4,
                  rate_func=linear)
        self.wait(1.2)

        # --- el espectro de una captura real, en BANDA BASE -----------------
        self.play(FadeOut(circ), FadeOut(vector), FadeOut(punta),
                  FadeOut(nombre), run_time=0.6)
        rot.limpiar(zona="abajo", run_time=0.3)

        x = S.captura_banda(CENTRO)
        f, db = S.espectro_db(x, FS, nfft=2048)
        esp = S.Espectro(f, db, piso=-75.0, techo=2.0, ancho=12.2, alto=3.6,
                         color=C_SENAL)
        esp.move_to(DOWN * 0.15)
        ticks = esp.marcas([-1.2e6, -0.6e6, 0.0, 0.6e6, 1.2e6],
                           ["-1200", "-600", "0", "600", "1200"])
        u = tag_junto(ticks[-1], "kHz", RIGHT, buff=0.2, font_size=20)
        cero = esp.marca_f(0.0, color=C_DATO, ancho=2.2)
        self.play(Create(esp.ejes), FadeIn(ticks), FadeIn(u), run_time=0.7)
        self.play(Create(esp.curva), FadeIn(esp.area), Create(cero),
                  run_time=1.8)
        self.wait(1.8)

        # --- la emisora mas fuerte, medida con S.emisoras_captura -----------
        offs, niveles = S.emisoras_captura(CENTRO)
        i_fuerte = int(np.argmax(niveles))
        off = float(offs[i_fuerte])
        f_antes, _ = S.pico(f, db, f_lo=off - 60e3, f_hi=off + 60e3)
        marca = esp.marca_f(f_antes)
        self.play(Create(marca), run_time=0.6)
        self.wait(1.8)

        y = S.desplazar(x, off, FS)
        f2, db2 = S.espectro_db(y, FS, nfft=2048)
        esp2 = esp.con_db(db2)
        f_despues, _ = S.pico(f2, db2, f_lo=-60e3, f_hi=60e3)
        marca2 = esp.marca_f(f_despues)

        self.play(Transform(esp.curva, esp2.curva),
                  Transform(esp.area, esp2.area),
                  Transform(marca, marca2), run_time=1.8)
        self.wait(1.8)

        desplazamiento_khz = (f_antes - f_despues) / 1e3
        rot.mostrar(cifra_pie(f"{fmt(desplazamiento_khz, 0)} kHz -> 0"),
                    zona="abajo", run_time=0.5)
        self.wait(7.6)
