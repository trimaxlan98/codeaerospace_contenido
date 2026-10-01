"""Compara una traducción de presentación (tesis_seminario_en.py) contra el original en español.

Comprueba, diapositiva por diapositiva: mismo tipo, mismo video, misma cantidad de viñetas, mismas cifras
(tokens numéricos de título, subtítulo, viñetas y frase), advertencias «cuidado» presentes, citas literales en
inglés conservadas (MUST / MUST NOT), y longitud de textos razonable para el diseño.
Uso: python3 verificar_traduccion.py [seminario]   → imprime problemas; sale con código 1 si los hay.
"""
import importlib
import re
import sys


def nums(t):
    t = t.replace(",", "").replace("−", "-")
    return sorted(re.findall(r"\d+(?:\.\d+)?", t))


def textos(d):
    """Textos de pantalla (no el guion): título/sub/viñetas/frase."""
    t = d[0]
    if t == "seccion":
        return [d[1], d[2]]
    if t == "video":
        return [d[2], d[3]]
    if t in ("texto", "respaldo"):
        return [d[1], d[2], *d[3]]
    if t == "cita":
        return [d[1], d[2]]
    return []


def main(nombre="seminario"):
    es = importlib.import_module({"seminario": "tesis_seminario"}[nombre])
    en = importlib.import_module({"seminario": "tesis_seminario_en"}[nombre])
    problemas = []
    if len(es.DIAPOS) != len(en.DIAPOS):
        problemas.append(f"distinto número de diapositivas: {len(es.DIAPOS)} vs {len(en.DIAPOS)}")
    for i, (a, b) in enumerate(zip(es.DIAPOS, en.DIAPOS), 1):
        if a[0] != b[0]:
            problemas.append(f"#{i} tipo {a[0]} vs {b[0]}")
            continue
        if a[0] == "video" and a[1] != b[1]:
            problemas.append(f"#{i} video {a[1]} vs {b[1]}")
        ta, tb = textos(a), textos(b)
        if len(ta) != len(tb):
            problemas.append(f"#{i} cantidad de textos {len(ta)} vs {len(tb)}")
            continue
        for x, y in zip(ta, tb):
            if nums(x) != nums(y):
                problemas.append(f"#{i} cifras distintas: {nums(x)} vs {nums(y)}  «{y[:50]}»")
            if len(x) > 40 and len(y) > 1.35 * len(x):
                problemas.append(f"#{i} texto mucho más largo ({len(x)}→{len(y)}): «{y[:60]}»")
        # guion y advertencia
        for k in ("MUST NOT", "MUST"):
            ca = sum(s.count(k) for s in ta)
            cb = sum(s.count(k) for s in tb)
            if ca != cb:
                problemas.append(f"#{i} cita normativa «{k}» {ca} vs {cb}")
        if len(a) != len(b):
            problemas.append(f"#{i} distinta cantidad de campos (¿falta la advertencia «cuidado»?): {len(a)} vs {len(b)}")
    for k in es.CFG:
        if k not in en.CFG:
            problemas.append(f"CFG sin clave {k}")
    from tesis_decks import guion_de
    pal_es = sum(len(guion_de(d)[0].split()) for d in es.DIAPOS if d[0] != "respaldo")
    pal_en = sum(len(guion_de(d)[0].split()) for d in en.DIAPOS if d[0] != "respaldo")
    print(f"palabras de guion (sin respaldo): ES {pal_es} · EN {pal_en} → EN a 140 ppm = {pal_en / 140:.1f} min (ES {pal_es / 140:.1f})")
    # cifras del guion (dígitos escritos en cifras)
    for i, (a, b) in enumerate(zip(es.DIAPOS, en.DIAPOS), 1):
        na, nb = nums(guion_de(a)[0]), nums(guion_de(b)[0])
        if na != nb:
            problemas.append(f"#{i} cifras escritas en el guion difieren: ES {na} EN {nb}")
    for p in problemas:
        print("✗", p)
    print("OK" if not problemas else f"{len(problemas)} problema(s)")
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main(*(sys.argv[1:2] or ["seminario"])))
