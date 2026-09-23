#!/usr/bin/env python3
"""Invariantes de `tesis6g.py`. Se corre ANTES de escribir una pieza.

    python3 studio/tools/traer_datos_tesis.py        # una vez, en el host
    docker run --rm --network none --user $(id -u):$(id -g) \\
        -v "$PWD":/workspace -w /workspace \\
        codeaerospace_contenido-manim python3 studio/tools/sonda_tesis6g.py

Lo que se prueba es lo que un dibujo no delata: que la construccion de
holgura no acotada da EXACTAMENTE MA = m-1 con MA_dec = 0 (y que la
formula cerrada de la variante con perdida es la optima, por fuerza bruta
sobre TODAS las politicas descentralizadas deterministas), que la maldicion
del ganador deprime el MA y desaparece con una sola politica, que las cifras
de la tesis se leen coherentes entre si (la mejora de G2b cabe bajo el MA de
G1, como exige el Corolario 4.7.2), que la paleta se lee sobre los dos
fondos, y que el guardian de etiquetas ABORTA con una frase.
"""
import itertools
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]
                       / "content" / "manim_extensions"))
import presentacion  # noqa: E402
import tesis6g as T6  # noqa: E402

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
print("\n== 01 - Paleta sobre los dos fondos ==")
for fondo in (T6.FONDO_OSCURO, T6.FONDO_CLARO):
    pal = T6.Paleta.de(fondo)
    c = pal.contrastes()
    peor = min(c[k] for k in T6.ROLES_TEXTO)
    ok(f"fondo {fondo}: todo rol con texto >= 4.5:1", peor >= 4.5,
       ", ".join(f"{k} {c[k]}" for k in T6.ROLES_TEXTO))
    ok(f"fondo {fondo}: se clasifica {'claro' if fondo == T6.FONDO_CLARO else 'oscuro'}",
       pal.es_claro == (fondo == T6.FONDO_CLARO))

    def rgb(h):
        h = h.lstrip("#")
        return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)
    # Estatica, adaptativa y privilegiada conviven en casi todas las piezas:
    # tienen que distinguirse entre si, no solo contra el fondo.
    trio = [pal.estatica, pal.adapta, pal.priv]
    dmin = min(np.linalg.norm(rgb(a) - rgb(b)) for a, b in itertools.combinations(trio, 2))
    ok(f"fondo {fondo}: estatica/adapta/priv separadas (dist RGB >= 90)", dmin >= 90,
       f"{dmin:.0f}")
# Contraejemplo: el azul original del deck NO se lee sobre el navy (por eso
# la variante oscura lo aclara). Si esto pasara, la variante sobraria.
ok("contraejemplo: azul del deck sobre navy < 4.5:1",
   presentacion.contraste(T6.DECK["azul"], T6.FONDO_OSCURO) < 4.5,
   f"{presentacion.contraste(T6.DECK['azul'], T6.FONDO_OSCURO):.2f}")

# =============================================================================
print("\n== 02 - Juego de coordinacion: holgura sin cota ==")
for m in range(2, 11):
    j = T6.juego_coordinacion(m)
    ok(f"m={m}: MA = m-1 y MA_dec = 0 exactos",
       abs(j["MA"] - (m - 1)) < 1e-12 and abs(j["MA_dec"]) < 1e-12,
       f"MA {j['MA']:.3f}")
for m in (3, 5, 8):
    ok(f"m={m}: eps=0 (ven todo) da MA_dec = MA",
       abs(T6.juego_coordinacion_obs(m, 0.0)["MA_dec"] - (m - 1)) < 1e-12)
    ok(f"m={m}: eps=1 (no ven nada) da MA_dec = 0",
       abs(T6.juego_coordinacion_obs(m, 1.0)["MA_dec"]) < 1e-12)
    eps = np.linspace(0, 1, 11)
    serie = [T6.juego_coordinacion_obs(m, e)["MA_dec"] for e in eps]
    ok(f"m={m}: MA_dec baja monotona con eps y nunca pasa de MA",
       all(a >= b for a, b in zip(serie, serie[1:])) and max(serie) <= m - 1 + 1e-12)


