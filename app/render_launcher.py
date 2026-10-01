"""App de Co.De Aerospace: lanzador de renders Manim y constructor de presentaciones espaciales.

Pestañas (cada una es un componente de app/componentes/):
  · Renders          escenas del proyecto (raíz y animaciones/) con tema oscuro/claro e idioma es/en
  · Presentaciones   decks espaciales: presentación + idioma + temas (uno por tema o mezclados) + temas nuevos
Uso: python app/render_launcher.py
"""
import re
import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication, QComboBox, QHBoxLayout, QLabel, QMainWindow, QPlainTextEdit, QPushButton, QTabWidget, QVBoxLayout,
    QWidget,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from componentes import tema_espacial  # noqa: E402
from componentes.base import ANIM, ROOT, Ejecutor  # noqa: E402
from componentes.presentaciones import PresentacionesPanel  # noqa: E402

QUALITIES = {"Baja (480p)": ["-ql"], "Media (720p)": ["-qm"], "Alta (1080p)": ["-qh"],
             "Producción (1080p30)": ["-r", "1920,1080", "--fps", "30"], "4K": ["-qk"]}
SCENE_RE = re.compile(r"^class\s+(\w+)\((?:Pieza\w*|\w*Scene\w*)\)", re.M)


def discover_scenes():
    """Devuelve [(ruta relativa a ROOT, clase)] para cada escena Manim del proyecto (raíz y animaciones/)."""
    found = []
    for carpeta in (ROOT, ANIM):
        for py in sorted(carpeta.glob("*.py")):
            if py.name.startswith("_") or py.name == "code_lib.py":
                continue
            for cls in SCENE_RE.findall(py.read_text(encoding="utf-8", errors="replace")):
                if cls not in ("Pieza", "Pieza3D"):
                    found.append((py.relative_to(ROOT).as_posix(), cls))
    return found


class RendersPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.log = QPlainTextEdit(readOnly=True)
        self.ejecutor = Ejecutor(self, self.log, self.done, self._ocupado)
        titulo = QLabel("RENDERS")
        titulo.setObjectName("titulo")
        self.scene = QComboBox()
        for f, c in discover_scenes():
            self.scene.addItem(f"{c}  ({f})", (f, c))
        self.quality = QComboBox()
        self.quality.addItems(QUALITIES)
        self.quality.setCurrentText("Media (720p)")
        self.tema = QComboBox()
        self.tema.addItem("Fondo oscuro", "oscuro")
        self.tema.addItem("Fondo claro", "claro")
        self.idioma = QComboBox()
        self.idioma.addItem("Español", "es")
        self.idioma.addItem("English (strict translation)", "en")

        self.btn_render = QPushButton("Renderizar")
        self.btn_render.setObjectName("primario")
        self.btn_render.clicked.connect(self.render)
        self.btn_stop = QPushButton("Detener")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.ejecutor.detener)
        self.btn_open = QPushButton("Abrir carpeta de videos")
        self.btn_open.clicked.connect(self.open_videos)

        top = QHBoxLayout()
        for w in (QLabel("Escena:"), self.scene, QLabel("Calidad:"), self.quality, self.tema, self.idioma):
            top.addWidget(w)
        top.setStretch(1, 1)
        bar = QHBoxLayout()
        for b in (self.btn_render, self.btn_stop, self.btn_open):
            bar.addWidget(b)
        nota = QLabel("Las escenas de animaciones/ respetan tema e idioma (CODE_TEMA / CODE_IDIOMA). En inglés, una cadena sin traducir aborta el render.")
        nota.setObjectName("nota")
        lay = QVBoxLayout(self)
        lay.addWidget(titulo)
        lay.addWidget(nota)
        lay.addLayout(top)
        lay.addLayout(bar)
        lay.addWidget(self.log)

    def _ocupado(self, si):
        self.btn_render.setEnabled(not si)
        self.btn_stop.setEnabled(si)

    def render(self):
        data = self.scene.currentData()
        if not data:
            self.log.appendPlainText("No se encontraron escenas.")
            return
        file, cls = data
        q = QUALITIES[self.quality.currentText()]
        en_anim = file.startswith("animaciones/")
        ruta = Path(file).name if en_anim else file
        args = ["-m", "manim", "render", *q, "-o", cls, ruta, cls] if en_anim else ["-m", "manim", "render", "-p", *q, file, cls]
        env = {"CODE_TEMA": self.tema.currentData(), "CODE_IDIOMA": self.idioma.currentData()} if en_anim else None
        self.ejecutor.correr(sys.executable, args, env, ANIM if en_anim else ROOT)

    def done(self, _code):
        pass

    def open_videos(self):
        d = (ANIM if (ANIM / "media").exists() else ROOT) / "media" / "videos"
        d.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(d)))


class Launcher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Co.De Aerospace · Estudio")
        self.resize(1180, 820)
        self.tabs = QTabWidget()
        self.tabs.addTab(PresentacionesPanel(), "PRESENTACIONES")
        self.tabs.addTab(RendersPanel(), "RENDERS")
        raiz = QWidget()
        raiz.setObjectName("raiz")
        QVBoxLayout(raiz).addWidget(self.tabs)
        self.setCentralWidget(raiz)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    tema_espacial.aplicar(app)
    w = Launcher()
    w.show()
    sys.exit(app.exec())
