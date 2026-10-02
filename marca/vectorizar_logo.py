"""Vectoriza el logo de Co.De Aerospace desde el PNG oficial y genera el kit vectorial.

Fuente: `originales/logo-fondo-oscuro.png` (1167×1218, logo plata sobre #080F15), el de mayor
resolución y contraste. Salidas (todas regenerables; no se editan a mano):

  marca/logo-codeaerospace.svg            logo completo, plata con degradado, fondo transparente
  marca/logo-codeaerospace-negro.svg      una tinta (#000) para fondos claros
  marca/logo-codeaerospace-blanco.svg     una tinta (#fff) para fondos oscuros
  marca/emblema-codeaerospace.svg         sin «AEROSPACE»: para íconos y espacios cuadrados
  marca/logo-codeaerospace-{plata,negro}.png  1600 px de alto, fondo transparente (PPTX, documentos)
  studio/content/manim_extensions/marca_aerospace.json
                                          geometría por partes para `marca_aerospace.py` (Manim)

Cómo separa las partes: el PNG se etiqueta por componentes conexos y cada componente se asigna a
una parte (órbitas, luna, satélite, C, O, punto, D, E, letras de AEROSPACE) por su posición, que
es fija en el original. Las letras y el satélite se trazan con potrace a 3× (contornos Bézier con
huecos en orientación opuesta, así que se rellenan bien con la regla nonzero de Cairo). Las órbitas
se guardan DOS veces: el contorno trazado (para el SVG, fiel al pixel) y su línea central con su
grosor (para Manim, donde una órbita tiene que poder «dibujarse» con Create de un extremo a otro).
La luna y el punto de «CO.DE» son círculos exactos (centro y radio medidos).

Uso:  python3 marca/vectorizar_logo.py          (requiere: pip install potracer scikit-image scipy)
"""

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

try:
    import potrace
    from scipy import interpolate, ndimage
    from skimage import measure, morphology
except ImportError as e:  # pragma: no cover
    sys.exit(f"falta una dependencia ({e.name}): pip install potracer scikit-image scipy")

MARCA = Path(__file__).resolve().parent
REPO = MARCA.parent
ORIGEN = MARCA / "originales" / "logo-fondo-oscuro.png"
JSON_MANIM = REPO / "studio" / "content" / "manim_extensions" / "marca_aerospace.json"

UMBRAL = 122            # luminancia: fondo ≈14, tinta ≈230
SUPER = 3               # potrace trabaja a 3× para que las curvas no hereden el escalón del pixel
FONDO = "#080F15"       # fondo del PNG oficial (medido)
PLATA = ("#F2F3F4", "#D3D5D8")   # degradado vertical medido en el PNG plata (arriba → abajo)

# Orden y nombre de las letras de AEROSPACE (los componentes se ordenan por x).
AEROSPACE = list("AEROSPACE")


def _mascara(img, factor=1):
    """Tinta=True. A `factor`× se reescala con Lanczos ANTES de umbralizar (bordes subpixel)."""
    g = img.convert("L")
    if factor > 1:
        g = g.resize((g.width * factor, g.height * factor), Image.LANCZOS)
    return np.array(g) > UMBRAL


