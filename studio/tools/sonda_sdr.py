"""Sonda de invariantes de manim_extensions/sdr.py (curso 38, SDR).

Corre EN EL CONTENEDOR, antes de escribir un solo clip:

    docker run --rm --user $(id -u):$(id -g) -v "$PWD":/workspace \
      -w /workspace codeaerospace_contenido-manim \
      python3 studio/tools/sonda_sdr.py

Cada comprobacion es una propiedad que la funcion solo cumple si esta bien,
con su contraejemplo (la variante rota tiene que FALLAR). Las cifras que van
a pantalla se miden con DOS mallas; scipy entra como oraculo independiente,
nunca como implementacion. Al final imprime la tabla de cifras del lote.
"""
import math
import sys

import numpy as np
from scipy import signal as sps

sys.path.insert(0, "studio/content/manim_extensions")
import sdr as S  # noqa: E402

fallos = []
cifras = {}


def ok(cond, que, valor=""):
    print(("  ok  " if cond else "  XX  ") + que
          + (f"  -> {valor}" if valor != "" else ""))
    if not cond:
        fallos.append(que)


def cifra(nombre, valor):
    cifras[nombre] = valor


# ---------------------------------------------------------------------
print("== Utilidades ==")
fs = 1e6
n = 4096
x = S.tono(fs * 300 / n, fs, n)
f, d = S.espectro_db(x, fs, nfft=n)
fp, _ = S.pico(f, d)
ok(abs(fp - fs * 300 / n) < 1, "pico de un tono complejo en bin", fp)
x = S.tono(fs * 300.37 / n, fs, n)
f, d = S.espectro_db(x, fs, nfft=n)
fp, _ = S.pico(f, d)
ok(abs(fp - fs * 300.37 / n) < 0.1 * fs / n,
   "interpolacion parabolica: error < 0.1 bin fuera de bin",
   round((fp - fs * 300.37 / n) / (fs / n), 3))
# oraculo scipy: nuestro Welch sin solape = scipy.welch sin solape
xr = S.ruido_complejo(8192, 1.0, 3) + S.tono(1e5, fs, 8192)
f1, d1 = S.espectro_db(xr, fs, nfft=1024, ref="abs")
fo, po = sps.welch(xr, fs, window="hann", nperseg=1024, noverlap=0,
                   return_onesided=False, scaling="spectrum",
                   detrend=False)
po = np.fft.fftshift(po)
ok(np.allclose(10 ** (d1 / 10), po, rtol=1e-6),
   "espectro_db = scipy.welch (oraculo)")
p = S.potencia_tono(3 * S.tono(1234.5, fs, 10000), 1234.5, fs)
ok(abs(p - 9) < 1e-9, "potencia_tono exacta fuera de bin", p)

# ---------------------------------------------------------------------
print("== 1.1 De la antena al numero ==")
ok(S.caudal_bps() == 38.4e6, "caudal RTL = 38.4 Mbit/s", S.caudal_bps())
ok(S.caudal_audio() == 768000, "audio = 0.768 Mbit/s")
ok(abs(S.reduccion() - 50) < 1e-9, "reduccion 50x")
cifra("caudal_mbps", S.caudal_bps() / 1e6)
cifra("audio_mbps", S.caudal_audio() / 1e6)
cifra("reduccion", S.reduccion())
fe, ne = S.banda_fm()
ok(len(fe) == 22 and np.all(np.diff(fe) > 0), "22 emisoras ordenadas")
dec = np.round(fe / 1e5) % 2
ok(np.all(dec == 1), "todas en decimas impares (reglamento de las Americas)")
mejor = None
for c in np.arange(88.5e6, 107.6e6, 0.1e6):
    k, _ = S.emisoras_en(c)
    if mejor is None or k > mejor[0]:
        mejor = (k, c)
