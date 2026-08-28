class Clip(Scene):
    """11 · Los epiciclos — un contorno cerrado, sumado en circulos.

    El fotograma es `epiciclos.simular`: una unica silueta cerrada (la
    palabra CO.DE, geometria pura) y su DFT. La pelicula ya trae, horneados
    en cada frame, el trazo cian que se reconstruye, los circulos y radios
    ambar de la cadena activa, y el contorno objetivo violeta de fondo —
    por eso esta pieza NO necesita enfasis vectorial encima: la version
    horneada ya es nitida y barata (ver informe).

    Ocho vueltas (`extra["secuencia"]`: 1, 2, 5, 10, 25, 50, 100, 200
    circulos), cada una reconstruye el contorno entero; al terminar una
    vuelta relevamos LA CIFRA (numero de circulos + error RMS de esa
    vuelta) con `become()`, sin fundido: el cambio es instantaneo y por
    tanto nunca se solapan dos valores. En la vuelta de 100 circulos el
    ritmo se abre con `ritmo_por_tramos` justo en el ultimo tramo, cuando
    el trazo cierra sobre si mismo: camara lenta ahi. Cierra con la cifra
    de la pieza: 100 circulos para bajar de 1 pixel de error.
    """

    def construct(self):
        # --- lo que se mide (antes de dibujar nada) ------------------
        r = em.epiciclos.simular(semilla=1)
        F, extra = r["frames"], r["extra"]
        T = len(F)
        secuencia = [int(n) for n in extra["secuencia"]]
        cuota = [int(n) for n in extra["frames_por_vuelta"]]
        err_vuelta = [float(v) for v in extra["error_por_vuelta"]]

        peli = pelicula(F)
        self.add(peli.mob)

        def fmt_err(v):
            return f"{v:.1f}" if v >= 10 else f"{v:.2f}"

        marca = hud_pieza("11 . epiciclos")
        regs = reglas(["circulos sobre", "circulos", "cada uno gira fijo"])

        pie = medida(str(secuencia[0]), "circulos",
                    f"error {fmt_err(err_vuelta[0])} px")

        def num_de(n):
            t = cifra(str(n))
            t.move_to(UP * Y_NUMERO)
            return t

        def sub_de(err):
            t = hud(f"error {fmt_err(err)} px", font_size=18, color=C_REGLA)
            t.move_to(UP * Y_SUB)
            return t

        numeros = [num_de(n) for n in secuencia]
        subs = [sub_de(e) for e in err_vuelta]

        def tramo(run_time, desde, hasta, *otras, ritmo=None):
            def paso(_m, alpha):
                f = ritmo(alpha) if ritmo else alpha
                k = int(round(desde + f * (hasta - desde)))
                peli.mostrar(min(max(k, 0), T - 1))
            self.play(UpdateFromAlphaFunc(peli.mob, paso, run_time=run_time,
                                          rate_func=linear),
                      *otras, run_time=run_time)

        acumulado = [0] + list(np.cumsum(cuota))

        # --- 0. la vuelta de 1 circulo: la pelicula ya se mueve desde el
        # frame 0; el HUD y la primera cifra entran a la vez, y las tres
        # reglas se encienden una a una mientras el trazo sigue ---------
        a0, a1 = acumulado[0], acumulado[1]
        p0 = a0 + (a1 - a0) // 4
        p1 = a0 + 2 * (a1 - a0) // 4
        p2 = a0 + 3 * (a1 - a0) // 4
        tramo(0.55, a0, p0,
              FadeIn(marca, shift=DOWN * 0.16),
              FadeIn(pie.etiqueta), FadeIn(pie.numero), FadeIn(pie.sub))
        tramo(0.55, p0, p1, FadeIn(regs[0], shift=RIGHT * 0.15))
        tramo(0.55, p1, p2, FadeIn(regs[1], shift=RIGHT * 0.15))
        tramo(0.55, p2, a1, FadeIn(regs[2], shift=RIGHT * 0.15))

        # --- 1..7: relevo instantaneo de la cifra en cada vuelta nueva;
        # ritmo normal salvo en la vuelta de 100 (el trazo cierra ahi:
        # camara lenta en el ultimo tramo de esa vuelta) -----------------
        duraciones = [None, 2.1, 2.4, 2.7, 3.3, 3.6, 6.3, 4.2]
        for i in range(1, len(secuencia)):
            pie.numero.become(numeros[i])
            pie.sub.become(subs[i])
            desde, hasta = acumulado[i], acumulado[i + 1]
            if secuencia[i] == 100:
                ritmo = em.ritmo_por_tramos([(0.0, 0.0), (0.55, 0.75),
                                             (1.0, 1.0)])
                tramo(duraciones[i], desde, hasta, ritmo=ritmo)
            else:
                tramo(duraciones[i], desde, hasta)

        self.wait(0.3)

        # --- la cifra de la pieza: 100 circulos para bajar de 1 pixel --
        final = medida("100", "para 1 pixel", "circulos")
        cambiar(self, [pie.numero, pie.etiqueta, pie.sub],
               [final.numero, final.etiqueta, final.sub])
        self.wait(2.2)

        cerrar_pieza(self)
