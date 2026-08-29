"""Sonda del curso 30 (Sistemas ATP): exige a cada funcion de atp.py que
devuelva un numero, y lo contrasta contra el ejemplo resuelto del curso
fuente de la Academy (prisma/seed-data/sistemas-apt).

Un fallo aqui es una cifra que habria salido en pantalla siendo mentira.

Se corre EN EL CONTENEDOR: el numpy del host ya corrompio arrays en
silencio una vez (1.26.4 de sdist sobre Python 3.14).
"""
import sys

sys.path.insert(0, "/workspace/studio/content/manim_extensions")
import numpy as np  # noqa: E402

import atp  # noqa: E402

fallos = []


def check(nombre, ok, detalle=""):
    print(f"{'OK   ' if ok else 'FALLA'} {nombre}: {detalle}")
    if not ok:
        fallos.append(nombre)


def cerca(a, b, tol_rel=0.02):
    """Tolerancia relativa: el texto fuente redondea a 3 cifras."""
    if b == 0:
        return abs(a) < tol_rel
    return abs(a - b) / abs(b) <= tol_rel


print("=" * 70)
print("0 - el canario de numpy (ver memoria numpy-sistema-roto)")
print("=" * 70)
print(f"  numpy {np.__version__}, python {sys.version.split()[0]}")
_v = np.linspace(0.0, 1.0, 5)
check("numpy vivo", np.allclose(_v, [0, .25, .5, .75, 1.0]), f"{_v}")
_m = np.linalg.eig(np.array([[0.0, 1.0], [-2.0, -3.0]]))[0]
check("numpy.linalg vivo", cerca(float(np.min(_m.real)), -2.0, 1e-6),
      f"autovalores {np.sort(_m.real)}")

print()
print("=" * 70)
print("L1.1 - el cielo que se mueve")
print("=" * 70)

v550 = atp.velocidad_circular(550)
check("v a 550 km = 7.59 km/s", cerca(v550, 7.59), f"{v550:.4f}")
w550 = atp.velocidad_angular_cenit(550)
check("omega cenit 550 = 0.79 grados/s", cerca(w550, 0.79), f"{w550:.4f}")
w400 = atp.velocidad_angular_cenit(400)
check("omega cenit 400 = 1.10 grados/s", cerca(w400, 1.10), f"{w400:.4f}")
per = atp.periodo_orbital(550) / 60.0
check("periodo 550 = 95.5 min", cerca(per, 95.5), f"{per:.3f} min")

arco = atp.arco_central_pase(550, 90.0, 5.0)
check("arco central cenital = 36.9 grados", cerca(arco, 36.9), f"{arco:.3f}")
dur = atp.duracion_pase(550, 90.0, 5.0) / 60.0
check("pase cenital = 9.8 min", cerca(dur, 9.8), f"{dur:.3f} min")

# el GEO, para el clip 1 (dato publico, pero la altura se comprueba)
t_geo = atp.periodo_orbital(35786) / 3600.0
check("GEO ~ dia sidereo (23.934 h)", cerca(t_geo, 23.934, 0.005),
      f"{t_geo:.4f} h")

print()
print("=" * 70)
print("L1.2 - de dos lineas a dos angulos")
print("=" * 70)

h155 = atp.altitud_de_movimiento_medio(15.5)
check("n=15.5 -> h=424 km", cerca(h155, 424, 0.01), f"{h155:.2f} km")
h150 = atp.altitud_de_movimiento_medio(15.0)
check("n=15.0 -> h=574 km", cerca(h150, 574, 0.01), f"{h150:.2f} km")
check("media rev menos = ~150 km mas", cerca(h150 - h155, 150, 0.05),
      f"{h150 - h155:.1f} km")

az, el, d = atp.enu_a_azel(400, 300, 500)
check("ENU(400,300,500) -> Az 53.13", cerca(az, 53.13), f"{az:.3f}")
check("ENU(400,300,500) -> El 45.0", cerca(el, 45.0), f"{el:.3f}")
check("ENU(400,300,500) -> d 707.1", cerca(d, 707.1), f"{d:.2f}")
# el error de signo mas frecuente: si se invierte, Az sale 36.87
check("Az mide del NORTE al ESTE (no al reves)", abs(az - 36.87) > 1.0,
      f"invertido daria 36.87, da {az:.2f}")

