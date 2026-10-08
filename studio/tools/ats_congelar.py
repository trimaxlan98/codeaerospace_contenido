#!/usr/bin/env python3
"""Congela en este repo los datos de la Estación ATP (ros2-workspace) que usan los reels de la serie «Estación ATP».

Los reels NO leen el otro proyecto al renderizar: leen `studio/content/datos_ats/ats_muestra.json`, que este script arma
(solo lectura sobre ros2-workspace, sin ejecutar ROS ni gastar CPU) y que lleva la procedencia de cada bloque
(archivo, fecha, commit del workspace). Regla de la casa de la Estación: toda cifra en pantalla sale de un archivo.

Uso:  python3 studio/tools/ats_congelar.py [ruta/a/ros2-workspace]
"""
import hashlib
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
WS = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO.parent / "ros2-workspace"
SALIDA = REPO / "studio/content/datos_ats/ats_muestra.json"

SERIES = ("t", "az", "el", "ref_az", "ref_el", "e_pt", "e_az", "e_el", "doppler_hz", "margin_db", "range_km")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()[:12]


def commit():
    try:
        return subprocess.check_output(["git", "-C", str(WS), "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        return "desconocido"


def pase(nombre):
    ruta = WS / "contenido/datasets" / f"{nombre}.json"
    d = json.loads(ruta.read_text(encoding="utf-8"))
    m = d["metricas"]
    return {"fuente": f"contenido/datasets/{nombre}.json", "sha256": sha(ruta), "experimento": d["params"]["experiment_id"],
            "argumentos": d["params"]["args"], "metricas": {"pointing": m["pointing"], "axes": m["axes"], "duration_s": m["duration_s"],
                                                           "link": m["link"], "verdict": m.get("verdict")},
            "series": {k: d["series"][k] for k in SERIES if k in d["series"]}}


def tabla_c():
    ruta = WS / "docs/pnt_resultados/tabla_C.json"
    filas = json.loads(ruta.read_text(encoding="utf-8"))
    return {"fuente": "docs/pnt_resultados/tabla_C.json", "sha256": sha(ruta),
            "filas": [{"grupo": f["grupo"], "efemeride": f["efemeride"], "cep50_m": f["mc"]["cep50_m"], "r95_m": f["mc"]["r95_m"]} for f in filas]}


def keyhole_mpc():
    ruta = WS / "docs/mpc_resultados/keyhole.json"
    d = json.loads(ruta.read_text(encoding="utf-8"))
    claves = ("pid_ingenua", "lqr_kf_ingenua", "pid_anticipada", "mpc", "mpc_horizonte_2s", "mpc_q_int_bajo")
    return {"fuente": "docs/mpc_resultados/keyhole.json", "sha256": sha(ruta),
            "celdas": {k: {x: d[k][x] for x in ("max_deg", "rms_deg", "p95_deg", "fuera_s") if x in d[k]}
                       for k in d if k.split("|", 1)[1] in claves for _ in [0]}}


def main():
    out = {"congelado": date.today().isoformat(), "workspace_commit": commit(),
           "nota": "Simulación de la Estación ATP (ROS 2 Jazzy, SGP4 con TLE reales de CelesTrak). Nada es medida con hardware.",
           "pases": {n: pase(n) for n in ("demo-pase", "demo-n5a", "demo-n5b", "demo-n2")},
           "pnt_tabla_C": tabla_c(), "keyhole_mpc": keyhole_mpc()}
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{SALIDA.relative_to(REPO)}  {SALIDA.stat().st_size / 1e3:.0f} kB  (workspace {out['workspace_commit']})")


if __name__ == "__main__":
    main()
