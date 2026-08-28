"""Sonda del curso 28 (satelites verticales): exige a cada funcion nueva de satelites.py que
devuelva un numero, y lo contrasta contra algo que se sepa por otro lado.

Un fallo aqui es una cifra que habria salido en pantalla siendo mentira.
"""
import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")
import numpy as np
import satelites as sa

fallos = []


def check(nombre, ok, detalle=""):
    print(f"{'OK  ' if ok else 'FALLA'} {nombre}: {detalle}")
    if not ok:
        fallos.append(nombre)


print("=" * 66)
print("M1 - caerse sin llegar al suelo")
print("=" * 66)

for h in (400, 550, 2000, 20200, 35786):
    p = sa.periodo_orbital(h)
    print(f"  h={h:6d} km  v={p['velocidad_km_s']:.3f} km/s  "
          f"T={p['minutos']:8.2f} min = {p['horas']:.3f} h")

# GEO tiene que dar el dia sidereo (23h56m4s = 86164 s), no 24 h.
geo = sa.periodo_orbital(35786)
check("GEO = dia sidereo", abs(geo["segundos"] - 86164.0) < 60.0,
      f"{geo['segundos']:.1f} s vs 86164 s")
# GPS a 20200 km: 11 h 58 min (media orbita sideral)
gps = sa.periodo_orbital(20200)
check("GPS = medio dia sidereo", abs(gps["segundos"] - 86164.0 / 2) < 120.0,
      f"{gps['segundos']:.1f} s vs {86164/2:.1f} s")
# 3a de Kepler: T^2/a^3 constante
a1 = sa.periodo_orbital(550); a2 = sa.periodo_orbital(20200)
k1 = a1["segundos"]**2 / a1["radio_km"]**3
k2 = a2["segundos"]**2 / a2["radio_km"]**3
check("3a de Kepler constante", abs(k1 - k2) / k1 < 1e-12,
      f"{k1:.6e} vs {k2:.6e}")

c = sa.caida_vs_curvatura(400.0, 1.0)
print(f"  a 400 km: v={c['velocidad_km_s']:.3f} km/s, en 1 s recorre "
      f"{c['distancia_km']:.3f} km, cae {c['caida_m']:.3f} m y el suelo "
      f"se hunde {c['curvatura_m']:.3f} m")
check("caida == curvatura (ESO es la orbita)",
      abs(c["caida_m"] - c["curvatura_m"]) / c["caida_m"] < 0.02,
      f"{c['caida_m']:.3f} m vs {c['curvatura_m']:.3f} m")

v_orb = sa.velocidad_circular(300.0)
lento = sa.canon_newton(v_orb * 0.7, 300.0)
justo = sa.canon_newton(v_orb, 300.0)
rapido = sa.canon_newton(v_orb * 1.15, 300.0)
print(f"  canon a 300 km (v circular = {v_orb:.3f} km/s):")
for nom, r in (("70%", lento), ("100%", justo), ("115%", rapido)):
    print(f"    v={nom:>5}: impacto={r['impacto']}, vueltas={r['vueltas']:.3f}, "
          f"r_min={r['r_min_km']:.0f} km, r_max={r['r_max_km']:.0f} km")
check("disparo lento CAE", lento["impacto"], f"{lento['alcance_grados']:.1f} grados")
check("disparo circular NO cae", not justo["impacto"], "da la vuelta")
check("orbita circular se mantiene redonda",
      (justo["r_max_km"] - justo["r_min_km"]) < 5.0,
      f"r entre {justo['r_min_km']:.1f} y {justo['r_max_km']:.1f} km")
check("disparo rapido sube (elipse)", not rapido["impacto"]
      and rapido["r_max_km"] > justo["r_max_km"] + 500,
      f"apogeo {rapido['r_max_km'] - sa.R_TIERRA_KM:.0f} km")

