#!/usr/bin/env python3
"""codeae — línea de comandos ÚNICA del estudio de contenido de Co.De Aerospace.

Reúne los motores que antes se usaban por separado: carruseles (JSON → PNG), reels y logos animados (Manim),
audio sintético sincronizado, verificación (loops, rigor, pruebas), índice/galería, paquetes de entrega y
subida a Drive. La app de escritorio y los scripts llaman a esto: un solo punto de entrada.

    codeae piezas [--tipo carrusel|video] [--json]     lista todo lo que se puede producir
    codeae estado [--json]                             qué está renderizado y qué falta
    codeae validar [ID …|--todo]                       valida specs de carruseles (y que cada video tenga audio)
    codeae render ID … [--sin-audio] [--png]           renderiza (carruseles; videos + audio + verificación)
    codeae audio ID …                                  rehace solo el audio de videos ya renderizados
    codeae verificar [ID …|--todo] [--pruebas]         loops, costura de audio y (con --pruebas) la batería de pruebas
    codeae indice                                      INDICE.md, GALERIA.html, registro CSV, PARA_DRIVE.md y la página de revisión
    codeae paquete ID … [--nombre X]                   copia los FINALES de esas piezas a exports/estudio/paquetes/<X>/
    codeae subir PAQUETE [--confirmo]                  lista (y solo con --confirmo sube) un paquete a Drive: Mac-Pro-code/Estudio-CoDe/

ID de carrusel: «serie/id» o solo «id» (las variantes A/B salen como id-b, id-c). ID de video: nombre de la escena.
Salidas: exports/estudio/ (carruseles, paquetes, informes) y exports/marca-codeaerospace/ (videos de marca).
Subir a Drive SIEMPRE lista antes y exige --confirmo (decisión del dueño).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EST = REPO / "exports" / "estudio"
MARCA = REPO / "exports" / "marca-codeaerospace"
EXP = REPO / "studio/content/animations/experimentacion"
for p in ("studio/tools", "studio/content/manim_extensions", "animaciones", "redes/carruseles"):
    sys.path.insert(0, str(REPO / p))

DRIVE_RAIZ = "gdrive:Mac-Pro-code/Estudio-CoDe"


@dataclass
class Video:
    id: str
    archivo: str                 # script con la escena (en EXP)
    salida: Path                 # carpeta donde queda el mp4
    resolucion: str              # "1080,1920"
    fps: int
    audio: str                   # clave del grupo de audio: "marca" | "reels"
    audio_fn: object = field(default=None, repr=False)
    loop: bool = False
    grupo: str = ""
    escena: str = ""             # nombre de la clase si difiere del id (RotulosAerospace ← DemoRotulosAerospace)


def _videos():
    """Registro de videos, construido desde los diccionarios de audio (una sola fuente de verdad por escena)."""
    import sonido_marca as SM
    import sonido_reels as SR
    v = []
    for n, f in SM.ESCENAS.items():
        if n == "RotulosAerospace":
            v.append(Video(n, "31-rotulos-aerospace.py", MARCA, "1920,1080", 60, "marca", f, grupo="marca-horizontal", escena="DemoRotulosAerospace"))
        else:                                              # LogoCoDeVertical se renderiza a 1080×1920
            v.append(Video(n, "30-logo-co-de-aerospace.py", MARCA, "1080,1920" if n == "LogoCoDeVertical" else "1920,1080", 60, "marca", f, grupo="marca-horizontal"))
    for n, f in SM.ESCENAS_V.items():
        v.append(Video(n, "32-marca-vertical.py", MARCA / "vertical", "1080,1920", 30, "marca", f, grupo="marca-vertical"))
    for n, f in SM.ESCENAS_LE.items():
        v.append(Video(n, "34-logo-entornos.py", EST / "logo_entornos/animados", "1080,1920", 30, "marca", f, grupo="logo-entornos"))
    for n, (f, T, d) in SR.REELS.items():
        v.append(Video(n, "33-reels-promo.py", MARCA / "reels-promo", "1080,1920", 30, "reels", (f, T, d), True, "reels-promo"))
    for n, (f, T, d) in SR.REELS_VIVO.items():
        v.append(Video(n, "35-logo-vivo.py", EST / "logo_vivo", "1080,1920", 30, "reels", (f, T, d), True, "logo-vivo"))
    for n, (f, T, d) in SR.REELS_DATOS.items():
        v.append(Video(n, "36-reel-datos-reales.py", EST / "reels_datos", "1080,1920", 30, "reels", (f, T, d), True, "datos-reales"))
    for n, (f, T, d) in SR.REELS_DIVULGACION.items():
        v.append(Video(n, "37-reels-divulgacion.py", EST / "reels_divulgacion", "1080,1920", 30, "reels", (f, T, d), True, "divulgacion"))
    for n, (f, T, d) in SR.REELS_ATS.items():
        v.append(Video(n, "38-reels-ats.py", EST / "reels_ats", "1080,1920", 30, "reels", (f, T, d), True, "ats"))
    for n, (f, T, d) in SR.REELS_TRIAGE.items():
        v.append(Video(n, "39-reels-triage.py", EST / "reels_triage", "1080,1920", 30, "reels", (f, T, d), True, "triage"))
    for n, (f, T, d) in SR.REELS_CLIMA.items():
        v.append(Video(n, "40-reels-clima.py", EST / "reels_clima", "1080,1920", 30, "reels", (f, T, d), True, "clima"))
    for n, (f, T, d) in SR.REELS_IA.items():
        v.append(Video(n, "41-reels-ia.py", EST / "reels_ia", "1080,1920", 30, "reels", (f, T, d), True, "ia"))
    return {x.id: x for x in v}


def _specs():
    import motor_carrusel as MC
    salida = {}
    for r in sorted((REPO / "redes/carruseles/specs").rglob("*.json")):
        base = json.loads(r.read_text(encoding="utf-8"))
        for s in MC.expandir_variantes(base):
            salida[s["id"]] = (r, s)
    return salida


def _entorno():
    e = dict(os.environ)
    e["PYTHONPATH"] = os.pathsep.join([str(REPO / "studio/content/manim_extensions"), str(REPO / "animaciones"), e.get("PYTHONPATH", "")])
    return e


# ── comandos ─────────────────────────────────────────────────────────────────────────────────────

def cmd_piezas(a):
    vs, cs = _videos(), _specs()
    filas = []
    for i, (r, s) in cs.items():
        filas.append({"id": i, "tipo": "carrusel", "grupo": s["serie"], "detalle": f"{len(s['laminas'])} láminas · {s.get('fondo', {}).get('tema', 'orbita')}",
                      "estado": s.get("estado", ""), "renderizado": (EST / "carruseles" / s["serie"] / i / f"{i}_hoja.jpg").exists()})
    for i, v in vs.items():
        con = v.salida / "con_sonido" / f"{i}.mp4"
        filas.append({"id": i, "tipo": "video", "grupo": v.grupo, "detalle": f"{v.resolucion.replace(',', '×')} · {v.fps} fps" + (" · loop" if v.loop else ""),
                      "estado": "", "renderizado": con.exists()})
    if a.tipo:
        filas = [f for f in filas if f["tipo"] == a.tipo]
    if a.json:
        print(json.dumps(filas, ensure_ascii=False, indent=1))
        return 0
    g = None
    for f in sorted(filas, key=lambda f: (f["tipo"], f["grupo"], f["id"])):
        if (f["tipo"], f["grupo"]) != g:
            g = (f["tipo"], f["grupo"])
            print(f"\n{f['tipo']} · {f['grupo']}")
        print(f"  {'✓' if f['renderizado'] else '·'} {f['id']:42s} {f['detalle']}{'   ⛔ no publicar' if f['estado'] == 'no_publicar' else ''}")
    print(f"\n{len(filas)} piezas ({sum(f['renderizado'] for f in filas)} renderizadas)")
    return 0


def cmd_estado(a):
    vs, cs = _videos(), _specs()
    datos = {"carruseles": len(cs), "carruseles_renderizados": sum((EST / 'carruseles' / s['serie'] / i / f'{i}_hoja.jpg').exists() for i, (_, s) in cs.items()),
             "videos": len(vs), "videos_con_sonido": sum((v.salida / 'con_sonido' / f'{i}.mp4').exists() for i, v in vs.items()),
             "paquetes": sorted(p.name for p in (EST / "paquetes").glob("*")) if (EST / "paquetes").exists() else []}
    print(json.dumps(datos, ensure_ascii=False, indent=1) if a.json else "\n".join(f"{k}: {v}" for k, v in datos.items()))
    return 0


def _resolver(ids, vs, cs):
    for i in ids:
        i = i.split("/")[-1]
        if i in cs:
            yield "carrusel", i
        elif i in vs:
            yield "video", i
        else:
            raise SystemExit(f"codeae: no conozco «{i}» (usa `codeae piezas`)")


def cmd_validar(a):
    import motor_carrusel as MC
    vs, cs = _videos(), _specs()
    ids = list(cs) + list(vs) if a.todo or not a.ids else [x for _, x in _resolver(a.ids, vs, cs)]
    malos = 0
    for i in ids:
        if i in cs:
            errores, avisos = MC.validar(cs[i][1])
            print(("✗ " if errores else "✓ ") + i + ("  " + "; ".join(errores) if errores else "") + (f"  (avisos: {len(avisos)})" if avisos else ""))
            malos += bool(errores)
        else:
            v = vs[i]
            ok = (EXP / v.archivo).exists() and v.audio_fn is not None
            print(("✓ " if ok else "✗ ") + i + ("" if ok else "  falta la escena o su audio"))
            malos += not ok
    return 1 if malos else 0


def _render_video(v, sin_audio=False, png=False):
    v.salida.mkdir(parents=True, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="codeae_")
    try:
        cmd = ["manim", "render", "-r", v.resolucion, "--fps", str(v.fps), "--disable_caching", "--media_dir", tmp, str(EXP / v.archivo), v.escena or v.id]
        r = subprocess.run(cmd, cwd=REPO, env=_entorno(), capture_output=True, text=True)
        hallado = list(Path(tmp, "videos").rglob(f"{v.escena or v.id}.mp4"))
        if r.returncode or not hallado:
            print(r.stdout[-1500:], r.stderr[-1500:])
            return False
        shutil.copy2(hallado[0], v.salida / f"{v.id}.mp4")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if not sin_audio:
        _audio(v)
    return True


def _audio(v):
    import sonido_marca as SM
    import sonido_reels as SR
    if not (v.salida / f"{v.id}.mp4").exists():
        print(f"✗ {v.id}: no está renderizado (codeae render {v.id})")
        return False
    (SR if v.audio == "reels" else SM).mezclar(v.salida, {v.id: v.audio_fn})
    return True


def cmd_render(a):
    import motor_carrusel as MC
    vs, cs = _videos(), _specs()
    malos = 0
    for tipo, i in _resolver(a.ids, vs, cs):
        if tipo == "carrusel":
            try:
                _, avisos = MC.renderizar(cs[i][1])
                print(f"✓ {i}" + (f"  (avisos: {len(avisos)})" if avisos else ""))
            except Exception as e:
                print(f"✗ {i}: {e}")
                malos += 1
        else:
            ok = _render_video(vs[i], a.sin_audio, a.png)
            print(("✓ " if ok else "✗ ") + i)
            malos += not ok
            if ok and not a.sin_audio and vs[i].loop:
                malos += cmd_verificar(argparse.Namespace(ids=[i], todo=False, pruebas=False)) != 0
    return 1 if malos else 0


def cmd_audio(a):
    vs, cs = _videos(), _specs()
    return 0 if all(_audio(vs[i]) for t, i in _resolver(a.ids, vs, cs) if t == "video") else 1


def cmd_verificar(a):
    vs, cs = _videos(), _specs()
    malos = 0
    ids = [i for i in vs] if a.todo or not a.ids else [i for t, i in _resolver(a.ids, vs, cs) if t == "video"]
    ruta = REPO / "studio/tools/verificar_loop.py"
    for i in ids:
        v = vs[i]
        mp4 = v.salida / "con_sonido" / f"{i}.mp4"
        if not (v.loop and mp4.exists()):
            continue
        r = subprocess.run([sys.executable, str(ruta), str(mp4)], capture_output=True, text=True)
        print(r.stdout.strip())
        malos += r.returncode != 0
    if a.pruebas:
        r = subprocess.run([sys.executable, str(REPO / "redes/pruebas_estudio.py")], cwd=REPO)
        malos += r.returncode != 0
    return 1 if malos else 0


def cmd_indice(a):
    for s in ("redes/indice_estudio.py", "redes/pagina_estudio.py"):
        r = subprocess.run([sys.executable, str(REPO / s)], cwd=REPO)
        if r.returncode:
            return r.returncode
    return 0


def _finales(i, vs, cs):
    """Archivos FINALES de una pieza (nunca intermedios)."""
    if i in cs:
        _, s = cs[i]
        c = EST / "carruseles" / s["serie"] / i
        arch = sorted(c.glob(f"{i}_[0-9][0-9].png")) + [c / f"{i}_pie.txt", c / f"{i}_alt.txt", c / f"{i}_CUIDADO.txt"]
        return "carruseles/" + s["serie"] + "/" + i, [x for x in arch if x.exists()]
    v = vs[i]
    arch = [v.salida / "con_sonido" / f"{i}.mp4"] + sorted((v.salida / "con_voz").glob(f"{i}_voz*.mp4"))   # con voz en off (A/B)
    return "videos/" + v.grupo, [x for x in arch if x.exists()]


def cmd_paquete(a):
    vs, cs = _videos(), _specs()
    nombre = a.nombre or f"{date.today().isoformat()}"
    raiz = EST / "paquetes" / nombre
    n = 0
    for t, i in _resolver(a.ids, vs, cs):
        if t == "carrusel" and cs[i][1].get("estado") == "no_publicar":
            print(f"⛔ {i}: marcado no_publicar, se omite")
            continue
        sub, arch = _finales(i, vs, cs)
        if not arch:
            print(f"· {i}: sin finales (¿renderizado?)")
            continue
        (raiz / sub).mkdir(parents=True, exist_ok=True)
        for f in arch:
            shutil.copy2(f, raiz / sub / f.name)
            n += 1
    lista = sorted(p.relative_to(raiz) for p in raiz.rglob("*") if p.is_file()) if raiz.exists() else []
    (raiz / "LEEME.txt").write_text("Paquete del estudio Co.De Aerospace\n" + "\n".join(map(str, lista)) + "\n", encoding="utf-8") if raiz.exists() else None
    print(f"paquete «{nombre}»: {n} archivos → {raiz}")
    return 0


def cmd_subir(a):
    raiz = EST / "paquetes" / a.paquete
    if not raiz.exists():
        raise SystemExit(f"codeae: no existe el paquete «{a.paquete}» (codeae paquete …)")
    archivos = sorted(p for p in raiz.rglob("*") if p.is_file())
    mb = sum(p.stat().st_size for p in archivos) / 1e6
    destino = f"{DRIVE_RAIZ}/{a.paquete}"
    print(f"Se subirían {len(archivos)} archivos ({mb:.1f} MB) a {destino}:")
    for p in archivos:
        print("  ", p.relative_to(raiz))
    if not a.confirmo:
        print("\nNo se subió nada. Repite con --confirmo cuando el dueño lo apruebe.")
        return 0
    return subprocess.run(["rclone", "copy", str(raiz), destino, "-P", "--exclude", "LEEME.txt"]).returncode


def main(argv=None):
    ap = argparse.ArgumentParser(prog="codeae", description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("piezas"); s.add_argument("--tipo", choices=["carrusel", "video"]); s.add_argument("--json", action="store_true"); s.set_defaults(f=cmd_piezas)
    s = sub.add_parser("estado"); s.add_argument("--json", action="store_true"); s.set_defaults(f=cmd_estado)
    s = sub.add_parser("validar"); s.add_argument("ids", nargs="*"); s.add_argument("--todo", action="store_true"); s.set_defaults(f=cmd_validar)
    s = sub.add_parser("render"); s.add_argument("ids", nargs="+"); s.add_argument("--sin-audio", action="store_true"); s.add_argument("--png", action="store_true"); s.set_defaults(f=cmd_render)
    s = sub.add_parser("audio"); s.add_argument("ids", nargs="+"); s.set_defaults(f=cmd_audio)
    s = sub.add_parser("verificar"); s.add_argument("ids", nargs="*"); s.add_argument("--todo", action="store_true"); s.add_argument("--pruebas", action="store_true"); s.set_defaults(f=cmd_verificar)
    s = sub.add_parser("indice"); s.set_defaults(f=cmd_indice)
    s = sub.add_parser("paquete"); s.add_argument("ids", nargs="+"); s.add_argument("--nombre"); s.set_defaults(f=cmd_paquete)
    s = sub.add_parser("subir"); s.add_argument("paquete"); s.add_argument("--confirmo", action="store_true"); s.set_defaults(f=cmd_subir)
    a = ap.parse_args(argv)
    return a.f(a)


if __name__ == "__main__":
    sys.exit(main())
