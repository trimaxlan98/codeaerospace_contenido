#!/usr/bin/env python3
"""Comprueba que un curso vertical esta listo para narrar y montar.

Se corre DESPUES de los renders qh y ANTES de mandar nada al VPS: cada
cosa que revisa aqui costo una vuelta entera en algun curso anterior.

    studio/backend/venv/bin/python studio/tools/verifica_vertical.py \
        studio/content/verticales/<slug>

Qué mira:

  - que exista el render de cada pieza, que sea vertical y que este a la
    resolucion y los fps que se esperan;
  - que `duracion_objetivo` coincida con la duracion REAL del render. La
    voz se alinea contra el manifiesto, asi que un manifiesto desfasado
    pone la voz encima del plano equivocado. El redondeo a frame de 60 fps
    no es el de 30: hay que re-comprobarlo DESPUES del qh, no solo en ql;
  - que las piezas de curso caigan en el rango de duracion;
  - que ninguna frase de voz empiece antes de que acabe la anterior, y que
    quede cola de silencio al final;
  - que el `fade_out` del audio caiga dentro de la pieza;
  - que los eventos de SFX existan en la paleta y no se salgan del final;
  - las COSTURAS: el ultimo frame de cada pieza contra el primero de la
    siguiente. En este estilo toda pieza empieza y termina en azul limpio,
    asi que la costura tiene que valer casi cero. No se da por supuesto: en
    el curso 28 el fundido final dejaba encendidas la marca de agua y las
    esquinas del HUD, la pieza siguiente las re-encendia de golpe, y habia
    un parpadeo en las catorce uniones que a ojo no se veia. Cuando la
    cifra de la costura se repite EXACTA en todas las uniones, el culpable
    es siempre el mismo objeto: es la pista mas util del chequeo.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "studio" / "tools"))

from render_vertical import (COLA_FINAL, SALIDA, cargar_curso,  # noqa: E402
                             datos_video)

# Charon lee a 1.2-1.7 palabras/s; 1.3 + 0.4 s de aire es la regla util
# que sale de medir tres cursos. Una frase de UNA palabra cuesta ~5.5 s
# porque el TTS le pone entrada y cola propias.
PALABRAS_POR_S = 1.3
AIRE_S = 0.4
COSTE_MINIMO_S = 5.0


# Suelo de la costura: el codec no devuelve el mismo azul bit a bit ni
# entre dos frames identicos. Medido en cursos anteriores, el ruido de
# compresion se queda por debajo de 1.0/255.
COSTURA_MAX = 1.0


def _frame(video: Path, destino: Path, primero: bool) -> Path:
    """Primer o ultimo frame REAL de un video.

    El ultimo se saca con `-sseof` y `-update 1`: un `-ss` al filo de la
    duracion sale con exito SIN escribir nada."""
    cmd = ["ffmpeg", "-nostdin", "-v", "error"]
    if primero:
        cmd += ["-i", str(video), "-frames:v", "1"]
    else:
        cmd += ["-sseof", f"-{COLA_FINAL}", "-i", str(video), "-update", "1"]
    subprocess.run(cmd + ["-y", str(destino)], check=True)
    return destino


def costuras(curso, slug, tmp: Path):
    """Diferencia media por canal entre el final de cada pieza y el
    principio de la siguiente, en unidades de 0-255."""
    # Solo PIL, y a proposito. Con `numpy` en la lista este bloque se
    # convirtio en un agujero silencioso: el venv del backend no lleva
    # numpy (no lo necesita, los renders van en el contenedor), asi que el
    # chequeo MAS util de la herramienta se saltaba solo imprimiendo una
    # linea entre parentesis y el resumen seguia diciendo "0 fallos". Un
    # guardian que se desactiva solo y da el visto bueno es peor que no
    # tenerlo. `ImageChops` + `ImageStat` dan la misma media por canal.
    try:
        from PIL import Image, ImageChops, ImageStat
    except Exception as e:
        print(f"  FALLO: sin PIL no se pueden medir las costuras ({e})")
        return 1
    tmp.mkdir(parents=True, exist_ok=True)
    piezas = curso["_piezas"]
    fallos = 0
    valores = []
    for a, b in zip(piezas, piezas[1:]):
        va = SALIDA / slug / a["_slug"] / "video.mp4"
        vb = SALIDA / slug / b["_slug"] / "video.mp4"
        if not (va.is_file() and vb.is_file()):
            continue
        fa = _frame(va, tmp / f"{a['_n']:02d}_fin.png", primero=False)
        fb = _frame(vb, tmp / f"{b['_n']:02d}_ini.png", primero=True)
        xa = Image.open(fa).convert("RGB")
        xb = Image.open(fb).convert("RGB")
        if xa.size != xb.size:
            print(f"  FALLO: {a['_slug']} y {b['_slug']} no miden lo mismo")
            fallos += 1
            continue
        canales = ImageStat.Stat(ImageChops.difference(xa, xb)).mean
        d = sum(canales) / len(canales)
        valores.append(d)
        marca = "ok" if d <= COSTURA_MAX else "FALLO"
        if d > COSTURA_MAX:
            fallos += 1
        print(f"  {marca}  {a['_slug']} -> {b['_slug']}: {d:.4f}/255")
    if valores:
        iguales = len(set(round(v, 4) for v in valores)) == 1
        print(f"  peor costura: {max(valores):.4f}/255"
              + ("  (todas EXACTAS iguales: el culpable es un objeto "
                 "de la capa fija)" if iguales and max(valores) > COSTURA_MAX
                 else ""))
    return fallos


def estima(texto):
    n = len(texto.split())
    return max(n / PALABRAS_POR_S + AIRE_S, COSTE_MINIMO_S if n <= 1 else 0.0)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("curso_dir", type=Path)
    p.add_argument("--ancho", type=int, default=1080)
    p.add_argument("--alto", type=int, default=1920)
    p.add_argument("--fps", type=int, default=60)
    p.add_argument("--tolerancia", type=float, default=0.10)
    args = p.parse_args()

    curso = cargar_curso(args.curso_dir)
    slug = curso.get("slug", args.curso_dir.name)
    try:
        from sfx import PALETA
    except Exception:
        PALETA = None

    fallos = avisos = 0
    total = 0.0
    for clip in curso["_piezas"]:
        nombre = clip["_slug"]
        video = SALIDA / slug / nombre / "video.mp4"
        print(f"\n[{clip['_n']:02d}] {clip['name']}")
        if not video.is_file():
            print(f"     FALLO: no existe {video}")
            fallos += 1
            continue
        d = datos_video(video)
        total += d["dur"]
        print(f"     {d['ancho']}x{d['alto']} @ {d['fps']:.0f} fps · "
              f"{d['dur']:.2f} s")
        if (d["ancho"], d["alto"]) != (args.ancho, args.alto):
            print(f"     FALLO: se esperaba {args.ancho}x{args.alto}")
            fallos += 1
        if abs(d["fps"] - args.fps) > 0.5:
            print(f"     FALLO: se esperaban {args.fps} fps")
            fallos += 1

        obj = clip.get("duracion_objetivo")
        if obj is None:
            print("     FALLO: falta duracion_objetivo en el manifiesto")
            fallos += 1
        elif abs(float(obj) - d["dur"]) > args.tolerancia:
            print(f"     FALLO: el manifiesto dice {obj} y el render dio "
                  f"{d['dur']:.2f} (la voz se alinea con el manifiesto)")
            fallos += 1

        if clip["_tipo"] != "marca":
            if not (curso["_min"] <= d["dur"] <= curso["_max"]):
                print(f"     FALLO: fuera del rango "
                      f"{curso['_min']:.0f}-{curso['_max']:.0f} s")
                fallos += 1

        secciones = clip.get("voz", {}).get("secciones", [])
        fin_anterior = 0.0
        for i, sec in enumerate(secciones):
            t0 = float(sec["t_inicio"])
            dur = estima(sec["texto"])
            if t0 < fin_anterior - 1e-6:
                print(f"     AVISO: la frase {i + 1} entra en {t0:.1f} y la "
                      f"anterior deberia acabar en {fin_anterior:.1f}")
                avisos += 1
            fin_anterior = t0 + dur
        if secciones:
            cola = d["dur"] - fin_anterior
            objetivo = float(clip.get("cola_silencio", 0.8))
            marca = "ok" if cola >= objetivo else "AVISO"
            if cola < objetivo:
                avisos += 1
            print(f"     voz: {len(secciones)} frases, cola estimada "
                  f"{cola:.2f} s ({marca}, minimo {objetivo})")

        audio = clip.get("audio") or {}
        fo = audio.get("fade_out")
        if fo and (fo[1] > d["dur"] + 1e-6 or fo[0] >= fo[1]):
            print(f"     FALLO: fade_out {fo} no cabe en {d['dur']:.2f} s")
            fallos += 1
        for ev in audio.get("eventos", []):
            nombre_ev, t0 = ev[0], float(ev[1])
            if PALETA is not None and nombre_ev not in PALETA:
                print(f"     FALLO: '{nombre_ev}' no esta en la paleta de sfx")
                fallos += 1
            if t0 > d["dur"]:
                print(f"     AVISO: el evento '{nombre_ev}' entra en {t0} y "
                      f"la pieza dura {d['dur']:.2f}")
                avisos += 1

    print("\n=== costuras ===")
    fallos += costuras(curso, slug, SALIDA / slug / "_costuras")

    print(f"\n=== {len(curso['_piezas'])} piezas · {total:.1f} s "
          f"({total / 60:.2f} min) · {fallos} fallos · {avisos} avisos")
    return 1 if fallos else 0


if __name__ == "__main__":
    raise SystemExit(main())
