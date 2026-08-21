class Clip3(Scene):
    """4.1.3 - Los 4 estados (00,01,10,11) y sus 8 flechas de RAMAS_CONV;
    una ristra real recorre los estados (trellis.camino) y la salida
    verde se acumula. La misma entrada da salida distinta segun el
    estado. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("La maquina de estados")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: los 4 estados y sus 8 flechas --------------------------
        rot.mostrar(pie_curso("Cuatro estados, ocho flechas: la misma "
                              "maquina se repite en cada paso."),
                    zona="abajo", run_time=0.5)
        tr = trellis(pasos=len(BITS_MENSAJE), ancho=7.4, alto=2.8)
        tr.move_to(DOWN * 0.3)
        self.play(FadeIn(tr), run_time=0.9)
        ramas = tr.todas_ramas()
        self.play(Create(ramas), run_time=1.8)
        ramas_desde_00 = [(b, s2, sal) for (s, b, s2, sal) in RAMAS_CONV
                          if s == 0]
        etiquetas_rama = VGroup()
        for b, s2, (o1, o2) in ramas_desde_00:
            medio = (tr.nodo(0, 0) + tr.nodo(1, s2)) / 2.0
            et = tag_hud(f"{fmt(b, 0)}/{fmt(o1, 0)}{fmt(o2, 0)}",
                        font_size=14, color=C_CIFRA)
            et.move_to(medio + UP * 0.16)
            etiquetas_rama.add(et)
        self.play(FadeIn(etiquetas_rama), run_time=0.7)
        self.wait(4.0)

        # --- momento: una ristra real recorre los estados ----------------------
        rot.mostrar(pie_curso("Una ristra real recorre los estados, "
                              "paso a paso."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(etiquetas_rama), run_time=0.4)
        entrada = tren_bits(BITS_MENSAJE, lado=0.42)
        entrada.to_edge(UP, buff=1.35)
        et_entrada = tag_junto(entrada, "la entrada", direccion=UP,
                               buff=0.14)
        self.play(FadeIn(entrada), FadeIn(et_entrada), run_time=0.7)
        camino = tr.camino(ESTADOS_CONV)
        self.play(Create(camino), run_time=2.4)
        self.wait(4.0)

        # --- momento: la salida verde se acumula --------------------------------
        rot.mostrar(pie_curso("La salida se acumula en verde: dos bits "
                              "por cada uno que entra."),
                    zona="abajo", run_time=0.5)
        salida = tren_bits(SALIDA_CONV, lado=0.35, color=C_COD)
        salida.to_edge(DOWN, buff=1.55)
        et_salida = tag_junto(salida, "la salida", direccion=DOWN,
                              buff=0.14)
        self.play(FadeIn(salida), FadeIn(et_salida), run_time=1.0)
        self.wait(5.0)

        # --- momento: la salida depende del camino ------------------------------
        rot.mostrar(pie_curso("La salida depende del camino, no solo "
                              "del bit."),
                    zona="abajo", run_time=0.5)
        est_a = format(ESTADOS_CONV[0], "02b")
        est_b = format(ESTADOS_CONV[2], "02b")
        linea_a = tag_hud(f"bit=1 en {est_a} -> "
                          f"{fmt(SALIDA_CONV[0], 0)}{fmt(SALIDA_CONV[1], 0)}",
                          font_size=18, color=C_CIFRA)
        linea_b = tag_hud(f"bit=1 en {est_b} -> "
                          f"{fmt(SALIDA_CONV[4], 0)}{fmt(SALIDA_CONV[5], 0)}",
                          font_size=18, color=C_CIFRA)
        panel = panel_derecha(linea_a, linea_b)
        self.play(FadeIn(panel), run_time=0.6)
        self.wait(6.5)