def _clasificar(lab, props):
    """Asigna cada componente conexo (área ≥ 30 px) a una parte del logo por su posición."""
    partes = {"orbitas": [], "luna": [], "panel_1": [], "cuerpo": [], "panel_2": [], "C": [], "O": [],
              "punto": [], "D": [], "E": [], "aerospace": []}
    letras = []
    for r in props:
        y, x = r.centroid
        if r.area < 100 and 540 < x < 620 and 420 < y < 490:
            partes["cuerpo"].append(r.label)                    # los dos puntitos del cubo
            continue
        if r.area < 30:
            continue
        y0, x0, y1, x1 = r.bbox
        cy, cx = r.centroid
        alto, ancho = y1 - y0, x1 - x0
        if 760 < cy < 860 and alto < 70:
            letras.append((cx, r.label))                       # fila de AEROSPACE
        elif 560 < y0 and y1 < 740 and alto > 140:              # letras grandes C O D E
            parte = "C" if cx < 390 else "O" if cx < 600 else "D" if cx < 860 else "E"
            partes[parte].append(r.label)
        elif r.area > 300 and r.solidity > 0.9 and abs(alto - ancho) < 6:        # círculos: luna y punto
            partes["luna" if cy < 400 else "punto"].append(r.label)
        elif 480 < cx < 720 and 330 < cy < 560 and max(alto, ancho) < 120:
            # Satélite: panel de arriba a la izquierda, cubo y panel de abajo a la derecha.
            parte = "panel_1" if cx < 560 else "panel_2" if cx > 640 else "cuerpo"
            partes[parte].append(r.label)
        else:
            partes["orbitas"].append(r.label)
    letras.sort()
    if len(letras) != len(AEROSPACE):
        sys.exit(f"esperaba {len(AEROSPACE)} letras en AEROSPACE y hay {len(letras)}")
    partes["aerospace"] = [lbl for _, lbl in letras]
    for k, v in partes.items():
        if not v:
            sys.exit(f"no se encontró la parte «{k}»")
    return partes


def _trazar(mascara_sup):
    """Contornos potrace de una máscara a SUPER× → lista de subtrayectos de cúbicas en px 1×."""
    curvas = potrace.Bitmap(~mascara_sup).trace(turdsize=4, alphamax=1.0, opticurve=True,
                                                opttolerance=0.2)
    sub = []
    for c in curvas:
        p0 = np.array([c.start_point.x, c.start_point.y]) / SUPER
        cubicas = []
        for s in c.segments:
            fin = np.array([s.end_point.x, s.end_point.y]) / SUPER
            if s.is_corner:
                esq = np.array([s.c.x, s.c.y]) / SUPER
                for a, b in ((p0, esq), (esq, fin)):          # dos rectas como cúbicas
                    cubicas.append([a, a + (b - a) / 3, a + 2 * (b - a) / 3, b])
            else:
                c1 = np.array([s.c1.x, s.c1.y]) / SUPER
                c2 = np.array([s.c2.x, s.c2.y]) / SUPER
                cubicas.append([p0, c1, c2, fin])
            p0 = fin
        sub.append(cubicas)
    return sub