e_reloj = atp.error_por_reloj(1.0, 550)
check("1 s de reloj = 0.79 grados", cerca(e_reloj, 0.79), f"{e_reloj:.4f}")
check("1 s de reloj > 8 presupuestos", e_reloj / atp.OBJETIVO_DEG > 7.5,
      f"{e_reloj / atp.OBJETIVO_DEG:.2f}x el objetivo")

print()
print("=" * 70)
print("L1.3 - la ventana y el keyhole")
print("=" * 70)

d_cenit = float(atp.rango_oblicuo(550, 90))
check("rango en el cenit = la altitud", cerca(d_cenit, 550, 1e-6),
      f"{d_cenit:.4f} km")
d5 = float(atp.rango_oblicuo(550, 5))
check("rango a 5 grados = 2205 km", cerca(d5, 2205, 0.01), f"{d5:.1f} km")
atten = 20.0 * np.log10(d5 / 550.0)
check("atenuacion extra = 12.1 dB", cerca(atten, 12.1, 0.02),
      f"{atten:.2f} dB")

lam0 = float(atp.angulo_central(550, 0.0))
check("angulo central en el horizonte = 22.9", cerca(lam0, 22.9),
      f"{lam0:.3f}")

d30 = float(atp.rango_oblicuo(550, 30))
check("d en culminacion a 30 grados ~ 990 km", cerca(d30, 993, 0.01),
      f"{d30:.1f} km")
d85 = float(atp.rango_oblicuo(550, 85))
check("d en culminacion a 85 grados ~ 552 km", cerca(d85, 552, 0.01),
      f"{d85:.1f} km")

az30 = atp.tasa_acimut(550, 30)
check("tasa acimut a 30 grados = 0.51 /s", cerca(az30, 0.51, 0.03),
      f"{az30:.4f}")
az85 = atp.tasa_acimut(550, 85)
check("tasa acimut a 85 grados = 9.04 /s", cerca(az85, 9.04, 0.03),
      f"{az85:.4f}")
check("85 es ~18x mas exigente que 30", cerca(az85 / az30, 17.8, 0.05),
      f"{az85 / az30:.2f}x")

kh = atp.radio_keyhole(550, 6.0)
check("keyhole con rotor de 6 /s existe y es de pocos grados",
      0.5 < kh < 15.0, f"radio {kh:.2f} grados")
kh10 = atp.radio_keyhole(550, 10.0)
check("un rotor mas rapido deja keyhole mas chico", kh10 < kh,
      f"6/s -> {kh:.2f}, 10/s -> {kh10:.2f}")

print()
print("--- perfil_pase: el modelo completo ---")
for elm in (30.0, 70.0, 85.0):
    p = atp.perfil_pase(550, elm, 5.0, n=2000)
    print(f"  el_max={elm:5.1f}  dur={p['duracion'] / 60:5.2f} min  "
          f"d_min={p['d_min']:7.1f} km  el_max_medido={p['el_max']:5.2f}  "
          f"az_barrido={p['az_barrido']:7.2f}  "
          f"az_pto_max={p['az_pto_max']:6.3f} /s  "
          f"vr_max={p['vr_max']:5.3f} km/s")

p85 = atp.perfil_pase(550, 85.0, 5.0, n=4000)
check("perfil: el_max se respeta", cerca(p85["el_max"], 85.0, 0.01),
      f"{p85['el_max']:.3f}")
check("perfil: d_min coincide con rango_oblicuo(85)",
      cerca(p85["d_min"], d85, 0.01), f"{p85['d_min']:.1f} vs {d85:.1f}")
check("perfil: tasa de acimut pico coincide con tasa_acimut(85)",
      cerca(p85["az_pto_max"], az85, 0.06),
      f"perfil {p85['az_pto_max']:.3f} vs formula {az85:.3f}")
p89 = atp.perfil_pase(550, 89.5, 5.0, n=4000)
check("perfil: pase casi cenital barre casi 180 grados de acimut",
      abs(p89["az_barrido"]) > 170.0, f"{p89['az_barrido']:.2f} grados")

