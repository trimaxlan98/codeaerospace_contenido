"""Banco de sonidos audible (sprint E3).

Sin Docker: la sintesis corre `sfx.py paleta` en el contenedor. Lo que se
prueba aqui es la puerta — que un nombre de la URL no pueda salirse del
conjunto cerrado de la paleta — y que el listado no ofrezca efectos que la
mezcla ya no sabe sintetizar.
"""

from app import audio_promo


def _sembrar(cfg, *nombres):
    cfg.sfx_dir.mkdir(parents=True, exist_ok=True)
    for n in nombres:
        (cfg.sfx_dir / f"{n}.wav").write_bytes(b"RIFF----WAVEfmt ")


def test_banco_vacio(authed):
    r = authed.get("/api/sfx")
    assert r.status_code == 200
    body = r.json()
    assert body["listos"] == []
    assert body["completo"] is False
    assert sorted(body["sonidos"]) == sorted(audio_promo.SONIDOS)


def test_el_listado_ignora_los_efectos_de_una_paleta_vieja(authed):
    """`exports/sfx/` sobrevive a los cambios de PALETA: una corrida anterior
    dejo `pad_intro`/`pad_cierre`, que ya no existen. Ofrecerlos en el
    desplegable seria ofrecer algo que la mezcla no sabe sintetizar."""
    from app.main import cfg

    _sembrar(cfg, "tick", "pad", "pad_intro", "pad_cierre")
    listos = authed.get("/api/sfx").json()["listos"]
    assert listos == ["pad", "tick"]


def test_completo_cuando_estan_todos(authed):
    from app.main import cfg

    _sembrar(cfg, *audio_promo.SONIDOS)
    body = authed.get("/api/sfx").json()
    assert body["completo"] is True
    assert len(body["listos"]) == len(audio_promo.SONIDOS)


def test_se_puede_oir_un_sonido_de_la_paleta(authed):
    from app.main import cfg

    _sembrar(cfg, "sting")
    r = authed.get("/api/sfx/sting")
    assert r.status_code == 200
    assert r.headers["content-type"] == "audio/wav"


def test_un_sonido_que_no_esta_en_la_paleta_es_404(authed):
    from app.main import cfg

    _sembrar(cfg, "sting")
    assert authed.get("/api/sfx/trueno").status_code == 404
    # Y nada de la URL toca el disco: el nombre va contra el conjunto cerrado
    # ANTES de construir ninguna ruta.
    assert authed.get("/api/sfx/..%2F..%2Fetc%2Fpasswd").status_code == 404


def test_sonido_sin_sintetizar_es_404_con_mensaje(authed):
    r = authed.get("/api/sfx/sting")
    assert r.status_code == 404
    assert "sintetizado" in r.json()["detail"]


def test_el_banco_requiere_sesion(client):
    assert client.get("/api/sfx").status_code == 401
    assert client.get("/api/sfx/tick").status_code == 401
