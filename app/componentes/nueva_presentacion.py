"""Panel «Nueva presentación»: crea y edita presentaciones propias con las piezas Manim ya renderizadas.

Cada presentación es un JSON en animaciones/presentaciones/<id>.json (formato y reglas en presentaciones_usuario.py):
  · datos de la portada y el cierre (título, lema, autor, institución…), idioma y ritmo del guion;
  · lista de diapositivas (portada, sección, texto + sticker, video, cita, cierre, respaldo) que se añaden,
    reordenan, duplican y quitan;
  · editor de la diapositiva elegida: textos, pieza de video o sticker (buscador sobre el catálogo), guion y advertencia;
  · validación en vivo (lo que impide construir y los avisos de diseño) y tiempo estimado del guion;
  · construir en el tema elegido con decks_espaciales.py (también escribe exports/GUION_<ID>.md).
"""
import copy
import json
import subprocess

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QCompleter, QFormLayout, QGroupBox, QHBoxLayout, QInputDialog, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QMenu, QMessageBox, QPlainTextEdit, QPushButton, QSpinBox, QVBoxLayout, QWidget,
)

from .base import EXPORTS, Ejecutor, animaciones_en_path, python

SALIDA = EXPORTS / "presentaciones" / "espaciales"
SIN = "(sin sticker)"


class Buscador(QComboBox):
    """Combo editable con búsqueda por contenido sobre las piezas del catálogo; `clase()` devuelve la elegida o None."""

    def __init__(self, piezas, permitir_vacio=False):
        super().__init__()
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)
        if permitir_vacio:
            self.addItem(SIN, None)
        for p in piezas:
            self.addItem(f"{p['clase']}  —  {p['muestra']}", p["clase"])
        c = self.completer()
        c.setFilterMode(Qt.MatchContains)
        c.setCompletionMode(QCompleter.PopupCompletion)
        c.setCaseSensitivity(Qt.CaseInsensitive)

    def clase(self):
        i = self.findText(self.currentText())
        return self.itemData(i) if i >= 0 else None

    def poner(self, clase):
        i = self.findData(clase)
        self.setCurrentIndex(i if i >= 0 else (0 if self.itemData(0) is None else -1))
        self.lineEdit().setCursorPosition(0)  # que se vea el nombre de la pieza, no el final de la descripción