print()
print("=" * 70)
print("L2.1 - la frecuencia que se mueve")
print("=" * 70)

vr = atp.velocidad_radial_max(550)
check("vr max = 7.0 km/s (NO 7.59)", cerca(vr, 7.0, 0.02), f"{vr:.4f} km/s")
check("vr max es menor que la velocidad orbital", vr < v550,
      f"{vr:.3f} < {v550:.3f}")

fd = abs(atp.doppler_hz(7500.0, 437e6))
check("437 MHz con vr=7.5 km/s -> 10.9 kHz", cerca(fd, 10925, 0.01),
      f"{fd:.0f} Hz")

tabla = atp.tabla_doppler(550)
for f in tabla:
    print(f"  {f['nombre']:<14s} fd={f['fd_hz'] / 1000:8.2f} kHz   "
          f"excursion={f['excursion_hz'] / 1000:8.2f} kHz")
esperado = {"VHF 145 MHz": 3.4, "UHF 437 MHz": 10.2, "S 2200 MHz": 51.0,
            "X 8400 MHz": 196.0}
for f in tabla:
    e = esperado[f["nombre"]]
    check(f"doppler {f['nombre']} ~ {e} kHz",
          cerca(f["fd_hz"] / 1000.0, e, 0.05), f"{f['fd_hz'] / 1000:.2f} kHz")
check("la excursion es el DOBLE del corrimiento",
      cerca(tabla[1]["excursion_hz"], 2 * tabla[1]["fd_hz"], 1e-9),
      f"{tabla[1]['excursion_hz'] / 1000:.2f} kHz")

tasa = atp.tasa_doppler(550, 437e6)
check("tasa doppler en culminacion ~ 153 Hz/s", cerca(tasa, 153, 0.05),
      f"{tasa:.1f} Hz/s")

# el signo: acercarse SUBE la frecuencia
check("acercarse (vr<0) sube la frecuencia", atp.doppler_hz(-7000.0, 437e6) > 0,
      f"{atp.doppler_hz(-7000.0, 437e6):.0f} Hz")

pd = atp.perfil_pase(550, 70.0, 5.0, n=1200)
cur = atp.curva_doppler(pd, 437e6)
check("curva S: empieza positiva y acaba negativa",
      cur[0] > 0 and cur[-1] < 0, f"{cur[0]:.0f} -> {cur[-1]:.0f} Hz")
i_cruce = int(np.argmin(np.abs(cur)))
check("curva S: cruza cero en la maxima aproximacion",
      abs(i_cruce - int(np.argmin(pd["d"]))) < len(cur) * 0.03,
      f"cruce en i={i_cruce}, d_min en i={int(np.argmin(pd['d']))}")

print()
print("=" * 70)
print("L2.2 - la montura es un robot")
print("=" * 70)

A, B = atp.matrices_eje()
check("A = [[0,1],[0,-0.25]]", cerca(A[1, 1], -0.25, 1e-9), f"{A.tolist()}")
check("B = [0, 0.5]", cerca(float(B[1, 0]), 0.5, 1e-9), f"{B.ravel().tolist()}")
tm = atp.constante_mecanica()
check("constante mecanica J/b = 4 s", cerca(tm, 4.0, 1e-9), f"{tm:.3f} s")

par = atp.par_necesario(alpha_deg_s2=5.0, w_deg_s=1.0)
check("par inercial = 0.175 N m", cerca(par["inercial"], 0.175, 0.01),
      f"{par['inercial']:.4f}")
check("par friccion = 0.0087 N m", cerca(par["friccion"], 0.0087, 0.02),
      f"{par['friccion']:.5f}")
check("par total = 0.184 N m", cerca(par["total"], 0.184, 0.01),
      f"{par['total']:.4f}")

pm = atp.par_motor(par["total"], 1000.0, 0.7)
check("par del motor = 0.26 mN m", cerca(pm * 1000, 0.26, 0.02),
      f"{pm * 1000:.4f} mN m")

pv = atp.par_viento(10.0, 3.0, 0.15)
check("par de viento (10 m/s, plato 3 m) ~ 78 N m", cerca(pv, 78, 0.03),
      f"{pv:.2f} N m")