def valor_exacto(m, eps, p1, p2):
    """Valor esperado de un par de politicas deterministas. p[i] es la
    accion al observar s=i, p[m] la accion al no observar nada."""
    v = 0.0
    for s in range(m):
        for ve1, q1 in ((True, 1 - eps), (False, eps)):
            for ve2, q2 in ((True, 1 - eps), (False, eps)):
                a1 = p1[s] if ve1 else p1[m]
                a2 = p2[s] if ve2 else p2[m]
                v += (1 / m) * q1 * q2 * (a1 == s and a2 == s)
    return v


m, eps = 3, 0.3
politicas = list(itertools.product(range(m), repeat=m + 1))
mejor = max(valor_exacto(m, eps, p1, p2) for p1 in politicas for p2 in politicas)
casi(f"fuerza bruta ({len(politicas) ** 2} pares, m=3, eps=0.3): la formula es la optima",
     mejor, T6.juego_coordinacion_obs(m, eps)["V_dec"], 1e-12)
mejor0 = max(valor_exacto(m, 1.0, p1, p2) for p1 in politicas for p2 in politicas)
casi("fuerza bruta sin observacion: ninguna politica supera a la estatica",
     mejor0, 1 / m, 1e-12)

for m, eps in ((4, 0.0), (4, 0.25), (6, 0.5)):
    s = T6.simular_juego(m, eps, pasos=400_000, semilla=42)
    x = T6.juego_coordinacion_obs(m, eps)
    # 4 sigmas de cada estimador por separado (el MA es un cociente de dos)
    p = x["V_dec"]
    casi(f"Monte Carlo m={m} eps={eps}: V_dec simulado = cerrado", s["V_dec"], p,
         4 * np.sqrt(p * (1 - p) / 400_000) + 1e-12)
    casi(f"Monte Carlo m={m} eps={eps}: V_est simulado = 1/m", s["V_est"], 1 / m,
         4 * np.sqrt((1 / m) * (1 - 1 / m) / 400_000))

# =============================================================================
print("\n== 03 - Maldicion del ganador ==")
rng = np.random.default_rng(7)
valores = 100 + rng.normal(0, 3, 27)
oraculo = 130.0
res = [T6.maldicion_ganador(valores, sigma=12.0, episodios=e, v_oraculo=oraculo)
       for e in (1, 5, 10, 30, 300)]
ok("el maximo muestral sobreestima (sesgo > 0) con pocos episodios",
   res[0]["sesgo"] > 0.5, f"{res[0]['sesgo']:.2f}")
ok("el sesgo baja al crecer los episodios",
   all(a["sesgo"] > b["sesgo"] for a, b in zip(res, res[1:])),
   " > ".join(f"{r['sesgo']:.2f}" for r in res))
ok("el MA estimado sale por DEBAJO del verdadero (conservador)",
   all(r["MA_est"] < r["MA"] for r in res))
ok("el MA estimado sube hacia el verdadero",
   all(a["MA_est"] < b["MA_est"] for a, b in zip(res, res[1:])))
uno = T6.maldicion_ganador([100.0], sigma=12.0, episodios=1, v_oraculo=oraculo,
                           repeticiones=40_000)
ok("contraejemplo: con UNA sola politica no hay sesgo de seleccion",
   abs(uno["sesgo"]) < 0.2, f"{uno['sesgo']:.3f}")

# =============================================================================
print("\n== 04 - Cifras de la tesis, leidas y coherentes ==")
try:
    D = T6.datos_tesis()
except FileNotFoundError as e:
    D = None
    ok("datos de la tesis presentes", False, str(e))
