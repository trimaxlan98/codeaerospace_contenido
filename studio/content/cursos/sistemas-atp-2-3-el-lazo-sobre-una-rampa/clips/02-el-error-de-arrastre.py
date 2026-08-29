import control as _control  # noqa: E402

_control.Text = Text
from control import rampa_con_rezago  # noqa: E402

T_RAMPA = 20.0            # s de rampa simulada
T_VER = 1.5               # s: se muestra a partir de aqui, ya asentado
# `simular_pase` registra `real` un paso DESPUES del instante que rotula,
# asi que el arrastre medido sale sesgado en v*dt: con el dt por defecto
# (0.005) da 0.225 en vez de 0.250. Con dt = 2e-4 el sesgo baja a 0.001 y
# lo dibujado coincide con `error_arrastre`.
DT_FINO = 2e-4
Y_TOPE = 0.36             # grados a fondo de escala de la traza


def _rampa(v):
    """Perfil de referencia con pendiente constante `v` grados/s: es la
    entrada que revela el arrastre (un escalon no lo revela)."""
    t = np.linspace(0.0, T_RAMPA, int(T_RAMPA * 100) + 1)
    return {"t": t, "az_continuo": v * t, "el": v * t}


def _traza_de(v):
    """(t, error) del tramo ya asentado, con el lazo bien amortiguado
    para que se lea el rezago y no el transitorio."""
    s = simular_pase(_rampa(v), kp=KP_BAJO, ki=0.0, kd=KD_OBJ,
                     dt=DT_FINO)
    m = s["t"] >= T_VER
    return s["t"][m], s["error"][m]


T_1, E_1 = _traza_de(1.0)
T_5, E_5 = _traza_de(5.0)


class Clip2(Scene):
    """2.3.2 - Un pase no es un escalon: es una rampa, y ante una rampa
    el proporcional se queda rezagado para siempre. A 5 grados/s ese
    rezago vale dos veces y media el presupuesto. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("El error de arrastre"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- Acto 1: dos rectas paralelas que no se juntan nunca --------
        ramp = rampa_con_rezago(ancho=5.6, alto=2.4, rezago=0.22,
                                muestras=120, color_ref=C_SAT,
                                color_sis=C_CALCULO)
        ramp.move_to(UP * 0.15)
        self.play(Create(ramp.ejes), FadeIn(ramp.etiquetas), run_time=0.9)
        self.play(Create(ramp.ref), run_time=1.4)
        t_ref = tag_hud("referencia", font_size=20, color=C_SAT)
        t_ref.next_to(ramp.punto_ref(1.0), UR, buff=0.10)
        self.play(FadeIn(t_ref), run_time=0.5)
        self.play(Create(ramp.sis), run_time=1.4)
        t_ant = tag_hud("antena", font_size=20, color=C_CALCULO)
        t_ant.next_to(ramp.punto_sis(1.0), DR, buff=0.12)
        self.play(FadeIn(t_ant), run_time=0.5)
        self.wait(0.6)

        p_ref, p_sis = ramp.brecha_en(0.60)
        brecha = DoubleArrow(p_sis, p_ref, buff=0.0, color=C_PELIGRO,
                             stroke_width=3.2, tip_length=0.15)
        self.play(GrowFromCenter(brecha), run_time=0.7)
        rot.mostrar(formula_pie(r"e = v\,b / k_p"), zona="abajo")
        self.wait(2.8)

        self.play(FadeOut(ramp), FadeOut(t_ref), FadeOut(t_ant),
                  FadeOut(brecha), run_time=0.6)

        # --- Acto 2: el error contra el presupuesto ---------------------
        # La banda de +-0.1 grados YA esta dibujada: el rebase se ve
        # cruzar una linea que estaba antes que la curva.
        # `etiqueta_x` de la pieza cuelga a 0.28 del cero, y con esta
        # escala la banda de +-0.1 mide 0.31: el rotulo "t" caia DENTRO de
        # la banda. Se pide sin etiqueta y se pone a mano, mas abajo.
        tr = traza_error(T_1, E_1, ancho=6.0, alto=2.2, y_max=Y_TOPE,
                         color=C_OK, etiqueta_x=None,
                         etiqueta_y="err deg")
        tr.shift(DOWN * 1.05 - tr.cero.get_center())
        t_eje = tag_hud("t", font_size=17, color=C_TENUE)
        t_eje.move_to(tr.cero.get_end() + DOWN * 0.62)
        self.play(Create(tr.ejes), Create(tr.cero), FadeIn(t_eje),
                  run_time=0.8)
        self.play(FadeIn(tr.banda), Create(tr.borde_sup),
                  Create(tr.borde_inf), run_time=0.9)
        t_banda = tag_hud(f"+-{fmt(OBJETIVO_DEG, 1)} deg", font_size=19)
        t_banda.next_to(tr.borde_sup, RIGHT, buff=0.14)
        self.play(FadeIn(t_banda), run_time=0.5)
        self.wait(0.6)

        self.play(Create(tr.curva), run_time=1.8)
        # La pieza entro por sus hijos: se consolida antes del Transform.
        self.remove(*tr.get_family())
        self.add(tr)
        rot.mostrar(cifra_pie(f"1 deg/s: {fmt(E_ARRASTRE_1, 3)} deg",
                              color=C_OK), zona="abajo")
        self.wait(2.4)

        tr5 = tr.gemela(E_5, color=C_PELIGRO)
        tr5.shift(DOWN * 1.05 - tr5.cero.get_center())
        # El carril de la cifra se APAGA antes del morfeo: mientras la
        # curva sube, un frame muestreado ensenaria la cifra de 1 deg/s
        # con la traza de 5. Se vuelve a encender ya con la curva arriba.
        rot.limpiar("abajo", run_time=0.3)
        self.play(Transform(tr, tr5), run_time=1.8)
        rot.mostrar(cifra_pie(f"5 deg/s: {fmt(E_ARRASTRE_5, 2)} deg",
                              color=C_PELIGRO), zona="abajo")
        self.wait(2.4)

        rot.mostrar(cifra_pie(f"{fmt(VECES_PRESUPUESTO, 1)}x el "
                              f"presupuesto", color=C_PELIGRO),
                    zona="abajo")
        self.wait(2.2)

        rot.mostrar(cifra_pie(f"hace falta kp {fmt(KP_NECESARIO, 0)}"),
                    zona="abajo")
        self.wait(2.0)

        panel = panel_cifras(f"kp {fmt(KP_BAJO, 1)}",
                             (f"1 deg/s {fmt(E_ARRASTRE_1, 3)} deg", C_OK),
                             (f"5 deg/s {fmt(E_ARRASTRE_5, 2)} deg",
                              C_PELIGRO),
                             f"kp para 0.1: {fmt(KP_NECESARIO, 0)}")
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(4.2)
