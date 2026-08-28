class Clip4(Scene):
    """8.2.4 - El CIC no es gratis: su respuesta CAE dentro de la banda
    util, y cuanto cae depende de cuanta banda uses. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 08"))
        rot.mostrar(titulo_curso("Lo que cuesta"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        F_UTIL = {f: f / R_CIC for f in FRACCIONES}
        BORDE = F_UTIL[max(FRACCIONES)]

        # --- la respuesta entera, y donde esta la banda util --------------
        full = respuesta_dibujo(F_CIC, DB_CIC, ancho=9.0, alto=2.6,
                                piso_db=-60.0, techo_db=5.0, color=C_SALIDA)
        full.move_to(UP * 0.35)
        self.play(FadeIn(full.ejes), run_time=0.5)
        self.play(Create(full.curva), run_time=1.5)
        self.wait(0.8)

        banda = full.banda(F_CIC[0], BORDE, color=C_BANDA)
        et_b = tag_hud(f"banda util 1/{R_CIC}", font_size=19, color=C_BANDA)
        et_b.next_to(full, UP, buff=0.20).align_to(full, LEFT)
        self.play(FadeIn(banda), FadeIn(et_b), run_time=0.7)
        rot.mostrar(cifra_pie(f"banda util = 1/{R_CIC}", color=C_BANDA),
                    zona="abajo", run_time=0.5)
        self.wait(2.4)

        # --- de cerca: la caida vive DENTRO de esa banda ------------------
        cerca = F_CIC <= BORDE * 1.06
        zoom = respuesta_dibujo(F_CIC[cerca], DB_CIC[cerca], ancho=9.0,
                                alto=2.7, piso_db=-16.0, techo_db=1.0,
                                color=C_SALIDA)
        zoom.move_to(UP * 0.35)
        et_z = tag_hud("dentro de la banda", font_size=19, color=C_BANDA)
        et_z.next_to(zoom, UP, buff=0.20).align_to(zoom, LEFT)
        self.play(FadeOut(full.curva), FadeOut(full.ejes), FadeOut(banda),
                  FadeOut(et_b), run_time=0.6)
        self.play(FadeIn(zoom.ejes), FadeIn(et_z), run_time=0.5)
        self.play(Create(zoom.curva), run_time=1.4)
        self.wait(1.0)

        # --- las tres condiciones, cada una con su cifra ------------------
        lineas = VGroup(*[tag_hud(f"{fmt(f, 2)} banda: "
                                  f"{fmt(CAIDA[f], 2)} dB", font_size=19,
                                  color=C_CALCULO) for f in FRACCIONES])
        lineas.arrange(DOWN, buff=0.24, aligned_edge=RIGHT)
        lineas.to_corner(UR, buff=0.55).shift(DOWN * 0.15)

        marcas = VGroup()
        puntos = VGroup()
        for i, f in enumerate(FRACCIONES):
            w = F_UTIL[f]
            marca = zoom.marca_w(w, color=C_BANDA)
            punto = zoom.punto(w, color=C_CALCULO, radio=0.065)
            marcas.add(marca)
            puntos.add(punto)
            self.play(Create(marca), FadeIn(punto), run_time=0.5)
            self.play(FadeIn(lineas[i]), run_time=0.35)
            rot.mostrar(cifra_pie(f"{fmt(f, 2)} de banda: "
                                  f"{fmt(CAIDA[f], 2)} dB"), zona="abajo",
                        run_time=0.45)
            self.wait(2.4)

        rot.mostrar(cifra_pie(f"{fmt(FRACCIONES[0], 2)} o "
                              f"{fmt(FRACCIONES[-1], 2)} de banda"),
                    zona="abajo", run_time=0.5)
        self.wait(3.0)

        rot.mostrar(formula_pie(r"H(f) = \left|\frac{\sin(\pi R f)}"
                                r"{R \sin(\pi f)}\right|^{N}"), zona="abajo",
                    run_time=0.5)
        self.wait(3.2)

        cierre_leccion(self, rot, "Lo barato no es gratis.",
                       "El CIC se paga en banda.",
                       zoom.ejes, zoom.curva, et_z, marcas, puntos,
                       lineas)