if D:
    ok("G1: la media de las tres semillas redondea al 0.318 de GATES.md",
       f"{D['g1_ma']:.3f}" == [c for c in D["compuertas"] if c["id"] == "G1"][0]["valor"].split("=")[-1].strip(),
       f"{D['g1_ma']:.4f}")
    ok("umbral leido = 0.25", D["umbral"] == 0.25, str(D["umbral"]))
    ok("G0 por debajo del umbral y G1 por encima (control negativo y valido)",
       D["g0_ma"] < D["umbral"] < D["g1_ma"], f"{D['g0_ma']} / {D['g1_ma']:.3f}")
    for g in D["g2b"]:
        casi(f"G2b semilla {g['semilla']}: mejora = (qmix - estatica)/estatica",
             g["mejora"], (g["qmix"] - g["estatica"]) / g["estatica"], 1e-9)
        casi(f"G2b semilla {g['semilla']}: fraccion del oraculo = qmix/oraculo",
             g["frac_oraculo"], g["qmix"] / g["oraculo"], 1e-9)
        ok(f"G2b semilla {g['semilla']}: estatica < qmix < oraculo",
           g["estatica"] < g["qmix"] < g["oraculo"])
        ok(f"G2b semilla {g['semilla']}: la mejora cabe bajo el MA de G1 (Cor. 4.7.2)",
           g["mejora"] <= D["g1_ma"], f"{g['mejora']:.3f} <= {D['g1_ma']:.3f}")
    mej = [g["mejora"] for g in D["g2b"]]
    ok("G2b: rango 9.5 %-16.3 % como en GATES.md",
       f"{100 * min(mej):.1f}" == "9.5" and f"{100 * max(mej):.1f}" == "16.3",
       f"{100 * min(mej):.2f} - {100 * max(mej):.2f}")
    for s, r in D["piloto_mock"].items():
        orc = [g["oraculo"] for g in D["g2b"] if g["semilla"] == s][0]
        ok(f"piloto mock semilla {s}: > 1.05 x oraculo (R5 lo invalida)",
           r > 1.05 * orc, f"{r / orc:.2f} x")
    sens = sorted(D["sensibilidad"])
    ok("sensibilidad: el MA sube con los episodios (1/5/10/30)",
       all(a[1] < b[1] for a, b in zip(sens, sens[1:])),
       " < ".join(f"{e}:{v:.3f}" for e, v in sens))
    ok("sensibilidad: con 1 episodio el MA cae bajo el umbral (por eso G1 usa 30)",
       sens[0][1] < D["umbral"] < sens[-1][1])
    ok("compuertas: G3 y G4 pendientes (nada se dibuja como corrido)",
       all(c["estado"] == "pending" for c in D["compuertas"] if c["id"] in ("G3", "G4")))
    ev = [v for v in D["vdn"] if v["encontrada"]]
    ok("VDN: donde hay politica, supera a la estatica (gate y heldout)",
       all(v["gate"] > 0 and v["heldout"] > 0 for v in ev),
       ", ".join(f"{v['semilla']}:{v['gate']:.3f}/{v['heldout']:.3f}" for v in ev)
       + f"  ({len(ev)}/{len(D['vdn'])} semillas con politica)")

    for h in D["heuristica"]:
        ok(f"G-H semilla {h['semilla']}: ingenua < estatica < afinada (el rival importa)",
           h["ingenua"] < h["estatica"] < h["afinada"],
           f"{h['ingenua']:.0f} < {h['estatica']:.0f} < {h['afinada']:.0f}")
        casi(f"G-H semilla {h['semilla']}: la estatica de G-H es la de G1/G2b",
             h["estatica"], [g["estatica"] for g in D["g2b"] if g["semilla"] == h["semilla"]][0], 1.0)

# =============================================================================
print("\n== 05 - Guardian de etiquetas ==")
pal = T6.Paleta.de(T6.FONDO_OSCURO)
try:
    T6.etiqueta("Mejor politica estatica", pal)
    ok("3 palabras pasan", True)
except T6.LetraProhibida:
    ok("3 palabras pasan", False)
try:
    T6.etiqueta("La red no esta siempre ahi", pal)
    ok("contraejemplo: una frase de 6 palabras ABORTA", False, "no aborto")
except T6.LetraProhibida:
    ok("contraejemplo: una frase de 6 palabras ABORTA", True)
import manimpango  # noqa: E402
T6.registrar_fuentes()
ok("Carlito registrada en Pango", "Carlito" in manimpango.list_fonts())

# =============================================================================
print("\n== 06 - Pase LEO de la pieza ventana ==")
import ntn  # noqa: E402
p = ntn.pase_leo(600.0, 53.0, lat_gs=19.43, lon_gs=-99.13)
ok("pase casi cenital (elevacion maxima > 85 grados)", p["elev_max_deg"] > 85,
   f"{p['elev_max_deg']:.2f} grados, {p['duracion_s'] / 60:.2f} min")
