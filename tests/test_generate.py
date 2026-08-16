import json
from datetime import datetime, timezone
from src import generate
from src.model import Match

def test_assign_channel_trt():
    m = Match(1, "CL", "Galatasaray", "Bayern München", datetime(2026,9,1,tzinfo=timezone.utc), 1, False, None)
    generate.assign_channels([m], trt_pairs={("galatasaray", "bayern munih")})
    assert m.channel == "TRT 1"
    m.channel = ""
    generate.assign_channels([m], trt_pairs={("bayern munih", "galatasaray")})   # ters sıra eşleşmez
    assert m.channel == "tabii"
    m2 = Match(2, "CL", "Arsenal", "Inter", m.start, 1, False, None)
    generate.assign_channels([m2], trt_pairs=set())
    assert m2.channel == "tabii"

def test_split_calendars():
    t = datetime(2026,9,1,tzinfo=timezone.utc)
    ms = [Match(1,"SL","Beşiktaş","Rizespor",t,1,False,None,"TOD"),
          Match(3,"PL","Arsenal","Burnley",t,1,False,None,"TOD")]
    bjk, futbol = generate.split(ms)
    assert [m.id for m in bjk] == [1]
    assert [m.id for m in futbol] == [1, 3]

def test_run_writes_files_and_skips_missing_cl(tmp_path, monkeypatch):
    sample = json.load(open("tests/fixtures/sl_sample.json", encoding="utf-8"))
    monkeypatch.setattr(generate.fetch, "fetch_feed", lambda league: None if league == "CL" else sample)
    monkeypatch.setattr(generate.fetch, "trt_cl_pairs", lambda: set())
    generate.run(out_dir=tmp_path, watchlist_path="watchlist.yml", suffix="test")
    bjk = (tmp_path / "besiktas-test.ics").read_text(encoding="utf-8")
    assert "BEGIN:VALARM" in bjk and "UID:SL-3@futbol-takvim" in bjk
    assert (tmp_path / "futbol-test.ics").exists()