ok(mejor[0] >= 3, "hay una ventana de 2.4 MHz con >= 3 emisoras", mejor)
cifra("ventana_mejor_centro_mhz", round(mejor[1] / 1e6, 1))
cifra("ventana_mejor_emisoras", mejor[0])
# contraejemplo: con fs/2 de ancho (receptor real) caben menos
k_real, _ = S.emisoras_en(mejor[1], ancho=S.RTL["fs"] / 2)
ok(k_real < mejor[0], "contraejemplo: ventana fs/2 (solo I) ve menos",
   (k_real, mejor[0]))
cifra("ventana_real_emisoras", k_real)
for b in (8, 12):
    s1 = S.sqnr_adc(b, n=1 << 16)
    s2 = S.sqnr_adc(b, n=1 << 18, semilla=9)
    ok(abs(s1 - S.sqnr_teorica(b)) < 0.3, f"SQNR {b} bits ~ 6.02b+1.76",
       (round(s1, 2), round(S.sqnr_teorica(b), 2)))
    ok(abs(s1 - s2) < (0.15 if b == 8 else 0.35), f"SQNR {b} bits estable con otra malla/semilla",
       (round(s1, 2), round(s2, 2)))
    cifra(f"sqnr_{b}", round(s1, 1 if b == 8 else 0))
# contraejemplo: un seno a MEDIA escala pierde 6 dB
s_media = S.sqnr_adc(8, amp=0.5)
ok(abs((cifras["sqnr_8"] - s_media) - 6.0) < 0.5,
   "contraejemplo: media escala cuesta ~6 dB", round(s_media, 2))

# ---------------------------------------------------------------------
print("== 1.2 Mezclar es multiplicar ==")
f, d, (fsum, fdif) = S.mezclar_real()
ok(abs(fsum - (S.F_SENAL + S.F_LO)) < 2e3, "suma medida = f1 + f2",
   fsum / 1e6)
ok(abs(fdif - S.F_IF) < 2e3, "diferencia medida = 10.7 MHz", fdif / 1e6)
cifra("mezcla_suma_mhz", round(fsum / 1e6, 1))
cifra("mezcla_dif_mhz", round(fdif / 1e6, 1))
fd2 = S.mezclar_real(n=1 << 14)[2][1]
ok(abs(fd2 - fdif) < 5e3, "diferencia estable con otra malla", fd2 / 1e6)
a, b = S.imagen_real()
ok(abs(a - 100.3e6) < 1 and abs(b - 78.9e6) < 1, "imagen = 78.9 MHz",
   (a / 1e6, b / 1e6))
cifra("imagen_mhz", round(b / 1e6, 1))
real = S.mezcla_imagen(complejo=False)
cplx = S.mezcla_imagen(complejo=True)
# LO real: deseada e imagen aparecen en +FI y en -FI por igual
ok(abs(real["deseada"][0] - real["deseada"][1]) < 0.01 and
   abs(real["imagen"][0] - real["imagen"][1]) < 0.01,
   "LO real: todo aparece en +FI y -FI (espectro simetrico)")
ok(abs((real["deseada"][0] - real["imagen"][0]) - 6.0) < 0.01,
   "LO real: la imagen llega a +FI (solo 6 dB bajo, su propio nivel)")
# LO complejo: la deseada solo en +FI, la imagen solo en -FI
ok(cplx["deseada"][0] - cplx["deseada"][1] > 60 and
   cplx["imagen"][1] - cplx["imagen"][0] > 60,
   "LO complejo: deseada en +FI, imagen en -FI (separadas)",
   (round(cplx["deseada"][0], 1), round(cplx["imagen"][1], 1)))
cap = S.captura_banda(centro=cifras["ventana_mejor_centro_mhz"] * 1e6)
f, d = S.espectro_db(cap, S.RTL["fs"], nfft=4096)
k_vis = int(np.sum(d > -45))
ok(k_vis > 0, "captura de banda tiene emisoras visibles")
off = 300e3
f2, d2 = S.espectro_db(S.desplazar(cap, off, S.RTL["fs"]), S.RTL["fs"],
                       nfft=4096)
