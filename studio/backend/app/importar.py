"""Un proyecto es un directorio: leerlo, escribirlo y aplicarlo a la base.

Hasta el sprint R3a un curso NUEVO nacia en la terminal: `subir_curso.py`
leia `studio/content/cursos/<slug>/` (curso.json + style_block.py +
clips/NN-*.py) y lo metia en la base con los mismos modulos que la API. La
app no sabia ni leer ni escribir esa forma, asi que git y la base eran dos
estados distintos que solo un humano sincronizaba.

Aqui vive ese trabajo, UNA vez, sin FastAPI y sin `sys.exit`:

  - `cargar_curso`      un curso horizontal (curso.json con `clips`)
  - `cargar_vertical`   un curso 9:16 (curso.json con `piezas`, y una
                        `clip.json` + `escena.py` por pieza)
  - `cargar_promo`      un promo de redes (promo.json, un solo clip)
  - `aplicar`           lo escribe en la base, idempotente por nombre
  - `exportar_fuentes`  el camino de vuelta: el zip de fuentes
  - `abrir_zip`         un zip de fuentes recibido por HTTP, validado

`studio/tools/subir_curso.py` y `subir_promo.py` son ahora envoltorios de
estas funciones (traducen `ErrorImportacion` a `sys.exit`), de modo que la
terminal y la app ejecutan EL MISMO codigo y no pueden divergir.

Reglas que no cambian respecto del CLI:

  - **Idempotente por nombre exacto**: el proyecto se empareja por `name` y
    los clips por POSICION. Se crea lo que falta y se actualiza lo que
    cambio; nunca se borra nada (borrar es decision humana, desde la UI).
  - **Nada de renders**: si un clip cambia queda `stale` por hash y se
    re-renderiza cuando alguien lo pida.
"""

import json
import re
import unicodedata
import zipfile
from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path

from . import audio_promo
from .db import Database
from .projects import (FORMATO_DEFECTO, FORMATOS, QUALITIES, TIPO_DEFECTO,
                       TIPOS, ProjectService, compose_script, content_hash)
from .scenes import detect_scenes

# Los tres directorios de `studio/content/` que contienen proyectos. Cada uno
# tiene su propio manifiesto porque son tres formatos distintos, no tres
# variantes del mismo.
ORIGENES = ("cursos", "verticales", "promos")

# El nombre de un directorio de contenido es un slug de git: minusculas,
# digitos y guiones. Sin puntos (para que `..` no pueda existir ni por
# composicion) y sin barras. Los 60 cursos del repo ya cumplen esto.
RE_SLUG = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,78}[a-z0-9])?\Z")

# Prefijo de nombre de un promo: el indice de la app agrupa por lo que hay
# antes del "·", asi que los promos salen juntos y no mezclados con las
# lecciones de los cursos.
PREFIJO_PROMO = "Promo · "
CALIDAD_PROMO = "qh"
# Un vertical no declara calidad en su curso.json: los seis que existen se
# renderizaron en alta, que es lo unico que tiene sentido para Instagram.
CALIDAD_VERTICAL = "qh"

# Topes del zip que llega por HTTP. Un curso de 30 clips de fuentes pesa
# ~300 KB; 5 MB es dos ordenes de magnitud de aire y corta en seco cualquier
# bomba de descompresion.
MAX_ZIP_BYTES = 5 * 1024 * 1024
MAX_MIEMBROS = 400
MAX_DESCOMPRIMIDO = 24 * 1024 * 1024

# Lo unico que un zip de fuentes puede contener. Todo lo demas se rechaza
# (no se ignora): un zip con archivos de mas es casi siempre otra cosa.
PREFIJOS_ZIP = ("clips/", "guiones/")
RAICES_ZIP = ("curso.json", "style_block.py")

# Fecha fija de los miembros del zip. Sin esto el zip lleva la hora de
# generacion en cada cabecera local y dos exportaciones del MISMO proyecto
# salen con bytes distintos: el round-trip deja de ser verificable.
FECHA_ZIP = (1980, 1, 1, 0, 0, 0)


class ErrorImportacion(Exception):
    """Un manifiesto que no se puede aplicar. El mensaje es para el humano."""


