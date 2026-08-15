class Clip3(Scene):
    """1.3.3 - El criterio de Rayleigh. Dos estrellas cercanas son dos discos
    de Airy que se pisan: se distinguen mientras el maximo de una caiga en el
    primer cero de la otra (1.22 lambda/D). Hubble resuelve 0.28 urad; el ojo,
    224. La regla de luz tiene un tope. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 01")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("El criterio de Rayleigh"), zona="arriba",
                    run_time=0.6)

        # Imagen 2-D arriba y perfil sumado abajo: pieza alta, se escala y se
        # corre a la derecha para dejar la banda izquierda a las cifras.
        rl = dos_fuentes_rayleigh(3.0, d_rel=12.0, ancho=5.0, alto=1.25,
                                  res=180, lado_imagen=2.2)
        rl.scale(0.86).move_to(RIGHT * 1.55 + DOWN * 0.10)
        y_tag = rl.get_top()[1] + 0.30

        def estado(texto, color):
            t = tag_hud(texto, font_size=18, color=color)
            t.move_to(np.array([1.55, y_tag, 0.0]))
            return t

        def acercar(pieza, sep, tag_nuevo=None, tag_viejo=None, run_time=1.4):
            """FadeTransform a la gemela con otra separacion (lleva imagen:
            nunca Transform) y relevo del rotulo de estado."""
            otra = pieza.con_separacion(sep)
            # FadeTransform entre Groups con ImageMobject revienta (become no
            # implementado): imagen por fundido, vectorial por Transform.
            anims = [FadeOut(pieza.imagen), FadeIn(otra.imagen),
                     ReplacementTransform(pieza.marco, otra.marco),
                     ReplacementTransform(pieza.vectorial, otra.vectorial)]
            if tag_viejo is not None:
                anims.append(FadeOut(tag_viejo))
            self.play(*anims, run_time=run_time)
            self.remove(pieza, otra.imagen, otra.marco, otra.vectorial)
            self.add(otra)
            if tag_nuevo is not None:
                self.play(FadeIn(tag_nuevo), run_time=0.4)
            return otra

        # --- momento: dos discos que se pisan ----------------------------------
        rot.mostrar(pie_curso("Dos estrellas cercanas: dos discos que se "
                              "pisan."), zona="abajo", run_time=0.5)
        self.play(FadeIn(rl.imagen), FadeIn(rl.marco), run_time=0.9)
        self.play(FadeIn(rl.vectorial), run_time=0.8)
        # Las partes entraron sueltas; los FadeTransform sustituyen al GRUPO,
        # asi que la escena tiene que tener el grupo, no las partes.
        self.remove(rl.imagen, rl.marco, rl.vectorial)
        self.add(rl)
        t_estado = estado("separadas", C_OBJETO)
        self.play(FadeIn(t_estado), run_time=0.4)
        self.wait(2.6)
        rl = acercar(rl, 1.6, tag_viejo=t_estado, run_time=1.5)
        t_estado = None
        self.wait(1.4)

        # --- momento: el criterio -----------------------------------------------
        rot.mostrar(pie_curso("Rayleigh: se distinguen si el máximo de una "
                              "cae en el primer cero de la otra."),
                    zona="abajo", run_time=0.5)
        t_estado = estado("justo resueltas", C_MEDIDA)
        rl = acercar(rl, 1.22, tag_nuevo=t_estado, run_time=1.3)
        t_criterio = tag_hud("es un criterio, no una ley", font_size=13,
                             color=C_TENUE)
        t_criterio.move_to(np.array([-4.55, -0.35, 0.0]))
        self.play(FadeIn(t_criterio), run_time=0.4)
        self.wait(2.8)
        t_confusas = estado("confundidas", C_HAZ)
        rl = acercar(rl, 0.8, tag_nuevo=t_confusas, tag_viejo=t_estado,
                     run_time=1.3)
        self.wait(2.4)

        # --- momento: las cifras -------------------------------------------------
        rot.mostrar(pie_curso("Hubble, 2.4 metros: 0.28 microrradianes. Tu "
                              "ojo, 3 milímetros: 224."), zona="abajo",
                    run_time=0.5)
        t_estado = estado("justo resueltas", C_MEDIDA)
        rl = acercar(rl, 1.22, tag_nuevo=t_estado, tag_viejo=t_confusas,
                     run_time=1.3)
        cifras = VGroup(
            tag_hud(f"Hubble  D = 2.4 m  ->  "
                    f"{RAYLEIGH_HUBBLE_URAD:.2f} urad", font_size=15),
            tag_hud(f"ojo     D = 3 mm   ->  "
                    f"{RAYLEIGH_OJO_URAD:.0f} urad", font_size=15),
        ).arrange(DOWN, buff=0.24, aligned_edge=LEFT)
        cifras.move_to(np.array([-4.55, 1.10, 0.0]))
        self.play(FadeIn(cifras[0], shift=0.10 * UP), run_time=0.5)
        self.play(FadeIn(cifras[1], shift=0.10 * UP), run_time=0.5)
        self.wait(3.2)

        # --- cierre ---------------------------------------------------------------
        rot.mostrar(pie_curso("La regla de luz tiene un tope: la difracción "
                              "de quien la usa."), zona="abajo", run_time=0.5)
        self.wait(5.0)
