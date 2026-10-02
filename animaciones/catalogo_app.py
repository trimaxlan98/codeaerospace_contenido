"""Catálogo de presentaciones y temas en JSON, para la app de escritorio (CO.DE Studio).

La app no reimplementa nada del sistema de presentaciones: le pide a este script, una vez, todo lo
que necesita para mostrarlo y lo demás lo hace llamando a los CLI de siempre (decks_espaciales.py,
presentaciones_usuario.py). Rutas relativas a la raíz del repo, para que la app las resuelva dentro
de su carpeta de exports.

    python3 animaciones/catalogo_app.py            → JSON en stdout
    python3 animaciones/catalogo_app.py --validar  → además valida cada presentación (más lento)

Forma:
    {"temas": [{id, nombre, descripcion, modo, video, fuentes, color, oficial, vista}],
     "presentaciones": [{id, titulo, idiomas, propia, json, diapositivas, minutos, guion,
                         decks: [{tema, idioma, pptx, pdf, hoja, fecha}], errores, avisos}],
     "muestrarios": [...], "editor": "app/render_launcher.py"}
"""

import contextlib
import io
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
REPO = AQUI.parent
EXP = REPO / "exports"
ESP = EXP / "presentaciones" / "espaciales"
sys.path.insert(0, str(AQUI))

# Los módulos de presentaciones imprimen avisos al importarse: stdout tiene que quedar limpio (JSON).
with contextlib.redirect_stdout(io.StringIO()):
    import decks_espaciales as D
    import presentaciones_usuario as PU
    import temas_espaciales as TE


def rel(p):
    """Ruta relativa al repo si existe; None si no."""
    p = Path(p)
    return str(p.relative_to(REPO)) if p.exists() else None


def guion_de(deck, cfg, propia):
    if propia:
        return rel(PU.ruta_guion(PU.cargar(deck)))
    nombre = cfg.get("guion") or ("GUION_REDES_ORBITALES.md" if deck == "divulgacion" else
                                  f"GUION_{cfg['archivo'].upper()}.md")
    return rel(EXP / nombre)


def decks_construidos(archivo, idioma):
    out = []
    for t in TE.TEMAS:
        pptx = ESP / t / f"{archivo}_{t}.pptx"
        if pptx.exists():
            out.append(dict(tema=t, idioma=idioma, pptx=rel(pptx), pdf=rel(pptx.with_suffix(".pdf")),
                            hoja=rel(pptx.with_name(pptx.stem + "_hoja.jpg")), fecha=int(pptx.stat().st_mtime * 1000)))
    return out


def catalogo(validar=False):
    temas = []
    for t in TE.TEMAS.values():
        # Portada del tema: la miniatura si existe; si no, el fondo a resolución completa (los cuatro
        # temas de entornos no tienen miniatura).
        vista = next((v for v in (ESP / "_fondos_prev" / f"{t.id}_portada_0.jpg", ESP / "_fondos" / f"{t.id}_portada_0.jpg")
                      if v.exists()), ESP / "_fondos" / f"{t.id}_portada_0.jpg")
        temas.append(dict(id=t.id, nombre=t.nombre, descripcion=t.descripcion, modo=t.modo, video=t.video,
                          fuentes=t.fuentes, color=t.color, oficial=t.id == TE.TEMA_OFICIAL, vista=rel(vista)))
    pres = []
    for deck, idiomas in D.DECKS.items():
        propia = deck not in D.INCLUIDAS
        p = dict(id=deck, idiomas=sorted(idiomas), propia=propia, decks=[], errores=[], avisos=[],
                 json=rel(PU.ruta(deck)) if propia else None)
        for idioma in sorted(idiomas):
            with contextlib.redirect_stdout(io.StringIO()):
                cfg, ds = D.presentacion(deck, idioma)
            if idioma == "es" or "titulo" not in p:
                ritmo = float(cfg.get("ritmo") or 140)
                p.update(titulo=cfg.get("titulo_plano") or cfg.get("titulo", deck).replace("\n", " "),
                         diapositivas=len(ds),
                         minutos=round(sum(PU.palabras(x.get("guion", "")) for x in ds if x["tipo"] != "respaldo") / ritmo, 1),
                         guion=guion_de(deck, cfg, propia))
            p["decks"] += decks_construidos(cfg["archivo"], idioma)
        if validar and propia:
            p["errores"], p["avisos"] = PU.validar(PU.cargar(deck))
        pres.append(p)
    muestrarios = [rel(m) for m in sorted(ESP.glob("MUESTRARIO_*.jpg"))]
    return dict(temas=temas, presentaciones=pres, muestrarios=muestrarios, oficial=TE.TEMA_OFICIAL,
                editor="app/render_launcher.py")


if __name__ == "__main__":
    print(json.dumps(catalogo(validar="--validar" in sys.argv), ensure_ascii=False))
