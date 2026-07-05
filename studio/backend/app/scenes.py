"""Deteccion de escenas por analisis estatico (ast) — nunca se ejecuta el script."""

import ast

# Bases de Manim que marcan una clase como renderizable.
SCENE_BASES = {
    "Scene", "ThreeDScene", "MovingCameraScene", "ZoomedScene",
    "VectorScene", "LinearTransformationScene", "SpecialThreeDScene",
}


def _base_name(node: ast.expr) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def detect_scenes(source: str) -> list[str]:
    """Nombres de clases del script que heredan (directa o transitivamente,
    dentro del propio archivo) de una Scene de Manim."""
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        raise ValueError(f"error de sintaxis en linea {e.lineno}: {e.msg}") from e

    classes: dict[str, list[str]] = {}
    order: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            bases = [b for b in (_base_name(x) for x in node.bases) if b]
            classes[node.name] = bases
            order.append(node.name)

    def is_scene(name: str, seen: frozenset[str] = frozenset()) -> bool:
        if name in SCENE_BASES:
            return True
        if name in seen or name not in classes:
            return False
        return any(is_scene(b, seen | {name}) for b in classes[name])

    return [n for n in order if n not in SCENE_BASES and is_scene(n)]
