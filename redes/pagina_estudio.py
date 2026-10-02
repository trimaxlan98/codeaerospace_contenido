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
VIDEOS = [EST / "reels_datos/con_sonido/ReelDopplerReal.mp4"] + \
         [REPO / "exports/marca-codeaerospace/reels-promo/con_sonido" / f"{n}.mp4" for n in ("ReelOrbitEye", "ReelATP", "ReelModelo")] + \
         [REPO / "exports/marca-codeaerospace/reels-promo/con_voz" / f"{n}_voz.mp4" for n in ("ReelOrbitEye", "ReelATP", "ReelModelo")] + \
         [EST / "logo_vivo/con_sonido" / f"LogoVivo{n}.mp4" for n in ("Orbita", "Nebulosa", "Marte", "Lunar", "Fisica", "Espectro")]
DECISIONES = [
    ("Hecho · Versionado en git", "Motor, carruseles, CLI y datos orbitales están en git (commits 39d2d5e y 306ae38, firmados como Alan Rosas Palacios). Pendiente de tu revisión: la sección «Contenido» de la app de escritorio, que quedó mezclada con tus cambios sin confirmar en studio/desktop."),
    ("Hecho · Reels con voz", "Voz neuronal local (Piper es_MX-ald, licencia unlicense) en los 3 reels, variantes A (voz libre) y B (lazo de frase). Pendiente: oírlas (yo no puedo), decidir si regrabas con tu voz con los guiones de studio/content/voz/guiones/, y revisar si Instagram pide etiquetar audio generado con IA."),
    ("Hecho · Datos reales", "sgp4 instalado; módulo datos_orbitales con CelesTrak y época visible. Primera pieza: curva Doppler real de un pase de la ISS (carrusel y reel). El pase es el sábado 3 de octubre, 09:06 hora de CDMX: verifica la hora en NASA Spot the Station antes de anunciarlo."),
    ("Hecho · Cadencia mínima", "2 carruseles + 1 reel por semana. Calendario de 6 semanas con el plan A/B y la prueba de voz en docs/estudio/calendario_6_semanas.md."),
    ("Hecho · Estudio unificado", "Una sola CLI (./codeae) y un solo frente: la app de escritorio, sección «Contenido» (Ctrl+8). Subir a Drive pide confirmación propia."),
    ("Hecho · Drive", "Subidos los carruseles (53) y los 4 reels nuevos con sus variantes de voz a Mac-Pro-code/Estudio-CoDe/2026-10-02. No se subieron los logos animados ni los reels de marca de ayer; dime si los quieres."),
    ("Pendiente · Siguiente ronda de datos reales", "Traza terrestre de la ISS, «pases de la semana», Starlink en un globo (necesita costas del mundo: Natural Earth)."),
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
