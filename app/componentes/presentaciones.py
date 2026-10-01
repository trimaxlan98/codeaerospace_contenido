"""Panel «Presentaciones»: arma las presentaciones espaciales (decks_espaciales.py) desde la app.

Elige presentación (con su idioma), uno o varios temas y cómo usarlos:
  · un deck por tema, o
  · un solo deck que mezcla los temas marcados (uno por sección o uno por diapositiva).
También lista los temas registrados (incluidos los plugins de animaciones/temas/), muestra su vista previa,
avisa qué fuentes faltan en este equipo y crea temas derivados nuevos con «Nuevo tema…».
"""
from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QColor, QDesktopServices, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (
    QButtonGroup, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QMessageBox, QPlainTextEdit, QPushButton, QRadioButton, QSlider, QVBoxLayout, QWidget,
)

from . import tema_espacial as tema
from .base import ANIM, EXPORTS, Ejecutor, animaciones_en_path, python

# (presentación, idioma) → etiqueta. Debe coincidir con DECKS de animaciones/decks_espaciales.py.
PRESENTACIONES = [
    ("seminario", "es", "Seminario de divulgación  ·  ES"),
    ("seminario", "en", "Public seminar  ·  EN"),
    ("comite", "es", "Comité tutorial · protocolo  ·  ES"),
    ("divulgacion", "es", "Redes Orbitales · divulgación  ·  ES"),
]
CARPETA_SALIDA = EXPORTS / "presentaciones" / "espaciales"
PREVIEWS = CARPETA_SALIDA / "_fondos"


def _miniatura(t, ancho=96):
    """Icono de la lista: fondo de portada si existe; si no, un recuadro con los colores del tema."""
    jpg = PREVIEWS / f"{t.id}_portada_0.jpg"
    if jpg.exists():
        pm = QPixmap(str(jpg)).scaledToWidth(ancho, Qt.SmoothTransformation)
    else:
        pm = QPixmap(ancho, int(ancho * 9 / 16))
        pm.fill(QColor(t.pantalla or t.color["panel"]))
        p = QPainter(pm)
        for i, k in enumerate(("acento", "acento2", "calido")):
            p.fillRect(8 + i * 22, pm.height() - 16, 16, 8, QColor(t.color[k]))
        p.end()
    return QIcon(pm)


class NuevoTemaDialog(QDialog):
    """Crea un tema derivado (JSON en animaciones/temas/): base + giro de matiz + fuentes opcionales."""

    def __init__(self, padre, te):
        super().__init__(padre)
        self.te, self.F = te, te.F
        self.setWindowTitle("Nuevo tema")
        self.setMinimumWidth(460)
        self.id_ = QLineEdit()
        self.id_.setPlaceholderText("aurora (sin espacios)")
        self.nombre = QLineEdit()
        self.base = QComboBox()
        self.base.addItems(te.ids())
        self.tinte = QSlider(Qt.Horizontal)
        self.tinte.setRange(0, 360)
        self.tinte.setValue(140)
        self.desc = QLineEdit()
        self.titulo_f = QLineEdit()
        self.titulo_f.setPlaceholderText("(la de la base)")
        self.muestra = QLabel()
        self.muestra.setFixedHeight(34)
        self.estado = QLabel("")
        self.estado.setObjectName("aviso")
        f = QFormLayout()
        f.addRow("Id", self.id_)
        f.addRow("Nombre", self.nombre)
        f.addRow("Base", self.base)
        f.addRow("Matiz (°)", self.tinte)
        f.addRow("Colores", self.muestra)
        f.addRow("Fuente de títulos", self.titulo_f)
        f.addRow("Descripción", self.desc)
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.button(QDialogButtonBox.Ok).setText("Crear")
        bb.button(QDialogButtonBox.Cancel).setText("Cancelar")
        bb.accepted.connect(self.crear)
        bb.rejected.connect(self.reject)
        lay = QVBoxLayout(self)
        nota = QLabel("Un tema derivado toma la base, gira el matiz del fondo y de la paleta y puede cambiar la fuente. "
                      "El fondo se genera la primera vez que se usa (≈3 min).")
        nota.setObjectName("nota")
        nota.setWordWrap(True)
        lay.addWidget(nota)
        lay.addLayout(f)
        lay.addWidget(self.estado)
        lay.addWidget(bb)
        self.base.currentTextChanged.connect(self.actualizar)
        self.tinte.valueChanged.connect(self.actualizar)
        self.actualizar()

    def actualizar(self, *_):
        b = self.te.obtener(self.base.currentText())
        g = self.tinte.value()
        cols = [self.F.rotar_hex(b.pantalla or b.color["panel"], g)] + [self.F.rotar_hex(b.color[k], g) for k in ("acento", "acento2", "calido")]
        self.muestra.setText("".join(f'<span style="background:{c};">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>&nbsp;' for c in cols))

    def crear(self):
        id_ = self.id_.text().strip().lower()
        if not id_ or id_ in self.te.TEMAS and not self.te.TEMAS[id_].base:
            self.estado.setText("Escribe un id nuevo (los temas incluidos no se pueden reemplazar).")
            return
        extra = {"fuentes": {"titulo": self.titulo_f.text().strip()}} if self.titulo_f.text().strip() else {}
        try:
            self.ruta = self.te.crear_json(id_, self.base.currentText(), self.nombre.text().strip() or None, self.tinte.value(),
                                           self.desc.text().strip(), **extra)
        except Exception as e:  # id inválido, etc.
            self.estado.setText(str(e))
            return
        self.id_creado = id_
        self.accept()


