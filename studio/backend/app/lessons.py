"""Biblioteca de lecciones educativas: Markdown + frontmatter YAML en disco.

El contenido vive en studio/content/lessons/<categoria>/<NN>-<slug>.md y se
versiona en git (sin CRUD web). El indice se cachea en memoria y se invalida
cuando cambia el mtime mas reciente del arbol.
"""

import re
import threading
from pathlib import Path

import yaml

# id valido: "<categoria>/<NN>-<slug>" — sin puntos ni barras extra, lo que
# tambien bloquea cualquier path traversal.
RE_LESSON_ID = re.compile(r"^[a-z0-9][a-z0-9-]*/[0-9]{2}-[a-z0-9][a-z0-9-]*$")


def _meta(meta: dict, lesson_id: str) -> dict:
    return {
        "id": lesson_id,
        "title": meta.get("title", lesson_id),
        "level": meta.get("level", "intro"),
        "summary": meta.get("summary", ""),
        "tags": meta.get("tags", []),
        "minutes": meta.get("minutes", 10),
        "order": meta.get("order", 99),
    }


class LessonStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self._lock = threading.Lock()
        self._index: dict | None = None
        self._mtime: float = -1.0

    @staticmethod
    def parse(text: str) -> tuple[dict, str]:
        """Separa frontmatter YAML (entre '---') del cuerpo markdown."""
        if not text.startswith("---"):
            return {}, text
        parts = text.split("---", 2)
        if len(parts) < 3:
            return {}, text
        meta = yaml.safe_load(parts[1]) or {}
        return (meta if isinstance(meta, dict) else {}), parts[2].lstrip("\n")

    def _tree_mtime(self) -> float:
        latest = 0.0
        try:
            latest = self.root.stat().st_mtime
            for p in self.root.rglob("*"):
                latest = max(latest, p.stat().st_mtime)
        except OSError:
            pass
        return latest

    def _build_index(self) -> dict:
        cats_file = self.root / "categories.yaml"
        try:
            cats = yaml.safe_load(cats_file.read_text(encoding="utf-8")) or []
        except OSError:
            cats = []
        categories = []
        for cat in cats:
            cat_dir = self.root / cat["slug"]
            lessons = []
            if cat_dir.is_dir():
                for md in sorted(cat_dir.glob("*.md")):
                    try:
                        meta, _ = self.parse(md.read_text(encoding="utf-8"))
                    except OSError:
                        continue
                    lessons.append(_meta(meta, f"{cat['slug']}/{md.stem}"))
            lessons.sort(key=lambda l: (l["order"], l["id"]))
            categories.append({"slug": cat["slug"], "name": cat["name"],
                               "count": len(lessons), "lessons": lessons})
        return {"categories": categories}

    def index(self) -> dict:
        with self._lock:
            mtime = self._tree_mtime()
            if self._index is None or mtime != self._mtime:
                self._index = self._build_index()
                self._mtime = mtime
            return self._index

    def get(self, lesson_id: str) -> dict | None:
        if not RE_LESSON_ID.match(lesson_id):
            return None
        path = self.root / f"{lesson_id}.md"  # el regex garantiza ruta interna
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            return None
        meta, body = self.parse(text)
        return _meta(meta, lesson_id) | {"markdown": body}
