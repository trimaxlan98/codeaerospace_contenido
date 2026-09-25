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
from sdr import db10  # noqa: E402

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
print("== 3.1 Sintonizar en software ==")
y = np.conj(S.nco_por_bloques(37.5e3, 240e3, 24000, 1000, True))
ok(np.allclose(y, np.conj(S.nco(37.5e3, 240e3, 24000))),
   "NCO por bloques con fase continua = NCO de una pieza")
esp_nco, sep_nco = S.espurio_nco_dbc()
ok(-15 < esp_nco < -5 and sep_nco == 240.0,
   "NCO reiniciado: espurio exacto a fs/bloque", (round(esp_nco, 2), sep_nco))
ok(S.espurio_nco_dbc(bloque=1024)[0] < -200,
   "contraejemplo: si el bloque cierra ciclos enteros no hay espurio")
cifra("nco_espurio_dbc", round(esp_nco, 1))
off, niv = S.emisoras_captura()
ok(len(off) == 5, "5 emisoras en la captura", list(np.round(off / 1e3)))
cap = S.captura_banda(96.4e6)
f0, d0 = S.espectro_db(cap, S.RTL["fs"], nfft=2048)
def centroide(f, d, c, ancho=150e3):
    m = np.abs(f - c) < ancho
    p = 10 ** (d[m] / 10)
    return float(np.sum(f[m] * p) / np.sum(p))


fuerte = off[np.argmax(niv)]
c0 = centroide(f0, d0, fuerte)
ok(abs(c0 - fuerte) < 10e3, "el canal de la mas fuerte esta centrado en -700 kHz",
   round(c0 / 1e3, 1))
f1, d1 = S.espectro_db(cap * S.nco(fuerte, S.RTL["fs"], len(cap)),
                       S.RTL["fs"], nfft=2048)
ok(abs(centroide(f1, d1, 0.0)) < 10e3, "el NCO la trae a 0 Hz",
   round(centroide(f1, d1, 0.0) / 1e3, 1))

print("== 3.2 Filtrar y diezmar ==")
fs0 = S.RTL["fs"]
nt = S.kaiser_taps(60, 40e3, fs0)
h = S.fir_paso_bajo(nt, 120e3, fs0)
ho = sps.firwin(nt, 120e3, window=("kaiser", S.kaiser_beta(60)), fs=fs0)
ok(np.allclose(h, ho / ho.sum(), atol=1e-12), "fir_paso_bajo = firwin (oraculo)")
at = S.aten_minima(h, fs0, 140e3)
ok(58.5 < at < 61, "atenuacion de lobulos ~60 dB", round(at, 2))
cifra("fir_taps", nt)
cifra("fir_aten_db", round(at, 1))
fs_, fp_ = S.fuga_vecina(False)
ok(abs(fs_) < 0.01 and fp_ == 20e3, "sin filtro la vecina se pliega entera a +20 kHz",
   (round(fs_, 3), fp_))
techo, mn, mx = S.fuga_vecina_suelo()
ok(techo <= -60, "con filtro: menos de -60 dBc (se rotula el techo)",
   (techo, round(mn, 1), round(mx, 1)))
cifra("fuga_con_filtro_techo", techo)
n1, c1 = S.coste_una_etapa()
a1, a2, c2 = S.coste_dos_etapas()
ok(c2 < c1, "dos etapas cuestan menos", (c1 / 1e6, c2 / 1e6))
h1 = S.fir_paso_bajo(a1, 120e3, fs0)
ok(S.aten_minima(h1, fs0, 480e3 - 140e3) > 58,
   "la primera etapa protege lo que se pliega sobre el canal")
cifra("mac_una_etapa_M", round(c1 / 1e6, 1))
cifra("mac_dos_etapas_M", round(c2 / 1e6, 1))

print("== 3.3 El reloj que miente ==")
for fr in (100e6, 437e6, 1090e6):
    cifra(f"err25ppm_{int(fr / 1e6)}_khz", round(S.ppm_a_hz(25, fr) / 1e3, 2))
for p_ in (27.0, 3.0, -12.5):
    e1 = S.estimar_ppm(p_)[0]
    e2 = S.estimar_ppm(p_, n=1 << 14, semilla=3)[0]
    ok(abs(e1 - p_) < 0.05 and abs(e2 - p_) < 0.05,
       f"estimar_ppm recupera {p_} ppm (dos mallas)", (round(e1, 3), round(e2, 3)))
