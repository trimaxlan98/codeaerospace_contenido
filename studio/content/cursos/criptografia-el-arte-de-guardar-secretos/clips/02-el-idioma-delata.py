class Clip2(Scene):
    """2 - El idioma delata. El histograma de frecuencias MEDIDO en el texto
    de muestra: la E manda, luego A, O, S. Debajo, el del texto cifrado con
    Cesar: la misma silueta, corrida. Deslizando el de abajo hasta que encaja,
    el desplazamiento (chi-cuadrado minimo) aparece solo. Cierre: un buen
    cifrado tiene que borrar la huella del idioma. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 02")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("El idioma delata"), zona="arriba",
                    run_time=0.6)

        # Geometria del clip: los dos histogramas apilados y a la MISMA
        # escala (`escala_max` comun), corridos a la derecha para dejar la
        # columna izquierda libre para sus rotulos. El de arriba apoya su
        # linea base en y=+0.58 (barras hasta y=+2.13, letras hasta y=+0.37)
        # y el de abajo en y=-1.82 (barras hasta y=-0.27, letras hasta
        # y=-2.04): entre los dos quedan 0.63 de aire y el pie vive en -3.02.
        X_HIST, ANCHO, ALTO = 0.95, 5.4, 1.55
        TOPE = max(FREC_ES.values())

        hist_es = histograma_frecuencias(FREC_ES, C_CLARO, alto=ALTO,
                                         ancho=ANCHO, escala_max=TOPE)
        hist_es.shift(RIGHT * X_HIST + UP * 0.58)
        hist_cif = histograma_frecuencias(FREC_CIFRADO, C_CIFRADO, alto=ALTO,
                                          ancho=ANCHO, escala_max=TOPE)
        hist_cif.shift(RIGHT * X_HIST + DOWN * 1.82)

        et_es = tag_junto(hist_es, "español (texto de muestra)", LEFT,
                          buff=0.52, font_size=17, color=C_CLARO)
        et_cif = tag_junto(hist_cif, "texto cifrado", LEFT, buff=0.52,
                           font_size=17, color=C_CIFRADO)

        # El orden del top-4 es el MEDIDO en el texto de muestra, no una
        # tabla: si el texto cambiara, cambiaria el pie.
        top4 = sorted(FREC_ES, key=FREC_ES.get, reverse=True)[:4]
        letra_top_cif = max(FREC_CIFRADO, key=FREC_CIFRADO.get)

        # --- momento: la otra grieta de Cesar -------------------------------
        rot.mostrar(pie_curso("Aunque la llave fuera enorme, César deja otra "
                              "grieta."), zona="abajo", run_time=0.45)
        self.play(Create(hist_es.linea_base), run_time=0.6)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN)
                                for b in hist_es.barras], lag_ratio=0.045),
                  LaggedStart(*[FadeIn(e) for e in hist_es.etiquetas],
                              lag_ratio=0.045),
                  run_time=1.8)
        self.play(FadeIn(et_es, shift=0.10 * RIGHT), run_time=0.45)
        self.add(hist_es)      # el grupo entero, ya sin piezas sueltas

        barra_top = hist_es.barra(LETRA_TOP)
        t_top = tag_hud(f"{LETRA_TOP}: {FREC_ES[LETRA_TOP]:.1%}",
                        font_size=16, color=C_CLARO)
        t_top.next_to(barra_top, UP, buff=0.14)
        self.play(barra_top.animate.set_fill(C_CLARO, opacity=1.0)
                  .set_stroke(C_CLARO, width=2.4),
                  FadeIn(t_top, shift=0.10 * UP), run_time=0.6)
        self.wait(2.6)

        # --- momento: la huella del idioma ----------------------------------
        rot.mostrar(pie_curso(f"El español tiene huella: la {top4[0]} manda, "
                              f"luego {', '.join(top4[1:])}."), zona="abajo")
        # El top-4 se lee apagando el resto: subirle el brillo a cuatro
        # barras que ya estaban al 85 % no se distingue en pantalla.
        otras = [ch for ch in ALFABETO if ch not in top4]
        self.play(LaggedStart(*[hist_es.barra(ch).animate
                                .set_fill(opacity=0.16)
                                .set_stroke(opacity=0.25)
                                for ch in otras], lag_ratio=0.02),
                  *[hist_es.barra(ch).animate.set_fill(C_CLARO, opacity=1.0)
                    .set_stroke(C_CLARO, width=2.4) for ch in top4],
                  run_time=1.5)
        self.wait(2.9)

        # --- momento: la misma silueta, corrida ------------------------------
        rot.mostrar(pie_curso("Cifrado con César, la silueta es la "
                              "misma... corrida."), zona="abajo")
        # Vuelve la silueta entera (el top-4 se queda brillante): las dos
        # curvas hay que compararlas completas.
        self.play(*[hist_es.barra(ch).animate.set_fill(C_CLARO, opacity=0.85)
                    .set_stroke(C_CLARO, width=0.8) for ch in otras],
                  run_time=0.55)
        self.play(Create(hist_cif.linea_base), run_time=0.5)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN)
                                for b in hist_cif.barras], lag_ratio=0.045),
                  LaggedStart(*[FadeIn(e) for e in hist_cif.etiquetas],
                              lag_ratio=0.045),
                  run_time=1.7)
        self.play(FadeIn(et_cif, shift=0.10 * RIGHT), run_time=0.45)
        self.add(hist_cif)     # idem: el Transform de abajo va sobre el grupo

        barra_top_cif = hist_cif.barra(letra_top_cif)
        t_top_cif = tag_hud(f"{letra_top_cif}: "
                            f"{FREC_CIFRADO[letra_top_cif]:.1%}",
                            font_size=16, color=C_CIFRADO)
        t_top_cif.next_to(barra_top_cif, UP, buff=0.14)
        self.play(barra_top_cif.animate.set_fill(C_CIFRADO, opacity=1.0)
                  .set_stroke(C_CIFRADO, width=2.4),
                  FadeIn(t_top_cif, shift=0.10 * UP), run_time=0.6)
        self.wait(2.6)

        # --- momento: deslizar hasta que encaje ------------------------------
        rot.mostrar(pie_curso("Deslizamos hasta que encaje: el "
                              "desplazamiento aparece solo."), zona="abajo")
        self.play(FadeOut(t_top_cif), run_time=0.3)
        # `desplazado(k)` corre la silueta k lugares a la DERECHA; para
        # deshacer un Cesar de llave k hay que correrla a la izquierda, de
        # ahi el signo. Cada paso se calcula sobre el histograma ORIGINAL,
        # asi que el desfase acumulado es exacto.
        for k in range(1, K_ESTIMADO + 1):
            self.play(Transform(hist_cif, hist_cif.desplazado(-k)),
                      run_time=0.45)
            self.wait(0.25)
        t_k = tag_hud(f"desplazamiento = {K_ESTIMADO}", font_size=16,
                      color=C_LLAVE)
        t_k.move_to(np.array([5.30, -1.15, 0.0]))
        self.play(FadeIn(t_k, shift=0.10 * UP),
                  Flash(hist_cif.barra(LETRA_TOP), color=C_LLAVE,
                        line_length=0.16, num_lines=12, flash_radius=0.34),
                  run_time=0.8)
        self.wait(2.6)

        # --- cierre: borrar la huella ----------------------------------------
        rot.mostrar(pie_curso("Un buen cifrado tiene que borrar la huella "
                              "del idioma."), zona="abajo")
        self.wait(5.0)
