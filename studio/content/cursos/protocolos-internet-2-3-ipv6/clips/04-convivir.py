class Clip4(Scene):
    """2.3.4 - La cabecera IPv6, fija en 40 bytes, sin checksum ni
    fragmentacion en transito, junto a la de IPv4: que campos se fueron,
    cuales quedaron (renombrados) y cual es nuevo. Doble pila y tunel para
    convivir mientras dura la mudanza. Cierre de la leccion. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Convivir")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: las dos cabeceras, una al lado de la otra -------------
        rot.mostrar(pie_curso("IPv6 fija la cabecera en 40 bytes: nada "
                              "que calcular, nada que revisar."),
                    zona="abajo", run_time=0.5)
        # Las dos cabeceras van APILADAS y a todo el ancho, no lado a
        # lado: con 5.0 de ancho los campos estrechos (Version, IHL,
        # Banderas) se encogian a ~6 px y no habia forma de leerlos.
        # Sin valores: con nombre Y valor la fila necesita >=0.42 de alto y
        # las dos cabeceras no caben apiladas (se encimaban las filas). Este
        # clip compara QUE campos existen; los valores son cosa de la 2.1.
        c4 = cabecera(CAMPOS_IPV4, {}, ancho=7.4,
                      alto_fila=0.27, fs=13, color=C_CAPA)
        c6 = cabecera(CAMPOS_IPV6, {}, ancho=7.4, alto_fila=0.27, fs=13,
                      color=C_CAPA)
        c4.move_to(UP * 1.75)
        c6.move_to(DOWN * 0.85)
        et4 = tag_hud("IPv4\n%d B" % BYTES_IPV4, font_size=18,
                     color=C_CIFRA)
        et6 = tag_hud("IPv6\n%d B fijos" % BYTES_IPV6, font_size=18,
                     color=C_CIFRA)
        et4.next_to(c4, LEFT, buff=0.40)
        et6.next_to(c6, LEFT, buff=0.40)
        self.play(FadeIn(c4), FadeIn(et4), run_time=0.7)
        self.play(FadeIn(c6), FadeIn(et6), run_time=0.7)
        self.wait(3.6)

        # --- momento: los campos que se fueron -------------------------------
        rot.mostrar(pie_curso("Cinco campos se fueron: los que servian "
                              "para revisar o partir el paquete en el "
                              "camino."),
                    zona="abajo", run_time=0.5)
        for nombre in CAMPOS_FUERA:
            c4.iluminar(nombre, C_PERDIDA)
        self.wait(4.4)

        # --- momento: los que quedan (renombrados) y el nuevo ----------------
        rot.mostrar(pie_curso("Siete quedan, algunos con otro nombre. Y "
                              "aparece uno nuevo: la etiqueta de flujo."),
                    zona="abajo", run_time=0.5)
        for nombre in CAMPOS_IGUALES:
            c4.iluminar(nombre, C_OK)
            c6.iluminar(nombre, C_OK)
        for antes, ahora in CAMPOS_RENOMBRADOS:
            c4.iluminar(antes, C_OK)
            c6.iluminar(ahora, C_OK)
        et_nuevo = tag_hud("nuevo", font_size=13, color=C_EJE)
        et_nuevo.next_to(c6.campo(CAMPO_NUEVO_IPV6), UP, buff=0.10)
        self.play(FadeIn(et_nuevo), run_time=0.5)
        self.wait(4.4)

        # --- momento: doble pila, tunel y adopcion real ----------------------
        rot.mostrar(pie_curso("Mientras dura la mudanza: doble pila donde "
                              "se puede, tunel donde no. Cerca del %s%% "
                              "del trafico mundial ya va por IPv6 (medicion "
                              "publica, no de esta libreria)."
                              % fmt(ADOPCION_IPV6_PCT, 0)),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(c4), FadeOut(c6), FadeOut(et4), FadeOut(et6),
                  FadeOut(et_nuevo), run_time=0.6)
        a = nodo("host", "A", tam=0.55, color=C_RED)
        b = nodo("host", "B", tam=0.55, color=C_RED)
        r1 = nodo("router", "R1", tam=0.5, color=C_RED)
        r2 = nodo("router", "R2", tam=0.5, color=C_RED)
        a.move_to(LEFT * 5.2)
        r1.move_to(LEFT * 1.7 + UP * 0.6)
        r2.move_to(RIGHT * 1.7 + UP * 0.6)
        b.move_to(RIGHT * 5.2)
        e_dual = enlace(a.centro(), r1.centro(), "doble pila", C_RED)
        e_tun = enlace(r1.centro(), r2.centro(), "tunel IPv6-en-IPv4",
                       C_CAPA, punteada=True)
        e_dual2 = enlace(r2.centro(), b.centro(), "doble pila", C_RED)
        pct = tag_hud("adopcion IPv6: ~%s%%" % fmt(ADOPCION_IPV6_PCT, 0),
                     font_size=22, color=C_CIFRA)
        pct.move_to(DOWN * 1.6)
        red = VGroup(a, r1, r2, b, e_dual, e_tun, e_dual2)
        self.play(FadeIn(red), run_time=0.9)
        self.play(FadeIn(pct, shift=0.15 * UP), run_time=0.6)
        self.wait(4.4)

        # --- cierre de la leccion --------------------------------------------
        cierre_leccion(self, rot,
                       "La red nueva ya está aquí.",
                       "Lleva veinte años mudándose.",
                       "Siguiente: como se encuentra el camino sin un "
                       "mapa completo.",
                       red, pct)