razon = pv / par["total"]
print(f"  el viento es {razon:.0f}x el par de acelerar la inercia")
check("el viento domina por 2+ ordenes de magnitud", razon > 300,
      f"{razon:.0f}x")

res = atp.resolucion_encoder(16, 360.0)
check("encoder 16 bits = 0.0055 grados", cerca(res, 0.0055, 0.02),
      f"{res:.6f}")

bl = atp.traza_backlash(0.3, 1.2)
recorrido_perdido = float(np.max(bl["entrada"]) - np.max(bl["salida"]))
check("backlash: la salida pierde media holgura en cada extremo",
      cerca(recorrido_perdido, 0.15, 0.1), f"{recorrido_perdido:.4f} grados")
check("backlash de 0.3 se come el presupuesto de 0.1 entero",
      bl["perdido_deg"] > atp.OBJETIVO_DEG,
      f"{bl['perdido_deg']} > {atp.OBJETIVO_DEG}")

print()
print("=" * 70)
print("L2.3 - el lazo sobre una rampa")
print("=" * 70)

e1 = atp.error_arrastre(1.0, kp=10.0)
check("arrastre a 1 grado/s = 0.05", cerca(e1, 0.05, 1e-9), f"{e1:.4f}")
e5 = atp.error_arrastre(5.0, kp=10.0)
check("arrastre a 5 grados/s = 0.25", cerca(e5, 0.25, 1e-9), f"{e5:.4f}")
check("a 5 grados/s se pasa 2.5x del presupuesto",
      cerca(e5 / atp.OBJETIVO_DEG, 2.5, 1e-9), f"{e5 / atp.OBJETIVO_DEG:.2f}x")
kp_ok = atp.kp_para_arrastre(5.0, 0.1)
check("kp necesario para 0.1 a 5 grados/s = 25", cerca(kp_ok, 25.0, 1e-9),
      f"{kp_ok:.2f}")

z0, wn0 = atp.zeta_wn(kp=10.0, kd=0.0)
check("wn con kp=10, J=2 -> 2.24 rad/s", cerca(wn0, 2.236, 0.01),
      f"{wn0:.4f}")
check("zeta con P puro = 0.056", cerca(z0, 0.056, 0.02), f"{z0:.5f}")
mp0 = atp.sobreimpulso(z0)
check("sobreimpulso P puro = 84 %", cerca(mp0, 0.84, 0.02),
      f"{mp0 * 100:.1f} %")
ts0 = atp.t_establecimiento(z0, wn0)
check("t_est P puro = 32 s", cerca(ts0, 32, 0.06), f"{ts0:.2f} s")

kd7 = atp.kd_para_zeta(0.7, 10.0)
check("kd para zeta=0.7 -> 5.76", cerca(kd7, 5.76, 0.01), f"{kd7:.4f}")
z7, wn7 = atp.zeta_wn(kp=10.0, kd=kd7)
check("zeta resultante = 0.7", cerca(z7, 0.7, 1e-6), f"{z7:.5f}")
mp7 = atp.sobreimpulso(z7)
check("sobreimpulso con zeta=0.7 = 4.6 %", cerca(mp7, 0.046, 0.05),
      f"{mp7 * 100:.2f} %")
ts7 = atp.t_establecimiento(z7, wn7)
check("t_est con zeta=0.7 = 2.6 s", cerca(ts7, 2.6, 0.06), f"{ts7:.3f} s")
check("D acelera el asentamiento ~12x", cerca(ts0 / ts7, 12.2, 0.1),
      f"{ts0 / ts7:.1f}x")
# el detalle que importa: D NO cambia el arrastre
check("D NO cambia el error de arrastre",
      atp.error_arrastre(5.0, kp=10.0) == e5, "kd no entra en v b / kp")