def _ordenar(esqueleto):
    """Pixeles de un esqueleto → polilínea ordenada del camino más largo (diámetro del grafo de
    pixeles: dos BFS). Las espuelas cortas que deja skeletonize quedan fuera solas."""
    pts = {tuple(p) for p in np.argwhere(esqueleto)}
    vecinos = lambda p: [(p[0] + dy, p[1] + dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                         if (dy or dx) and (p[0] + dy, p[1] + dx) in pts]

    def bfs(origen):
        padre, cola, ultimo = {origen: None}, [origen], origen
        for p in cola:
            for q in vecinos(p):
                if q not in padre:
                    padre[q] = p
                    cola.append(q)
            ultimo = p
        return ultimo, padre

    a, _ = bfs(min(pts))
    b, padre = bfs(a)
    camino = [b]
    while padre[camino[-1]] is not None:
        camino.append(padre[camino[-1]])
    return np.array([(x, y) for y, x in camino], float)


def _alargar(linea, mascara):
    """El esqueleto se queda corto ≈ medio grosor en cada punta: se prolonga por la tangente
    hasta salir de la tinta, para que el trazo de Manim cubra la órbita completa."""
    def punta(a, b):
        t = (a - b) / np.linalg.norm(a - b)
        p, extra = a.copy(), []
        for _ in range(40):
            q = p + t * 0.5
            yi, xi = int(round(q[1])), int(round(q[0]))
            if not (0 <= yi < mascara.shape[0] and 0 <= xi < mascara.shape[1]) or not mascara[yi, xi]:
                break
            p = q
            extra.append(p.copy())
        return extra
    ini = punta(linea[0], linea[min(6, len(linea) - 1)])
    fin = punta(linea[-1], linea[max(-7, -len(linea))])
    return np.vstack([ini[::-1] or np.empty((0, 2)), linea, fin or np.empty((0, 2))])


def _suavizar(linea, n=96):
    """Spline de suavizado sobre la polilínea del esqueleto → n puntos equiespaciados."""
    d = np.r_[0, np.cumsum(np.hypot(*np.diff(linea, axis=0).T))]
    tck, _ = interpolate.splprep([linea[:, 0], linea[:, 1]], u=d / d[-1], s=len(linea) * 0.25, k=3)
    u = np.linspace(0, 1, n)
    return np.c_[interpolate.splev(u, tck)].T


def _centrales(lab, etiquetas, mascara):
    """Línea central y grosor de cada arco de órbita. Un componente puede traer DOS arcos que se
    cruzan (arriba a la derecha): se corta el cruce, se reagrupan los tramos por continuidad de
    dirección y cada arco se ordena por separado."""
    esq = morphology.skeletonize(mascara)
    dist = ndimage.distance_transform_edt(mascara)
    arcos = []
    for e in etiquetas:
        s = (lab == e) & esq
        nb = ndimage.convolve(s.astype(int), np.ones((3, 3)), mode="constant") - 1
        # Los puntos de bifurcación incluyen las espuelas de skeletonize; el cruce verdadero es
        # el grupo de bifurcaciones que, recortado, deja CUATRO tramos largos.
        grupos = measure.label(ndimage.binary_dilation(s & (nb > 2), iterations=4))
        tl, cx, cy = None, 0.0, 0.0
        for g in range(1, grupos.max() + 1):
            gy, gx = np.nonzero(grupos == g)
            s2 = s.copy()
            s2[gy.min() - 10:gy.max() + 11, gx.min() - 10:gx.max() + 11] = False
            t = measure.label(s2, connectivity=2)
            if sum((t == k).sum() > 40 for k in range(1, t.max() + 1)) >= 4:
                tl, cx, cy = t, gx.mean(), gy.mean()
                break
        if tl is None:
            arcos.append((_ordenar(s), e))
            continue
        tramos = [_ordenar(tl == k) for k in range(1, tl.max() + 1) if (tl == k).sum() > 40]

        # Cada tramo tiene un extremo junto al cruce; dos tramos son el mismo arco si al
        # atravesar el cruce siguen en línea (direcciones de llegada opuestas).
        def junto(t):
            cerca_ini = np.hypot(*(t[0] - [cx, cy])) < np.hypot(*(t[-1] - [cx, cy]))
            t = t[::-1] if cerca_ini else t          # el extremo del cruce queda al final
            v = t[-1] - t[max(-11, -len(t))]
            return v / np.linalg.norm(v), t

        info = [junto(t) for t in tramos]
        usados = set()
        for i in range(len(info)):
            if i in usados:
                continue
            j = min((k for k in range(len(info)) if k != i and k not in usados),
                    key=lambda k: np.dot(info[i][0], info[k][0]))
            usados |= {i, j}
            arcos.append((np.vstack([info[i][1], info[j][1][::-1]]), e))
    salida = []
    for linea, e in arcos:
        grosor = 2 * float(np.median(dist[(lab == e) & esq]))
        larga = _alargar(linea, mascara)
        salida.append({"puntos": _suavizar(larga).round(2).tolist(), "grosor": round(grosor, 2)})
    return salida


def _circulo(lab, etiquetas):
    m = np.isin(lab, etiquetas)
    y, x = np.nonzero(m)
    return {"centro": [round(float(x.mean()), 2), round(float(y.mean()), 2)],
            "radio": round(float(np.sqrt(m.sum() / np.pi)), 2)}


def _d_svg(subtrayectos, dx=0.0, dy=0.0):
    f = lambda p: f"{p[0] - dx:.2f} {p[1] - dy:.2f}"
    partes = []
    for cub in subtrayectos:
        partes.append("M" + f(cub[0][0]) + "".join("C" + " ".join(f(q) for q in c[1:]) for c in cub) + "Z")
    return "".join(partes)


def _circ_svg(c, dx, dy):
    (x, y), r = c["centro"], c["radio"]
    x, y = x - dx, y - dy
    return f"M{x - r:.2f} {y:.2f}a{r:.2f} {r:.2f} 0 1 0 {2 * r:.2f} 0a{r:.2f} {r:.2f} 0 1 0 {-2 * r:.2f} 0Z"


def _png(geo, colores, destino, alto=1600, margen=0.04):
    """Rasteriza la geometría con Cairo: fondo transparente, degradado vertical arriba→abajo."""
    import cairo
    x0, y0, x1, y1 = geo["caja"]
    k = alto * (1 - 2 * margen) / (y1 - y0)
    ancho = int(round((x1 - x0) * k + 2 * alto * margen))
    sup = cairo.ImageSurface(cairo.FORMAT_ARGB32, ancho, alto)
    c = cairo.Context(sup)
    c.translate(alto * margen - x0 * k, alto * margen - y0 * k)
    c.scale(k, k)
    c.set_fill_rule(cairo.FILL_RULE_WINDING)
    rgb = lambda h: tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
    grad = cairo.LinearGradient(0, y0, 0, y1)
    grad.add_color_stop_rgb(0, *rgb(colores[0]))
    grad.add_color_stop_rgb(1, *rgb(colores[1]))

    def sub(subs):
        for cub in subs:
            c.move_to(*cub[0][0])
            for q in cub:
                c.curve_to(*q[1], *q[2], *q[3])
            c.close_path()

    sub(geo["orbitas_contorno"])
    for v in geo["satelite"].values():
        sub(v)
    for k_ in "CODE":
        sub(geo["letras"][k_])
    for l in geo["aerospace"]:
        sub(l)
    for k_ in ("luna", "punto"):
        c.new_sub_path()
        c.arc(*geo[k_]["centro"], geo[k_]["radio"], 0, 2 * np.pi)
    c.set_source(grad)
    c.fill()
    sup.write_to_png(str(destino))


def main():
    img = Image.open(ORIGEN).convert("RGB")
    m1 = _mascara(img)
    m3 = _mascara(img, SUPER)
    lab = measure.label(m1, connectivity=2)
    props = measure.regionprops(lab)
    partes = _clasificar(lab, props)
    lab3 = np.array(Image.fromarray(lab.astype(np.int32)).resize(m3.shape[::-1], Image.NEAREST))

    def trazar(etqs):
        return _trazar(m3 & np.isin(lab3, etqs))

    geo = {
        "fuente": "marca/originales/logo-fondo-oscuro.png",
        "tamano": [img.width, img.height],
        "colores": {"fondo": FONDO, "plata": list(PLATA)},
        "orbitas": _centrales(lab, partes["orbitas"], m1),
        "orbitas_contorno": trazar(partes["orbitas"]),
        "luna": _circulo(lab, partes["luna"]),
        "punto": _circulo(lab, partes["punto"]),
        "satelite": {k: trazar(partes[k]) for k in ("panel_1", "cuerpo", "panel_2")},
        "letras": {k: trazar(partes[k]) for k in "CODE"},
        "aerospace": [trazar([e]) for e in partes["aerospace"]],
    }
    # Caja del logo completo (para centrar) y de la fila AEROSPACE.
    ys, xs = np.nonzero(m1)
    geo["caja"] = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
    a = np.isin(lab, partes["aerospace"])
    ya, xa = np.nonzero(a)
    geo["caja_aerospace"] = [int(xa.min()), int(ya.min()), int(xa.max()) + 1, int(ya.max()) + 1]

    redondear = lambda v: np.round(np.asarray(v, float), 2).tolist()
    geo_json = dict(geo)
    geo_json["orbitas_contorno"] = [[redondear(c) for c in s] for s in geo["orbitas_contorno"]]
    geo_json["satelite"] = {k: [[redondear(c) for c in s] for s in v] for k, v in geo["satelite"].items()}
    geo_json["letras"] = {k: [[redondear(c) for c in s] for s in v] for k, v in geo["letras"].items()}
    geo_json["aerospace"] = [[[redondear(c) for c in s] for s in letra] for letra in geo["aerospace"]]
    JSON_MANIM.write_text(json.dumps(geo_json, separators=(",", ":")) + "\n", encoding="utf-8")

    # ── SVG ──────────────────────────────────────────────────────────────────────
    M = 24
    x0, y0, x1, y1 = geo["caja"]
    dx, dy = x0 - M, y0 - M

    def svg(relleno, defs="", con_aerospace=True, nombre=""):
        yfin = (y1 if con_aerospace else geo["caja_aerospace"][1] - 8) + M
        # Sin AEROSPACE, la parte baja de las órbitas también sale; se recorta con el viewBox
        # solo si el arco inferior no cruza: se conserva entero (el emblema es el logo sin texto).
        if not con_aerospace:
            yfin = y1 + M
        w, h = x1 - x0 + 2 * M, yfin - dy
        cuerpo = [
            f'<path id="orbitas" d="{_d_svg(geo["orbitas_contorno"], dx, dy)}"/>',
            f'<path id="luna" d="{_circ_svg(geo["luna"], dx, dy)}"/>',
            f'<path id="satelite" d="{"".join(_d_svg(v, dx, dy) for v in geo["satelite"].values())}"/>',
            f'<path id="co_de" d="{"".join(_d_svg(geo["letras"][k], dx, dy) for k in "CODE")}'
            f'{_circ_svg(geo["punto"], dx, dy)}"/>',
        ]
        if con_aerospace:
            cuerpo.append(f'<path id="aerospace" d="{"".join(_d_svg(l, dx, dy) for l in geo["aerospace"])}"/>')
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" '
                f'width="{w:.0f}" height="{h:.0f}" role="img" aria-label="Co.De Aerospace">\n'
                f'<title>Co.De Aerospace{nombre}</title>\n{defs}<g fill="{relleno}" fill-rule="nonzero">\n'
                + "\n".join(cuerpo) + "\n</g>\n</svg>\n")

    plata = (f'<defs><linearGradient id="plata" x1="0" y1="0" x2="0" y2="1">'
             f'<stop offset="0" stop-color="{PLATA[0]}"/><stop offset="1" stop-color="{PLATA[1]}"/>'
             f'</linearGradient></defs>\n')
    (MARCA / "logo-codeaerospace.svg").write_text(svg("url(#plata)", plata), encoding="utf-8")
    (MARCA / "logo-codeaerospace-negro.svg").write_text(svg("#000000"), encoding="utf-8")
    (MARCA / "logo-codeaerospace-blanco.svg").write_text(svg("#FFFFFF"), encoding="utf-8")
    (MARCA / "emblema-codeaerospace.svg").write_text(
        svg("url(#plata)", plata, con_aerospace=False, nombre=" (emblema)"), encoding="utf-8")

    for nombre, colores in (("plata", PLATA), ("negro", ("#0A0D12", "#0A0D12"))):
        _png(geo, colores, MARCA / f"logo-codeaerospace-{nombre}.png")

    n = lambda s: sum(len(c) for c in s)
    sat = [c for v in geo["satelite"].values() for c in v]
    print(f"órbitas: {len(geo['orbitas'])} arcos (grosor ≈ {geo['orbitas'][0]['grosor']} px), "
          f"satélite: {len(sat)} contornos / {n(sat)} cúbicas, "
          f"letras: {sum(n(v) for v in geo['letras'].values())} cúbicas, "
          f"aerospace: {sum(n(l) for l in geo['aerospace'])} cúbicas")
    print(f"→ {JSON_MANIM.relative_to(REPO)} ({JSON_MANIM.stat().st_size // 1024} KB) y 4 SVG en marca/")


if __name__ == "__main__":
    main()
