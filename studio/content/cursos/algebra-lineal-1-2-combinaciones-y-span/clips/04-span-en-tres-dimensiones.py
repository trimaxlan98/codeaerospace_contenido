class Clip4(Scene):
    """1.2.4 - En tres dimensiones, dos vectores generan un plano; un
    tercero que no vive ahi añade la dimension que falta: el espacio.
    Cierra la leccion. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Span en tres dimensiones")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: dos vectores en el espacio -----------------------------
        es = espacio3()
        self.play(FadeIn(es), run_time=0.9)
        rot.mostrar(pie_curso("La misma idea, un eje mas: a*u + b*v en "
                              "tres dimensiones."), zona="abajo",
                    run_time=0.5)
        u3 = vector3(es, U3, color=C_VEC, nombre=r"\vec u")
        v3 = vector3(es, V3, color=C_VEC_2, nombre=r"\vec v")
        self.play(GrowArrow(u3.flecha), GrowArrow(v3.flecha), run_time=0.9)
        self.play(FadeIn(u3.etiqueta), FadeIn(v3.etiqueta), run_time=0.3)
        self.wait(3.2)

        # --- momento: el plano que generan --------------------------------
        rot.mostrar(pie_curso("Dos vectores no alineados generan un plano: "
                              "todo a*u + b*v vive ahi."), zona="abajo",
                    run_time=0.5)
        parche = plano_generado(es, U3, V3, color=C_IMG, opacidad=0.24)
        self.play(FadeIn(parche), run_time=1.2)
        # El parche translucido, si queda delante, destine el color de u y v
        # (rol de color arruinado); lo mandamos detras de las flechas ya
        # dibujadas para que sigan leyendose en su color puro.
        self.bring_to_back(parche)
        self.wait(3.4)

        # --- momento: una combinacion vive dentro ---------------------------
        rot.mostrar(pie_curso("w' = u + v es una combinacion: por eso vive "
                              "dentro del plano."), zona="abajo",
                    run_time=0.5)
        w3_dentro = vector3(es, W3_DENTRO, color=C_IMG, nombre=r"\vec{w}'",
                            font_size=26)
        # La punta de w3_dentro cae junto a la etiqueta "y" del eje (vector3
        # no acepta etiqueta_dir como el Vector 2D): se reubica a mano bajo
        # la punta, lejos del eje, para que ninguna de las dos se pise.
        w3_dentro.etiqueta.move_to(w3_dentro.punta() + 0.34 * DOWN)
        w3_dentro.set_opacity(0.55)
        self.play(GrowArrow(w3_dentro.flecha), FadeIn(w3_dentro.etiqueta),
                  run_time=1.0)
        self.wait(3.4)

        # --- momento: w se sale ---------------------------------------------
        rot.mostrar(pie_curso("Pero w se sale del plano: ninguna pareja "
                              "(a, b) lo alcanza."), zona="abajo",
                    run_time=0.5)
        # C_K ya lo lleva v (via C_VEC_2 = C_K) y el eje z de espacio3(): un
        # tercer vector con el mismo violeta se confunde con v en pantalla.
        # C_PROPIO (fucsia) queda libre en este clip y distingue a w a
        # simple vista de u (rojo), v (violeta) y w' (verde).
        w3 = vector3(es, W3, color=C_PROPIO, nombre=r"\vec w")
        self.play(GrowArrow(w3.flecha), FadeIn(w3.etiqueta), run_time=1.0)
        self.wait(3.6)

        # --- cierre de la leccion -------------------------------------------
        cierre_leccion(self, rot, "Dos flechas: un plano.",
                       "Tres, si no se esconden: el espacio.",
                       "La proxima lección pregunta cuándo un vector "
                       "sobra.", es, u3, v3, parche, w3_dentro, w3)
