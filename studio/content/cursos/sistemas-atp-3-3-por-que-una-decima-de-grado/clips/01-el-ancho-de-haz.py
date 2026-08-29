class Clip1(Scene):
    """3.3.1 - El ancho de haz sale del plato y de la longitud de onda.
    La comprobacion de coherencia: a media anchura la perdida da
    exactamente 3 dB, que es la definicion del haz. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("El ancho de haz"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        ELEV = 20.0          # elevacion a la que apunta la montura
        LARGO = 5.2          # largo dibujado del haz, en unidades de escena

        # --- el plato de 3 m ---------------------------------------------
        mont = montura(alto=2.0)
        mont.apuntar(el_deg=ELEV)
        destino = LEFT * 5.15 + DOWN * 1.55
        delta = destino - mont.pivote
        mont.shift(delta)
        # `pivote`, `base_izq` y `base_der` son atributos FIJOS, no
        # propiedades: tras el shift quedan desfasados y `.direccion`
        # apuntaria a donde la pieza NACIO. Se arrastran con el mismo delta.
        mont.pivote = mont.pivote + delta
        mont.base_izq = mont.base_izq + delta
        mont.base_der = mont.base_der + delta

        t_plato = tag_junto(mont, f"plato {fmt(D_PLATO, 0)} m",
                            direccion=DOWN, buff=0.16)
        self.play(FadeIn(mont), FadeIn(t_plato), run_time=0.9)
        self.wait(0.5)

        boca = mont.plato.get_center() + mont.direccion * 0.16

        def colocar(pieza):
            """El haz nace horizontal y centrado: se gira sobre su propio
            vertice hasta la elevacion de la montura y se ancla en la boca
            del plato (`move_to` centraria el bounding box del cono)."""
            pieza.rotate(np.radians(ELEV), about_point=pieza.vertice)
            pieza.shift(boca - pieza.vertice)
            pieza.vertice = np.array(boca, dtype=float)
            # Este clip mide el ANCHO, no el desapuntamiento: la marca del
            # satelite se apaga (y tambien en las gemelas, o reaparece en
            # mitad del Transform) para que el unico punto ambar del cuadro
            # sea la sonda que recorre el haz.
            pieza.satelite.set_opacity(0.0)
            return pieza

        def punto(ang_deg, radio):
            """Punto del haz a `ang_deg` GRADOS DE HAZ del eje (la escala
            angular del dibujo es ESC_HAZ, no 1:1)."""
            a = np.radians(ELEV + float(ang_deg) / ESC_HAZ)
            return boca + np.array([np.cos(a), np.sin(a), 0.0]) * radio

        # --- el haz de banda S -------------------------------------------
        h = colocar(haz(TH3_S, error_deg=0.0, largo=LARGO,
                        escala_ang=ESC_HAZ))
        self.play(Create(h.bordes), FadeIn(h.sector), Create(h.eje),
                  run_time=1.6)
        # entro por sus hijos: se consolida antes del primer Transform.
        self.remove(*h.get_family())
        self.add(h)

        ang_dib = TH3_S / ESC_HAZ
        arco = Arc(radius=1.55, arc_center=boca,
                   start_angle=np.radians(ELEV - ang_dib / 2.0),
                   angle=np.radians(ang_dib), color=C_CALCULO,
                   stroke_width=2.6)
        t_banda = tag_hud(f"banda S {fmt(TH3_S, 2)} deg", font_size=21)
        t_banda.next_to(h, DOWN, buff=0.34)
        self.play(Create(arco), FadeIn(t_banda), run_time=0.8)
        self.wait(1.2)

        rot.mostrar(formula_pie(r"\theta_{3dB} \approx 70\,\lambda / D"),
                    zona="abajo")
        self.wait(2.6)
        # La constante 70 engloba la iluminacion del reflector: es una
        # aproximacion de ingenieria, no una identidad. Va en gris.
        rot.mostrar(dato_pie("constante entre 65 y 75"), zona="abajo")
        self.wait(2.4)

        # --- la comprobacion: a media anchura, 3 dB ----------------------
        sonda = Dot(punto(0.0, LARGO * 0.90), radius=0.078, color=C_SAT)
        cont = tag_hud(f"{fmt(0.0, 2)} dB", font_size=27)
        cont.move_to(RIGHT * 4.05 + UP * 0.62)
        t_cont = tag_junto(cont, "perdida", direccion=DOWN, buff=0.22)
        self.play(FadeIn(sonda, scale=1.5), FadeIn(cont), FadeIn(t_cont),
                  run_time=0.7)
        self.wait(0.5)

        # El contador se releva con `become` FUERA de todo play, y DESPUES
        # del movimiento que lo justifica. El "Transform corto" no existe:
        # el `run_time` del play PISA el de cada animacion (manim 0.20,
        # Scene.compile_animations hace setattr por kwarg), asi que un
        # Transform de 0.02 dentro de un play de 0.85 dura 0.85 y deja los
        # digitos a medio morfar. Medido en el frame 4 del primer render.
        for k in (0.25, 0.5, 0.75, 1.0):
            ang = k * TH3_S / 2.0
            perd = perdida_apuntamiento(ang, TH3_S)
            self.play(sonda.animate.move_to(punto(ang, LARGO * 0.90)),
                      run_time=0.85)
            cont.become(tag_hud(f"{fmt(perd, 2)} dB",
                                font_size=27).move_to(cont))
            self.wait(0.40)

        rot.mostrar(cifra_pie(f"media anchura {fmt(L_MEDIA, 1)} dB"),
                    zona="abajo")
        self.wait(2.8)

        # --- se estrecha al subir la frecuencia --------------------------
        # el carril de la cifra se apaga ANTES de cambiar la figura que la
        # justifica.
        rot.limpiar("abajo", run_time=0.35)
        self.play(FadeOut(sonda), FadeOut(cont), FadeOut(t_cont),
                  FadeOut(arco), run_time=0.6)

        h_x = colocar(h.gemela(TH3_X))
        t_x = tag_hud(f"banda X {fmt(TH3_X, 2)} deg", font_size=21)
        t_x.move_to(t_banda)
        self.play(Transform(h, h_x), run_time=1.5)
        # Dos rotulos de distinta longitud NO son gemelos: se relevan por
        # fundido, en dos play seguidos.
        self.play(FadeOut(t_banda), run_time=0.28)
        self.play(FadeIn(t_x), run_time=0.28)
        self.wait(1.6)

        h_ka = colocar(h.gemela(TH3_KA))
        t_ka = tag_hud(f"banda Ka {fmt(TH3_KA, 2)} deg", font_size=21,
                       color=C_PELIGRO)
        t_ka.move_to(t_banda)
        self.play(Transform(h, h_ka), run_time=1.5)
        self.play(FadeOut(t_x), run_time=0.28)
        self.play(FadeIn(t_ka), run_time=0.28)
        self.wait(1.4)

        rot.mostrar(cifra_pie(f"mismo plato {fmt(D_PLATO, 0)} m"),
                    zona="abajo")
        self.wait(2.2)

        panel = panel_cifras(f"S  {fmt(TH3_S, 2)} deg",
                             f"X  {fmt(TH3_X, 2)} deg",
                             (f"Ka {fmt(TH3_KA, 2)} deg", C_PELIGRO))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(3.6)