class NuevaPresentacionPanel(QWidget):
    def __init__(self):
        super().__init__()
        animaciones_en_path()
        try:
            import presentaciones_usuario as pu
            import temas_espaciales as te
        except Exception as e:
            QVBoxLayout(self).addWidget(QLabel(f"No se pudo cargar presentaciones_usuario.py: {e}"))
            self.pu = None
            return
        self.pu, self.te = pu, te
        self.piezas = [p for p in pu.piezas() if p["oscuro"]]
        self.por_clase = {p["clase"]: p for p in self.piezas}
        self.d = None            # presentación en edición (dict completo)
        self.sucio = False
        self._cargando = False
        self.log = QPlainTextEdit(readOnly=True)
        self.log.setMaximumHeight(130)
        self.ejecutor = Ejecutor(self, self.log, self._termino, self._ocupado)

        titulo = QLabel("NUEVA PRESENTACIÓN")
        titulo.setObjectName("titulo")
        nota = QLabel("Arma una presentación con las piezas ya renderizadas, escribe su guion y constrúyela en cualquier tema. "
                      "Se guarda en animaciones/presentaciones/<id>.json y aparece también en la pestaña Presentaciones.")
        nota.setObjectName("nota")
        nota.setWordWrap(True)

        # ---- barra superior: elegir / crear / duplicar / guardar
        self.sel = QComboBox()
        self.sel.setMinimumWidth(320)
        self.sel.activated.connect(self._elegir)
        self.b_nueva = QPushButton("Nueva…")
        self.b_nueva.clicked.connect(self.nueva)
        self.b_duplicar = QPushButton("Duplicar…")
        self.b_duplicar.clicked.connect(self.duplicar)
        self.b_guardar = QPushButton("Guardar")
        self.b_guardar.clicked.connect(self.guardar)
        self.estado_arch = QLabel("")
        self.estado_arch.setObjectName("nota")
        arriba = QHBoxLayout()
        arriba.addWidget(QLabel("Presentación"))
        arriba.addWidget(self.sel, 1)
        for b in (self.b_nueva, self.b_duplicar, self.b_guardar):
            arriba.addWidget(b)
        arriba.addWidget(self.estado_arch)

        # ---- columna 1: datos generales
        self.f_id = QLineEdit(readOnly=True)
        self.f_titulo, self.f_lema, self.f_kicker = QLineEdit(), QLineEdit(), QLineEdit()
        self.f_autor, self.f_instit, self.f_pie, self.f_cierre = QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()
        self.f_idioma = QComboBox()
        self.f_idioma.addItem("Español", "es")
        self.f_idioma.addItem("English", "en")
        self.f_ritmo = QSpinBox()
        self.f_ritmo.setRange(80, 220)
        self.f_ritmo.setSuffix(" palabras/min")
        self.f_marca = QCheckBox("Logotipo CO.DE en la portada")
        self.f_nota = QPlainTextEdit()
        self.f_nota.setObjectName("editor")
        self.f_nota.setPlaceholderText("Contexto que va al inicio del guion .md (fuentes, fecha, público…)")
        self.f_nota.setMaximumHeight(90)
        fd = QFormLayout()
        for etq, w in (("Id", self.f_id), ("Título", self.f_titulo), ("Lema", self.f_lema), ("Etiqueta", self.f_kicker),
                       ("Autor", self.f_autor), ("Institución", self.f_instit), ("Pie", self.f_pie),
                       ("Título del cierre", self.f_cierre), ("Idioma", self.f_idioma), ("Ritmo", self.f_ritmo)):
            fd.addRow(etq, w)
        fd.addRow("", self.f_marca)
        fd.addRow("Nota", self.f_nota)
        for w in (self.f_titulo, self.f_lema, self.f_kicker, self.f_autor, self.f_instit, self.f_pie, self.f_cierre):
            w.textEdited.connect(self._datos_cambiados)
        self.f_idioma.currentIndexChanged.connect(self._datos_cambiados)
        self.f_ritmo.valueChanged.connect(self._datos_cambiados)
        self.f_marca.toggled.connect(self._datos_cambiados)
        self.f_nota.textChanged.connect(self._datos_cambiados)
        g_datos = QGroupBox("DATOS")
        g_datos.setLayout(fd)

        # ---- columna 2: diapositivas
        self.lista = QListWidget()
        self.lista.setWordWrap(True)
        self.lista.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.lista.currentRowChanged.connect(self._ver_diapo)
        self.b_anadir = QPushButton("Añadir")
        menu = QMenu(self.b_anadir)
        for t in pu.TIPOS:
            menu.addAction(pu.ETIQUETA[t], lambda t=t: self.anadir(t))
        self.b_anadir.setMenu(menu)
        self.b_quitar = QPushButton("Quitar")
        self.b_quitar.clicked.connect(self.quitar)
        self.b_subir = QPushButton("▲")
        self.b_subir.clicked.connect(lambda: self.mover(-1))
        self.b_bajar = QPushButton("▼")
        self.b_bajar.clicked.connect(lambda: self.mover(1))
        self.b_dup = QPushButton("Duplicar")
        self.b_dup.clicked.connect(self.duplicar_diapo)
        botones = QHBoxLayout()
        for b in (self.b_anadir, self.b_dup, self.b_quitar, self.b_subir, self.b_bajar):
            botones.addWidget(b)
        self.tiempo = QLabel("")
        self.tiempo.setObjectName("ok")
        g_lista = QGroupBox("DIAPOSITIVAS")
        lg = QVBoxLayout(g_lista)
        lg.addWidget(self.lista, 1)
        lg.addLayout(botones)
        lg.addWidget(self.tiempo)

        # ---- columna 3: editor de la diapositiva
        self.e_tipo = QLabel("")
        self.e_tipo.setObjectName("seccion")
        self.e_titulo, self.e_sub = QLineEdit(), QLineEdit()
        self.e_frase = QPlainTextEdit()
        self.e_frase.setObjectName("editor")
        self.e_frase.setMaximumHeight(70)
        self.e_puntos = QPlainTextEdit()
        self.e_puntos.setObjectName("editor")
        self.e_puntos.setPlaceholderText("Un punto por línea (hasta 6)")
        self.e_puntos.setMaximumHeight(110)
        self.e_clase = Buscador(self.piezas)
        self.e_sticker = Buscador(self.piezas, permitir_vacio=True)
        self.e_guion = QPlainTextEdit()
        self.e_guion.setObjectName("editor")
        self.e_guion.setPlaceholderText("Lo que se dice en esta diapositiva (va a las notas del orador y al guion .md)")
        self.e_cuidado = QLineEdit()
        self.e_cuidado.setPlaceholderText("Opcional: lo que NO se puede afirmar aquí (⚠️)")
        self.vista = QLabel("")
        self.vista.setAlignment(Qt.AlignCenter)
        self.vista.setMinimumHeight(150)
        self.vista.setStyleSheet("border: 1px solid #1f2c5c; border-radius: 8px;")
        self.vista_nota = QLabel("")
        self.vista_nota.setObjectName("nota")
        self.vista_nota.setWordWrap(True)
        self.palabras = QLabel("")
        self.palabras.setObjectName("nota")
        self.fe = QFormLayout()
        self.filas = {}
        for clave, etq, w in (("titulo", "Título", self.e_titulo), ("frase", "Frase", self.e_frase), ("sub", "Subtítulo", self.e_sub),
                              ("puntos", "Puntos", self.e_puntos), ("clase", "Pieza", self.e_clase),
                              ("sticker", "Sticker", self.e_sticker), ("guion", "Guion", self.e_guion), ("cuidado", "Cuidado", self.e_cuidado)):
            self.fe.addRow(etq, w)
            self.filas[clave] = w
        self.e_titulo.textEdited.connect(self._diapo_cambiada)
        self.e_sub.textEdited.connect(self._diapo_cambiada)
        self.e_cuidado.textEdited.connect(self._diapo_cambiada)
        for w in (self.e_frase, self.e_puntos, self.e_guion):
            w.textChanged.connect(self._diapo_cambiada)
        for w in (self.e_clase, self.e_sticker):
            w.currentIndexChanged.connect(self._diapo_cambiada)
        g_ed = QGroupBox("DIAPOSITIVA")
        le = QVBoxLayout(g_ed)
        le.addWidget(self.e_tipo)
        le.addLayout(self.fe)
        le.addWidget(self.vista)
        le.addWidget(self.vista_nota)
        le.addWidget(self.palabras)

        medio = QHBoxLayout()
        g_datos.setMinimumWidth(420)
        medio.addWidget(g_datos, 4)
        medio.addWidget(g_lista, 3)
        medio.addWidget(g_ed, 5)

        # ---- validación y construcción
        self.validacion = QLabel("")
        self.validacion.setWordWrap(True)
        self.validacion.setTextFormat(Qt.RichText)
        self.tema = QComboBox()
        for t in te.TEMAS.values():
            self.tema.addItem(f"{t.nombre}  ·  {t.video}", t.id)
        self.tema.setCurrentIndex(max(0, self.tema.findData(te.TEMA_OFICIAL)))
        self.b_construir = QPushButton("Guardar y construir")
        self.b_construir.setObjectName("primario")
        self.b_construir.clicked.connect(self.construir)
        self.b_parar = QPushButton("Detener")
        self.b_parar.setEnabled(False)
        self.b_parar.clicked.connect(self.ejecutor.detener)
        self.b_guion = QPushButton("Escribir guion .md")
        self.b_guion.clicked.connect(self.escribir_guion)
        self.b_abrir = QPushButton("Abrir carpeta")
        self.b_abrir.clicked.connect(self.abrir_carpeta)
        abajo = QHBoxLayout()
        abajo.addWidget(QLabel("Tema"))
        abajo.addWidget(self.tema, 1)
        for b in (self.b_construir, self.b_parar, self.b_guion, self.b_abrir):
            abajo.addWidget(b)

        lay = QVBoxLayout(self)
        lay.addWidget(titulo)
        lay.addWidget(nota)
        lay.addLayout(arriba)
        lay.addLayout(medio, 1)
        lay.addWidget(self.validacion)
        lay.addLayout(abajo)
        lay.addWidget(self.log)
        self.recargar()

    # ================================================================ archivos
    def recargar(self, elegir=None):
        self.sel.blockSignals(True)
        self.sel.clear()
        for id_, tit, idioma in self.pu.listar():
            self.sel.addItem(f"{tit}   [{id_} · {idioma}]", id_)
        self.sel.blockSignals(False)
        if self.sel.count() == 0:
            self.abrir(self.pu.nueva("mi_presentacion"), nueva=True)
            return
        i = self.sel.findData(elegir) if elegir else 0
        self.sel.setCurrentIndex(max(i, 0))
        self.abrir(self.pu.cargar(self.sel.currentData()))

    def _elegir(self, *_):
        id_ = self.sel.currentData()
        if self.d and id_ == self.d["id"]:
            return
        if not self._confirmar_descartar():
            self.sel.setCurrentIndex(max(0, self.sel.findData(self.d["id"])))
            return
        self.abrir(self.pu.cargar(id_))

    def _confirmar_descartar(self):
        if not self.sucio:
            return True
        r = QMessageBox.question(self, "Cambios sin guardar", f"«{self.d['titulo']}» tiene cambios sin guardar. ¿Guardarlos?",
                                 QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        if r == QMessageBox.Save:
            return self.guardar()
        return r == QMessageBox.Discard

    def abrir(self, d, nueva=False):
        self.d = self.pu.completar(d)
        self._cargando = True
        self.f_id.setText(self.d["id"])
        for w, k in ((self.f_titulo, "titulo"), (self.f_lema, "lema"), (self.f_kicker, "kicker"), (self.f_autor, "autor"),
                     (self.f_instit, "instit"), (self.f_pie, "pie"), (self.f_cierre, "cierre_titulo")):
            w.setText(str(self.d.get(k, "")))
            w.setCursorPosition(0)
        self.f_idioma.setCurrentIndex(max(0, self.f_idioma.findData(self.d["idioma"])))
        self.f_ritmo.setValue(int(self.d["ritmo"]))
        self.f_marca.setChecked(bool(self.d["marca"]))
        self.f_nota.setPlainText(self.d.get("nota", ""))
        self._cargando = False
        self._pintar_lista(0)
        self._marcar(nueva)

    def _marcar(self, sucio):
        self.sucio = sucio
        self.estado_arch.setText("● sin guardar" if sucio else "guardado")
        self.estado_arch.setObjectName("aviso" if sucio else "nota")
        self.estado_arch.style().unpolish(self.estado_arch)  # reaplica el estilo del nuevo objectName
        self.estado_arch.style().polish(self.estado_arch)
        self._validar()

    def guardar(self):
        if not self.d:
            return False
        try:
            p = self.pu.guardar(self.d)
        except Exception as e:
            QMessageBox.warning(self, "No se pudo guardar", str(e))
            return False
        self.log.appendPlainText(f"Guardado: {p}")
        actual = self.d["id"]
        self.sel.blockSignals(True)
        self.sel.clear()
        for id_, tit, idioma in self.pu.listar():
            self.sel.addItem(f"{tit}   [{id_} · {idioma}]", id_)
        self.sel.setCurrentIndex(max(0, self.sel.findData(actual)))
        self.sel.blockSignals(False)
        self._marcar(False)
        return True

    def _pedir_id(self, titulo, sugerido):
        id_, ok = QInputDialog.getText(self, titulo, "Id (minúsculas, dígitos y «_»):", text=sugerido)
        id_ = (id_ or "").strip().lower()
        if not ok or not id_:
            return None
        if not self.pu.ID_OK.match(id_):
            QMessageBox.warning(self, titulo, "Id inválido: 2–41 caracteres, minúsculas, dígitos y «_».")
            return None
        if self.pu.ruta(id_).exists():
            QMessageBox.warning(self, titulo, f"Ya existe una presentación «{id_}».")
            return None
        return id_

    def nueva(self, id_=None):
        if not self._confirmar_descartar():
            return
        id_ = id_ or self._pedir_id("Nueva presentación", "mi_presentacion")
        if id_:
            self.abrir(self.pu.nueva(id_), nueva=True)

    def duplicar(self, id_=None):
        if not self.d or not self._confirmar_descartar():
            return
        id_ = id_ or self._pedir_id("Duplicar presentación", self.d["id"] + "_copia")
        if id_:
            d = copy.deepcopy(self.d)
            d["id"] = id_
            d["titulo"] = d["titulo"] + " (copia)"
            self.abrir(d, nueva=True)

    # ================================================================ datos generales
    def _datos_cambiados(self, *_):
        if self._cargando or not self.d:
            return
        for w, k in ((self.f_titulo, "titulo"), (self.f_lema, "lema"), (self.f_kicker, "kicker"), (self.f_autor, "autor"),
                     (self.f_instit, "instit"), (self.f_pie, "pie"), (self.f_cierre, "cierre_titulo")):
            self.d[k] = w.text()
        self.d["idioma"] = self.f_idioma.currentData()
        self.d["ritmo"] = self.f_ritmo.value()
        self.d["marca"] = self.f_marca.isChecked()
        self.d["nota"] = self.f_nota.toPlainText()
        self._marcar(True)

    # ================================================================ lista de diapositivas
    def _texto_item(self, n, x):
        t = x.get("tipo")
        nombre = self.pu.titulo_de(x, self.d) if t in self.pu.TIPOS else t
        extra = f"   ▸ {x['clase']}" if t == "video" and x.get("clase") else ""
        vacio = "" if str(x.get("guion", "")).strip() else "   · sin guion"
        return f"{n:02d}  {self.pu.ETIQUETA.get(t, t).upper()}\n      {nombre}{extra}{vacio}"

    def _pintar_lista(self, fila=None):
        fila = self.lista.currentRow() if fila is None else fila
        self.lista.blockSignals(True)
        self.lista.clear()
        for n, x in enumerate(self.d["diapos"], 1):
            self.lista.addItem(QListWidgetItem(self._texto_item(n, x)))
        self.lista.blockSignals(False)
        if self.d["diapos"]:
            self.lista.setCurrentRow(min(max(fila, 0), len(self.d["diapos"]) - 1))
        self._ver_diapo(self.lista.currentRow())

    def _actual(self):
        i = self.lista.currentRow()
        return (i, self.d["diapos"][i]) if self.d and 0 <= i < len(self.d["diapos"]) else (None, None)

    def anadir(self, tipo):
        i, _ = self._actual()
        x = self.pu.completar({"diapos": [{"tipo": tipo}]})["diapos"][0]
        if tipo in ("texto", "respaldo"):
            x["puntos"] = []
        donde = len(self.d["diapos"]) if i is None else i + 1
        if tipo == "respaldo":
            donde = len(self.d["diapos"])
        self.d["diapos"].insert(donde, x)
        self._pintar_lista(donde)
        self._marcar(True)

    def quitar(self):
        i, x = self._actual()
        if i is None:
            return
        del self.d["diapos"][i]
        self._pintar_lista(i)
        self._marcar(True)

    def mover(self, paso):
        i, x = self._actual()
        j = (i if i is not None else -1) + paso
        if i is None or not 0 <= j < len(self.d["diapos"]):
            return
        ds = self.d["diapos"]
        ds[i], ds[j] = ds[j], ds[i]
        self._pintar_lista(j)
        self._marcar(True)

    def duplicar_diapo(self):
        i, x = self._actual()
        if i is None:
            return
        self.d["diapos"].insert(i + 1, copy.deepcopy(x))
        self._pintar_lista(i + 1)
        self._marcar(True)

    # ================================================================ editor de una diapositiva
    def _ver_diapo(self, i):
        _, x = self._actual()
        self._cargando = True
        visibles = set()
        if x:
            t = x["tipo"]
            obl, opc = self.pu.CAMPOS.get(t, ((), ()))
            visibles = set(obl) | set(opc) | {"guion", "cuidado"}
            self.e_tipo.setText(f"{self.pu.ETIQUETA.get(t, t).upper()}   ·   {', '.join(obl) or 'solo guion'} obligatorio")
            self.e_titulo.setText(x.get("titulo", ""))
            self.e_sub.setText(x.get("sub", ""))
            self.e_titulo.setCursorPosition(0)
            self.e_sub.setCursorPosition(0)
            self.e_frase.setPlainText(x.get("frase", ""))
            self.e_puntos.setPlainText("\n".join(x.get("puntos", []) or []))
            self.e_clase.poner(x.get("clase"))
            self.e_sticker.poner(x.get("sticker"))
            self.e_guion.setPlainText(x.get("guion", ""))
            self.e_cuidado.setText(x.get("cuidado", ""))
        else:
            self.e_tipo.setText("")
        for clave, w in self.filas.items():
            self.fe.setRowVisible(w, clave in visibles)
        self._cargando = False
        self._vista_previa()

    def _diapo_cambiada(self, *_):
        if self._cargando:
            return
        i, x = self._actual()
        if x is None:
            return
        t = x["tipo"]
        obl, opc = self.pu.CAMPOS.get(t, ((), ()))
        campos = set(obl) | set(opc)
        if "titulo" in campos:
            x["titulo"] = self.e_titulo.text()
        if "sub" in campos:
            x["sub"] = self.e_sub.text()
        if "frase" in campos:
            x["frase"] = self.e_frase.toPlainText().strip()
        if "puntos" in campos:
            x["puntos"] = [l.strip() for l in self.e_puntos.toPlainText().split("\n") if l.strip()]
        if "clase" in campos:
            x["clase"] = self.e_clase.clase()
        if "sticker" in campos:
            x["sticker"] = self.e_sticker.clase()
        x["guion"] = self.e_guion.toPlainText()
        x["cuidado"] = self.e_cuidado.text()
        it = self.lista.item(i)
        if it:
            it.setText(self._texto_item(i + 1, x))
        self._vista_previa()
        self._marcar(True)

    def _vista_previa(self):
        """Muestra el sticker (último cuadro) de la pieza elegida, si ya se generó, y su descripción del catálogo."""
        _, x = self._actual()
        clase = x and (x.get("clase") if x["tipo"] == "video" else x.get("sticker"))
        self.vista.setPixmap(QPixmap())
        self.vista.setText("")
        self.vista_nota.setText("")
        if x:
            n = len(str(x.get("guion", "")).split())
            ritmo = float(self.d.get("ritmo") or 140)
            self.palabras.setText(f"{n} palabras · {n / ritmo * 60:.0f} s de guion" + ("  (respaldo: fuera del tiempo)" if x["tipo"] == "respaldo" else ""))
        else:
            self.palabras.setText("")
        if not clase or clase not in self.por_clase:
            self.vista.setText("Sin pieza" if x and x["tipo"] in ("video", "texto", "respaldo", "cita") else "")
            return
        p = self.por_clase[clase]
        jpg = self.miniatura(p)
        if jpg:
            self.vista.setPixmap(QPixmap(str(jpg)).scaled(320, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.vista.setText(f"{clase}\n(sin miniatura: no encuentro su video)")
        self.vista_nota.setText(f"{p['bloque']} · {p['muestra']}" + (f"\nCuándo usarla: {p['cuando']}" if p.get("cuando") else ""))

    @staticmethod
    def miniatura(p):
        """JPG con un cuadro casi final del video oscuro de la pieza (en caché en exports/png/miniaturas/)."""
        dst = EXPORTS / "png" / "miniaturas" / f"{p['clase']}.jpg"
        fin = EXPORTS / p["carpeta"] / "oscuro_final" / f"{p['clase']}.mp4"
        src = fin if fin.exists() else EXPORTS / p["carpeta"] / "oscuro" / f"{p['clase']}.mp4"
        if dst.exists() and src.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
            return dst
        if not src.exists():
            return None
        try:
            dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(src)],
                                       capture_output=True, text=True, timeout=20).stdout.strip())
            t = dur - 0.15 if src == fin else dur * 0.8  # el original termina en fundido: se toma antes
            dst.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{max(t, 0):.2f}", "-i", str(src), "-frames:v", "1",
                            "-vf", "scale=480:-2", "-q:v", "4", str(dst)], timeout=30, check=True)
            return dst if dst.exists() else None
        except Exception:
            return None

    # ================================================================ validación y construcción
    def _validar(self):
        if not self.d:
            return [], []
        err, av = self.pu.validar(self.d)
        mins = self.pu.minutos_total(self.d) if not any("ritmo" in e for e in err) else 0
        n = len(self.d["diapos"])
        self.tiempo.setText(f"{n} diapositivas · {mins:.1f} min de guion")
        partes = []
        if err:
            partes.append('<span style="color:#ff6b8b"><b>Impide construir:</b> ' + " · ".join(err[:6]) +
                          (f" · (+{len(err) - 6})" if len(err) > 6 else "") + "</span>")
        if av:
            partes.append('<span style="color:#F59E0B"><b>Avisos:</b> ' + " · ".join(av[:5]) +
                          (f" · (+{len(av) - 5})" if len(av) > 5 else "") + "</span>")
        if not partes:
            partes.append('<span style="color:#37CFA0">Lista para construir: sin errores ni avisos.</span>')
        self.validacion.setText("<br>".join(partes))
        self.b_construir.setEnabled(not err and not self.ejecutor.ocupado)
        return err, av

    def construir(self):
        err, _ = self._validar()
        if err or not self.guardar():
            return
        self.ejecutor.correr(python(), ["decks_espaciales.py", self.tema.currentData(), self.d["id"]])

    def escribir_guion(self):
        if not self.d:
            return
        p = self.pu.ruta_guion(self.d)
        p.write_text(self.pu.guion_md(self.d), encoding="utf-8")
        self.log.appendPlainText(f"Guion escrito: {p}")

    def abrir_carpeta(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(SALIDA / self.tema.currentData())))

    def _ocupado(self, si):
        for b in (self.b_nueva, self.b_duplicar, self.b_guardar, self.b_guion):
            b.setEnabled(not si)
        self.b_construir.setEnabled(not si)
        self.b_parar.setEnabled(si)
        if not si:
            self._validar()

    def _termino(self, codigo):
        if codigo == 0 and self.d:
            pptx = SALIDA / self.tema.currentData() / f"{self.d['id']}_{self.tema.currentData()}.pptx"
            self.log.appendPlainText(f"Listo: {pptx}" if pptx.exists() else "Terminó, pero no encuentro el .pptx: revisa el registro.")
        self._vista_previa()

    def exportar_json(self):
        """Texto JSON de la presentación en edición (para pruebas y para copiar)."""
        return json.dumps(self.d, ensure_ascii=False, indent=2)
