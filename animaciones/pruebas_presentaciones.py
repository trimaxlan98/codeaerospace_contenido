"""Pruebas de calidad de las presentaciones propias y de los temas (sin pytest: `python3 pruebas_presentaciones.py`).

  1. validación: el esqueleto es válido y cada error típico se detecta (orden, tipos, campos, piezas, id, ritmo)
  2. archivos: guardar → cargar devuelve lo mismo; las plantillas «_*.json» no se listan
  3. guion .md: una sección por diapositiva en el formato que lee la página, horas crecientes, ⚠️ donde hay advertencia
  4. temas: fuentes instaladas, paleta Manim completa, fondo del video = fondo del tema, contraste del texto (WCAG)
  5. decks construidos (`--decks ID`): número de diapositivas, video en cada diapositiva de video, notas = guion,
     sticker en las de texto y cita, y solo las fuentes del tema en el texto
  6. app (`--app`, sin pantalla): la pestaña «Nueva presentación» edita, añade, mueve, quita, valida y guarda
     (en una carpeta temporal) y la pestaña «Presentaciones» ve la presentación guardada
Sale con código 1 si algo falla. Uso: python3 pruebas_presentaciones.py [--decks que_es_code] [--app]
"""
import json
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import presentaciones_usuario as PU  # noqa: E402
import temas_espaciales as TE  # noqa: E402

FALLAS, OK = [], [0]


def prueba(cond, que):
    if cond:
        OK[0] += 1
    else:
        FALLAS.append(que)
        print("  ✗", que)


def con_error(d, texto):
    err, _ = PU.validar(d)
    return any(texto in e for e in err)


# ------------------------------------------------------------------ 1. validación
def t_validacion():
    print("1. validación")
    base = PU.nueva("prueba_val")
    err, av = PU.validar(base)
    prueba(not err, f"el esqueleto debe ser válido; errores: {err}")
    prueba(all("sin guion" in a for a in av), f"el esqueleto solo debe avisar de guiones vacíos; avisos: {av}")

    def variante(f):
        d = json.loads(json.dumps(base))
        f(d)
        return d
    prueba(con_error(variante(lambda d: d["diapos"].reverse()), "primera diapositiva debe ser la portada"), "portada fuera de lugar")
    prueba(con_error(variante(lambda d: d["diapos"].append({"tipo": "cierre", "guion": "x"})), "exactamente un cierre"), "dos cierres")
    prueba(con_error(variante(lambda d: d["diapos"].insert(1, {"tipo": "respaldo", "titulo": "R", "puntos": ["a"], "guion": "x"})),
                     "respaldo van después del cierre"), "respaldo antes del cierre")
    prueba(con_error(variante(lambda d: d["diapos"].append({"tipo": "texto", "titulo": "t", "puntos": ["a"], "guion": "x"})),
                     "después del cierre solo van"), "texto después del cierre")
    prueba(con_error(variante(lambda d: d["diapos"].insert(1, {"tipo": "grafica"})), "tipo desconocido"), "tipo desconocido")
    prueba(con_error(variante(lambda d: d["diapos"][3].update(clase="NoExiste")), "no está en el catálogo"), "pieza inexistente")
    prueba(con_error(variante(lambda d: d["diapos"][2].update(puntos=["", "  "])), "falta «puntos»"), "puntos vacíos")
    prueba(con_error(variante(lambda d: d["diapos"][1].update(titulo="   ")), "falta «titulo»"), "título en blanco")
    prueba(con_error(variante(lambda d: d.update(id="Mal Id")), "id inválido"), "id inválido")
    prueba(con_error(variante(lambda d: d.update(ritmo="rápido")), "ritmo"), "ritmo no numérico")
    prueba(con_error(variante(lambda d: d.update(diapos=[])), "no tiene diapositivas"), "sin diapositivas")
    _, av = PU.validar(variante(lambda d: d["diapos"][2].update(puntos=[f"p{i}" for i in range(8)])))
    prueba(any("8 puntos" in a for a in av), "más de 6 puntos debe avisar")
    _, av = PU.validar(variante(lambda d: d["diapos"][2].update(sticker=None)))
    prueba(any("sin sticker" in a for a in av), "texto sin sticker debe avisar")


# ------------------------------------------------------------------ 2. archivos
def t_archivos():
    print("2. archivos")
    viejo = PU.DIR
    with tempfile.TemporaryDirectory() as tmp:
        PU.DIR = Path(tmp)
        try:
            d = PU.nueva("ida_vuelta", "Ida y vuelta")
            d["diapos"][2]["puntos"] = ["uno", "dos"]
            d["diapos"][2]["cuidado"] = "no afirmar X"
            PU.guardar(d)
            (Path(tmp) / "_plantilla.json").write_text(json.dumps({"id": "_plantilla"}), encoding="utf-8")
            e = PU.cargar("ida_vuelta")
            prueba(e["titulo"] == "Ida y vuelta" and e["diapos"][2]["puntos"] == ["uno", "dos"], "guardar → cargar conserva los datos")
            prueba(e["diapos"][2]["cuidado"] == "no afirmar X", "se conserva la advertencia")
            prueba(all("guion" in x for x in json.loads(PU.ruta("ida_vuelta").read_text())["diapos"]), "el guion se guarda aunque esté vacío")
            prueba([i for i, _, _ in PU.listar()] == ["ida_vuelta"], "las plantillas con «_» no se listan")
            try:
                PU.guardar({**d, "id": "_malo"})
                prueba(False, "guardar con id inválido debe fallar")
            except ValueError:
                prueba(True, "")
        finally:
            PU.DIR = viejo


