#!/usr/bin/env python3
"""Sincroniza un promo de redes versionado en el repo con la base del Studio.

Hermano de `subir_curso.py`, con las diferencias que vienen del formato:

  1. **Un promo es un proyecto de UN clip** (`tipo='promo'`), vertical y en
     `qh`. No hay continuidad entre clips ni zip de curso.
  2. **Trae su audio**: el bloque `audio` (cama de sonido) y `voz` del
     `promo.json` se guardan como manifiesto del clip, listos para mezclar
     desde la app. Es la misma forma de archivo que ya usan los diez promos
     escritos a mano, asi que no hay conversion.
  3. **El nombre lleva prefijo `Promo · `**: el indice agrupa por lo que hay
     antes del `·`, asi que los promos salen juntos y no mezclados con las
     lecciones de los cursos.

    studio/backend/venv/bin/python studio/tools/subir_promo.py \
        studio/content/promos/determinante
    ... --todos                              sube todos los de content/promos
    ... --db studio/backend/manimstudio.db   otra base (defecto: la del VPS
                                             o MS_DB_PATH)
    ... --dry-run                            muestra el plan sin escribir

Idempotente: empareja el proyecto por nombre exacto. Crea lo que falta,
actualiza lo que cambio (script, escena, estilo, descripcion, manifiesto de
audio) y avisa de lo que queda `stale` o con la mezcla vieja. No borra nada
ni toca renders: re-renderizar y re-mezclar son decisiones humanas, desde
la interfaz.
"""

import argparse
import json
import os
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND))

from app import audio_promo  # noqa: E402
from app.db import Database  # noqa: E402
from app.projects import (FORMATOS, QUALITIES, ProjectService,  # noqa: E402
                          compose_script, content_hash)
from app.scenes import detect_scenes  # noqa: E402

DEFAULT_DB = "/var/www/codeaerospace_contenido/studio/backend/manimstudio.db"
PREFIJO = "Promo · "
CALIDAD = "qh"


def cargar_promo(promo_dir: Path) -> dict:
    """Lee y valida promo.json + style_block + escena. Sale con mensaje
    claro ante cualquier inconsistencia."""
    manifest_path = promo_dir / "promo.json"
    if not manifest_path.is_file():
        sys.exit(f"no existe {manifest_path}")
    promo = json.loads(manifest_path.read_text())

    for campo in ("name", "scene", "file"):
        if not promo.get(campo):
            sys.exit(f"{manifest_path}: falta el campo obligatorio {campo}")

    style_path = promo_dir / promo.get("style_block", "style_block.py")
    style = style_path.read_text() if style_path.is_file() else ""

    ruta = promo_dir / promo["file"]
    if not ruta.is_file():
        sys.exit(f"{manifest_path}: no existe {ruta}")
    script = ruta.read_text()
    compuesto = compose_script(style, script)
    if promo["scene"] not in detect_scenes(compuesto):
        sys.exit(f"{promo_dir.name}: la escena '{promo['scene']}' no esta "
                 "definida en el script compuesto")

    # El formato sale del manifiesto (el primero de la lista es el que se
    # trabajo); si no lo dice, vertical, que es el formato de redes.
    formatos = promo.get("formatos") or ["vertical"]
    formato = formatos[0]
    if formato not in FORMATOS:
        sys.exit(f"{promo_dir.name}: formato desconocido '{formato}'")
    if CALIDAD not in QUALITIES:  # defensa boba, por si cambian las calidades
        sys.exit(f"calidad invalida: {CALIDAD}")

    manifiesto = audio_promo.normalizar(
        {"audio": promo.get("audio"), "voz": promo.get("voz")})
    errores = audio_promo.validar(manifiesto)
    if errores:
        sys.exit(f"{promo_dir.name}: manifiesto de audio invalido: "
                 + "; ".join(errores))

    descripcion = promo.get("description") or ""
    curso = promo.get("curso")
    if curso and curso.lower() not in descripcion.lower():
        descripcion = f"[{curso}] {descripcion}".strip()

    return {
        "name": PREFIJO + promo["name"],
        "description": descripcion,
        "quality": CALIDAD,
        "formato": formato,
        "style_block": style,
        "clip": {"title": promo["name"], "script": script,
                 "scene": promo["scene"]},
        "audio": manifiesto,
        "duracion_objetivo": promo.get("duracion_objetivo"),
    }


