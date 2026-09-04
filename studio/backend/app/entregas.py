"""Biblioteca de entregas: navegar `exports/` desde la app.

La pestaña «Renders» enseña los *jobs* —un clip suelto, identificado por su
escena— y eso es lo que produce el pipeline por dentro. Lo que se ENTREGA
vive en otro sitio y hasta ahora no se veia desde ninguna pantalla:

    exports/
      peliculas/<project_id>/pelicula.mp4     el curso montado
      verticales/<slug>/                      piezas sueltas + la pelicula
      presentaciones/<project_id>/            fragmentos, posters y el .pptx
      marca-intro-y-cierre/                   la marca sonora
      musica/  sfx/                           los bancos audibles
      <curso>/                                los cursos muxeados a mano

Esta vista es un explorador de ese arbol: carpetas, archivos, su tamaño y
—en los videos— su duracion, con reproductor y descarga. Solo LEE; no borra
ni escribe nada, que es justo lo que hace segura una vista que sirve
archivos por ruta.

La defensa de ruta es la misma politica que `/api/jobs/{id}/video`: la ruta
llega relativa, se prohibe cualquier `..` y el resultado tiene que seguir
dentro de la raiz *resuelta* (en esta maquina `exports/` es un enlace a otro
disco, ver studio/docs/ARTEFACTOS-LOCALES.md, asi que la comparacion se hace
contra el destino real).
"""

from __future__ import annotations

import os
import struct
from pathlib import Path

# Extension -> (tipo, media type). El tipo es lo que la interfaz usa para
# decidir si pinta un reproductor, una imagen o un enlace.
TIPOS = {
    ".mp4": ("video", "video/mp4"),
    ".mov": ("video", "video/quicktime"),
    ".webm": ("video", "video/webm"),
    ".mkv": ("video", "video/x-matroska"),
    ".gif": ("imagen", "image/gif"),
    ".png": ("imagen", "image/png"),
    ".jpg": ("imagen", "image/jpeg"),
    ".jpeg": ("imagen", "image/jpeg"),
    ".webp": ("imagen", "image/webp"),
    ".wav": ("audio", "audio/wav"),
    ".mp3": ("audio", "audio/mpeg"),
    ".m4a": ("audio", "audio/mp4"),
    ".flac": ("audio", "audio/flac"),
    ".ogg": ("audio", "audio/ogg"),
    ".pptx": ("documento",
              "application/vnd.openxmlformats-officedocument.presentationml.presentation"),
    ".pdf": ("documento", "application/pdf"),
    ".zip": ("documento", "application/zip"),
    ".txt": ("texto", "text/plain; charset=utf-8"),
    ".md": ("texto", "text/plain; charset=utf-8"),
    ".json": ("texto", "application/json"),
    ".srt": ("texto", "text/plain; charset=utf-8"),
    ".csv": ("texto", "text/csv; charset=utf-8"),
    ".sh": ("texto", "text/plain; charset=utf-8"),
}

# Nombres legibles de las carpetas que produce el propio Estudio.
NOMBRES = {
    "peliculas": "Películas de curso",
    "verticales": "Cursos verticales (9:16)",
    "presentaciones": "Presentaciones (.pptx)",
    "marca-intro-y-cierre": "Marca: intro y cierre",
    "musica": "Banco de música",
    "sfx": "Banco de efectos",
    "promos": "Promos de redes",
}

# Un listado no debe costar minutos: tope de entradas por carpeta y de
# duraciones medidas (leer el `moov` de un mp4 son dos o tres seeks, pero
# con mil archivos se nota).
MAX_ENTRADAS = 2000
MAX_DURACIONES = 400


def tipo_de(nombre: str) -> tuple[str, str]:
    return TIPOS.get(Path(nombre).suffix.lower(), ("otro", "application/octet-stream"))


def duracion_mp4(path: Path) -> float | None:
    """Duracion de un mp4 leyendo `moov/mvhd`, SIN cargar el archivo.

    `narracion.duracion_mp4` hace lo mismo con `read_bytes()`, que para un
    video de media hora son cientos de MB en memoria: aqui se salta de caja
    en caja con `seek`, porque esta vista lista carpetas enteras.
    """
    try:
        with path.open("rb") as f:
            fin = path.stat().st_size
            pos = 0
            while pos + 8 <= fin:
                f.seek(pos)
                cab = f.read(8)
                if len(cab) < 8:
                    return None
                size, kind = struct.unpack(">I4s", cab)
                if size == 1:  # tamaño de 64 bits
                    ext = f.read(8)
                    if len(ext) < 8:
                        return None
                    size = struct.unpack(">Q", ext)[0]
                if size < 8:
                    return None
                if kind == b"moov":
                    datos = f.read(min(size - 8, 8 << 20))
                    return _mvhd(datos)
                pos += size
    except (OSError, struct.error, ValueError):
        return None
    return None


