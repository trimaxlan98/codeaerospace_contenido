#!/usr/bin/env python3
"""Índice de todo lo producido por el estudio de contenido (exports/estudio/ + reels de marca).

Genera, sin borrar nada:
  exports/estudio/INDICE.md                         qué hay, dónde, para qué (clasificado)
  exports/estudio/GALERIA.html                      galería local (abrir en el navegador): hojas de contacto,
                                                    pie de publicación y advertencias de cada carrusel
  exports/estudio/experimentos/registro_publicaciones.csv
                                                    una fila por pieza para anotar métricas a 7 días (si ya
                                                    existe, solo AÑADE las piezas nuevas; nunca pisa métricas)
  exports/estudio/PARA_DRIVE.md                     lista de entregables finales propuestos para subir
                                                    (NO sube nada: cada subida se confirma con el dueño)
Uso: python3 redes/indice_estudio.py
"""
import csv
import html
import json
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EST = REPO / "exports" / "estudio"
SPECS = REPO / "redes" / "carruseles" / "specs"
REELS = [REPO / "exports/marca-codeaerospace/reels-promo/con_sonido", REPO / "exports/marca-codeaerospace/reels-promo/con_voz",
         EST / "logo_vivo/con_sonido", EST / "reels_datos/con_sonido",
         REPO / "exports/marca-codeaerospace/vertical/con_sonido",
         REPO / "exports/marca-codeaerospace/con_sonido",
         EST / "logo_entornos/animados/con_sonido"]
REELS = list(dict.fromkeys(REELS))
COLUMNAS = ["id_pieza", "variante_de", "serie_pilar", "formato", "fecha_pub", "hora", "gancho", "gancho_tipo",
            "fondo_tema", "portada_tipo", "n_laminas_o_duracion_s", "voz", "colab", "variable_en_prueba",
            "alcance_7d", "alcance_no_seg_%", "vistas_7d", "guardados", "envios", "comentarios", "likes",
            "%_visto_reels", "repeticiones", "seguidores_ganados", "guard/alcance", "envios/alcance", "notas",
            "correcciones"]


def gancho_tipo(t):
    if "?" in t:
        return "pregunta"
    if any(c.isdigit() for c in t):
        return "dato"
    return "promesa/afirmación"


def carruseles():
    salida = []
    for ruta in sorted(SPECS.rglob("*.json")):
        base = json.loads(ruta.read_text(encoding="utf-8"))
        import sys
        sys.path.insert(0, str(REPO / "redes" / "carruseles"))
        from motor_carrusel import expandir_variantes
        for spec in expandir_variantes(base):
            carpeta = EST / "carruseles" / spec["serie"] / spec["id"]
            if not carpeta.exists():
                continue
            portada = spec["laminas"][0]
            cuidado = carpeta / f"{spec['id']}_CUIDADO.txt"
            salida.append({
                "id": spec["id"], "serie": spec["serie"], "variante_de": spec.get("variante_de", ""),
                "gancho": portada.get("titulo", ""), "n": len(spec["laminas"]),
                "tema": spec.get("fondo", {}).get("tema", "orbita"), "tipo": spec.get("fondo", {}).get("tipo", "portada"),
                "carpeta": carpeta, "hoja": carpeta / f"{spec['id']}_hoja.jpg",
                "pie": (carpeta / f"{spec['id']}_pie.txt").read_text(encoding="utf-8") if (carpeta / f"{spec['id']}_pie.txt").exists() else "",
                "cuidado": cuidado.read_text(encoding="utf-8") if cuidado.exists() else "",
                "spec": ruta, "estado": spec.get("estado", ""),
            })
    return salida


def reels():
    out = []
    for c in REELS:
        if c.exists():
            out += sorted(c.glob("*.mp4"))
    return out


def rel(p, desde=EST):
    try:
        return str(Path(p).relative_to(desde))
    except ValueError:
        return str(Path("..") / Path(p).relative_to(desde.parent))


