class Clip2(Scene):
    """3.2.2 - Los cuatro terminos se suman en cuadratura: 0.0735 deg,
    con 27 % de margen. Y la leccion del metodo: bajar el termino GRANDE
    mueve el total; anular el pequeno casi no. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("Suma en cuadratura"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # Las dos variantes salen de TERMINOS, no de numeros a mano: el
        # grande se baja al nivel del sesgo y el pequeno se anula.
        T_BAJA_GRANDE = {**TERMINOS, "viento": TERMINOS["sesgo"]}
        T_BAJA_CHICO = {**TERMINOS, "ruido": 0.0}

        # La gemela nace centrada en ORIGIN: si se transforma sin
        # recolocarla, el Transform arrastra la pieza ENTERA hacia el
        # centro del cuadro y el rotulo del objetivo cae sobre el eje.
        # Todas las variantes se anclan en POS.
        POS = LEFT * 1.75 + DOWN * 0.30
        pres = presupuesto_barras(TERMINOS, ancho=5.2, alto=2.3)
        pres.move_to(POS)

        # --- primero el listón: el objetivo ya esta dibujado -------------
        self.play(Create(pres.ejes), run_time=0.7)
        self.play(Create(pres.linea_objetivo), run_time=0.8)
        t_obj = tag_hud(f"objetivo {fmt(OBJETIVO_DEG, 1)} deg",
                        font_size=19)
        t_obj.next_to(pres.linea_objetivo, UP, buff=0.12)
        t_obj.align_to(pres.linea_objetivo, LEFT).shift(RIGHT * 0.16)
        self.play(FadeIn(t_obj), run_time=0.5)
        self.wait(1.0)

        # --- las cuatro contribuciones -----------------------------------
        terminos_rot = VGroup(*pres.rotulos[:4])
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN)
                                for b in pres.barras[:4]], lag_ratio=0.28),
                  FadeIn(terminos_rot), run_time=2.0)
        self.wait(1.2)

        rot.mostrar(formula_pie(r"\mathrm{RMS} = \sqrt{\sum_i e_i^2}"),
                    zona="abajo")
        self.wait(2.2)

        # --- y el total en cuadratura ------------------------------------
        self.play(GrowFromEdge(pres.barras[4], DOWN),
                  FadeIn(pres.rotulos[4]), run_time=0.9)
        POS_LECTURA = RIGHT * 4.05 + DOWN * 0.15
        marcador = tag_hud(f"total {fmt(PRES_TOTAL, 4)} deg", font_size=26)
        marcador.move_to(POS_LECTURA)
        self.play(FadeIn(marcador), run_time=0.6)
        self.wait(1.4)

        rot.mostrar(cifra_pie(f"total {fmt(PRES_TOTAL, 4)} deg"),
                    zona="abajo")
        self.wait(2.0)
        rot.mostrar(cifra_pie(f"margen {fmt(100 * PRES_MARGEN, 0)} % "
                              f"de {fmt(OBJETIVO_DEG, 1)}"), zona="abajo")
        self.wait(2.0)

        # El viento no es "el mas alto y ya": aporta el 46 % de la SUMA DE
        # CUADRADOS, que es lo que decide cuanto mueve el total.
        frac_viento = 100 * PRES["fraccion"]["viento"]
        rot.mostrar(cifra_pie(f"viento {fmt(frac_viento, 0)} % del cuadrado"),
                    zona="abajo")
        self.wait(2.0)

        # La pieza entro por sus HIJOS: para transformarla como grupo hay
        # que consolidarla primero, o el Transform mete una copia entera
        # de la pieza por encima de todo lo demas.
        self.remove(*pres.get_family())
        self.add(pres)

        # --- bajar el termino GRANDE mueve el total ----------------------
        # El carril de la cifra se APAGA antes de cada relevo y vuelve
        # DESPUES: mostrandolo antes, el frame muestreado ensena la cifra
        # nueva sobre las barras viejas (y peor, la cifra vieja se quedaba
        # puesta mientras las barras ya habian vuelto a la base).
        rot.limpiar("abajo", run_time=0.25)
        self.play(FadeOut(marcador), run_time=0.25)
        self.play(Transform(pres, pres.gemela(T_BAJA_GRANDE).move_to(POS)),
                  run_time=1.2)
        marcador = tag_hud(f"total {fmt(PRES_BAJA_GRANDE, 4)} deg",
                           font_size=26, color=C_OK)
        marcador.move_to(POS_LECTURA)
        self.play(FadeIn(marcador), run_time=0.4)
        rot.mostrar(cifra_pie(f"viento {fmt(T_BAJA_GRANDE['viento'], 3)} "
                              f"total {fmt(PRES_BAJA_GRANDE, 4)}"),
                    zona="abajo")
        self.wait(1.9)

        rot.limpiar("abajo", run_time=0.25)
        self.play(FadeOut(marcador), run_time=0.25)
        self.play(Transform(pres, pres.gemela(TERMINOS).move_to(POS)),
                  run_time=1.0)
        marcador = tag_hud(f"total {fmt(PRES_TOTAL, 4)} deg", font_size=26)
        marcador.move_to(POS_LECTURA)
        self.play(FadeIn(marcador), run_time=0.4)
        self.wait(0.7)

        # --- anular el pequeno casi no lo mueve --------------------------
        self.play(FadeOut(marcador), run_time=0.25)
        self.play(Transform(pres, pres.gemela(T_BAJA_CHICO).move_to(POS)),
                  run_time=1.2)
        marcador = tag_hud(f"total {fmt(PRES_BAJA_CHICO, 4)} deg",
                           font_size=26, color=C_PELIGRO)
        marcador.move_to(POS_LECTURA)
        self.play(FadeIn(marcador), run_time=0.4)
        rot.mostrar(cifra_pie(f"ruido {fmt(T_BAJA_CHICO['ruido'], 1)} "
                              f"total {fmt(PRES_BAJA_CHICO, 4)}"),
                    zona="abajo")
        self.wait(1.9)

        rot.limpiar("abajo", run_time=0.25)
        self.play(FadeOut(marcador), run_time=0.25)
        self.play(Transform(pres, pres.gemela(TERMINOS).move_to(POS)),
                  run_time=1.0)
        marcador = tag_hud(f"total {fmt(PRES_TOTAL, 4)} deg", font_size=26)
        marcador.move_to(POS_LECTURA)
        self.play(FadeIn(marcador), run_time=0.4)
        self.wait(0.6)

        panel = panel_cifras(f"total    {fmt(PRES_TOTAL, 4)} deg",
                             f"margen   {fmt(100 * PRES_MARGEN, 0)} %",
                             (f"objetivo {fmt(OBJETIVO_DEG, 3)} deg",
                              C_TENUE))
        self.play(FadeIn(panel), run_time=0.7)
        rot.mostrar(cifra_pie(f"total {fmt(PRES_TOTAL, 4)} deg cabe"),
                    zona="abajo")
        self.wait(3.2)