def _mvhd(moov: bytes) -> float | None:
    pos, fin = 0, len(moov)
    while pos + 8 <= fin:
        size, kind = struct.unpack(">I4s", moov[pos:pos + 8])
        if size < 8:
            return None
        if kind == b"mvhd":
            cuerpo = moov[pos + 8:pos + size]
            if not cuerpo:
                return None
            version = cuerpo[0]
            try:
                if version == 1:
                    escala, dur = struct.unpack(">IQ", cuerpo[20:32])
                else:
                    escala, dur = struct.unpack(">II", cuerpo[12:20])
            except struct.error:
                return None
            return dur / escala if escala else None
        pos += size
    return None


class EntregasService:
    """Explorador de solo lectura de `exports/`."""

    def __init__(self, cfg) -> None:
        self.cfg = cfg
        self._dur: dict[tuple[str, int, int], float | None] = {}

    @property
    def raiz(self) -> Path:
        return Path(self.cfg.exports_dir)

    def disponible(self) -> bool:
        return self.raiz.is_dir()

    # ── rutas ────────────────────────────────────────────────────────────

    def resolver(self, ruta: str | None) -> Path:
        """Ruta absoluta dentro de `exports/`. ValueError si se sale.

        `exports/` puede ser un enlace a otro disco, asi que la comparacion
        va contra el destino REAL de la raiz (y del candidato)."""
        rel = (ruta or "").strip().strip("/")
        if rel in ("", "."):
            return self.raiz
        partes = [p for p in rel.split("/") if p not in ("", ".")]
        if any(p == ".." for p in partes) or len(partes) > 12:
            raise ValueError("ruta invalida")
        destino = self.raiz.joinpath(*partes)
        base = os.path.realpath(self.raiz)
        real = os.path.realpath(destino)
        if real != base and not real.startswith(base + os.sep):
            raise ValueError("ruta fuera de exports")
        return destino

    def _rel(self, path: Path) -> str:
        base = os.path.realpath(self.raiz)
        real = os.path.realpath(path)
        return "" if real == base else os.path.relpath(real, base)

    # ── consulta ─────────────────────────────────────────────────────────

    def _duracion(self, path: Path) -> float | None:
        try:
            st = path.stat()
        except OSError:
            return None
        clave = (str(path), st.st_size, int(st.st_mtime))
        if clave not in self._dur:
            self._dur[clave] = duracion_mp4(path)
        return self._dur[clave]

    def _resumen_carpeta(self, path: Path) -> dict:
        """Cuantos archivos y cuantos bytes cuelgan de una carpeta (en todo
        su arbol). Es lo que hace util la vista: se ve el peso de la entrega
        sin entrar."""
        archivos = bytes_ = 0
        for raiz, _dirs, nombres in os.walk(path):
            for n in nombres:
                try:
                    bytes_ += os.path.getsize(os.path.join(raiz, n))
                    archivos += 1
                except OSError:
                    continue
            if archivos > MAX_ENTRADAS:
                break
        return {"archivos": archivos, "bytes": bytes_}

    def listar(self, ruta: str | None = None) -> dict:
        destino = self.resolver(ruta)
        if not destino.is_dir():
            raise FileNotFoundError(ruta or "")
        carpetas, archivos = [], []
        try:
            entradas = sorted(os.scandir(destino), key=lambda e: e.name.lower())
        except OSError as e:
            raise FileNotFoundError(str(e))
        for e in entradas[:MAX_ENTRADAS]:
            rel = self._rel(Path(e.path))
            try:
                if e.is_dir():
                    resumen = self._resumen_carpeta(Path(e.path))
                    carpetas.append({
                        "nombre": e.name, "ruta": rel,
                        "titulo": NOMBRES.get(e.name),
                        "modificado": e.stat().st_mtime, **resumen,
                    })
                elif e.is_file():
                    st = e.stat()
                    tipo, _mt = tipo_de(e.name)
                    archivos.append({
                        "nombre": e.name, "ruta": rel, "tipo": tipo,
                        "bytes": st.st_size, "modificado": st.st_mtime,
                        "duracion": None,
                    })
            except OSError:
                continue
        # Duraciones solo de los videos, y solo si la carpeta es manejable.
        videos = [a for a in archivos if a["tipo"] == "video"]
        if len(videos) <= MAX_DURACIONES:
            for a in videos:
                a["duracion"] = self._duracion(destino / a["nombre"])
        padre = None
        rel_actual = self._rel(destino)
        if rel_actual:
            padre = str(Path(rel_actual).parent) if "/" in rel_actual else ""
        return {
            "ruta": rel_actual, "padre": padre,
            "titulo": NOMBRES.get(destino.name) if rel_actual else "Biblioteca",
            "carpetas": carpetas, "archivos": archivos,
            "bytes": sum(a["bytes"] for a in archivos)
                     + sum(c["bytes"] for c in carpetas),
        }

    def archivo(self, ruta: str) -> tuple[Path, str]:
        destino = self.resolver(ruta)
        if not destino.is_file():
            raise FileNotFoundError(ruta)
        _tipo, media = tipo_de(destino.name)
        return destino, media
