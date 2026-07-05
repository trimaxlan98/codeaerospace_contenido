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
