#!/usr/bin/env python3
"""Empaqueta una PRESENTACION de presentacion desde la linea de comandos: de un .py
de manim a un .pptx que el ponente abre y presenta.

Es el hermano de consola de lo que hace la app (Proyectos -> tipo presentacion). Los
dos usan EXACTAMENTE el mismo cortador (`cortar_presentacion.py`, el que corre dentro
del contenedor) y el mismo constructor de deck (`app.presentaciones.construir_deck`):
esta herramienta solo anade el render y el LEEME. Si la logica viviera dos
veces, la presentacion que arma la app y la que arma la consola se irian separando.

Uso:

    studio/backend/venv/bin/python studio/tools/empaquetar_presentacion.py \
        studio/content/presentaciones/ventana-de-contacto
    ... --escena VentanaDeContacto   si el archivo tiene mas de una
    ... --formato horizontal         horizontal 16:9 | clasico 4:3 | cuadrado
    ... --fondo blanco               marca (defecto) | blanco | pizarra | #rrggbb
    ... --calidad qh                 ql | qm | qh (defecto)
    ... --video                      deck de mp4 en vez de GIF
    ... --bucle                      los GIF se repiten (presentacion de una parte)
    ... --titulo "Ventana de contacto"
    ... --sin-pptx                   solo los fragmentos y los posters
    ... --salida DIR

Deja todo en `exports/presentaciones/<slug>/<formato>-<fondo>/`:

    scene.py            el script tal cual lo vio manim
    completa.mp4        el render entero, sin cortar
    pasos.json          los instantes de clic que anoto la escena
    fragmentos/NN.mp4   un fragmento por paso
    fragmentos/NN.gif   lo mismo en GIF (el deck de respaldo)
    posters/NN.png      el primer fotograma de cada fragmento
    <slug>.pptx         el deck, un slide por fragmento
    LEEME.md            que hacer con esto en la sala

Acepta un directorio con la escena dentro o un .py suelto: las animaciones de
`studio/content/animations/` se empaquetan tal cual, sin tocarlas.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "studio" / "backend"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app import branding                       # noqa: E402
from app.presentaciones import construir_deck          # noqa: E402
from app.scenes import detect_scenes           # noqa: E402
import cortar_presentacion                            # noqa: E402

IMAGEN = "codeaerospace_contenido-manim"
SALIDA = REPO / "exports" / "presentaciones"
FORMATOS = ("horizontal", "clasico", "cuadrado")
CALIDADES = ("ql", "qm", "qh")


def visible(ruta: Path) -> str:
    """La ruta como conviene leerla: relativa al repo si cuelga de el, y
    absoluta si `--salida` apunta fuera."""
    try:
        return str(ruta.relative_to(REPO))
    except ValueError:
        return str(ruta)


def slugify(texto: str) -> str:
    ascii_txt = (unicodedata.normalize("NFKD", texto)
                 .encode("ascii", "ignore").decode("ascii"))
    return re.sub(r"[^a-z0-9]+", "-", ascii_txt.lower()).strip("-")


# ── 1. la escena ─────────────────────────────────────────────────────────────

def resolver_escena(ruta: Path, pedida: str | None) -> tuple[Path, str]:
    """El .py y el nombre de la clase."""
    if ruta.is_dir():
        candidatos = sorted(ruta.glob("*.py"))
        if not candidatos:
            sys.exit(f"{ruta} no tiene ningun .py")
        ruta = candidatos[0] if len(candidatos) == 1 else ruta / "escena.py"
    if not ruta.is_file():
        sys.exit(f"no existe {ruta}")
    escenas = detect_scenes(ruta.read_text(encoding="utf-8"))
    if not escenas:
        sys.exit(f"{ruta}: no encontre ninguna clase Scene")
    if pedida:
        if pedida not in escenas:
            sys.exit(f"{ruta}: no tiene la escena {pedida!r}"
                     f" (hay {', '.join(escenas)})")
        return ruta, pedida
    if len(escenas) > 1:
        sys.exit(f"{ruta} tiene {len(escenas)} escenas ({', '.join(escenas)}):"
                 " elige una con --escena")
    return ruta, escenas[0]


# ── 2. el render ─────────────────────────────────────────────────────────────

def renderizar(script: Path, escena: str, trabajo: Path, args) -> Path:
    """Un render, en el contenedor, con el repo montado read-only.

    Es lo unico que esta herramienta hace por su cuenta: en la app, el render
    va por la cola normal de jobs.
    """
    scene_py = trabajo / "scene.py"
    # tipo="presentacion": garantiza el lienzo tambien en un script que no
    # llame a `presentacion.lienzo()` — que es el caso de las ~60 animaciones
    # de studio/content/animations/. Sin esto, --formato y --fondo se
    # ignorarian en silencio.
    scene_py.write_text(
        branding.aplicar(script.read_text(encoding="utf-8"), tipo="presentacion"),
        encoding="utf-8")

    entorno = {"PRESENTACION_FORMATO": args.formato, "PRESENTACION_FONDO": args.fondo,
               "PRESENTACION_CALIDAD": args.calidad}
    cmd = ["docker", "run", "--rm", "--network", "none",
           "--user", f"{os.getuid()}:{os.getgid()}", "-e", "HOME=/tmp"]
    for k, v in entorno.items():
        cmd += ["-e", f"{k}={v}"]
    cmd += ["-v", f"{REPO}:/workspace:ro", "-v", f"{trabajo}:/media",
            IMAGEN, "manim", "render", f"-{args.calidad}", "--disable_caching",
            "--media_dir", "/media", "/media/scene.py", escena]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        cola = "\n".join(proc.stderr.strip().splitlines()[-15:])
        sys.exit(f"FALLO el render (exit {proc.returncode}):\n{cola}")

    # La carpeta de manim depende de resolucion y fps (1080p60, 480p30...): se
    # busca, y se coge la MAS RECIENTE por si la presentacion ya se renderizo antes
    # en otra calidad.
    candidatos = list((trabajo / "videos").rglob(f"{escena}.mp4"))
    if not candidatos:
        sys.exit(f"el render no dejo video en {trabajo / 'videos'}")
    completa = trabajo / "completa.mp4"
    shutil.copyfile(max(candidatos, key=lambda p: p.stat().st_mtime), completa)
    return completa


# ── 3. el informe en la sala ─────────────────────────────────────────────────

LEEME = """# {titulo}

