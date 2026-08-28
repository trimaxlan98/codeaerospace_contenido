#!/usr/bin/env python3
"""Sonda del paquete `emergencia` (curso 29): las cifras, medidas EN el
contenedor que renderiza, contra lo que la fisica exige.

Corre `medir()` de cada simulador (sin frames: es rapido) y comprueba
invariantes que no dependen del gusto de nadie: conservacion, rangos,
periodos conocidos, que la cifra que el clip pondra en pantalla exista y
sea finita. Un simulador que no cumple NO entra en un clip.

    docker run --rm --network none --user $(id -u):$(id -g) \\
      -v <repo>:/workspace:ro codeaerospace_contenido-manim \\
      python3 /workspace/studio/tools/sonda_emergencia.py [--frames]

`--frames` corre ademas `simular()` completo de cada modulo y mide tiempo y
memoria de la pila (tarda: ~10-15 min en total).
"""
import argparse
import importlib
import sys
import time

sys.path.insert(0, "/workspace/studio/content/manim_extensions")
sys.path.insert(0, "studio/content/manim_extensions")

import numpy as np  # noqa: E402

FALLOS = []
OK = []


def check(cond, msg):
    (OK if cond else FALLOS).append(msg)
    print(("  ok   " if cond else "  FALLO") + " " + msg)


def finito(d, *claves):
    for k in claves:
        v = d.get(k)
        check(v is not None and np.all(np.isfinite(v)), f"{k} = {v}")


# Invariantes por modulo. Cada entrada: (modulo, funcion(cifras)).
def sonda_bandada(c):
    finito(c, "polarizacion_inicial", "polarizacion_final", "agentes")
    check(c["polarizacion_inicial"] < 0.3, "arranca desordenada (< 0.3)")
    check(c["polarizacion_final"] > 0.8, "acaba alineada (> 0.8)")
    check(c["agentes"] >= 2000, "al menos 2000 agentes")


def sonda_moho(c):
    finito(c, "red_vs_arbol")
    check(1.0 <= c["red_vs_arbol"] <= 3.0,
          "la red mide entre 1 y 3 veces el arbol minimo")


def sonda_arena(c):
    finito(c, "granos", "avalancha_mayor")
    check(c["granos"] >= 40_000, "al menos 40k granos (1M no cabe en 90 s: medido)")
    check(0 < c["avalancha_mayor"] <= c["granos"], "avalancha acotada")
    if "exponente" in c:
        check(-2.5 < c["exponente"] < -0.5, f"exponente {c['exponente']:.2f}")


def sonda_vida(c):
    finito(c, "periodo_canon_pasos", "planeadores_emitidos")
    check(c["periodo_canon_pasos"] == 30, "el cañon de Gosper tiene periodo 30")
    check(c["planeadores_emitidos"] >= 5, "emite al menos 5 planeadores")


def sonda_turing(c):
    for k in ("lambda_manchas_px", "lambda_rayas_px"):
        if k in c:
            check(2.0 < c[k] < 80.0, f"{k} = {c[k]:.1f} px razonable")
    if "n_manchas" in c:
        check(c["n_manchas"] >= 10, f"{c['n_manchas']} manchas")


def sonda_ondas(c):
    finito(c, "franjas_medido_px", "franjas_teorico_px")
    err = abs(c["franjas_medido_px"] - c["franjas_teorico_px"]) \
        / c["franjas_teorico_px"]
    check(err < 0.25, f"franjas medido vs teoria: {err * 100:.1f} %")


def sonda_chladni(c):
    fr = [v for k, v in c.items() if k.startswith("fraccion_nodal")]
    check(len(fr) >= 3 and all(f > 0.5 for f in fr),
          f"la arena se junta en las lineas nodales {fr}")


