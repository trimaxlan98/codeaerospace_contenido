class Clip5(Scene):
    """5 - XOR: el muro. Tres rectas intentan separar los cuatro racimos
    alternos de XOR y fallan siempre: los puntos mal clasificados pulsan
    en rojo y un contador HUD lleva la cuenta de errores. Cierre que
    siembra la necesidad de apilar neuronas (clip 6)."""

    def _mal_clasificados(self, X, y, m, b):
        """Indices de los puntos que la recta y = m*x + b deja del lado
        equivocado: compara el signo respecto a la recta contra la clase
        real de cada punto."""
        lado_recta = np.sign(X[:, 1] - (m * X[:, 0] + b))
        lado_clase = np.where(y > 0.5, 1.0, -1.0)
        return np.where(lado_recta != lado_clase)[0]

    def _releva_errores(self, anterior, n):
        """HUD 'ERRORES: N' en la esquina UR. Releva al contador previo:
        primero sale el viejo, luego entra el nuevo (nunca coexisten)."""
        nuevo = etiqueta_hud(f"ERRORES: {n}")
        nuevo.to_corner(UR, buff=0.5)
        if anterior is None:
            self.play(FadeIn(nuevo, shift=0.12 * LEFT), run_time=0.4)
        else:
            self.play(FadeOut(anterior, shift=0.12 * RIGHT), run_time=0.3)
            self.play(FadeIn(nuevo, shift=0.12 * LEFT), run_time=0.4)
        return nuevo

    def construct(self):
        rot = Rotulos(self)

        # --- HUD de modulo y titulo -------------------------------------
        modulo = hud_modulo("Modulo 05")
        titulo = titulo_curso("XOR: el problema imposible")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(1.1)

        # --- El plano con los cuatro racimos alternos --------------------
        ejes = ejes_plano()
        self.play(Create(ejes), run_time=1.0)

        X, y = datos_xor()
        puntos = puntos_datos(ejes, X, y)
        self.play(FadeIn(puntos, lag_ratio=0.05), run_time=1.5)
        self.wait(2.0)

        # --- Intento 1: recta horizontal ---------------------------------
        m1, b1 = 0.0, 0.0
        recta = recta_modelo(ejes, m1, b1)
        self.play(Create(recta), run_time=0.9)
        self.wait(0.4)
        mal = self._mal_clasificados(X, y, m1, b1)
        self.play(AnimationGroup(*[
            Indicate(puntos[i], color=C_PERDIDA, scale_factor=1.4)
            for i in mal]), run_time=0.9)
        contador = self._releva_errores(None, len(mal))
        self.wait(2.0)

        # --- Intento 2: diagonal ascendente -------------------------------
        m2, b2 = 1.4, 0.0
        self.play(Transform(recta, recta_modelo(ejes, m2, b2)), run_time=0.9)
        self.wait(0.4)
        mal = self._mal_clasificados(X, y, m2, b2)
        self.play(AnimationGroup(*[
            Indicate(puntos[i], color=C_PERDIDA, scale_factor=1.4)
            for i in mal]), run_time=0.9)
        contador = self._releva_errores(contador, len(mal))
        self.wait(2.0)

        # --- Intento 3: diagonal descendente ------------------------------
        m3, b3 = -1.4, 0.2
        self.play(Transform(recta, recta_modelo(ejes, m3, b3)), run_time=0.9)
        self.wait(0.4)
        mal = self._mal_clasificados(X, y, m3, b3)
        self.play(AnimationGroup(*[
            Indicate(puntos[i], color=C_PERDIDA, scale_factor=1.4)
            for i in mal]), run_time=0.9)
        contador = self._releva_errores(contador, len(mal))
        self.wait(2.1)

        # --- Ninguna recta alcanza -----------------------------------------
        rot.mostrar(pie_curso("Ninguna recta puede separar esto."),
                   zona="abajo", run_time=0.5)
        self.wait(2.0)
        rot.mostrar(pie_curso("En 1969 este problema congeló la "
                              "investigación en redes por una década."),
                   zona="abajo", run_time=0.5)
        self.wait(2.2)

        # --- La recta derrotada y el contador se retiran --------------------
        self.play(FadeOut(recta, shift=0.6 * DOWN), run_time=0.9)
        self.play(FadeOut(contador), run_time=0.5)
        self.wait(0.7)

        # --- Cierre: gancho hacia apilar neuronas ---------------------------
        rot.mostrar(pie_curso("Hacía falta una idea nueva: apilar "
                              "neuronas."), zona="abajo", run_time=0.5)
        self.wait(2.8)
