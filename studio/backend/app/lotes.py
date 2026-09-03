"""Progreso agregado de un lote de renders.

Renderizar un curso entero es lo que se hace en la terminal con
`render_local.py --todos --calidad qh`. En la app existia el boton
«Re-renderizar desactualizados», que encolaba y despues dejaba al operador
contando tarjetas verdes de una en una: no habia ni «12 de 30», ni cuanto
falta, ni si alguno reviento.

Este modulo pone ese numero. La cola sigue siendo la de siempre (un job a la
vez, `JobManager`); un lote es solo **una lista de job_ids con nombre**.

Doble via a proposito:

  - **En memoria**: al encolar se guarda la lista exacta (un dict por
    proyecto). Es la verdad mientras el backend viva.
  - **Derivado de los jobs**: si el backend se reinicio y el dict esta
    vacio, el lote vigente se reconstruye desde la tabla de jobs — los que
    siguen activos y todo lo que se encolo desde el primero de ellos. No es
    el mismo objeto, pero responde la pregunta que importa ("¿que queda?")
    sin inventarse una tabla nueva.

Un lote NO es una cola aparte ni un estado del proyecto: si alguien encola
un clip suelto mientras corre el lote, ese clip entra en el conteo derivado
y no pasa nada. El lote mide el trabajo pendiente, no la intencion.
"""

import time
import uuid

ACTIVOS = ("queued", "running")
FALLIDOS = ("error", "timeout", "cancelled")


class LoteManager:
    def __init__(self, db) -> None:
        self.db = db
        self._lotes: dict[str, dict] = {}

    def abrir(self, pid: str, job_ids: list[str], calidad: str,
              saltados: int = 0) -> str:
        lote_id = uuid.uuid4().hex[:12]
        self._lotes[pid] = {"lote_id": lote_id, "creado": time.time(),
                            "calidad": calidad, "jobs": list(job_ids),
                            "saltados": saltados}
        return lote_id

    # ── consulta ─────────────────────────────────────────────────────────

    def estado(self, pid: str) -> dict | None:
        """El lote vigente del proyecto, o None si no hay ninguno."""
        jobs = self.db.project_jobs(pid)
        por_id = {j["id"]: j for j in jobs}
        lote = self._lotes.get(pid)
        derivado = False

        if lote:
            ids = [i for i in lote["jobs"] if i in por_id]
        else:
            activos = [j for j in jobs if j["status"] in ACTIVOS]
            if not activos:
                return None
            corte = min(j["created_at"] for j in activos)
            ids = [j["id"] for j in jobs if j["created_at"] >= corte]
            ids.reverse()  # project_jobs viene del mas nuevo al mas viejo
            derivado = True
            lote = {"lote_id": f"derivado-{pid[:8]}", "creado": corte,
                    "calidad": activos[0].get("quality"), "saltados": 0}
        if not ids:
            return None

        del_lote = [por_id[i] for i in ids]
        media = self._media(jobs)
        hechos = sum(1 for j in del_lote if j["status"] == "done")
        fallidos = sum(1 for j in del_lote if j["status"] in FALLIDOS)
        en_curso = sum(1 for j in del_lote if j["status"] == "running")
        pendientes = sum(1 for j in del_lote if j["status"] == "queued")

        return {
            "lote_id": lote["lote_id"],
            "creado": lote["creado"],
            "calidad": lote.get("calidad"),
            "derivado": derivado,
            "total": len(del_lote),
            "hechos": hechos,
            "fallidos": fallidos,
            "en_curso": en_curso,
            "pendientes": pendientes,
            "saltados": lote.get("saltados", 0),
            "activo": bool(en_curso or pendientes),
            "media_s": media,
            "eta_s": self._eta(media, del_lote),
            "jobs": [{"job_id": j["id"], "clip_id": j.get("clip_id"),
                      "status": j["status"], "error": j.get("error")}
                     for j in del_lote],
        }

    # ── estimacion ───────────────────────────────────────────────────────

    def _media(self, jobs: list[dict]) -> float | None:
        """Segundos que tarda un render de ESTE proyecto, de media.

        Solo cuentan los `done` con las dos marcas de tiempo: un job que
        fallo a los dos segundos no dice nada de lo que tarda un render
        bueno, y meterlo en la media haria que la estimacion cayera
        justo cuando algo va mal.
        """
        duraciones = [j["finished_at"] - j["started_at"] for j in jobs
                      if j["status"] == "done" and j.get("started_at")
                      and j.get("finished_at")
                      and j["finished_at"] > j["started_at"]]
        if not duraciones:
            return None
        return sum(duraciones) / len(duraciones)

    def _eta(self, media: float | None, del_lote: list[dict]) -> float | None:
        """Segundos que faltan, con la media del proyecto. None si aun no
        hay ni un render terminado del que aprender."""
        if media is None:
            return None
        restantes = sum(1 for j in del_lote if j["status"] in ACTIVOS)
        if not restantes:
            return 0.0
        eta = media * restantes
        # Al job en curso ya se le descuenta lo que lleva corriendo: sin
        # esto la ETA se queda clavada mientras el render avanza.
        for j in del_lote:
            if j["status"] == "running" and j.get("started_at"):
                eta -= min(time.time() - j["started_at"], media)
                break
        return max(eta, 0.0)
