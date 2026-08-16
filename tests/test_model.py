import json
from src.model import normalize, parse_feed

def test_normalize_strips_accents_and_case():
    assert normalize("Beşiktaş") == "besiktas"
    assert normalize("Fenerbahçe") == "fenerbahce"
    assert normalize("  Manchester City ") == "manchester city"
    assert normalize("Kasımpaşa") == "kasimpasa"
    assert normalize("Gençlerbirligi") == "genclerbirligi"

def test_parse_feed():
    data = json.load(open("tests/fixtures/sl_sample.json", encoding="utf-8"))
    matches = parse_feed(data, "SL")
    assert len(matches) == 3
    m = matches[0]
    assert m.id == 7 and m.league == "SL" and m.round == 1
    assert m.home == "Galatasaray" and m.away == "Çorum"
    assert m.start.isoformat() == "2026-08-14T18:30:00+00:00"
    assert m.finished and m.score == "2-2"
    assert m.uid == "SL-7@futbol-takvim"
    assert not matches[1].finished and matches[1].score is None
