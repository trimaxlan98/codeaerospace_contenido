class Clip2(Scene):
    """4.4.2 - Perfiles supercriticos (Whitcomb).

    La segunda solucion, y mas fina: si el problema no es la burbuja sino el
    choque que la cierra, aplana el extrados para que la succion sea una
    MESETA en vez de un pico. Con la succion repartida el choque aparece mas
    tarde y mas debil, y la sustentacion que se pierde delante se recupera
    atras. (~42 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("El perfil de Whitcomb")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        par = perfiles_transonicos(cuerda=2.9, alto_cp=1.0,
                                   separacion=1.30, escala_perfil=3.2)
        par.move_to(RIGHT * 0.55 + DOWN * 0.10)

        self.play(FadeIn(par.perfil(0)), FadeIn(par.etiquetas[0]),
                  run_time=0.8)
        self.play(Create(par.curva(0)), run_time=1.0)
        rot.mostrar(pie_curso("Un perfil clásico: el morro curvo acelera "
                              "mucho el aire de golpe."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("Su succión es un pico. Y un pico llega a "
                              "Mach 1 antes que nadie."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        # --- momento: el supercritico ---------------------------------------
        self.play(FadeIn(par.perfil(1)), FadeIn(par.etiquetas[1]),
                  run_time=0.8)
        self.play(Create(par.curva(1)), run_time=1.0)
        rot.mostrar(pie_curso("El supercrítico aplana el extradós. La "
                              "succión deja de ser un pico y se vuelve una "
                              "meseta."), zona="abajo", run_time=0.5)
        self.wait(5.4)

        rot.mostrar(pie_curso("Con el mismo empuje total, pero repartido, el "
                              "flujo local tarda más en llegar a Mach 1."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("Ahí recupera la sustentación que el extradós "
                              "plano le hace perder delante."), zona="abajo",
                    run_time=0.5)
        self.wait(5.2)

        rot.mostrar(pie_curso(f"El resultado: {GANANCIA_WHITCOMB:.2f} de "
                              "Mach más antes de que el arrastre se "
                              "dispare."), zona="abajo", run_time=0.5)
        self.wait(5.0)
