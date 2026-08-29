# El mobiliario de lazo del curso 11: el diagrama de bloques y el
# analogo mecanico (resorte + amortiguador) ya estaban dibujados alli.
# Se inyecta la sombra de Text igual que hace el style_block con las
# demas librerias: control.py crea sus rotulos con el nombre GLOBAL.
import control as _control  # noqa: E402

_control.Text = Text
from control import lazo_cerrado, masa_resorte  # noqa: E402

EL_INICIO = 15.0          # grados: la montura aparcada
EL_META = 60.0            # grados: lo que se le ordena
EL_RESIDUO = 45.0         # grados: donde se queda P+D sola


class Clip1(Scene):
    """2.3.1 - Tres terminos, tres analogos mecanicos sobre el plato: el
    resorte que tira (kp), el amortiguador que frena (kd) y la memoria
    que acumula (ki). (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("Tres terminos"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- Acto 1: el lazo, bloque a bloque ----------------------------
        lazo = lazo_cerrado(ancho=5.6, font_size=15)
        lazo.move_to(UP * 0.55)
        self.play(FadeIn(lazo.eti_r), Create(lazo.flecha_r), run_time=0.7)
        self.play(FadeIn(lazo.sumador), run_time=0.5)
        self.play(Create(lazo.flecha_control), FadeIn(lazo.control),
                  run_time=0.8)
        self.play(Create(lazo.flecha_planta), FadeIn(lazo.planta),
                  run_time=0.8)
        self.play(Create(lazo.flecha_y), FadeIn(lazo.eti_y), run_time=0.7)
        self.play(Create(lazo.rama_retro), run_time=1.0)
        # El grupo entro por sus HIJOS: si no se consolida, el primer
        # `.animate` sobre el padre lo mete otra vez y quedan dos copias.
        self.remove(*lazo.get_family())
        self.add(lazo)

        t_ctrl = tag_junto(lazo.control, "controlador", DOWN, buff=0.14,
                           color=C_CIELO)
        t_pl = tag_junto(lazo.planta, "montura", DOWN, buff=0.14,
                         color=C_CALCULO)
        self.play(FadeIn(t_ctrl), FadeIn(t_pl), run_time=0.6)
        self.wait(1.2)

        # --- Acto 2: el lazo sube y entran los analogos ------------------
        subir = UP * 1.25
        self.play(lazo.animate.shift(subir), t_ctrl.animate.shift(subir),
                  t_pl.animate.shift(subir), run_time=1.0)

        mr = masa_resorte(ancho=2.9)
        mr.move_to(LEFT * 4.05 + DOWN * 1.05)

        mont = montura(alto=2.4, font_size=15)
        d_piv = DOWN * 1.25 - mont.pivote
        mont.shift(d_piv)
        # `pivote` / `base_*` son atributos FIJOS: hay que arrastrarlos con
        # el shift o `apuntar` gira alrededor de donde nacio la pieza.
        mont.pivote = mont.pivote + d_piv
        mont.base_izq = mont.base_izq + d_piv
        mont.base_der = mont.base_der + d_piv
        mont.apuntar(el_deg=EL_INICIO)

        u_meta = np.array([np.cos(np.radians(EL_META)),
                           np.sin(np.radians(EL_META)), 0.0])
        rayo = DashedVMobject(
            Line(mont.pivote, mont.pivote + 1.90 * u_meta,
                 stroke_width=2.4, color=C_SAT), num_dashes=16)

        self.play(FadeIn(mr), FadeIn(mont), Create(rayo), run_time=1.1)
        self.wait(0.4)

        # El estiramiento del resorte ES el error: se ata a la elevacion
        # en vez de animarse aparte, y asi los dos dibujos no se pueden
        # contradecir.
        el = ValueTracker(EL_INICIO)

        def _seguir(m):
            m.apuntar(el_deg=el.get_value())

        def _estirar(m):
            m.estirar((EL_META - el.get_value()) / EL_META * 0.9)

        t_res = tag_junto(mr, "resorte kp", UP, buff=0.18, color=C_CIELO)
        t_amo = tag_junto(mr, "amortiguador kd", DOWN, buff=0.18,
                          color=C_CIELO)

        # --- el resorte: tira fuerte y se pasa ---------------------------
        self.play(FadeIn(t_res),
                  Indicate(mr.resorte, color=C_CIELO, scale_factor=1.12),
                  run_time=0.9)
        rot.mostrar(formula_pie(r"k_p\,e"), zona="abajo")
        mont.add_updater(_seguir)
        mr.add_updater(_estirar)
        for objetivo, rt in ((78.0, 0.55), (44.0, 0.50), (70.0, 0.46),
                             (52.0, 0.42), (65.0, 0.40), (57.0, 0.38)):
            self.play(el.animate.set_value(objetivo), run_time=rt)
        mont.clear_updaters()
        mr.clear_updaters()
        self.wait(1.4)

        # --- el amortiguador: el mismo mando, sin rebote -----------------
        self.play(FadeIn(t_amo),
                  Indicate(mr.amortiguador, color=C_CIELO,
                           scale_factor=1.12), run_time=0.9)
        rot.mostrar(formula_pie(r"k_d\,\dot e"), zona="abajo")
        mont.add_updater(_seguir)
        mr.add_updater(_estirar)
        self.play(el.animate.set_value(EL_INICIO), run_time=0.7)
        self.play(el.animate.set_value(EL_META), run_time=1.8,
                  rate_func=smooth)
        mont.clear_updaters()
        mr.clear_updaters()
        self.wait(1.4)

        # --- la memoria: lo que queda cuando P y D ya no dan mas ---------
        mont.add_updater(_seguir)
        mr.add_updater(_estirar)
        self.play(el.animate.set_value(EL_RESIDUO), run_time=0.8)

        def _arco():
            # Una cuna rellena, no un arco fino: 15 grados de hueco en un
            # arco de trazo se pierden en el cuadro. Los radios caen DENTRO
            # del brazo (1.10) y por fuera del anillo de acimut, asi que la
            # cuna no pisa ni el plato ni la elipse.
            a0 = np.radians(el.get_value())
            da = max(np.radians(EL_META) - a0, 1e-3)
            a = AnnularSector(inner_radius=0.34, outer_radius=0.92,
                              angle=da, start_angle=a0,
                              arc_center=mont.pivote, stroke_width=0,
                              fill_color=C_PELIGRO, fill_opacity=0.45)
            return a

        arco = always_redraw(_arco)
        self.add(arco)
        self.wait(0.8)

        marco = Rectangle(width=0.66, height=1.55, stroke_width=2.6,
                          color=C_CIELO)
        marco.move_to(RIGHT * 3.35 + DOWN * 1.05)
        nivel = ValueTracker(0.0)

        def _relleno():
            h = max(1e-3, nivel.get_value() * 1.42)
            r = Rectangle(width=0.54, height=h, stroke_width=0,
                          fill_color=C_CIELO, fill_opacity=0.55)
            r.move_to(marco.get_bottom() + UP * (h / 2.0 + 0.062))
            return r

        relleno = always_redraw(_relleno)
        t_mem = tag_junto(marco, "memoria ki", DOWN, buff=0.18,
                          color=C_CIELO)
        rot.mostrar(formula_pie(r"k_i \int e\,dt"), zona="abajo")
        self.play(Create(marco), FadeIn(t_mem), run_time=0.7)
        self.add(relleno)
        self.play(nivel.animate.set_value(1.0),
                  el.animate.set_value(EL_META), run_time=2.6,
                  rate_func=smooth)
        mont.clear_updaters()
        mr.clear_updaters()
        relleno.clear_updaters()
        arco.clear_updaters()
        self.play(FadeOut(arco), run_time=0.4)
        self.wait(1.2)

        # --- la ley entera, y las dos ganancias medidas ------------------
        rot.mostrar(formula_pie(
            r"u = k_p\,e + k_i \int e\,dt + k_d\,\dot e"), zona="abajo")
        panel = panel_cifras(f"kp {fmt(KP_BAJO, 1)}",
                             f"kd {fmt(KD_OBJ, 2)}")
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(4.4)
