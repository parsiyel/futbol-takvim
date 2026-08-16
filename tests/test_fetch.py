import pytest
from src import fetch

class FakeResp:
    def __init__(self, status, payload=None, text=""):
        self.status_code = status; self._p = payload; self.text = text
    def json(self): return self._p
    def raise_for_status(self):
        if self.status_code >= 400: raise RuntimeError("http")

def test_fetch_feed_ok(monkeypatch):
    seen = {}
    def fake_get(url, headers, timeout):
        seen["url"] = url
        return FakeResp(200, [{"MatchNumber": 1}])
    monkeypatch.setattr(fetch.requests, "get", fake_get)
    assert fetch.fetch_feed("SL") == [{"MatchNumber": 1}]
    assert seen["url"].endswith("/super-lig-2026")

def test_fetch_feed_optional_404_returns_none(monkeypatch):
    monkeypatch.setattr(fetch.requests, "get", lambda *a, **k: FakeResp(404))
    assert fetch.fetch_feed("CL") is None

def test_fetch_feed_required_404_raises(monkeypatch):
    monkeypatch.setattr(fetch.requests, "get", lambda *a, **k: FakeResp(404))
    with pytest.raises(fetch.FetchError):
        fetch.fetch_feed("SL")

def test_fetch_feed_empty_raises(monkeypatch):
    monkeypatch.setattr(fetch.requests, "get", lambda *a, **k: FakeResp(200, []))
    with pytest.raises(fetch.FetchError):
        fetch.fetch_feed("PL")

def test_fetch_tff_all_weeks(monkeypatch):
    html = open("tests/fixtures/tff_week2.html", encoding="utf-8").read()
    calls = []
    def fake_get(url, headers, timeout):
        calls.append(url); return FakeResp(200, text=html)
    monkeypatch.setattr(fetch.requests, "get", fake_get)
    ms = fetch.fetch_tff()
    assert len(calls) == 34 and calls[0].endswith("hafta=1") and calls[-1].endswith("hafta=34")
    assert len(ms) == 34 * 2 and ms[-1].round == 34

def test_fetch_tff_empty_week_raises(monkeypatch):
    monkeypatch.setattr(fetch.requests, "get", lambda *a, **k: FakeResp(200, text="<html></html>"))
    with pytest.raises(fetch.FetchError):
        fetch.fetch_tff()

def test_trt_matches_parses_teams():
    html = ('{"title":"Haber","starttime":"x"},'
            '{"title":"Fenerbahçe - Lyon | UEFA Şampiyonlar Ligi Play Off Maçı","starttime":"y"},'
            '{"title":"Manchester City-Galatasaray | UEFA Şampiyonlar Ligi Grup Maçları"},'
            '{"title":"FSCB -Fenerbahçe | Avrupa Ligi Grup Maçları"}')
    assert fetch.parse_trt_html(html) == [("fenerbahce", "lyon"), ("manchester city", "galatasaray")]

def test_trt_failure_returns_empty(monkeypatch):
    def boom(*a, **k): raise RuntimeError("down")
    monkeypatch.setattr(fetch.requests, "get", boom)
    assert fetch.trt_cl_pairs() == set()