per = 2 * np.pi * np.sqrt((ntn.R_TIERRA_KM + 600.0) ** 3 / ntn.MU_TIERRA)
lam = np.degrees(np.arccos(ntn.R_TIERRA_KM * np.cos(np.radians(10)) / (ntn.R_TIERRA_KM + 600)) ) - 10
ok("la duracion cenital cae cerca de la geometria sin rotacion terrestre (+-10 %)",
   abs(p["duracion_s"] - per * 2 * lam / 360) / (per * 2 * lam / 360) < 0.10,
   f"geometria {per * 2 * lam / 360 / 60:.2f} min, semiangulo {lam:.2f} grados")

# =============================================================================
print("\n== 07 - Mecanica de NTNEnv-v2 reproducida ==")
E = T6.entorno_v2()
ok("YAML: 3 agentes, eclipse 0.35, factor 0.10, pico 35 %",
   E["agentes"] == 3 and E["eclipse_umbral"] == 0.35 and E["eclipse_factor"] == 0.10
   and abs(E["gw_capacidad_pico"] - 0.35) < 1e-9)
v = T6.visibilidad_v2(60 * 200, E)
fr = float((v < E["eclipse_umbral"]).mean())
# LA MALLA DECIDE: el entorno avanza 6 grados por paso. sin(6k) < -0.3 para
# 6k entre 197.46 y 342.54 grados -> k = 33..57: 25 de 60 pasos. La formula
# continua (pi - 2 asin 0.3)/2pi = 40.3 % NO es lo que vive el entorno.
k_ecl = [k for k in range(60) if 197.4576 < 6 * k < 342.5424]
casi("eclipse: 25 de 60 pasos (41.7 %), no el 40.3 % continuo", fr, len(k_ecl) / 60, 1e-9)
ok("contraejemplo: la formula continua NO coincide con el entorno discreto",
   abs(fr - (np.pi - 2 * np.arcsin(0.3)) / (2 * np.pi)) > 0.01)
ok("visibilidad en [0, 1] y periodo de 60 pasos",
   v.min() >= 0 and v.max() <= 1 and np.allclose(v[:, :60], v[:, 60:120]))
ambos = float(((v < E["eclipse_umbral"]).all(axis=0)).mean())
ok("los dos satelites a la vez en eclipse MENOS que uno solo", ambos < fr, f"{ambos:.3f} < {fr:.3f}")
cg = T6.congestion_v2(45 * 100, E)
# pico = pasos k con k < 0.3*45 = 13.5 -> 14 de 45 (31.1 %), no 30 %
casi("congestion sin jitter: 14 de 45 pasos (31.1 %)", cg.mean(), 14 / 45, 1e-9)
cj = T6.congestion_v2(45 * 400, E, semilla=42)
casi("congestion con jitter: ~30 % (el inicio fraccionario reparte el paso extra)",
     cj.mean(), 0.30, 5e-3)
cd = T6.canal_degradado_v2(320, E)
ok("canal degradado rota cada 80 pasos", (cd[:80] == 0).all() and (cd[80:160] == 1).all())
i = T6.interferencia_v2(np.r_[np.ones(10), np.zeros(10)], E)
ok("interferencia satura en 1 usando el canal degradado", abs(i[9] - 1.0) < 1e-9, f"{i[9]:.3f}")
casi("y decae como 0.7^t al dejarlo", i[14], 1.0 * 0.7 ** 5, 1e-9)

# =============================================================================
print("\n== 08 - Creer sin ver y el coste de descentralizar ==")
ok("estado de 10 y observacion de 6, como el YAML", len(T6.ESTADO_V2) == E["dim_estado"]
   and len(T6.OBS_V2) == E["dim_obs"])
ok("el canal degradado esta en el estado y en NINGUNA observacion",
   "canal degradado" in T6.ESTADO_V2 and "canal degradado" not in T6.OBS_V2)
