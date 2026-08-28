class Clip(Scene):
    """10 · Las cuencas — un pendulo por pixel y una frontera sin grosor.

    El fotograma entero es `cuencas.simular` a 360x640: 230400 pendulos
    magneticos integrados a la vez, uno por pixel, sobre tres imanes en
    triangulo. El color de cada pixel dice a que iman se acerca mas EN ESE
    INSTANTE y el brillo baja con la velocidad, asi que el mapa se ve
    nacer en tres actos: a t=0 un Voronoi limpio de tres sectores; luego
    se revuelve (anillos de interferencia, el mapa casi negro hirviendo);
    y al final cuaja a color pleno con la frontera fractal ya dibujada.

    Encima, poco y vectorial: los tres imanes marcados en su color
    (`extra["imanes_px"]`), la trayectoria de UN pendulo soltado en un
    punto triple de la frontera (`extra["trayectoria"]`, dibujada con
    Create en el color del iman al que acaba cayendo) y el contador de
    cuantos pendulos "ya decidieron" (`extra["convergidos"]`).

    Camara y ritmo: camara lenta en el frame de la mitad convergida
    (`frame_mitad_convergida` = 477, el ultimo cuarto) y zoom continuo
    hasta 3.0 sobre `extra["zoom_frontera"]` en el ultimo tercio, que es
    el mismo punto del que salio el pendulo dibujado. Remate: el reparto
    34/33/33 % y la dimension de la frontera, 1.63.
    """

    ZOOM = 3.0

    def construct(self):
        # --- lo que se mide (antes de dibujar nada) ------------------
        r = em.cuencas.simular(res=(360, 640), pasos=600, semilla=1)
        F, cifras, extra = r["frames"], r["cifras"], r["extra"]
        T, H, W = F.shape[:3]
        conv = np.asarray(extra["convergidos"], dtype=np.float64)
        colores = [str(c) for c in extra["colores"]]
        imanes = np.asarray(extra["imanes_px"], dtype=np.float64)
        traza_px = np.asarray(extra["trayectoria"], dtype=np.float64)
        i_traza = int(extra["trayectoria_iman"])
        zx, zy = (float(v) for v in extra["zoom_frontera"])
        f_mitad = int(cifras["frame_mitad_convergida"])
        if not 400 <= f_mitad <= 560:      # red de seguridad del tramo lento
            f_mitad = 477

        peli = pelicula(F, nearest=True)   # pixel duro: la frontera es pixel
        self.add(peli.mob)

        marca = hud_pieza("10 . las cuencas")
        regs = reglas(["1 . tres imanes", "2 . un pendulo",
                       "3 . por cada pixel"])

        # --- enfasis vectorial: los imanes y UN pendulo --------------
        pts = px_a_escena(imanes, peli.mob, W, H)
        imanes_mob = VGroup()
        for p, c in zip(pts, colores):
            imanes_mob.add(VGroup(
                Dot(p, radius=0.085, color=c),
                Circle(radius=0.26, stroke_color=c, stroke_width=2.4,
                       stroke_opacity=0.9).move_to(p)))
        imanes_mob.set_z_index(700)

        traza = poli(px_a_escena(traza_px, peli.mob, W, H),
                     color=colores[i_traza], grosor=2.4)
        traza.set_z_index(720)

        # --- el contador: un Text por entero, cambiado con become ----
        pie = medida("0 %", "ya decidieron",
                     f"{cifras['pendulos']} pendulos")
        pie.remove(pie.numero)
        contador = VGroup(pie.numero)
        contador.set_z_index(800)
        cache = {}

        def texto_conv(k):
            # TRUNCA, no redondea: al final quedan 60 pendulos de 230400 sin
            # converger (`pixeles_sin_converger`), o sea 99.96 %. Redondear
            # escribiria "100 %" con 60 sin decidir todavia — un rotulo
            # falso que el render deja pasar tan campante.
            v = int(float(conv[min(max(k, 0), T - 1)]) * 100)
            if v not in cache:
                t = cifra(f"{v} %")
                t.move_to(UP * Y_NUMERO)
                t.set_z_index(800)
                cache[v] = t
            return cache[v]

        vivo = {"contador": False}

        def tramo(run_time, desde, hasta, *otras, ritmo=None, encuadre=None):
            """Un tramo de pelicula con el contador vivo (si toca) y, a la
            vez, las animaciones vectoriales que se le pasen."""
            anims = [peli.animacion(run_time, desde=desde, hasta=hasta,
                                    ritmo=ritmo, encuadre=encuadre)]
            if vivo["contador"]:
                def cuenta(_m, alpha):
                    f = ritmo(alpha) if ritmo else alpha
                    k = int(round(desde + f * (hasta - desde)))
                    contador[0].become(texto_conv(k))
                anims.append(UpdateFromAlphaFunc(contador, cuenta,
                                                 run_time=run_time,
                                                 rate_func=linear))
            self.play(*anims, *otras, run_time=run_time)

        # --- 1. el Voronoi limpio se revuelve; las tres reglas -------
        tramo(0.8, 0, 28, FadeIn(marca, shift=DOWN * 0.16))
        for i, et in enumerate(regs):
            tramo(1.0, 28 + i * 42, 70 + i * 42,
                  FadeIn(et, shift=RIGHT * 0.15))
        self.wait(0.5)

        # --- 2. tres imanes y UN pendulo -----------------------------
        # Las reglas se apagan ANTES de encender los imanes: el iman de
        # arriba cae en y = 3.47 y el tercer renglon de reglas en 3.49.
        cambiar(self, regs, None, salida=0.30)
        tramo(1.2, 154, 200, FadeIn(imanes_mob, scale=1.5))
        tramo(3.0, 200, 290, Create(traza))
        self.wait(0.4)

        # --- 3. por cada pixel: el contador de los que ya decidieron -
        tramo(1.0, 290, 320, FadeOut(traza), FadeIn(pie.etiqueta),
              FadeIn(pie.sub))
        contador[0].become(texto_conv(320))
        tramo(0.5, 320, 336, FadeIn(contador))
        vivo["contador"] = True
        tramo(3.6, 336, 425)
        tramo(3.0, 425, f_mitad - 12)

        # camara lenta justo sobre la mitad convergida (frame 477)
        lento = em.ritmo_por_tramos([(0.0, 0.0), (0.30, 0.35),
                                     (0.70, 0.50), (1.0, 1.0)])
        tramo(4.0, f_mitad - 12, f_mitad + 18, ritmo=lento)

        tramo(1.0, f_mitad + 18, f_mitad + 35, FadeOut(imanes_mob))
        tramo(2.6, f_mitad + 35, 545)

        # --- 4. zoom a la frontera fractal (ultimo tercio) -----------
        tramo(6.0, 545, T - 1,
              encuadre=em.zoom_hacia(zx, zy, self.ZOOM))
        self.wait(0.6)
        vivo["contador"] = False

        # RODEO a un defecto de manim 0.20.1 (no de la libreria del curso,
        # pero solo salta si una Pelicula termina RECORTADA):
        # `ImageMobject.set_opacity` — lo que usa FadeOut — hace
        #     pixel_array[:, :, 3] = orig_alpha_pixel_array * alpha
        # y `orig_alpha_pixel_array` se capturo al construir, con el TAMAÑO
        # COMPLETO. Tras un `zoom_hacia`, `recortar` deja un pixel_array mas
        # chico y el FadeOut de `cerrar_pieza` revienta con
        #     could not broadcast input array from shape (640,360)
        #     into shape (213,120)
        # y el render se cuelga con la traza, sin escribir el mp4. El molde
        # (clip 01) no lo ve porque su ultima camara vuelve a zoom 1.0. Se
        # vuelve a capturar el alfa con la forma del recorte final: una
        # linea, sin tocar la libreria.
        peli.mob.orig_alpha_pixel_array = peli.mob.pixel_array[:, :, 3].copy()

        # --- 5. el reparto y la dimension ----------------------------
        reparto = medida(
            "{}/{}/{}".format(round(cifras["fraccion_iman_violeta"] * 100),
                              round(cifras["fraccion_iman_ambar"] * 100),
                              round(cifras["fraccion_iman_verde"] * 100)),
            "reparto en %", "violeta ambar verde",
            font_size=84, color_sub=C_TINTA)
        cambiar(self, [pie.etiqueta, pie.sub, contador], reparto)
        self.wait(1.6)

        dim = medida(f"{cifras['dimension_frontera']:.2f}", "dimension",
                     "de la frontera")
        cambiar(self, reparto, dim)
        self.wait(2.0)

        cerrar_pieza(self)
