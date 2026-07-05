"""Metricas de sistema del host (psutil) para el centro de monitoreo."""

import time
from collections import deque

import psutil

RENDER_PREFIX = "manimstudio-render-"


class History:
    """Ring buffer en memoria de muestras de metricas (cero disco, cero procesos).

    Lo alimenta el _metrics_loop existente en cada tick; con el intervalo por
    defecto (4 s) cubre los ultimos 30 minutos.
    """

    def __init__(self, maxlen: int) -> None:
        self.samples: deque[dict] = deque(maxlen=maxlen)

    def add(self, host: dict, containers: list | None) -> None:
        render = None
        if containers:
            for c in containers:
                if c.get("name", "").startswith(RENDER_PREFIX) and c.get("state") == "running":
                    render = c
                    break
        self.samples.append({
            "ts": host["ts"],
            "cpu": host["cpu_pct"],
            "mem": host["mem"]["pct"],
            "disk": host["disk"]["pct"],
            "render": render is not None,
            "render_cpu": render.get("cpu_pct") if render else None,
            "render_mem": render.get("mem_pct") if render else None,
        })


def host_metrics() -> dict:
    vm = psutil.virtual_memory()
    sw = psutil.swap_memory()
    disk = psutil.disk_usage("/")
    load1, load5, load15 = psutil.getloadavg()
    return {
        "ts": time.time(),
        "cpu_pct": psutil.cpu_percent(interval=None),
        "cpu_count": psutil.cpu_count(),
        "load": [round(load1, 2), round(load5, 2), round(load15, 2)],
        "mem": {"total": vm.total, "used": vm.used, "available": vm.available,
                "pct": vm.percent},
        "swap": {"total": sw.total, "used": sw.used, "pct": sw.percent},
        "disk": {"total": disk.total, "used": disk.used, "free": disk.free,
                 "pct": disk.percent},
    }
