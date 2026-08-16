#!/usr/bin/env python3
"""Agrupa los cursos sueltos en areas dentro del indice de Proyectos.

La vista Proyectos agrupa por *familia*: parte el nombre por el primer " · "
y llama familia a lo que queda delante (`Projects.jsx:splitName`). Un prefijo
con un solo proyecto no forma grupo, cae en "Cursos sueltos". Por eso las tres
familias numeradas (Aerodinamica, Electromagnetismo, Metrologia optica) salen
ordenadas y los 16 cursos monograficos de 8 clips salian en un monton plano.

Este CLI aplica el catalogo de `studio/docs/CATALOGO-CURSOS.md`: renombra cada
curso suelto a "Area · N Titulo" en TRES sitios que tienen que ir a la par:

  1. `studio/content/cursos/<slug>/curso.json` — la fuente en git.
  2. `guiones/<slug-del-nombre>/` — las narraciones ya generadas.
  3. la tabla `projects` de la base — lo que ve la app.

El 1, porque `subir_curso.py` empareja el proyecto por NOMBRE EXACTO
(`subir_curso.py:86`): si solo se cambiara la base, la siguiente subida no
reconoceria el proyecto y crearia un DUPLICADO con todos sus clips.

El 2, porque el directorio de narracion NO se guarda en ninguna parte: se
DERIVA del nombre (`narracion.destino` -> `guiones_dir / slugify(name)`).
Renombrar el proyecto sin mover su carpeta deja las narraciones huerfanas —
los 16 cursos aparecerian como "sin narracion" y su zip saldria sin wav ni
txt, aunque los archivos sigan en disco.

    studio/backend/venv/bin/python studio/tools/ordenar_cursos.py
    ... --aplicar                          escribe (por defecto: dry-run)
    ... --db studio/backend/manimstudio.db otra base (defecto: MS_DB_PATH o VPS)
    ... --guiones ruta/guiones             otra carpeta de narraciones

Idempotente: cada curso se busca por su nombre viejo y, si ya lleva el nuevo,
se reporta como "ya ordenado". Se puede correr dos veces sin dano.

Efecto secundario aceptado: renombrar toca `updated_at`, asi que con el orden
"por actividad" los renombrados suben al principio una vez. Con el orden "por
nombre" el indice queda como se diseno.
"""

import argparse
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
BACKEND = REPO / "studio" / "backend"
CURSOS = REPO / "studio" / "content" / "cursos"
sys.path.insert(0, str(BACKEND))

from app.db import Database  # noqa: E402
from app.narracion import slugify  # noqa: E402  (misma regla que narracion.destino)
from app.projects import ProjectService  # noqa: E402

DEFAULT_DB = "/var/www/codeaerospace_contenido/studio/backend/manimstudio.db"
DEFAULT_GUIONES = "/var/www/codeaerospace_contenido/guiones"

# Catalogo: nombre viejo -> nombre nuevo. El numero fija el orden DENTRO del
# area, porque la lista ordena por etiqueta (`localeCompare`), no por fecha.
# La razon de cada area esta en studio/docs/CATALOGO-CURSOS.md.
RENOMBRES = {
    # Comunicaciones — del espectro a apuntar la antena.
    "El espectro: la guerra invisible por las ondas":
        "Comunicaciones · 1 El espectro: la guerra invisible por las ondas",
    "SDR: la radio hecha software":
        "Comunicaciones · 2 SDR: la radio hecha software",
    "Cerrar el enlace: la cuenta en decibelios":
        "Comunicaciones · 3 Cerrar el enlace: la cuenta en decibelios",
    "Apuntar a un satélite: el arte del seguimiento":
        "Comunicaciones · 4 Apuntar a un satélite: el arte del seguimiento",

    # Informacion y computo — medir la informacion, guardarla, repartirla.
    "Teoría de la información: los bits de Shannon":
        "Información y cómputo · 1 Teoría de la información: los bits de Shannon",
    "Criptografía: el arte de guardar secretos":
        "Información y cómputo · 2 Criptografía: el arte de guardar secretos",
    "Sistemas distribuidos: la nube por dentro":
        "Información y cómputo · 3 Sistemas distribuidos: la nube por dentro",

    # Inteligencia artificial — la red, el lenguaje, el agente.
    "Redes neuronales: la máquina que aprende":
        "Inteligencia artificial · 1 Redes neuronales: la máquina que aprende",
    "De la palabra al vector: embeddings y atención":
        "Inteligencia artificial · 2 De la palabra al vector: embeddings y atención",
    "Agentes de IA: máquinas que operan el mundo":
        "Inteligencia artificial · 3 Agentes de IA: máquinas que operan el mundo",

    # Sistemas dinamicos — el patron, su ruptura, su control.
    "Matemáticas en la naturaleza":
        "Sistemas dinámicos · 1 Matemáticas en la naturaleza",
    "Caos: el orden escondido":
        "Sistemas dinámicos · 2 Caos: el orden escondido",
    "Control: domar sistemas que se resisten":
        "Sistemas dinámicos · 3 Control: domar sistemas que se resisten",

    # Astronautica — subir, sobrevivir alla arriba, medir el tiempo.
    "Tsiolkovsky: la tiranía del cohete":
        "Astronáutica · 1 Tsiolkovsky: la tiranía del cohete",
    "Materiales que van al espacio":
        "Astronáutica · 2 Materiales que van al espacio",
    "Relatividad y el GPS":
        "Astronáutica · 3 Relatividad y el GPS",
}


