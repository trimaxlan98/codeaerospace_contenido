class Clip2(Scene):
    """1.3.2 - El disco de Airy. Una abertura circular no enfoca un punto en
    un punto: lo enfoca en un disco rodeado de anillos, con el primer cero en
    1.22 lambda/D. Al doblar el diametro el disco se encoge a la mitad: por
    eso los telescopios son grandes. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 01")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("El disco de Airy"), zona="arriba",
                    run_time=0.6)

        # La pieza es alta (imagen 2-D arriba + perfil abajo): se escala para
        # dejar sitio al titulo y al pie, y se corre a la derecha para que la
        # formula viva a su izquierda sin encimarse.
        D_REL = 12.0
        airy = disco_airy(D_REL, lam=LAMBDA_HENE, ancho=5.0, alto_perfil=1.20,
                          res=200, lado_imagen=2.2)
        airy.scale(0.86).move_to(RIGHT * 1.55 + DOWN * 0.05)
        # El rotulo ASCII "primer cero: 1.22 lambda / D" lo dice el MathTex.
        airy.vectorial.remove(airy.vectorial[3])

        # --- momento: el disco con sus anillos --------------------------------
        rot.mostrar(pie_curso("Con una abertura circular, la luz forma un "
                              "disco con anillos: el disco de Airy."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(airy.imagen), FadeIn(airy.marco), run_time=1.0)
        self.play(FadeIn(airy.vectorial), run_time=0.9)
        # Las partes entraron sueltas; el FadeTransform de mas abajo sustituye
        # al GRUPO, asi que la escena tiene que tener el grupo, no las partes.
        self.remove(airy.imagen, airy.marco, airy.vectorial)
        self.add(airy)
        self.wait(4.6)

        # --- momento: donde cae el primer cero --------------------------------
        rot.mostrar(pie_curso("El radio del disco es 1.22 lambda sobre el "
                              "diámetro."), zona="abajo", run_time=0.5)
        ley = MathTex(r"\theta = 1.22\,\lambda / D", font_size=42,
                      color=C_ACENTO)
        ley.move_to(np.array([-4.05, 1.15, 0.0]))
        self.play(Write(ley), run_time=1.2)
        cero = Dot(airy.primer_cero, radius=0.075, color=C_MEDIDA)
        t_cero = tag_hud("primer cero", font_size=14, color=C_MEDIDA)
        t_cero.next_to(cero, DOWN, buff=0.14)
        self.play(FadeIn(cero, scale=1.6), FadeIn(t_cero), run_time=0.6)
        self.wait(4.4)

        # --- momento: el doble de apertura, la mitad de disco -----------------
        rot.mostrar(pie_curso("Abertura mayor, disco menor: por eso los "
                              "telescopios son grandes."), zona="abajo",
                    run_time=0.5)
        self.play(FadeOut(cero), FadeOut(t_cero), run_time=0.35)
        grande = airy.con_diametro(2.0 * D_REL)
        grande.vectorial.remove(grande.vectorial[3])
        # FadeTransform entre Groups con ImageMobject revienta (become no
        # implementado): la imagen se releva por fundido y lo vectorial por
        # Transform; luego la escena se queda con el grupo nuevo entero.
        self.play(FadeOut(airy.imagen), FadeIn(grande.imagen),
                  ReplacementTransform(airy.marco, grande.marco),
                  ReplacementTransform(airy.vectorial, grande.vectorial),
                  run_time=1.6)
        self.remove(airy, grande.imagen, grande.marco, grande.vectorial)
        self.add(grande)
        airy = grande
        cero2 = Dot(airy.primer_cero, radius=0.075, color=C_MEDIDA)
        t_cero2 = tag_hud("el doble de D: la mitad de disco", font_size=14,
                          color=C_MEDIDA)
        t_cero2.next_to(cero2, DOWN, buff=0.14).shift(RIGHT * 0.55)
        self.play(FadeIn(cero2, scale=1.6), FadeIn(t_cero2), run_time=0.6)
        self.wait(4.0)

        # --- cierre -----------------------------------------------------------
        rot.mostrar(pie_curso("Ningún punto se enfoca en un punto. Se enfoca "
                              "en un disco."), zona="abajo", run_time=0.5)
        self.wait(5.0)
