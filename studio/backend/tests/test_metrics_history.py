"""Pruebas del ring buffer de metricas y su endpoint."""


def test_history_requires_auth(client):
    assert client.get("/api/metrics/history").status_code == 401


def test_history_shape_and_ring(authed):
    from app.main import history
    host = {"ts": 1000.0, "cpu_pct": 12.5, "mem": {"pct": 40.0}, "disk": {"pct": 55.0}}
    history.add(host, None)
    history.add(host | {"ts": 1004.0}, [
        {"name": "manimstudio-render-abc123", "state": "running",
         "cpu_pct": 90.0, "mem_pct": 20.0},
    ])

    data = authed.get("/api/metrics/history").json()
    assert data["interval"] > 0
    samples = data["samples"]
    assert len(samples) >= 2
    s0, s1 = samples[-2], samples[-1]
    assert s0 == {"ts": 1000.0, "cpu": 12.5, "mem": 40.0, "disk": 55.0,
                  "render": False, "render_cpu": None, "render_mem": None}
    assert s1["render"] is True and s1["render_cpu"] == 90.0

    # Ring: nunca crece mas alla de maxlen
    for i in range(history.samples.maxlen + 10):
        history.add(host | {"ts": 2000.0 + i}, None)
    assert len(history.samples) == history.samples.maxlen


def test_history_save_and_load_roundtrip(tmp_path):
    from app.metrics import History
    host = {"ts": 5000.0, "cpu_pct": 10.0, "mem": {"pct": 20.0}, "disk": {"pct": 30.0}}
    h = History(maxlen=10)
    h.add(host, None)
    h.add(host | {"ts": 5004.0}, None)
    path = tmp_path / "snap.json"
    h.save(path)

    h2 = History(maxlen=10)
    h2.load(path, interval=4.0, now=5010.0)  # ventana=40s: ambas caben
    assert [s["ts"] for s in h2.samples] == [5000.0, 5004.0]
    assert h2.samples[0]["cpu"] == 10.0


def test_history_load_drops_stale(tmp_path):
    from app.metrics import History
    h = History(maxlen=10)
    h.add({"ts": 1000.0, "cpu_pct": 1.0, "mem": {"pct": 1.0}, "disk": {"pct": 1.0}}, None)
    h.add({"ts": 9000.0, "cpu_pct": 2.0, "mem": {"pct": 2.0}, "disk": {"pct": 2.0}}, None)
    path = tmp_path / "snap.json"
    h.save(path)

    h2 = History(maxlen=10)
    h2.load(path, interval=4.0, now=9010.0)  # ventana=40s: corta ts=1000
    assert [s["ts"] for s in h2.samples] == [9000.0]


def test_history_load_missing_or_corrupt_ok(tmp_path):
    from app.metrics import History
    h = History(maxlen=10)
    h.load(tmp_path / "nope.json", interval=4.0, now=0.0)  # ausente: no falla
    assert len(h.samples) == 0
    bad = tmp_path / "bad.json"
    bad.write_text("{no es json", encoding="utf-8")
    h.load(bad, interval=4.0, now=0.0)                     # corrupto: no falla
    assert len(h.samples) == 0
