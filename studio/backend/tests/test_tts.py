"""Voz sin GCP (R1): catalogo de proveedores, guion escrito a mano, narracion
con un proveedor que no escribe guiones, y grabacion propia subida."""

import io
import os
import time
import wave

from tests.test_narracion import (VALID_SCRIPT, FakeVertex, _add_clip,
                                  _create_project, _wait_run)


class FakeEdge:
    """Proveedor que solo habla: sin `guion` util (como edge-tts/Piper)."""
    id = "edge"
    model_tts = "edge-de-prueba"

    def __init__(self):
        self.textos = []

    def guion(self, system, user):
        raise RuntimeError("no escribo guiones")

    def tts(self, texto, voz):
        self.textos.append((texto, voz))
        return b"\xe8\x03" * 12_000  # 0.5 s de tono


def _wav_bytes(segundos=2.0, rate=48_000, canales=2, amplitud=8000):
    """Un WAV estereo a 48 kHz con un tono: lo que sale de una grabadora."""
    import math
    buf = io.BytesIO()
    n = int(segundos * rate)
    with wave.open(buf, "wb") as w:
        w.setnchannels(canales)
        w.setsampwidth(2)
        w.setframerate(rate)
        frames = bytearray()
        for i in range(n):
            v = int(amplitud * math.sin(2 * math.pi * 220 * i / rate))
            for _ in range(canales):
                frames += v.to_bytes(2, "little", signed=True)
        w.writeframes(bytes(frames))
    return buf.getvalue()


def test_catalogo_de_proveedores(authed, tmp_path, monkeypatch):
    r = authed.get("/api/narracion/proveedores")
    assert r.status_code == 200
    d = r.json()
    ids = [p["id"] for p in d["proveedores"]]
    assert ids == ["vertex", "edge", "piper", "archivo"]
    por_id = {p["id"]: p for p in d["proveedores"]}
    # En tests el catalogo esta acotado a vertex,archivo y no hay key
    assert por_id["vertex"]["disponible"] is False
    assert "service account" in por_id["vertex"]["motivo"]
    assert por_id["edge"]["disponible"] is False
    assert por_id["archivo"]["disponible"] is True
    assert d["proveedor"] is None
    # 45 voces en espanol de edge, con Jorge por defecto
    assert len(por_id["edge"]["voces"]) >= 40
    assert por_id["edge"]["voz_defecto"] == "es-MX-JorgeNeural"


def test_guion_a_mano_y_narracion_con_proveedor_que_no_escribe(
        authed, tmp_path, monkeypatch):
    project = _create_project(authed)
    pid = project["id"]
    clip = _add_clip(authed, pid)

    # Sin guion y sin nadie que lo escriba: se dice que clips lo necesitan
    monkeypatch.setenv("MS_TTS_PROVEEDORES", "edge,archivo")
    import app.main as main_mod
    svc = main_mod.narracion_service
    svc.cfg.tts_proveedores = ("edge", "archivo")
    svc.cfg.tts_provider = "edge"
    fake = FakeEdge()
    monkeypatch.setattr(svc, "_narrador", lambda proveedor: fake)
    # edge "disponible" aunque el venv de CI no lo tenga: se fuerza el catalogo
    from app import tts as tts_mod
    monkeypatch.setattr(tts_mod, "_instalado", lambda m: True)

    d = authed.get(f"/api/projects/{pid}/narracion").json()
    assert d["enabled"] is True
    assert d["proveedor"] == "edge"
    assert d["escribe_guion"] is False

    r = authed.post(f"/api/projects/{pid}/narracion", json={})
    assert r.status_code == 409
    assert "sin guion" in r.json()["detail"]

    # Guion invalido -> 422 con motivo
    r = authed.put(f"/api/projects/{pid}/narracion/{clip['id']}/guion",
                   json={"secciones": [{"t_inicio": 3, "texto": "b"},
                                       {"t_inicio": 1, "texto": "a"}]})
    assert r.status_code == 422
    assert "retrocede" in r.json()["detail"]

    # Guion valido -> estado "guion" (texto sin audio)
    secciones = [{"t_inicio": 0, "t_fin": 4, "momento": "intro",
                  "texto": "La orbita geoestacionaria."},
                 {"t_inicio": 4.5, "t_fin": 9, "momento": "cifra",
                  "texto": "Treinta y cinco mil kilometros."}]
    r = authed.put(f"/api/projects/{pid}/narracion/{clip['id']}/guion",
                   json={"secciones": secciones})
    assert r.status_code == 200, r.text
    assert r.json()["palabras"] == 8
    d = authed.get(f"/api/projects/{pid}/narracion").json()
    assert d["clips"][0]["estado"] == "guion"
    assert d["clips"][0]["has_guion"] is True
    r = authed.get(f"/api/projects/{pid}/narracion/{clip['id']}/guion")
    assert r.json()["existe"] is True
    assert [s["texto"] for s in r.json()["secciones"]] == [
        s["texto"] for s in secciones]

    # Narrar con edge y una voz suya: sintetiza seccion a seccion
    r = authed.post(f"/api/projects/{pid}/narracion",
                    json={"proveedor": "edge", "voz": "es-MX-DaliaNeural"})
    assert r.status_code == 202, r.text
    assert r.json()["voz"] == "es-MX-DaliaNeural"
    d = _wait_run(authed, pid)
    assert d["run"]["errores"] == []
    c = d["clips"][0]
    assert c["estado"] == "al_dia"
    assert c["voz"] == "es-MX-DaliaNeural"
    assert c["proveedor"] == "edge"
    assert c["origen"] == "tts"
    assert [t for t, _ in fake.textos] == [s["texto"] for s in secciones]
    assert all(v == "es-MX-DaliaNeural" for _, v in fake.textos)
    # Alineada EXACTA (guion a mano, sin el tope de 2.5 s de hueco que
    # aplica a los tiempos estimados por Gemini): la segunda seccion cae en
    # t=4.5 y dura 0.5 -> 5.0 s
    assert 4.9 <= c["audio_s"] <= 5.1

    # Una voz que no es del proveedor se rechaza antes de arrancar
    r = authed.post(f"/api/projects/{pid}/narracion",
                    json={"proveedor": "edge", "voz": "Charon", "force": True})
    assert r.status_code == 409
    assert "no es de edge" in r.json()["detail"]

    # Cambiar el proveedor por defecto NO deja la narracion desactualizada
    svc.cfg.tts_provider = "vertex"
    d = authed.get(f"/api/projects/{pid}/narracion").json()
    assert d["clips"][0]["estado"] == "al_dia"