Presentacion de presentacion generada por ManimStudio.
Formato {formato} · fondo {fondo} ({hex}) · {n} fragmento(s) · {dur:.1f} s en total.

## En la sala

Abre `{pptx}` y presenta. Cada fragmento esta en su propio slide y arranca
solo al entrar: **avanzas con la flecha, como con cualquier slide**. Cuando
un fragmento termina se queda congelado en su ultima imagen, que es la
misma con la que empresentacion el siguiente — el salto de slide no se ve.

Los pasos, en orden:

{pasos}

## Si lo quieres en TU plantilla

Copia los slides (Ctrl+A en el panel de miniaturas, Ctrl+C, y pegar en tu
presentacion con la opcion "usar el tema de destino"). El fondo de cada slide
esta pintado de `{fondo}` ({hex}): si tu plantilla usa otro color, vuelve a
generar la presentacion con `--fondo <tu color>` en vez de repintarlo a mano, o el
video se vera como un recorte sobre un fondo distinto.

## Si algo falla en la sala

{rescate}
- **No hay PowerPoint**: `completa.mp4` es la presentacion entera de corrido, y
  `posters/` tiene la imagen fija de cada paso para pegar en cualquier cosa.

## Que hay aqui

    completa.mp4        el render entero, sin cortar
    fragmentos/NN.mp4   un fragmento por paso
    fragmentos/NN.gif   lo mismo en GIF (el deck de respaldo)
    posters/NN.png      la primera imagen de cada fragmento
    pasos.json          los instantes de corte que anoto la escena
    scene.py            el script tal cual lo vio manim
