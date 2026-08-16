import json
from src.model import Match, normalize, parse_fixtures

def test_normalize_strips_accents_and_case():
    assert normalize("Beşiktaş") == "besiktas"
    assert normalize("Fenerbahçe") == "fenerbahce"
    assert normalize("  Manchester City ") == "manchester city"
    assert normalize("Kasımpaşa") == "kasimpasa"

def test_parse_fixtures():
    data = json.load(open("tests/fixtures/sl_sample.json", encoding="utf-8"))
    matches = parse_fixtures(data, "SL")
    assert len(matches) == 2
    m = matches[0]
    assert m.id == 1001 and m.league == "SL"
    assert m.home == "Besiktas" and m.away == "Galatasaray"
    assert m.start.tzinfo is not None and m.start.utcoffset().total_seconds() == 0
    assert m.round == "Regular Season - 2"
    assert m.finished and m.score == "2-1"
    assert not matches[1].finished and matches[1].score is None
