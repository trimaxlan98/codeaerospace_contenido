class Clip2(Scene):
    """1.1.2 - Sumar vectores es caminar uno tras otro; la suma es el atajo
    del origen al final, y en listas se suma componente a componente. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Sumar es caminar")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        pl = plano_leccion(vivo=False)
        u = vector(pl, U_SUMA, color=C_VEC, nombre=r"\vec u")
        v = vector(pl, V_SUMA, color=C_VEC_2, nombre=r"\vec v")
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Dos vectores. ¿Qué querría decir sumarlos?"),
                    zona="abajo", run_time=0.5)
        self.play(GrowArrow(u.flecha), GrowArrow(v.flecha), run_time=0.9)
        self.play(FadeIn(u.etiqueta), FadeIn(v.etiqueta), run_time=0.3)
        self.wait(3.6)

        # --- momento: v se traslada a la punta de u -----------------------
        rot.mostrar(pie_curso("Sumar es caminar: primero u, y luego v desde "
                              "donde te dejó u."), zona="abajo",
                    run_time=0.5)
        v_movida = flecha_libre(pl, U_SUMA, SUMA, color=C_VEC_2)
        v_copia = flecha_libre(pl, (0, 0), V_SUMA, color=C_VEC_2)
        self.add(v_copia)
        self.play(Transform(v_copia, v_movida), run_time=1.4)
        self.wait(3.4)

        # --- momento: la resultante ---------------------------------------
        rot.mostrar(pie_curso("La suma es la flecha que se ahorra el "
                              "rodeo: del origen al punto final."),
                    zona="abajo", run_time=0.5)
        s = vector(pl, SUMA, color=C_IMG, nombre=r"\vec u + \vec v",
                   etiqueta_dir=np.array([-0.55, 0.85, 0.0]))
        self.play(GrowArrow(s.flecha), run_time=1.0)
        self.play(FadeIn(s.etiqueta), run_time=0.3)
        self.wait(3.8)

        # --- momento: el orden no importa ---------------------------------
        rot.mostrar(pie_curso("Y da igual el orden: v y luego u cierran el "
                              "mismo paralelogramo."), zona="abajo",
                    run_time=0.5)
        u_movida = flecha_libre(pl, V_SUMA, SUMA, color=C_VEC, opacidad=0.55)
        par = paralelogramo_de(pl, U_SUMA, V_SUMA, color=C_IMG,
                               opacidad=0.12, borde=1.2)
        self.play(FadeIn(par), GrowArrow(u_movida), run_time=1.0)
        self.wait(3.8)

        # --- momento: la cuenta ------------------------------------------
        rot.mostrar(pie_curso("En el idioma de las listas: se suma "
                              "componente a componente."), zona="abajo",
                    run_time=0.5)
        cu = vector_columna(U_SUMA, color=C_VEC, font_size=34)
        cv = vector_columna(V_SUMA, color=C_VEC_2, font_size=34)
        cs = vector_columna(SUMA, color=C_IMG, font_size=34)
        mas = MathTex("+", font_size=34, color=C_TENUE)
        igual = MathTex("=", font_size=34, color=C_TENUE)
        cuenta = VGroup(cu, mas, cv, igual, cs).arrange(RIGHT, buff=0.22)
        panel = panel_derecha(cuenta)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.7)
        self.wait(4.4)

        rot.mostrar(pie_curso("Geometría y aritmética cuentan la misma "
                              "historia. Siempre."), zona="abajo",
                    run_time=0.5)
        self.play(Indicate(s.flecha, color=C_IMG, scale_factor=1.05),
                  Indicate(cs, color=C_IMG, scale_factor=1.08), run_time=0.9)
        self.wait(4.6)
