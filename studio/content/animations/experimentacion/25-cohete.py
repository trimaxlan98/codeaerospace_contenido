import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import *
from cohete import (COLOR_CARGA, COLOR_EJE, COLOR_ESTRUCTURA, COLOR_MUERTO,
                    COLOR_PROPELENTE, COLOR_TIERRA, DV_LEO, VE_HIDROLOX,
                    VE_QUIMICO, barras_carga, canon_newton, carga_util,
                    curva_tirania, fraccion_propelente, llama_escape,
                    patinador, razon_masas, silueta_cohete)
from code_brand import FUENTE_HUD, registrar_fuentes


class DemoCohete(Scene):
    """Demo de cohete.py: la silueta del cohete apilada por fracciones
    de masa (propelente/estructura/carga, con la llama de escape en la
    base), el patinador sobre el hielo reproducido por `.en(t)` con su
    primer retroceso medido, la curva de la tirania con el presupuesto
    DV_LEO marcado junto a su razon de masas, el canon de Newton
    disparando varias trayectorias reales hasta cerrar la orbita (con
    la velocidad orbital rotulada), y por ultimo las barras de carga
    util para 1/2/3 etapas -- la barra negativa del SSTO quimico que no
    cierra es el punto.

    Todo es determinista: mismo script, mismo render. Los numeros
    (fracciones de masa, retroceso, razon de masas, velocidad orbital,
    carga util) salen de las funciones de la libreria, medidos o
    calculados, nunca a mano.
    """

    def construct(self):
        registrar_fuentes()
        titulo = Text("Tsiolkovsky: la tirania del cohete", font_size=24,
                      color=COLOR_CARGA)
        titulo.to_edge(UP, buff=0.22)
        self.add(titulo)

        # --- acto 1: la silueta apilada y la llama de escape ---
        frac_prop = fraccion_propelente(DV_LEO, VE_HIDROLOX)
        frac_carga = carga_util(DV_LEO, VE_HIDROLOX)
        frac_estr = 1.0 - frac_prop - frac_carga

        silueta = silueta_cohete(frac_prop, frac_estr, frac_carga)
        silueta.move_to(LEFT * 4.3 + UP * 0.1)
        self.play(FadeIn(silueta.contorno), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(silueta.zona(n)) for n in
                                ("propelente", "estructura", "carga")],
                              lag_ratio=0.5), run_time=1.0)

        llama = llama_escape()
        llama.next_to(silueta, DOWN, buff=0.05)
        self.play(LaggedStart(*[FadeIn(p) for p in llama], lag_ratio=0.04),
                  run_time=0.6)

        etiqueta_silueta = Text(
            f"propelente {frac_prop:.1%}  estructura {frac_estr:.1%}  "
            f"carga {frac_carga:.1%}  (ve hidrolox)", font=FUENTE_HUD,
            font_size=12, color=COLOR_CARGA)
        etiqueta_silueta.next_to(silueta, RIGHT, buff=0.6)
        self.play(FadeIn(etiqueta_silueta), run_time=0.4)
        self.wait(0.4)
        self.play(FadeOut(silueta), FadeOut(llama),
                  FadeOut(etiqueta_silueta), run_time=0.4)

        # --- acto 2: el patinador, el cohete en miniatura ---
        n_bolas, dt_lanza = 3, 1.1
        pat = patinador(n_bolas=n_bolas, dt_lanza=dt_lanza)
        pat.move_to(DOWN * 0.4)
        self.play(FadeIn(pat.hielo), run_time=0.3)
        self.play(FadeIn(pat.cuerpo), FadeIn(pat.bolas), run_time=0.3)

        t_max = n_bolas * dt_lanza + 1.2
        self.play(UpdateFromAlphaFunc(
            pat, lambda m, al: m.en(al * t_max)),
            run_time=2.4, rate_func=linear)
        etiqueta_pat = Text(
            f"primer retroceso = {pat.retroceso():.3f} m/s",
            font=FUENTE_HUD, font_size=13, color=COLOR_CARGA)
        etiqueta_pat.next_to(pat, DOWN, buff=0.4)
        self.play(FadeIn(etiqueta_pat), run_time=0.4)
        self.wait(0.3)
        self.play(FadeOut(pat), FadeOut(etiqueta_pat), run_time=0.4)

        # --- acto 3: la curva de la tirania y el canon de Newton ---
        curva = curva_tirania()
        curva.move_to(LEFT * 3.6 + UP * 0.2)
        self.play(FadeIn(curva.ejes), run_time=0.3)
        self.play(Create(curva.curva), run_time=1.2)

        punto_dv = Dot(curva.en(DV_LEO), radius=0.07,
                       color=COLOR_PROPELENTE)
        etiqueta_curva = Text(
            f"DV_LEO = {DV_LEO:.0f} m/s  ->  m0/mf = "
            f"x{razon_masas(DV_LEO, VE_QUIMICO):.2f}", font=FUENTE_HUD,
            font_size=11, color=COLOR_PROPELENTE)
        etiqueta_curva.next_to(curva, DOWN, buff=0.25)
        self.play(FadeIn(punto_dv), FadeIn(etiqueta_curva), run_time=0.5)
        self.wait(0.3)

        canon = canon_newton()
        canon.move_to(RIGHT * 3.4 + DOWN * 0.2)
        self.play(FadeIn(canon.tierra), FadeIn(canon.monte), run_time=0.4)
        disparo = Dot(canon.cima(), radius=0.05, color=COLOR_EJE)
        self.play(FadeIn(disparo), run_time=0.2)

        trayectos = []
        for v_frac, color in ((0.7, COLOR_MUERTO), (0.9, COLOR_ESTRUCTURA),
                              (1.0, COLOR_TIERRA)):
            trayecto = canon.trayectoria(v_frac, color=color)
            trayectos.append(trayecto)
            self.play(Create(trayecto), run_time=1.0)
            self.wait(0.15)

        etiqueta_canon = Text(
            f"v_orbital = {canon.v_orbital_kms():.2f} km/s",
            font=FUENTE_HUD, font_size=12, color=COLOR_TIERRA)
        etiqueta_canon.next_to(canon, DOWN, buff=0.3)
        self.play(FadeIn(etiqueta_canon), run_time=0.4)
        self.wait(0.4)
        self.play(*[FadeOut(m) for m in (
            curva, punto_dv, etiqueta_curva, canon, disparo,
            etiqueta_canon, *trayectos)], run_time=0.5)

        # --- acto 4: las barras de carga util, 1/2/3 etapas ---
        valores = tuple(carga_util(DV_LEO, VE_QUIMICO, etapas=n) * 100.0
                        for n in (1, 2, 3))
        barras = barras_carga(valores)
        barras.move_to(UP * 0.1)
        self.play(FadeIn(barras.eje), run_time=0.3)
        self.play(LaggedStart(*[FadeIn(b) for b in barras.barras],
                              lag_ratio=0.3), run_time=1.0)

        nombres = ("1 etapa", "2 etapas", "3 etapas")
        etiquetas_barras = VGroup()
        for i, nombre in enumerate(nombres):
            color_txt = COLOR_MUERTO if valores[i] < 0 else COLOR_CARGA
            cifra = Text(f"{valores[i]:+.1f}%", font=FUENTE_HUD,
                        font_size=12, color=color_txt)
            cifra.next_to(barras.tope(i),
                         UP if valores[i] >= 0 else DOWN, buff=0.1)
            etiqueta_n = Text(nombre, font=FUENTE_HUD, font_size=11,
                             color=COLOR_EJE)
            etiqueta_n.next_to(barras.base(i),
                              DOWN if valores[i] >= 0 else UP, buff=0.1)
            etiquetas_barras.add(cifra, etiqueta_n)
        self.play(FadeIn(etiquetas_barras), run_time=0.5)

        etiqueta_ssto = Text(
            "el SSTO quimico no cierra: carga util negativa",
            font=FUENTE_HUD, font_size=13, color=COLOR_MUERTO)
        etiqueta_ssto.next_to(barras, DOWN, buff=0.6)
        self.play(FadeIn(etiqueta_ssto), run_time=0.5)
        self.wait(0.6)

        self.play(FadeOut(barras), FadeOut(etiquetas_barras),
                  FadeOut(etiqueta_ssto), run_time=0.5)
