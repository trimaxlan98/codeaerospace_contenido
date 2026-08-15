class Clip2(Scene):
    """2 - Cada franja vale media longitud de onda. El espejo movil se
    desplaza y el camino de ida y vuelta cambia el doble: la curva I(d) del
    contador sube y baja, y cada vuelta completa del brillo es UNA franja de
    316.4 nm (lambda/2 del HeNe). Tres franjas son 949.2 nm. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 01")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        # Titulo largo: a 34 pt rozaria la etiqueta "MODULO 01" de la esquina
        # (llega a x = -3.9 y la etiqueta acaba en -4.1), asi que baja a 30.
        rot.mostrar(titulo_curso("Cada franja vale media longitud de onda",
                                 font_size=30), zona="arriba", run_time=0.6)

        # Michelson chico arriba-izquierda (3.3 x 3.0, de y = -1.2 a +1.8) y
        # el contador al 80 % a la derecha: la esquina inferior izquierda
        # queda libre para la formula y la cifra. El `move_to` cuenta las
        # anclas (+-3.3), de ahi el centro corrido.
        m = michelson()
        m.scale(0.60).move_to(np.array([-4.54, 0.28, 0.0]))
        cont = contador_franjas()
        cont.scale(0.80).move_to(np.array([2.50, -0.10, 0.0]))

        # --- momento: movemos el espejo ------------------------------------
        rot.mostrar(pie_curso("Movemos el espejo: el camino de ida y vuelta "
                              "cambia el doble."), zona="abajo")
        self.play(FadeIn(m), run_time=1.0)
        self.wait(0.6)
        d = ValueTracker(0.0)
        # `a_desplazamiento` SUSTITUYE el mobject de la lectura (no reescribe
        # el mismo): el renderer Cairo congela la lista de mobiles al empezar
        # el play, asi que la lectura que habia AL ARRANCAR se sigue pintando
        # encima de las nuevas hasta que acaba la animacion. Se apaga antes
        # de arrancar; la primera pasada del updater ya pone la suya.
        m.lectura.set_opacity(0.0)
        m.add_updater(lambda mob: mob.a_desplazamiento(d.get_value()))
        self.play(d.animate.set_value(PASO_FRANJA_NM), run_time=3.0,
                  rate_func=linear)
        m.clear_updaters()
        self.wait(1.4)

        # --- momento: cada vuelta del brillo es una franja -----------------
        rot.mostrar(pie_curso("Cada vez que el brillo da una vuelta completa, "
                              "pasó una franja."), zona="abajo")
        # El contador arranca donde quedo el espejo (una franja), para que
        # el punto y el esquema cuenten lo mismo.
        cont.a_desplazamiento(PASO_FRANJA_NM)
        self.play(Create(cont.ejes), FadeIn(cont.ticks),
                  FadeIn(cont.etiquetas), run_time=1.0)
        self.play(Create(cont.curva), run_time=1.8)
        self.play(FadeIn(cont.punto), FadeIn(cont.guia),
                  FadeIn(cont.lectura_d), FadeIn(cont.lectura_n),
                  run_time=0.6)
        # A partir de aqui el grupo entero vive en la escena: las relecturas
        # de `a_desplazamiento` entran y salen DENTRO del grupo, asi que si
        # solo estuvieran las piezas sueltas los numeros viejos se quedarian.
        self.add(cont)
        m.lectura.set_opacity(0.0)
        cont.lectura_d.set_opacity(0.0)
        cont.lectura_n.set_opacity(0.0)
        m.add_updater(lambda mob: mob.a_desplazamiento(d.get_value()))
        cont.add_updater(lambda mob: mob.a_desplazamiento(d.get_value()))
        self.play(d.animate.set_value(3 * PASO_FRANJA_NM), run_time=4.5,
                  rate_func=linear)
        m.clear_updaters()
        cont.clear_updaters()
        self.wait(1.6)

        # --- momento: la cifra de una franja -------------------------------
        rot.mostrar(pie_curso("Una franja es media longitud de onda: 316 "
                              "nanómetros."), zona="abajo")
        eq = MathTex(r"N = \frac{2d}{\lambda}", font_size=40, color=C_MEDIDA)
        eq.move_to(np.array([-4.50, -1.95, 0.0]))
        t_paso = tag_hud(f"1 franja = {PASO_FRANJA_NM:.1f} nm")
        t_paso.move_to(np.array([-4.50, -2.66, 0.0]))
        self.play(Write(eq), run_time=1.1)
        self.play(FadeIn(t_paso, shift=0.10 * UP), run_time=0.5)
        self.wait(4.6)

        # --- cierre ---------------------------------------------------------
        rot.mostrar(pie_curso("Tres franjas son 949 nanómetros. Y se cuentan "
                              "de una en una."), zona="abajo")
        t_tres = tag_hud(f"3 franjas = {3 * PASO_FRANJA_NM:.1f} nm")
        t_tres.move_to(t_paso.get_center())
        self.play(FadeOut(t_paso), run_time=0.3)
        self.play(FadeIn(t_tres, shift=0.10 * UP), run_time=0.5)
        self.wait(5.0)