class PresentacionesPanel(QWidget):
    def __init__(self):
        super().__init__()
        animaciones_en_path()
        try:
            import temas_espaciales as te
            self.te = te
        except Exception as e:  # falta numpy/scipy/Pillow
            lay = QVBoxLayout(self)
            lay.addWidget(QLabel(f"No se pudo cargar temas_espaciales.py: {e}\nInstala las dependencias de requirements.txt."))
            self.te = None
            return
        self.log = QPlainTextEdit(readOnly=True)
        self.ejecutor = Ejecutor(self, self.log, self._termino, self._ocupado)

        titulo = QLabel("PRESENTACIONES ESPACIALES")
        titulo.setObjectName("titulo")
        nota = QLabel("Misma secuencia, guion y videos; eliges presentación, idioma y tema. Las salidas quedan en exports/presentaciones/espaciales/.")
        nota.setObjectName("nota")

        self.lista_pres = QListWidget()
        for k, idioma, etiqueta in PRESENTACIONES:
            it = QListWidgetItem(etiqueta)
            it.setData(Qt.UserRole, (k, idioma))
            self.lista_pres.addItem(it)
        self.lista_pres.setCurrentRow(0)
        g1 = QGroupBox("PRESENTACIÓN")
        QVBoxLayout(g1).addWidget(self.lista_pres)

        self.lista_temas = QListWidget()
        self.lista_temas.setIconSize(QPixmap(96, 54).size())
        self.lista_temas.currentItemChanged.connect(self._ver_tema)
        self.lista_temas.itemChanged.connect(self._avisos)
        g2 = QGroupBox("TEMAS  (marca uno o varios)")
        QVBoxLayout(g2).addWidget(self.lista_temas)

        self.r_uno = QRadioButton("Un deck por cada tema marcado")
        self.r_mezcla = QRadioButton("Un solo deck mezclando los temas marcados")
        self.r_uno.setChecked(True)
        self.reparto = QComboBox()
        self.reparto.addItem("un tema por sección", "seccion")
        self.reparto.addItem("alternar en cada diapositiva", "diapositiva")
        self.reparto.setEnabled(False)
        self.r_mezcla.toggled.connect(self.reparto.setEnabled)
        self.r_mezcla.toggled.connect(self._avisos)
        self.descripcion = QLabel("")
        self.descripcion.setWordWrap(True)
        self.descripcion.setObjectName("nota")
        self.vista = QLabel("Sin vista previa")
        self.vista.setAlignment(Qt.AlignCenter)
        self.vista.setMinimumSize(300, 170)
        self.vista.setStyleSheet("border: 1px solid #1f2c5c; border-radius: 8px;")
        self.aviso = QLabel("")
        self.aviso.setObjectName("aviso")
        self.aviso.setWordWrap(True)
        g3 = QGroupBox("DISEÑO")
        l3 = QVBoxLayout(g3)
        for w in (self.r_uno, self.r_mezcla, self.reparto, self.vista, self.descripcion, self.aviso):
            l3.addWidget(w)
        l3.addStretch(1)

        arriba = QHBoxLayout()
        arriba.addWidget(g1, 3)
        arriba.addWidget(g2, 4)
        arriba.addWidget(g3, 4)

        self.b_construir = QPushButton("Construir")
        self.b_construir.setObjectName("primario")
        self.b_construir.clicked.connect(lambda: self.construir(False))
        self.b_videos = QPushButton("Solo preparar videos")
        self.b_videos.clicked.connect(lambda: self.construir(True))
        self.b_parar = QPushButton("Detener")
        self.b_parar.setEnabled(False)
        self.b_parar.clicked.connect(self.ejecutor.detener)
        self.b_prev = QPushButton("Generar vista previa")
        self.b_prev.clicked.connect(self.generar_vista)
        self.b_nuevo = QPushButton("Nuevo tema…")
        self.b_nuevo.clicked.connect(self.nuevo_tema)
        self.b_abrir = QPushButton("Abrir carpeta")
        self.b_abrir.clicked.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(str(CARPETA_SALIDA))))
        barra = QHBoxLayout()
        for b in (self.b_construir, self.b_videos, self.b_parar, self.b_prev, self.b_nuevo, self.b_abrir):
            barra.addWidget(b)

        lay = QVBoxLayout(self)
        lay.addWidget(titulo)
        lay.addWidget(nota)
        lay.addLayout(arriba, 3)
        lay.addLayout(barra)
        lay.addWidget(self.log, 2)
        self.recargar_temas()

    # ---- temas
    def recargar_temas(self, seleccionar=None):
        marcados = {self.lista_temas.item(i).data(Qt.UserRole) for i in range(self.lista_temas.count())
                    if self.lista_temas.item(i).checkState() == Qt.Checked}
        self.lista_temas.blockSignals(True)
        self.lista_temas.clear()
        for t in self.te.TEMAS.values():
            it = QListWidgetItem(_miniatura(t), f"{t.nombre}\n{t.video} · {'deriva de ' + t.base if t.base else t.id}")
            it.setData(Qt.UserRole, t.id)
            it.setFlags(it.flags() | Qt.ItemIsUserCheckable)
            it.setCheckState(Qt.Checked if (t.id in marcados or (not marcados and t.id == "orbita")) else Qt.Unchecked)
            self.lista_temas.addItem(it)
            if t.id == seleccionar:
                self.lista_temas.setCurrentItem(it)
        self.lista_temas.blockSignals(False)
        if self.lista_temas.currentRow() < 0:
            self.lista_temas.setCurrentRow(0)
        self._avisos()

    def temas_marcados(self):
        return [self.lista_temas.item(i).data(Qt.UserRole) for i in range(self.lista_temas.count())
                if self.lista_temas.item(i).checkState() == Qt.Checked]

    def _tema_actual(self):
        it = self.lista_temas.currentItem()
        return self.te.obtener(it.data(Qt.UserRole)) if it else None

    def _ver_tema(self, *_):
        t = self._tema_actual()
        if not t:
            return
        jpg = PREVIEWS / f"{t.id}_portada_0.jpg"
        if jpg.exists():
            self.vista.setPixmap(QPixmap(str(jpg)).scaled(300, 170, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.vista.setPixmap(QPixmap())
            self.vista.setText("Sin vista previa\n(botón «Generar vista previa»)")
        f = t.fuentes
        self.descripcion.setText(f"{t.descripcion}\nFuentes: {f['titulo']} · {f['cuerpo']} · {f['etiqueta']}")

    def _avisos(self, *_):
        marc = self.temas_marcados()
        faltan = tema.fuentes_faltantes(x for i in marc for x in self.te.obtener(i).fuentes.values())
        msgs = []
        if faltan:
            msgs.append("Faltan fuentes en este equipo: " + ", ".join(faltan) + " (ver espaciales/fuentes/LEEME.md).")
        if self.r_mezcla.isChecked():
            if len(marc) < 2:
                msgs.append("Para mezclar marca al menos dos temas.")
            elif any(self.te.obtener(i).modo == "claro" for i in marc) and any(self.te.obtener(i).modo == "oscuro" for i in marc):
                msgs.append("Mezclas temas claros y oscuros: el cambio se nota en cada sección.")
        self.aviso.setText("\n".join(msgs))

    # ---- acciones
    def _ocupado(self, si):
        for b in (self.b_construir, self.b_videos, self.b_prev, self.b_nuevo):
            b.setEnabled(not si)
        self.b_parar.setEnabled(si)

    def _termino(self, codigo):
        self.recargar_temas(self._tema_actual().id if self._tema_actual() else None)

    def construir(self, solo_videos):
        k, idioma = self.lista_pres.currentItem().data(Qt.UserRole)
        marc = self.temas_marcados()
        if not marc:
            QMessageBox.information(self, "Temas", "Marca al menos un tema.")
            return
        args = ["decks_espaciales.py", k]
        if idioma == "en":
            args.append("--en")
        if self.r_mezcla.isChecked():
            if len(marc) < 2:
                QMessageBox.information(self, "Mezcla", "Para mezclar marca al menos dos temas.")
                return
            args += ["--mezcla", ",".join(marc), "--mezcla-por", self.reparto.currentData()]
        else:
            args += marc
        if solo_videos:
            args.append("--solo-videos")
        if idioma == "en" and not (EXPORTS / "tesis_sem_2_examen" / "oscuro_en").exists():
            self.log.appendPlainText("Aviso: faltan los videos en inglés (IDIOMA=en ./render_todo.sh ambos …); el deck saldrá incompleto.")
        self.ejecutor.correr(python(), args)

    def generar_vista(self):
        t = self._tema_actual()
        if t:
            self.ejecutor.correr(python(), ["temas_espaciales.py", "--vista-previa", t.id])

    def nuevo_tema(self):
        d = NuevoTemaDialog(self, self.te)
        if d.exec() == QDialog.Accepted:
            self.log.appendPlainText(f"Tema creado: {d.ruta}")
            self.recargar_temas(d.id_creado)
