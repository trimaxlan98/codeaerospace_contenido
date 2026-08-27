class Clip3(Scene):
    """5.1.3 - Multiplicar el recorte por una ventana suave mata la oreja
    -- pero ensancha la transicion, y eso tiene precio. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 05"))
        rot.mostrar(titulo_curso("La ventana que ablanda"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        colores = {"rect": C_RUIDO, "hann": C_CALCULO,
                   "hamming": C_MUESTRA, "blackman": C_IDEAL}
        w0, m0, _ = RESP_VENT["rect"]
        rf = respuesta_dibujo(w0, m0, ancho=9.4, alto=3.2, piso_db=-60.0,
                              techo_db=8.0, color=colores["rect"])
        rf.move_to(DOWN * 0.45)
        linea_0 = DashedLine(rf.en(0.0, 0.0), rf.en(np.pi, 0.0),
                             color=C_TENUE, stroke_width=1.2,
                             dash_length=0.06)
        banda = rf.banda(F_RECHAZO * np.pi, np.pi, color=C_TENUE,
                         opacidad=0.10)
        self.play(FadeIn(rf), FadeIn(linea_0), FadeIn(banda), run_time=0.9)
        rot.mostrar(cifra_pie(f"rect {SOBREPICO_V['rect']:+.3f} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(2.2)

        # --- las tres ventanas suaves, una a una --------------------------
        curvas = {"rect": rf.curva}
        for v in ("hann", "hamming", "blackman"):
            w, m, _ = RESP_VENT[v]
            gem = rf.con_mag(m, color=colores[v])
            rot.mostrar(cifra_pie(f"{v} {SOBREPICO_V[v]:+.3f} dB"),
                        zona="abajo", run_time=0.45)
            self.play(Create(gem.curva), run_time=1.5)
            curvas[v] = gem.curva
            self.add(gem.curva)
            self.wait(1.9)

        self.play(*[c.animate.set_stroke(opacity=0.45)
                    for k, c in curvas.items() if k != "hamming"],
                  run_time=0.7)
        self.wait(1.4)

        # --- lo que de verdad importa: la atenuacion ----------------------
        panel = panel_cifras(*[(f"{v}: {fmt(ATEN_V[v], 1)} dB", colores[v])
                               for v in VENTANAS_FIR], buff=0.20)
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.6)

        # --- el matiz honesto: blackman SUSPENDE --------------------------
        self.play(curvas["blackman"].animate.set_stroke(opacity=1.0,
                                                        width=3.4),
                  curvas["hamming"].animate.set_stroke(opacity=0.45),
                  run_time=0.7)
        rot.mostrar(cifra_pie(f"blackman {fmt(ATEN_V['blackman'], 1)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(3.0)
        rot.mostrar(cifra_pie(f"pide {fmt(-ATEN_PEDIDA, 0)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(3.8)