est, hz = S.estimar_ppm(27.0)
cifra("ppm_estimado", round(est, 1))
cifra("ppm_hz", round(hz))
_, _, dh, med = S.waterfall_deriva()
ok(np.sqrt(np.mean((med - dh) ** 2)) < 10, "la deriva medida sigue a la real",
   round(float(np.sqrt(np.mean((med - dh) ** 2))), 1))
cifra("deriva_hz", round(float(dh[-1])))
cifra("deriva_medida_hz", round(float(med[-1])))

print("== 4.1 El discriminador ==")
fsm = S.FS_MPX
t = np.arange(1 << 15) / fsm
m = np.sin(2 * np.pi * 1e3 * t)
d = S.discriminador(S.fm_modular(m, fsm), fsm)
ok(np.max(np.abs(d[1:] - 75e3 * m[1:])) < 1e-6, "discriminador exacto (salvo n=0)")
x15 = S.fm_modular(np.sin(2 * np.pi * 15e3 * t), fsm)
occ = S.ancho_ocupado(x15, fsm)
occ2 = S.ancho_ocupado(x15, fsm, nfft=16384)
ok(abs(occ - S.carson(75e3, 15e3)) < 3e3 and abs(occ - occ2) < 1e3,
   "Carson ~ ancho ocupado al 98 % medido (dos mallas)", (occ, occ2))
cifra("carson_mono_khz", S.carson(75e3, 15e3) / 1e3)
cifra("carson_estereo_khz", S.carson(75e3, 53e3) / 1e3)
cifra("ocupado_khz", round(occ / 1e3, 1))
de1, de2 = S.mejora_deenfasis(), S.mejora_deenfasis(semilla=9, n=1 << 17)
ok(10 < de1 < 14 and abs(de1 - de2) < 0.3, "deenfasis baja el ruido ~12 dB",
   (round(de1, 2), round(de2, 2)))
cifra("deenfasis_db", round(de1, 1))

print("== 4.2 El multiplex estereo ==")
y, L, R = S.mpx()
f, db = S.espectro_db(y, fsm, nfft=8192)
ok(abs(S.pico(f, db, 18e3, 20e3)[0] - 19e3) < 20, "piloto en 19 kHz")
fase, _ = S.pll_piloto(y)
res = np.unwrap(fase) - 2 * np.pi * 19e3 * np.arange(len(fase)) / fsm
res = (res[20000:] + np.pi) % (2 * np.pi) - np.pi
ok(np.std(res) < 0.02, "PLL enganchado al piloto", round(float(np.std(res)), 4))
Lr, Rr = S.separar_lr(y, fase)
sep = S.separacion_db(Lr, Rr)
ok(sep > 40, "separacion L/R > 40 dB", round(sep, 1))
Lr0, _ = S.separar_lr(y, fase + np.pi / 2)
ok(S.separacion_db(Lr0, Rr) < 1, "contraejemplo: subportadora a 90 grados = mono")
cifra("separacion_db", round(sep, 1))
Lr5, Rr5 = S.separar_lr(y, fase + math.radians(5))
cifra("separacion_5grados_db", round(S.separacion_db(Lr5, Rr5), 1))
pe1, pe2 = S.precio_estereo(), S.precio_estereo(semilla=11, n=1 << 17)
ok(abs(pe1 - pe2) < 0.4, "precio del estereo estable", (round(pe1, 2), round(pe2, 2)))
teo = 10 * math.log10((53 ** 3 - 23 ** 3) / 15 ** 3)
ok(abs(pe1 - teo) < 1.0, "precio ~ integral de f^2 (16.1 dB)", round(teo, 2))
cifra("precio_estereo_db", round(pe1, 1))

print("== 4.3 RDS ==")
ok(S.que_offset(S.bloque_rds(0xC0DE, "A")) == "A", "bloque A se reconoce")
ok(S.que_offset(S.bloque_rds(0xC0DE, "A") ^ (1 << 7)) is None,
   "contraejemplo: un bit volteado rompe el sindrome")
buenas = 0
for sem in range(1, 9):
    r = S.cadena_rds(semilla=sem)
    buenas += int(r["ps"] == "CODE FM " and r["errores"] == 0)