def sonda_ising(c):
    check(abs(c.get("Tc_literatura", 0) - 2.269) < 1e-3, "Tc declarada")
    check(c["M_abs_en_T3"] < 0.3, f"|M| a T=3 {c['M_abs_en_T3']:.2f} < 0.3")
    check(c["M_abs_final"] > 0.85, f"|M| final {c['M_abs_final']:.2f} > 0.85")
    check(1.8 < c["T_cruce_M_0_5"] < 2.7,
          f"cruce 0.5 a T={c['T_cruce_M_0_5']:.2f}")
    # con campo nulo el final es un sorteo: la semilla 1 decide (documentado)


def sonda_pendulos(c):
    finito(c, "t_separacion_1rad")
    check(0.5 < c["t_separacion_1rad"] < 30.0, "se separan dentro del clip")
    if "deriva_energia" in c:
        check(abs(c["deriva_energia"]) < 1e-3,
              f"energia conservada ({c['deriva_energia']:.2e})")


def sonda_cuencas(c):
    fr = [v for k, v in c.items() if k.startswith("fraccion_iman")]
    check(len(fr) == 3 and abs(sum(fr) - 1.0) < 0.02, f"tres cuencas {fr}")
    check(1.0 < c["dimension_frontera"] < 2.0,
          f"D frontera {c['dimension_frontera']:.3f}")


def sonda_epiciclos(c):
    finito(c, "n_para_1px")
    check(2 <= c["n_para_1px"] <= 1000, f"N para 1 px = {c['n_para_1px']}")


def sonda_rio(c):
    check(50 < c["reynolds"] < 400, f"Re = {c['reynolds']:.0f}")
    check(0.1 < c["strouhal_medido"] < 0.3,
          f"St = {c['strouhal_medido']:.3f} (lit. ~0.2)")


def sonda_galaxias(c):
    check(abs(c["deriva_energia_nucleos_pct"]) < 1.0,
          f"energia: deriva {c['deriva_energia_nucleos_pct']:.3e} %")
    finito(c, "distancia_minima")


SONDAS = {
    "bandada": sonda_bandada, "moho": sonda_moho, "arena": sonda_arena,
    "vida": sonda_vida, "turing": sonda_turing, "ondas": sonda_ondas,
    "chladni": sonda_chladni, "ising": sonda_ising,
    "pendulos": sonda_pendulos, "cuencas": sonda_cuencas,
    "epiciclos": sonda_epiciclos, "rio": sonda_rio, "galaxias": sonda_galaxias,
}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--frames", action="store_true")
    p.add_argument("--solo", action="append", default=[])
    args = p.parse_args()
    for nombre, sonda in SONDAS.items():
        if args.solo and nombre not in args.solo:
            continue
        print(f"\n== {nombre}")
        try:
            mod = importlib.import_module(f"emergencia.{nombre}")
        except Exception as e:  # noqa: BLE001
            check(False, f"no importa: {e}")
            continue
        t0 = time.time()
        try:
            cifras = mod.medir()
        except Exception as e:  # noqa: BLE001
            check(False, f"medir() revienta: {e}")
            continue
        print(f"  medir(): {time.time() - t0:.1f} s")
        for k, v in cifras.items():
            print(f"    {k} = {v}")
        try:
            sonda(cifras)
        except KeyError as e:
            check(False, f"falta la cifra {e}")
        if args.frames:
            t0 = time.time()
            r = mod.simular()
            f = r["frames"]
            print(f"  simular(): {time.time() - t0:.1f} s, pila {f.shape} "
                  f"{f.nbytes / 1e6:.0f} MB")
            check(f.dtype == np.uint8 and f.ndim == 4 and f.shape[-1] == 3,
                  "pila uint8 (T,H,W,3)")
            check(abs(f.shape[1] / f.shape[2] - 16 / 9) < 0.01, "9:16")
            check(f.nbytes <= 1_000_000_000, "≤ 1 GB")
            check(time.time() - t0 <= 120, "simular ≤ 120 s")
            del r, f
    print(f"\n{len(OK)} ok, {len(FALLOS)} fallos")
    for f in FALLOS:
        print("  FALLO:", f)
    return 1 if FALLOS else 0


if __name__ == "__main__":
    sys.exit(main())
