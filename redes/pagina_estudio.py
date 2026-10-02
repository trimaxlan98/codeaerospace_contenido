#!/usr/bin/env python3
"""Página de revisión del estudio (para el celular): exports/estudio/pagina/{index.html, img/, vid/}.

Reúne las hojas de contacto de los carruseles (con gancho, serie, ⛔/⚠️, texto de la publicación y
advertencias), el logo en entornos, los reels en loop con sonido y las decisiones pendientes. Se publica
como Artifact privado; las imágenes se comprimen (JPG 1200 px) para que pese poco.
Uso: python3 redes/pagina_estudio.py
"""
import html
import json
import shutil
import sys
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "redes"))
import indice_estudio as IE  # noqa: E402

EST = REPO / "exports" / "estudio"
OUT = EST / "pagina"
VIDEOS = [REPO / "exports/marca-codeaerospace/reels-promo/con_sonido" / f"{n}.mp4" for n in ("ReelOrbitEye", "ReelATP", "ReelModelo")] + \
         [EST / "logo_vivo/con_sonido" / f"LogoVivo{n}.mp4" for n in ("Orbita", "Nebulosa", "Marte", "Lunar", "Fisica", "Espectro")]
DECISIONES = [
    ("Versionar el motor en git", "marca/, redes/ y los módulos nuevos aún no están en git. Recomendado: sí, tras revisar que no entre nada de la tesis ni de clientes."),
    ("Voz humana en los reels", "Probar reel con voz en off contra sin voz (variable A/B)."),
    ("Datos orbitales reales", "Instalar sgp4 y descargar TLE de CelesTrak con caché: habilita pases reales de la ISS, curva Doppler real, etc."),
    ("Cadencia", "Propuesta: 2 carruseles y 1 reel por semana; el plan A/B está en experimentos/plan_ab_ronda1.md."),
    ("Un solo frente", "Unificar la app de escritorio (Electron) como único frente del estudio."),
    ("Subida a Drive", "Nada se subió. PARA_DRIVE.md lista los finales; confirma qué subir."),
]


def comprimir(src, dst, ancho=1200):
    dst.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(src).convert("RGB")
    if im.width > ancho:
        im = im.resize((ancho, int(im.height * ancho / im.width)), Image.LANCZOS)
    im.save(dst, quality=78, optimize=True)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    cs = IE.carruseles()
    datos = []
    for c in cs:
        rel = f"img/{c['serie']}__{c['id']}.jpg"
        comprimir(c["hoja"], OUT / rel)
        datos.append({"id": c["id"], "serie": c["serie"], "gancho": c["gancho"], "n": c["n"], "tema": c["tema"],
                      "variante_de": c["variante_de"], "estado": c["estado"], "img": rel, "pie": c["pie"],
                      "cuidado": c["cuidado"]})
    hojas = []
    for fmt in ("9x16", "4x5", "16x9"):
        rel = f"img/logo_entornos_{fmt}.jpg"
        comprimir(EST / "logo_entornos" / f"HOJA_{fmt}.jpg", OUT / rel, 1600)
        hojas.append((fmt, rel))
    vids = []
    for v in VIDEOS:
        if v.exists():
            (OUT / "vid").mkdir(parents=True, exist_ok=True)
            shutil.copy2(v, OUT / "vid" / v.name)
            vids.append(f"vid/{v.name}")
    plantilla = (REPO / "redes" / "pagina_estudio.html").read_text(encoding="utf-8")
    pagina = (plantilla.replace("/*DATOS*/[]", json.dumps(datos, ensure_ascii=False))
              .replace("/*HOJAS*/[]", json.dumps(hojas))
              .replace("/*VIDEOS*/[]", json.dumps(vids))
              .replace("/*DECISIONES*/[]", json.dumps(DECISIONES, ensure_ascii=False)))
    (OUT / "index.html").write_text(pagina, encoding="utf-8")
    archivos = sorted(p.relative_to(OUT) for p in OUT.rglob("*") if p.is_file() and p.name != "index.html")
    (OUT / "archivos.json").write_text(json.dumps([str(a) for a in archivos]), encoding="utf-8")
    peso = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file()) / 1e6
    print(f"{len(datos)} carruseles, {len(vids)} videos, {len(archivos)} archivos, {peso:.1f} MB → {OUT}")


if __name__ == "__main__":
    main()