ok(buenas == 8, "RDS decodifica CODE FM sin errores en 8 semillas", buenas)
r8 = S.cadena_rds(cnr_db=8, semilla=1)
cifra("rds_cnr8_errores", r8["errores"])
cifra("rds_cnr8_ps", r8["ps"])

# ---------------------------------------------------------------------
print("== 5.1 La constelacion que gira ==")
for df in (0.0037, -0.011, 0.02):
    _, rx = S.escenario_giro(df_rs=df, semilla=11)
    e = S.estimar_desfase_x4(rx)
    _, rx2 = S.escenario_giro(n=1024, df_rs=df, semilla=5)
    e2 = S.estimar_desfase_x4(rx2)
    ok(abs(e - df) < 1e-5 and abs(e2 - df) < 5e-5,
       f"x^4 estima {df} ciclos/simbolo (dos mallas)", (round(e, 6), round(e2, 6)))
_, rx = S.escenario_giro()
df_est = S.estimar_desfase_x4(rx)
cifra("giro_grados_simbolo", round(360 * 0.0037, 2))
cifra("giro_estimado_grados", round(360 * df_est, 3))
cifra("giro_error_ppm_de_rs", round(abs(df_est - 0.0037) * 1e6, 2))
# contraejemplo: al cuadrado (BPSK) no borra la QPSK
z = rx ** 2
Z = np.abs(np.fft.fft(z, 4 * len(z)))
ok(Z.max() / np.median(Z) < 20, "contraejemplo: x^2 no deja raya con QPSK",
   round(float(Z.max() / np.median(Z)), 1))

print("== 5.2 El lazo de Costas ==")
res_c = {}
for bn in (0.005, 0.02, 0.08):
    tes, js = [], []
    for sem in range(1, 9):
        sim, rx, fr = S.escenario_costas(semilla=sem)
        out, fase, err = S.costas_bpsk(rx, bn)
        te = S.tiempo_enganche(fase, fr)
        tes.append(te if te is not None else 10 ** 6)
        js.append(S.jitter_fase(fase, fr, 1000))
    res_c[bn] = (float(np.median(tes)), float(np.mean(js)))
ok(res_c[0.005][0] > res_c[0.02][0] > res_c[0.08][0],
   "lazo mas ancho engancha antes", [res_c[b][0] for b in res_c])
ok(res_c[0.005][1] < res_c[0.02][1] < res_c[0.08][1],
   "lazo mas ancho tiembla mas", [round(res_c[b][1], 3) for b in res_c])
for bn in res_c:
    cifra(f"costas_{bn}_enganche_simb", int(res_c[bn][0]))
    cifra(f"costas_{bn}_jitter_grados", round(math.degrees(res_c[bn][1]), 1))
inv = []
for f0 in (0.3, 1.1, 1.4, 1.8, 2.3, 2.8):
    sim, rx, fr = S.escenario_costas(fase0=f0, df_rs=0.0, semilla=3)
    out, _, _ = S.costas_bpsk(rx, 0.02)
    inv.append(S.ambiguedad_180(sim, out))
ok(inv == [False, False, False, True, True, True],
   "engancha invertido si la fase inicial pasa de 90 grados", inv)
b = np.random.default_rng(1).integers(0, 2, 60)
ok(np.array_equal(S.dediferencial(1 - S.diferencial(b))[1:], b[1:]),
   "la codificacion diferencial sobrevive a la inversion")

print("== 5.3 El reloj de simbolo ==")
taus = np.array([0.0, 0.1, 0.2, 0.3, 0.4])
ber = S.ber_vs_desfase(taus)
ok(np.all(np.diff(ber) > 0), "la BER crece al muestrear a destiempo",
   list(np.round(ber, 4)))
ber2 = S.ber_vs_desfase(taus, semilla=8, n=40000)
ok(np.all(np.abs(ber2 - ber) < 0.25 * ber + 0.002), "BER estable con otra semilla",
   list(np.round(ber2, 4)))
cifra("ber_tau0", round(float(ber[0]), 4))
cifra("ber_tau03", round(float(ber[3]), 4))
tt = np.linspace(-0.5, 0.5, 11)
sc = S.gardner_curva_s(tt)
ok(abs(sc[5]) < 1e-3 and sc[7] > 0 and sc[3] < 0,
   "curva S de Gardner: cero en el centro, signo del desfase")
