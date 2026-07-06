"""Biblioteca de animaciones Manim ejecutables desde la Biblioteca.

El contenido vive en studio/content/animations/<categoria>/<NN>-<slug>.py y
se versiona en git (sin CRUD web), igual que las lecciones. El id de cada
animacion coincide 1:1 con el id de su leccion (misma categoria y mismo
NN-slug), asi que titulo y orden se toman del frontmatter de esa leccion
cuando existe; si no, se derivan del slug del archivo.
"""

import re
import threading
from pathlib import Path

import yaml

from .lessons import LessonStore
from .scenes import detect_scenes

# id valido: "<categoria>/<NN>-<slug>" — igual que el de lecciones, lo que
# tambien bloquea cualquier path traversal.
RE_ANIMATION_ID = re.compile(r"^[a-z0-9][a-z0-9-]*/[0-9]{2}-[a-z0-9][a-z0-9-]*\Z")


def _title_from_slug(animation_id: str) -> str:
    slug = animation_id.rsplit("/", 1)[-1]
    words = slug.split("-")[1:]  # descarta el prefijo NN-
    return " ".join(words).capitalize() or animation_id


class AnimationStore:
    def __init__(self, root: Path, lessons_store: LessonStore) -> None:
        self.root = root
        self.lessons_store = lessons_store
        self._lock = threading.Lock()
        self._index: dict | None = None
        self._mtime: float = -1.0

    def _tree_mtime(self) -> float:
        latest = 0.0
        try:
            latest = self.root.stat().st_mtime
            for p in self.root.rglob("*"):
                latest = max(latest, p.stat().st_mtime)
        except OSError:
            pass
        return latest

    def _meta(self, animation_id: str, path: Path) -> dict:
        lesson = self.lessons_store.get(animation_id)
        try:
            scenes = detect_scenes(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            scenes = []
        return {
            "id": animation_id,
            "title": lesson["title"] if lesson else _title_from_slug(animation_id),
            "order": lesson["order"] if lesson else 99,
            "scene": scenes[0] if scenes else None,
        }

    def _build_index(self) -> dict:
        cats_file = self.lessons_store.root / "categories.yaml"
        try:
            cats_raw = yaml.safe_load(cats_file.read_text(encoding="utf-8")) or []
        except (OSError, yaml.YAMLError):
            cats_raw = []
        cats = [c for c in (cats_raw if isinstance(cats_raw, list) else [])
                if isinstance(c, dict) and "slug" in c and "name" in c]

        categories = []
        for cat in cats:
            cat_dir = self.root / cat["slug"]
            animations = []
            if cat_dir.is_dir():
                for py in sorted(cat_dir.glob("*.py")):
                    animation_id = f"{cat['slug']}/{py.stem}"
                    animations.append(self._meta(animation_id, py))
            animations.sort(key=lambda a: (a["order"], a["id"]))
            categories.append({"slug": cat["slug"], "name": cat["name"],
                               "count": len(animations), "animations": animations})
        return {"categories": categories}

    def index(self) -> dict:
        with self._lock:
            mtime = self._tree_mtime()
            if self._index is None or mtime != self._mtime:
                self._index = self._build_index()
                self._mtime = mtime
            return self._index

    def get(self, animation_id: str) -> dict | None:
        if not RE_ANIMATION_ID.fullmatch(animation_id):
            return None
        path = self.root / f"{animation_id}.py"  # el regex garantiza ruta interna
        try:
            script = path.read_text(encoding="utf-8")
        except OSError:
            return None
        return self._meta(animation_id, path) | {"script": script}
