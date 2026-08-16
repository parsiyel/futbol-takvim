import json
from datetime import datetime, timezone
from src import generate
from src.model import Match

def test_assign_channel_trt():
    m = Match(1, "CL", "Galatasaray", "Bayern München", datetime(2026,9,1,tzinfo=timezone.utc), "League Stage - 1", False, None)
    generate.assign_channels([m], trt_pairs={("galatasaray", "bayern munchen")})
    assert m.channel == "TRT 1"
    m2 = Match(2, "CL", "Arsenal", "Inter", m.start, "League Stage - 1", False, None)
    generate.assign_channels([m2], trt_pairs=set())
    assert m2.channel == "tabii"

def test_split_calendars():
    t = datetime(2026,9,1,tzinfo=timezone.utc)
    ms = [Match(1,"SL","Beşiktaş","Rizespor",t,"Regular Season - 1",False,None,"TOD"),
          Match(2,"TRCUP","Beşiktaş","Amedspor",t,"Round of 32",False,None,"A Spor"),
          Match(3,"PL","Arsenal","Burnley",t,"Regular Season - 1",False,None,"TOD")]
    bjk, futbol = generate.split(ms)
    assert [m.id for m in bjk] == [1, 2]
    assert [m.id for m in futbol] == [1, 3]

def test_run_writes_files(tmp_path, monkeypatch):
    sample = json.load(open("tests/fixtures/sl_sample.json", encoding="utf-8"))
    monkeypatch.setattr(generate.fetch, "fetch_league", lambda lid, key: sample)
    monkeypatch.setattr(generate.fetch, "trt_cl_pairs", lambda: set())
    monkeypatch.setenv("API_FOOTBALL_KEY", "k")
    generate.run(out_dir=tmp_path, watchlist_path="watchlist.yml", suffix="test")
    assert (tmp_path / "besiktas-test.ics").exists()
    assert (tmp_path / "futbol-test.ics").exists()
    assert "BEGIN:VALARM" in (tmp_path / "besiktas-test.ics").read_text(encoding="utf-8")
