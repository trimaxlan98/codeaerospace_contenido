#!/usr/bin/env python3
"""Copia los resultados de la tesis 6G que dibujan las piezas y el curso 36.

El repo de la tesis es PRIVADO y tiene licencia restrictiva; este repo es
PUBLICO. Por eso los JSON no se versionan: se copian a
`studio/content/datos/tesis-6g-privado/` (gitignored) y lo unico versionado
es esta herramienta, que deja la copia reproducible en esta maquina.

    python3 studio/tools/traer_datos_tesis.py [--tesis RUTA]

Ademas de copiar, escribe:
  - compuertas.json : el estado G0-G4 leido de 05_PROGRESO/GATES.md (fuente
                      unica de los veredictos en la tesis), sin reinterpretar.
  - procedencia.json: commit de la tesis, ruta de origen y sha256 de cada
                      fichero, para que una cifra en pantalla se pueda
                      rastrear hasta su archivo.
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DESTINO = RAIZ / "studio/content/datos/tesis-6g-privado"
TESIS = Path("/home/alanrosasp/Claude/tesis-doctorado-6g")

# destino -> origen (relativo a la raiz de la tesis)
FICHEROS = {
    "g2b_v7.json": "03_IMPLEMENTACION/results/gates/G2B_RECUALIFICACION_v7.json",
    "g2b_piloto_mock.json": "03_IMPLEMENTACION/results/gates/G2B_PILOTO_GPU_v2.json",
    "g2b_vdn.json": "03_IMPLEMENTACION/results/gates/G2B_ADAPTIVE_arm3_vdn.json",
    "g1_42.json": "03_IMPLEMENTACION/results/g1_ntnenv_v2/g1_result_42.json",
    "g1_43.json": "03_IMPLEMENTACION/results/g1_ntnenv_v2/g1_result_43.json",
    "g1_44.json": "03_IMPLEMENTACION/results/g1_ntnenv_v2/g1_result_44.json",
    "ma_sensibilidad.json": "03_IMPLEMENTACION/mvp3_qmix/results/teoria/MA_SENSIBILIDAD.json",
    "oraculo_k2.json": "03_IMPLEMENTACION/mvp3_qmix/results/teoria/ORACULO_K2_VS_K1.json",
    "entorno_v2.yaml": "03_IMPLEMENTACION/mvp3_qmix/configs/env_v2_dynamic.yaml",
    "gh_heuristica.json": "03_IMPLEMENTACION/results/gates/G-H_HEURISTICA_v1.json",
    "historia_g2b_42.json": "03_IMPLEMENTACION/mvp3_qmix/results/fase0_g2b/fase0_g2b_backup/history_seed42.json",
    "historia_vdn_42.json": "03_IMPLEMENTACION/mvp3_qmix/results/fase0_g2b_arm3_vdn/history_seed42.json",
    "historia_g2b_43.json": "03_IMPLEMENTACION/mvp3_qmix/results/fase0_g2b/fase0_g2b_backup/history_seed43.json",
    "historia_vdn_43.json": "03_IMPLEMENTACION/mvp3_qmix/results/fase0_g2b_arm3_vdn/history_seed43.json",
    "historia_g2b_44.json": "03_IMPLEMENTACION/mvp3_qmix/results/fase0_g2b/fase0_g2b_backup/history_seed44.json",
    "historia_vdn_44.json": "03_IMPLEMENTACION/mvp3_qmix/results/fase0_g2b_arm3_vdn/history_seed44.json",
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def leer_compuertas(gates_md: Path) -> list[dict]:
    """Parsea el formato fijo de GATES.md: `## ID · Nombre` + `- clave: valor`."""
    salida, actual = [], None
    for linea in gates_md.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^## (\S+) · (.+)$", linea)
        if m:
            actual = {"id": m.group(1), "nombre": m.group(2).strip()}
            salida.append(actual)
            continue
        m = re.match(r"^- (\w+): (.*)$", linea)
        if m and actual is not None:
            actual[m.group(1)] = m.group(2).strip()
    return salida


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tesis", type=Path, default=TESIS)
    a = ap.parse_args()
    if not (a.tesis / "05_PROGRESO/GATES.md").exists():
        print(f"no encuentro la tesis en {a.tesis}", file=sys.stderr)
        return 1
    DESTINO.mkdir(parents=True, exist_ok=True)
    commit = subprocess.run(["git", "-C", str(a.tesis), "rev-parse", "--short", "HEAD"],
                            capture_output=True, text=True).stdout.strip()
    proc = {"tesis_commit": commit, "ficheros": {}}
    for dst, org in FICHEROS.items():
        src = a.tesis / org
        shutil.copy2(src, DESTINO / dst)
        proc["ficheros"][dst] = {"origen": org, "sha256_16": sha(src)}
    comp = leer_compuertas(a.tesis / "05_PROGRESO/GATES.md")
    (DESTINO / "compuertas.json").write_text(
        json.dumps(comp, ensure_ascii=False, indent=1), encoding="utf-8")
    proc["ficheros"]["compuertas.json"] = {"origen": "05_PROGRESO/GATES.md",
                                           "sha256_16": sha(a.tesis / "05_PROGRESO/GATES.md")}
    (DESTINO / "procedencia.json").write_text(
        json.dumps(proc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(FICHEROS) + 1} ficheros en {DESTINO} (tesis @ {commit})")
    for c in comp:
        print(f"  {c['id']:4s} {c.get('estado', '?'):8s} {c.get('valor', '')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