"""

# El consejo de rescate depende del deck: en el de GIF no hay nada sobre lo
# que hacer clic, asi que decirlo solo confundiria a quien lo lea con la sala
# llena.
RESCATE_VIDEO = """- **El video no arranca solo**: haz clic sobre el. Ocupa el slide entero,
  asi que un clic en cualquier parte lo dispara. Si vas a presentar en un
  equipo ajeno, vuelve a generar la presentacion SIN `--video`: el deck de GIF
  arranca solo en todas las versiones de PowerPoint, sin depender de nada."""

RESCATE_GIF = """- **Una imagen se queda quieta**: es un GIF, y algunas versiones antiguas de
  PowerPoint solo los animan en modo presentacion (F5), no en la vista de
  edicion. Prueba con F5 antes de dar nada por roto."""


def escribir_leeme(trabajo: Path, informe: dict, args, titulo: str,
                   pptx: Path | None, fondo_hex: str) -> None:
    pasos = "\n".join(
        f"{i}. **{fr['etiqueta']}** — {fr['duracion']:.1f} s"
        for i, fr in enumerate(informe["fragmentos"], start=1))
    (trabajo / "LEEME.md").write_text(LEEME.format(
        titulo=titulo, formato=args.formato, fondo=args.fondo, hex=fondo_hex,
        n=informe["total"], dur=informe["duracion"],
        pptx=pptx.name if pptx else "(no se genero)", pasos=pasos,
        rescate=RESCATE_VIDEO if args.video else RESCATE_GIF),
        encoding="utf-8")


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("ruta", type=Path, help="el .py de la presentacion, o su directorio")
    p.add_argument("--escena", help="clase Scene, si el archivo tiene varias")
    p.add_argument("--formato", default="horizontal", choices=FORMATOS)
    p.add_argument("--fondo", default="marca",
                   help="marca | blanco | pizarra | #rrggbb")
    p.add_argument("--calidad", default="qh", choices=CALIDADES)
    p.add_argument("--titulo", help="titulo de la presentacion (defecto: del slug)")
    p.add_argument("--video", action="store_true",
                   help="deck de mp4 en vez de GIF: pesa menos, pero el "
                        "autoplay hay que verificarlo una vez")
    p.add_argument("--bucle", action="store_true",
                   help="los GIF se repiten (presentacion decorativa de una parte)")
    p.add_argument("--sin-pptx", action="store_true", dest="sin_pptx")
    p.add_argument("--salida", type=Path, help="directorio de salida")
    args = p.parse_args()

    script, escena = resolver_escena(args.ruta, args.escena)
    # El nombre de la presentacion es el del DIRECTORIO cuando se da uno: dentro se
    # llama `escena.py`, que no identifica nada.
    origen = args.ruta.name if args.ruta.is_dir() else script.stem
    slug = slugify(origen) or "presentacion"
    titulo = args.titulo or slug.replace("-", " ").capitalize()
    trabajo = args.salida or (SALIDA / slug /
                              f"{args.formato}-{slugify(args.fondo) or 'color'}")
    trabajo.mkdir(parents=True, exist_ok=True)

    print(f"\n{titulo}  [{escena} · {args.formato} · {args.fondo} · {args.calidad}]")
    completa = renderizar(script, escena, trabajo, args)

    # El MISMO cortador que corre dentro del contenedor cuando la presentacion se
    # arma desde la app. `presentacion.lienzo()` escribio pasos.json en el media_dir,
    # que aqui es el propio directorio de trabajo.
    plan = {
        "proyecto": titulo,
        "raiz": str(REPO),
        "destino": visible(trabajo),
        "gif": True,
        "bucle": args.bucle,
        "escenas": [{
            "titulo": titulo,
            "video": visible(completa),
            "pasos_json": visible(trabajo / "pasos.json"),
        }],
    }
    informe = cortar_presentacion.cortar(plan)
    if not informe.get("ok"):
        sys.exit(f"el corte fallo: {informe.get('error')}")

    print(f"    presentacion: {informe['resolucion']} · {informe['duracion']:.2f} s repartidos en fragmentos")
    for aviso in informe["avisos"]:
        print(f"    AVISO: {aviso}")
    print(f"    {informe['total']} fragmento(s):")
    for fr in informe["fragmentos"]:
        print(f"      {fr['nombre']} {fr['etiqueta']:<28} {fr['duracion']:5.2f} s"
              f"  mp4 {fr['peso']/1024:6.0f} KB"
              f"  gif {fr.get('peso_gif', 0)/1024:6.0f} KB")

    fondo_real = informe.get("fondo") or args.fondo
    pptx = None
    if not args.sin_pptx:
        ancho, alto = (int(v) for v in informe["resolucion"].split("x"))
        # El cortador habla en rutas relativas a la raiz del plan (aqui, el
        # repo): construir_deck abre los archivos y las necesita absolutas.
        absolutos = [dict(f, **{k: str(REPO / f[k]) for k in ("mp4", "gif", "poster")
                                if f.get(k)})
                     for f in informe["fragmentos"]]
        pptx = construir_deck(absolutos, trabajo / f"{slug}.pptx",
                              ancho / alto, fondo_real,
                              "video" if args.video else "gif")
        print(f"    deck ({'mp4' if args.video else 'GIF'}):"
              f" {visible(pptx)}  {pptx.stat().st_size/1024:.0f} KB")

    escribir_leeme(trabajo, informe, args, titulo, pptx, fondo_real)
    print(f"    todo en {visible(trabajo)}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
