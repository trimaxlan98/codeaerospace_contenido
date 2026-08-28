class Clip(Scene):
    """01 · El cañon de Newton — por que no se cae.

    El gancho del curso. El mismo disparo horizontal desde una montaña de
    400 km, cada vez mas rapido: las balas caen a 11.8, 17.5, 27.4 y 49.2
    grados de distancia, y la quinta falla el suelo y da la vuelta entera.
    Despues, la cuenta que lo explica: en un segundo el satelite CAE 4.347 m
    y el suelo se aleja otros 4.347. Cae todo el rato; nunca llega.

    Todas las cifras las miden `satelites.canon_newton` (RK4 sobre dos
    cuerpos) y `satelites.caida_vs_curvatura` durante el render. La escala
    es REAL: el anillo de 400 km casi roza el planeta porque asi es.
    """

    R_GLOBO = 2.75            # radio del planeta en unidades de escena
    ALTURA_KM = 400.0
    FRACCIONES = (0.50, 0.65, 0.80, 0.92, 1.00)

    def _a_escena(self, pts, centro):
        """Puntos de la libreria (radios terrestres) -> escena, con el cañon
        arriba. La libreria dispara desde (r,0) hacia +y; girar 90 grados
        pone la montaña en lo alto del globo y la bala saliendo hacia la
        izquierda, que en columna es lo que se lee."""
        pts = np.asarray(pts, dtype=np.float64)
        girado = np.column_stack([-pts[:, 1], pts[:, 0]])
        return girado * self.R_GLOBO + np.array([centro[0], centro[1]])

    def construct(self):
        # --- lo que se mide (antes de dibujar nada) -----------------
        v_orb = sa.velocidad_circular(self.ALTURA_KM)
        disparos = [sa.canon_newton(v_orb * f, self.ALTURA_KM, dt_s=1.0,
                                    pasos=8000) for f in self.FRACCIONES]
        cuenta = sa.caida_vs_curvatura(self.ALTURA_KM, 1.0)

        marca = hud_pieza("01 . el canon")
        tierra = globo(self.R_GLOBO)
        centro = tierra.get_center()
        anillo = anillo_orbita(tierra, self.ALTURA_KM, opacidad=0.0)

        # La montaña: el pelo de 400 km del que sale el disparo, a escala.
        cima = centro + UP * self.R_GLOBO * (1.0 + self.ALTURA_KM
                                             / sa.R_TIERRA_KM)
        torre = Line(centro + UP * self.R_GLOBO, cima,
                     stroke_color=C_SAT, stroke_width=2.4)
        canon = Triangle(stroke_width=0, fill_color=C_SAT, fill_opacity=1.0)
        canon.height = 0.22
        canon.rotate(-PI / 2).move_to(cima)

        self.play(FadeIn(marca, shift=DOWN * 0.16), run_time=0.55)
        self.wait(0.35)
        self.play(Create(tierra), run_time=1.10)
        self.play(GrowFromPoint(torre, centro + UP * self.R_GLOBO),
                  FadeIn(canon, scale=0.6), run_time=0.55)
        self.wait(0.80)

        # --- los cinco disparos -------------------------------------
        pie = medida(f"{v_orb * self.FRACCIONES[0]:.2f}", "velocidad",
                     "km / s", color=C_MEDIDO, color_sub=C_EXTERNO)
        self.play(FadeIn(pie.etiqueta), FadeIn(pie.sub),
                  FadeIn(pie.numero, scale=1.08), run_time=0.55)

        trazos, marcas_impacto, camino_orbita = [], [], None
        for i, (frac, d) in enumerate(zip(self.FRACCIONES, disparos)):
            ultimo = i == len(self.FRACCIONES) - 1
            pts = d["puntos"]
            if len(pts) > 460:                 # una corners de 5657 puntos
                pts = pts[::max(1, len(pts) // 460)]   # se dibuja igual y
            xy = self._a_escena(pts, centro)           # cuesta la decima parte
            # El disparo que FALLA va tenue y fino; el que se queda arriba,
            # vivo y grueso. Ambar y naranja son casi el mismo color a
            # grosor 2 (se vio en el primer render): la diferencia la tiene
            # que hacer el peso de la linea, no solo el tono.
            trazo = poli(xy, color=C_SAT if ultimo else C_PERDIDO,
                         grosor=3.6 if ultimo else 2.0,
                         opacidad=1.0 if ultimo else 0.50)
            if ultimo:
                camino_orbita = trazo
            if i:
                nuevo = cifra(f"{v_orb * frac:.2f}", font_size=104,
                              color=C_MEDIDO)
                nuevo.move_to(pie.numero.get_center())
                cambiar(self, pie.numero, nuevo, salida=0.22, entrada=0.24)
                pie.remove(pie.numero)
                pie.numero = nuevo
                pie.add(nuevo)
            self.play(Create(trazo), run_time=2.05 if ultimo else 1.05,
                      rate_func=linear)
            trazos.append(trazo)
            if d["impacto"]:
                golpe = Dot(np.append(xy[-1], 0.0), radius=0.13,
                            color=C_PERDIDO)
                self.play(FadeIn(golpe, scale=2.4), run_time=0.22)
                self.play(golpe.animate.scale(0.55).set_opacity(0.60),
                          run_time=0.22)
                marcas_impacto.append(golpe)
                self.wait(0.55)
            else:
                sub_nuevo = hud("da la vuelta", font_size=18, color=C_SAT)
                sub_nuevo.move_to(pie.sub.get_center())
                cambiar(self, pie.sub, sub_nuevo, salida=0.22, entrada=0.26)
                pie.remove(pie.sub)
                pie.sub = sub_nuevo
                pie.add(sub_nuevo)
                anillo.set_stroke(opacity=0.0)
                self.add(anillo)
                self.play(anillo.animate.set_stroke(opacity=0.5),
                          run_time=0.6)
                self.wait(2.00)

        # --- el respiro: se apagan los fallidos ---------------------
        self.play(*[FadeOut(m) for m in marcas_impacto],
                  *[FadeOut(t) for t in trazos[:-1]], run_time=0.6)
        self.wait(1.20)

        # --- la cuenta: cae tanto como se aleja el suelo -------------
        et_vieja = [pie.etiqueta, pie.numero, pie.sub]
        alto_barra = 2.30
        # Los dos rotulos van SEPARADOS de verdad: a 0.80 de distancia
        # "CAE" y "SUELO" se leian como una sola frase, "CAE SUELO".
        x_cae, x_suelo = -1.35, 1.35
        y_base = -0.35
        rot_cae = hud("cae", font_size=18, color=C_SAT)
        rot_suelo = hud("suelo", font_size=18, color=C_TIERRA)
        rot_cae.move_to([x_cae, y_base + alto_barra + 0.42, 0])
        rot_suelo.move_to([x_suelo, y_base + alto_barra + 0.42, 0])
        barra_cae = Rectangle(width=0.70, height=alto_barra, stroke_width=0,
                              fill_color=C_SAT, fill_opacity=0.85)
        barra_suelo = Rectangle(width=0.70, height=alto_barra, stroke_width=0,
                                fill_color=C_TIERRA, fill_opacity=0.85)
        barra_cae.move_to([x_cae, y_base + alto_barra / 2, 0])
        barra_suelo.move_to([x_suelo, y_base + alto_barra / 2, 0])

        pie_final = medida(f"{cuenta['caida_m']:.3f}", "metros en 1 s",
                           "las dos cosas", color=C_MEDIDO,
                           color_sub=C_TIERRA)

        self.play(FadeOut(tierra), FadeOut(torre), FadeOut(canon),
                  FadeOut(camino_orbita), FadeOut(anillo),
                  *[FadeOut(m) for m in et_vieja], run_time=0.8)
        self.play(FadeIn(rot_cae), FadeIn(rot_suelo), run_time=0.45)
        # Crecen desde el suelo comun: se escala en y y se ancla la base.
        for barra in (barra_cae, barra_suelo):
            barra.save_state()
            barra.stretch_to_fit_height(0.02)
            barra.move_to([barra.get_center()[0], y_base + 0.01, 0])
        self.add(barra_cae, barra_suelo)
        self.play(Restore(barra_cae), Restore(barra_suelo), run_time=1.6,
                  rate_func=rate_functions.ease_out_cubic)
        igual = Text("=", font=FUENTE_HUD, font_size=52, color=C_MEDIDO)
        igual.move_to([0.0, y_base + alto_barra / 2, 0])
        self.play(FadeIn(igual, scale=1.5), run_time=0.5)
        self.play(FadeIn(pie_final.etiqueta), FadeIn(pie_final.sub),
                  FadeIn(pie_final.numero, scale=1.06), run_time=0.6)
        self.wait(2.40)

        # --- y por eso se queda: la orbita con su satelite ----------
        self.play(FadeOut(barra_cae), FadeOut(barra_suelo), FadeOut(igual),
                  FadeOut(rot_cae), FadeOut(rot_suelo),
                  FadeOut(pie_final.etiqueta), FadeOut(pie_final.numero),
                  FadeOut(pie_final.sub), run_time=0.7)
        sat = Dot(radius=0.10, color=C_SAT)
        sat.move_to(camino_orbita.get_start())
        pie_cierre = medida(f"{v_orb:.3f}", "km por segundo", "a 400 km",
                            color=C_MEDIDO, color_sub=C_EXTERNO)
        self.play(FadeIn(tierra), FadeIn(anillo), run_time=0.7)
        self.play(FadeIn(sat, scale=1.8),
                  FadeIn(pie_cierre.etiqueta), FadeIn(pie_cierre.sub),
                  FadeIn(pie_cierre.numero, scale=1.06), run_time=0.6)
        self.play(MoveAlongPath(sat, camino_orbita), run_time=3.40,
                  rate_func=linear)
        self.wait(1.10)

        # --- fundido a fondo limpio ---------------------------------
        fundido_final(self, run_time=0.9, cola=0.5)