print()
print("--- simular_pase: el lazo sobre el pase real ---")
perf = atp.perfil_pase(550, 70.0, 5.0, n=1200)
for etiqueta, kw in (
        ("P puro kp=10", dict(kp=10.0, ki=0.0, kd=0.0)),
        ("PD kp=25 kd=8", dict(kp=25.0, ki=0.0, kd=8.0)),
        ("PID kp=25 ki=2 kd=8", dict(kp=25.0, ki=2.0, kd=8.0)),
):
    s = atp.simular_pase(perf, **kw)
    print(f"  {etiqueta:<22s} rms={s['rms']:8.4f} deg  "
          f"max={s['max']:8.4f} deg  sat={s['frac_saturado'] * 100:5.1f} %")

s_p = atp.simular_pase(perf, kp=10.0, ki=0.0, kd=0.0)
s_pid = atp.simular_pase(perf, kp=25.0, ki=2.0, kd=8.0)
check("el PID mejora al P puro", s_pid["rms"] < s_p["rms"],
      f"{s_pid['rms']:.4f} < {s_p['rms']:.4f}")
check("el error del PID cabe en el presupuesto", s_pid["rms"] < 0.1,
      f"rms {s_pid['rms']:.4f} grados")

# El par de seguimiento es DIMINUTO: por eso el windup no puede
# demostrarse con el seguimiento, hace falta una RAFAGA (ver docstring).
p85 = atp.perfil_pase(550, 85.0, 5.0, n=1500)
s85 = atp.simular_pase(p85, kp=25.0, ki=2.0, kd=8.0, u_max=10.0)
u_pico = float(np.max(np.abs(s85["u"])))
print(f"  par de SEGUIMIENTO pico en el pase mas exigente: "
      f"{u_pico:.4f} N m")
check("el seguimiento nunca satura un accionamiento sensato",
      u_pico < 0.5, f"pico {u_pico:.4f} N m frente a u_max=0.5")

print()
print("--- windup: en la ADQUISICION, no en una rafaga ---")
# Medido: a esta escala, una rafaga que supera el motor no da windup, da
# perdida de control (14 a 900 grados de error). El windup de libro vive
# en el escalon de preposicionamiento previo al AOS.
a_sin = atp.simular_adquisicion(60.0, ki=2.0, antiwindup=False)
a_con = atp.simular_adquisicion(60.0, ki=2.0, antiwindup=True)
for et, s in (("sin antiwindup", a_sin), ("con antiwindup", a_con)):
    print(f"  {et:<16s} sobreimpulso={s['sobreimpulso']:7.3f} deg  "
          f"t_asent={s['t_asentamiento']:7.2f} s  "
          f"sat={s['frac_saturado'] * 100:5.1f} %")
check("el salto de adquisicion SI satura el accionamiento",
      a_sin["frac_saturado"] > 0.15,
      f"{a_sin['frac_saturado'] * 100:.1f} % del tiempo saturado")
check("sin antiwindup el sobreimpulso es ~28 grados",
      cerca(a_sin["sobreimpulso"], 27.7, 0.05), f"{a_sin['sobreimpulso']:.3f}")
check("con antiwindup baja a ~15 grados",
      cerca(a_con["sobreimpulso"], 15.3, 0.05), f"{a_con['sobreimpulso']:.3f}")
check("el antiwindup casi parte por dos el sobreimpulso",
      a_con["sobreimpulso"] < 0.6 * a_sin["sobreimpulso"],
      f"{a_con['sobreimpulso'] / a_sin['sobreimpulso']:.2f}x")
check("sin antiwindup NO se asienta en 40 s",
      not np.isfinite(a_sin["t_asentamiento"]),
      f"{a_sin['t_asentamiento']}")
check("con antiwindup se asienta en ~10 s",
      cerca(a_con["t_asentamiento"], 9.95, 0.1),
      f"{a_con['t_asentamiento']:.2f} s")

print()
print("=" * 70)
print("L3.1 - LQR")
print("=" * 70)

c = atp.controlabilidad(A, B)
check("det C = -0.25", cerca(c["det"], -0.25, 1e-9), f"{c['det']:.6f}")
check("rango 2: el eje es controlable", c["rango"] == 2, f"rango {c['rango']}")

