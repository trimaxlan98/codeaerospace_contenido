"""Presentaciones creadas por el usuario (desde la app o a mano): un JSON por presentación en animaciones/presentaciones/.

Cada archivo `<id>.json` describe una presentación completa con las piezas Manim ya renderizadas del catálogo
(catalogo.py + catalogo_tesis.py); decks_espaciales.py la construye en cualquier tema igual que las incluidas
(seminario, comité, divulgación). Este módulo no importa nada pesado: lo usan la app y el constructor.

Formato (los campos con * son obligatorios):
{
  "id"*: "que_es_code",                 minúsculas, dígitos y «_»; también es el nombre del archivo de salida
  "idioma": "es" | "en",
  "titulo"*: "…", "lema": "…", "kicker": "PRESENTACIÓN INSTITUCIONAL", "autor": "…", "instit": "…",
  "pie": "…", "cierre_titulo": "…", "ritmo": 140 (palabras por minuto del guion), "marca": true (logotipo CO.DE en la portada),
  "nota": "contexto que va al inicio del guion .md",
  "diapos"*: [
    {"tipo": "portada", "guion"*: "…"},                                       primera
    {"tipo": "seccion", "titulo"*: "…", "sub": "…", "guion"*: "…"},
    {"tipo": "texto", "titulo"*: "…", "sub": "…", "puntos"*: ["…", …], "sticker": "Clase", "guion"*: "…"},
    {"tipo": "video", "clase"*: "Clase", "titulo"*: "…", "sub": "…", "guion"*: "…"},
    {"tipo": "cita", "frase"*: "…", "sub": "…", "sticker": "Clase", "guion"*: "…"},
    {"tipo": "cierre", "guion"*: "…"},                                        una sola, después del contenido
    {"tipo": "respaldo", … como «texto»}                                      después del cierre, fuera del tiempo
  ]
}
Cualquier diapositiva admite "cuidado": advertencia de lo que no se puede afirmar (va a las notas y al guion con ⚠️).

Uso:  python3 presentaciones_usuario.py --lista | --validar ID | --guion ID | --nueva ID | --piezas
"""
import json
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import catalogo  # noqa: E402
import catalogo_tesis  # noqa: E402

DIR = AQUI / "presentaciones"
EXP = AQUI.parent / "exports"
TIPOS = ("portada", "seccion", "texto", "video", "cita", "cierre", "respaldo")
CAMPOS = {  # tipo → (obligatorios, opcionales) además de guion / cuidado
    "portada": ((), ()),
    "cierre": ((), ()),
    "seccion": (("titulo",), ("sub",)),
    "texto": (("titulo", "puntos"), ("sub", "sticker")),
    "respaldo": (("titulo", "puntos"), ("sub", "sticker")),
    "video": (("clase", "titulo"), ("sub",)),
    "cita": (("frase",), ("sub", "sticker")),
}
ETIQUETA = {"portada": "Portada", "seccion": "Sección", "texto": "Texto + sticker", "video": "Video",
            "cita": "Cita", "cierre": "Cierre", "respaldo": "Respaldo (preguntas)"}
POR_DEFECTO = {"idioma": "es", "kicker": "PRESENTACIÓN", "autor": "", "instit": "Co.De Aerospace  ·  codeaerospace.com",
               "pie": "", "cierre_titulo": "Gracias", "ritmo": 140, "marca": True, "lema": "", "nota": ""}
# límites de diseño: más largo que esto todavía cabe (el constructor reduce la letra) pero se ve apretado
LIMITES = {"titulo": 70, "sub": 110, "punto": 130, "frase": 150, "puntos": 6}
ID_OK = re.compile(r"^[a-z0-9][a-z0-9_]{1,40}$")


# ------------------------------------------------------------------ catálogo de piezas
def piezas():
    """Lista de piezas Manim utilizables: dict(clase, carpeta, bloque, muestra, cuando, oscuro, claro, en)."""
    out = []
    for mod in (catalogo, catalogo_tesis):
        for bloque, carpeta, ps in mod.BLOQUES:
            for p in ps:
                c = p[0]
                out.append(dict(clase=c, carpeta=carpeta, bloque=bloque, muestra=p[1], cuando=p[2] if len(p) > 2 else "",
                                oscuro=(EXP / carpeta / "oscuro" / f"{c}.mp4").exists(),
                                claro=(EXP / carpeta / "claro" / f"{c}.mp4").exists(),
                                en=(EXP / carpeta / "oscuro_en" / f"{c}.mp4").exists()))
    return out


def _indice():
    return {p["clase"]: p for p in piezas()}