def escribir_indice(cs, rs):
    series = {}
    for c in cs:
        series.setdefault(c["serie"], []).append(c)
    L = [f"# Estudio de contenido Co.De Aerospace — índice", "",
         f"Generado {date.today().isoformat()} por `redes/indice_estudio.py`. Nada se publica ni se sube solo.", "",
         "## Mapa", "",
         "| Carpeta | Qué es |", "|---|---|",
         "| `carruseles/<serie>/<id>/` | Carruseles 1080×1350: PNG por lámina, `_hoja.jpg`, `_pie.txt` (texto de la publicación + fuentes), `_CUIDADO.txt` (confirmar antes de publicar) |",
         "| `logo_entornos/{16x9,4x5,9x16}/` | El logo oficial sobre los 18 entornos espaciales (fijos); `HOJA_*.jpg` para comparar |",
         "| `logo_entornos/animados/` | El logo entrando (orbital) sobre entornos, 9:16; `con_sonido/` con audio |",
         "| `../marca-codeaerospace/reels-promo/con_sonido/` | Reels promocionales en loop perfecto (Orbit Eye, ATP-DT, el modelo) |",
         "| `../marca-codeaerospace/reels-promo/con_voz/` | Los mismos reels con voz en off (prueba A/B voz vs sin voz) |",
         "| `reels_datos/con_sonido/` | Reels con DATOS REALES (SGP4 + CelesTrak): curva Doppler real de la ISS |",
         "| `logo_vivo/con_sonido/` | «Logo vivo»: loops de 8 s sobre entornos espaciales |",
         "| `paquetes/<nombre>/` | Entregas finales armadas con `./codeae paquete` (lo que se sube a Drive) |",
         "| `../marca-codeaerospace/vertical/con_sonido/` | Reels de marca 9:16 |",
         "| `informes/` | Estudio por rondas de agentes (motor, producto, contenido, síntesis, contrato de pieza, datos reales) |",
         "| `experimentos/registro_publicaciones.csv` | Una fila por pieza: anota métricas a 7 días para saber qué funciona |",
         "| `GALERIA.html` | Ábrela en el navegador para revisar todo de un vistazo |",
         "| `_fondos/` | Caché de fondos procedurales (se puede borrar; se regenera) |", "",
         f"## Carruseles ({len(cs)})", ""]
    for s, lst in sorted(series.items()):
        L += [f"### {s} ({len(lst)})", "", "| id | gancho | láminas | fondo | ⚠️ |", "|---|---|---|---|---|"]
        for c in lst:
            marca = "⛔ NO PUBLICAR · " if c["estado"] == "no_publicar" else ""
            L.append(f"| [{c['id']}]({rel(c['hoja'])}) | {marca}{c['gancho']} | {c['n']} | {c['tema']}/{c['tipo']} | {'sí' if c['cuidado'] else ''} |")
        L.append("")
    L += [f"## Reels y videos con sonido ({len(rs)})", ""] + [f"- `{rel(r)}`" for r in rs] + [""]
    L += ["## Informes", ""] + [f"- [{p.name}]({rel(p)})" for p in sorted((EST / "informes").glob("*.md"))] + [""]
    (EST / "INDICE.md").write_text("\n".join(L), encoding="utf-8")


def escribir_galeria(cs, rs):
    tarjetas = []
    for c in cs:
        aviso = f"<details class='cuidado'><summary>⚠️ Confirmar antes de publicar</summary><pre>{html.escape(c['cuidado'])}</pre></details>" if c["cuidado"] else ""
        nop = "<p style='color:#FF3C6E;margin:0'>⛔ NO PUBLICAR</p>" if c["estado"] == "no_publicar" else ""
        tarjetas.append(f"""<article data-serie="{c['serie']}">{nop}<h3>{html.escape(c['gancho'])}</h3>
<p class="meta">{c['serie']} · <code>{c['id']}</code> · {c['n']} láminas · fondo {c['tema']}{' · variante de ' + c['variante_de'] if c['variante_de'] else ''}</p>
<a href="{rel(c['hoja'])}"><img loading="lazy" src="{rel(c['hoja'])}" alt="Hoja de contacto de {c['id']}"></a>
<details><summary>Texto de la publicación</summary><pre>{html.escape(c['pie'])}</pre></details>{aviso}</article>""")
    series = sorted({c["serie"] for c in cs})
    botones = "".join(f"<button data-f='{s}'>{s}</button>" for s in series)
    videos = "".join(f"<figure><video controls loop preload='none' src='{rel(r)}'></video><figcaption>{r.stem}</figcaption></figure>" for r in rs)
    pagina = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Estudio Co.De — galería</title><style>
