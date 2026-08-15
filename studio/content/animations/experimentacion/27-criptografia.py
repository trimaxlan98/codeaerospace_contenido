import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import *
from cripto import (A_DH, B_DH, DIGITOS_RSA_2048, E_RSA, G_DH, MENSAJE_HASH,
                    MENSAJE_HASH_2, MENSAJE_OTP, N_BITS_OTP, P_DH, P_RSA,
                    Q_RSA, SEMILLA_OTP, TEXTO_ES, COLOR_ATAQUE,
                    COLOR_CIFRADO, COLOR_CLARO, COLOR_EJE, COLOR_HUELLA,
                    COLOR_LLAVE, bits_distintos, candado, caja_numero,
                    curva_divisiones, diffie_hellman, esquema_dh,
                    exponente_divisiones, flujo, frecuencias,
                    histograma_frecuencias, llave_otp, rejilla_hash,
                    rsa_juguete, rueda_cesar, sha256_bits, texto_a_bits,
                    tira_bits, xor_bits)
from code_brand import FUENTE_HUD, registrar_fuentes


class DemoCriptografia(Scene):
    """Demo de cripto.py: la rueda de Cesar (`rueda_cesar`) girada 3
    posiciones (`.girar(3)`), con la N exterior enfrentada a la Q
    interior; el histograma de frecuencias del espanol
    (`histograma_frecuencias(frecuencias(TEXTO_ES), ...)`) con la letra
    mas comun marcada; una tira de bits (`tira_bits`) con el mensaje, la
    llave (`llave_otp`) y su XOR (`xor_bits`); el esquema de
    Diffie-Hellman (`esquema_dh`) con el valor publico A que Ana grita
    por el canal (`.mensaje()`), calculado con `diffie_hellman`; una caja
    (`caja_numero`) con el modulo RSA de juguete n=3233
    (`rsa_juguete(61, 53, 17)`); la curva de divisiones
    (`curva_divisiones`) con el punto de un RSA-2048 real marcado con
    `.en(617)`; dos rejillas de hash (`rejilla_hash`) de SHA-256("hola")
    y SHA-256("Hola") con los bits distintos marcados y CONTADOS
    (`.marcar_distintos()`); un candado (`candado`) cerrandose
    (`.abierto()` -> `.cerrado()`); y el flujo de una firma (`flujo`)
    mensaje -> huella -> firma.

    Todo el calculo es determinista (el unico azar, `llave_otp`, va
    sembrado; SHA-256 es hashlib): mismo script, mismo render. Sin
    style_block: los colores salen de las constantes `COLOR_*` de
    `cripto.py`.
    """

    def construct(self):
        registrar_fuentes()
        titulo = Text("Criptografía: el arte de guardar secretos",
                      font_size=26, color=COLOR_CLARO)
        titulo.to_edge(UP, buff=0.3)
        self.play(FadeIn(titulo), run_time=0.6)

        # --- acto 1: la rueda de Cesar ---------------------------------
        rueda = rueda_cesar(radio=1.7)
        rueda.move_to(ORIGIN + DOWN * 0.2)
        self.play(Create(rueda.circulo_ext), Create(rueda.circulo_int),
                  run_time=0.6)
        self.play(FadeIn(rueda.exterior), FadeIn(rueda.interior),
                  run_time=0.6)
        self.play(rueda.girar(3), run_time=1.4)
        n_ext = rueda.letra_exterior("N")
        q_int = rueda.letra_interior("Q")
        self.play(Indicate(n_ext, color=COLOR_CLARO, scale_factor=1.6),
                  Indicate(q_int, color=COLOR_CIFRADO, scale_factor=1.6),
                  run_time=0.9)
        etiqueta_cesar = Text("N -> Q  (desplazamiento 3)", font=FUENTE_HUD,
                              font_size=16, color=COLOR_CIFRADO)
        etiqueta_cesar.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(etiqueta_cesar), run_time=0.4)
        self.wait(4.5)
        self.play(FadeOut(rueda), FadeOut(etiqueta_cesar), run_time=0.6)

        # --- acto 2: el histograma medido --------------------------------
        frecs = frecuencias(TEXTO_ES)
        hist = histograma_frecuencias(frecs, COLOR_CLARO, alto=2.2, ancho=8.0)
        hist.move_to(DOWN * 0.2)
        self.play(FadeIn(hist.linea_base), run_time=0.3)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in hist.barras],
                              lag_ratio=0.03), run_time=1.3)
        self.play(FadeIn(hist.etiquetas), run_time=0.4)
        letra_top = max(frecs, key=frecs.get)
        self.play(Indicate(hist.barra(letra_top), color=COLOR_ATAQUE,
                           scale_factor=1.3),
                  Indicate(hist.etiqueta(letra_top), color=COLOR_ATAQUE,
                           scale_factor=1.4), run_time=0.8)
        etiqueta_hist = Text(f"letra mas frecuente: {letra_top} "
                             f"({frecs[letra_top]:.1%})", font=FUENTE_HUD,
                             font_size=16, color=COLOR_ATAQUE)
        etiqueta_hist.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(etiqueta_hist), run_time=0.4)
        self.wait(4.2)
        self.play(FadeOut(hist), FadeOut(etiqueta_hist), run_time=0.6)

        # --- acto 3: la tira de bits y el XOR ------------------------------
        bits_msg = texto_a_bits(MENSAJE_OTP)
        bits_llave = llave_otp(N_BITS_OTP, SEMILLA_OTP)
        bits_cif = xor_bits(bits_msg, bits_llave)
        msg = tira_bits(bits_msg, COLOR_CLARO, celda=0.30)
        msg.shift(UP * 1.0)
        llave = tira_bits(bits_llave, COLOR_LLAVE, celda=0.30)
        cif = tira_bits(bits_cif, COLOR_CIFRADO, celda=0.30)
        cif.shift(DOWN * 1.0)
        oplus = MathTex(r"\oplus", color=COLOR_EJE, font_size=32)
        oplus.move_to(UP * 0.5)
        self.play(LaggedStart(*[FadeIn(c, scale=0.6) for c in msg.celdas],
                              lag_ratio=0.03), run_time=0.9)
        self.play(FadeIn(oplus, scale=0.7),
                  LaggedStart(*[FadeIn(c, scale=0.6) for c in llave.celdas],
                              lag_ratio=0.03), run_time=0.9)
        self.play(LaggedStart(*[FadeIn(c, scale=0.6) for c in cif.celdas],
                              lag_ratio=0.03), run_time=1.0)
        etiqueta_xor = Text(f'xor_bits(texto_a_bits("{MENSAJE_OTP}"), '
                            f"llave_otp) -> ruido", font=FUENTE_HUD,
                            font_size=15, color=COLOR_CIFRADO)
        etiqueta_xor.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(etiqueta_xor), run_time=0.4)
        self.wait(4.2)
        self.play(FadeOut(msg), FadeOut(llave), FadeOut(cif), FadeOut(oplus),
                  FadeOut(etiqueta_xor), run_time=0.6)

        # --- acto 4: Diffie-Hellman gritando en publico ---------------------
        dh = diffie_hellman(P_DH, G_DH, A_DH, B_DH)
        esquema = esquema_dh()
        esquema.move_to(UP * 0.2)
        self.play(FadeIn(esquema.ana), FadeIn(esquema.beto), run_time=0.4)
        self.play(Create(esquema.canal), run_time=0.5)
        self.play(FadeIn(esquema.eva), Create(esquema.eva_linea),
                  run_time=0.4)
        grito = esquema.mensaje(f"A={dh['A']}", desde="ana")
        self.play(FadeIn(grito, shift=0.15 * RIGHT), run_time=0.5)
        self.play(grito.animate.shift(RIGHT * 3.6), run_time=1.0)
        etiqueta_dh = Text(f"diffie_hellman(23,5,6,15): secreto comun = "
                           f"{dh['s_ana']}", font=FUENTE_HUD, font_size=15,
                           color=COLOR_CLARO)
        etiqueta_dh.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(etiqueta_dh), run_time=0.4)
        self.wait(4.5)
        self.play(FadeOut(esquema), FadeOut(grito), FadeOut(etiqueta_dh),
                  run_time=0.6)

        # --- acto 5: la caja del modulo RSA ---------------------------------
        rsa = rsa_juguete(P_RSA, Q_RSA, E_RSA)
        caja_n = caja_numero("n = p * q", rsa["n"], COLOR_CIFRADO, ancho=2.6)
        caja_n.move_to(LEFT * 2.4)
        caja_d = caja_numero("d (privada)", rsa["d"], COLOR_CLARO, ancho=2.6)
        caja_d.move_to(RIGHT * 2.4)
        self.play(FadeIn(caja_n, shift=0.2 * UP), run_time=0.6)
        self.play(FadeIn(caja_d, shift=0.2 * UP), run_time=0.6)
        etiqueta_rsa = Text(f"rsa_juguete(61, 53, 17): n={rsa['n']}, "
                            f"phi={rsa['phi']}, d={rsa['d']}",
                            font=FUENTE_HUD, font_size=15, color=COLOR_CIFRADO)
        etiqueta_rsa.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(etiqueta_rsa), run_time=0.4)
        self.wait(4.0)
        self.play(FadeOut(caja_n), FadeOut(caja_d), FadeOut(etiqueta_rsa),
                  run_time=0.6)

        # --- acto 6: la curva de divisiones ---------------------------------
        curva = curva_divisiones()
        curva.move_to(DOWN * 0.1)
        self.play(FadeIn(curva.ejes), FadeIn(curva.ticks),
                  FadeIn(curva.etiquetas_x), run_time=0.5)
        self.play(Create(curva.curva), run_time=1.4)
        punto = Dot(curva.en(DIGITOS_RSA_2048), radius=0.07,
                   color=COLOR_ATAQUE)
        self.play(FadeIn(punto, scale=0.6), run_time=0.4)
        etiqueta_curva = Text(
            f"RSA-2048: {DIGITOS_RSA_2048} digitos -> "
            f"10^{exponente_divisiones(DIGITOS_RSA_2048):.0f} divisiones",
            font=FUENTE_HUD, font_size=14, color=COLOR_ATAQUE)
        etiqueta_curva.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(etiqueta_curva), run_time=0.4)
        self.wait(4.5)
        self.play(FadeOut(curva), FadeOut(punto), FadeOut(etiqueta_curva),
                  run_time=0.6)

        # --- acto 7: la avalancha del hash -----------------------------------
        bits_1 = sha256_bits(MENSAJE_HASH)
        bits_2 = sha256_bits(MENSAJE_HASH_2)
        rej1 = rejilla_hash(bits_1, COLOR_HUELLA, celda=0.16)
        rej1.move_to(LEFT * 2.6)
        rej2 = rejilla_hash(bits_2, COLOR_HUELLA, celda=0.16)
        rej2.move_to(RIGHT * 2.6)
        self.play(FadeIn(rej1), run_time=0.6)
        self.play(FadeIn(rej2), run_time=0.6)
        n_dist = rej2.marcar_distintos(bits_1, COLOR_ATAQUE)
        etiqueta_hash = Text(
            f'bits_distintos(sha256_bits("{MENSAJE_HASH}"), '
            f'sha256_bits("{MENSAJE_HASH_2}")) = {n_dist} de 256',
            font=FUENTE_HUD, font_size=14, color=COLOR_ATAQUE)
        etiqueta_hash.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(etiqueta_hash), run_time=0.5)
        self.wait(4.2)
        self.play(FadeOut(rej1), FadeOut(rej2), FadeOut(etiqueta_hash),
                  run_time=0.6)
        assert n_dist == bits_distintos(bits_1, bits_2)

        # --- acto 8: el candado cerrandose --------------------------------
        cerrojo = candado(COLOR_LLAVE, alto=1.6).abierto()
        cerrojo.move_to(UP * 0.3)
        self.play(FadeIn(cerrojo), run_time=0.6)
        objetivo = candado(COLOR_LLAVE, alto=1.6).cerrado()
        objetivo.move_to(cerrojo.get_center())
        self.play(Transform(cerrojo, objetivo), run_time=1.0)
        etiqueta_candado = Text("candado(...).abierto() -> .cerrado()",
                                font=FUENTE_HUD, font_size=15,
                                color=COLOR_LLAVE)
        etiqueta_candado.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(etiqueta_candado), run_time=0.4)
        self.wait(4.2)
        self.play(FadeOut(cerrojo), FadeOut(etiqueta_candado), run_time=0.6)

        # --- acto 9: el flujo de la firma -------------------------------------
        cadena = flujo(["mensaje", "huella", "firma"],
                       [COLOR_CLARO, COLOR_HUELLA, COLOR_LLAVE])
        cadena.move_to(ORIGIN)
        self.play(LaggedStart(*[FadeIn(cadena.caja(i), shift=0.2 * UP)
                                for i in range(3)], lag_ratio=0.3),
                  run_time=1.0)
        self.play(LaggedStart(*[GrowArrow(f) for f in cadena.flechas],
                              lag_ratio=0.4), run_time=0.8)
        etiqueta_flujo = Text("flujo(['mensaje', 'huella', 'firma'])",
                             font=FUENTE_HUD, font_size=15, color=COLOR_LLAVE)
        etiqueta_flujo.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(etiqueta_flujo), run_time=0.4)
        self.wait(4.2)
        self.play(FadeOut(cadena), FadeOut(etiqueta_flujo), FadeOut(titulo),
                  run_time=0.6)
