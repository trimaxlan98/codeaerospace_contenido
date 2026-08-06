#!/usr/bin/env python3
"""Sincroniza un curso versionado en el repo con la base del Studio.

Los cursos nuevos viven en git (studio/content/cursos/<slug>/: curso.json +
style_block.py + clips/NN-*.py) y este CLI los sube a la tabla de proyectos
del backend usando los MISMOS modulos que la API (ProjectService,
detect_scenes), sin pasar por HTTP. No toca renders ni jobs: si un clip
cambia, queda `stale` por hash y se re-renderiza desde el Studio.

    studio/backend/venv/bin/python studio/tools/subir_curso.py \
        studio/content/cursos/redes-neuronales-la-maquina-que-aprende
    ... --db studio/backend/manimstudio.db   otra base (defecto: la del VPS
                                             o MS_DB_PATH)
    ... --dry-run                            muestra el plan sin escribir

Idempotente: empareja el proyecto por nombre exacto y los clips por
posicion. Crea lo que falta, actualiza lo que cambio (titulo, script,
escena, final_state, style_block, descripcion) y reporta que clips quedan
`stale`. Nunca borra clips: si el curso.json tiene menos clips que la base,
avisa y los deja (borrar es decision humana, via UI).
"""

import argparse
import json
import os
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND))

from app.db import Database  # noqa: E402
from app.projects import (QUALITIES, ProjectService,  # noqa: E402
                          compose_script, content_hash)
from app.scenes import detect_scenes  # noqa: E402

DEFAULT_DB = "/var/www/codeaerospace_contenido/studio/backend/manimstudio.db"


def cargar_curso(curso_dir: Path) -> dict:
    """Lee y valida curso.json + style_block + clips. Sale con mensaje claro
    ante cualquier inconsistencia (archivo faltante, escena ausente...)."""
    manifest_path = curso_dir / "curso.json"
    if not manifest_path.is_file():
        sys.exit(f"no existe {manifest_path}")
    curso = json.loads(manifest_path.read_text())

    for campo in ("name", "quality", "clips"):
        if not curso.get(campo):
            sys.exit(f"curso.json sin campo obligatorio: {campo}")
    if curso["quality"] not in QUALITIES:
        sys.exit(f"calidad invalida: {curso['quality']}")

    style_path = curso_dir / curso.get("style_block", "style_block.py")
    style = style_path.read_text() if style_path.is_file() else ""

    clips = []
    for i, spec in enumerate(curso["clips"]):
        ruta = curso_dir / spec["file"]
        if not ruta.is_file():
            sys.exit(f"clip {i + 1}: no existe {ruta}")
        script = ruta.read_text()
        escena = spec.get("scene") or ""
        compuesto = compose_script(style, script)
        if escena not in detect_scenes(compuesto):
            sys.exit(f"clip {i + 1} ({ruta.name}): la escena '{escena}' no "
                     "esta definida en el script compuesto")
        clips.append({
            "title": spec.get("title") or ruta.stem,
            "script": script,
            "scene": escena,
            "final_state": spec.get("final_state") or "",
        })

    return {"name": curso["name"],
            "description": curso.get("description") or "",
            "quality": curso["quality"], "style_block": style,
            "clips": clips}


def sincronizar(service: ProjectService, db: Database, curso: dict,
                dry_run: bool) -> list[str]:
    """Aplica el curso sobre la base; devuelve las lineas del reporte."""
    reporte = []
    proyecto = next((p for p in db.list_projects()
                     if p["name"] == curso["name"]), None)

    if proyecto is None:
        reporte.append(f"+ proyecto nuevo: {curso['name']!r} "
                       f"({curso['quality']})")
        if not dry_run:
            proyecto = service.create_project(
                curso["name"], curso["description"], curso["quality"],
                curso["style_block"])
    else:
        cambios = {k: curso[k] for k in ("description", "style_block")
                   if proyecto.get(k) != curso[k]}
        if proyecto["quality"] != curso["quality"]:
            # update_project ya protege el caso con renders; aqui solo se
            # intenta si de verdad cambio.
            cambios["quality"] = curso["quality"]
        if cambios:
            reporte.append(f"~ proyecto {proyecto['id']}: actualiza "
                           + ", ".join(sorted(cambios)))
            if not dry_run:
                proyecto = service.update_project(proyecto["id"], **cambios)
        else:
            reporte.append(f"= proyecto {proyecto['id']}: sin cambios de "
                           "metadatos")

    existentes = db.list_clips(proyecto["id"]) if proyecto else []
    for pos, clip in enumerate(curso["clips"]):
        actual = existentes[pos] if pos < len(existentes) else None
        if actual is None:
            reporte.append(f"+ clip {pos + 1}: {clip['title']!r}")
            if not dry_run:
                creado = service.add_clip(proyecto["id"], clip["title"],
                                          clip["script"], clip["scene"],
                                          position=pos)
                service.update_clip(creado["id"],
                                    final_state=clip["final_state"])
            continue

        campos = {k: clip[k] for k in ("title", "script", "scene",
                                       "final_state")
                  if (actual.get(k) or "") != clip[k]}
        if not campos:
            reporte.append(f"= clip {pos + 1}: {clip['title']!r} al dia")
            continue
        nuevo_hash = content_hash(curso["style_block"], clip["script"],
                                  clip["scene"])
        stale = (bool(actual.get("job_id"))
                 and actual.get("rendered_hash") != nuevo_hash)
        reporte.append(f"~ clip {pos + 1}: {clip['title']!r} actualiza "
                       + ", ".join(sorted(campos))
                       + ("  -> STALE (re-render)" if stale else ""))
        if not dry_run:
            service.update_clip(actual["id"], **campos)

    if proyecto and len(existentes) > len(curso["clips"]):
        sobran = existentes[len(curso["clips"]):]
        reporte.append("! en la base sobran "
                       f"{len(sobran)} clips no listados en curso.json "
                       "(no se borran): "
                       + ", ".join(c["title"] for c in sobran))
    return reporte


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("curso_dir",
                    help="directorio del curso (con curso.json)")
    ap.add_argument("--db", default=None,
                    help="ruta de manimstudio.db (defecto: MS_DB_PATH o la "
                    "del VPS)")
    ap.add_argument("--dry-run", action="store_true",
                    help="muestra el plan sin escribir")
    args = ap.parse_args()

    curso_dir = Path(args.curso_dir)
    curso = cargar_curso(curso_dir)

    db_path = Path(args.db or os.environ.get("MS_DB_PATH", DEFAULT_DB))
    if not db_path.is_file():
        sys.exit(f"no existe la base {db_path} (usa --db)")

    db = Database(db_path)
    service = ProjectService(db)
    reporte = sincronizar(service, db, curso, args.dry_run)

    encabezado = "PLAN (dry-run)" if args.dry_run else "Sincronizado"
    print(f"{encabezado}: {curso['name']} -> {db_path}")
    for linea in reporte:
        print(" ", linea)


if __name__ == "__main__":
    main()
