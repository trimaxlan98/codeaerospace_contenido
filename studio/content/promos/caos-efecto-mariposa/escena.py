# =====================================================================
# Promo "El efecto mariposa" — curso 15, Caos: el orden escondido.
#
#   estado 0   ..  el punto de partida, solo
#   0.35-7.95  ..  se traza el atractor de Lorenz. Son DOS trayectorias
#                  dibujandose a la vez, pero durante trece segundos
#                  simulados ocupan el mismo pixel: solo se ve una.
#   ~5.2       ..  se abren. Aparece la segunda linea y los dos puntos
#                  dejan de ser uno; la cifra de abajo se dispara.
#   7.95-9.55  ..  respiro con las dos alas separadas
#   9.55-11.65 ..  el trazo se recoge por donde vino
#   estado 0   ..  el punto de partida otra vez
#
# La cifra es la distancia euclidea REAL entre las dos trayectorias en
# ese paso de la integracion, no una animacion decorativa.
# =====================================================================


class Promo(Scene):
    def setup(self):
        code_brand.aplicar_marca(self, esquinas=True, marca=False, fondo=True)

    def construct(self):
        fmt = FMT

        # Las dos trayectorias: misma integracion, mismo dt, y el gemelo
        # arranca a EPS en x. Todo lo que se ve sale de aqui.
        a, b, d = par_lorenz(eps=EPS, n=PASOS, dt=DT)

        alto = 6.4 if fmt.es_vertical else 5.4
        curva_a = curva_lorenz(a, plano="xz", alto=alto, color=C_A,
                               grosor=2.2, maximo=SUBM)
        # `como=` reutiliza el encuadre de la primera: la separacion que se
        # ve es la fisica, no un artefacto de centrar cada una por su lado.
        curva_b = curva_lorenz(b, plano="xz", alto=alto, color=C_B,
                               grosor=2.2, maximo=SUBM, como=curva_a)

        if fmt.es_vertical:
            centro = fmt.centro_util + UP * 0.35
            pos_lectura = UP * (fmt.suelo + 1.05)
            pos_premisa = UP * (fmt.tope - 0.95)
        else:
            centro = fmt.centro_util + LEFT * 3.4
            pos_lectura = centro + RIGHT * 4.6 + DOWN * 0.5
            pos_premisa = centro + RIGHT * 4.6 + UP * 1.2

        trazo = VGroup(curva_a, curva_b).move_to(centro)

        # Las mismas coordenadas de pantalla que usa el trazo, para que los
        # puntos viajeros caigan EXACTAMENTE sobre su curva.
        def proyectar(pts):
            p2 = (pts[:, [0, 2]] - curva_a.centro_usado) * curva_a.escala_usada
            return np.column_stack([p2, np.zeros(len(p2))]) + centro

        proy_a, proy_b = proyectar(a), proyectar(b)

        self.add(_promo.fondo_seguro(fmt), _promo.marca_promo(fmt))
        if GUIAS:
            self.add(_promo.guias(fmt))

        # --- estado de arranque Y de cierre ---------------------------
        salida = Dot(proy_a[0], radius=0.07, color=C_A)
        salida.set_z_index(6)
        self.add(salida)
        self.wait(0.35)

        # etiqueta_hud separa las letras con espacios: una linea de 30
        # caracteres a fs 17 mide mas que el ancho del lienzo vertical.
        premisa = etiqueta_hud(f"EMPIEZAN A {EPS:.6f}", font_size=16,
                               color=CODE_MUTED)
        premisa.move_to(pos_premisa)
        etiqueta = etiqueta_hud("SEPARACION", font_size=17, color=CODE_MUTED)
        lectura = VGroup(cifra(0.0).move_to(pos_lectura))
        etiqueta.next_to(lectura, DOWN, buff=0.30)

        punto_a = Dot(proy_a[0], radius=0.075, color=C_A).set_z_index(10)
        punto_b = Dot(proy_b[0], radius=0.075, color=C_B).set_z_index(11)

        # Todo lo que cambia frame a frame va DENTRO de la animacion: un
        # updater sobre un mobject ajeno al play se ejecuta pero no se ve.
        vivo = VGroup(punto_a, punto_b, lectura)

        def avanzar(m, alpha):
            k = int(alpha * (PASOS - 1))
            punto_a.move_to(proy_a[k])
            punto_b.move_to(proy_b[k])
            lectura.become(VGroup(cifra(d[k]).move_to(pos_lectura)))

        # --- 1. el trazo, y la separacion que nadie ve venir -----------
        # El marcador de salida se apaga: con los dos viajeros en pantalla,
        # un tercer punto quieto se lee como una trayectoria mas.
        self.play(FadeIn(premisa), FadeIn(etiqueta), FadeOut(salida),
                  run_time=0.5)
        self.add(vivo)
        self.play(Create(curva_a), Create(curva_b),
                  UpdateFromAlphaFunc(vivo, avanzar),
                  run_time=7.6, rate_func=linear)
        self.wait(1.6)

        # --- 2. el trazo se recoge por donde vino ---------------------
        self.play(Uncreate(curva_a), Uncreate(curva_b),
                  FadeOut(vivo, run_time=0.8),
                  FadeOut(premisa, run_time=0.8),
                  FadeOut(etiqueta, run_time=0.8),
                  run_time=2.1)
        self.remove(trazo, vivo)
        # Vuelve el marcador de salida: el ultimo frame tiene que ser el
        # primero, y el primero lo tenia.
        self.play(FadeIn(salida), run_time=0.4)
        self.wait(0.35)