canal = T6.canal_degradado_v2(480, E)
y, b = T6.creencia_canal(T6.interferencia_v2(canal == 0, E))
acierta = float(((b > 0.5) == (canal == 0)).mean())
ok("la creencia sigue al estado oculto > 90 % del tiempo", acierta > 0.9, f"{acierta:.3f}")
_, b_ciego = T6.creencia_canal(T6.interferencia_v2(canal == 0, E), acierto=0.5)
ok("contraejemplo: con observacion sin informacion la creencia no sale de 0.5",
   np.allclose(b_ciego, 0.5), f"{b_ciego.min():.3f}-{b_ciego.max():.3f}")
casi("politicas conjuntas a horizonte 1: 3^3 = 27", 10 ** T6.log10_politicas_dec(3, 3, 2, 1), 27, 1e-6)
casi("a horizonte 2: cada agente 3 nodos -> 3^9 conjuntas", 10 ** T6.log10_politicas_dec(3, 3, 2, 2), 3 ** 9, 1e-3)

# =============================================================================
print("\n== 09 - Aprender por refuerzo (juguete) ==")
q = T6.q_juguete()
ok("Q aprende: visible -> espectro alto, eclipse -> ruta alterna",
   int(q["Q"][-1][0].argmax()) == 1 and int(q["Q"][-1][1].argmax()) == 2,
   f"{np.round(q['Q'][-1], 1).tolist()}")
ok("la mejor estatica del juguete es la ruta alterna (como la [2,2,2] de la tesis)",
   q["estatica"] == 2)
casi("MA del juguete = (p_v*80 + p_e*70)/70 - 1", q["MA"],
     (q["p"][0] * 80 + q["p"][1] * 70) / 70 - 1, 1e-9)
ok("contraejemplo: sin exploracion (eps=0) Q se queda en la primera accion",
   int(T6.q_juguete(eps=0.0)["Q"][-1][0].argmax()) != 1)
C = T6.curva_entrenamiento()
ok("curva de G2b: 5000 episodios con eps 0.999 -> 0.05", C["episodios"] == 5000
   and C["eps_decay"] == 0.999 and C["eps_min"] == 0.05)
ok("la media final supera a la estatica de la semilla 42",
   C["media"][-1] > D["g2b"][0]["estatica"], f"{C['media'][-1]:.0f} > {D['g2b'][0]['estatica']:.0f}")
k = T6.pasos_hasta_eps(0.05, 0.999)
casi("eps llega a 0.05 en ln(0.05)/ln(0.999) episodios", k, 2995, 1)

# =============================================================================
print("\n== 10 - Muchos agentes ==")
ind, con = T6.coordinacion_estadistica(400)
ok("independientes tardan mas en coordinarse que el conjunto (mediana, 400 semillas)",
   np.median(ind) > np.median(con), f"{np.median(ind):.0f} > {np.median(con):.0f}")
ok("y en la cola (p90) tambien", np.percentile(ind, 90) > np.percentile(con, 90),
   f"{np.percentile(ind, 90):.0f} > {np.percentile(con, 90):.0f}")
a, c = T6.aprendices_independientes(semilla=89)
ok("la semilla del clip (89) es de la mediana", T6.pasos_para_coordinar(c) == int(np.median(
   T6.coordinacion_estadistica(1000)[0])), str(T6.pasos_para_coordinar(c)))
g = np.linspace(-1, 1, 41)
Q1g, Q2g = np.meshgrid(g, g, indexing="ij")
for t in ("vdn", "qmix"):
    M = T6.mezcla(Q1g, Q2g, t)
    ok(f"{t}: Q_tot monotona en Q1 y en Q2", (np.diff(M, axis=0) >= -1e-12).all()
       and (np.diff(M, axis=1) >= -1e-12).all())
M = T6.mezcla(Q1g, Q2g, "roto")
ok("contraejemplo: el mezclador 'roto' NO es monotono", (np.diff(M, axis=0) < 0).any())
rng = np.random.default_rng(1)
fallos_igm = {t: 0 for t in ("vdn", "qmix", "roto")}
for _ in range(500):
    Q1, Q2 = rng.uniform(-1, 1, 3), rng.uniform(-1, 1, 3)
    for t in fallos_igm:
        fallos_igm[t] += not T6.igm(Q1, Q2, t)[0]
