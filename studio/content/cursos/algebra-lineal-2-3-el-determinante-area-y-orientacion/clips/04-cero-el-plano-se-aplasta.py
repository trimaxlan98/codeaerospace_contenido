class Clip4(Scene):
    """2.3.4 - Determinante cero: las dos columnas apuntan a lo mismo y el
    plano entero cae en una recta. En 3D, el cubo unidad se aplasta contra el
    suelo y su volumen es cero. Cierra la leccion. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Cero: el plano se aplasta")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: dos columnas que apuntan a lo mismo -------------------
        pl = plano_leccion(unidad=UNIDAD_4)
        i_hat = vector(pl, (1, 0), color=C_I, nombre=r"\hat{\imath}",
                       etiqueta_dir=DOWN)
        j_hat = vector(pl, (0, 1), color=C_J, nombre=r"\hat{\jmath}",
                       etiqueta_dir=LEFT)
        cuadrado = paralelogramo(pl, np.eye(2))
        col_i, col_j = M_SINGULAR[:, 0], M_SINGULAR[:, 1]
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Sus columnas apuntan a lo mismo: ("
                              + fmt(col_j[0], 0) + ", " + fmt(col_j[1], 0)
                              + ") es el doble de (" + fmt(col_i[0], 0) + ", "
                              + fmt(col_i[1], 0) + ")."),
                    zona="abajo", run_time=0.5)
        panel = panel_derecha(matriz_columnas(M_SINGULAR, font_size=40))
        self.play(GrowArrow(i_hat.flecha), GrowArrow(j_hat.flecha),
                  run_time=0.7)
        self.play(FadeIn(i_hat.etiqueta), FadeIn(j_hat.etiqueta),
                  FadeIn(cuadrado), FadeIn(panel, shift=0.15 * LEFT),
                  run_time=0.7)
        cifra = self._cifra("area = " + fmt(cuadrado.area), 0)
        self.play(FadeIn(cifra), run_time=0.4)
        self.wait(3.6)

        # --- momento: el plano cae en una recta -----------------------------
        rot.mostrar(pie_curso("Mira lo que le pasa al plano entero."),
                    zona="abajo", run_time=0.5)
        # Las etiquetas cambian de lado: las dos flechas acaban sobre la
        # misma recta y con etiqueta_dir heredada se pisarian.
        i_fin = vector(pl, M_SINGULAR @ i_hat.coords, color=C_I,
                       nombre=r"\hat{\imath}", etiqueta_dir=RIGHT)
        j_fin = vector(pl, M_SINGULAR @ j_hat.coords, color=C_J,
                       nombre=r"\hat{\jmath}", etiqueta_dir=LEFT)
        aplastado = paralelogramo(pl, M_SINGULAR)
        # La cifra se apaga mientras dura el aplaste: a medio camino el area
        # no es ni uno ni cero (en pantalla no se miente).
        self.play(*pl.anim_matriz(M_SINGULAR, run_time=2.2),
                  Transform(i_hat, i_fin, run_time=2.2),
                  Transform(j_hat, j_fin, run_time=2.2),
                  Transform(cuadrado, aplastado, run_time=2.2),
                  FadeOut(cifra, run_time=0.6))
        # Las dos columnas acaban sobre el MISMO rayo: la mas larga (ĵ) tapa
        # a la corta (î). La corta manda al frente para que se vea su ambar.
        self.bring_to_front(j_hat, i_hat)
        cifra = self._cifra("area = " + fmt(aplastado.area), 0)
        cifra_det = self._cifra("det = " + fmt(DET_SINGULAR), 1)
        self.play(FadeIn(cifra), FadeIn(cifra_det), run_time=0.6)
        self.wait(3.6)

        # --- momento: todo el plano vive en esa recta -----------------------
        rot.mostrar(pie_curso("Todo cayó en una recta: el área es cero y el "
                              "determinante también."), zona="abajo",
                    run_time=0.5)
        linea = span_recta(pl, DIR_APLASTE, color=C_IMG, grosor=5.0,
                           opacidad=0.9)
        self.play(Create(linea), run_time=0.8)
        # La recta verde se dibuja ENCIMA de las dos flechas y les roba el
        # color: las columnas vuelven al frente.
        self.bring_to_front(j_hat, i_hat)
        self.wait(4.0)

        # --- momento: en tres dimensiones es un volumen ---------------------
        self.play(FadeOut(pl), FadeOut(i_hat), FadeOut(j_hat),
                  FadeOut(cuadrado), FadeOut(linea), FadeOut(panel),
                  FadeOut(cifra), FadeOut(cifra_det), run_time=0.8)
        rot.mostrar(pie_curso("En tres dimensiones el determinante es un "
                              "volumen: el del cubo."), zona="abajo",
                    run_time=0.5)
        esp = espacio3(unidad=0.96, alcance=3)
        esp.move_to(DOWN * 0.3)
        cubo = caja3(esp, np.eye(3))
        k_hat = vector3(esp, (0, 0, 1), color=C_K, nombre=r"\hat k")
        # La etiqueta por defecto cae SOBRE el eje z (violeta sobre violeta):
        # se aparta a la izquierda. El gemelo del aplaste se construye solo,
        # con la colocacion por defecto (alli el eje ya no estorba).
        k_hat.etiqueta.shift(0.34 * LEFT)
        panel3 = panel_derecha(matriz_columnas(M3_APLASTA, font_size=32))
        self.play(FadeIn(esp), FadeIn(cubo), FadeIn(k_hat),
                  FadeIn(panel3, shift=0.15 * LEFT), run_time=1.1)
        cifra_vol = self._cifra("volumen = " + fmt(cubo.volumen), 0)
        self.play(FadeIn(cifra_vol), run_time=0.4)
        self.wait(3.4)

        # --- momento: el cubo se aplasta contra el suelo --------------------
        rot.mostrar(pie_curso("Si el tercer eje cae en el suelo, el cubo se "
                              "aplasta: volumen cero."), zona="abajo",
                    run_time=0.5)
        cubo_plano = caja3(esp, M3_APLASTA)
        self.play(Transform(cubo, cubo_plano, run_time=2.0),
                  Transform(k_hat, k_hat.con_matriz(M3_APLASTA),
                            run_time=2.0),
                  FadeOut(cifra_vol, run_time=0.6))
        cifra_vol = self._cifra("volumen = " + fmt(cubo_plano.volumen), 0)
        self.play(FadeIn(cifra_vol), run_time=0.5)
        self.wait(3.4)

        # --- cierre de la leccion -------------------------------------------
        cierre_leccion(self, rot, "El determinante es cuánto crece el área.",
                       "Cero: algo se perdió.",
                       "Si el área sobrevive, hay vuelta atrás. Empieza el "
                       "módulo siguiente.",
                       esp, cubo, k_hat, panel3, cifra_vol)

    # -- cifras bajo el HUD, con fondo (la rejilla pasa por debajo) ---------
    def _cifra(self, texto, fila=0):
        g = _con_fondo(tag_hud(texto, font_size=20), buff=0.13, opacidad=0.82)
        g.to_corner(UL, buff=0.5).shift(DOWN * (0.66 + 0.46 * fila))
        return g
