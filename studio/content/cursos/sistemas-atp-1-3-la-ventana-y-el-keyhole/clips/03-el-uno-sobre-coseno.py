class Clip3(Scene):
    """1.3.3 - El mismo cielo, dos pases: el que mejor cierra el enlace
    es el que le pide 18 veces mas velocidad al acimut. (~42 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("El uno sobre coseno"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        AZ_CULM = 140.0            # eleccion de dibujo: los dos pases
                                   # culminan en el mismo acimut, asi que
                                   # salen como dos cuerdas paralelas.

        def tramo(traza, el_min, n=601):
            ts = np.linspace(0.0, 1.0, n)
            dentro = [t for t in ts if traza.el_en(t) >= el_min]
            if not dentro:
                return None
            return float(dentro[0]), float(dentro[-1])

        vista = vista_polar(radio=2.22, font_size=16)
        vista.move_to(LEFT * 3.35 + UP * 0.20)
        self.play(Create(vista), run_time=1.4)

        aguja = aguja_velocidad(maximo=10.0, valor=0.0, ancho=2.7,
                                color=C_CALCULO)
        aguja.move_to(RIGHT * 3.55 + DOWN * 1.05)
        self.play(FadeIn(aguja), run_time=0.6)

        # La lectura sale de la GEOMETRIA de la aguja, asi que no puede
        # discrepar de lo que marca en el frame.
        def lectura():
            v = float(aguja.valor)
            return tag_hud(f"{fmt(v, 2)} deg/s", font_size=26,
                           color=C_PELIGRO if aguja.en_peligro(v)
                           else C_CALCULO).move_to(RIGHT * 3.55
                                                   + DOWN * 2.35)

        lect_ini = lectura()
        self.play(FadeIn(lect_ini), run_time=0.4)
        self.remove(lect_ini)
        lect = always_redraw(lectura)
        self.add(lect)
        self.wait(0.5)

        # --- pase 1: culmina a 30 grados ---------------------------------
        traza_a = traza_pase(vista, el_max=EL_MAX_BAJO,
                             az_culminacion=AZ_CULM, muestras=150,
                             color=C_CIELO)
        t_a = tag_hud(f"el max {fmt(EL_MAX_BAJO, 0)} deg", font_size=21,
                      color=C_CIELO)
        t_a.move_to(RIGHT * 3.55 + UP * 1.32)
        self.play(Create(traza_a), run_time=1.5)
        self.play(FadeIn(t_a), run_time=0.4)

        u = ValueTracker(0.0)
        sat = Dot(traza_a.punto_en(0.0), radius=0.085, color=C_SAT)
        sat.add_updater(lambda m: m.move_to(traza_a.punto_en(u.get_value())))
        self.play(FadeIn(sat, scale=1.5), run_time=0.5)
        self.play(u.animate.set_value(0.5),
                  Rotate(aguja.aguja, aguja.a_valor(AZ_BAJO) - aguja.angulo,
                         about_point=aguja.pivote),
                  run_time=2.3)
        self.wait(0.6)
        rot.mostrar(cifra_pie(f"acimut {fmt(AZ_BAJO, 2)} deg/s"),
                    zona="abajo")
        self.wait(1.7)

        # se deja marcada la aguja de este pase: la del siguiente se lee
        # contra ella
        marca = aguja.aguja.copy().set_stroke(color=C_CIELO, opacity=0.55,
                                              width=3.0)
        self.add(marca)
        # el carril se apaga ANTES de que la aguja baje: si no, un frame
        # muestrea "acimut 0.51" con la aguja marcando 0.07.
        rot.limpiar("abajo", run_time=0.3)
        self.play(u.animate.set_value(0.97),
                  Rotate(aguja.aguja,
                         aguja.a_valor(AZ_BAJO * 0.12) - aguja.angulo,
                         about_point=aguja.pivote),
                  run_time=1.9)
        sat.clear_updaters()
        self.play(FadeOut(sat), traza_a.animate.set_stroke(opacity=0.45),
                  run_time=0.6)

        # --- pase 2: el cenital, el que mejor cierra el enlace ------------
        traza_b = traza_pase(vista, el_max=EL_MAX_ALTO,
                             az_culminacion=AZ_CULM, muestras=150,
                             color=C_SAT)
        t_b = tag_hud(f"el max {fmt(EL_MAX_ALTO, 0)} deg", font_size=21,
                      color=C_SAT)
        t_b.move_to(RIGHT * 3.55 + UP * 0.80)
        self.play(Create(traza_b), run_time=1.5)
        self.play(FadeIn(t_b), run_time=0.4)

        v = ValueTracker(0.0)
        sat2 = Dot(traza_b.punto_en(0.0), radius=0.085, color=C_SAT)
        sat2.add_updater(lambda m: m.move_to(traza_b.punto_en(v.get_value())))
        self.play(FadeIn(sat2, scale=1.5), run_time=0.5)
        self.play(v.animate.set_value(0.5),
                  Rotate(aguja.aguja, aguja.a_valor(AZ_ALTO) - aguja.angulo,
                         about_point=aguja.pivote),
                  run_time=2.5)
        self.wait(0.8)
        rot.mostrar(cifra_pie(f"acimut {fmt(AZ_ALTO, 2)} deg/s"),
                    zona="abajo")
        self.wait(1.9)

        # --- el agujero: donde el rotor ya no puede -----------------------
        # el satelite se retira del cenit: parado en la culminacion tapa
        # justo el trozo ciego que hay que ver.
        sat2.clear_updaters()
        self.play(FadeOut(sat2), run_time=0.4)
        cono = cono_keyhole(vista, radio_deg=R_KEYHOLE, color=C_PELIGRO)
        # el relleno baja a 0.18: el trozo ciego de la traza es del MISMO
        # rojo y sobre el relleno de 0.25 se perdia.
        cono.set_fill(opacity=0.18)
        par = tramo(traza_b, 90.0 - R_KEYHOLE)
        ciego = Line(traza_b.punto_en(par[0]), traza_b.punto_en(par[1]),
                     color=C_PELIGRO, stroke_width=7.0)
        self.play(FadeIn(cono), run_time=0.8)
        self.play(Create(ciego), run_time=0.6)
        rot.mostrar(dato_pie(f"rotor {fmt(ROTOR_MAX, 1)} deg/s"),
                    zona="abajo")
        self.wait(1.9)
        rot.mostrar(cifra_pie(f"keyhole {fmt(R_KEYHOLE, 1)} deg"),
                    zona="abajo")
        self.wait(1.8)

        # el agujero no es del cielo: es del rotor
        cono_rapido = cono_keyhole(vista, radio_deg=R_KEYHOLE_RAPIDO,
                                   color=C_PELIGRO)
        cono_rapido.set_fill(opacity=0.18)
        # el tope del rotor rapido es el fondo de escala de la aguja: la
        # cifra se lee del propio instrumento, no se escribe a mano.
        rot.mostrar(dato_pie(f"rotor {fmt(aguja.maximo, 0)} deg/s"),
                    zona="abajo")
        self.play(Transform(cono, cono_rapido), run_time=1.0)
        self.wait(1.1)
        rot.mostrar(cifra_pie(f"keyhole {fmt(R_KEYHOLE_RAPIDO, 1)} deg"),
                    zona="abajo")
        self.wait(1.8)

        rot.mostrar(cifra_pie(f"{fmt(RAZON_EXIGENCIA, 2)}x mas exigente"),
                    zona="abajo")
        self.wait(2.2)

        panel = panel_cifras(f"d {fmt(D_BAJO, 0)} km  {fmt(AZ_BAJO, 2)} deg/s",
                             (f"d {fmt(D_ALTO, 0)} km  {fmt(AZ_ALTO, 2)}"
                              " deg/s", C_PELIGRO),
                             f"{fmt(RAZON_EXIGENCIA, 2)}x mas exigente")
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(3.4)
