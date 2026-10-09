#!/usr/bin/env python3
"""Verifica el entorno para los reels 2D (Manim) y 3D (motor3d con GPU): dependencias, fuentes, ffmpeg, GPU/EGL, texturas y un cuadro de prueba.

Úsalo igual en la Mac-Pro (Linux, sin GPU NVIDIA) y en la Estación (WSL2 con GPU): imprime un informe y sale con código 0 solo si lo
imprescindible está bien. No modifica nada salvo escribir un PNG de prueba en --salida (por defecto exports/estudio/_prueba3d/).

    python3 studio/tools/verificar_entorno_3d.py [--salida DIR] [--ros2 RUTA/ros2-workspace]
"""
import argparse
import importlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(REPO / "studio"), str(REPO / "studio/content/manim_extensions"), str(REPO / "animaciones")]
OK, MAL, AV = "✓", "✗", "!"


def linea(est, txt):
    print(f" {est} {txt}")
    return est == OK


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", default=str(REPO / "exports/estudio/_prueba3d"))
    ap.add_argument("--ros2", default=str(REPO.parent / "ros2-workspace"))
    a = ap.parse_args()
    graves = 0
    print(f"== Entorno ({sys.platform}, Python {sys.version.split()[0]}) · repo {REPO} ==")
    print("\n[Dependencias]")
    for mod, grave in (("numpy", True), ("scipy", True), ("PIL", True), ("manim", True), ("moderngl", False), ("sgp4", False)):
        try:
            m = importlib.import_module(mod)
            linea(OK, f"{mod} {getattr(m, '__version__', '')}")
        except Exception as e:
            graves += grave
            linea(MAL if grave else AV, f"{mod}: {type(e).__name__} ({'necesario' if grave else 'solo para 3D/datos orbitales'})")
    print("\n[Herramientas]")
    for exe, grave in (("ffmpeg", True), ("ffprobe", True), ("rclone", False)):
        ruta = shutil.which(exe)
        graves += (ruta is None) and grave
        linea(OK if ruta else (MAL if grave else AV), f"{exe}: {ruta or 'no está en el PATH'}")
    print("\n[Fuentes de los temas de reels]")
    try:
        sal = subprocess.run(["fc-list"], capture_output=True, text=True, timeout=30).stdout
        for f in ("Oxanium", "Barlow", "Red Hat Display", "Urbanist", "Lexend", "Rajdhani"):
            linea(OK if f in sal else AV, f"{f}" + ("" if f in sal else "  → python3 animaciones/instalar_fuentes.py"))
    except Exception:
        linea(AV, "fc-list no disponible (en Windows nativo instala las fuentes a mano; en WSL2 usa instalar_fuentes.py)")
    print("\n[GPU / motor3d]")
    gpu = None
    try:
        from motor3d import GPU
        gpu = GPU(320, 180, muestras=1)
        r = gpu.render
        soft = any(s in r.lower() for s in ("llvmpipe", "swrast", "software"))
        linea(AV if soft else OK, f"GL_RENDERER = {r}" + ("  ← POR SOFTWARE: sin GPU real (lento)" if soft else "  ← GPU real"))
    except Exception as e:
        linea(AV, f"no se pudo crear el contexto EGL ({type(e).__name__}: {str(e)[:90]}). Los reels 2D no lo necesitan; los 3D sí.")
    tex = REPO / "studio/assets/tierra"
    faltan = [n for n in ("world.topo.bathy.200412.3x5400x2700.jpg", "BlackMarble_2016_01deg.jpg", "cloud_combined_2048.jpg") if not (tex / n).exists()]
    linea(OK if not faltan else AV, "texturas de la Tierra" + ("" if not faltan else f" faltan: {faltan}"))
    if gpu is not None and not faltan:
        try:
            import numpy as np
            from PIL import Image
            from motor3d import Escena, Camara
            esc = Escena(gpu)
            Path(a.salida).mkdir(parents=True, exist_ok=True)
            cam = Camara(ojo=np.array([0.0, -3.2, 0.8]), objetivo=np.zeros(3), fov=40.0)
            gpu.empezar()
            esc.estrellas(cam)
            esc.tierra(cam, 0.0, np.array([1.0, 0.4, 0.3]))
            esc.atmosfera(cam, np.array([1.0, 0.4, 0.3]))
            Image.fromarray(gpu.terminar()).save(Path(a.salida) / "prueba_tierra.png")
            linea(OK, f"cuadro de prueba: {Path(a.salida) / 'prueba_tierra.png'}")
        except Exception as e:
            linea(AV, f"cuadro de prueba falló ({type(e).__name__}: {str(e)[:100]}); revisar a mano con motor3d")
    print("\n[ros2-workspace (datos del rover)]")
    ws = Path(a.ros2)
    linea(OK if ws.exists() else AV, f"{ws}" + ("" if ws.exists() else "  → clónalo junto a este repo para leer las corridas"))
    if ws.exists():
        try:
            sys.path.insert(0, str(ws / "src/atp_rover"))
            from atp_rover.terreno import Terreno
            t = Terreno("rocoso", 7)
            linea(OK, f"Terreno('rocoso', 7) altura(0,0) = {t.altura(0.0, 0.0):.3f} m")
        except Exception as e:
            linea(AV, f"no se pudo importar atp_rover.terreno ({type(e).__name__}: {str(e)[:80]})")
        runs = sorted(ws.glob("runs/*/telemetry.jsonl"))[-3:]
        linea(OK if runs else AV, f"corridas con telemetría: {len(list(ws.glob('runs/*/telemetry.jsonl')))}" + ("" if runs else "  (genera una con scripts/ o desde la app)"))
    print("\n[Carga]")
    try:
        print(f"   load average: {os.getloadavg()}")
    except Exception:
        pass
    print(f"\n== {'LISTO' if not graves else 'FALTAN COSAS NECESARIAS'} ({graves} graves) ==")
    return 1 if graves else 0


if __name__ == "__main__":
    sys.exit(main())