# ── nombres de archivo ───────────────────────────────────────────────────

def slug(texto: str) -> str:
    """Slug ASCII de un titulo. MISMA funcion que `narracion.slugify`.

    Se repite aqui (cuatro lineas) en vez de importarse porque `narracion`
    arrastra el TTS entero —edge_tts, miniaudio, el cliente de Vertex— y
    este modulo lo usan tambien los CLI de la terminal, que no tienen por
    que cargar nada de eso. `tests/test_projects_r3a.py` compara las dos
    funciones sobre una bateria de titulos para que no se separen.
    """
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z0-9]+", "-", texto.lower()).strip("-")[:40]
    return s or "clip"


def etiqueta(position: int, title: str) -> str:
    """`01-el-numero-de-mach`: el nombre base de un clip en los archivos.

    Es el MISMO que usa `narracion.etiqueta_clip`, y por eso el guion de un
    clip exportado se vuelve a encontrar al reimportarlo.
    """
    return f"{position + 1:02d}-{slug(title)}"


# ── el manifiesto en memoria ─────────────────────────────────────────────

def _clip(title: str, script: str, scene: str, final_state: str = "",
          notes: str = "", audio_json: str | None = None) -> dict:
    return {"title": title, "script": script, "scene": scene,
            "final_state": final_state, "notes": notes,
            "audio_json": audio_json}


def _valida_escena(style: str, script: str, scene: str, donde: str) -> None:
    compuesto = compose_script(style, script)
    try:
        escenas = detect_scenes(compuesto)
    except ValueError as e:
        raise ErrorImportacion(f"{donde}: script invalido: {e}")
    if scene not in escenas:
        raise ErrorImportacion(
            f"{donde}: la escena '{scene}' no esta definida en el script "
            "compuesto")


def _leer_json(path: Path) -> dict:
    if not path.is_file():
        raise ErrorImportacion(f"no existe {path}")
    try:
        datos = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise ErrorImportacion(f"{path}: no se puede leer ({e})")
    if not isinstance(datos, dict):
        raise ErrorImportacion(f"{path}: el manifiesto no es un objeto")
    return datos


