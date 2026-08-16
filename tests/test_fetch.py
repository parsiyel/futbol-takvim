import pytest
from src import fetch

class FakeResp:
    def __init__(self, status, payload): self.status_code = status; self._p = payload
    def json(self): return self._p
    def raise_for_status(self):
        if self.status_code >= 400: raise RuntimeError("http")

def test_fetch_league_ok(monkeypatch):
    seen = {}
    def fake_get(url, headers, params, timeout):
        seen.update(url=url, headers=headers, params=params)
        return FakeResp(200, {"response": [{"x": 1}]})
    monkeypatch.setattr(fetch.requests, "get", fake_get)
    data = fetch.fetch_league(203, "KEY")
    assert data["response"] == [{"x": 1}]
    assert seen["url"].endswith("/fixtures")
    assert seen["headers"]["x-apisports-key"] == "KEY"
    assert seen["params"] == {"league": 203, "season": fetch.config.SEASON}

def test_fetch_league_empty_raises(monkeypatch):
    monkeypatch.setattr(fetch.requests, "get", lambda *a, **k: FakeResp(200, {"response": [], "errors": {"plan": "x"}}))
    with pytest.raises(fetch.FetchError):
        fetch.fetch_league(203, "KEY")

def test_trt_matches_parses_teams():
    html = '<div class="program"><span class="time">22:00</span><span class="title">UEFA Şampiyonlar Ligi: Galatasaray - Bayern Münih</span></div>'
    pairs = fetch.parse_trt_html(html)
    assert pairs == [("galatasaray", "bayern munih")]

def test_trt_failure_returns_empty(monkeypatch):
    def boom(*a, **k): raise RuntimeError("down")
    monkeypatch.setattr(fetch.requests, "get", boom)
    assert fetch.trt_cl_pairs(days=2) == set()
