"""Biblioteca de animaciones Manim ejecutables desde la Biblioteca.

El contenido vive en studio/content/animations/<categoria>/<NN>-<slug>.py y
se versiona en git. Desde la pestana Animaciones se pueden ANADIR secciones
(categorias) y animaciones nuevas (los archivos quedan en el arbol como
untracked hasta que se commiteen); editar/borrar sigue siendo por git. El id
de cada animacion coincide 1:1 con el id de su leccion (misma categoria y
mismo NN-slug), asi que titulo y orden se toman del frontmatter de esa
leccion cuando existe; si no, se derivan del slug del archivo.
"""

import os
import re
import tempfile
import threading
import unicodedata
from pathlib import Path

import yaml

from .lessons import LessonStore
from .scenes import detect_scenes

# id valido: "<categoria>/<NN>-<slug>" — igual que el de lecciones, lo que
# tambien bloquea cualquier path traversal.
RE_ANIMATION_ID = re.compile(r"^[a-z0-9][a-z0-9-]*/[0-9]{2}-[a-z0-9][a-z0-9-]*\Z")
RE_CATEGORY_SLUG = re.compile(r"^[a-z0-9][a-z0-9-]*\Z")
RE_NN_PREFIX = re.compile(r"^([0-9]{2})-")


def slugify(text: str, max_len: int = 40) -> str:
    """Slug ascii-minusculas para nombres de seccion y titulos de animacion."""
    ascii_text = (unicodedata.normalize("NFKD", text)
                  .encode("ascii", "ignore").decode("ascii"))
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")[:max_len]


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
            # has_dir distingue las categorias con arbol de animaciones (se
            # muestran en la pestana aunque esten vacias, p.ej. recien creadas)
            # de las solo-lecciones del curso de Manim (se ocultan).
            categories.append({"slug": cat["slug"], "name": cat["name"],
                               "count": len(animations), "has_dir": cat_dir.is_dir(),
                               "animations": animations})
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

    # ── alta web de secciones y animaciones ──────────────────────────────────
    #
    # Errores → HTTP en main.py: ValueError=422, LookupError=404,
    # FileExistsError=409.

    def _category_slugs(self) -> list[str]:
        cats_file = self.lessons_store.root / "categories.yaml"
        try:
            raw = yaml.safe_load(cats_file.read_text(encoding="utf-8")) or []
        except (OSError, yaml.YAMLError):
            raw = []
        return [c["slug"] for c in (raw if isinstance(raw, list) else [])
                if isinstance(c, dict) and "slug" in c]

    def create_category(self, name: str) -> dict:
        """Anade una seccion a categories.yaml y crea su directorio."""
        slug = slugify(name)
        if not RE_CATEGORY_SLUG.fullmatch(slug):
            raise ValueError("El nombre no produce un identificador valido")
        with self._lock:
            if slug in self._category_slugs():
                raise FileExistsError(f"La seccion '{slug}' ya existe")
            entry = yaml.safe_dump([{"slug": slug, "name": name}],
                                   allow_unicode=True, default_flow_style=False,
                                   sort_keys=False)
            cats_file = self.lessons_store.root / "categories.yaml"
            original = cats_file.read_text(encoding="utf-8")
            if original and not original.endswith("\n"):
                original += "\n"
            # Escritura atomica: nunca dejar un categories.yaml a medias.
            fd, tmp = tempfile.mkstemp(dir=cats_file.parent, suffix=".tmp")
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    f.write(original + entry)
                os.replace(tmp, cats_file)
            except BaseException:
                Path(tmp).unlink(missing_ok=True)
                raise
            # El directorio ademas invalida la cache del indice (mtime del arbol).
            (self.root / slug).mkdir(parents=True, exist_ok=True)
        return {"slug": slug, "name": name}

    def create_animation(self, category: str, title: str, script: str) -> dict:
        """Escribe <categoria>/<NN>-<slug>.py con el siguiente NN libre."""
        try:
            detected = detect_scenes(script)
        except ValueError as e:
            raise ValueError(f"Script invalido: {e}")
        if not detected:
            raise ValueError("El script no define ninguna escena de Manim")

        slug = slugify(title)
        if not slug:
            raise ValueError("El titulo no produce un identificador valido")
        with self._lock:
            if (not RE_CATEGORY_SLUG.fullmatch(category)
                    or category not in self._category_slugs()):
                raise LookupError(f"La seccion '{category}' no existe")
            cat_dir = self.root / category
            cat_dir.mkdir(parents=True, exist_ok=True)
            usados = [int(m.group(1)) for p in cat_dir.glob("*.py")
                      if (m := RE_NN_PREFIX.match(p.stem))]
            siguiente = max(usados, default=0) + 1
            if siguiente > 99:
                raise ValueError("La seccion ya tiene 99 animaciones")
            animation_id = f"{category}/{siguiente:02d}-{slug}"
            if not RE_ANIMATION_ID.fullmatch(animation_id):
                raise ValueError("El titulo no produce un identificador valido")
            path = self.root / f"{animation_id}.py"
            if path.exists():
                raise FileExistsError(f"'{animation_id}' ya existe")
            path.write_text(script, encoding="utf-8")
        return self._meta(animation_id, path)
