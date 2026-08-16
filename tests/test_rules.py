from datetime import datetime, timezone
from src.model import Match
from src.rules import Watchlist, is_selected, is_team

def m(home, away, league="SL", round=1, channel=""):
    return Match(1, league, home, away, datetime(2026, 9, 1, tzinfo=timezone.utc), round, False, None, channel)

WL = Watchlist(teams=["Beşiktaş", "manchester city"], matches=["Arsenal-Liverpool"],
               rules={"sl_derbies": True, "pl_big6": True, "cl_from_qf": True, "cl_tr_teams": True, "cl_trt": True},
               alerts_minutes=[60, 15])

def test_is_team_alias_and_accent():
    assert is_team(m("Beşiktaş", "Kasımpaşa"), "besiktas")
    assert is_team(m("Man City", "Burnley"), "manchester city")
    assert is_team(m("Spurs", "Burnley"), "Tottenham")
    assert not is_team(m("Man Utd", "Burnley"), "man city")

def test_teams_list():
    assert is_selected(m("Kasimpasa", "Besiktas"), WL)
    assert is_selected(m("Man City", "Burnley", "PL"), WL)

def test_matches_list_order_free():
    assert is_selected(m("Liverpool", "Arsenal", "PL"), WL)
    off = Watchlist(teams=[], matches=["Arsenal-Liverpool"], rules={}, alerts_minutes=[60])
    assert is_selected(m("Liverpool", "Arsenal", "PL"), off)
    assert not is_selected(m("Liverpool", "Chelsea", "PL"), off)

def test_sl_derby():
    assert is_selected(m("Fenerbahçe", "Galatasaray"), WL)
    assert not is_selected(m("Fenerbahçe", "Konyaspor"), WL)

def test_pl_big6_only_between_big6():
    assert is_selected(m("Chelsea", "Man Utd", "PL"), WL)
    assert not is_selected(m("Chelsea", "Burnley", "PL"), WL)

def test_cl_rules():
    assert is_selected(m("Real Madrid", "Bayern München", "CL", 13), WL)
    assert not is_selected(m("Real Madrid", "Bayern München", "CL", 3), WL)
    assert is_selected(m("Galatasaray", "Bayern München", "CL", 3), WL)
    assert is_selected(m("Real Madrid", "Bayern München", "CL", 3, channel="TRT 1"), WL)

def test_rules_off():
    off = Watchlist(teams=[], matches=[], rules={}, alerts_minutes=[60])
    assert not is_selected(m("Fenerbahçe", "Galatasaray"), off)

def test_load_yaml(tmp_path):
    p = tmp_path / "w.yml"
    p.write_text("teams: [Beşiktaş]\nmatches: []\nrules: {sl_derbies: true}\nalerts_minutes: [30]\n", encoding="utf-8")
    wl = Watchlist.load(p)
    assert wl.teams == ["Beşiktaş"] and wl.alerts_minutes == [30] and wl.rules["sl_derbies"]