# contra la forma cerrada del doble integrador
Ad = np.array([[0.0, 1.0], [0.0, 0.0]])
Bd = np.array([[0.0], [1.0]])
for q, r in ((100.0, 1.0), (100.0, 100.0), (1.0, 1.0), (16.0, 1.0)):
    K, P = atp.lqr(Ad, Bd, np.diag([q, 0.0]), np.array([[r]]))
    cf = atp.lqr_doble_integrador(q, r)
    ok = cerca(K[0, 0], cf["k1"], 1e-6) and cerca(K[0, 1], cf["k2"], 1e-6)
    check(f"lqr(q={q}, r={r}) == forma cerrada", ok,
          f"K numerico {K.ravel().round(5).tolist()} vs "
          f"cerrada [{cf['k1']:.5f}, {cf['k2']:.5f}]")

cf = atp.lqr_doble_integrador(100.0, 1.0)
check("q=100 r=1 -> k1=10", cerca(cf["k1"], 10.0, 1e-9), f"{cf['k1']:.4f}")
check("q=100 r=1 -> k2=4.47", cerca(cf["k2"], 4.4721, 1e-4), f"{cf['k2']:.4f}")
check("q=100 r=1 -> wn=3.16", cerca(cf["wn"], 3.1623, 1e-4), f"{cf['wn']:.4f}")
check("q=100 r=1 -> t_est=1.8 s", cerca(cf["t_est"], 1.75, 0.05),
      f"{cf['t_est']:.3f} s")
cf100 = atp.lqr_doble_integrador(100.0, 100.0)
check("r=100 -> wn=1 rad/s", cerca(cf100["wn"], 1.0, 1e-6),
      f"{cf100['wn']:.4f}")
check("el lazo se hace 3.16x mas lento (raiz cuarta de 100)",
      cerca(cf["wn"] / cf100["wn"], 100 ** 0.25, 1e-6),
      f"{cf['wn'] / cf100['wn']:.4f} vs {100 ** 0.25:.4f}")
# EL REGALO: zeta = 0.707 para cualquier q y r
zetas = [atp.lqr_doble_integrador(q, r)["zeta"]
         for q in (1.0, 10.0, 100.0, 5000.0) for r in (0.1, 1.0, 100.0)]
check("zeta = 0.707 para CUALQUIER q y r",
      all(cerca(z, 0.7071, 1e-4) for z in zetas),
      f"min {min(zetas):.5f} max {max(zetas):.5f}")

# margenes del LQR sobre el eje real
Kr, _ = atp.lqr(A, B, np.diag([100.0, 1.0]), np.array([[1.0]]))
m = atp.margenes(A, B, Kr)
print(f"  K = {Kr.ravel().round(4).tolist()}")
print(f"  margen de ganancia = {m['margen_ganancia_db']}, "
      f"margen de fase = {m['margen_fase_deg']:.2f} grados, "
      f"wc = {m['wc']:.3f} rad/s")
check("LQR: margen de fase >= 60 grados (garantia del metodo)",
      m["margen_fase_deg"] >= 59.5, f"{m['margen_fase_deg']:.2f}")
check("LQR: margen de ganancia infinito hacia arriba",
      not np.isfinite(m["margen_ganancia_db"]),
      f"{m['margen_ganancia_db']}")
mf_ret = atp.margen_fase_con_retardo(A, B, Kr, 0.05)
check("un retardo de 50 ms se come margen de fase",
      mf_ret < m["margen_fase_deg"],
      f"{m['margen_fase_deg']:.1f} -> {mf_ret:.1f} grados")

print()
print("=" * 70)
print("L3.2 - Monte Carlo")
print("=" * 70)

pres = atp.presupuesto_cuadratura({"sesgo": 0.03, "viento": 0.05,
                                   "ruido": 0.02, "latencia": 0.04})
check("presupuesto en cuadratura = 0.073 grados",
      cerca(pres["total"], 0.073, 0.02), f"{pres['total']:.5f}")
check("el dominante es el viento", pres["dominante"] == "viento",
      f"{pres['dominante']}")
check("margen del 27 % bajo el objetivo", cerca(pres["margen_rel"], 0.27, 0.05),
      f"{pres['margen_rel'] * 100:.1f} %")
# la leccion del metodo: bajar el grande mueve, bajar el chico no
baja_grande = atp.presupuesto_cuadratura({"sesgo": 0.03, "viento": 0.03,
                                          "ruido": 0.02, "latencia": 0.04})
