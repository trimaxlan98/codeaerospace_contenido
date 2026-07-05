"""Metricas de sistema del host (psutil) para el centro de monitoreo."""

import time

import psutil


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