ar = sa.areas_barridas(a_km=sa.R_TIERRA_KM + 12000.0, e=0.65)
print(f"  elipse e=0.65: v_peri={ar['v_perigeo_km_s']:.3f} km/s, "
      f"v_apo={ar['v_apogeo_km_s']:.3f} km/s")
print(f"    area perigeo={ar['area_perigeo_km2']:.4e} km2, "
      f"apogeo={ar['area_apogeo_km2']:.4e} km2")
check("2a de Kepler: areas iguales",
      abs(ar["cociente_areas"] - 1.0) < 0.01,
      f"cociente {ar['cociente_areas']:.4f}")
check("cociente de rapideces = (1+e)/(1-e)",
      abs(ar["cociente_v"] - ar["cociente_v_teorico"]) < 1e-6,
      f"{ar['cociente_v']:.4f} vs {ar['cociente_v_teorico']:.4f}")

print()
print("=" * 66)
print("M2 - la Tierra gira debajo")
print("=" * 66)

for h in (550, 780, 35786):
    r = sa.radio_huella_km(h, 10.0)
    f = sa.fraccion_visible(h, 10.0)
    print(f"  h={h:6d} km: psi={sa.angulo_cobertura(h,10.0):5.2f} grados, "
          f"huella r={r:7.1f} km, ve el {100*f:5.2f}% de la Tierra")
check("uno a 550 km ve poco", 0.01 < sa.fraccion_visible(550, 10) < 0.03,
      f"{100*sa.fraccion_visible(550,10):.2f}%")
# Con elevacion util (10 grados) GEO ve ~1/3 de la Tierra: de ahi el "con
# tres GEO se cubre el mundo menos los polos". Con elevacion 0 la geometria
# da 42.4%, que tiende a 50% (media esfera) desde infinito: las dos cifras
# son correctas y dicen cosas distintas.
check("GEO ve ~1/3 con elevacion util",
      0.32 < sa.fraccion_visible(35786, 10.0) < 0.36,
      f"{100*sa.fraccion_visible(35786,10.0):.2f}% a 10 grados")
check("GEO con horizonte rasante: 42% y nunca medio planeta",
      0.42 < sa.fraccion_visible(35786, 0.0) < 0.50,
      f"{100*sa.fraccion_visible(35786,0.0):.2f}%")

co = sa.corrimiento_traza(550.0)
print(f"  a 550 km: T={co['periodo_min']:.2f} min, la traza se corre "
      f"{co['grados_por_vuelta']:.2f} grados = {co['km_ecuador']:.0f} km "
      f"por vuelta; {co['vueltas_por_dia']:.2f} vueltas al dia")
check("corrimiento coherente con el periodo",
      abs(co["grados_por_vuelta"] * co["vueltas_por_dia"] - 360.0) < 1.0,
      f"{co['grados_por_vuelta'] * co['vueltas_por_dia']:.2f} grados/dia")

p = sa.pase(19.43, -99.13, 550.0, 53.0, 10.0)      # Ciudad de Mexico
print(f"  pase sobre CDMX: dura {p['duracion_min']:.2f} min, "
      f"elevacion maxima {p['el_max_deg']:.1f} grados")
check("un pase LEO dura entre 3 y 15 min",
      3.0 < p["duracion_min"] < 15.0, f"{p['duracion_min']:.2f} min")
check("la elevacion maxima es alta en el mejor pase",
      p["el_max_deg"] > 45.0, f"{p['el_max_deg']:.1f} grados")
i, j, k = p["indices"]
az = p["azimut"]
print(f"    azimut: entra por {az[i]:.0f}, culmina en {az[k]:.0f}, "
      f"sale por {az[j]:.0f} grados; el pase es el "
      f"{100*p['fraccion_del_periodo']:.1f}% de la orbita")
check("el satelite entra y sale por lados opuestos del cielo",
      abs(((az[j] - az[i] + 180) % 360) - 180) > 90.0,
      f"{az[i]:.0f} -> {az[j]:.0f}")
