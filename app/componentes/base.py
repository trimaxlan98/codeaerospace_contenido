"""Piezas comunes de los paneles: rutas del proyecto y un ejecutor de procesos con registro en pantalla."""
import sys
from pathlib import Path

from PySide6.QtCore import QProcess, QProcessEnvironment
from PySide6.QtWidgets import QPlainTextEdit

ROOT = Path(__file__).resolve().parent.parent.parent
ANIM = ROOT / "animaciones"
EXPORTS = ROOT / "exports"


def animaciones_en_path():
    """Deja importables los módulos de animaciones/ (temas_espaciales, traducciones_en…)."""
    if str(ANIM) not in sys.path:
        sys.path.insert(0, str(ANIM))


class Ejecutor:
    """Corre un proceso (python, bash…) en animaciones/ y vuelca su salida a un QPlainTextEdit; un proceso a la vez."""

    def __init__(self, padre, log: QPlainTextEdit, al_terminar=None, cambia_estado=None):
        self.padre, self.log, self.al_terminar, self.cambia_estado = padre, log, al_terminar, cambia_estado
        self.proc = None

    @property
    def ocupado(self):
        return self.proc is not None and self.proc.state() != QProcess.NotRunning

    def correr(self, programa, args, env=None, cwd=None):
        if self.ocupado:
            self.log.appendPlainText("Ya hay un proceso en marcha.")
            return False
        self.proc = QProcess(self.padre)
        self.proc.setWorkingDirectory(str(cwd or ANIM))
        self.proc.setProcessChannelMode(QProcess.MergedChannels)
        if env:
            e = QProcessEnvironment.systemEnvironment()
            for k, v in env.items():
                e.insert(k, v)
            self.proc.setProcessEnvironment(e)
        self.proc.readyRead.connect(self._leer)
        self.proc.finished.connect(self._fin)
        self.log.appendPlainText(f"$ {programa} {' '.join(args)}" + (f"   [{' '.join(f'{k}={v}' for k, v in env.items())}]" if env else ""))
        if self.cambia_estado:
            self.cambia_estado(True)
        self.proc.start(programa, args)
        return True

    def detener(self):
        if self.ocupado:
            self.proc.kill()

    def _leer(self):
        txt = bytes(self.proc.readAll()).decode(errors="replace")
        # las barras de progreso de manim usan \r: quedarse con el último tramo de cada línea
        for linea in txt.replace("\r", "\n").split("\n"):
            if linea.strip():
                self.log.appendPlainText(linea.rstrip())

    def _fin(self, codigo, _estado):
        self.log.appendPlainText(f"--- terminado (código {codigo}) ---")
        if self.cambia_estado:
            self.cambia_estado(False)
        if self.al_terminar:
            self.al_terminar(codigo)


def python():
    return sys.executable
