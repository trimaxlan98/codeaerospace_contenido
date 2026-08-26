class Clip4(Scene):
    """3.3.4 - Un AS anuncia un prefijo que no es suyo. Con el mismo
    prefijo casi no engana a nadie; con uno mas especifico se lleva la
    red entera, porque gana el prefijo mas largo. RPKI es el freno.
    Cierre de la leccion. (~39 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("El secuestro")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        topo = topologia(POS_AS, ARISTAS_AS, TIPOS_AS, costos=False,
                         tam=0.46, fs=14)
        etiquetas_a(topo, ETIQ_AS)

        # --- momento: el prefijo tiene dueno ------------------------------
        rot.mostrar(pie_curso("El prefijo %s es de %s, y toda la red lo "
                              "sabe." % (PREFIJO, LEGITIMO)),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(topo.enlaces), FadeIn(topo.nodos), run_time=1.0)
        topo.nodo(LEGITIMO).forma.set_stroke(C_OK, width=3.6)
        et_dueno = tag_hud("%s  ->  %d hosts, origen %s"
                           % (PREFIJO, CIDR_LEG["hosts"], LEGITIMO),
                           font_size=19, color=C_OK)
        et_dueno.move_to(DOWN * 2.62)
        self.play(FadeIn(et_dueno), run_time=0.4)
        self.wait(3.8)

        # --- momento: mentir con el mismo prefijo -------------------------
        rot.mostrar(pie_curso("%s anuncia el MISMO prefijo. Solo le creen "
                              "los que le quedan mas cerca."
                              % ATACANTE),
                    zona="abajo", run_time=0.5)
        self.play(topo.nodo(ATACANTE).forma.animate.set_stroke(
            C_PERDIDA, width=3.6), run_time=0.5)
        self.play(*[topo.nodo(k).forma.animate.set_stroke(C_PERDIDA,
                                                          width=3.6)
                    for k in SEC_MISMO["envenenados"]], run_time=0.5)
        et_cuenta = tag_hud("creen al atacante:  %d de %d ASes  =  %s %%"
                            % (SEC_MISMO["n_envenenados"],
                               SEC_MISMO["n_total"],
                               fmt(SEC_MISMO["pct"], 0)),
                            font_size=21, color=C_PERDIDA)
        et_cuenta.move_to(DOWN * 2.62)
        et_porque = tag_hud("%s lo tiene a %d salto; al dueno real, a %d"
                            % (AS_CAE, SALTOS_ATA, SALTOS_LEG),
                            font_size=19, color=C_CIFRA)
        et_porque.move_to(DOWN * 2.18)
        self.play(FadeOut(et_dueno), FadeIn(et_cuenta), FadeIn(et_porque),
                  run_time=0.5)
        self.wait(3.9)

        # --- momento: la mitad del prefijo, mas especifica ----------------
        rot.mostrar(pie_curso("Ahora anuncia la mitad: %s. Un prefijo mas "
                              "especifico." % PREF_ESPECIFICO),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(topo), FadeOut(et_cuenta), FadeOut(et_porque),
                  run_time=0.5)
        pk_leg = paquete([("prefijo anunciado", 2.4, PREFIJO),
                          ("origen", 1.0, LEGITIMO)],
                         ancho=4.6, alto=0.62, fs=16, color=C_OK)
        pk_ata = paquete([("prefijo anunciado", 2.4, PREF_ESPECIFICO),
                          ("origen", 1.0, ATACANTE)],
                         ancho=4.6, alto=0.62, fs=16, color=C_PERDIDA)
        anuncios = VGroup(pk_leg, pk_ata).arrange(DOWN, buff=0.78)
        anuncios.move_to(UP * 1.30)
        self.play(LaggedStart(FadeIn(pk_leg), FadeIn(pk_ata),
                              lag_ratio=0.45), run_time=0.9)
        cifras = VGroup(
            tag_hud("destino %s: coincide con %d rutas anunciadas"
                    % (IP_VICTIMA, LPM["n_coinciden"]), font_size=20),
            tag_hud("el /%d cubre %d direcciones de las %d del /%d"
                    % (CIDR_ATA["bits"], CIDR_ATA["direcciones"],
                       CIDR_LEG["direcciones"], CIDR_LEG["bits"]),
                    font_size=20, color=C_CAPA),
            tag_hud("gana %s (%d bits): el trafico va a %s"
                    % (LPM["elegida"], LPM["bits"], LPM["siguiente"]),
                    font_size=21, color=C_PERDIDA),
        ).arrange(DOWN, buff=0.24, aligned_edge=LEFT)
        cifras.move_to(DOWN * 1.62)
        self.play(LaggedStart(*[FadeIn(c, shift=0.12 * UP) for c in cifras],
                              lag_ratio=0.32), run_time=1.0)
        self.wait(4.0)

        # --- momento: se la lleva entera ----------------------------------
        rot.mostrar(pie_curso("No hay debate: gana el prefijo mas largo. "
                              "La misma regla del modulo 2."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(anuncios), FadeOut(cifras), run_time=0.45)
        for k in SEC_ESPEC["envenenados"]:
            topo.nodo(k).forma.set_stroke(C_PERDIDA, width=3.6)
        self.play(FadeIn(topo), run_time=0.8)
        et_todos = tag_hud("creen al atacante:  %d de %d ASes  =  %s %%"
                           % (SEC_ESPEC["n_envenenados"],
                              SEC_ESPEC["n_total"],
                              fmt(SEC_ESPEC["pct"], 0)),
                           font_size=21, color=C_PERDIDA)
        et_todos.move_to(DOWN * 2.62)
        self.play(FadeIn(et_todos), run_time=0.45)
        self.wait(3.9)

        # --- momento: RPKI, el freno --------------------------------------
        rot.mostrar(pie_curso("RPKI firma quien puede originar cada "
                              "prefijo: el que comprueba, descarta."),
                    zona="abajo", run_time=0.5)
        insignia = tag_hud("ROA", font_size=18, color=C_CLAVE)
        insignia.next_to(topo.nodo(LEGITIMO).forma, DOWN, buff=0.20)
        et_rpki = tag_hud("RPKI: solo %s puede originar %s"
                          % (LEGITIMO, PREFIJO), font_size=20,
                          color=C_CLAVE)
        et_rpki.move_to(DOWN * 2.62)
        self.play(*[topo.nodo(k).forma.animate.set_stroke(C_RED, width=2.6)
                    for k in SEC_ESPEC["envenenados"]],
                  FadeOut(et_todos), run_time=0.6)
        self.play(FadeIn(et_rpki), FadeIn(insignia), run_time=0.45)
        self.wait(4.2)

        # --- cierre de la leccion -----------------------------------------
        cierre_leccion(
            self, rot,
            "La red que nadie manda se sostiene en la palabra.",
            "Y a veces alguien miente.",
            "RPKI firma el origen, no el camino: solo frena al que filtra.",
            topo, et_rpki, insignia, espera=4.0)