def _leer_texto(path: Path, donde: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as e:
        raise ErrorImportacion(f"{donde}: no se puede leer {path} ({e})")


def _estilo(curso_dir: Path, manifiesto: dict) -> str:
    nombre = manifiesto.get("style_block") or "style_block.py"
    if "/" in nombre or "\\" in nombre or nombre.startswith("."):
        raise ErrorImportacion(f"style_block invalido: {nombre!r}")
    path = curso_dir / nombre
    return _leer_texto(path, "style_block") if path.is_file() else ""


def _sub_ruta(base: Path, relativa: str, donde: str) -> Path:
    """`base / relativa` comprobando que no se sale del directorio."""
    if not relativa or relativa.startswith("/") or "\\" in relativa:
        raise ErrorImportacion(f"{donde}: ruta invalida {relativa!r}")
    destino = (base / relativa).resolve()
    if base.resolve() not in destino.parents and destino != base.resolve():
        raise ErrorImportacion(f"{donde}: ruta fuera del proyecto: {relativa!r}")
    return destino


def cargar_curso(curso_dir: Path) -> dict:
    """Un curso horizontal: curso.json + style_block.py + clips/NN-*.py."""
    curso_dir = Path(curso_dir)
    manifiesto = _leer_json(curso_dir / "curso.json")

    for campo in ("name", "quality", "clips"):
        if not manifiesto.get(campo):
            raise ErrorImportacion(
                f"curso.json sin campo obligatorio: {campo}")
    quality = manifiesto["quality"]
    if quality not in QUALITIES:
        raise ErrorImportacion(f"calidad invalida: {quality}")
    formato = manifiesto.get("formato") or FORMATO_DEFECTO
    if formato not in FORMATOS:
        raise ErrorImportacion(f"formato invalido: {formato}")
    tipo = manifiesto.get("tipo") or TIPO_DEFECTO
    if tipo not in TIPOS:
        raise ErrorImportacion(f"tipo invalido: {tipo}")

    style = _estilo(curso_dir, manifiesto)
    clips = []
    for i, spec in enumerate(manifiesto["clips"]):
        if not isinstance(spec, dict) or not spec.get("file"):
            raise ErrorImportacion(f"clip {i + 1}: falta el campo file")
        ruta = _sub_ruta(curso_dir, spec["file"], f"clip {i + 1}")
        if not ruta.is_file():
            raise ErrorImportacion(f"clip {i + 1}: no existe {ruta}")
        script = _leer_texto(ruta, f"clip {i + 1}")
        scene = spec.get("scene") or ""
        _valida_escena(style, script, scene, f"clip {i + 1} ({ruta.name})")
        clips.append(_clip(spec.get("title") or ruta.stem, script, scene,
                           spec.get("final_state") or "",
                           spec.get("notes") or ""))

    return {"name": manifiesto["name"],
            "description": manifiesto.get("description") or "",
            "quality": quality, "formato": formato, "tipo": tipo,
            "estilo": str(manifiesto.get("estilo") or ""),
            "style_block": style, "clips": clips}


def notas_pieza(pieza: dict) -> str:
    """Las notas de un clip vertical a partir de su `clip.json`.

    Modulo y duracion objetivo NO tienen columna propia: viajan en `notes`,
    que es texto libre y ya viaja en el manifiesto exportado. Asi el
    round-trip de un vertical no pierde nada sin pagar una migracion por
    dos campos que solo un vertical usa. El formato es fijo (mismas lineas,
    mismo orden) para que reimportar dos veces no genere un cambio.
    """
    lineas = []
    modulo = str(pieza.get("modulo") or "").strip()
    if modulo:
        lineas.append(f"Módulo: {modulo}")
    dur = pieza.get("duracion_objetivo")
    if isinstance(dur, (int, float)):
        lineas.append(f"Duración objetivo: {float(dur):.2f} s")
    desc = str(pieza.get("description") or "").strip()
    if desc:
        lineas.append(desc)
    return "\n".join(lineas)


def cargar_vertical(curso_dir: Path) -> dict:
    """Un curso vertical: curso.json con `piezas`, y una `clip.json` +
    `escena.py` por pieza.

    Cada pieza se convierte en un clip del proyecto. Su bloque `audio`/`voz`
    (cama de sonido y, si la trae, voz) se guarda normalizado en
    `audio_json`, que es exactamente lo que la app mezcla; `modulo` y
    `duracion_objetivo` van a `notes` (ver `notas_pieza`).
    """
    curso_dir = Path(curso_dir)
    manifiesto = _leer_json(curso_dir / "curso.json")
    if not manifiesto.get("name"):
        raise ErrorImportacion("curso.json sin campo obligatorio: name")
    piezas = manifiesto.get("piezas")
    if not piezas:
        raise ErrorImportacion("curso.json sin campo obligatorio: piezas")

    formato = manifiesto.get("formato") or "vertical"
    if formato not in FORMATOS:
        raise ErrorImportacion(f"formato invalido: {formato}")
    quality = manifiesto.get("quality") or CALIDAD_VERTICAL
    if quality not in QUALITIES:
        raise ErrorImportacion(f"calidad invalida: {quality}")

    style = _estilo(curso_dir, manifiesto)
    clips = []
    for i, spec in enumerate(piezas):
        donde = f"pieza {i + 1}"
        if not isinstance(spec, dict) or not spec.get("dir"):
            raise ErrorImportacion(f"{donde}: falta el campo dir")
        pieza_dir = _sub_ruta(curso_dir, spec["dir"], donde)
        pieza = _leer_json(pieza_dir / "clip.json")
        archivo = pieza.get("file") or "escena.py"
        ruta = _sub_ruta(pieza_dir, archivo, donde)
        if not ruta.is_file():
            raise ErrorImportacion(f"{donde}: no existe {ruta}")
        script = _leer_texto(ruta, donde)
        scene = pieza.get("scene") or ""
        _valida_escena(style, script, scene, f"{donde} ({spec['dir']})")

        manifiesto_audio = None
        if pieza.get("audio") or pieza.get("voz"):
            normalizado = audio_promo.normalizar(
                {"audio": pieza.get("audio"), "voz": pieza.get("voz")})
            errores = audio_promo.validar(normalizado)
            if errores:
                raise ErrorImportacion(
                    f"{donde}: manifiesto de audio invalido: "
                    + "; ".join(errores))
            manifiesto_audio = json.dumps(normalizado, ensure_ascii=False)

        clips.append(_clip(pieza.get("name") or pieza_dir.name, script, scene,
                           "", notas_pieza(pieza), manifiesto_audio))

    return {"name": manifiesto["name"],
            "description": manifiesto.get("description") or "",
            "quality": quality, "formato": formato, "tipo": TIPO_DEFECTO,
            "estilo": str(manifiesto.get("estilo") or ""),
            "style_block": style, "clips": clips}


def cargar_promo(promo_dir: Path) -> dict:
    """Un promo de redes: promo.json + style_block.py + escena.py.

    Un promo es un proyecto de UN clip (`tipo='promo'`), vertical y en `qh`,
    y trae su audio dentro del manifiesto.
    """
    promo_dir = Path(promo_dir)
    manifiesto = _leer_json(promo_dir / "promo.json")
    for campo in ("name", "scene", "file"):
        if not manifiesto.get(campo):
            raise ErrorImportacion(
                f"{promo_dir / 'promo.json'}: falta el campo obligatorio {campo}")

    style = _estilo(promo_dir, manifiesto)
    ruta = _sub_ruta(promo_dir, manifiesto["file"], "promo")
    if not ruta.is_file():
        raise ErrorImportacion(f"{promo_dir / 'promo.json'}: no existe {ruta}")
    script = _leer_texto(ruta, "promo")
    _valida_escena(style, script, manifiesto["scene"], promo_dir.name)

    # El formato sale del manifiesto (el primero de la lista es el que se
    # trabajo); si no lo dice, vertical, que es el formato de redes.
    formato = (manifiesto.get("formatos") or ["vertical"])[0]
    if formato not in FORMATOS:
        raise ErrorImportacion(f"{promo_dir.name}: formato desconocido "
                               f"'{formato}'")

    normalizado = audio_promo.normalizar(
        {"audio": manifiesto.get("audio"), "voz": manifiesto.get("voz")})
    errores = audio_promo.validar(normalizado)
    if errores:
        raise ErrorImportacion(f"{promo_dir.name}: manifiesto de audio "
                               "invalido: " + "; ".join(errores))

    descripcion = manifiesto.get("description") or ""
    curso = manifiesto.get("curso")
    if curso and curso.lower() not in descripcion.lower():
        descripcion = f"[{curso}] {descripcion}".strip()

    clip = _clip(manifiesto["name"], script, manifiesto["scene"],
                 audio_json=json.dumps(normalizado, ensure_ascii=False))
    return {"name": PREFIJO_PROMO + manifiesto["name"],
            "description": descripcion, "quality": CALIDAD_PROMO,
            "formato": formato, "tipo": "promo", "estilo": "",
            "style_block": style, "clips": [clip],
            "duracion_objetivo": manifiesto.get("duracion_objetivo")}


CARGADORES = {"cursos": cargar_curso, "verticales": cargar_vertical,
              "promos": cargar_promo}


def cargar_del_repo(base: Path, origen: str, slug_dir: str) -> dict:
    """El proyecto `<base>/<origen>/<slug>/`, validando el slug a mano.

    El slug llega de HTTP: se comprueba contra un regex cerrado ANTES de
    tocar el disco y, ademas, se verifica que la ruta resuelta siga dentro
    de su origen (defensa en profundidad contra enlaces simbolicos).
    """
    if origen not in ORIGENES:
        raise ErrorImportacion(
            f"origen invalido: {origen!r} (usa {', '.join(ORIGENES)})")
    if not RE_SLUG.match(slug_dir or ""):
        raise ErrorImportacion(
            f"slug invalido: {slug_dir!r} (minusculas, digitos y guiones)")
    raiz = (Path(base) / origen).resolve()
    destino = (raiz / slug_dir).resolve()
    if raiz not in destino.parents:
        raise ErrorImportacion(f"slug fuera de {origen}: {slug_dir!r}")
    if not destino.is_dir():
        raise ErrorImportacion(f"no existe {origen}/{slug_dir} en el repo")
    return CARGADORES[origen](destino)


def listar_del_repo(base: Path) -> dict[str, list[str]]:
    """Los slugs disponibles por origen (para el desplegable de la UI)."""
    salida: dict[str, list[str]] = {}
    for origen in ORIGENES:
        raiz = Path(base) / origen
        manifiesto = "promo.json" if origen == "promos" else "curso.json"
        try:
            slugs = sorted(d.name for d in raiz.iterdir()
                           if d.is_dir() and (d / manifiesto).is_file()
                           and RE_SLUG.match(d.name))
        except OSError:
            slugs = []
        salida[origen] = slugs
    return salida


# ── aplicar sobre la base ────────────────────────────────────────────────

@dataclass
class Resultado:
    """Lo que dejo (o dejaria, en dry-run) una importacion."""
    reporte: list[str] = field(default_factory=list)
    project_id: str | None = None
    creado: bool = False
    clips: int = 0          # clips del manifiesto
    creados: int = 0        # clips nuevos en la base
    actualizados: int = 0   # clips que cambiaron
    stale: int = 0          # clips que se quedaron sin render vigente

    def publico(self) -> dict:
        return {"project_id": self.project_id, "creado": self.creado,
                "clips": self.clips, "creados": self.creados,
                "actualizados": self.actualizados, "stale": self.stale,
                "reporte": self.reporte}


CAMPOS_CLIP = ("title", "script", "scene", "final_state", "notes")


def aplicar(service: ProjectService, db: Database, curso: dict,
            dry_run: bool = False) -> Resultado:
    """Escribe el manifiesto en la base. Idempotente por nombre exacto.

    Empareja el proyecto por `name` y los clips por POSICION: crea lo que
    falta, actualiza lo que cambio y NUNCA borra (si la base tiene mas clips
    que el manifiesto, avisa y los deja).
    """
    r = Resultado(clips=len(curso["clips"]))
    proyecto = next((p for p in db.list_projects()
                     if p["name"] == curso["name"]), None)

    if proyecto is None:
        r.creado = True
        r.reporte.append(f"+ proyecto nuevo: {curso['name']!r} "
                         f"({curso['quality']})")
        if not dry_run:
            proyecto = service.create_project(
                curso["name"], curso["description"], curso["quality"],
                curso["style_block"], tipo=curso.get("tipo", TIPO_DEFECTO),
                formato=curso.get("formato", FORMATO_DEFECTO),
                estilo=curso.get("estilo", ""))
            r.project_id = proyecto["id"]
    else:
        r.project_id = proyecto["id"]
        cambios = {k: curso[k] for k in ("description", "style_block")
                   if proyecto.get(k) != curso[k]}
        if curso.get("estilo") and proyecto.get("estilo") != curso["estilo"]:
            cambios["estilo"] = curso["estilo"]
        # Calidad y formato solo se intentan si de verdad cambiaron:
        # update_project los rechaza con renders vigentes, y ese aviso es
        # informacion, no un fallo del importador.
        for campo, clave in (("quality", "quality"), ("formato", "formato")):
            valor = curso.get(clave)
            if valor and proyecto.get(campo) != valor:
                cambios[campo] = valor
        if cambios:
            r.reporte.append(f"~ proyecto {proyecto['id']}: actualiza "
                             + ", ".join(sorted(cambios)))
            if not dry_run:
                try:
                    proyecto = service.update_project(proyecto["id"], **cambios)
                except ValueError as e:
                    r.reporte.append(f"  ! {e}")
                    for campo in ("quality", "formato"):
                        cambios.pop(campo, None)
                    if cambios:
                        proyecto = service.update_project(proyecto["id"],
                                                          **cambios)
        else:
            r.reporte.append(f"= proyecto {proyecto['id']}: sin cambios de "
                             "metadatos")

    existentes = db.list_clips(proyecto["id"]) if proyecto else []
    for pos, clip in enumerate(curso["clips"]):
        actual = existentes[pos] if pos < len(existentes) else None
        if actual is None:
            r.creados += 1
            r.reporte.append(f"+ clip {pos + 1}: {clip['title']!r}")
            if not dry_run:
                creado = service.add_clip(proyecto["id"], clip["title"],
                                          clip["script"], clip["scene"],
                                          position=pos)
                extra = {"final_state": clip["final_state"],
                         "notes": clip["notes"]}
                if clip.get("audio_json"):
                    extra["audio_json"] = clip["audio_json"]
                service.update_clip(creado["id"], **extra)
            continue

        campos = {k: clip[k] for k in CAMPOS_CLIP
                  if (actual.get(k) or "") != clip[k]}
        if clip.get("audio_json") and \
                (actual.get("audio_json") or "") != clip["audio_json"]:
            campos["audio_json"] = clip["audio_json"]
        if not campos:
            r.reporte.append(f"= clip {pos + 1}: {clip['title']!r} al dia")
            continue
        r.actualizados += 1
        nuevo_hash = content_hash(curso["style_block"], clip["script"],
                                  clip["scene"])
        stale = (bool(actual.get("job_id"))
                 and actual.get("rendered_hash") != nuevo_hash)
        if stale:
            r.stale += 1
        visibles = sorted(c for c in campos if c != "audio_json")
        detalle = ", ".join(visibles) or "manifiesto de audio"
        if visibles and "audio_json" in campos:
            detalle += ", manifiesto de audio"
        r.reporte.append(f"~ clip {pos + 1}: {clip['title']!r} actualiza "
                         + detalle
                         + ("  -> STALE (re-render)" if stale else ""))
        if not dry_run:
            service.update_clip(actual["id"], **campos)

    if proyecto and len(existentes) > len(curso["clips"]):
        sobran = existentes[len(curso["clips"]):]
        r.reporte.append("! en la base sobran "
                         f"{len(sobran)} clips no listados en el manifiesto "
                         "(no se borran): "
                         + ", ".join(c["title"] for c in sobran))
    return r


# ── exportacion: el proyecto de vuelta a archivos ────────────────────────

def manifiesto_de(project: dict, clips: list[dict]) -> dict:
    """El `curso.json` de un proyecto de la base, en el esquema que lee
    `cargar_curso` (y por tanto `subir_curso.py`)."""
    salida = {
        "name": project["name"],
        "description": project.get("description") or "",
        "quality": project["quality"],
        "formato": project.get("formato") or FORMATO_DEFECTO,
        "tipo": project.get("tipo") or TIPO_DEFECTO,
    }
    if project.get("estilo"):
        salida["estilo"] = project["estilo"]
    salida["style_block"] = "style_block.py"
    salida["clips"] = [{
        "file": f"clips/{etiqueta(c['position'], c['title'])}.py",
        "title": c["title"],
        "scene": c.get("scene") or "",
        "final_state": c.get("final_state") or "",
        "notes": c.get("notes") or "",
    } for c in clips]
    return salida


def exportar_fuentes(project: dict, clips: list[dict],
                     guiones: dict[str, Path] | None = None) -> bytes:
    """El zip de fuentes del proyecto: lo que `cargar_curso` vuelve a leer.

        curso.json
        style_block.py
        clips/NN-<slug>.py
        guiones/NN-<slug>.secciones.json   (si el clip tiene guion)
        guiones/NN-<slug>.txt

    `guiones` mapea clip_id -> ruta BASE del guion en disco (sin sufijo),
    tal como la nombra `NarracionService`. Los archivos se copian tal cual,
    sin volver a serializarlos: lo que se exporta es lo que hay.

    El zip es DETERMINISTA (fecha fija, orden fijo, sin compresion): dos
    exportaciones del mismo proyecto dan los mismos bytes, que es lo que
    hace verificable el round-trip export -> import -> export.
    """
    manifiesto = manifiesto_de(project, clips)
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_STORED) as zf:
        def escribe(nombre: str, datos: bytes) -> None:
            info = zipfile.ZipInfo(nombre, date_time=FECHA_ZIP)
            info.external_attr = 0o644 << 16
            zf.writestr(info, datos)

        escribe("curso.json",
                (json.dumps(manifiesto, indent=2, ensure_ascii=False) + "\n")
                .encode("utf-8"))
        escribe("style_block.py",
                (project.get("style_block") or "").encode("utf-8"))
        for clip in clips:
            escribe(f"clips/{etiqueta(clip['position'], clip['title'])}.py",
                    (clip.get("script") or "").encode("utf-8"))
        for clip in clips:
            base = (guiones or {}).get(clip["id"])
            if base is None:
                continue
            nombre = etiqueta(clip["position"], clip["title"])
            for sufijo in (".secciones.json", ".txt"):
                origen = Path(f"{base}{sufijo}")
                try:
                    datos = origen.read_bytes()
                except OSError:
                    continue
                escribe(f"guiones/{nombre}{sufijo}", datos)
    return buf.getvalue()