# ------------------------------------------------------------------ archivos
def ruta(id_):
    return DIR / f"{id_}.json"


def listar():
    """[(id, titulo, idioma)] de las presentaciones guardadas (las que empiezan con «_» son plantillas y se omiten)."""
    out = []
    for f in sorted(DIR.glob("*.json")) if DIR.is_dir() else []:
        if f.name.startswith("_"):
            continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            out.append((d.get("id", f.stem), d.get("titulo", f.stem), d.get("idioma", "es")))
        except Exception as e:  # un archivo roto no debe esconder a los demás
            print(f"[presentación omitida] {f.name}: {e}", file=sys.stderr)
    return out


def cargar(id_):
    d = json.loads(ruta(id_).read_text(encoding="utf-8"))
    return completar(d)


def completar(d):
    """Rellena los campos opcionales con sus valores por defecto (no modifica el original)."""
    d = {**POR_DEFECTO, **d}
    d["pie"] = d["pie"] or d.get("titulo", "")
    d["diapos"] = [dict(x) for x in d.get("diapos", [])]
    for x in d["diapos"]:
        x.setdefault("guion", "")
        x.setdefault("cuidado", "")
        if x.get("tipo") in ("texto", "respaldo"):
            x.setdefault("sub", "")
            x.setdefault("sticker", None)
        elif x.get("tipo") in ("seccion", "video"):
            x.setdefault("sub", "")
        elif x.get("tipo") == "cita":
            x.setdefault("sub", "")
            x.setdefault("sticker", None)
    return d