ok("IGM: vdn y qmix aciertan siempre el maximo conjunto (500 casos)",
   fallos_igm["vdn"] == 0 and fallos_igm["qmix"] == 0, str(fallos_igm))
ok("contraejemplo: el roto falla IGM en algun caso", fallos_igm["roto"] > 0, str(fallos_igm["roto"]))
V = T6.vdn_contra_qmix()
ok("VDN y QMIX superan a la estatica en las 3 semillas", all(v["vdn"] > v["estatica"] and
   v["qmix"] > v["estatica"] for v in V))
ok("y ninguno pasa del oraculo (R5 sin disparar)", all(max(v["vdn"], v["qmix"]) <= 1.05 * v["oraculo"]
   for v in V))

# =============================================================================
print("\n== 11 - Consenso ==")
import ntn as _ntn
q4, q6, q7 = (_ntn.quorum_pbft(n) for n in (4, 6, 7))
ok("n=6 tolera lo mismo que n=4 (f=1); n=7 sube a f=2", q4["f"] == q6["f"] == 1 and q7["f"] == 2)
ok("con n=6 el quorum es 4, no 2f+1 = 3", q6["quorum"] == 4 and q6["quorum_2f1"] == 3)
# interseccion de dos quorums: 2q - n >= f + 1 (al menos un honesto en comun)
for n in range(4, 30):
    q = _ntn.quorum_pbft(n)
    if 2 * q["quorum"] - n < q["f"] + 1:
        ok(f"interseccion de quorums n={n}", False)
        break
else:
    ok("para n = 4..29 dos quorums comparten >= f+1 replicas", True)
ok("contraejemplo: con n=6 y quorum 2f+1=3 dos quorums pueden no compartir nada",
   2 * 3 - 6 < 1 + 1)
g = T6.mensajes_por_grupos(1000, 10)
ok("1000 satelites en grupos de 10: ahorro > 99 %", g["ahorro"] > 0.99,
   f"{g['plano']} -> {g['grupos']} ({100 * g['ahorro']:.2f} %)")
g1 = T6.mensajes_por_grupos(10, 10)
ok("contraejemplo: con un solo grupo no hay ahorro (solo el mensaje de propagacion)",
   g1["grupos"] == g1["plano"] + 1)

# =============================================================================
print("\n== 12 - Cuello de botella de informacion ==")
b = np.linspace(0, 8, 400)
cg = T6.cuello_gaussiano(b, 0.9)
ok("IB gaussiano: sube con los bits enviados y empieza en 0", abs(cg[0]) < 1e-12 and (np.diff(cg) > 0).all())
casi("satura en I(X;Y) = -1/2 log2(1 - rho^2)", cg[-1], T6.info_mutua_gauss(0.9), 1e-4)
ok("nunca conserva mas de lo que envia (desigualdad de procesamiento)", (cg <= b + 1e-12).all())
ok("contraejemplo: con rho = 0 no hay nada relevante que conservar",
   np.allclose(T6.cuello_gaussiano(b, 0.0), 0.0))

# =============================================================================
print("\n== 13 - Medir sin enganarse ==")
si = T6.semillas_invierten()
ok("dos algoritmos identicos: 5 semillas y 10 discrepan en ~1/5 de los casos",
   0.15 < si["p_inversion"] < 0.30, f"{si['p_inversion']:.3f}")
ok("el ejemplo dibujado se invierte de verdad", si["a"][:5].mean() > si["b"][:5].mean()
   and si["a"].mean() < si["b"].mean())
k2 = T6.oraculo_k2()
ok("k=2 gana a k=1 en las tres semillas (el voraz NO es el techo)",
   all(p["k2"] > p["k1"] for p in k2["por_semilla"]),
   ", ".join(f"{100 * p['ganancia']:.2f} %" for p in k2["por_semilla"]))
ok("y la ganancia es < 1 %: el voraz es una cota inferior ajustada",
   all(p["ganancia"] < 0.01 for p in k2["por_semilla"]))
ok("la correccion transferida a G1 no la acerca al umbral (factor >= 4)",
   k2["correccion_G1"]["factor_min"] >= 4)

print(f"\n{n_ok} ok, {len(fallos)} fallos")
for f in fallos:
    print("  -", f)
sys.exit(1 if fallos else 0)
