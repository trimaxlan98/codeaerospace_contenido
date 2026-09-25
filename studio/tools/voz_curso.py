#!/usr/bin/env python3
"""Reparte el guion de voz de un curso horizontal en los ficheros que
`guiones.py --solo-audio` sintetiza (generaliza voz_tesis6g.py, curso 36).

El VPS no tiene guionista (MS_TTS_GUIONISTA=ninguno): la narracion se
escribe a mano en `docs/plan_contenido/curso-NN-guion-de-voz.md`, un bloque
`### N.M.K` por clip. Esta herramienta deja, por leccion, en
`guiones/<slugify(nombre del proyecto)>/`:

    NN-<titulo>.txt             la narracion plana
    NN-<titulo>.secciones.json  una seccion por frase, con t_inicio

    python3 studio/tools/voz_curso.py --prefijo rendimiento-sql \
        --guion docs/plan_contenido/curso-37-guion-de-voz.md [--comprobar]

Los tiempos se colocan a 2.2 palabras por segundo desde el segundo 1: es el
ritmo con el que la casa sintetiza sin que la voz se salga del clip.
`--comprobar` solo cuenta palabras contra la duracion del render qh local y
avisa de lo que no cabe (con el 10 % de margen de `guiones.py`).
"""
import argparse
import json
import re
import struct
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
CURSOS = RAIZ / "studio/content/cursos"
PPS = 2.2           # palabras por segundo
MARGEN = 0.9        # la voz ocupa como mucho el 90 % del clip
T0 = 1.0


def slugify(text: str) -> str:
    """La MISMA que app.narracion.slugify (40 caracteres)."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40] or "clip"


def leer_guion(guion: Path) -> dict:
    bloques, clave = {}, None
    for linea in guion.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^### (\d+)\.(\d+)\.(\d+)\s*$", linea)
        if m:
            clave = tuple(int(x) for x in m.groups())
            bloques[clave] = []
        elif linea.startswith("## "):
            clave = None
        elif clave and linea.strip():
            bloques[clave].append(linea.strip())
    return {k: " ".join(v) for k, v in bloques.items()}


def duracion_mp4(path: Path):
    try:
        data = path.read_bytes()
    except OSError:
        return None
    i = data.find(b"mvhd")
    if i < 0:
        return None
    ver = data[i + 4]
    if ver == 1:
        escala, dur = struct.unpack(">IQ", data[i + 24:i + 36])
    else:
        escala, dur = struct.unpack(">II", data[i + 16:i + 24])
    return dur / escala if escala else None


def secciones(texto: str) -> list:
    frases = [f.strip() for f in re.split(r"(?<=[.:;])\s+", texto) if f.strip()]
    out, t = [], T0
    for f in frases:
        n = len(f.split())
        out.append({"t_inicio": round(t, 2), "t_fin": round(t + n / PPS, 2), "momento": "", "texto": f})
        t += n / PPS + 0.3
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--salida", type=Path, default=RAIZ / "guiones")
    ap.add_argument("--comprobar", action="store_true")
    ap.add_argument("--prefijo", required=True, help="prefijo de slug, p. ej. rendimiento-sql")
    ap.add_argument("--guion", type=Path, required=True)
    ap.add_argument("--lecciones", help="solo estas, p. ej. 1.1,1.2")
    a = ap.parse_args()
    g = leer_guion(a.guion if a.guion.is_absolute() else RAIZ / a.guion)
    solo = set(a.lecciones.split(",")) if a.lecciones else None
    problemas = 0
    for d in sorted(CURSOS.glob(f"{a.prefijo}-*")):
        m = re.match(rf"{re.escape(a.prefijo)}-(\d+)-(\d+)-", d.name)
        mod, lec = int(m.group(1)), int(m.group(2))
        if solo and f"{mod}.{lec}" not in solo:
            continue
        cj = json.loads((d / "curso.json").read_text(encoding="utf-8"))
        destino = a.salida / slugify(cj["name"])
        for pos, clip in enumerate(cj["clips"]):
            texto = g.get((mod, lec, pos + 1))
            if not texto:
                print(f"FALTA guion {mod}.{lec}.{pos + 1}")
                problemas += 1
                continue
            etq = f"{pos + 1:02d}-{slugify(clip['title'])}"
            n = len(texto.split())
            video = duracion_mp4(RAIZ / "render_jobs/qh" / d.name / f"{pos + 1:02d}-{clip['scene']}" / "video.mp4")
            cabe = video is None or n / PPS <= video * MARGEN
            marca = "" if cabe else "  <-- NO CABE"
            problemas += 0 if cabe else 1
            vs = f"{video:5.1f} s" if video else "  sin qh"
            print(f"{mod}.{lec}.{pos + 1}  {n:3d} palabras  {n / PPS:5.1f} s de voz  clip {vs}{marca}")
            if not a.comprobar:
                destino.mkdir(parents=True, exist_ok=True)
                (destino / f"{etq}.txt").write_text(texto + "\n", encoding="utf-8")
                (destino / f"{etq}.secciones.json").write_text(
                    json.dumps(secciones(texto), ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n{problemas} problema(s)")
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