fa, _ = S.pico(f, d)
fb, _ = S.pico(f2, d2)
ok(abs((fa - fb) - off) < 1e3, "desplazar corre el espectro exactamente f",
   (fa - fb) / 1e3)

# ---------------------------------------------------------------------
print("== 1.3 Las cicatrices del cero-IF ==")
xl, xn = S.senal_iq_prueba()
for eps, phi in ((0.05, 3.0), (0.02, 1.0), (0.10, 5.0)):
    y = S.desbalance_iq(xl, eps, phi)
    ok(abs(S.irr_medida(y, xl) - S.irr_db(eps, phi)) < 0.01,
       f"IRR medida = formula (eps={eps}, phi={phi})",
       (round(S.irr_medida(y, xl), 2), round(S.irr_db(eps, phi), 2)))
cifra("irr_antes_db", round(S.irr_db(0.05, 3.0), 1))
# la imagen se VE en -f del espectro, al nivel que dice la IRR
y = S.desbalance_iq(xl, 0.05, 3.0)
pim = S.potencia_tono(y, -180e3, S.RTL["fs"])
pde = S.potencia_tono(y, 180e3, S.RTL["fs"])
ok(abs(S.db10(pde / pim) - S.irr_db()) < 0.1,
   "la imagen espejo en -f esta a -IRR dB")
# correccion ciega sobre la senal RUIDOSA desbalanceada
yn = S.desbalance_iq(xn, 0.05, 3.0)
yc = S.corregir_iq(yn)
irr_desp = S.irr_medida(yc, xl)
ok(irr_desp > 45, "correccion ciega sube la IRR > 45 dB", round(irr_desp, 1))
irrs = []
for sem in range(1, 9):
    _, xs_ = S.senal_iq_prueba(semilla=sem)
    irrs.append(S.irr_medida(S.corregir_iq(S.desbalance_iq(xs_, 0.05, 3.0)),
                             xl))
ok(min(irrs) > 45, "correccion > 45 dB en 8 semillas",
   (round(min(irrs), 1), round(max(irrs), 1)))
suelo, mn, mx = S.irr_corregida_minima()
ok(suelo >= 60 and mx - mn > 10,
   "IRR corregida depende de la malla: se rotula solo el suelo",
   (suelo, round(mn, 1), round(mx, 1)))
cifra("irr_despues_suelo", suelo)
# contraejemplo: no corregir deja la IRR igual
ok(abs(S.irr_medida(yn, xl) - S.irr_db()) < 0.5,
   "contraejemplo: sin corregir sigue en ~29 dB",
   round(S.irr_medida(yn, xl), 2))
xdc = S.con_dc(xn, -12.0)
p_ref = np.mean(np.abs(xn) ** 2)
ok(abs(S.dc_dbc(xdc, p_ref) - (-12.0)) < 0.3, "pico DC a -12 dBc",
   round(S.dc_dbc(xdc, p_ref), 2))
yb = S.quitar_dc(xdc, 0.995)
dc_desp = S.dc_dbc(yb, p_ref, desde=4000)
ok(dc_desp < -40, "bloqueador de DC lo hunde > 28 dB", round(dc_desp, 1))
cifra("dc_antes_dbc", -12.0)
cifra("dc_despues_dbc", round(dc_desp, 1))
# el bloqueador no se come el tono de 180 kHz
ok(abs(S.db10(S.potencia_tono(yb[4000:], 180e3, S.RTL["fs"]) /
              S.potencia_tono(xn[4000:], 180e3, S.RTL["fs"]))) < 0.1,
   "el bloqueador de DC deja pasar el tono intacto")
# oraculo scipy: mismo IIR con lfilter
ok(np.allclose(yb, sps.lfilter([1, -1], [1, -0.995], xdc)),
   "quitar_dc = lfilter([1,-1],[1,-a]) (oraculo)")

