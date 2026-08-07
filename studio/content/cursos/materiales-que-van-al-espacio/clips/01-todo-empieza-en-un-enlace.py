class Clip1(Scene):
    """1 - Todo empieza en un enlace. Portada del curso Materiales: un par
    de atomos unidos por un resorte arriba y el pozo de Lennard-Jones
    abajo, con un punto brillante marcando el fondo -el equilibrio-. Los
    atomos se separan y regresan dos veces, sincronizados con el punto
    trepando y bajando la pared derecha del pozo. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)

        # --- momento: portada del curso -----------------------------------
        portada = VGroup(
            titulo_marca("Materiales", font_size=46),
            Text("que van al espacio", font_size=25, color=C_ACENTO),
        ).arrange(DOWN, buff=0.26)
        portada.move_to(ORIGIN)

        self.play(Write(portada[0]), run_time=1.3)
        self.play(FadeIn(portada[1], shift=0.18 * UP), run_time=0.7)
        self.wait(1.5)

        modulo = hud_modulo("Modulo 01")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        self.play(FadeOut(portada, shift=0.5 * UP), run_time=0.7)

        titulo = titulo_curso("Todo empieza en un enlace")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: el enlace arriba, el pozo abajo -----------------------
        par = par_atomos(separacion=1.5, radio=0.26).move_to(UP * 0.9)
        pozo = pozo_lennard_jones(ancho=4.4, alto=2.0).move_to(DOWN * 1.0)

        self.play(FadeIn(par), Create(pozo.ejes), FadeIn(pozo.etiquetas),
                  run_time=0.8)
        self.play(Create(pozo.curva), Create(pozo.r0_linea), run_time=0.9)

        pie1 = pie_curso("Un cohete, un ala, un tornillo: en el fondo, "
                         "átomos tomados de la mano.")
        rot.mostrar(pie1, zona="abajo", run_time=0.45)
        self.wait(5.0)

        # --- momento: el punto brillante en el fondo ------------------------
        punto = punto_brillante(pozo.fondo(), color=C_MAT, radio=0.075)
        punto.set_z_index(6)
        self.play(FadeIn(punto), run_time=0.5)

        pie2 = pie_curso("Dos fuerzas en guerra —atracción lejos, "
                         "repulsión cerca— cavan un pozo.")
        rot.mostrar(pie2, zona="abajo", run_time=0.45)
        self.wait(5.0)

        # --- momento: la formula del potencial LJ ----------------------------
        formula = formula_pie(
            r"U(r) = 4\varepsilon[(\sigma/r)^{12} - (\sigma/r)^6]")
        rot.mostrar(formula, zona="abajo", run_time=0.45)
        self.wait(5.0)

        # --- momento: el fondo es el equilibrio -------------------------------
        # El pie cambia ANTES de la animacion que ilustra.
        pie3 = pie_curso("El fondo del pozo es la distancia de equilibrio: "
                         "ahí viven.")
        rot.mostrar(pie3, zona="abajo", run_time=0.45)
        self.wait(2.0)

        for _ in range(2):
            self.play(par.animate.separar(2.3),
                      punto.animate.move_to(pozo.punto_de(1.35)),
                      run_time=0.9, rate_func=rate_functions.ease_in_out_sine)
            self.play(par.animate.separar(1.5),
                      punto.animate.move_to(pozo.fondo()),
                      run_time=0.9, rate_func=rate_functions.ease_in_out_sine)

        # --- momento: el gancho -------------------------------------------------
        pie4 = pie_curso("De la forma de ese pozo sale TODO lo demás.")
        rot.mostrar(pie4, zona="abajo", run_time=0.45)
        self.wait(5.0)