def renombrar_repo(aplicar: bool) -> list[str]:
    """Cambia el `name` de los curso.json afectados.

    Reemplazo de texto, no `json.dump`: reescribir el manifiesto entero
    normalizaria el formato de los 58 ficheros y ensuciaria el diff.
    """
    reporte = []
    pendientes = dict(RENOMBRES)

    for manifest in sorted(CURSOS.glob("*/curso.json")):
        texto = manifest.read_text(encoding="utf-8")
        try:
            nombre = json.loads(texto)["name"]
        except (json.JSONDecodeError, KeyError) as err:
            reporte.append(f"! {manifest.parent.name}: manifiesto ilegible ({err})")
            continue

        if nombre in RENOMBRES.values():
            pendientes.pop(
                next(k for k, v in RENOMBRES.items() if v == nombre), None)
            reporte.append(f"= {manifest.parent.name}: ya ordenado")
            continue
        if nombre not in pendientes:
            continue

        nuevo = pendientes.pop(nombre)
        viejo_txt = f'"name": {json.dumps(nombre, ensure_ascii=False)}'
        nuevo_txt = f'"name": {json.dumps(nuevo, ensure_ascii=False)}'
        if texto.count(viejo_txt) != 1:
            reporte.append(f"! {manifest.parent.name}: el nombre no aparece "
                           "exactamente una vez, se salta")
            continue
        reporte.append(f"~ {manifest.parent.name}: {nombre!r} -> {nuevo!r}")
        if aplicar:
            manifest.write_text(texto.replace(viejo_txt, nuevo_txt, 1),
                                encoding="utf-8")

    for sobrante in pendientes:
        reporte.append(f"! sin curso.json para {sobrante!r} (catalogo desfasado)")
    return reporte


def renombrar_guiones(guiones_dir: Path, aplicar: bool) -> list[str]:
    """Mueve la carpeta de narracion de cada curso al slug de su nombre nuevo.

    Nunca fusiona: si el destino ya existe con contenido distinto se reporta y
    se salta, porque perder guiones y wav generados con Vertex no se arregla
    con un ctrl+z.
    """
    reporte = []
    for viejo, nuevo in RENOMBRES.items():
        origen = guiones_dir / slugify(viejo)
        destino = guiones_dir / slugify(nuevo)
        if destino.is_dir():
            reporte.append(f"= {destino.name}: ya ordenado"
                           + (f" (queda {origen.name} sin mover)" if origen.is_dir() else ""))
            continue
        if not origen.is_dir():
            reporte.append(f". {slugify(viejo)}: sin narracion, nada que mover")
            continue
        reporte.append(f"~ {origen.name} -> {destino.name}")
        if aplicar:
            origen.rename(destino)
    return reporte


def renombrar_db(db_path: Path, aplicar: bool) -> list[str]:
    """Renombra los proyectos de la base. No toca clips, jobs ni renders."""
    db = Database(db_path)
    service = ProjectService(db)
    proyectos = {p["name"]: p for p in db.list_projects()}
    reporte = []

    for viejo, nuevo in RENOMBRES.items():
        if nuevo in proyectos:
            reporte.append(f"= {nuevo!r}: ya ordenado")
            continue
        proyecto = proyectos.get(viejo)
        if proyecto is None:
            reporte.append(f"! {viejo!r}: no esta en esta base")
            continue
        reporte.append(f"~ {proyecto['id']}: {viejo!r} -> {nuevo!r}")
        if aplicar:
            service.update_project(proyecto["id"], name=nuevo)
    return reporte


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", default=None,
                    help="ruta de manimstudio.db (defecto: MS_DB_PATH o la del VPS)")
    ap.add_argument("--aplicar", action="store_true",
                    help="escribe los cambios (por defecto solo muestra el plan)")
    ap.add_argument("--guiones", default=None,
                    help="carpeta de narraciones (defecto: MS_GUIONES_DIR o la del VPS)")
    ap.add_argument("--solo-repo", action="store_true",
                    help="no toca la base ni las narraciones, solo los curso.json")
    args = ap.parse_args()

    encabezado = "APLICADO" if args.aplicar else "PLAN (dry-run)"
    print(f"{encabezado} — {len(RENOMBRES)} cursos sueltos -> 5 areas")

    print("\nrepo (studio/content/cursos/*/curso.json):")
    for linea in renombrar_repo(args.aplicar):
        print(" ", linea)

    if args.solo_repo:
        return

    # Las narraciones se mueven ANTES que la base: asi, cuando la app empiece a
    # ver el nombre nuevo, su carpeta ya esta donde la va a buscar.
    guiones_dir = Path(args.guiones or os.environ.get("MS_GUIONES_DIR", DEFAULT_GUIONES))
    if guiones_dir.is_dir():
        print(f"\nnarraciones ({guiones_dir}):")
        for linea in renombrar_guiones(guiones_dir, args.aplicar):
            print(" ", linea)
    else:
        print(f"\nnarraciones: no existe {guiones_dir} — se omite")

    db_path = Path(args.db or os.environ.get("MS_DB_PATH", DEFAULT_DB))
    if not db_path.is_file():
        print(f"\nbase: no existe {db_path} — se omite (usa --db o --solo-repo)")
        return

    print(f"\nbase ({db_path}):")
    for linea in renombrar_db(db_path, args.aplicar):
        print(" ", linea)


if __name__ == "__main__":
    main()
