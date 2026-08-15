class Clip4(Scene):
    """3.3.4 - El array en fase: una rampa de fase inclina el frente y el
    haz gira sin que nada se mueva. Starlink en el tejado. Cierra el
    modulo 3. (~42 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("El array en fase")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: la fila de antenas quietas ---------------------------
        arr = array_fases(fase_deg=0.0)
        arr.shift(DOWN * 1.0)
        self.play(FadeIn(arr.elementos, lag_ratio=0.08), run_time=0.9)
        rot.mostrar(pie_curso("Ocho antenas iguales, en fila, todas "
                              "quietas. Nadie va a moverse."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        # --- momento: en fase, el haz sale recto ---------------------------
        rot.mostrar(pie_curso("Alimentadas en fase, sus ondas suman de "
                              "frente: el haz sale recto."), zona="abajo",
                    run_time=0.5)
        # El +0.0 normaliza el -0.0 que devuelve arcsin(-0) en broadside.
        tag_ap = tag_hud(f"apunta: {arr.apuntado_deg() + 0.0:+.1f} deg",
                         font_size=17)
        tag_ap.to_corner(UR, buff=0.55).shift(DOWN * 0.5)
        self.play(FadeIn(arr.barras), FadeIn(arr.frente),
                  GrowArrow(arr.flecha), FadeIn(tag_ap), run_time=0.9)
        self.wait(4.4)

        # El grupo entra en escena por partes; para transformarlo entero se
        # sustituyen las partes por el grupo (mismo dibujo, un solo mobject).
        self.remove(arr.elementos, arr.barras, arr.frente, arr.flecha)
        self.add(arr)

        # --- momento: la rampa de fase inclina el frente -------------------
        rot.mostrar(pie_curso("Retrasa cada elemento un poco más que el "
                              "anterior: una rampa de fase."),
                    zona="abajo", run_time=0.5)
        arr2 = arr.con_fase(-FASE_ARRAY)
        # con_fase centra por caja; se realinea por la fila de elementos
        # para que las antenas no salten al crecer las barras.
        arr2.shift(arr.elementos.get_center()
                   - arr2.elementos.get_center())
        tag_ap2 = tag_hud(f"apunta: {arr2.apuntado_deg():+.1f} deg",
                          font_size=17)
        tag_ap2.to_corner(UR, buff=0.55).shift(DOWN * 0.5)
        self.play(ReplacementTransform(arr, arr2),
                  ReplacementTransform(tag_ap, tag_ap2), run_time=1.4)
        arr, tag_ap = arr2, tag_ap2
        self.wait(3.6)

        # --- momento: rampa opuesta, haz al otro lado ----------------------
        rot.mostrar(pie_curso("Rampa al revés, haz al otro lado. Sin "
                              "bisagras: pura suma de ondas."),
                    zona="abajo", run_time=0.5)
        arr2 = arr.con_fase(FASE_ARRAY)
        arr2.shift(arr.elementos.get_center()
                   - arr2.elementos.get_center())
        tag_ap2 = tag_hud(f"apunta: {arr2.apuntado_deg():+.1f} deg",
                          font_size=17)
        tag_ap2.to_corner(UR, buff=0.55).shift(DOWN * 0.5)
        self.play(ReplacementTransform(arr, arr2),
                  ReplacementTransform(tag_ap, tag_ap2), run_time=1.4)
        arr, tag_ap = arr2, tag_ap2
        self.wait(3.6)

        rot.mostrar(pie_curso("Starlink en tu tejado es esto: miles de "
                              "antenas siguiendo a un satélite veloz."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        # --- momento: la formula del apuntado ------------------------------
        # El array se retira ANTES: sus barras de fase cuelgan justo en la
        # zona 'abajo', que es donde vive la formula.
        self.play(FadeOut(arr), FadeOut(tag_ap), run_time=0.8)
        rot.mostrar(formula_pie(r"\sin\theta_0 = -\,\frac{\Delta\varphi"
                                r"\,\lambda}{2\pi d}"), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)

        # --- cierre del modulo 3 -------------------------------------------
        rot.limpiar("arriba", run_time=0.4)
        linea1 = Text("Miles de antenas quietas", font_size=40,
                      color=C_TITULO)
        linea2 = Text("apuntando a un satélite que corre.", font_size=40,
                      color=C_CALCULO)
        linea1.move_to(UP * 0.42)
        linea2.move_to(DOWN * 0.42)
        rot.mostrar(pie_curso("La onda ya está en el aire. Falta cruzar "
                              "el cielo: la ionosfera espera."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(linea1, shift=0.2 * UP), run_time=0.7)
        self.play(FadeIn(linea2, shift=0.2 * UP), run_time=0.7)
        self.wait(4.6)
