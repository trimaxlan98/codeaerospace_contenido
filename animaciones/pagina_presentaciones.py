"""Prepara los archivos de la página de presentaciones (Artifact, para leer en el celular).

Para cada presentación (Redes Orbitales, seminario ES, seminar EN, comité) y cada uno de los dos temas de la página
(Órbita = oscuro, Estación = claro) toma el .pptx espacial, lo pasa a PDF con LibreOffice, rasteriza las diapositivas
a JPG ligeros y arma un PDF liviano con ellas; copia los guiones .md y genera index.html desde pagina_plantilla.html.
Salida: exports/pagina_presentaciones/  (index.html, dia/<clave>-<tema>-NN.jpg, pdf/<clave>-<tema>.pdf, guion-<clave>.md, fondos)
La publicación (herramienta Artifact) sube esa carpeta por tandas; aquí solo se prepara.
Uso: python3 pagina_presentaciones.py [clave …]
"""
import glob
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from decks_espaciales import EXP, SALIDA, presentacion  # noqa: E402
from muestrario_espacial import a_pdf  # noqa: E402

OUT = EXP / "pagina_presentaciones"
TEMAS_PAGINA = ("orbita", "estacion")
DPI = 82  # 13.33 in → ≈1093 px de ancho
CALIDAD = 70
PRES = [
    dict(clave="redes", deck="divulgacion", idioma="es", etiqueta="Redes Orbitales", lang="es",
         titulo="Redes Orbitales", lema="El siguiente salto de la economía espacial",
         autores="Alan Rosas Palacios · Yuritzi Elena Ordaz Huerta · Co.De Aerospace", guion="GUION_REDES_ORBITALES.md"),
    dict(clave="seminario", deck="seminario", idioma="es", etiqueta="Seminario · ES", lang="es",
         titulo="Agentes de inteligencia artificial en órbita", lema="…y el problema de saber si funcionan",
         autores="Alan Rosas Palacios · Doctorado, Instituto Politécnico Nacional", guion="GUION_SEMINARIO_AGENTES_IA_ORBITA.md"),
    dict(clave="seminar-en", deck="seminario", idioma="en", etiqueta="Seminar · EN", lang="en",
         titulo="Artificial intelligence agents in orbit", lema="…and the problem of knowing whether they work",
         autores="Alan Rosas Palacios · PhD program, Instituto Politécnico Nacional (IPN)", guion="SEMINAR_AI_AGENTS_IN_ORBIT_EN.md"),
    dict(clave="comite", deck="comite", idioma="es", etiqueta="Comité tutorial", lang="es",
         titulo="Gobernanza autónoma de redes programables", lema="Protocolo de tesis · instanciada en redes no terrestres 6G",
         autores="Alan Rosas Palacios · Comité tutorial", guion="GUION_COMITE_TUTORIAL_PROTOCOLO.md"),
]


def rasterizar(pdf, clave, tema):
    """JPG por diapositiva + PDF liviano; devuelve (n diapositivas, ruta del PDF)."""
    (OUT / "dia").mkdir(parents=True, exist_ok=True)
    (OUT / "pdf").mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(["pdftoppm", "-r", str(DPI), "-jpeg", "-jpegopt", f"quality={CALIDAD}", str(pdf), f"{d}/p"], check=True)
        fs = sorted(glob.glob(f"{d}/p-*.jpg"))
        for i, f in enumerate(fs, 1):
            shutil.copy2(f, OUT / "dia" / f"{clave}-{tema}-{i:02d}.jpg")
        ims = [Image.open(f).convert("RGB") for f in fs]
    destino = OUT / "pdf" / f"{clave}-{tema}.pdf"
    ims[0].save(destino, "PDF", save_all=True, append_images=ims[1:], resolution=DPI)
    return len(fs), destino


def main(claves):
    OUT.mkdir(parents=True, exist_ok=True)
    manifiesto = []
    for p in PRES:
        if claves and p["clave"] not in claves:
            continue
        cfg, _ = presentacion(p["deck"], p["idioma"])
        pdfs, n = {}, None
        for tema in TEMAS_PAGINA:
            pptx = SALIDA / tema / f"{cfg['archivo']}_{tema}.pptx"
            if not pptx.exists():
                raise SystemExit(f"falta {pptx}: construye el deck (python3 decks_espaciales.py {tema}{' --en' if p['idioma'] == 'en' else ''} {p['deck']})")
            pdf = a_pdf(pptx)
            n, ligero = rasterizar(pdf, p["clave"], tema)
            pdfs[tema] = dict(archivo=f"pdf/{ligero.name}", mb=round(ligero.stat().st_size / 1e6, 1))
            print(f"{p['clave']:11s} {tema:9s} {n} diapositivas · PDF {pdfs[tema]['mb']} MB", flush=True)
        g = EXP / p["guion"]
        shutil.copy2(g, OUT / f"guion-{p['clave']}.md")
        m = re.search(r"\*\*(\d+(?:\.\d+)?) min\*\*", g.read_text(encoding="utf-8"))
        minutos = round(float(m.group(1))) if m else "?"
        resumen = f"{n} {'slides' if p['lang'] == 'en' else 'diapositivas'} · ~{minutos} min"
        manifiesto.append({**{k: v for k, v in p.items() if k not in ("deck", "idioma")}, "guion": f"guion-{p['clave']}.md",
                           "n": n, "minutos": minutos, "resumen": resumen, "pdf": pdfs})
    if claves:  # reconstrucción parcial: conservar el resto del manifiesto
        previo = json.loads((OUT / "manifiesto.json").read_text(encoding="utf-8")) if (OUT / "manifiesto.json").exists() else []
        por = {m["clave"]: m for m in previo}
        por.update({m["clave"]: m for m in manifiesto})
        manifiesto = [por[p["clave"]] for p in PRES if p["clave"] in por]
    (OUT / "manifiesto.json").write_text(json.dumps(manifiesto, ensure_ascii=False, indent=1), encoding="utf-8")
    # fondos de la página (los mismos de las presentaciones, más pequeños)
    for origen, destino in (("orbita_contenido_0", "fondo-oscuro"), ("estacion_contenido_0", "fondo-claro")):
        Image.open(SALIDA / "_fondos" / f"{origen}.jpg").convert("RGB").resize((1600, 900), Image.LANCZOS).save(
            OUT / f"{destino}.jpg", "JPEG", quality=72, optimize=True)
    plantilla = (Path(__file__).parent / "pagina_plantilla.html").read_text(encoding="utf-8")
    html = plantilla.replace("/*MANIFEST*/[]", json.dumps(manifiesto, ensure_ascii=False)).replace(
        "/*PIE*/", f"actualizada {date.today().isoformat()}")
    (OUT / "index.html").write_text(html, encoding="utf-8")
    archivos = [f for f in OUT.rglob("*") if f.is_file() and f.name != "manifiesto.json"]
    print(f"{len(archivos)} archivos · {sum(f.stat().st_size for f in archivos) / 1e6:.0f} MB en {OUT}")


if __name__ == "__main__":
    main(sys.argv[1:])