# ── el zip de vuelta: validacion y extraccion ────────────────────────────

def _nombre_seguro(nombre: str) -> bool:
    if not nombre or nombre.startswith("/") or "\\" in nombre:
        return False
    if "\x00" in nombre or nombre.endswith("/"):
        return False
    partes = nombre.split("/")
    if any(p in ("", ".", "..") for p in partes):
        return False
    if nombre in RAICES_ZIP:
        return True
    return (nombre.startswith(PREFIJOS_ZIP) and len(partes) == 2)


def abrir_zip(datos: bytes, destino: Path) -> Path:
    """Extrae un zip de fuentes en `destino` y devuelve ese directorio.

    Solo se aceptan los nombres del layout de `exportar_fuentes`: nada de
    rutas absolutas, `..`, subdirectorios de mas ni enlaces. El tope de
    tamano se comprueba dos veces (comprimido y descomprimido) para que un
    zip pequeno no pueda pedir gigabytes de disco.
    """
    if len(datos) > MAX_ZIP_BYTES:
        raise ErrorImportacion(
            f"el zip pasa de {MAX_ZIP_BYTES // (1024 * 1024)} MB")
    try:
        zf = zipfile.ZipFile(BytesIO(datos))
    except zipfile.BadZipFile:
        raise ErrorImportacion("el cuerpo no es un zip valido")
    with zf:
        miembros = zf.infolist()
        if len(miembros) > MAX_MIEMBROS:
            raise ErrorImportacion(f"el zip trae mas de {MAX_MIEMBROS} archivos")
        total = sum(m.file_size for m in miembros)
        if total > MAX_DESCOMPRIMIDO:
            raise ErrorImportacion("el zip se descomprime a demasiado")
        nombres = set()
        for m in miembros:
            if m.is_dir():
                continue
            if not _nombre_seguro(m.filename):
                raise ErrorImportacion(
                    f"el zip trae un archivo que no toca: {m.filename!r}")
            nombres.add(m.filename)
        if "curso.json" not in nombres:
            raise ErrorImportacion("el zip no trae curso.json")

        destino = Path(destino)
        for m in miembros:
            if m.is_dir():
                continue
            salida = destino / m.filename
            salida.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(m) as src:
                salida.write_bytes(src.read())
    return destino


def guiones_del_zip(curso_dir: Path, curso: dict) -> dict[int, list[dict]]:
    """Guiones del zip por POSICION de clip: {pos: secciones}.

    El nombre del archivo es el canonico (`NN-<slug del titulo>`), asi que
    se busca por el que le tocaria a cada clip del manifiesto y no por el
    numero suelto: dos clips nunca colisionan.
    """
    salida: dict[int, list[dict]] = {}
    raiz = Path(curso_dir) / "guiones"
    if not raiz.is_dir():
        return salida
    for pos, clip in enumerate(curso["clips"]):
        path = raiz / f"{etiqueta(pos, clip['title'])}.secciones.json"
        if not path.is_file():
            continue
        try:
            secciones = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            raise ErrorImportacion(f"guion del clip {pos + 1}: {e}")
        if not isinstance(secciones, list):
            raise ErrorImportacion(
                f"guion del clip {pos + 1}: no es una lista de secciones")
        salida[pos] = secciones
    return salida
