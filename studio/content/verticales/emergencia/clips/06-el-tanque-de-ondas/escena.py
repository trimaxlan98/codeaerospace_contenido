class Clip(Scene):
    """06 · El tanque de ondas — FDTD 2D, una pared, dos rendijas, franjas.

    El fotograma entero es la ecuacion de onda 2D por diferencias finitas
    (`ondas.simular`): una fuente puntual emite frentes circulares y, a los
    210 de 750 frames, aparece una pared con dos rendijas -marcadas un
    instante con dos circulos ambar-; del otro lado nacen las franjas de
    interferencia. La camara hace zoom 1.6 justo cuando nace el patron (con
    ritmo lento en ese instante) y se abre otra vez para el cierre, donde
    se traza en cian la curva de intensidad medida sobre la linea de
    deteccion y se releva la cifra medida a la prediccion de Fresnel.
    """

    def construct(self):
        # --- lo que se mide (antes de dibujar nada) -------------------
        r = em.ondas.simular(semilla=1)
        F, cifras, extra = r["frames"], r["cifras"], r["extra"]
        T, H, W = F.shape[0], F.shape[1], F.shape[2]
        frame_pared = int(extra["frame_pared"])
        k_medir = int(extra["frame_medicion"])
        rendijas = extra["rendijas_px"]
        y_linea = float(extra["linea_medicion_y_px"])
        perfil = np.asarray(extra["perfil_intensidad"], dtype=np.float64)
        f_escala = len(perfil) / W
        sep_medida = cifras["franjas_medido_px"]
        sep_fresnel = cifras["franjas_fresnel_px"]

        peli = pelicula(F)
        peli.mostrar(95)
        self.add(peli.mob)

        def tramo(run_time, desde, hasta, *otras, ritmo=None, encuadre=None):
            self.play(peli.animacion(run_time, desde=desde, hasta=hasta,
                                     ritmo=ritmo, encuadre=encuadre),
                      *otras, run_time=run_time)

        marca = hud_pieza("06 . tanque")
        regs = reglas(["CADA PUNTO EMPUJA", "AL VECINO", "DOS RENDIJAS"])

        # --- 1. el frente ya se mueve; entra el HUD --------------------
        self.play(FadeIn(marca, shift=DOWN * 0.16),
                  peli.animacion(0.6, desde=95, hasta=140), run_time=0.6)

        # --- 2. las reglas se encienden mientras el frente avanza -----
        cortes = [(140, 165), (165, 190), (190, frame_pared)]
        for et, (a, b) in zip(regs, cortes):
            tramo(0.85, a, b, FadeIn(et, shift=RIGHT * 0.15))

        # --- 3. la pared aparece; se marcan las dos rendijas en ambar -
        radio = 8.0 * peli.mob.height / H
        centros = px_a_escena(rendijas, peli.mob, W, H)
        circ1 = Circle(radius=radio, color=C_REGLA, stroke_width=3,
                       fill_opacity=0.0).move_to(centros[0])
        circ2 = Circle(radius=radio, color=C_REGLA, stroke_width=3,
                       fill_opacity=0.0).move_to(centros[1])
        circ1.set_z_index(20)
        circ2.set_z_index(20)
        tramo(1.0, frame_pared, frame_pared + 12,
              FadeIn(circ1, scale=1.3), FadeIn(circ2, scale=1.3))
        self.play(FadeOut(circ1), FadeOut(circ2), run_time=0.3)

        # --- 4. nace el patron: zoom 1.6, camara lenta en ese instante -
        lento = em.ritmo_por_tramos([(0, 0), (0.55, 0.18), (1, 1)])
        acercar = em.zoom_hacia(0.5, 0.40, 1.6, desde=1.0)
        tramo(7.0, frame_pared + 12, 350, ritmo=lento, encuadre=acercar)

        # --- 5. las franjas viajan hasta la linea de deteccion --------
        sostenido = em.zoom_hacia(0.5, 0.40, 1.6, desde=1.6)
        tramo(8.0, 350, k_medir, encuadre=sostenido)

        # --- 6. la linea se enciende; la camara vuelve a abrirse ------
        pie = medida(f"{sep_medida:.1f}", "entre franjas", "pixeles")
        etiqueta, numero, sub = pie.etiqueta, pie.numero, pie.sub
        pie.remove(etiqueta, numero, sub)
        abrir = em.zoom_hacia(0.5, 0.40, 1.0, desde=1.6)
        tramo(6.0, k_medir, T - 1,
              FadeIn(etiqueta, shift=UP * 0.12),
              FadeIn(numero, shift=UP * 0.12),
              FadeIn(sub, shift=UP * 0.12), encuadre=abrir)
        self.wait(0.6)

        # --- 7. la curva de intensidad medida, vectorial, en cian -----
        # La linea de deteccion real vive a 8 % del alto del tanque: pegada
        # al HUD de la pieza. Trazar el perfil ahi encima lo hacia chocar
        # con "CADA PUNTO EMPUJA" (visto en el primer render). Se traza en
        # la franja central, libre de texto, pero con el MISMO eje X (cada
        # pico queda alineado con su franja real, solo se reubica el alto)
        # y con el pico hacia ARRIBA = mas intensidad, en vez de hacia
        # abajo como salia al usar directamente la fila de pixeles.
        xs_px = np.arange(len(perfil)) / f_escala
        puntos = px_a_escena(np.column_stack([xs_px, np.zeros_like(xs_px)]),
                             peli.mob, W, H)
        puntos[:, 1] = -0.7 + perfil * 2.4
        curva = poli(puntos, color=C_MEDIDO, grosor=2.2)
        curva.set_z_index(50)
        self.play(Create(curva), run_time=1.0)
        self.wait(1.0)

        # --- 8. relevo a la cifra teorica: Fresnel, en gris -----------
        nuevo_num = cifra(f"{sep_fresnel:.1f}", color=C_EXTERNO)
        nuevo_num.move_to(numero.get_center())
        nuevo_sub = nota_externa("fresnel")
        nuevo_sub.move_to(sub.get_center())
        cambiar(self, [numero, sub], [nuevo_num, nuevo_sub])
        self.wait(1.2)

        cerrar_pieza(self)
