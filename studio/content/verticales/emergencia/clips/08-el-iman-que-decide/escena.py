class Clip(Scene):
    """08 · El iman que decide — Ising 2D enfriado a traves de Tc.

    El fotograma entero es la malla: 32 400 espines que solo saben del
    vecino de al lado (`em.ising.simular`). Arranca en ruido caliente a
    T = 3.50, se enfria despacio, y en Tc = 2.269 la pelicula se va a
    camara lenta con un zoom 1.8 sobre el sitio donde se ve lo unico que
    pasa una sola vez: manchas de TODOS los tamaños. Abajo de Tc, uno de
    los dos signos se come la malla.

    Dos cifras, una detras de otra y nunca a la vez: primero la
    temperatura del temple (cian, medida en este render) contra el Tc de
    Onsager (gris, literatura); despues de Tc, la magnetizacion |M| con
    su curva |M|(T) dibujandose arriba mientras sube. Remate: |M| = 0.997
    medido contra el 0.9970 exacto de Onsager a T = 1.2.

    PARAMETROS, Y POR QUE NO SON LOS DE DEFECTO (ver el informe):
    `periodica=True`. La tabla de aceptacion de la libreria se indexa con
    `(s*nb + 4) >> 1`, que solo es exacta cuando `s*nb` es PAR — es decir,
    cuando la celda tiene 4 vecinas. Con la frontera abierta (el defecto)
    las celdas del borde tienen 3 y el desplazamiento redondea hacia
    abajo: en todo el perimetro se aceptan con probabilidad 1 volteos que
    SUBEN la energia en 2J (deberian ir a exp(-2/T) = 0.20 a T = 1.25).
    El borde queda anormalmente caliente, nuclea dominios que se comen el
    interior y |M| pega saltos no fisicos abajo de Tc (0.93 -> 0.13 ->
    0.95 -> 0.05 -> 0.97 en el ultimo tercio). En el toro TODAS las
    celdas tienen 4 vecinas, el desplazamiento es exacto y el modelo sale
    bien: |M| = 0.9973 medido contra 0.997026 de Onsager. `barridos_max`
    baja de 260 a 110 porque el toro cuesta ~3x por barrido (np.roll) y
    26 811 barridos caben en los 90 s de presupuesto (63 s medidos).
    """

    ZOOM = 1.8                     # acercamiento en el instante critico
    CX, CY = 0.38, 0.45            # donde mirar (fraccion del frame)
    F_RELEVO = 470                 # frame en que la cifra pasa a |M|
    # el hueco de la curva |M|(T), arriba y sobre la pelicula
    XC0, XC1 = -2.15, 2.15
    YC0, YC1 = 1.52, 2.72
    # Onsager exacto: M(T) = (1 - sinh(2/T)^-4)^(1/8) en T = 1.20 (GRIS:
    # es literatura, no lo mide la libreria)
    M_ONSAGER = "0.9970"

    def construct(self):
        # --- lo que se mide (antes de dibujar nada) ------------------
        r = em.ising.simular(semilla=1, pasos=800, periodica=True,
                             barridos_max=110)
        F, cifras, extra = r["frames"], r["cifras"], r["extra"]
        n = len(F)
        Ts = np.asarray(extra["temperatura"], dtype=np.float64)
        Ms = np.asarray(extra["M_abs"], dtype=np.float64)
        f_tc = int(extra["frame_en_Tc"])
        if not 300 <= f_tc <= 520:
            f_tc = 416

        peli = pelicula(F, nearest=True)
        self.add(peli.mob)

        marca = hud_pieza("08 . el iman")
        regs = reglas(["cada espin mira", "a sus 4 vecinos",
                       "y copia si puede"])

        # --- los dos pies de cifra (nunca los dos a la vez) ----------
        pie_t = medida(f"{Ts[0]:.2f}", "temperatura",
                       f"tc {cifras['Tc_literatura']:.3f} onsager",
                       color_sub=C_EXTERNO)
        pie_m = medida(f"{Ms[self.F_RELEVO]:.3f}", "magnetizacion",
                       f"{cifras['celdas']} celdas")
        cont_t = VGroup(pie_t.numero)
        pie_t.remove(pie_t.numero)
        cont_m = VGroup(pie_m.numero)
        pie_m.remove(pie_m.numero)
        cont_t.set_z_index(800)
        cont_m.set_z_index(800)

        # Contadores pre-renderizados: un Text por valor, cacheado, que se
        # cambia con become DENTRO del UpdateFromAlphaFunc.
        cache = {}

        def num(valor, dec):
            clave = (dec, round(float(valor), dec))
            if clave not in cache:
                t = cifra(f"{clave[1]:.{dec}f}")
                t.move_to(UP * Y_NUMERO)
                cache[clave] = t
            return cache[clave]

        # --- la curva |M|(T), vectorial y pequeña, arriba ------------
        xs = self.XC0 + (self.XC1 - self.XC0) * np.arange(n) / (n - 1)
        ys = self.YC0 + (self.YC1 - self.YC0) * np.clip(Ms, 0.0, 1.0)
        pts = np.column_stack([xs, ys])

        def traza(k):
            k = int(min(max(k, 2), n - 1))
            v = poli(pts[:k + 1:2], color=C_MEDIDO, grosor=2.4)
            v.set_z_index(880)
            return v

        panel = Rectangle(width=(self.XC1 - self.XC0) + 0.34,
                          height=(self.YC1 - self.YC0) + 0.32,
                          stroke_color=C_EJE, stroke_width=1.6,
                          fill_color=CODE_BG, fill_opacity=0.55)
        panel.set_stroke(opacity=0.60)
        panel.move_to(np.array([0.0, (self.YC0 + self.YC1) / 2, 0.0]))
        eje = Line([self.XC0, self.YC0, 0], [self.XC1, self.YC0, 0],
                   stroke_width=1.4, stroke_color=C_EJE)
        x_tc = self.XC0 + (self.XC1 - self.XC0) * f_tc / (n - 1)
        linea_tc = DashedLine([x_tc, self.YC0, 0], [x_tc, self.YC1, 0],
                              stroke_width=1.6, stroke_color=C_EXTERNO,
                              dash_length=0.07)
        linea_tc.set_stroke(opacity=0.70)
        grafica = VGroup(panel, eje, linea_tc)
        grafica.set_z_index(860)
        curva = VGroup(traza(self.F_RELEVO))
        curva.set_z_index(880)

        # --- un tramo de pelicula con sus contadores vivos -----------
        def anim_num(run_time, desde, hasta, grupo, serie, dec, ritmo):
            def paso(_m, alpha):
                fr = ritmo(alpha) if ritmo else alpha
                k = int(round(desde + fr * (hasta - desde)))
                grupo[0].become(num(serie[min(max(k, 0), n - 1)], dec))
            return UpdateFromAlphaFunc(grupo, paso, run_time=run_time,
                                       rate_func=linear)

        def anim_curva(run_time, desde, hasta, ritmo):
            def paso(_m, alpha):
                fr = ritmo(alpha) if ritmo else alpha
                k = int(round(desde + fr * (hasta - desde)))
                curva[0].become(traza(k))
                curva[0].set_z_index(880)
            return UpdateFromAlphaFunc(curva, paso, run_time=run_time,
                                       rate_func=linear)

        def tramo(run_time, desde, hasta, *otras, ritmo=None, encuadre=None,
                  contador=None, serie=None, dec=2, con_curva=False):
            anims = [peli.animacion(run_time, desde=desde, hasta=hasta,
                                    ritmo=ritmo, encuadre=encuadre)]
            if contador is not None:
                anims.append(anim_num(run_time, desde, hasta, contador,
                                      serie, dec, ritmo))
            if con_curva:
                anims.append(anim_curva(run_time, desde, hasta, ritmo))
            self.play(*anims, *otras, run_time=run_time)

        # --- 1. el ruido caliente ya se mueve; entra el HUD ----------
        self.play(peli.animacion(0.7, desde=0, hasta=18),
                  FadeIn(marca, shift=DOWN * 0.16),
                  FadeIn(pie_t.etiqueta), FadeIn(pie_t.sub),
                  FadeIn(cont_t), run_time=0.7)
        tramo(1.6, 18, 65, contador=cont_t, serie=Ts)

        # --- 2. las tres reglas, una a una, sobre el ruido -----------
        for i, et in enumerate(regs):
            a, b = 65 + i * 45, 110 + i * 45
            tramo(1.5, a, b, FadeIn(et, shift=RIGHT * 0.15),
                  contador=cont_t, serie=Ts)

        # --- 3. el grano engorda: T baja de 2.75 a 2.45 --------------
        tramo(3.6, 200, 320, contador=cont_t, serie=Ts)

        # --- 4. Tc: camara lenta en 400-440 y zoom 1.8 --------------
        # El ritmo reparte 9.5 s entre 150 frames: 2.85 s para los 80 de
        # 320->400 (tiempo real), 4.75 s para los 40 de 400->440 (0.28x:
        # AQUI nacen las manchas de todos los tamaños) y 1.9 s para
        # volver. El zoom entra y sale dentro de la parte lenta.
        ritmo = em.ritmo_por_tramos([(0.0, 0.0), (0.30, 0.5333),
                                     (0.80, 0.80), (1.0, 1.0)])

        def camara(frac, W_, H_):
            k = 320 + frac * 150.0
            if k <= 396:
                z = 1.0
            elif k <= 424:
                z = 1.0 + (self.ZOOM - 1.0) * (k - 396) / 28.0
            elif k <= 444:
                z = self.ZOOM
            else:
                z = self.ZOOM - (self.ZOOM - 1.0) * min((k - 444) / 26.0, 1.0)
            return self.CX, self.CY, z

        tramo(9.5, 320, self.F_RELEVO, ritmo=ritmo, encuadre=camara,
              contador=cont_t, serie=Ts)

        # --- 5. relevo: la temperatura deja paso a la magnetizacion --
        cambiar(self, [cont_t, pie_t.etiqueta, pie_t.sub],
                [pie_m.etiqueta, pie_m.sub, cont_m, grafica, curva])

        # --- 6. abajo de Tc uno gana, y la curva lo dibuja -----------
        tramo(5.2, self.F_RELEVO, 620, contador=cont_m, serie=Ms, dec=3,
              con_curva=True)
        tramo(5.6, 620, n - 1, contador=cont_m, serie=Ms, dec=3,
              con_curva=True)

        # --- 7. y lo medido cuadra con Onsager ----------------------
        sub_ons = nota_externa(f"onsager {self.M_ONSAGER}")
        sub_ons.move_to(UP * Y_SUB)
        sub_ons.set_z_index(800)
        cambiar(self, pie_m.sub, sub_ons)
        self.wait(1.6)

        cerrar_pieza(self)
