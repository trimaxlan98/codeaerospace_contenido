class Clip7(Scene):
    """7 - El espacio muerde. Una placa central resiste cuatro amenazas del
    ambiente espacial que aparecen en relevo alrededor: ciclado termico,
    oxigeno atomico, radiacion UV y micrometeoritos. Cada una se atenua a
    opacidad 0.4 antes de que entre la siguiente; la ultima queda plena.
    (~35 s)"""

    def _sol(self, pos):
        """Icono de ciclado termico: nucleo con 8 rayos cortos, C_FALLA."""
        nucleo = Circle(radius=0.14, stroke_width=2.2, color=C_FALLA)
        nucleo.set_fill(color=C_FALLA, opacity=0.16)
        rayos = VGroup()
        for k in range(8):
            ang = k * (TAU / 8.0)
            u = np.array([np.cos(ang), np.sin(ang), 0.0])
            rayos.add(Line(u * 0.20, u * 0.34, stroke_width=2.2,
                           color=C_FALLA))
        icono = VGroup(nucleo, rayos)
        icono.move_to(pos)
        return icono

    def _flechas_veloces(self, pos, direccion, color=C_FALLA):
        """Icono de oxigeno atomico: 3 flechas finas paralelas hacia la placa."""
        u = direccion / np.linalg.norm(direccion)
        n = np.array([-u[1], u[0], 0.0])
        grupo = VGroup()
        for off in (-0.15, 0.0, 0.15):
            base = pos + n * off - u * 0.17
            punta = pos + n * off + u * 0.17
            grupo.add(Arrow(base, punta, buff=0.0, color=color,
                            stroke_width=2.2, tip_length=0.10,
                            max_tip_length_to_length_ratio=0.5))
        return grupo

    def _ondas_uv(self, pos, direccion, color=C_FAM):
        """Icono de radiacion UV: 3 lineas onduladas cortas hacia la placa."""
        u = direccion / np.linalg.norm(direccion)
        n = np.array([-u[1], u[0], 0.0])
        grupo = VGroup()
        largo, amp, muestras = 0.36, 0.045, 12
        for off in (-0.17, 0.0, 0.17):
            centro = pos + n * off
            pts = []
            for i in range(muestras):
                t = i / (muestras - 1)
                onda = amp * np.sin(t * TAU * 1.5)
                pts.append(centro - u * largo / 2.0 + u * largo * t
                          + n * onda)
            linea = VMobject(color=color, stroke_width=2.0)
            linea.set_points_smoothly(pts)
            grupo.add(linea)
        return grupo

    def _micrometeorito(self, pos, direccion, color=C_FALLA):
        """Icono de micrometeorito: punto con estela detras."""
        u = direccion / np.linalg.norm(direccion)
        cabeza = Dot(pos, radius=0.055, color=color)
        estela = Line(pos - u * 0.55, pos - u * 0.14, stroke_width=2.4,
                      color=color)
        estela.set_stroke(opacity=0.55)
        return VGroup(estela, cabeza)

    def construct(self):
        rot = Rotulos(self)

        # --- momento: HUD y titulo -------------------------------------------
        modulo = hud_modulo("Modulo 07")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("El espacio muerde")
        rot.mostrar(titulo, zona="arriba", run_time=0.7)
        self.wait(0.6)

        # --- momento: la placa central ----------------------------------------
        placa = placa_con_ciclos(ancho=2.4, alto=1.4).placa
        placa.move_to(0.1 * DOWN)
        self.play(Create(placa), run_time=0.7)
        self.wait(0.3)

        # --- momento: amenaza 1, ciclado termico (arriba-izquierda) ------------
        pos_sol = np.array([-2.9, 1.1, 0.0])
        sol = self._sol(pos_sol)
        tag_sol = tag_junto(sol, "±200 °C por órbita", direccion=UP)
        amenaza1 = VGroup(sol, tag_sol)
        self.play(FadeIn(amenaza1, scale=0.9), run_time=0.6)
        rot.mostrar(pie_curso("Cada 90 minutos, del horno al congelador: "
                              "el ciclado térmico fatiga sin tocar."),
                   zona="abajo", run_time=0.5)
        self.wait(5.2)

        # --- momento: amenaza 1 se atenua, entra amenaza 2 (arriba-derecha) ---
        self.play(amenaza1.animate.set_opacity(0.4), run_time=0.4)
        pos_oxi = np.array([2.9, 1.1, 0.0])
        oxigeno = self._flechas_veloces(pos_oxi,
                                        np.array([-1.0, -0.42, 0.0]))
        tag_oxi = tag_junto(oxigeno, "oxígeno atómico", direccion=UP)
        amenaza2 = VGroup(oxigeno, tag_oxi)
        self.play(FadeIn(amenaza2, scale=0.9), run_time=0.6)
        rot.mostrar(pie_curso("En órbita baja, oxígeno atómico: lija "
                              "química que adelgaza superficies."),
                   zona="abajo", run_time=0.5)
        self.wait(5.2)

        # --- momento: amenaza 2 se atenua, entra amenaza 3 (abajo-izquierda) --
        self.play(amenaza2.animate.set_opacity(0.4), run_time=0.4)
        pos_uv = np.array([-2.9, -1.4, 0.0])
        uv = self._ondas_uv(pos_uv, np.array([1.0, 0.42, 0.0]))
        tag_uv = tag_junto(uv, "radiación UV", direccion=DOWN)
        amenaza3 = VGroup(uv, tag_uv)
        self.play(FadeIn(amenaza3, scale=0.9), run_time=0.6)
        rot.mostrar(pie_curso("La radiación rompe cadenas de polímero: lo "
                              "flexible se vuelve quebradizo."),
                   zona="abajo", run_time=0.5)
        self.wait(5.2)

        # --- momento: amenaza 3 se atenua, entra amenaza 4 (abajo-derecha) ----
        self.play(amenaza3.animate.set_opacity(0.4), run_time=0.4)
        pos_met = np.array([2.9, -1.4, 0.0])
        met = self._micrometeorito(pos_met, np.array([-1.0, 0.42, 0.0]))
        tag_met = tag_junto(met, "micrometeoritos", direccion=DOWN)
        amenaza4 = VGroup(met, tag_met)
        self.play(FadeIn(amenaza4, scale=0.9), run_time=0.6)
        rot.mostrar(pie_curso("Y basura y polvo a 15 km/s: cráteres del "
                              "tamaño de un grano de sal."), zona="abajo",
                   run_time=0.5)
        self.wait(5.2)

        # --- momento: cierre, en el espacio no hay taller -----------------------
        rot.mostrar(pie_curso("En el espacio no hay taller: el material "
                              "aguanta solo o la misión muere."),
                   zona="abajo", run_time=0.5)
        self.wait(5.2)
