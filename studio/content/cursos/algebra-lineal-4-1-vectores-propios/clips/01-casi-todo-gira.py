class Clip1(Scene):
    """4.1.1 - Una transformacion saca de su recta a casi todas las
    direcciones; dos se quedan exactamente donde estaban. Se aplica DOS
    veces: la segunda con las rectas propias ya dibujadas, para VER que las
    fucsia no abandonan su carril mientras el resto gira. (~39 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Casi todo gira")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: un abanico de direcciones -----------------------------
        pl = plano_leccion()
        abanico = self._abanico(pl, np.eye(2), propios=False)
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Un abanico de direcciones sobre la rejilla. "
                              "Ocho flechas, ocho rumbos."),
                    zona="abajo", run_time=0.5)
        self.play(*[GrowArrow(v.flecha) for v in abanico], run_time=1.0)
        self.wait(3.5)

        # --- momento: la matriz que las va a mover --------------------------
        rot.mostrar(pie_curso(
            "Esta matriz manda î a (" + fmt(A_PROPIA[0, 0], 0) + ", "
            + fmt(A_PROPIA[1, 0], 0) + ") y ĵ a (" + fmt(A_PROPIA[0, 1], 0)
            + ", " + fmt(A_PROPIA[1, 1], 0) + ")."),
            zona="abajo", run_time=0.5)
        mat = matriz_columnas(A_PROPIA, font_size=40)
        panel = panel_derecha(mat)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.7)
        self.wait(3.6)

        # --- momento: la rejilla se deforma y arrastra a las flechas --------
        rot.mostrar(pie_curso("Aplicada al plano entero: mira cómo se "
                              "deforma la rejilla."),
                    zona="abajo", run_time=0.5)
        self.play(*self._paso(pl, abanico, A_PROPIA, propios=False),
                  run_time=2.0)
        self.wait(2.4)

        # --- momento: casi todas salieron de su carril ----------------------
        rot.mostrar(pie_curso("Casi todas cambiaron de rumbo: esta se salió "
                              "de su recta."), zona="abajo", run_time=0.5)
        # (el abanico[5] va a 110 grados: su recta de partida es oblicua y
        # no se confunde con los ejes del plano, como pasaria con 0 o 90)
        #
        # El carril va en ROJO y a trazos: C_TENUE es el MISMO color que los
        # ejes del plano (#94a0b0), asi que una recta gris ahi se lee como un
        # eje mas. A trazos y en el color del vector se lee como "la recta de
        # esta flecha". El fantasma marca donde estaba antes de moverse.
        carril = DashedVMobject(
            span_recta(pl, ABANICO[5], color=C_VEC, opacidad=0.7, grosor=3.0),
            num_dashes=46)
        fantasma = self._flecha(pl, ABANICO[5], propio=False)
        fantasma.flecha.set_stroke(opacity=0.55)
        fantasma.flecha.set_fill(opacity=0.55)
        self.play(Create(carril), FadeIn(fantasma), run_time=0.8)
        self.play(Indicate(abanico[5], color=C_VEC, scale_factor=1.06),
                  run_time=0.9)
        self.wait(2.6)

        # --- momento: las dos que no giraron --------------------------------
        rot.mostrar(pie_curso("Menos dos. Estas siguen en su recta: solo "
                              "cambió su largo."), zona="abajo", run_time=0.5)
        self.play(FadeOut(carril), FadeOut(fantasma), run_time=0.3)
        rectas = VGroup(span_recta(pl, DIR_ESTIRA, color=C_PROPIO,
                                   opacidad=0.6),
                        span_recta(pl, DIR_QUIETA, color=C_PROPIO,
                                   opacidad=0.6))
        self.play(Create(rectas), run_time=1.2)
        # Solo cambia el color de las dos propias: se quedan donde estan.
        destino = self._abanico(pl, A_PROPIA, propios=True)
        self.play(*[Transform(abanico[k], destino[k])
                    for k in INDICES_PROPIOS], run_time=0.9)
        self.wait(2.2)

        # --- momento: otra vez, mirando solo a las fucsia -------------------
        # Rebobinar a la identidad y volver a aplicar A con las rectas ya
        # dibujadas: ahora se VE que las fucsia resbalan por su propia recta
        # mientras las rojas se salen de la suya.
        rot.mostrar(pie_curso("Rebobina y mira otra vez: las fucsia resbalan "
                              "por su recta, sin salirse."),
                    zona="abajo", run_time=0.5)
        self.play(*self._paso(pl, abanico, np.eye(2), propios=True),
                  run_time=1.3)
        self.play(*self._paso(pl, abanico, A_PROPIA, propios=True),
                  run_time=2.2)
        self.wait(1.2)

        rot.mostrar(pie_curso("Se llaman direcciones propias. Son el "
                              "esqueleto de la transformación."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

    # -- una flecha del abanico, con el papel que le toca -------------------
    def _flecha(self, pl, coords, propio):
        return vector(pl, coords,
                      color=C_PROPIO if propio else C_VEC,
                      grosor=6.5 if propio else 4.0,
                      punta_len=0.24 if propio else 0.18)

    # -- el abanico entero llevado por M ------------------------------------
    def _abanico(self, pl, m, propios):
        return [self._flecha(pl, np.asarray(m) @ np.asarray(c),
                             propio=propios and k in INDICES_PROPIOS)
                for k, c in enumerate(ABANICO)]

    # -- animaciones que llevan rejilla viva y abanico al estado M ----------
    # (M es la transformacion TOTAL desde la identidad, como en anim_matriz;
    # aqui se hace a mano porque el color de las flechas cambia a mitad del
    # clip y `con_matriz` heredaria el rojo de partida.)
    def _paso(self, pl, abanico, m, propios):
        destino = self._abanico(pl, m, propios)
        return ([Transform(pl.vivo, pl.rejilla_con(m))]
                + [Transform(a, b) for a, b in zip(abanico, destino)])