def sincronizar(service: ProjectService, db: Database, promo: dict,
                dry_run: bool) -> list[str]:
    """Aplica el promo sobre la base; devuelve las lineas del reporte."""
    reporte = []
    proyecto = next((p for p in db.list_projects()
                     if p["name"] == promo["name"]), None)

    if proyecto is None:
        reporte.append(f"+ promo nuevo: {promo['name']!r} "
                       f"({promo['formato']} · {promo['quality']})")
        if dry_run:
            return reporte
        proyecto = service.create_project(
            promo["name"], promo["description"], promo["quality"],
            promo["style_block"], tipo="promo", formato=promo["formato"])
    else:
        cambios = {k: promo[k] for k in ("description", "style_block")
                   if proyecto.get(k) != promo[k]}
        # Calidad y formato solo se intentan si de verdad cambiaron:
        # update_project los rechaza con renders vigentes, y ese aviso es
        # informacion, no un fallo del importador.
        for campo in ("quality", "formato"):
            if proyecto.get(campo) != promo[campo]:
                cambios[campo] = promo[campo]
        if cambios:
            reporte.append(f"~ promo {proyecto['id']}: actualiza "
                           + ", ".join(sorted(cambios)))
            if not dry_run:
                try:
                    proyecto = service.update_project(proyecto["id"], **cambios)
                except ValueError as e:
                    reporte.append(f"  ! {e}")
                    for campo in ("quality", "formato"):
                        cambios.pop(campo, None)
                    if cambios:
                        proyecto = service.update_project(proyecto["id"], **cambios)
        else:
            reporte.append(f"= promo {proyecto['id']}: sin cambios de metadatos")

    clips = db.list_clips(proyecto["id"])
    spec = promo["clip"]
    manifiesto = json.dumps(promo["audio"], ensure_ascii=False)

    if not clips:
        reporte.append(f"+ clip: {spec['title']!r} ({spec['scene']})")
        if not dry_run:
            creado = service.add_clip(proyecto["id"], spec["title"],
                                      spec["script"], spec["scene"], position=0)
            service.update_clip(creado["id"], audio_json=manifiesto)
        return reporte

    actual = clips[0]
    campos = {k: spec[k] for k in ("title", "script", "scene")
              if (actual.get(k) or "") != spec[k]}
    nuevo_hash = content_hash(promo["style_block"], spec["script"], spec["scene"])
    stale = (bool(actual.get("job_id"))
             and actual.get("rendered_hash") != nuevo_hash)

    if (actual.get("audio_json") or "") != manifiesto:
        campos["audio_json"] = manifiesto

    if campos:
        visibles = [c for c in campos if c != "audio_json"]
        detalle = ", ".join(sorted(visibles)) or "manifiesto de audio"
        if visibles and "audio_json" in campos:
            detalle += ", manifiesto de audio"
        reporte.append(f"~ clip: {spec['title']!r} actualiza {detalle}"
                       + ("  -> STALE (re-render)" if stale else ""))
        if not dry_run:
            service.update_clip(actual["id"], **campos)
        if "audio_json" in campos and actual.get("job_id"):
            reporte.append("  ! la mezcla anterior queda vieja: vuelve a "
                           "mezclar el audio desde la interfaz")
    else:
        reporte.append(f"= clip: {spec['title']!r} al dia")

    if len(clips) > 1:
        reporte.append(f"! el proyecto tiene {len(clips)} clips y un promo es "
                       "uno solo (no se borra nada)")
    return reporte


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("promo_dir", nargs="?",
                    help="directorio del promo (con promo.json)")
    ap.add_argument("--todos", action="store_true",
                    help="sube todos los de studio/content/promos")
    ap.add_argument("--db", default=None,
                    help="ruta de manimstudio.db (defecto: MS_DB_PATH o la del VPS)")
    ap.add_argument("--dry-run", action="store_true",
                    help="muestra el plan sin escribir")
    args = ap.parse_args()

    if args.todos:
        raiz = Path(__file__).resolve().parents[1] / "content" / "promos"
        dirs = sorted(d for d in raiz.iterdir() if (d / "promo.json").is_file())
        if not dirs:
            sys.exit(f"no hay promos en {raiz}")
    elif args.promo_dir:
        dirs = [Path(args.promo_dir)]
    else:
        ap.error("da un directorio de promo o usa --todos")

    db_path = Path(args.db or os.environ.get("MS_DB_PATH", DEFAULT_DB))
    if not db_path.is_file():
        sys.exit(f"no existe la base {db_path} (usa --db)")

    db = Database(db_path)
    service = ProjectService(db)
    encabezado = "PLAN (dry-run)" if args.dry_run else "Sincronizado"
    for d in dirs:
        promo = cargar_promo(d)
        reporte = sincronizar(service, db, promo, args.dry_run)
        print(f"{encabezado}: {promo['name']} -> {db_path}")
        for linea in reporte:
            print(" ", linea)


if __name__ == "__main__":
    main()
