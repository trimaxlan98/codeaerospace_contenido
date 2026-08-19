class Clip4(Scene):
    """2.1.4 - El catalogo: rotacion, cizalla, escala y reflexion. La misma
    rejilla ejecuta los cuatro, uno tras otro, y en cada uno la matriz del
    panel dice a donde van i-sombrero y j-sombrero. Cierra la leccion.
    (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Un catálogo de movimientos")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # Unidad mayor que la de la familia: aqui el protagonista es la
        # rejilla y conviene que sus celdas se lean grandes al deformarse.
        pl = plano_leccion(unidad=1.15)
        i_hat = vector(pl, (1, 0), color=C_I, nombre=r"\hat{\imath}",
                       etiqueta_dir=DOWN)
        j_hat = vector(pl, (0, 1), color=C_J, nombre=r"\hat{\jmath}",
                       etiqueta_dir=LEFT)
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Cuatro números, cuatro movimientos. Mira las "
                              "columnas."), zona="abajo", run_time=0.5)
        self.play(GrowArrow(i_hat.flecha), FadeIn(i_hat.etiqueta),
                  GrowArrow(j_hat.flecha), FadeIn(j_hat.etiqueta),
                  run_time=0.7)
        self.wait(3.0)

        panel = None

        def movimiento(M, nombre, pie, volver=True):
            """Un movimiento del catalogo: primero el pie y la matriz, y
            despues la rejilla ejecutandolo desde la identidad."""
            nonlocal panel
            rot.mostrar(pie_curso(pie), zona="abajo", run_time=0.5)
            nuevo = panel_derecha(tag_hud(nombre, font_size=17),
                                  matriz_columnas(M, font_size=30,
                                                  h_buff=1.0),
                                  buff=0.22)
            if panel is None:
                self.play(FadeIn(nuevo, shift=0.15 * LEFT), run_time=0.45)
            else:
                self.play(FadeOut(panel), FadeIn(nuevo), run_time=0.45)
            panel = nuevo
            # M es SIEMPRE la transformacion total desde la identidad: entre
            # movimiento y movimiento la rejilla vuelve a su sitio, asi que
            # i_hat y j_hat conservan sus coords (1,0) y (0,1) y no hay que
            # recrearlos.
            self.play(*pl.anim_matriz(M, i_hat, j_hat), run_time=1.4)
            self.wait(2.2)
            if volver:
                self.play(*pl.anim_matriz(IDENTIDAD, i_hat, j_hat),
                          run_time=0.8)

        movimiento(M_ROT, "ROTACION " + fmt(ANG_ROT, 0) + " deg",
                   "Girar: los dos destinos rotan y la rejilla gira entera.")
        movimiento(M_CIZ, "CIZALLA k = " + fmt(K_CIZALLA),
                   "Cizallar: î se queda y ĵ se desliza. Los cuadrados se "
                   "inclinan.")
        movimiento(M_ESC, "ESCALA " + fmt(ESC_XY[0]) + " x " + fmt(ESC_XY[1]),
                   "Escalar: estira en x, encoge en y. Nada gira.")
        movimiento(M_REF, "REFLEXION EN EL EJE Y",
                   "Reflejar: î cruza al otro lado y el plano queda del "
                   "revés.", volver=False)

        # --- cierre de la leccion -------------------------------------------
        cierre_leccion(self, rot, "La matriz no es una tabla.",
                       "Es a dónde van î y ĵ.",
                       "¿Y si encadenamos dos movimientos? Siguiente "
                       "lección.",
                       pl, i_hat, j_hat, panel)
