"""Biblioteca de entregas: listar exports/, servir un archivo y no salirse."""

import struct


def _mp4(segundos: float, escala: int = 600) -> bytes:
    """Un mp4 minimo con ftyp + moov/mvhd: lo justo para que el lector de
    duracion tenga algo real que leer (sin ffmpeg, que el backend no tiene)."""
    mvhd = bytearray(b"\x00" * 100)
    mvhd[0] = 0  # version 0
    struct.pack_into(">II", mvhd, 12, escala, int(segundos * escala))
    caja_mvhd = struct.pack(">I4s", len(mvhd) + 8, b"mvhd") + bytes(mvhd)
    moov = struct.pack(">I4s", len(caja_mvhd) + 8, b"moov") + caja_mvhd
    ftyp = struct.pack(">I4s", 16, b"ftyp") + b"isom" + b"\x00" * 4
    # `mdat` entre medias: obliga a saltar de caja en caja, como un mp4 real
    mdat = struct.pack(">I4s", 8 + 4096, b"mdat") + b"\x00" * 4096
    return ftyp + mdat + moov


def _sembrar(tmp_path):
    ex = tmp_path / "exports"
    (ex / "peliculas" / "abc123").mkdir(parents=True)
    (ex / "peliculas" / "abc123" / "pelicula.mp4").write_bytes(_mp4(151.5))
    (ex / "peliculas" / "abc123" / "plan.json").write_text('{"piezas": 4}')
    (ex / "verticales" / "sistemas" / "piezas").mkdir(parents=True)
    (ex / "verticales" / "sistemas" / "sistemas_vertical.mp4").write_bytes(_mp4(30.25))
    (ex / "musica").mkdir()
    (ex / "musica" / "orbita.wav").write_bytes(b"RIFF" + b"\x00" * 100)
    return ex


def test_listar_raiz_y_carpeta(authed, tmp_path):
    _sembrar(tmp_path)
    r = authed.get("/api/entregas")
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["ruta"] == "" and d["padre"] is None
    nombres = {c["nombre"]: c for c in d["carpetas"]}
    assert set(nombres) == {"peliculas", "verticales", "musica"}
    # El resumen cuenta TODO el arbol, no solo el primer nivel
    assert nombres["peliculas"]["archivos"] == 2
    assert nombres["peliculas"]["bytes"] > 4000
    assert nombres["musica"]["titulo"] == "Banco de música"
    assert d["archivos"] == []

    r = authed.get("/api/entregas", params={"ruta": "peliculas/abc123"})
    d = r.json()
    assert d["padre"] == "peliculas"
    por_nombre = {a["nombre"]: a for a in d["archivos"]}
    assert por_nombre["pelicula.mp4"]["tipo"] == "video"
    assert abs(por_nombre["pelicula.mp4"]["duracion"] - 151.5) < 0.01
    assert por_nombre["plan.json"]["tipo"] == "texto"
    assert por_nombre["plan.json"]["duracion"] is None


def test_servir_archivo_y_descarga(authed, tmp_path):
    ex = _sembrar(tmp_path)
    r = authed.get("/api/entregas/archivo/verticales/sistemas/sistemas_vertical.mp4")
    assert r.status_code == 200
    assert r.headers["content-type"] == "video/mp4"
    assert r.content == (ex / "verticales" / "sistemas" / "sistemas_vertical.mp4").read_bytes()
    r = authed.get("/api/entregas/archivo/musica/orbita.wav")
    assert r.status_code == 200 and r.headers["content-type"] == "audio/wav"


def test_no_se_sale_de_exports(authed, tmp_path):
    _sembrar(tmp_path)
    (tmp_path / "secreto.txt").write_text("no")
    for ruta in ("../secreto.txt", "peliculas/../../secreto.txt",
                 "/etc/passwd", "peliculas/abc123/../../../secreto.txt"):
        r = authed.get("/api/entregas", params={"ruta": ruta})
        assert r.status_code in (400, 404), (ruta, r.status_code)
        r = authed.get(f"/api/entregas/archivo/{ruta}")
        assert r.status_code in (400, 404), (ruta, r.status_code)
    # Un enlace que apunta fuera tampoco vale (exports puede ser un enlace,
    # pero lo que cuelga de el tiene que seguir dentro).
    (tmp_path / "exports" / "fuga").symlink_to(tmp_path / "secreto.txt")
    r = authed.get("/api/entregas/archivo/fuga")
    assert r.status_code in (400, 404)


def test_carpeta_inexistente_y_sin_exports(authed, tmp_path):
    _sembrar(tmp_path)
    assert authed.get("/api/entregas", params={"ruta": "nada"}).status_code == 404
    import shutil
    shutil.rmtree(tmp_path / "exports")
    d = authed.get("/api/entregas").json()
    assert d["carpetas"] == [] and "vacio" in d


def test_requiere_sesion(client, tmp_path):
    _sembrar(tmp_path)
    assert client.get("/api/entregas").status_code == 401
    assert client.get("/api/entregas/archivo/musica/orbita.wav").status_code == 401


def test_duracion_sin_cargar_el_archivo(tmp_path):
    """El lector salta de caja en caja: un archivo grande no se lee entero."""
    from app.entregas import duracion_mp4
    p = tmp_path / "grande.mp4"
    datos = _mp4(42.0)
    # 8 MB de relleno entre el mdat y el moov
    relleno = struct.pack(">I4s", 8 + (8 << 20), b"free") + b"\x00" * (8 << 20)
    p.write_bytes(datos[:16] + relleno + datos[16:])
    assert abs(duracion_mp4(p) - 42.0) < 0.01
    assert duracion_mp4(tmp_path / "no-existe.mp4") is None
    (tmp_path / "roto.mp4").write_bytes(b"no soy un mp4")
    assert duracion_mp4(tmp_path / "roto.mp4") is None
