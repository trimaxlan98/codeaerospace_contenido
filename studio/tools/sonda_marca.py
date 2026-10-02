#!/usr/bin/env python3
"""Sonda de la marca Co.De Aerospace y sus librerías Manim (marca_aerospace, estelas, rotulos_aerospace).

Mide contra el PNG oficial, no contra el gusto: la geometría vectorizada tiene que cubrir el logo
(IoU), las piezas tienen que caber en el cuadro y las animaciones tienen que poder recorrerse de
principio a fin sin error. Una librería que no pasa NO entra en un clip.

    python3 studio/tools/sonda_marca.py                 (host, desde la raíz del repo)
    docker run --rm --network none --user $(id -u):$(id -g) \\
      -v <repo>:/workspace:ro codeaerospace_contenido-manim \\
      python3 /workspace/studio/tools/sonda_marca.py      (el contenedor que renderiza)

`--render DIR` renderiza además el último cuadro de la entrada orbital (oscura y clara) en DIR y
compara su silueta con el PNG oficial (IoU ≥ 0.95). Tarda ≈ 1 min.
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
EXT = RAIZ / "studio" / "content" / "manim_extensions"
sys.path.insert(0, str(EXT))

import numpy as np  # noqa: E402

FALLOS, OK = [], []
PNG = RAIZ / "marca" / "originales" / "logo-fondo-oscuro.png"


def check(cond, msg):
    (OK if cond else FALLOS).append(msg)
    print(("  ok   " if cond else "  FALLO") + " " + msg)


# ── 1 · Geometría ──────────────────────────────────────────────────────────────────

def sonda_geometria():
    print("geometría (marca_aerospace.json)")
    g = json.loads((EXT / "marca_aerospace.json").read_text(encoding="utf-8"))
    check(len(g["orbitas"]) == 6, f"6 arcos de órbita como trazo (hay {len(g['orbitas'])})")
    check(all(8 <= o["grosor"] <= 12 for o in g["orbitas"]), "grosor de órbita entre 8 y 12 px")
    check(set(g["satelite"]) == {"panel_1", "cuerpo", "panel_2"}, "satélite en panel_1, cuerpo y panel_2")
    check(set(g["letras"]) == set("CODE"), "letras C, O, D, E")
    check(len(g["aerospace"]) == 9, f"9 letras en AEROSPACE (hay {len(g['aerospace'])})")
    check(20 < g["luna"]["radio"] < 35 and 12 < g["punto"]["radio"] < 24, "radios de luna y punto plausibles")
    return g


def _raster(g, contorno):
    import cairo
    w, h = g["tamano"]
    s = cairo.ImageSurface(cairo.FORMAT_A8, w, h)
    c = cairo.Context(s)
    c.set_fill_rule(cairo.FILL_RULE_WINDING)

    def sub(subs):
        for cub in subs:
            c.move_to(*cub[0][0])
            for q in cub:
                c.curve_to(*q[1], *q[2], *q[3])
            c.close_path()

    for k in "CODE":
        sub(g["letras"][k])
    for l in g["aerospace"]:
        sub(l)
    for v in g["satelite"].values():
        sub(v)
    for k in ("luna", "punto"):
        c.new_sub_path()
        c.arc(*g[k]["centro"], g[k]["radio"], 0, 2 * np.pi)
    if contorno:
        sub(g["orbitas_contorno"])
    c.fill()
    if not contorno:
        c.set_line_cap(cairo.LINE_CAP_BUTT)
        for o in g["orbitas"]:
            c.move_to(*o["puntos"][0])
            for p in o["puntos"][1:]:
                c.line_to(*p)
            c.set_line_width(o["grosor"])
            c.stroke()
    s.flush()
    return np.ndarray((h, s.get_stride()), np.uint8, s.get_data())[:, :w] > 127


def sonda_fidelidad(g):
    print("fidelidad con el PNG oficial")
    from PIL import Image
    ref = np.array(Image.open(PNG).convert("L")) > 122
    for contorno, minimo, nombre in ((True, 0.98, "contorno"), (False, 0.93, "trazo de órbitas")):
        m = _raster(g, contorno)
        iou = (m & ref).sum() / (m | ref).sum()
        check(iou >= minimo, f"IoU {nombre} = {iou:.4f} (≥ {minimo})")
    for svg in ("logo-codeaerospace.svg", "logo-codeaerospace-negro.svg", "logo-codeaerospace-blanco.svg",
                "emblema-codeaerospace.svg"):
        t = (RAIZ / "marca" / svg).read_text(encoding="utf-8")
        check(t.startswith("<svg") and all(f'id="{p}"' in t for p in ("orbitas", "luna", "satelite", "co_de")),
              f"{svg}: SVG con sus partes")


# ── 2 · Librerías ──────────────────────────────────────────────────────────────────

def sonda_estelas():
    print("estelas.py")
    from manim import Create, Dot, Ellipse, VMobject
    import estelas as E
    arco = VMobject().set_points_smoothly([np.array([np.cos(a) * 3, np.sin(a) * 1.2, 0])
                                           for a in np.linspace(0, 4, 9)])
    check(np.allclose(E.punto_de_trazo(arco, 0), arco.get_start()) and
          np.allclose(E.punto_de_trazo(arco, 1), arco.get_end()), "punto_de_trazo: extremos")
    for t in (0.137, 0.5, 0.861):
        parcial = VMobject().pointwise_become_partial(arco, 0, t)
        check(np.allclose(E.punto_de_trazo(arco, t), parcial.get_end(), atol=1e-6),
              f"punto_de_trazo({t}) coincide con lo que dibuja Create")
    r = E.remuestrear(arco, 40)
    check(np.allclose(r.get_start(), arco.get_start()) and np.allclose(r.get_end(), arco.get_end()),
          "remuestrear conserva los extremos")
    largos = [np.linalg.norm(r.points[4 * i + 3] - r.points[4 * i]) for i in range(len(r.points) // 4)]
    check(max(largos) / min(largos) < 1.25, f"remuestrear: curvas parejas (max/min = {max(largos) / min(largos):.2f})")
    # Las animaciones se recorren cuadro a cuadro sin escena.
    for nombre, anim in (("dibujar_con_cometa", E.dibujar_con_cometa(arco.copy())),
                         ("recorrer_con_estela", E.recorrer_con_estela(Dot(), Ellipse(width=4, height=2))),
                         ("destello_en", E.destello_en(arco.copy()))):
        try:
            anim.begin()
            for a in np.linspace(0, 1, 31):
                anim.interpolate(a)
            anim.finish()
            check(True, f"{nombre}: 31 cuadros sin error")
        except Exception as e:  # noqa: BLE001
            check(False, f"{nombre}: {e!r}")


def sonda_logo():
    print("marca_aerospace.py")
    from manim import UP, config
    import marca_aerospace as M
    logo = M.LogoCoDe(altura=4.0)
    check(abs(logo.height - 4.0) < 0.08, f"altura pedida 4.0 → {logo.height:.3f}")
    check(1.0 < logo.width / logo.height < 1.1, f"proporción ancho/alto = {logo.width / logo.height:.3f}")
    check(len(logo.orbitas) == 6 and len(logo.letras) == 5 and len(logo.aerospace) == 9, "partes completas")
    sin = M.LogoCoDe(altura=4.0, aerospace=False)
    check(sin.aerospace not in sin.submobjects, "aerospace=False quita la palabra")
    # El contorno acompaña al grupo aunque se haya movido y escalado antes del cambio.
    logo.scale(0.5).shift(2 * UP + 1.5 * np.array([1, 0, 0]))
    antes = logo.orbitas.get_center(), logo.orbitas.width
    logo.usar_contorno()
    despues = logo.orbitas_contorno.get_center(), logo.orbitas_contorno.width
    check(np.linalg.norm(antes[0] - despues[0]) < 0.03 and abs(antes[1] - despues[1]) / antes[1] < 0.02,
          "usar_contorno: el contorno cae donde estaba el trazo tras mover y escalar")
    for color in ("plata", "negro", "blanco", "#00D9FF", ("#ffffff", "#888888")):
        try:
            M.LogoCoDe(altura=2, color=color)
            check(True, f"color {color!r}")
        except Exception as e:  # noqa: BLE001
            check(False, f"color {color!r}: {e!r}")
    m = M.marca_agua_aerospace()
    fw, fh = config.frame_width / 2, config.frame_height / 2
    check(m.get_right()[0] <= fw and m.get_bottom()[1] >= -fh and m.z_index >= 1000,
          "marca de agua dentro del cuadro y por encima")


def sonda_rotulos():
    print("rotulos_aerospace.py")
    from manim import config
    import rotulos_aerospace as R
    fw, fh = config.frame_width / 2, config.frame_height / 2

    def dentro(mob, nombre):
        ok = (mob.get_left()[0] >= -fw and mob.get_right()[0] <= fw and mob.get_bottom()[1] >= -fh
              and mob.get_top()[1] <= fh)
        check(ok, f"{nombre} cabe en el cuadro")

    dentro(R.tarjeta_titulo("Redes no terrestres", "Satélites y 6G", antetitulo="Seminario"), "tarjeta_titulo")
    larga = R.tarjeta_titulo("Un título larguísimo que de ninguna manera cabría en una sola línea del cuadro")
    dentro(larga, "tarjeta_titulo con título larguísimo (se encoge)")
    dentro(R.tercio_inferior("Alan Rosas Palacios", "Co.De Aerospace"), "tercio_inferior")
    dentro(R.capitulo(12, "Ventana de contacto y enlaces entre satélites"), "capitulo")
    dentro(R.cierre_marca(lema="Lema de prueba"), "cierre_marca")
    una = R._texto("SEMINARIO · CO.DE AEROSPACE", 20, "MEDIUM", tracking=0.22)
    sola = R._texto("S", 20, "MEDIUM")
    check(una.height < sola.height * 1.6, "el texto con tracking queda en UNA línea")
    sin = R._texto("SEMINARIO", 20, "MEDIUM")
    con = R._texto("SEMINARIO", 20, "MEDIUM", tracking=0.22)
    check(con.width > sin.width * 1.15, f"el tracking abre el texto ({con.width / sin.width:.2f}×)")


# ── 3 · Render del último cuadro ───────────────────────────────────────────────────

def _gris(ruta, claro=False):
    from PIL import Image
    g = np.array(Image.open(ruta).convert("L")).astype(float)
    g = 255 - g if claro else g
    fondo = np.median(np.r_[g[0], g[-1], g[:, 0], g[:, -1]])
    return g, (fondo + np.percentile(g, 99.5)) / 2   # umbral a media altura entre fondo y tinta medida


def _silueta(ruta, claro=False):
    g, u = _gris(ruta, claro)
    ys, xs = np.nonzero(g > u)
    return g[ys.min():ys.max() + 1, xs.min():xs.max() + 1] > u


def _iou_registrado(ruta, claro, ref):
    """IoU de la silueta de `ruta` contra `ref` (máscara recortada), con registro de ±1 px.

    El recorte a la caja de tinta se decide por un pixel de borde antialiasado: una fila de más o
    de menos cambia la escala al llevarla al tamaño del PNG y corre medio pixel los trazos finos
    (satélite, órbitas), lo que baja el IoU varios puntos sin ninguna diferencia visible. Se prueba
    cada borde de la caja a −1, 0 y +1 px y se queda el mejor. Se reescala en GRISES y se
    umbraliza después (umbralizar antes adelgaza los trazos finos).
    """
    from PIL import Image
    g, u = _gris(ruta, claro)
    ys, xs = np.nonzero(g > u)
    mejor = 0.0
    for d in np.ndindex(3, 3, 3, 3):
        y0, y1, x0, x1 = ys.min() + d[0] - 1, ys.max() + d[1], xs.min() + d[2] - 1, xs.max() + d[3]
        c = g[max(y0, 0):y1 + 1, max(x0, 0):x1 + 1]
        m = np.array(Image.fromarray(c.astype(np.uint8)).resize(ref.shape[::-1], Image.LANCZOS)) > u
        mejor = max(mejor, (m & ref).sum() / (m | ref).sum())
    return mejor


def sonda_render(salida):
    print("último cuadro de la entrada orbital contra el PNG oficial")
    demo = RAIZ / "studio" / "content" / "animations" / "experimentacion" / "30-logo-co-de-aerospace.py"
    ref = _silueta(PNG)
    for escena, claro in (("LogoCoDeIntro", False), ("LogoCoDeIntroClaro", True)):
        r = subprocess.run(["manim", "render", "-s", "-r", "2560,1440", "--disable_caching", "--media_dir",
                            str(salida), str(demo), escena], capture_output=True, text=True,
                           env={**__import__("os").environ, "PYTHONPATH": str(EXT)})
        pngs = sorted(Path(salida).rglob(f"{escena}*.png"))
        if r.returncode or not pngs:
            check(False, f"{escena}: no renderizó ({r.stderr[-300:]})")
            continue
        iou = _iou_registrado(pngs[-1], claro, ref)
        check(iou >= 0.95, f"{escena}: IoU de la silueta final = {iou:.4f} (≥ 0.95)")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--render", metavar="DIR", nargs="?", const="", help="renderiza el último cuadro y lo compara")
    a = ap.parse_args()
    from manim import config
    config.media_dir = tempfile.mkdtemp(prefix="sonda_marca_media_")   # Text escribe SVG; /workspace es de solo lectura
    g = sonda_geometria()
    sonda_fidelidad(g)
    sonda_estelas()
    sonda_logo()
    sonda_rotulos()
    if a.render is not None:
        sonda_render(a.render or tempfile.mkdtemp(prefix="sonda_marca_"))
    print(f"\n{len(OK)} ok · {len(FALLOS)} fallos")
    for f in FALLOS:
        print("  FALLO", f)
    sys.exit(1 if FALLOS else 0)


if __name__ == "__main__":
    main()