baja_chico = atp.presupuesto_cuadratura({"sesgo": 0.03, "viento": 0.05,
                                         "ruido": 0.0, "latencia": 0.04})
check("bajar el viento 0.05->0.03 lleva el total a 0.061",
      cerca(baja_grande["total"], 0.061, 0.02), f"{baja_grande['total']:.5f}")
check("anular el ruido apenas mueve el total (0.070)",
      cerca(baja_chico["total"], 0.070, 0.02), f"{baja_chico['total']:.5f}")

inc = atp.incertidumbre_percentil(500, 0.95)
check("N=500: sd = 4.9 corridas", cerca(inc["corridas_sd"], 4.87, 0.02),
      f"{inc['corridas_sd']:.3f}")
check("N=500: ~1 punto percentil", cerca(inc["puntos_percentil"], 0.97, 0.05),
      f"{inc['puntos_percentil']:.3f}")
inc2 = atp.incertidumbre_percentil(2000, 0.95)
check("N=2000: 9.7 corridas, ~0.5 puntos",
      cerca(inc2["corridas_sd"], 9.75, 0.02)
      and cerca(inc2["puntos_percentil"], 0.487, 0.05),
      f"{inc2['corridas_sd']:.2f} corridas, "
      f"{inc2['puntos_percentil']:.3f} puntos")
check("cuadruplicar N solo duplica la confianza",
      cerca(inc["puntos_percentil"] / inc2["puntos_percentil"], 2.0, 0.02),
      f"{inc['puntos_percentil'] / inc2['puntos_percentil']:.4f}x")

print()
print("--- la poblacion de pases (lam_min uniforme, NO el_max uniforme) ---")
elm = atp.elmax_aleatorio(20000, rng=np.random.default_rng(1))
for q in (10, 25, 50, 75, 90, 99):
    print(f"    p{q:<3d} el_max = {np.percentile(elm, q):6.2f} grados")
check("la mediana de el_max ronda 22 grados (pases altos RAROS)",
      15.0 < float(np.percentile(elm, 50)) < 30.0,
      f"p50 = {np.percentile(elm, 50):.2f}")
check("menos del 15 % de los pases pasa de 68 grados",
      float(np.mean(elm > 68.0)) < 0.15,
      f"{np.mean(elm > 68.0) * 100:.1f} %")

camp = atp.campana_montecarlo(500)
print(f"  N=500  p50={camp['p50']:.4f}  p95={camp['p95']:.4f}  "
      f"peor={camp['peor']:.4f}  pasa={camp['pasa']}")
check("p50 del orden de 0.04 grados", 0.02 < camp["p50"] < 0.07,
      f"{camp['p50']:.4f}")
check("p95 del orden de 0.1 grados (el criterio de aceptacion)",
      0.06 < camp["p95"] < 0.16, f"{camp['p95']:.4f}")
check("la campaña es reproducible con la misma semilla",
      np.array_equal(atp.campana_montecarlo(500)["rms"], camp["rms"]),
      "mismo array bit a bit")
check("otra semilla da otro resultado",
      not np.array_equal(atp.campana_montecarlo(500, semilla=99)["rms"],
                         camp["rms"]), "como debe ser")
check("la distribucion tiene cola a la derecha (p95 > p50)",
      camp["p95"] > camp["p50"] * 1.5,
      f"p95/p50 = {camp['p95'] / camp['p50']:.2f}")
check("el peor caso supera al p95", camp["peor"] > camp["p95"],
      f"{camp['peor']:.4f} > {camp['p95']:.4f}")

hd = atp.histograma_datos(camp["rms"])
check("histograma: la barra mas alta esta normalizada a 1",
      cerca(float(np.max(hd["alturas"])), 1.0, 1e-9),
      f"{np.max(hd['alturas']):.4f}")
check("histograma: el conteo suma N",
      int(np.sum(hd["conteo"])) == 500, f"{int(np.sum(hd['conteo']))}")

print()
print("=" * 70)
print("L3.3 - por que 0.1 grados")
print("=" * 70)

th_s = atp.ancho_haz(3.0, 2.2e9)
check("plato 3 m banda S -> 3.18 grados", cerca(th_s, 3.18, 0.02),
      f"{th_s:.4f}")
