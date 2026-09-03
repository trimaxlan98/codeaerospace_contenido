#!/usr/bin/env python3
"""Invariantes de `ntn.py`. Se corre ANTES de escribir una figura de la tesis.

    docker run --rm --network none --user $(id -u):$(id -g) \\
        -v "$PWD":/workspace -w /workspace \\
        codeaerospace_contenido-manim python3 studio/tools/sonda_ntn.py

Una geometria orbital mal implementada NO se ve mal: dibuja una campana de
elevacion muy convincente y saca una cifra plausible. Un quorum mal contado
tampoco: 6 replicas «parecen» tolerar mas que 4. Asi que cada propiedad se
demuestra aqui con una prueba que solo pasa si esta bien y, cuando existe, con
su CONTRAEJEMPLO: una prueba de quorum que no distinga n=6 de n=7 no esta
probando nada, y un gate que no falle cuando el intervalo cruza el umbral es
un sello de goma.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]
                       / "content" / "manim_extensions"))
import ntn  # noqa: E402

fallos = []
n_ok = 0


def ok(nombre, condicion, detalle=""):
    global n_ok
    if condicion:
        n_ok += 1
        print(f"  ok   {nombre}" + (f"   [{detalle}]" if detalle else ""))
    else:
        fallos.append(nombre)
        print(f"  FALLO {nombre}   {detalle}")


def casi(nombre, a, b, tol, unidad=""):
    ok(nombre, abs(float(a) - float(b)) <= tol,
       f"{float(a):.6g} vs {float(b):.6g} {unidad}".strip())


# =============================================================================
print("\n== 01 - Presupuesto de enlace ==")
# El valor exacto se calcula aqui, no se copia: 20log10(4 pi d f / c).
d, f = 600.0, 2.0
exacto = 20 * np.log10(4 * np.pi * (d * 1e3) * (f * 1e9) / 299792458.0)
casi("FSPL a 600 km y 2 GHz sale la formula exacta", ntn.fspl_exacto_db(d, f),
     exacto, 1e-9, "dB")
casi("y la del curso (92.45) coincide con ella", ntn.fspl_db(d, f), exacto,
     0.005, "dB")
delta = float(ntn.fspl_db(d, f) - ntn.fspl_exacto_db(d, f))
ok("el redondeo del 92.45 vale menos de 0.01 dB", abs(delta) < 0.01,
   f"{delta:.5f} dB de mas")
casi("doblar la distancia cuesta 6.02 dB",
     float(ntn.fspl_db(2 * d, f) - ntn.fspl_db(d, f)), 20 * np.log10(2), 1e-9,
     "dB")
casi("doblar la frecuencia cuesta lo mismo",
     float(ntn.fspl_db(d, 2 * f) - ntn.fspl_db(d, f)), 20 * np.log10(2), 1e-9,
     "dB")
fspl_600_2 = float(ntn.fspl_db(d, f))

print("\n== 02 - Retardo: distancia partido por c ==")
casi("un segundo luz son 299792.458 km",
     ntn.retardo_ida_ms(ntn.C_LUZ_KM_S), 1000.0, 1e-9, "ms")
casi("600 km de vertical son 2.0014 ms de ida",
     ntn.retardo_ida_ms(600.0), 600.0 / 299792.458 * 1e3, 1e-12, "ms")
ok("el retardo es lineal con la distancia",
   abs(float(ntn.retardo_ida_ms(2000.0)) - 2 * float(ntn.retardo_ida_ms(1000.0)))
   < 1e-12)

print("\n== 03 - Geometria: distancia oblicua y su inversa ==")
h = 600.0
horizonte = ntn.distancia_horizonte_km(h)
casi("en el cenit la distancia ES la altura",
     ntn.distancia_oblicua_km(90.0, h), h, 1e-9, "km")
casi("a elevacion cero, la del horizonte",
     ntn.distancia_oblicua_km(0.0, h), horizonte, 1e-9, "km")
casi("el horizonte a 600 km son 2829.35 km", horizonte, 2829.3462, 1e-3, "km")
for e in (5.0, 10.0, 30.0, 60.0, 89.0):
    dd = ntn.distancia_oblicua_km(e, h)
    casi(f"ida y vuelta de la formula a {e:.0f} grados",
         ntn.elevacion_de_distancia_deg(dd, h), e, 1e-9, "grados")
# CONTRAEJEMPLO: mas alla del horizonte la elevacion tiene que salir NEGATIVA
# (el satelite esta tras el limbo), y solo una distancia geometricamente
# imposible puede dar nan. Confundir las dos cosas es lo que haria pasar por
# «linea de vista» un retardo que no lo es.
ok("mas alla del horizonte la elevacion es negativa (contraejemplo)",
   float(ntn.elevacion_de_distancia_deg(horizonte * 1.2, h)) < 0.0,
   f"{float(ntn.elevacion_de_distancia_deg(horizonte * 1.2, h)):.2f} grados a "
   f"{horizonte * 1.2:.0f} km")
ok("...y dentro del horizonte, positiva",
   float(ntn.elevacion_de_distancia_deg(horizonte * 0.9, h)) > 0.0)
ok("una distancia menor que la altura si es imposible: nan",
   bool(np.isnan(ntn.elevacion_de_distancia_deg(h * 0.5, h))),
   f"{h * 0.5:.0f} km con el satelite a {h:.0f} km")

print("\n== 04 - El pase LEO ==")
pase = ntn.pase_leo(600.0, 53.0, lat_gs=19.43, lon_gs=-99.13)
ok("la elevacion nunca pasa de 90 grados",
   float(np.max(pase["elev_deg"])) <= 90.0 + 1e-9,
   f"maxima {pase['elev_max_deg']:.3f}")
ok("el TCA es a la vez la elevacion maxima y la distancia minima",
   int(np.argmax(pase["elev_deg"])) == int(np.argmin(pase["dist_km"])),
   f"indice {int(np.argmax(pase['elev_deg']))}")
casi("la distancia del TCA coincide con la de su elevacion",
     pase["dist_min_km"],
     ntn.distancia_oblicua_km(pase["elev_max_deg"], 600.0), 1e-6, "km")
ok("AOS y LOS estan en el umbral de elevacion",
   abs(float(pase["elev_deg"][0]) - pase["elev_min_deg"]) < 0.6
   and abs(float(pase["elev_deg"][-1]) - pase["elev_min_deg"]) < 0.6,
   f"{float(pase['elev_deg'][0]):.2f} y {float(pase['elev_deg'][-1]):.2f} grados")
ok("un pase de 600 km dura entre 5 y 12 minutos",
   300.0 < pase["duracion_s"] < 720.0, f"{pase['duracion_s']:.1f} s")

# Pase CENITAL: el unico caso con simetria exacta que se puede exigir.
cenital = ntn.pase_leo(600.0, 90.0, lat_gs=0.0, lon_gs=0.0)
casi("un pase cenital sube exactamente a 90 grados",
     cenital["elev_max_deg"], 90.0, 1e-3, "grados")
casi("y su distancia minima es la altura", cenital["dist_min_km"], 600.0,
     1e-2, "km")
tt, ee = cenital["t_s"], cenital["elev_deg"]
i_tca = int(np.argmax(ee))
n_lado = min(i_tca, len(ee) - 1 - i_tca)
ok("el TCA cae en medio del pase, no en un borde de la ventana",
   n_lado > 0.3 * len(ee),
   f"indice {i_tca} de {len(ee)}: {n_lado} muestras por el lado corto")
izq = ee[i_tca - n_lado:i_tca]
der = ee[i_tca + 1:i_tca + 1 + n_lado][::-1]
err_sim = float(np.max(np.abs(izq - der))) if n_lado > 4 else np.inf
ok("y es simetrico alrededor del TCA", err_sim < 0.35,
   f"{err_sim:.3f} grados de diferencia entre las dos alas")
# CONTRAEJEMPLO del propio guardian: una prueba de simetria que no sepa
# encontrar una asimetria no esta midiendo nada. Se le da un ala desplazada
# cuatro muestras y TIENE que fallar.
torcido = ee.copy()
torcido[i_tca + 1:] = np.roll(torcido[i_tca + 1:], 4)
err_torcido = float(np.max(np.abs(
    torcido[i_tca - n_lado:i_tca]
    - torcido[i_tca + 1:i_tca + 1 + n_lado][::-1])))
ok("y la prueba de simetria detecta un ala desplazada (contraejemplo)",
   err_torcido > 0.35, f"{err_torcido:.3f} grados con el ala corrida")
# Y el hallazgo medido: el pase oblicuo TAMBIEN sale casi simetrico. Los 2.2
# grados que gira la Tierra en los 530 s del pase apenas rompen la simetria de
# la elevacion (el que si se tuerce es el AZIMUT). Conviene tenerlo escrito
# para no «arreglar» una asimetria que la fisica no pide.
tt2, ee2 = pase["t_s"], pase["elev_deg"]
j = int(np.argmax(ee2))
m = min(j, len(ee2) - 1 - j)
asim = float(np.max(np.abs(ee2[j - m:j] - ee2[j + 1:j + 1 + m][::-1])))
ok("un pase oblicuo tambien sale casi simetrico en elevacion", asim < 0.35,
   f"{asim:.3f} grados entre las alas de un pase de "
   f"{pase['elev_max_deg']:.1f} grados")

print("\n== 05 - Doppler ==")
f_port = 2.0e9
r = ntn.resumen_doppler(pase, f_port)
df = r["df_hz"]
i_tca = int(np.argmin(np.abs(pase["t_s"] - pase["tca_s"])))
ok("acercandose el Doppler es positivo", float(df[2]) > 0,
   f"{float(df[0]) / 1e3:.2f} kHz en AOS")
ok("alejandose, negativo", float(df[-3]) < 0,
   f"{float(df[-1]) / 1e3:.2f} kHz en LOS")
ok("cambia de signo exactamente una vez",
   int(np.sum(np.diff(np.sign(df)) != 0)) == 1,
   f"{int(np.sum(np.diff(np.sign(df)) != 0))} cambios")
cruce = float(pase["t_s"][int(np.argmin(np.abs(df)))])
casi("y lo hace en el TCA", cruce, pase["tca_s"], 6.0, "s")
ok("en el TCA el corrimiento es despreciable",
   abs(float(df[i_tca])) < 0.02 * r["df_max_hz"],
   f"{abs(float(df[i_tca])):.1f} Hz frente a {r['df_max_hz']:.0f} Hz de pico")
ok("el maximo esta en AOS o en LOS, no en medio",
   min(int(np.argmax(np.abs(df))), len(df) - 1 - int(np.argmax(np.abs(df))))
   < 0.05 * len(df),
   f"indice {int(np.argmax(np.abs(df)))} de {len(df)}")
ok("y escala con la portadora",
   abs(float(ntn.resumen_doppler(pase, 2 * f_port)["df_max_hz"])
       - 2 * r["df_max_hz"]) < 1.0,
   f"{r['df_max_hz'] / 1e3:.2f} kHz a 2 GHz")
doppler_max_khz = r["df_max_hz"] / 1e3
ppm = r["ppm_max"]

print("\n== 06 - El escenario LEO-600 del banco de pruebas ==")
esc = ntn.escenario_leo600()
t0 = esc["ticks"][0]
ok("12.9 ms NO pueden ser de ida a 600 km (contraejemplo)",
   not t0["posible_si_ida"],
   f"serian {t0['d_si_ida_km']:.0f} km y el horizonte esta en "
   f"{esc['d_horizonte_km']:.0f} km")
ok("...pero si de ida y vuelta", t0["posible_si_rtt"],
   f"{t0['d_si_rtt_km']:.0f} km")
casi("y entonces la elevacion es la mascara de 10 grados",
     t0["elev_si_rtt_deg"], 10.0, 0.1, "grados")
ok("el tick central es el de mas elevacion",
   max(range(len(esc["ticks"])),
       key=lambda i: esc["ticks"][i]["elev_si_rtt_deg"]) == 4,
   f"{esc['ticks'][4]['elev_si_rtt_deg']:.2f} grados a 4.5 ms")
ok("todos los ticks son posibles leidos como ida y vuelta",
   all(t["posible_si_rtt"] for t in esc["ticks"]))
elev_tick0 = t0["elev_si_rtt_deg"]
elev_tick4 = esc["ticks"][4]["elev_si_rtt_deg"]

print("\n== 07 - Handover: la cascada ==")
casc = ntn.handover(4, solape=0.25)
casi("un tren solapado cubre el 100 % de su ventana", casc["cobertura"], 1.0,
     1e-9)
ok("sin huecos", casc["hueco_s"] == 0.0, f"{casc['hueco_s']:.2f} s")
ok("con n satelites hay n-1 relevos", len(casc["relevos_s"]) == 3,
   f"{len(casc['relevos_s'])} relevos")
ok("cada satelite del tren sirve un rato",
   all(dur > 0 for dur in casc["duracion_servicio_s"]),
   " ".join(f"{d:.0f}s" for d in casc["duracion_servicio_s"]))
ok("la Tierra gira debajo: los pases del tren no son iguales",
   float(casc["elev"][0].max()) - float(casc["elev"][-1].max()) > 5.0,
   f"{float(casc['elev'][0].max()):.1f} -> "
   f"{float(casc['elev'][-1].max()):.1f} grados de elevacion maxima")
# CONTRAEJEMPLO: con separacion mayor que la duracion del pase TIENE que
# aparecer hueco. Un detector de huecos que nunca encuentra ninguno no sirve.
flojo = ntn.handover(3, solape=-0.6)
ok("separando los pases aparece hueco (contraejemplo)",
   flojo["hueco_s"] > 0.0 and flojo["cobertura"] < 1.0,
   f"{flojo['hueco_s']:.1f} s sin servicio, cobertura "
   f"{flojo['cobertura'] * 100:.1f} %")
cobertura_pct = casc["cobertura"] * 100.0

print("\n== 08 - Quorum PBFT ==")
ok("n=4 tolera f=1", ntn.f_max(4) == 1)
ok("n=7 tolera f=2", ntn.f_max(7) == 2)
# EL CONTRAEJEMPLO del quorum: 6 replicas NO toleran mas que 4. La division es
# entera; escribir f = (n-1)/3 en coma flotante daria 1.67 y un quorum de 4.33.
ok("n=6 tolera f=1, lo mismo que n=4 (contraejemplo)", ntn.f_max(6) == 1,
   f"f_max(6) = {ntn.f_max(6)}, no {(6 - 1) / 3:.2f}")
ok("y le sobran dos replicas", ntn.quorum_pbft(6)["holgura"] == 2,
   f"n=6 necesita {ntn.quorum_pbft(6)['minimo_n']}")
ok("n=3 no tolera ningun bizantino", ntn.f_max(3) == 0)
for n in (4, 6, 7, 10, 31):
    q = ntn.quorum_pbft(n)
    ok(f"n={n}: n>=3f+1 y el quorum es ceil((n+f+1)/2)",
       n >= 3 * q["f"] + 1
       and q["quorum"] == -((-(n + q["f"] + 1)) // 2),
       f"f={q['f']} quorum={q['quorum']}")
    ok(f"n={n}: el quorum es mayoria estricta", 2 * q["quorum"] > n,
       f"{q['quorum']} de {n}")
    ok(f"n={n}: dos quorums comparten al menos f+1 replicas",
       2 * q["quorum"] - n >= q["f"] + 1,
       f"interseccion minima {2 * q['quorum'] - n}, f+1 = {q['f'] + 1}")
    ok(f"n={n}: el trafico total es 2n(n-1)",
       q["mensajes_total"] == 2 * n * (n - 1),
       f"{q['mensajes_total']} mensajes")
# EL CONTRAEJEMPLO de la formula del quorum: «2f+1» solo vale cuando la
# constelacion es justa (n = 3f+1). Con replicas de sobra se queda corto y dos
# quorums pueden no compartir ninguna replica correcta.
ok("2f+1 y la formula coinciden cuando n = 3f+1",
   all(ntn.quorum_pbft(n)["quorum"] == ntn.quorum_pbft(n)["quorum_2f1"]
       for n in (4, 7, 10, 13)))
q6 = ntn.quorum_pbft(6)
ok("con n=6 y f=1, 2f+1 NO es quorum valido (contraejemplo)",
   q6["quorum_2f1"] == 3 and q6["quorum"] == 4
   and 2 * q6["quorum_2f1"] - 6 < q6["f"] + 1,
   f"2f+1 = 3 dejaria interseccion {2 * 3 - 6}, hace falta {q6['f'] + 1}; "
   f"lo correcto es {q6['quorum']}")
ok("y crece cuadraticamente: de 4 a 8 replicas se multiplica por 4.7",
   abs(ntn.quorum_pbft(8)["mensajes_total"]
       / ntn.quorum_pbft(4)["mensajes_total"] - 112 / 24) < 1e-9,
   f"{ntn.quorum_pbft(4)['mensajes_total']} -> "
   f"{ntn.quorum_pbft(8)['mensajes_total']}")

print("\n== 09 - Margen adaptativo ==")
casi("con recompensas negativas, mejor oraculo da MA positivo",
     ntn.margen_adaptativo(-60.0, -80.0), 0.25, 1e-12)
# CONTRAEJEMPLO: sin el valor absoluto en el denominador el signo se invierte
# justo en el caso que interesa.
sin_abs = (-60.0 - (-80.0)) / (-80.0)
ok("sin |R_best| el signo se invertiria (contraejemplo)",
   sin_abs < 0 < float(ntn.margen_adaptativo(-60.0, -80.0)),
   f"{sin_abs:+.3f} contra {float(ntn.margen_adaptativo(-60.0, -80.0)):+.3f}")
casi("peor oraculo da MA negativo", ntn.margen_adaptativo(-90.0, -80.0),
     -0.125, 1e-12)
casi("con recompensas positivas funciona igual",
     ntn.margen_adaptativo(125.0, 100.0), 0.25, 1e-12)
casi("MA = 0 cuando empatan", ntn.margen_adaptativo(-80.0, -80.0), 0.0, 1e-12)
try:
    ntn.margen_adaptativo(1.0, 0.0)
    ok("MA con R_best = 0 tiene que fallar", False)
except ValueError as e:
    ok("MA con R_best = 0 falla y lo dice", "no esta definido" in str(e))

print("\n== 10 - Gates con IC95 % ==")
arriba = {42: [0.31, 0.29], 43: [0.27, 0.33], 44: [0.30, 0.28]}
g = ntn.gate(arriba, ntn.UMBRAL_MA, nombre="G3")
ok("un gate con todo el intervalo por encima PASA",
   g["pasa"] and g["veredicto"] == "pasa",
   f"IC [{g['ic_lo']:.3f}, {g['ic_hi']:.3f}] sobre {g['umbral']:.2f}")
# EL CONTRAEJEMPLO del gate: si el intervalo cruza el umbral, NO pasa aunque
# la media este por encima. Un gate que mire solo la media es un sello de goma.
cruza = {42: [0.26], 43: [0.20], 44: [0.30]}
gc = ntn.gate(cruza, ntn.UMBRAL_MA, nombre="G3-cruza")
ok("uno cuya media supera el umbral pero cuyo IC lo cruza NO pasa "
   "(contraejemplo)",
   gc["media"] > gc["umbral"] and not gc["pasa"]
   and gc["veredicto"] == "indeciso",
   f"media {gc['media']:.3f} pero IC [{gc['ic_lo']:.3f}, {gc['ic_hi']:.3f}]")
abajo = {42: [0.05], 43: [0.02], 44: [0.08]}
gb = ntn.gate(abajo, ntn.UMBRAL_MA)
ok("uno claramente por debajo dice 'no pasa'", gb["veredicto"] == "no pasa",
   f"IC [{gb['ic_lo']:.3f}, {gb['ic_hi']:.3f}]")
ok("el bootstrap es determinista con la misma semilla",
   ntn.gate(arriba, 0.25, semilla=7)["ic_lo"]
   == ntn.gate(arriba, 0.25, semilla=7)["ic_lo"])
ok("las tres semillas de la tesis se cuentan como tres",
   g["n_semillas"] == 3 and tuple(g["semillas"]) == ntn.SEMILLAS_TESIS)
# Con TRES semillas el bootstrap solo tiene C(5,3) = 10 remuestras distintas,
# asi que el IC esta cuantizado y dos semillas de bootstrap distintas dan el
# MISMO intervalo. No es un error: es el techo de resolucion de tres corridas,
# y por eso un gate al borde del umbral sale indeciso por construccion.
distintas = {tuple(sorted(c)) for c in
             [(a, b, c2) for a in range(3) for b in range(3) for c2 in range(3)]}
ok("con tres semillas el bootstrap solo tiene 10 remuestras distintas",
   len(distintas) == 10, f"{len(distintas)} combinaciones")
ok("y por eso dos semillas de bootstrap dan el mismo IC",
   ntn.gate(cruza, 0.25, semilla=7)["ic_lo"]
   == ntn.gate(cruza, 0.25, semilla=8)["ic_lo"])
ok("con doce semillas si cambia (el bootstrap no esta congelado)",
   ntn.gate({s_: [0.2 + 0.02 * s_] for s_ in range(12)}, 0.25,
            semilla=7)["ic_lo"]
   != ntn.gate({s_: [0.2 + 0.02 * s_] for s_ in range(12)}, 0.25,
               semilla=8)["ic_lo"])
# CONTRAEJEMPLO metodologico: remuestrear MUESTRAS sueltas en vez de SEMILLAS
# estrecha el intervalo hasta hacer PASAR un gate que es indeciso.
rng_dat = np.random.default_rng(11)
por_semilla = {s_: (media + 0.005 * rng_dat.standard_normal(8)).tolist()
               for s_, media in zip((42, 43, 44), (0.22, 0.27, 0.32))}
honesto = ntn.gate(por_semilla, 0.25)
planas = np.concatenate([np.asarray(v) for v in por_semilla.values()])
rng = np.random.default_rng(42)
por_muestra = rng.choice(planas, size=(10000, planas.size)).mean(axis=1)
lo_falso = float(np.quantile(por_muestra, 0.025))
ok("remuestrear muestras en vez de semillas estrecharia el IC hasta hacer "
   "PASAR un gate indeciso (contraejemplo metodologico)",
   lo_falso > ntn.UMBRAL_MA > honesto["ic_lo"] and not honesto["pasa"],
   f"IC honesto [{honesto['ic_lo']:.3f}, {honesto['ic_hi']:.3f}] "
   f"({honesto['veredicto']}) contra un limite inferior falso de "
   f"{lo_falso:.3f}")

print("\n== 11 - Banda IC punto a punto ==")
base = np.linspace(0.0, 1.0, 40)
series = np.stack([base + 0.02 * k for k in range(3)])
media, lo, hi = ntn.banda_ic_por_x(series)
ok("la media punto a punto es la media", np.allclose(media, series.mean(axis=0)))
ok("y la banda envuelve a la media", np.all(lo <= media + 1e-12)
   and np.all(hi >= media - 1e-12))
ok("la banda tiene el mismo largo que la serie", lo.shape == media.shape)

# =============================================================================
print("\n" + "=" * 68)
print("LAS CIFRAS QUE PUEDEN IR A UNA FIGURA")
print("=" * 68)
cifras = [
    ("FSPL a 600 km y 2 GHz", f"{fspl_600_2:.2f} dB"),
    ("error del 92.45 frente a la exacta", f"{delta:.4f} dB"),
    ("horizonte geometrico a 600 km", f"{horizonte:.2f} km"),
    ("elevacion maxima del pase (Mexico)",
     f"{pase['elev_max_deg']:.2f} grados"),
    ("duracion del pase", f"{pase['duracion_s']:.1f} s"),
    ("distancia en AOS / TCA",
     f"{pase['dist_aos_km']:.0f} / {pase['dist_min_km']:.0f} km"),
    ("retardo de ida en AOS / TCA",
     f"{float(ntn.retardo_ida_ms(pase['dist_aos_km'])):.2f} / "
     f"{float(ntn.retardo_ida_ms(pase['dist_min_km'])):.2f} ms"),
    ("Doppler de pico a 2 GHz", f"{doppler_max_khz:.2f} kHz"),
    ("...en partes por millon", f"{ppm:.2f} ppm"),
    ("tick 0 del banco leido como RTT", f"{elev_tick0:.2f} grados"),
    ("tick 4 del banco leido como RTT", f"{elev_tick4:.2f} grados"),
    ("cobertura del tren de 4 con solape 0.25", f"{cobertura_pct:.1f} %"),
    ("quorum PBFT n=7", f"f={ntn.quorum_pbft(7)['f']}, "
     f"quorum={ntn.quorum_pbft(7)['quorum']}, "
     f"{ntn.quorum_pbft(7)['mensajes_total']} mensajes"),
    ("quorum PBFT n=6 (2f+1 se queda corto)",
     f"f={q6['f']}, quorum={q6['quorum']} (2f+1 daria {q6['quorum_2f1']})"),
    ("MA del ejemplo (-60 contra -80)",
     f"{float(ntn.margen_adaptativo(-60.0, -80.0)):+.3f}"),
    ("gate indeciso (tres semillas)",
     f"media {gc['media']:.3f}, IC [{gc['ic_lo']:.3f}, {gc['ic_hi']:.3f}]"),
]
for k, v in cifras:
    print(f"  {k:<42} {v}")

print("\n" + "=" * 68)
print(f"{n_ok} invariantes ok, {len(fallos)} fallos")
if fallos:
    for f_ in fallos:
        print(f"  - {f_}")
sys.exit(1 if fallos else 0)