ok(abs(sc[0]) < 1e-3 and abs(sc[-1]) < 1e-3, "cero inestable en +-1/2")
tl, ys, sm = S.lazo_reloj()
fin = float(np.mean(tl[-300:]))
ok(abs(fin) < 0.05 and tl[0] > 0.3, "el lazo lleva 0.37 a ~0", round(fin, 4))
ev0, ev1 = S.evm_pct(ys[1:60], sm[1:60]), S.evm_pct(ys[-300:], sm[-300:])
ok(ev1 < ev0 / 3, "EVM baja al converger", (round(ev0, 1), round(ev1, 1)))
cifra("evm_antes_pct", round(ev0, 1))
cifra("evm_despues_pct", round(ev1, 1))

print("== 6.1 ADS-B ==")
h = "8D4840D6202CC371C32CE0576098"
bb = [int(c) for c in bin(int(h, 16))[2:].zfill(112)]
ok(S.crc24(bb[:88]) == int(h[-6:], 16), "CRC-24 de un mensaje REAL (KLM1023)")
klm = S.adsb_decodificar(S.adsb_captura(np.array(bb), snr_db=40), 137)
ok(klm["indicativo"].startswith("KLM1023") and klm["icao"] == "4840D6",
   "decodifica el mensaje real: 4840D6 KLM1023 (oraculo)", klm["indicativo"])
bits = S.adsb_identificacion()
okk, rech = 0, []
for sem in range(1, 11):
    mag = S.adsb_captura(bits, semilla=sem)
    off, d, rj = S.adsb_buscar(mag)
    okk += bool(d) and off == 137 and d["indicativo"] == "CODE101 "
    rech.append(len(rj))
ok(okk == 10, "ADS-B: 10 de 10 semillas (el CRC decide)", rech)
cifra("adsb_icao", d["icao"])
cifra("adsb_indicativo", d["indicativo"])
cifra("adsb_rechazados_por_crc", int(sum(rech)))

print("== 6.2 AIS ==")
okk = 0
for sem in range(1, 21):
    r, ins, tr = S.cadena_ais(snr_db=10, semilla=sem)
    okk += bool(r and r["crc_ok"])
ok(okk == 20, "AIS decodifica 20 de 20 a 10 dB", okk)
r, ins, tr = S.cadena_ais()
ok(r["mmsi"] == 345070001 and abs(r["lat"] - 19.4326) < 1e-4, "AIS: MMSI y posicion")
ok(S.quitar_relleno(S.relleno([1] * 12)[0]) == [1] * 12, "relleno ida y vuelta")
cifra("ais_relleno", ins)
cifra("ais_trama_bits", len(tr))
cifra("ais_mmsi", r["mmsi"])

print("== 6.3 LoRa ==")
for sf in (7, 9):
    s_ = int(np.random.default_rng(sf).integers(0, 2 ** sf))
    ok(S.lora_demodular(S.chirp_lora(sf, s_), sf) == s_, f"LoRa SF{sf} sin ruido")
u = {sf: S.umbral_lora(sf, n_sim=200) for sf in (7, 9, 12)}
ok(u[7] > u[9] > u[12], "cada SF baja el umbral", u)
u2 = {sf: S.umbral_lora(sf, n_sim=200, semilla=5) for sf in (7, 12)}
ok(abs(u2[7] - u[7]) <= 1.0 and abs(u2[12] - u[12]) <= 1.0,
   "umbral estable con otra semilla", u2)
for sf in (7, 9, 12):
    cifra(f"lora_sf{sf}_umbral_db", u[sf])
    cifra(f"lora_sf{sf}_ms", S.tiempo_simbolo_ms(sf))

print("== 7.1 Doppler ==")
t, d, tasa = S.doppler_pase()
t2, d2, tasa2 = S.doppler_pase(n=2401)
ok(abs(d.max() - d2.max()) < 5 and abs(np.abs(tasa).max() - np.abs(tasa2).max()) < 1,
   "Doppler y tasa estables con la malla", (round(d.max()), round(np.abs(tasa).max(), 1)))
cifra("doppler_max_khz", round(d.max() / 1e3, 2))
cifra("doppler_tasa_hz_s", round(float(np.abs(tasa).max()), 1))
_, res = S.residuo_seguimiento(2.0)
cifra("residuo_2s_hz", round(float(np.abs(res).max()), 1))
ok(abs(np.abs(res).max() - 2 * np.abs(tasa).max()) < 5, "residuo = error x tasa")

