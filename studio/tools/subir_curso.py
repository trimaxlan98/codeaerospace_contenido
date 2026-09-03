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
import os
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND))

from app import importar  # noqa: E402
from app.db import Database  # noqa: E402
from app.projects import ProjectService  # noqa: E402

DEFAULT_DB = "/var/www/codeaerospace_contenido/studio/backend/manimstudio.db"


def cargar_curso(curso_dir: Path) -> dict:
    """Lee y valida curso.json + style_block + clips.

    La logica vive en `app/importar.py`, que es el MISMO modulo que usa
    `POST /api/projects/importar`: la terminal y la app no pueden divergir.
    Aqui solo se traduce el error a un `sys.exit` con mensaje claro.
    """
    try:
        return importar.cargar_curso(curso_dir)
    except importar.ErrorImportacion as e:
        sys.exit(str(e))


def sincronizar(service: ProjectService, db: Database, curso: dict,
                dry_run: bool) -> list[str]:
    """Aplica el curso sobre la base; devuelve las lineas del reporte."""
    return importar.aplicar(service, db, curso, dry_run).reporte


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