th_ka = atp.ancho_haz(3.0, 30e9)
check("plato 3 m banda Ka -> 0.233 grados", cerca(th_ka, 0.233, 0.02),
      f"{th_ka:.5f}")

# coherencia de la formula de perdida: a media anchura da 3 dB exactos
l_media = atp.perdida_apuntamiento(th_s / 2.0, th_s)
check("coherencia: a theta3/2 la perdida es 3 dB", cerca(l_media, 3.0, 1e-9),
      f"{l_media:.6f} dB")

l_s = atp.perdida_apuntamiento(0.1, th_s)
check("0.1 grados en banda S = 0.012 dB", cerca(l_s, 0.012, 0.05),
      f"{l_s:.5f} dB")
l_ka = atp.perdida_apuntamiento(0.1, th_ka)
check("0.1 grados en banda Ka = 2.2 dB", cerca(l_ka, 2.2, 0.03),
      f"{l_ka:.4f} dB")
check("el mismo error cuesta ~180x mas en Ka", cerca(l_ka / l_s, 186, 0.1),
      f"{l_ka / l_s:.0f}x")
# la dependencia cuadratica
check("duplicar el error cuadruplica la perdida",
      cerca(atp.perdida_apuntamiento(0.2, th_s) / l_s, 4.0, 1e-9),
      f"{atp.perdida_apuntamiento(0.2, th_s) / l_s:.4f}x")

g = atp.ganancia_plato(3.0, 2.2e9, 0.6)
check("ganancia plato 3 m banda S = 34.6 dBi", cerca(g, 34.6, 0.01),
      f"{g:.3f} dBi")
gt = atp.g_sobre_t(3.0, 2.2e9, 0.6, 150.0)
check("G/T = 12.8 dB/K", cerca(gt, 12.8, 0.02), f"{gt:.3f} dB/K")

d10 = float(atp.rango_oblicuo(550, 10))
check("rango a 10 grados = 1815 km", cerca(d10, 1815, 0.02), f"{d10:.1f} km")
f10 = atp.fspl_db(d10, 2.2)
check("FSPL a 10 grados = 164.5 dB", cerca(f10, 164.5, 0.01), f"{f10:.2f} dB")
f90 = atp.fspl_db(550, 2.2)
check("FSPL en el cenit = 154.1 dB", cerca(f90, 154.1, 0.01), f"{f90:.2f} dB")
check("10.4 dB de diferencia solo por geometria",
      cerca(f10 - f90, 10.4, 0.03), f"{f10 - f90:.2f} dB")

pb = atp.presupuesto_cn0()
for k in ("eirp_dbw", "fspl_db", "perdidas_db", "l_point_db", "g_t_db",
          "cn0_dbhz"):
    print(f"  {k:<14s} {pb[k]:9.3f}")
check("C/N0 = 82.9 dB-Hz", cerca(pb["cn0_dbhz"], 82.9, 0.01),
      f"{pb['cn0_dbhz']:.3f}")
ebn0 = atp.eb_n0(pb["cn0_dbhz"], 1e6)
check("Eb/N0 a 1 Mbps = 22.9 dB", cerca(ebn0, 22.9, 0.01), f"{ebn0:.3f} dB")
check("el enlace cierra sobre QPSK (10.5 dB)", ebn0 > 10.5,
      f"margen {ebn0 - 10.5:.1f} dB")

comp = atp.comparar_bandas()
for f in comp:
    print(f"  {f['nombre']:<12s} theta3={f['theta3_deg']:7.4f} deg  "
          f"perdida={f['perdida_db']:7.4f} dB  "
          f"el error es {f['razon_haz'] * 100:5.1f} % del haz")

ea = atp.error_admisible(0.1, th_ka)
check("en Ka, admitir 0.1 dB exige ~0.02 grados", cerca(ea, 0.021, 0.1),
      f"{ea:.5f} grados")

print()
print("=" * 70)
if fallos:
    print(f"FALLARON {len(fallos)}:")
    for f in fallos:
        print(f"   - {f}")
    sys.exit(1)
print("TODO OK: la libreria dice lo que el curso fuente dice.")