def guardar(d):
    """Valida lo mínimo para poder escribir (id) y guarda con formato estable. Devuelve la ruta."""
    if not ID_OK.match(d.get("id", "")):
        raise ValueError("el id debe tener 2–41 caracteres: minúsculas, dígitos y «_», sin empezar con «_»")
    DIR.mkdir(parents=True, exist_ok=True)
    limpio = {k: v for k, v in d.items() if not k.startswith("_")}
    limpio["diapos"] = [{k: v for k, v in x.items() if not k.startswith("_") and v not in (None, "", [])} | {"tipo": x["tipo"]}
                        for x in d.get("diapos", [])]
    for x, orig in zip(limpio["diapos"], d.get("diapos", [])):
        x["guion"] = orig.get("guion", "")  # el guion siempre se guarda, aunque esté vacío (se ve que falta)
    p = ruta(d["id"])
    p.write_text(json.dumps(limpio, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return p


def nueva(id_, titulo="Nueva presentación", idioma="es"):
    """Esqueleto mínimo válido salvo los guiones: portada, una sección, un texto, un video y cierre."""
    return completar({
        "id": id_, "titulo": titulo, "idioma": idioma, "lema": "", "autor": "",
        "diapos": [
            {"tipo": "portada", "guion": ""},
            {"tipo": "seccion", "titulo": "Primera sección", "sub": "", "guion": ""},
            {"tipo": "texto", "titulo": "Idea principal", "sub": "", "puntos": ["Primer punto", "Segundo punto"],
             "sticker": "Tierra3DSatelites", "guion": ""},
            {"tipo": "video", "clase": "WalkerDelta3D", "titulo": "Una constelación", "sub": "", "guion": ""},
            {"tipo": "cierre", "guion": ""},
        ]})


# ------------------------------------------------------------------ validación
def validar(d):
    """(errores, avisos). Con errores no se construye; los avisos son de diseño (textos largos, guion vacío…)."""
    err, av = [], []
    if not ID_OK.match(d.get("id", "")):
        err.append("id inválido: minúsculas, dígitos y «_» (2–41 caracteres)")
    if not str(d.get("titulo", "")).strip():
        err.append("falta el título de la presentación")
    if d.get("idioma", "es") not in ("es", "en"):
        err.append("idioma debe ser «es» o «en»")
    try:
        if float(d.get("ritmo", 140)) <= 0:
            err.append("el ritmo (palabras por minuto) debe ser positivo")
    except (TypeError, ValueError):
        err.append("el ritmo debe ser un número")
    ds = d.get("diapos") or []
    if not ds:
        err.append("la presentación no tiene diapositivas")
        return err, av
    tipos = [x.get("tipo") for x in ds]
    if tipos[0] != "portada":
        err.append("la primera diapositiva debe ser la portada")
    if tipos.count("portada") > 1:
        err.append("solo puede haber una portada")
    if tipos.count("cierre") != 1:
        err.append("debe haber exactamente un cierre")
    else:
        ic = tipos.index("cierre")
        if any(t != "respaldo" for t in tipos[ic + 1:]):
            err.append("después del cierre solo van diapositivas de respaldo")
        if any(t == "respaldo" for t in tipos[:ic]):
            err.append("las diapositivas de respaldo van después del cierre")
    idx = _indice()
    en = d.get("idioma") == "en"
    for n, x in enumerate(ds, 1):
        t = x.get("tipo")
        pre = f"diapositiva {n} ({ETIQUETA.get(t, t)})"
        if t not in CAMPOS:
            err.append(f"{pre}: tipo desconocido; usa uno de {', '.join(TIPOS)}")
            continue
        oblig, _ = CAMPOS[t]
        for c in oblig:
            v = x.get(c)
            if not v or (isinstance(v, str) and not v.strip()) or (isinstance(v, list) and not any(str(p).strip() for p in v)):
                err.append(f"{pre}: falta «{c}»")
        for c in ("clase", "sticker"):
            v = x.get(c)
            if not v:
                continue
            p = idx.get(v)
            if p is None:
                err.append(f"{pre}: la pieza «{v}» no está en el catálogo")
            elif not p["oscuro"]:
                err.append(f"{pre}: la pieza «{v}» no está renderizada (exports/{p['carpeta']}/oscuro/{v}.mp4)")
            elif en and c == "clase" and not p["en"]:
                av.append(f"{pre}: «{v}» no tiene render en inglés; el video saldrá con textos en español")
        if not str(x.get("guion", "")).strip():
            av.append(f"{pre}: sin guion (la diapositiva no suma tiempo y las notas quedan vacías)")
        if x.get("titulo") and len(x["titulo"]) > LIMITES["titulo"]:
            av.append(f"{pre}: título de {len(x['titulo'])} caracteres; arriba de {LIMITES['titulo']} se reduce la letra")
        if x.get("sub") and len(x["sub"]) > LIMITES["sub"]:
            av.append(f"{pre}: subtítulo largo ({len(x['sub'])} caracteres)")
        if t in ("texto", "respaldo") and isinstance(x.get("puntos"), list):
            pts = [p for p in x["puntos"] if str(p).strip()]
            if len(pts) > LIMITES["puntos"]:
                av.append(f"{pre}: {len(pts)} puntos; más de {LIMITES['puntos']} quedan muy chicos")
            for p in pts:
                if len(p) > LIMITES["punto"]:
                    av.append(f"{pre}: un punto de {len(p)} caracteres («{p[:30]}…»)")
            if not x.get("sticker"):
                av.append(f"{pre}: sin sticker (la regla del diseño es que toda diapositiva de solo texto lleve uno)")
        if t == "cita":
            if x.get("frase") and len(x["frase"]) > LIMITES["frase"]:
                av.append(f"{pre}: frase de {len(x['frase'])} caracteres; arriba de {LIMITES['frase']} pierde fuerza")
            if not x.get("sticker"):
                av.append(f"{pre}: sin sticker")
    return err, av


# ------------------------------------------------------------------ para el constructor
def a_deck(d):
    """(cfg, diapositivas) en el formato que espera decks_espaciales.Diseno."""
    d = completar(d)
    cfg = dict(archivo=d["id"], kicker=d["kicker"], titulo=d["titulo"], lema=d["lema"], autor=d["autor"], instit=d["instit"],
               pie=d["pie"], cierre_titulo=d["cierre_titulo"], ritmo=float(d["ritmo"]), marca=bool(d["marca"]),
               tam_titulo=int(d.get("tam_titulo", 54)), idioma=d["idioma"], titulo_plano=d["titulo"], nota_md=d["nota"])
    out = []
    for x in d["diapos"]:
        y = {k: v for k, v in x.items() if not k.startswith("_")}
        if y["tipo"] in ("texto", "respaldo"):
            y["puntos"] = [p for p in y.get("puntos", []) if str(p).strip()]
        out.append(y)
    return cfg, out


def palabras(t):
    return len(str(t).split())


def titulo_de(x, cfg):
    t = x["tipo"]
    en = cfg.get("idioma") == "en"
    if t == "portada":
        return "Title slide" if en else "Portada"
    if t == "cierre":
        return "Closing" if en else "Cierre"
    return x.get("titulo") or x.get("frase") or ETIQUETA[t]


def minutos_total(d):
    cfg, ds = a_deck(d)
    return sum(palabras(x["guion"]) for x in ds if x["tipo"] != "respaldo") / cfg["ritmo"]


def guion_md(d):
    """Guion en el mismo formato que los de tesis_decks.guion_md (lo lee la página de presentaciones)."""
    cfg, ds = a_deck(d)
    en = cfg["idioma"] == "en"
    ritmo = cfg["ritmo"]
    princ = [x for x in ds if x["tipo"] != "respaldo"]
    pal = sum(palabras(x["guion"]) for x in princ)
    tot = pal / ritmo
    nresp = len(ds) - len(princ)
    autor = cfg["autor"] or ("No author" if en else "Sin autor")
    if en:
        L = [f"# Script — {cfg['titulo']}", "",
             f"**{autor}** · {cfg['instit']}. Pace {ritmo:g} words/min → **{tot:.1f} min** of script "
             f"({pal} words, {len(princ)} slides), plus {nresp} backup slides for questions (outside the timing).", ""]
        if cfg["nota_md"]:
            L += [cfg["nota_md"], ""]
        L += ["Videos start on click and hold on their last frame. Lines marked ⚠️ say what must **not** be claimed; "
              "they are also in the speaker notes.", "", "| # | Time | Slide |", "|---|---|---|"]
    else:
        L = [f"# Guion — {cfg['titulo']}", "",
             f"**{autor}** · {cfg['instit']}. Ritmo {ritmo:g} palabras/min → **{tot:.1f} min** de guion "
             f"({pal} palabras, {len(princ)} diapositivas), más {nresp} diapositivas de respaldo para preguntas (fuera del tiempo).", ""]
        if cfg["nota_md"]:
            L += [cfg["nota_md"], ""]
        L += ["Los videos arrancan con clic y se quedan en su último cuadro. Las líneas ⚠️ son advertencias de lo que **no** "
              "se puede afirmar: van también en las notas del orador.", "", "| # | Hora | Diapositiva |", "|---|---|---|"]
    t, filas, cuerpo = 0.0, [], []
    for n, x in enumerate(ds, 1):
        tit = titulo_de(x, cfg)
        if x["tipo"] == "respaldo":
            h = "backup" if en else "respaldo"
            filas.append(f"| {n} | — | {tit} |")
        else:
            h = f"{int(t)}:{int((t % 1) * 60):02d}"
            filas.append(f"| {n} | {h} | {tit} |")
        sub = x.get("sub", "") if x["tipo"] not in ("portada", "cierre") else ""
        meta = (f"*{sub}*  ·  " if sub else f"*{tit}*  ·  ") + h + (f"  ·  video `{x['clase']}`" if x["tipo"] == "video" else "")
        cuerpo += [f"## {n}. {tit}", meta, "", x["guion"].strip() or ("(no script yet)" if en else "(sin guion todavía)"), ""]
        if x.get("cuidado"):
            cuerpo += [f"> ⚠️ **{'Caution' if en else 'Cuidado'}:** {x['cuidado']}", ""]
        if x["tipo"] != "respaldo":
            t += palabras(x["guion"]) / ritmo
    return "\n".join(L + filas + [""] + cuerpo)


def ruta_guion(d):
    return EXP / f"GUION_{d['id'].upper()}.md"


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--lista", action="store_true")
    ap.add_argument("--piezas", action="store_true", help="catálogo de piezas utilizables")
    ap.add_argument("--validar", metavar="ID")
    ap.add_argument("--guion", metavar="ID", help="escribe exports/GUION_<ID>.md")
    ap.add_argument("--nueva", metavar="ID", help="crea presentaciones/<ID>.json con un esqueleto")
    a = ap.parse_args()
    if a.piezas:
        for p in piezas():
            print(f"{p['clase']:28s} {'✓' if p['oscuro'] else '·'}{'E' if p['en'] else ' '} {p['bloque'][:28]:28s} {p['muestra'][:70]}")
    if a.nueva:
        if ruta(a.nueva).exists():
            raise SystemExit(f"ya existe {ruta(a.nueva)}")
        print("creada:", guardar(nueva(a.nueva)))
    if a.validar:
        e, w = validar(cargar(a.validar))
        for x in e:
            print("ERROR ", x)
        for x in w:
            print("aviso ", x)
        print(f"{len(e)} errores · {len(w)} avisos · {minutos_total(cargar(a.validar)):.1f} min de guion")
        sys.exit(1 if e else 0)
    if a.guion:
        d = cargar(a.guion)
        ruta_guion(d).write_text(guion_md(d), encoding="utf-8")
        print(ruta_guion(d))
    if a.lista or not any((a.piezas, a.nueva, a.validar, a.guion)):
        for id_, tit, idioma in listar():
            print(f"{id_:24s} {idioma}  {tit}")
