class Clip1(Scene):
    """4.1.1 - El curso 21 repetia cada bit x3: gasta 3 bits por 1 util
    y el voto de mayoria aun puede perder con dos copias volteadas.
    (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Repetir no basta")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el mensaje y su copia x3 -----------------------------
        rot.mostrar(pie_curso("El curso 21 protegia cada bit repitiendolo "
                              "tres veces."),
                    zona="abajo", run_time=0.5)
        msg = tren_bits(MSG_REP, lado=0.5)
        msg.move_to(UP * 1.6)
        et_msg = tag_junto(msg, "el mensaje", direccion=UP, buff=0.14)
        self.play(FadeIn(msg), FadeIn(et_msg), run_time=0.8)
        self.wait(1.8)

        rep = tren_bits(REP_TRIPLE, lado=0.5, color=C_BIT)
        rep.move_to(DOWN * 0.15)
        et_rep = tag_junto(rep, "cada bit, x3", direccion=DOWN, buff=0.16)
        self.play(FadeIn(rep), FadeIn(et_rep), run_time=1.1)
        cifra_gasto = tag_hud(f"{fmt(GASTO_REP, 0)} bits por bit util",
                              font_size=19, color=C_CIFRA)
        cifra_gasto.next_to(rep, DOWN, buff=0.55)
        self.play(FadeIn(cifra_gasto), run_time=0.5)
        self.wait(4.4)

        # --- momento: el canal voltea dos copias ---------------------------
        rot.mostrar(pie_curso("El canal voltea dos de las tres copias del "
                              "primer bit."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(cifra_gasto), run_time=0.4)
        recibido = rep.con_bits(REP_RECIBIDO)
        recibido.move_to(DOWN * 2.1)
        recibido.marcar(1, color=C_RUIDO)
        recibido.marcar(2, color=C_RUIDO)
        et_recibido = tag_junto(recibido, "lo que llega", direccion=DOWN,
                                buff=0.16)
        self.play(TransformFromCopy(rep, recibido), FadeIn(et_recibido),
                  run_time=1.2)
        self.wait(4.6)

        # --- momento: el voto de mayoria pierde ------------------------------
        rot.mostrar(pie_curso("El voto de mayoria pierde: dos ceros ganan "
                              "al unico uno."),
                    zona="abajo", run_time=0.5)
        cifra_real = tag_hud(f"bit real = {fmt(MSG_REP[0], 0)}",
                             font_size=19, color=C_BIT)
        cifra_voto = tag_hud(f"voto = {fmt(VOTO_PRIMER_BIT, 0)}",
                             font_size=19, color=C_RUIDO)
        panel = panel_derecha(cifra_real, cifra_voto)
        self.play(FadeIn(panel), run_time=0.6)
        self.play(Indicate(cifra_voto, color=C_RUIDO, scale_factor=1.15),
                  run_time=1.0)
        self.wait(4.4)

        # --- momento: hace falta gastar mejor --------------------------------
        rot.mostrar(pie_curso("Repetir gasta bits y aun asi puede fallar. "
                              "Hace falta gastar mejor."),
                    zona="abajo", run_time=0.5)
        self.wait(6.4)