check("azimut en rango", float(az.min()) >= 0.0 and float(az.max()) < 360.0,
      f"[{az.min():.1f}, {az.max():.1f}]")

print()
print("=" * 66)
print("M3 - por eso son muchos")
print("=" * 66)

cfg = [(1, 1), (2, 3), (4, 6), (6, 11), (12, 20)]
res = sa.cobertura_vs_n(cfg, 550.0, 10.0, 53.0, res=(360, 180), instantes=6)
for r in res:
    print(f"  N={r['n']:4d} ({r['planos']}x{r['por_plano']}): "
          f"cubre {100*r['fraccion']:6.2f}% "
          f"[{100*r['fraccion_min']:.2f}-{100*r['fraccion_max']:.2f}]")
check("la cobertura crece con N",
      all(res[i]["fraccion"] <= res[i+1]["fraccion"] + 1e-9
          for i in range(len(res) - 1)),
      "monotona")
uno = sa.fraccion_visible(550, 10.0)
check("N=1 medido == formula de la esfera",
      abs(res[0]["fraccion"] - uno) / uno < 0.05,
      f"medido {100*res[0]['fraccion']:.3f}% vs formula {100*uno:.3f}%")

lm = sa.latitud_maxima_cubierta(53.0, 550.0, 10.0)
print(f"  inclinacion 53 grados: llega hasta {lm['lat_max_deg']:.1f} grados "
      f"de latitud; cubre polo = {lm['cubre_polo']}")
check("53 grados NO cubre los polos", not lm["cubre_polo"],
      f"lat max {lm['lat_max_deg']:.1f}")
check("86 grados (Iridium) SI cubre los polos",
      sa.latitud_maxima_cubierta(86.4, 780.0, 10.0)["cubre_polo"], "")

rel = sa.relevos(19.43, -99.13, planos=6, por_plano=11, elevacion_min_deg=25.0)
print(f"  {rel['n_satelites']} satelites sobre CDMX: {rel['relevos']} relevos "
      f"en {rel['duracion_s']/60:.0f} min "
      f"(uno cada {rel['intervalo_medio_s']/60:.2f} min); "
      f"sin servicio el {100*rel['fraccion_sin_servicio']:.1f}% del tiempo")
check("hay relevos", rel["relevos"] > 0, f"{rel['relevos']}")

lonlat = sa.subsatelites_walker(2, 18, 12, 53.0, 550.0, vueltas=0.0)[0]
lon_ny, lat_ny = -74.0, 40.7
lon_ld, lat_ld = -0.1, 51.5
try:
    ruta = sa.ruta_malla((lon_ny, lat_ny), (lon_ld, lat_ld), lonlat, 550.0,
                         elevacion_min_deg=20.0, isl_max_km=5000.0)
    fib = sa.latencia_fibra((lon_ny, lat_ny), (lon_ld, lat_ld))
    print(f"  Nueva York -> Londres: gran circulo {fib['gran_circulo_km']:.0f} km")
    print(f"    por la malla: {ruta['saltos']} saltos, {ruta['km']:.0f} km, "
          f"{ruta['latencia_ms']:.2f} ms")
    print(f"    por fibra:    {fib['km']:.0f} km, {fib['latencia_ms']:.2f} ms "
          f"(rodeo {fib['rodeo']}x, {fib['fraccion_c']:.2f}c) [SUPUESTO]")
    check("el camino por la malla es mas largo que el gran circulo",
          ruta["km"] > fib["gran_circulo_km"],
          f"{ruta['km']:.0f} > {fib['gran_circulo_km']:.0f} km")
    check("y aun asi llega antes que la fibra",
          ruta["latencia_ms"] < fib["latencia_ms"],
          f"{ruta['latencia_ms']:.2f} ms vs {fib['latencia_ms']:.2f} ms")
