class Clip4(Scene):
    """4.1.4 - Dos contraejemplos lado a lado: un giro no deja ninguna
    direccion en su recta; una cizalla deja una sola. Cierra la
    leccion. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Los que no los tienen")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el caso de la izquierda, el giro ----------------------
        # Dos planos pequeños lado a lado. plano_leccion() no expone
        # `alcance` y con el de la familia (12 unidades) las dos rejillas se
        # cruzarian en el centro del cuadro: aqui se llama a plano() directo.
        izq = plano(unidad=UNIDAD_MINI, alcance=ALCANCE_MINI)
        izq.move_to(CENTRO_IZQ)
        abanico_i = [vector(izq, c, color=C_VEC, grosor=3.2, punta_len=0.15)
                     for c in ABANICO_MINI]
        mat_i = matriz_columnas(R_GIRO, font_size=26, h_buff=0.7, v_buff=0.55)
        mat_i.move_to(CENTRO_IZQ + UP * 2.45)
        rot.mostrar(pie_curso("No toda matriz tiene direcciones propias. Dos "
                              "casos."), zona="abajo", run_time=0.5)
        self.play(FadeIn(izq), FadeIn(mat_i),
                  *[GrowArrow(v.flecha) for v in abanico_i], run_time=1.2)
        self.wait(3.0)

        # El angulo del giro sale de la propia matriz, no del enunciado.
        giro = angulo_entre((1.0, 0.0), R_GIRO @ np.array([1.0, 0.0]))
        rot.mostrar(pie_curso("Un giro de " + fmt(giro, 0) + " grados: la "
                              "rejilla entera gira."),
                    zona="abajo", run_time=0.5)
        self.play(*izq.anim_matriz(R_GIRO, *abanico_i), run_time=2.0)
        self.wait(2.6)

        # --- momento: el veredicto de la izquierda --------------------------
        # autos() levanta ValueError cuando los autovalores son complejos:
        # el veredicto lo dicta la libreria, no la cabeza del guion.
        try:
            autos(R_GIRO)
            tex_i = r"\text{tiene ejes propios}"
        except ValueError:
            tex_i = r"\text{ningún }\lambda\text{ real}"
        veredicto_i = MathTex(tex_i, font_size=28, color=C_TENUE)
        veredicto_i.move_to(CENTRO_IZQ + DOWN * 2.35)
        rot.mostrar(pie_curso("Ninguna flecha se quedó en su recta. No se "
                              "salva ni una."), zona="abajo", run_time=0.5)
        # Un giro de 90 grados manda la rejilla cuadrada sobre si misma: en
        # un fotograma quieto el final se ve igual que el principio. El
        # carril a trazos (mismo idioma que el clip 1) marca por donde iba
        # una flecha y la deja sin nadie encima. El indice 1 (30 grados)
        # acaba en 120: su carril queda en una zona vacia y se lee de golpe.
        carril_i = DashedVMobject(
            span_recta(izq, ABANICO_MINI[1], color=C_VEC, opacidad=0.65,
                       grosor=2.6, largo=ALCANCE_MINI),
            num_dashes=24)
        fantasma_i = vector(izq, ABANICO_MINI[1], color=C_VEC, grosor=3.2,
                            punta_len=0.15)
        fantasma_i.flecha.set_stroke(opacity=0.45)
        fantasma_i.flecha.set_fill(opacity=0.45)
        self.play(FadeIn(veredicto_i), Create(carril_i), FadeIn(fantasma_i),
                  run_time=0.7)
        self.wait(3.4)

        # --- momento: el caso de la derecha, la cizalla ---------------------
        der = plano(unidad=UNIDAD_MINI, alcance=ALCANCE_MINI)
        der.move_to(CENTRO_DER)
        abanico_d = [vector(der, c, color=C_VEC, grosor=3.2, punta_len=0.15)
                     for c in ABANICO_MINI]
        mat_d = matriz_columnas(S_CIZALLA, font_size=26, h_buff=0.7,
                                v_buff=0.55)
        mat_d.move_to(CENTRO_DER + UP * 2.45)
        rot.mostrar(pie_curso("La cizalla, en cambio, empuja hacia un lado "
                              "sin llegar a girar."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(der), FadeIn(mat_d),
                  *[GrowArrow(v.flecha) for v in abanico_d], run_time=1.3)
        self.wait(2.8)

        rot.mostrar(pie_curso("Casi todas se inclinan: la rejilla se "
                              "desliza."), zona="abajo", run_time=0.5)
        self.play(*der.anim_matriz(S_CIZALLA, *abanico_d), run_time=2.0)
        self.wait(2.6)

        # --- momento: el unico eje que aguanta ------------------------------
        rot.mostrar(pie_curso("Solo la horizontal aguanta: un único eje "
                              "propio, y nada más."), zona="abajo",
                    run_time=0.5)
        recta_d = span_recta(der, DIR_CIZALLA, color=C_PROPIO, opacidad=0.6,
                             largo=ALCANCE_MINI)
        propio_d = vector(der, S_CIZALLA @ abanico_d[0].coords,
                          color=C_PROPIO, grosor=5.0, punta_len=0.18)
        veredicto_d = MathTex(r"\lambda = " + fmt(LAMBDAS_CIZALLA[0], 0)
                              + r"\text{, un solo eje}", font_size=28,
                              color=C_PROPIO)
        veredicto_d.move_to(CENTRO_DER + DOWN * 2.35)
        self.play(Create(recta_d), Transform(abanico_d[0], propio_d),
                  run_time=1.0)
        self.play(FadeIn(veredicto_d), run_time=0.6)
        self.wait(3.0)

        # --- cierre de la leccion -------------------------------------------
        piezas = [izq, der, mat_i, mat_d, veredicto_i, veredicto_d, recta_d,
                  carril_i, fantasma_i, *abanico_i, *abanico_d]
        cierre_leccion(self, rot, "Los ejes propios",
                       "son los que la transformación respeta.",
                       "Con ellos como base, la matriz se vuelve casi "
                       "trivial. Siguiente lección.", *piezas)