# ---------------------------------------------------------------------
print("== 2.1 El piso de ruido ==")
ok(abs(S.ktb_dbm(1) - (-173.98)) < 0.01, "kTB = -174 dBm/Hz",
   round(S.ktb_dbm(1), 2))
for b in (2.4e6, 200e3, 2e3):
    cifra(f"ktb_{int(b)}", round(S.ktb_dbm(b), 1))
ok(abs(S.ktb_dbm(2.4e6) - S.ktb_dbm(200e3) - 10 * math.log10(12)) < 1e-9,
   "el piso sube 10 log(B2/B1)")
nf_a = S.friis([S.CABLE, S.LNA, S.RECEPTOR])
nf_b = S.friis([S.LNA, S.CABLE, S.RECEPTOR])
nf_c = S.friis([S.CABLE, S.RECEPTOR])
ok(nf_b < nf_a < nf_c, "LNA primero < cable primero < sin LNA",
   (round(nf_b, 2), round(nf_a, 2), round(nf_c, 2)))
ok(abs(S.friis([S.RECEPTOR]) - 6.0) < 1e-9, "una sola etapa = su NF")
# contraejemplo: una perdida pasiva de L dB en frente suma L dB exactos
ok(abs(S.friis([S.CABLE, S.RECEPTOR]) - 9.0) < 1e-9,
   "cable de 3 dB delante del receptor = 3 + 6")
cifra("nf_lna_en_antena", round(nf_b, 2))
cifra("nf_cable_primero", round(nf_a, 2))
cifra("nf_sin_lna", round(nf_c, 2))
s_fm = S.sensibilidad_dbm(200e3, nf_b, 12.0)
s_nb = S.sensibilidad_dbm(2e3, nf_b, 6.0)
cifra("sens_fm_dbm", round(s_fm, 1))
cifra("sens_baliza_dbm", round(s_nb, 1))
p_deb = -125.0
for nf, nombre in ((nf_b, "antena"), (nf_a, "escritorio")):
    teo = S.snr_db(p_deb, 2e3, nf)
    med = S.snr_medida(p_deb, 2e3, nf)
    med2 = S.snr_medida(p_deb, 2e3, nf, n=1 << 17, semilla=4)
    ok(abs(teo - med) < 0.2 and abs(med - med2) < 0.2,
       f"SNR medida = calculada, LNA en {nombre}",
       (round(teo, 2), round(med, 2), round(med2, 2)))
    cifra(f"snr_lna_{nombre}", round(med, 1))

# ---------------------------------------------------------------------
print("== 2.2 La ganancia justa ==")
g, s = S.snr_vs_ganancia()
i0, i1, gc, smax = S.punto_dulce(g, s)
ok(s[0] < smax - 15, "con poca ganancia la SINAD es mala", round(s[0], 1))
ok(s[-1] < smax - 10, "con demasiada ganancia se desploma", round(s[-1], 1))
ok(smax <= 30.5, "la SINAD maxima no supera la SNR de entrada (30 dB)",
   round(smax, 2))
cifra("sinad_max", round(smax, 1))
cifra("ganancia_optima", gc)
cifra("tramo_optimo", (i0, i1))
cifra("sinad_g0", round(s[0], 1))
cifra("sinad_gmax", round(s[-1], 1))
g2, s2 = S.snr_vs_ganancia(semilla=77)
_, _, gc2, smax2 = S.punto_dulce(g2, s2)
ok(abs(gc2 - gc) <= 3 and abs(smax2 - smax) < 0.5,
   "punto dulce estable con otra semilla", (gc, gc2, round(smax2, 1)))