except ValueError as e:
    check("ruta por la malla", False, str(e))

for d, f in ((550, 12.0), (35786, 12.0)):
    print(f"  FSPL a {d:6d} km en {f} GHz: {sa.fspl_db(d, f):.2f} dB")
dif = sa.fspl_db(35786, 12.0) - sa.fspl_db(550, 12.0)
check("GEO pierde ~36 dB mas que LEO", 35.0 < dif < 37.0,
      f"{dif:.2f} dB = {10**(dif/10):.0f} veces")

print()
print("=" * 66)
print("M4 - la red que se gobierna sola")
print("=" * 66)

mar = sa.tiempo_sobre_mar(planos=12, por_plano=10, instantes=32)
print(f"  el enjambre pasa el {100*mar['fraccion_mar']:.1f}% del tiempo "
      f"sobre agua ({mar['muestras']} muestras)")
check("mayoria del tiempo sobre agua", mar["fraccion_mar"] > 0.6,
      f"{100*mar['fraccion_mar']:.1f}%")

dem = sa.demanda_por_celda(res=(96, 48), semilla=11)
psi = sa.angulo_cobertura(550.0, 10.0)
ll = sa.subsatelites_walker(2, 12, 10, 53.0, 550.0, vueltas=0.0)[0]
cont = sa.conteo_cobertura((96, 48), ll, psi)
fijo = sa.asignar_haces(cont, dem, 8, modo="fijo")
apre = sa.asignar_haces(cont, dem, 8, modo="aprendido")
opt = sa.asignar_haces(cont, dem, 8, modo="demanda")
print(f"  demanda servida: fijo {100*fijo['servida']:.2f}% -> aprendido "
      f"{100*apre['servida']:.2f}% (techo {100*opt['servida']:.2f}%) "
      f"en {apre.get('pasos', 0)} pasos")
check("el aprendido mejora al fijo", apre["servida"] > fijo["servida"] * 1.2,
      f"x{apre['servida']/fijo['servida']:.2f}")
check("el aprendido no supera el techo",
      apre["servida"] <= opt["servida"] + 1e-9,
      f"{apre['servida']:.4f} <= {opt['servida']:.4f}")
check("la curva de aprendizaje sube siempre",
      all(np.diff(apre["curva"]) >= -1e-12), f"{len(apre['curva'])} puntos")

for lat, lon, nom in ((19.43, -99.13, "CDMX"), (78.2, 15.6, "Svalbard")):
    s = sa.sobre_el_horizonte(lat, lon, planos=24, por_plano=10,
                              altitud_km=550.0, inclinacion_deg=53.0)
    print(f"  sobre {nom:9s}: {s['n_visibles']:3d} de {s['n_total']} "
          f"satelites por encima de 10 grados")
cdmx = sa.sobre_el_horizonte(19.43, -99.13, planos=24, por_plano=10)
svb = sa.sobre_el_horizonte(78.2, 15.6, planos=24, por_plano=10)
check("desde CDMX se ven varios", cdmx["n_visibles"] > 0,
      f"{cdmx['n_visibles']}")
check("desde Svalbard (78N) se ven menos que en CDMX",
      svb["n_visibles"] < cdmx["n_visibles"],
      f"{svb['n_visibles']} vs {cdmx['n_visibles']}")
check("la cuenta cuadra con la fraccion visible",
      abs(cdmx["n_visibles"] / cdmx["n_total"]
          - sa.fraccion_visible(550, 10)) < 0.03,
      f"{cdmx['n_visibles']}/{cdmx['n_total']} = "
      f"{cdmx['n_visibles']/cdmx['n_total']:.4f} vs "
      f"{sa.fraccion_visible(550,10):.4f}")

print()
print("=" * 66)
print(f"RESULTADO: {len(fallos)} fallos")
for f in fallos:
    print(f"  - {f}")
print("=" * 66)
sys.exit(1 if fallos else 0)