# ------------------------------------------------------------------ 3. guion
def _horas(md):
    return [m for m in re.findall(r"^\*[^\n]*?\*  ·  (\d+:\d\d|respaldo|backup)", md, re.M)]


def t_guion(ids):
    print("3. guion .md")
    for id_ in ids:
        d = PU.cargar(id_)
        md = PU.guion_md(d)
        bloques = re.findall(r"^## (\d+)\. ", md, re.M)
        prueba(len(bloques) == len(d["diapos"]) and bloques == [str(i) for i in range(1, len(d["diapos"]) + 1)],
               f"[{id_}] una sección «## N.» por diapositiva, en orden")
        hs = _horas(md)
        prueba(len(hs) == len(d["diapos"]), f"[{id_}] cada sección lleva su línea de hora ({len(hs)} de {len(d['diapos'])})")
        mins = [int(h.split(":")[0]) * 60 + int(h.split(":")[1]) for h in hs if ":" in h]
        prueba(mins == sorted(mins), f"[{id_}] las horas del guion crecen")
        prueba(md.count("> ⚠️") == sum(1 for x in d["diapos"] if x.get("cuidado")), f"[{id_}] una línea ⚠️ por advertencia")
        m = re.search(r"\*\*(\d+(?:\.\d+)?) min\*\*", md)
        prueba(m and abs(float(m.group(1)) - PU.minutos_total(d)) < 0.06, f"[{id_}] la duración del encabezado coincide")
        # mismo parseo que la página (pagina_plantilla.html): título y la línea siguiente partida por «·»
        for b in md.split("\n## ")[1:]:
            lineas = b.split("\n")
            prueba(re.match(r"^\d+\. .+", lineas[0]) and "·" in lineas[1], f"[{id_}] bloque legible por la página: {lineas[0][:40]}")