:root{{--bg:#0a0e27;--panel:#111733;--tinta:#F1F5F9;--tenue:#93A4BD;--cian:#00D9FF;--ambar:#F59E0B}}
body{{margin:0;background:var(--bg);color:var(--tinta);font:16px/1.5 system-ui,sans-serif}}
header{{padding:24px 16px;border-bottom:1px solid #1d2650}} h1{{margin:0;font-size:22px}} h1 b{{color:var(--cian)}}
nav{{display:flex;gap:8px;flex-wrap:wrap;padding:12px 16px}} button{{background:var(--panel);color:var(--tinta);border:1px solid #2a3570;border-radius:20px;padding:6px 14px;cursor:pointer}}
button.on{{border-color:var(--cian);color:var(--cian)}}
main{{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,520px),1fr));gap:16px;padding:16px}}
article{{background:var(--panel);border-radius:14px;padding:14px}} article h3{{margin:0 0 4px;font-size:18px}}
.meta{{color:var(--tenue);font-size:13px;margin:0 0 10px}} img{{width:100%;border-radius:8px}}
pre{{white-space:pre-wrap;color:var(--tenue);font-size:13px}} .cuidado summary{{color:var(--ambar)}}
section.videos{{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:12px;padding:16px}} video{{width:100%;border-radius:8px}}
figcaption{{font-size:12px;color:var(--tenue)}}
</style></head><body><header><h1>Estudio <b>Co.De Aerospace</b> — {len(cs)} carruseles · {len(rs)} videos</h1>
<p style="color:var(--tenue);margin:6px 0 0">Generado {date.today().isoformat()}. Revisa el ⚠️ de cada pieza antes de publicar.</p></header>
<nav><button data-f="*" class="on">todas</button>{botones}</nav><main>{''.join(tarjetas)}</main>
<h2 style="padding:0 16px">Videos</h2><section class="videos">{videos}</section>
<script>document.querySelectorAll('nav button').forEach(b=>b.onclick=()=>{{document.querySelectorAll('nav button').forEach(x=>x.classList.toggle('on',x===b));
document.querySelectorAll('article').forEach(a=>a.style.display=(b.dataset.f==='*'||a.dataset.serie===b.dataset.f)?'':'none')}})</script></body></html>"""
    (EST / "GALERIA.html").write_text(pagina, encoding="utf-8")


def escribir_registro(cs, rs):
    ruta = EST / "experimentos" / "registro_publicaciones.csv"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    filas, ids = [], set()
    if ruta.exists():
        with ruta.open(encoding="utf-8") as f:
            filas = list(csv.DictReader(f))
        ids = {r["id_pieza"] for r in filas}
    for c in cs:
        if c["id"] not in ids:
            filas.append({"id_pieza": c["id"], "variante_de": c["variante_de"], "serie_pilar": c["serie"], "formato": "carrusel 4:5",
                          "gancho": c["gancho"], "gancho_tipo": gancho_tipo(c["gancho"]), "fondo_tema": c["tema"],
                          "portada_tipo": c["tipo"], "n_laminas_o_duracion_s": c["n"]})
    for r in rs:
        if r.stem not in ids and "reels-promo" in str(r):
            filas.append({"id_pieza": r.stem, "serie_pilar": "reels-promo", "formato": "reel 9:16 loop",
                          "n_laminas_o_duracion_s": 12, "voz": "no"})
    with ruta.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNAS, extrasaction="ignore")
        w.writeheader()
        for r in filas:
            w.writerow({k: r.get(k, "") for k in COLUMNAS})
    return ruta


def escribir_para_drive(cs, rs):
    L = ["# Propuesta de subida a Drive (NO subido)", "",
         "Destino acordado: remote `gdrive`, carpeta raíz `Mac-Pro-code` (rclone). Solo finales; confirmar cada subida.", "",
         "Estructura sugerida en Drive: `Mac-Pro-code/Estudio-CoDe/<fecha>/{carruseles,reels,logo-entornos,informes}`", "",
         "## Carruseles (carpetas completas: PNG + pie + cuidado)", ""]
    L += [f"- `{rel(c['carpeta'])}/`" for c in cs]
    L += ["", "## Reels y videos (solo `con_sonido/*.mp4`)", ""] + [f"- `{rel(r)}`" for r in rs]
    L += ["", "## Logo en entornos", "", "- `logo_entornos/16x9/`, `logo_entornos/4x5/`, `logo_entornos/9x16/`, `logo_entornos/HOJA_*.jpg`", "",
          "## Informes", ""] + [f"- `{rel(p)}`" for p in sorted((EST / "informes").glob("*.md"))]
    L += ["", "Comando (cuando lo apruebes), por ejemplo:", "",
          "```", "rclone copy exports/estudio/carruseles gdrive:Mac-Pro-code/Estudio-CoDe/2026-10-02/carruseles --include '*.png' --include '*.txt' -P", "```"]
    (EST / "PARA_DRIVE.md").write_text("\n".join(L), encoding="utf-8")


def main():
    cs, rs = carruseles(), reels()
    escribir_indice(cs, rs)
    escribir_galeria(cs, rs)
    r = escribir_registro(cs, rs)
    escribir_para_drive(cs, rs)
    print(f"{len(cs)} carruseles, {len(rs)} videos → {EST / 'INDICE.md'}, GALERIA.html, {r.name}, PARA_DRIVE.md")


if __name__ == "__main__":
    main()
