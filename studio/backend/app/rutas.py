"""Rutas relativas al workspace, a prueba de enlaces simbolicos.

El runner monta el repo en /workspace dentro del contenedor, asi que todo lo
que el backend le pasa viaja como ruta RELATIVA al workspace. Convertir una
ruta absoluta en esa relativa parece trivial y no lo es:

    Path(video).resolve().relative_to(cfg.workspace.resolve())   # NO

En una instalacion donde `render_jobs/` o `exports/` son enlaces simbolicos a
otro disco —que es como esta montada esta maquina, ver
studio/docs/ARTEFACTOS-LOCALES.md— `resolve()` sigue el enlace y devuelve algo
como /home/.../data/codeaerospace/render_jobs/..., que `relative_to` declara
"fuera del workspace" aunque el contenedor lo vea perfectamente montado.

La regla correcta: comparar SIN resolver primero (que es como el backend
construyo la ruta) y dejar `resolve()` solo como respaldo, para el caso
contrario — una ruta que llega ya resuelta y un workspace que si es un enlace.
"""

from pathlib import Path


def relativa_al_workspace(path, workspace) -> str | None:
    """La ruta relativa al workspace, o None si de verdad vive fuera."""
    p, base = Path(path), Path(workspace)
    for raiz, candidata in ((base, p), (base.resolve(), p.resolve())):
        try:
            return str(candidata.absolute().relative_to(raiz.absolute()))
        except ValueError:
            continue
    return None