xg, wg = S.escenario_ganancia()
lv = S.niveles_usados(10 ** (-60 / 20) * (xg + wg))
cifra("niveles_g0", lv)
ok(lv <= 6, "a -60 dBFS la senal usa un punado de niveles", lv)
esp0, _ = S.espurio_max_dbc(40.0)
esp1, kk = S.espurio_max_dbc(66.0)
ok(esp1 > esp0 + 15, "recortar hace crecer los espurios",
   (round(esp0, 1), round(esp1, 1)))
e_otra = S.espurio_max_dbc(66.0, n=1 << 15)[0]
ok(abs(e_otra - esp1) < 1.0, "espurio de recorte estable con la malla",
   (round(esp1, 2), round(e_otra, 2)))
cifra("espurio_recorte_dbc", round(esp1, 1))
env = S.desvanecimiento()
out = S.agc(env)
var_in = env.max() - env.min()
var_out = out[150:].max() - out[150:].min()
ok(var_out < var_in / 3, "AGC comprime la variacion",
   (round(var_in, 1), round(var_out, 1)))
cifra("agc_entrada_db", round(var_in, 1))
cifra("agc_salida_db", round(var_out, 1))

# ---------------------------------------------------------------------
print("== 2.3 Senales que saturan ==")
f, d, niv = S.dos_tonos_im(0.05)
ok(niv["im_bajo"] > niv["fund"] - 80, "hay producto IM3 visible")
ok(abs(niv["im_bajo"] - niv["im_alto"]) < 0.01, "IM3 simetricos")
r = S.recta_ip3()
ok(abs(r["pendiente_1"] - 1) < 0.05, "pendiente fundamental ~1",
   round(r["pendiente_1"], 3))
ok(abs(r["pendiente_3"] - 3) < 0.05, "pendiente IM3 ~3",
   round(r["pendiente_3"], 3))
ok(abs(r["iip3_db"] - S.iip3_teorico()) < 0.3, "IIP3 medido = teorico",
   (round(r["iip3_db"], 2), round(S.iip3_teorico(), 2)))
cifra("pend_1", round(r["pendiente_1"], 2))
cifra("pend_3", round(r["pendiente_3"], 2))
cifra("iip3_db", round(r["iip3_db"], 1))
# contraejemplo: sin termino cubico no hay IM3
t = np.arange(S.N_IM) / S.FS_IM
xx = 0.05 * (np.cos(2 * np.pi * S.F_IM1 * t) + np.cos(2 * np.pi * S.F_IM2 * t))
yy = S.amplificador(xx, a3=0.0)
ok(S.potencia_tono(yy, 2 * S.F_IM1 - S.F_IM2, S.FS_IM) < 1e-20,
   "contraejemplo: amplificador lineal no produce IM3")
g_lin = S.ganancia_debil(0.0)
g_blq = S.ganancia_debil(S.AMP_BLOQUEADOR)
g_fil = S.ganancia_debil(S.AMP_BLOQUEADOR * 10 ** (-S.ATEN_FILTRO_DB / 20))
ok(abs(g_lin - 20.0) < 0.01, "ganancia lineal 20 dB", round(g_lin, 3))
ok(g_blq < g_lin - 6, "un bloqueador fuerte desensibiliza",
   round(g_blq - g_lin, 2))
ok(abs(g_fil - g_lin) < 0.05, "filtrar 40 dB el bloqueador lo recupera",
   round(g_fil - g_lin, 3))
cifra("desensibilizacion_db", round(g_blq - g_lin, 1))
cifra("tras_filtro_db", round(g_fil - g_lin, 2))
fim = (2 * S.F_IM1 - S.F_IM2, 2 * S.F_IM2 - S.F_IM1)
cifra("im3_mhz", (round(fim[0] / 1e6, 1), round(fim[1] / 1e6, 1)))

# ---------------------------------------------------------------------
print()
print("== CIFRAS DEL LOTE 1 ==")
for k, v in cifras.items():
    print(f"  {k:28s} {v}")
print()
print(f"{len(fallos)} fallos")
for f_ in fallos:
    print("   -", f_)
sys.exit(1 if fallos else 0)