print("== 7.2 Meteor ==")
bits = np.random.default_rng(2).integers(0, 2, 200)
cod = S.conv_k7(np.concatenate([bits, np.zeros(6, int)]))
ok(np.array_equal(S.viterbi_k7(1 - 2 * cod.astype(float))[:200], bits),
   "Viterbi k=7 sin ruido")
rs = [S.cadena_meteor(semilla=s, rotacion=s % 4) for s in range(1, 11)]
ok(all(q["errores_viterbi"] == 0 and q["rotacion_hallada"] == s % 4
       for q, s in zip(rs, range(1, 11))), "Meteor a Es/N0 = 4 dB: 0 errores y rotacion hallada (10 semillas)")
m = S.cadena_meteor()
cifra("meteor_ber_cruda_pct", round(100 * m["ber_cruda"], 1))
cifra("meteor_errores_viterbi", m["errores_viterbi"])
m1 = S.cadena_meteor(esn0_db=1.0)
ok(m1["errores_viterbi"] > 0, "contraejemplo: a 1 dB Viterbi ya no alcanza",
   m1["errores_viterbi"])

print("== 7.3 GPS ==")
def oct10(c):
    return oct(int("".join(map(str, c[:10])), 2))
ok([oct10(S.codigo_ca(p)) for p in (1, 2, 3, 4, 5)] ==
   ["0o1440", "0o1620", "0o1710", "0o1744", "0o1133"], "C/A PRN1-5 = tabla ICD (oraculo)")
c1 = 1 - 2 * S.codigo_ca(1)
ok(sorted(set(int(np.dot(c1, np.roll(c1, k))) for k in range(1, 1023))) == [-65, -1, 63],
   "autocorrelacion de Gold de tres valores")
esp = (-600 * 2) % 2046
okk, sobre = 0, []
for sem in range(1, 9):
    x = S.gps_captura(semilla=sem)
    dop, rej, (i, j), _ = S.gps_adquirir(x)
    okk += dop[i] == 2500 and j == esp
    sobre.append(float(db10(rej.max() / rej.mean())))
ok(okk == 8, "GPS: Doppler y fase hallados en 8 de 8", round(min(sobre), 1))
cifra("gps_pico_sobre_media_db", round(float(np.median(sobre)), 1))
cifra("gps_ganancia_db", round(S.ganancia_correlacion_db(), 1))
x = S.gps_captura()
g3 = S.gps_adquirir(x, prn=3)[1]
malo = float(db10(g3.max() / g3.mean()))
ok(malo < min(sobre) - 6, "contraejemplo: con el PRN equivocado no hay pico",
   (round(malo, 1), round(min(sobre), 1)))
cifra("gps_prn_equivocado_db", round(malo, 1))

print("== 8.1 Transmitir ==")
im = S.imagenes_dac()
ok(all(abs(m_ - t_) < 0.1 for _, m_, t_ in im), "imagenes del DAC = sinc")
cifra("dac_imagen_0.9_dbc", round(im[0][1], 1))

print("== 8.2 Dos antenas ==")
a1, _ = S.doa_estimar(25.0)
a2, _ = S.doa_estimar(25.0, d_lambda=1.0)
ok(len(a1) == 1 and abs(a1[0] - 25) < 0.5, "lambda/2: un solo angulo", a1)
ok(len(a2) == 2, "lambda: dos angulos (ambiguo)", [round(v, 1) for v in a2])
cifra("doa_estimado", round(a1[0], 1))
cifra("doa_ambiguo", [round(v, 1) for v in a2])

print("== 8.3 Presupuesto ==")
p = S.presupuesto()
for k_ in ("alcance_km", "fspl_db", "prx_dbm", "ruido_dbm", "snr_db", "margen_db"):
    cifra(f"pres_{k_}", round(p[k_], 1))
ok(abs(p["prx_dbm"] - p["ruido_dbm"] - p["snr_db"]) < 1e-9, "presupuesto cierra")


# ---------------------------------------------------------------------
print()
print("== CIFRAS ==")
for k, v in cifras.items():
    print(f"  {k:28s} {v}")
print()
print(f"{len(fallos)} fallos")
for f_ in fallos:
    print("   -", f_)
sys.exit(1 if fallos else 0)