def test_vertex_sigue_escribiendo_el_guion_para_otra_voz(authed, tmp_path,
                                                          monkeypatch):
    """Con la key de Vertex y un proveedor gratis: Gemini escribe, edge habla."""
    (tmp_path / "gcp-key.json").write_text('{"project_id": "test"}')
    import app.main as main_mod
    svc = main_mod.narracion_service
    svc.cfg.tts_proveedores = ("vertex", "edge", "archivo")
    from app import tts as tts_mod
    monkeypatch.setattr(tts_mod, "_instalado", lambda m: True)
    vertex, edge = FakeVertex(), FakeEdge()
    monkeypatch.setattr(svc, "_vertex", lambda: vertex)
    monkeypatch.setattr(svc, "_narrador",
                        lambda p: vertex if p == "vertex" else edge)

    project = _create_project(authed)
    pid = project["id"]
    _add_clip(authed, pid)
    r = authed.post(f"/api/projects/{pid}/narracion", json={"proveedor": "edge"})
    assert r.status_code == 202, r.text
    d = _wait_run(authed, pid)
    assert d["run"]["errores"] == []
    assert vertex.llamadas_guion == 1
    assert edge.textos and edge.textos[0][1] == "es-MX-JorgeNeural"
    assert d["clips"][0]["proveedor"] == "edge"


def test_subir_grabacion_propia(authed, tmp_path, monkeypatch):
    project = _create_project(authed)
    pid = project["id"]
    clip = _add_clip(authed, pid)
    url = f"/api/projects/{pid}/narracion/{clip['id']}/audio"

    # Formato no admitido / vacio
    r = authed.put(url + "?nombre=voz.txt", content=b"x" * 2000)
    assert r.status_code == 415
    r = authed.put(url + "?nombre=voz.wav", content=b"")
    assert r.status_code == 422

    # Un WAV estereo a 48 kHz de 2 s: se decodifica a mono 24 kHz
    r = authed.put(url + "?nombre=toma%201.wav", content=_wav_bytes(2.0))
    assert r.status_code == 200, r.text
    assert 1.8 <= r.json()["audio_s"] <= 2.3
    d = authed.get(f"/api/projects/{pid}/narracion").json()
    c = d["clips"][0]
    assert c["estado"] == "al_dia"
    assert c["origen"] == "subido"
    assert c["proveedor"] == "archivo"
    assert c["voz"] == "propia"
    assert c["has_audio"] is True

    # El WAV canonico es mono 24 kHz: lo que sfx.lee_wav y la pelicula esperan
    r = authed.get(url)
    assert r.status_code == 200
    with wave.open(io.BytesIO(r.content)) as w:
        assert w.getnchannels() == 1
        assert w.getframerate() == 24_000
        assert w.getsampwidth() == 2

    # Cambiar el script deja la grabacion desactualizada (el video cambio)
    r = authed.patch(f"/api/projects/{pid}/clips/{clip['id']}",
                     json={"script": VALID_SCRIPT + "\n# otro\n"})
    assert r.status_code == 200
    d = authed.get(f"/api/projects/{pid}/narracion").json()
    assert d["clips"][0]["estado"] == "desactualizada"

    # Demasiado grande -> 413 (tope configurable)
    import app.main as main_mod
    main_mod.narracion_service.cfg.max_upload_audio_mb = 0
    r = authed.put(url + "?nombre=voz.wav", content=_wav_bytes(0.5))
    assert r.status_code == 413


def test_recortar_silencio_de_la_grabacion(authed, tmp_path):
    """Una toma casera trae aire al principio y al final: se recorta."""
    project = _create_project(authed)
    pid = project["id"]
    clip = _add_clip(authed, pid)
    import math
    rate = 24_000
    silencio = b"\x00\x00" * rate  # 1 s
    tono = b"".join(int(6000 * math.sin(2 * math.pi * 220 * i / rate))
                    .to_bytes(2, "little", signed=True) for i in range(rate))
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
        w.writeframes(silencio + tono + silencio)
    r = authed.put(f"/api/projects/{pid}/narracion/{clip['id']}/audio?nombre=a.wav",
                   content=buf.getvalue())
    assert r.status_code == 200, r.text
    # 1 s de voz + 0.12 s de margen a cada lado
    assert 1.1 <= r.json()["audio_s"] <= 1.35
