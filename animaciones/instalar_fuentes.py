"""Instala las fuentes de Google Fonts que piden los temas espaciales, con el nombre de familia corregido.

La API de CSS de Google entrega instancias estáticas de las fuentes variables con el nombre interno de la
instancia por defecto («Oxanium ExtraLight» en vez de «Oxanium»): PowerPoint, LibreOffice y Pango (Manim) no las
encuentran por el nombre que usa el tema. Aquí se descargan y se reescribe la tabla de nombres:
  400 → «<Familia>» Regular · 700 → «<Familia>» Bold (par que PowerPoint usa con la negrita) ·
  otros pesos → familia «<Familia> Medium|SemiBold|…» (útiles para Manim: Text(font="Teko SemiBold")).
Archivos: ~/.local/share/fonts/codeaerospace/<Familia>-<peso>.ttf (los copia decks_espaciales.py junto a los .pptx).
Requiere fonttools (pip install --user fonttools).

Uso:  python3 instalar_fuentes.py                 instala las de los temas registrados que falten
      python3 instalar_fuentes.py "Orbitron:400,700" "Teko:400,700"     familias sueltas (nombre:pesos)
"""
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from fontTools.ttLib import TTFont

DEST = Path.home() / ".local/share/fonts/codeaerospace"
NOMBRE_PESO = {100: "Thin", 200: "ExtraLight", 300: "Light", 400: "Regular", 500: "Medium", 600: "SemiBold", 700: "Bold",
               800: "ExtraBold", 900: "Black"}
# fuentes estáticas que ya trae Google con el nombre correcto o que se instalaron antes de este script (no se tocan)
EXISTENTES = {"Rajdhani", "DM Sans", "Space Mono", "Orbitron", "Chakra Petch", "IBM Plex Sans", "IBM Plex Mono", "Exo 2", "Sora",
              "Space Grotesk"}


def archivo(familia, peso):
    return DEST / f"{familia.replace(' ', '')}-{peso}.ttf"


def descargar(familia, pesos):
    """Descarga los pesos pedidos; si la familia no tiene alguno (las mono casi nunca traen 700) baja los demás."""
    try:
        return _descargar(familia, pesos)
    except urllib.error.HTTPError:
        hechos = []
        for p in pesos:
            try:
                hechos += _descargar(familia, [p])
            except urllib.error.HTTPError:
                print(f"  ({familia} no tiene peso {p}; se omite)", flush=True)
        if not hechos:
            raise
        return hechos


def _descargar(familia, pesos):
    url = "https://fonts.googleapis.com/css?family=" + urllib.parse.quote_plus(familia) + ":" + ",".join(map(str, pesos))
    css = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/4.0"}), timeout=30).read().decode()
    hechos = []
    for peso, u in re.findall(r"font-weight:\s*(\d+);\s*src:\s*url\((https[^)]+)\)", css):
        ruta = archivo(familia, peso)
        ruta.write_bytes(urllib.request.urlopen(u, timeout=60).read())
        normalizar(ruta, familia, int(peso))
        hechos.append(int(peso))
    if not hechos:
        raise SystemExit(f"Google Fonts no entregó {familia!r} ({pesos}); revisa el nombre exacto de la familia")
    return hechos


def normalizar(ruta, familia, peso):
    """Reescribe los nombres internos para que la familia sea `familia` (400/700) o «familia Peso» (demás)."""
    f = TTFont(ruta)
    n = f["name"]
    ps = familia.replace(" ", "")
    if peso in (400, 700):
        fam1, sub, completo = familia, NOMBRE_PESO[peso], familia if peso == 400 else f"{familia} Bold"
        f16 = f17 = None
    else:
        fam1, sub, completo = f"{familia} {NOMBRE_PESO[peso]}", "Regular", f"{familia} {NOMBRE_PESO[peso]}"
        f16, f17 = familia, NOMBRE_PESO[peso]
    for ident in (1, 2, 3, 4, 6, 16, 17, 21, 22, 25):
        n.removeNames(nameID=ident)
    for plat, enc, lang in ((3, 1, 0x409), (1, 0, 0)):
        n.setName(fam1, 1, plat, enc, lang)
        n.setName(sub, 2, plat, enc, lang)
        n.setName(f"{ps}-{NOMBRE_PESO[peso]};code-aerospace", 3, plat, enc, lang)
        n.setName(completo, 4, plat, enc, lang)
        n.setName(f"{ps}-{NOMBRE_PESO[peso]}", 6, plat, enc, lang)
        if f16:
            n.setName(f16, 16, plat, enc, lang)
            n.setName(f17, 17, plat, enc, lang)
    f["OS/2"].usWeightClass = peso
    sel = f["OS/2"].fsSelection & ~(1 | 32 | 64)  # sin itálica / negrita / regular previas
    f["OS/2"].fsSelection = sel | (32 if peso == 700 else 64)
    f["head"].macStyle = (f["head"].macStyle & ~1) | (1 if peso == 700 else 0)
    if "fvar" in f:
        del f["fvar"]
    f.save(ruta)


def instalar(pedidas):
    """pedidas: {familia: [pesos]}. Devuelve las que se descargaron."""
    nuevas = {}
    for fam, pesos in pedidas.items():
        if fam in EXISTENTES:
            continue
        pesos = sorted(set(pesos) | {400, 700})
        faltan = [p for p in pesos if not archivo(fam, p).exists() or _familia(archivo(fam, p)) not in (fam, f"{fam} {NOMBRE_PESO[p]}")]
        if faltan:
            try:
                nuevas[fam] = descargar(fam, faltan)
                print(f"  {fam}: {nuevas[fam]}", flush=True)
            except Exception as e:  # una familia mal escrita o sin ese peso no detiene al resto
                print(f"  [sin instalar] {fam} {faltan}: {e}", file=sys.stderr, flush=True)
    if nuevas:
        subprocess.run(["fc-cache", "-f", str(DEST)], check=True)
    return nuevas


def _familia(ruta):
    try:
        return TTFont(ruta, lazy=True)["name"].getDebugName(1)
    except Exception:
        return None


def de_los_temas():
    sys.path.insert(0, str(Path(__file__).parent))
    import temas_espaciales as TE
    pedidas = {}
    pesos = {v: k for k, v in NOMBRE_PESO.items()}
    for t in TE.TEMAS.values():
        for fam in set(t.fuentes.values()) | ({t.manim["FUENTE"], t.manim["FUENTE_CIFRA"]} if t.manim else set()):
            base, _, ultimo = fam.rpartition(" ")
            if base and ultimo in pesos and ultimo != "Regular":  # «Jura Medium» = familia Jura, peso 500
                pedidas.setdefault(base, [400, 700]).append(pesos[ultimo])
            else:
                pedidas.setdefault(fam, [400, 700])
    return pedidas


if __name__ == "__main__":
    DEST.mkdir(parents=True, exist_ok=True)
    if len(sys.argv) > 1:
        ped = {}
        for a in sys.argv[1:]:
            fam, _, ps = a.partition(":")
            ped[fam] = [int(p) for p in ps.split(",")] if ps else [400, 700]
    else:
        ped = de_los_temas()
    hecho = instalar(ped)
    print("instaladas:", ", ".join(hecho) or "ninguna nueva")
