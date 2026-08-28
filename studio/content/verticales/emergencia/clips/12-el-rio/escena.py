class Clip(Scene):
    """12 · El rio — nueve direcciones y la calle de von Karman.

    Todo el fotograma es `em.rio.simular`: lattice-Boltzmann D2Q9 sobre una
    malla de 135x240 celdas, 7790 pasos, con un cilindro cruzado a un cuarto
    de la altura. No se resuelve ninguna ecuacion de fluidos: poblaciones que
    se mueven por nueve direcciones, chocan y se relajan hacia el equilibrio.
    De ahi salen solos los remolinos.

    Arco: el rio ya baja en el primer frame (los 130 frames de arranque
    acelerado, 17 pasos cada uno); un anillo gris marca el cilindro —el unico
    obstaculo—; se encienden las tres reglas; entra Reynolds 180; la camara
    baja el ritmo y hace zoom 1.8 a la estela EN EL PASO donde la sonda mide
    su pico (un vortice cruzandola); vuelve a abrirse; y al final se dibuja la
    serie de la sonda en cian con el Strouhal medido, 0.205, contra el 0.19
    de la literatura para un cilindro libre (en gris: eso no lo mide nadie
    aqui; el canal de este render mide solo 6.75 diametros de ancho).

    DOS decisiones de composicion, las dos medidas en el primer render y no
    a ojo:

    1. **Las reglas van de una en una, en el renglon de arriba.** El cilindro
       cae en el 25 % del alto, o sea en y = 3.53 con un radio de 0.59: su
       borde superior (4.12) se come los renglones segundo y tercero de
       `reglas()` (3.89 y 3.49) y las letras de en medio pierden contraste
       sobre el disco gris. En el primer renglon (Y_REGLAS = 4.29) no lo
       tocan, asi que las tres se relevan ahi y la ultima —"nada mas"— se
       queda hasta el final.
    2. **El zoom se centra en 0.34 del alto, no en la estela.** `recortar`
       lleva un punto p a 0.5 + (p - cy)*z: con cy = 0.42 y z = 1.8 el
       cilindro se iba a 0.196 del alto y aterrizaba encima del HUD y de la
       marca de agua. Con cy = 0.34 cae en 0.34 (y = 2.27) y la ventana
       ensena el cilindro y 4.4 diametros de estela, con la sonda dentro.
    """

    ZOOM = 1.8
    ZX, ZY = 0.5, 0.34          # centro del recorte (ver la nota 2 de arriba)
    Y_TRAZA = -1.26             # el oscilograma de la sonda
    ANCHO_TRAZA = 5.2
    ALTO_TRAZA = 0.70
    Y_NOTA = -2.08              # la cifra de literatura, sobre la etiqueta

    def construct(self):
        # --- lo que se mide (antes de dibujar nada) ------------------
        r = em.rio.simular(semilla=1)
        F, cifras, extra = r["frames"], r["cifras"], r["extra"]
        T = len(F)
        W, H = extra["res"]
        serie = np.asarray(extra["serie_sonda"], dtype=np.float64)
        n_arr = int(extra["frames_arranque"])
        ini = int(extra["paso_inicio_crucero"])
        ppf = int(extra["pasos_por_frame"])

        # El instante clave: el paso en el que la sonda (3 diametros aguas
        # abajo) marca su pico mas cercano al frame 560, o sea un vortice
        # cruzandola. La camara lenta va AHI, no en un frame elegido a ojo.
        objetivo = ini + (560 - n_arr) * ppf
        a, b = max(ini, objetivo - 400), min(serie.size, objetivo + 400)
        p_pico = a + int(np.argmax(serie[a:b]))
        k_pico = int(round(n_arr + (p_pico - ini) / ppf))
        k_pico = min(max(k_pico, 470), 600)
        k0, k1 = k_pico - 62, k_pico - 22
        k2, k3 = k_pico + 23, k_pico + 63

        # --- el fondo ES el rio --------------------------------------
        peli = pelicula(F)
        self.add(peli.mob)

        def tramo(run_time, desde, hasta, *otras, **kw):
            self.play(peli.animacion(run_time, desde=desde, hasta=hasta,
                                     **kw), *otras, run_time=run_time)

        marca = hud_pieza("12 . el rio")
        # las tres al MISMO renglon: se relevan, no se apilan (nota 1)
        regs = reglas(["9 direcciones", "chocan y se relajan", "nada mas"])
        for et in regs:
            et.move_to(UP * Y_REGLAS)

        # --- 1. gancho: el rio ya baja (arranque acelerado) ----------
        self.play(peli.animacion(0.6, desde=0, hasta=24),
                  FadeIn(marca, shift=DOWN * 0.16), run_time=0.6)
        tramo(2.8, 24, 130)

        # --- 2. el unico obstaculo: un anillo gris sobre el cilindro --
        centro = px_a_escena(extra["centro_cilindro_px"], peli.mob, W, H)[0]
        radio = float(extra["radio_px"]) / W * peli.mob.width
        anillo = Circle(radius=radio * 1.35, stroke_color=C_EXTERNO,
                        stroke_width=2.4, fill_opacity=0.0)
        anillo.move_to(centro)
        anillo.set_z_index(700)
        tramo(1.0, 130, 162, Create(anillo))
        tramo(2.6, 162, 240)
        tramo(0.4, 240, 252, FadeOut(anillo))

        # --- 3. las tres reglas, una a una, con el rio corriendo ------
        tramo(0.55, 252, 268, FadeIn(regs[0], shift=RIGHT * 0.15))
        tramo(0.95, 268, 296)
        tramo(0.30, 296, 305, FadeOut(regs[0], scale=0.92))
        tramo(0.36, 305, 316, FadeIn(regs[1], scale=1.06))
        tramo(0.94, 316, 344)
        tramo(0.30, 344, 353, FadeOut(regs[1], scale=0.92))
        tramo(0.36, 353, 364, FadeIn(regs[2], scale=1.06))
        tramo(0.74, 364, 387)

        # --- 4. la primera cifra: Reynolds ---------------------------
        pie_re = medida(f"{cifras['reynolds']:.0f}", "reynolds",
                        "unidades de red", color_sub=C_EXTERNO)
        tramo(1.2, 387, 423, FadeIn(pie_re))
        tramo(2.8, 423, k0)

        # --- 5. camara lenta y zoom 1.8 al vortice que cruza la sonda -
        def acercar(frac, _W, _H):
            return self.ZX, self.ZY, 1.0 + (self.ZOOM - 1.0) * frac

        def pegado(frac, _W, _H):
            return self.ZX, self.ZY, self.ZOOM

        def alejar(frac, _W, _H):
            return self.ZX, self.ZY, self.ZOOM + (1.0 - self.ZOOM) * frac

        tramo(2.0, k0, k1, encuadre=acercar)      # 40 frames en 2 s
        tramo(4.5, k1, k2, encuadre=pegado)       # 45 frames en 4.5 s: 3x
        tramo(2.0, k2, k3, encuadre=alejar)

        # --- 6. otra vez el rio entero -------------------------------
        tramo(4.0, k3, 690)

        # --- 7. la sonda y su serie ----------------------------------
        punto = Dot(px_a_escena(extra["sonda_px"], peli.mob, W, H)[0],
                    radius=0.075, color=C_MEDIDO)
        punto.set_z_index(780)

        paso_sub = max(1, serie.size // 520)
        s = serie[::paso_sub] - serie.mean()
        s = s / max(float(np.abs(s).max()), 1e-12)
        xs = np.linspace(-self.ANCHO_TRAZA / 2, self.ANCHO_TRAZA / 2, s.size)
        traza = poli(np.column_stack([xs, self.Y_TRAZA
                                      + s * (self.ALTO_TRAZA / 2)]),
                     color=C_MEDIDO, grosor=2.4)
        traza.set_z_index(780)
        base = Line([-self.ANCHO_TRAZA / 2, self.Y_TRAZA, 0],
                    [self.ANCHO_TRAZA / 2, self.Y_TRAZA, 0],
                    stroke_color=C_EXTERNO, stroke_width=1.2,
                    stroke_opacity=0.45)
        base.set_z_index(770)

        pie_st = medida(f"{cifras['strouhal_medido']:.3f}", "strouhal",
                        f"{cifras['vortices_desprendidos']} vortices")
        nota = nota_externa("cilindro libre 0.19")
        nota.move_to(UP * self.Y_NOTA)
        nota.set_z_index(800)

        # relevo limpio: lo viejo se va ANTES de que entre lo nuevo. Solo
        # regs[2] sigue en escena (las otras dos ya se relevaron): pasar el
        # VGroup entero volveria a meter las tres.
        tramo(0.34, 690, 694, FadeOut(regs[2], scale=0.92),
              FadeOut(pie_re, scale=0.92))
        tramo(0.46, 694, 700, FadeIn(punto, scale=1.5))
        tramo(2.6, 700, 716, FadeIn(base), Create(traza))
        tramo(1.0, 716, 722, FadeIn(pie_st))
        tramo(1.6, 722, 730)
        tramo(0.9, 730, 735, FadeIn(nota))
        tramo(2.4, 735, T - 1)
        self.wait(0.7)

        cerrar_pieza(self)