# ------------------------------------------------------------------ 4. temas
def _lum(h):
    c = [int(h.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contraste(a, b):
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


CLAVES_MANIM = {"FUENTE", "FUENTE_CIFRA", "PESO_CIFRA", "ESCALA_TEXTO", "FONDO", "TINTA", "TENUE", "C_EJE", "C_TIERRA",
                "C_TIERRA_2", "C_SAT", "C_ANT", "C_CIELO", "C_MAL", "C_OK", "C_PANEL"}


def t_temas():
    print(f"4. temas ({len(TE.TEMAS)})")
    for t in TE.TEMAS.values():
        for f in set(t.fuentes.values()) | ({t.manim["FUENTE"]} if t.manim else set()):
            fam = subprocess.run(["fc-list", f, "family"], capture_output=True, text=True).stdout
            prueba(bool(fam.strip()), f"[{t.id}] fuente instalada: {f}")
        prueba(t.manim is not None and CLAVES_MANIM <= set(t.manim), f"[{t.id}] paleta Manim completa")
        if t.manim:
            esperado = (t.pantalla or "#FFFFFF").lower()
            prueba(t.manim["FONDO"].lower() == esperado, f"[{t.id}] FONDO del video ({t.manim['FONDO']}) = pantalla ({esperado})")
            prueba(contraste(t.manim["TINTA"], t.manim["FONDO"]) >= 7, f"[{t.id}] texto del video legible (contraste ≥ 7)")
        fondo = t.pantalla or t.color["panel"]
        prueba(contraste(t.color["tinta"], fondo) >= 7, f"[{t.id}] tinta/fondo {contraste(t.color['tinta'], fondo):.1f} ≥ 7 (WCAG AAA)")
        prueba(contraste(t.color["tenue"], fondo) >= 4.5, f"[{t.id}] tenue/fondo {contraste(t.color['tenue'], fondo):.1f} ≥ 4.5 (AA)")
        prueba(contraste(t.color["acento"], fondo) >= 3, f"[{t.id}] acento/fondo {contraste(t.color['acento'], fondo):.1f} ≥ 3")
        prueba(t.generador in TE.F.GENERADORES or callable(t.generador), f"[{t.id}] generador de fondo registrado")


# ------------------------------------------------------------------ 5. decks construidos
NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main", "p": "http://schemas.openxmlformats.org/presentationml/2006/main"}


def t_decks(ids):
    from lxml import etree
    salida = PU.EXP / "presentaciones" / "espaciales"
    for id_ in ids:
        d = PU.cargar(id_)
        _, ds = PU.a_deck(d)
        pptxs = sorted(salida.glob(f"*/{id_}_*.pptx"))
        print(f"5. decks de «{id_}»: {len(pptxs)} construidos")
        prueba(bool(pptxs), f"[{id_}] hay al menos un deck construido")
        for p in pptxs:
            tema = TE.TEMAS.get(p.stem[len(id_) + 1:])
            z = zipfile.ZipFile(p)
            slides = sorted((n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)), key=lambda n: int(re.findall(r"\d+", n)[0]))
            et = p.parent.name
            prueba(len(slides) == len(ds), f"[{et}] {len(slides)} diapositivas = {len(ds)}")
            fuentes_ok = (set(tema.fuentes.values()) | {"Orbitron"}) if tema else None
            for i, (sn, x) in enumerate(zip(slides, ds), 1):
                xml = etree.fromstring(z.read(sn))
                rels = z.read(sn.replace("slides/", "slides/_rels/") + ".rels").decode()
                if x["tipo"] == "video":
                    prueba("video" in rels and ".mp4" in rels, f"[{et}] diapositiva {i}: tiene el video incrustado")
                if x["tipo"] in ("texto", "cita", "respaldo") and x.get("sticker"):
                    prueba(len(xml.findall(".//p:pic", NS)) >= 1, f"[{et}] diapositiva {i}: tiene el sticker")
                if fuentes_ok:
                    usadas = {e.get("typeface") for e in xml.findall(".//a:latin", NS)}
                    prueba(usadas <= fuentes_ok, f"[{et}] diapositiva {i}: solo fuentes del tema (sobran {usadas - fuentes_ok})")
                nota = next((n for n in z.namelist() if n == f"ppt/notesSlides/notesSlide{i}.xml"), None)
                if nota and x["guion"].strip():
                    txt = "".join(etree.fromstring(z.read(nota)).itertext())
                    prueba(x["guion"].strip()[:60] in txt, f"[{et}] diapositiva {i}: las notas llevan el guion")
                    if x.get("cuidado"):
                        prueba("⚠️" in txt, f"[{et}] diapositiva {i}: las notas llevan la advertencia")


def t_app():
    import os
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    print("6. app (sin pantalla)")
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    viejo = PU.DIR
    with tempfile.TemporaryDirectory() as tmp:
        PU.DIR = Path(tmp)
        try:
            PU.guardar(json.loads((viejo / "que_es_code.json").read_text(encoding="utf-8")))
            import render_launcher as RL
            w = RL.Launcher()
            w.show()
            app.processEvents()
            N, P_ = w.nueva, w.presentaciones
            prueba(N.d and N.d["id"] == "que_es_code", "la pestaña abre la presentación guardada")
            prueba(N.tema.count() == len(TE.TEMAS), f"el selector de tema lista los {len(TE.TEMAS)} temas")
            prueba(N.b_construir.isEnabled(), "una presentación válida se puede construir")
            N.duplicar("copia_prueba")
            N.lista.setCurrentRow(1)
            app.processEvents()
            N.e_titulo.setText("Editado")
            N.e_titulo.textEdited.emit("Editado")
            N.e_puntos.setPlainText("a\n\nb")
            app.processEvents()
            prueba(N.d["diapos"][1]["titulo"] == "Editado" and N.d["diapos"][1]["puntos"] == ["a", "b"], "editar título y puntos")
            n0 = len(N.d["diapos"])
            N.anadir("cita")
            prueba(len(N.d["diapos"]) == n0 + 1 and not N.b_construir.isEnabled(), "una cita vacía bloquea construir")
            N.quitar()
            prueba(len(N.d["diapos"]) == n0 and N.b_construir.isEnabled(), "quitarla desbloquea")
            prueba(N.guardar() and (Path(tmp) / "copia_prueba.json").exists(), "guardar escribe el JSON")
            w.tabs.setCurrentIndex(1)  # como el usuario: de «Nueva presentación» de vuelta a «Presentaciones»
            w.tabs.setCurrentIndex(0)
            app.processEvents()
            etq = [P_.lista_pres.item(i).text() for i in range(P_.lista_pres.count())]
            prueba(sum("propia" in e for e in etq) == 2, "la pestaña Presentaciones ve las dos propias")
            w.nueva.sucio = False
            w.close()
        finally:
            PU.DIR = viejo


if __name__ == "__main__":
    decks = sys.argv[sys.argv.index("--decks") + 1].split(",") if "--decks" in sys.argv else []
    t_validacion()
    t_archivos()
    t_guion([i for i, _, _ in PU.listar()])
    t_temas()
    if decks:
        t_decks(decks)
    if "--app" in sys.argv:
        t_app()
    print(f"\n{OK[0]} comprobaciones correctas · {len(FALLAS)} fallas")
    sys.exit(1 if FALLAS else 0)
