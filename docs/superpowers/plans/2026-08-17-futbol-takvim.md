# futbol-takvim Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** API-Football fikstürlerinden iki `.ics` takvim (Beşiktaş + Futbol) üretip GitHub Pages'ta yayınlayan, watchlist kurallarıyla alarm ekleyen script + Actions workflow.

**Architecture:** `fetch.py` API'den ham fikstür JSON'u alır → `model.py` sade `Match` nesnesine çevirir → `rules.py` watchlist'e göre "seçili" mi karar verir → `ics.py` iki takvim üretir → `generate.py` hepsini bağlar ve `docs/*.ics` yazar. Actions cron ile çalıştırıp commit atar.

**Tech Stack:** Python 3.12, `requests`, `icalendar`, `pyyaml`, `pytest`, GitHub Actions, GitHub Pages.

Spec: `docs/superpowers/specs/2026-08-17-futbol-takvim-design.md`
Repo kökü: `D:\AI\Projeler\futbol-takvim`

---

## Dosya yapısı

| Dosya | Sorumluluk |
|---|---|
| `src/config.py` | Sabitler: lig ID'leri, sezon, kanal tablosu, takım grupları, alias tablosu |
| `src/model.py` | `Match` dataclass + API JSON → `Match` dönüşümü, ad normalizasyonu |
| `src/fetch.py` | API-Football HTTP çağrısı, TRT yayın akışı kazıma |
| `src/rules.py` | `Watchlist` yükleme + `is_selected(match, watchlist)` |
| `src/ics.py` | `Match` listesinden `icalendar.Calendar` üretimi |
| `src/generate.py` | Giriş noktası: fetch → rules → ics → dosya yaz |
| `watchlist.yml` | Kullanıcı seçimleri |
| `tests/fixtures/*.json` | Kayıtlı API cevapları |
| `tests/test_*.py` | Birim testler |
| `.github/workflows/build.yml` | Cron + push tetikli üretim ve commit |
| `docs/` | Pages çıktısı |

---

### Task 1: Proje iskeleti

**Files:**
- Create: `requirements.txt`, `pyproject.toml`, `.gitignore`, `src/__init__.py`, `tests/__init__.py`

- [ ] **Step 1: requirements.txt**

```
requests==2.32.3
icalendar==6.1.0
PyYAML==6.0.2
pytest==8.3.4
```

- [ ] **Step 2: pyproject.toml** (pytest'in `src`'yi bulması için)

```toml
[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
```

- [ ] **Step 3: .gitignore**

```
__pycache__/
.pytest_cache/
.venv/
*.pyc
```

- [ ] **Step 4: Boş `src/__init__.py` ve `tests/__init__.py` oluştur, venv kur**

```bash
cd D:/AI/Projeler/futbol-takvim
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt
```

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "chore: proje iskeleti"
```

---

### Task 2: config.py

**Files:**
- Create: `src/config.py`

- [ ] **Step 1: Yaz**

```python
SEASON = 2026
API_BASE = "https://v3.football.api-sports.io"

LEAGUES = {          # API-Football lig id -> kısa ad
    203: "SL",       # Süper Lig
    39: "PL",        # Premier League
    2: "CL",         # Şampiyonlar Ligi
    206: "TRCUP",    # Türkiye Kupası
}
LEAGUE_NAMES = {"SL": "Süper Lig", "PL": "Premier League", "CL": "Şampiyonlar Ligi", "TRCUP": "Türkiye Kupası"}
CHANNELS = {"SL": "TOD", "PL": "TOD", "CL": "tabii", "TRCUP": "A Spor"}
TRT_CHANNEL = "TRT 1"

# futbol.ics'e giren ligler (TRCUP sadece Beşiktaş takvimine girer)
FUTBOL_LEAGUES = {"SL", "PL", "CL"}

SL_BIG4 = {"besiktas", "fenerbahce", "galatasaray", "trabzonspor"}
PL_BIG6 = {"arsenal", "chelsea", "liverpool", "manchester city", "manchester united", "tottenham"}
TR_TEAMS = SL_BIG4 | {"basaksehir", "samsunspor", "eyupspor", "goztepe", "kasimpasa", "konyaspor", "rizespor", "antalyaspor", "kayserispor", "alanyaspor", "gaziantep", "sivasspor", "kocaelispor", "genclerbirligi", "karagumruk"}

# kullanıcı yazımı -> normalize edilmiş API adı alt-dizesi
ALIASES = {
    "man city": "manchester city",
    "man utd": "manchester united",
    "man united": "manchester united",
    "spurs": "tottenham",
    "bjk": "besiktas",
    "fb": "fenerbahce",
    "gs": "galatasaray",
    "ts": "trabzonspor",
}

CL_KO_ROUNDS = ("Quarter-finals", "Semi-finals", "Final")
```

- [ ] **Step 2: Commit**

```bash
git add src/config.py && git commit -m "feat: config sabitleri"
```

---

### Task 3: model.py — Match ve normalizasyon

**Files:**
- Create: `src/model.py`, `tests/test_model.py`, `tests/fixtures/sl_sample.json`

- [ ] **Step 1: Fixture JSON** (API-Football gerçek şekli, iki maç: biri bitmiş, biri planlı)

`tests/fixtures/sl_sample.json`:
```json
{"response": [
 {"fixture": {"id": 1001, "date": "2026-08-15T18:00:00+00:00", "status": {"short": "FT"}},
  "league": {"id": 203, "round": "Regular Season - 2"},
  "teams": {"home": {"name": "Besiktas"}, "away": {"name": "Galatasaray"}},
  "goals": {"home": 2, "away": 1}},
 {"fixture": {"id": 1002, "date": "2026-08-22T16:00:00+00:00", "status": {"short": "NS"}},
  "league": {"id": 203, "round": "Regular Season - 3"},
  "teams": {"home": {"name": "Fenerbahçe"}, "away": {"name": "Beşiktaş"}},
  "goals": {"home": null, "away": null}}
]}
```

- [ ] **Step 2: Failing test**

`tests/test_model.py`:
```python
import json
from datetime import timezone
from src.model import Match, normalize, parse_fixtures

def test_normalize_strips_accents_and_case():
    assert normalize("Beşiktaş") == "besiktas"
    assert normalize("Fenerbahçe") == "fenerbahce"
    assert normalize("  Manchester City ") == "manchester city"

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
```

- [ ] **Step 3: Çalıştır, FAIL gör**

Run: `.venv/Scripts/pytest tests/test_model.py -v` → `ModuleNotFoundError: src.model`

- [ ] **Step 4: Implement**

`src/model.py`:
```python
import unicodedata
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Match:
    id: int
    league: str          # "SL" | "PL" | "CL" | "TRCUP"
    home: str
    away: str
    start: datetime      # tz-aware (UTC)
    round: str
    finished: bool
    score: str | None
    channel: str = ""    # generate.py doldurur

    @property
    def home_n(self) -> str: return normalize(self.home)
    @property
    def away_n(self) -> str: return normalize(self.away)

def normalize(name: str) -> str:
    s = unicodedata.normalize("NFKD", name)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.replace("ı", "i").lower().strip()

def parse_fixtures(data: dict, league: str) -> list[Match]:
    out = []
    for item in data.get("response", []):
        f, t, g = item["fixture"], item["teams"], item["goals"]
        finished = f["status"]["short"] in ("FT", "AET", "PEN")
        score = f"{g['home']}-{g['away']}" if finished and g["home"] is not None else None
        out.append(Match(
            id=f["id"], league=league,
            home=t["home"]["name"], away=t["away"]["name"],
            start=datetime.fromisoformat(f["date"]),
            round=item["league"].get("round", ""),
            finished=finished, score=score,
        ))
    return out
```

- [ ] **Step 5: PASS gör, commit**

Run: `.venv/Scripts/pytest tests/test_model.py -v` → 2 passed
```bash
git add src/model.py tests/ && git commit -m "feat: Match modeli ve API parse"
```

---

### Task 4: rules.py — watchlist ve seçim

**Files:**
- Create: `src/rules.py`, `tests/test_rules.py`, `watchlist.yml`

- [ ] **Step 1: watchlist.yml**

```yaml
teams:
  - Beşiktaş
matches: []          # örnek: "Arsenal-Manchester City"
rules:
  sl_derbies: true
  pl_big6: true
  cl_from_qf: true
  cl_tr_teams: true
  cl_trt: true
alerts_minutes: [60, 15]
```

- [ ] **Step 2: Failing test**

`tests/test_rules.py`:
```python
from datetime import datetime, timezone
from src.model import Match
from src.rules import Watchlist, is_selected, is_team

def m(home, away, league="SL", round="Regular Season - 1", channel=""):
    return Match(1, league, home, away, datetime(2026, 9, 1, tzinfo=timezone.utc), round, False, None, channel)

WL = Watchlist(teams=["Beşiktaş", "man city"], matches=["Arsenal-Liverpool"],
               rules={"sl_derbies": True, "pl_big6": True, "cl_from_qf": True, "cl_tr_teams": True, "cl_trt": True},
               alerts_minutes=[60, 15])

def test_is_team_alias_and_accent():
    assert is_team(m("Beşiktaş", "Kasımpaşa"), "besiktas")
    assert is_team(m("Manchester City", "Burnley"), "man city")
    assert not is_team(m("Manchester United", "Burnley"), "man city")

def test_teams_list():
    assert is_selected(m("Kasımpaşa", "Beşiktaş"), WL)
    assert is_selected(m("Manchester City", "Burnley", "PL"), WL)

def test_matches_list_order_free():
    assert is_selected(m("Liverpool", "Arsenal", "PL"), WL)
    off = Watchlist(teams=[], matches=["Arsenal-Liverpool"], rules={}, alerts_minutes=[60])
    assert is_selected(m("Liverpool", "Arsenal", "PL"), off)
    assert not is_selected(m("Liverpool", "Chelsea", "PL"), off)

def test_sl_derby():
    assert is_selected(m("Fenerbahçe", "Galatasaray"), WL)
    assert not is_selected(m("Fenerbahçe", "Konyaspor"), WL)

def test_pl_big6_only_between_big6():
    assert not is_selected(m("Chelsea", "Burnley", "PL"), WL)

def test_cl_rules():
    assert is_selected(m("Real Madrid", "Bayern", "CL", "Quarter-finals"), WL)
    assert not is_selected(m("Real Madrid", "Bayern", "CL", "League Stage - 3"), WL)
    assert is_selected(m("Galatasaray", "Bayern", "CL", "League Stage - 3"), WL)
    assert is_selected(m("Real Madrid", "Bayern", "CL", "League Stage - 3", channel="TRT 1"), WL)

def test_rules_off():
    off = Watchlist(teams=[], matches=[], rules={}, alerts_minutes=[60])
    assert not is_selected(m("Fenerbahçe", "Galatasaray"), off)

def test_load_yaml(tmp_path):
    p = tmp_path / "w.yml"
    p.write_text("teams: [Beşiktaş]\nmatches: []\nrules: {sl_derbies: true}\nalerts_minutes: [30]\n", encoding="utf-8")
    wl = Watchlist.load(p)
    assert wl.teams == ["Beşiktaş"] and wl.alerts_minutes == [30] and wl.rules["sl_derbies"]
```

- [ ] **Step 3: FAIL gör**

Run: `.venv/Scripts/pytest tests/test_rules.py -v` → ModuleNotFoundError

- [ ] **Step 4: Implement**

`src/rules.py`:
```python
from dataclasses import dataclass, field
from pathlib import Path
import yaml
from src import config
from src.model import Match, normalize

@dataclass
class Watchlist:
    teams: list[str] = field(default_factory=list)
    matches: list[str] = field(default_factory=list)
    rules: dict = field(default_factory=dict)
    alerts_minutes: list[int] = field(default_factory=lambda: [60, 15])

    @classmethod
    def load(cls, path: Path) -> "Watchlist":
        d = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        return cls(teams=d.get("teams") or [], matches=d.get("matches") or [],
                   rules=d.get("rules") or {}, alerts_minutes=d.get("alerts_minutes") or [60, 15])

def _canon(user_name: str) -> str:
    n = normalize(user_name)
    return config.ALIASES.get(n, n)

def _has(match: Match, key: str) -> bool:
    return key in match.home_n or key in match.away_n

def is_team(match: Match, name: str) -> bool:
    return _has(match, _canon(name))

def _both_in(match: Match, group: set[str]) -> bool:
    return any(k in match.home_n for k in group) and any(k in match.away_n for k in group)

def is_selected(match: Match, wl: Watchlist) -> bool:
    if any(is_team(match, t) for t in wl.teams):
        return True
    for pair in wl.matches:
        parts = [_canon(p) for p in pair.split("-", 1)]
        if len(parts) == 2 and _both_in(match, set(parts)):
            return True
    r = wl.rules
    if match.league == "SL" and r.get("sl_derbies") and _both_in(match, config.SL_BIG4):
        return True
    if match.league == "PL" and r.get("pl_big6") and _both_in(match, config.PL_BIG6):
        return True
    if match.league == "CL":
        if r.get("cl_from_qf") and match.round.startswith(config.CL_KO_ROUNDS):
            return True
        if r.get("cl_tr_teams") and any(_has(match, t) for t in config.TR_TEAMS):
            return True
        if r.get("cl_trt") and match.channel == config.TRT_CHANNEL:
            return True
    return False
```

- [ ] **Step 5: PASS, commit**

Run: `.venv/Scripts/pytest tests/test_rules.py -v` → all passed
```bash
git add src/rules.py tests/test_rules.py watchlist.yml && git commit -m "feat: watchlist kural motoru"
```

---

### Task 5: ics.py — takvim üretimi

**Files:**
- Create: `src/ics.py`, `tests/test_ics.py`

- [ ] **Step 1: Failing test**

`tests/test_ics.py`:
```python
from datetime import datetime, timezone
from src.model import Match
from src.ics import build_calendar

def m(**kw):
    base = dict(id=7, league="SL", home="Beşiktaş", away="Galatasaray",
                start=datetime(2026, 9, 1, 17, 0, tzinfo=timezone.utc),
                round="Regular Season - 4", finished=False, score=None, channel="TOD")
    base.update(kw); return Match(**base)

def test_event_fields():
    cal = build_calendar("Futbol", [(m(), True)], alerts=[60, 15])
    text = cal.to_ical().decode()
    assert "X-WR-CALNAME:Futbol" in text
    assert "UID:af-7@futbol-takvim" in text
    assert "SUMMARY:🔔 ⚽ Beşiktaş – Galatasaray" in text
    assert "LOCATION:TOD" in text
    assert "DTSTART;TZID=Europe/Istanbul:20260901T200000" in text
    assert "DTEND;TZID=Europe/Istanbul:20260901T220000" in text
    assert "Süper Lig · 4. Hafta · TOD" in text
    assert text.count("BEGIN:VALARM") == 2
    assert "TRIGGER:-PT1H" in text and "TRIGGER:-PT15M" in text

def test_unselected_has_no_alarm_or_bell():
    text = build_calendar("Futbol", [(m(), False)], alerts=[60]).to_ical().decode()
    assert "BEGIN:VALARM" not in text
    assert "SUMMARY:⚽ Beşiktaş – Galatasaray" in text

def test_finished_score_in_description():
    text = build_calendar("Futbol", [(m(finished=True, score="2-1"), False)], alerts=[]).to_ical().decode()
    assert "Skor: 2-1" in text

def test_cl_round_label():
    text = build_calendar("F", [(m(league="CL", round="Quarter-finals", channel="tabii"), False)], alerts=[]).to_ical().decode()
    assert "Şampiyonlar Ligi · Quarter-finals · tabii" in text
```

- [ ] **Step 2: FAIL gör**

Run: `.venv/Scripts/pytest tests/test_ics.py -v`

- [ ] **Step 3: Implement**

`src/ics.py`:
```python
import re
from datetime import timedelta
from zoneinfo import ZoneInfo
from icalendar import Calendar, Event, Alarm
from src import config
from src.model import Match

TZ = ZoneInfo("Europe/Istanbul")

def _round_label(m: Match) -> str:
    mo = re.match(r"Regular Season - (\d+)", m.round)
    return f"{mo.group(1)}. Hafta" if mo else m.round

def build_calendar(name: str, items: list[tuple[Match, bool]], alerts: list[int]) -> Calendar:
    cal = Calendar()
    cal.add("prodid", "-//futbol-takvim//TR")
    cal.add("version", "2.0")
    cal.add("X-WR-CALNAME", name)
    cal.add("X-WR-TIMEZONE", "Europe/Istanbul")
    cal.add("REFRESH-INTERVAL;VALUE=DURATION", "PT1H")
    for m, selected in items:
        ev = Event()
        ev.add("uid", f"af-{m.id}@futbol-takvim")
        title = f"⚽ {m.home} – {m.away}"
        ev.add("summary", f"🔔 {title}" if selected else title)
        start = m.start.astimezone(TZ)
        ev.add("dtstart", start)
        ev.add("dtend", start + timedelta(hours=2))
        ev.add("dtstamp", start)
        ev.add("location", m.channel)
        desc = f"{config.LEAGUE_NAMES[m.league]} · {_round_label(m)} · {m.channel}"
        if m.finished and m.score:
            desc += f"\nSkor: {m.score}"
        ev.add("description", desc)
        if selected:
            for mins in alerts:
                a = Alarm()
                a.add("action", "DISPLAY")
                a.add("description", title)
                a.add("trigger", timedelta(minutes=-mins))
                ev.add_component(a)
        cal.add_component(ev)
    return cal
```

Not: `icalendar` `TRIGGER:-PT1H0M0S` gibi yazabilir; test `-PT1H` alt-dizesi arıyor, uyumlu. `DTSTART;TZID=Europe/Istanbul:` biçimi icalendar 6'da varsayılan; farklı çıkarsa `ev.add("dtstart", start, parameters={"TZID": "Europe/Istanbul"})` kullan.

- [ ] **Step 4: PASS, commit**

```bash
git add src/ics.py tests/test_ics.py && git commit -m "feat: ics üretimi"
```

---

### Task 6: fetch.py — API ve TRT

**Files:**
- Create: `src/fetch.py`, `tests/test_fetch.py`

- [ ] **Step 1: Failing test** (HTTP mock'lu)

`tests/test_fetch.py`:
```python
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
```

- [ ] **Step 2: FAIL gör**

- [ ] **Step 3: Implement**

`src/fetch.py`:
```python
import logging, re
from datetime import date, timedelta
import requests
from src import config
from src.model import normalize

log = logging.getLogger(__name__)

class FetchError(Exception): ...

def fetch_league(league_id: int, api_key: str) -> dict:
    r = requests.get(f"{config.API_BASE}/fixtures",
                     headers={"x-apisports-key": api_key},
                     params={"league": league_id, "season": config.SEASON}, timeout=30)
    r.raise_for_status()
    data = r.json()
    if not data.get("response"):
        raise FetchError(f"league {league_id}: boş cevap, errors={data.get('errors')}")
    return data

_TRT_RE = re.compile(r"Şampiyonlar Ligi[^<]*?:\s*([^<\-–]+?)\s*[-–]\s*([^<]+?)\s*<", re.I)

def parse_trt_html(html: str) -> list[tuple[str, str]]:
    return [(normalize(a), normalize(b)) for a, b in _TRT_RE.findall(html)]

def trt_cl_pairs(days: int = 7) -> set[tuple[str, str]]:
    """Önümüzdeki `days` gün için TRT 1 yayın akışındaki ŞL maçlarının (ev, dep) normalize çiftleri."""
    pairs: set[tuple[str, str]] = set()
    for i in range(days):
        d = date.today() + timedelta(days=i)
        url = f"https://www.trt1.com.tr/yayin-akisi/{d.isoformat()}"
        try:
            r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            pairs.update(parse_trt_html(r.text))
        except Exception as e:      # kazıma best-effort
            log.warning("TRT %s okunamadı: %s", d, e)
    return pairs
```

- [ ] **Step 4: PASS, commit**

```bash
git add src/fetch.py tests/test_fetch.py && git commit -m "feat: API-Football ve TRT fetch"
```

---

### Task 7: generate.py — giriş noktası

**Files:**
- Create: `src/generate.py`, `tests/test_generate.py`

- [ ] **Step 1: Failing test**

`tests/test_generate.py`:
```python
import json
from src import generate

def test_assign_channel_trt():
    from datetime import datetime, timezone
    from src.model import Match
    m = Match(1, "CL", "Galatasaray", "Bayern München", datetime(2026,9,1,tzinfo=timezone.utc), "League Stage - 1", False, None)
    generate.assign_channels([m], trt_pairs={("galatasaray", "bayern munchen")})
    assert m.channel == "TRT 1"
    m2 = Match(2, "CL", "Arsenal", "Inter", m.start, "League Stage - 1", False, None)
    generate.assign_channels([m2], trt_pairs=set())
    assert m2.channel == "tabii"

def test_split_calendars():
    from datetime import datetime, timezone
    from src.model import Match
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
```

- [ ] **Step 2: FAIL gör**

- [ ] **Step 3: Implement**

`src/generate.py`:
```python
import logging, os, sys
from pathlib import Path
from src import config, fetch
from src.ics import build_calendar
from src.model import Match, parse_fixtures
from src.rules import Watchlist, is_selected, is_team

log = logging.getLogger(__name__)

def assign_channels(matches: list[Match], trt_pairs: set[tuple[str, str]]) -> None:
    for m in matches:
        m.channel = config.CHANNELS[m.league]
        if m.league == "CL" and (m.home_n, m.away_n) in trt_pairs:
            m.channel = config.TRT_CHANNEL

def split(matches: list[Match]) -> tuple[list[Match], list[Match]]:
    bjk = [m for m in matches if is_team(m, "besiktas")]
    futbol = [m for m in matches if m.league in config.FUTBOL_LEAGUES]
    return bjk, futbol

def run(out_dir: Path, watchlist_path: str, suffix: str) -> None:
    key = os.environ["API_FOOTBALL_KEY"]
    wl = Watchlist.load(watchlist_path)
    matches: list[Match] = []
    for lid, short in config.LEAGUES.items():
        matches += parse_fixtures(fetch.fetch_league(lid, key), short)
    assign_channels(matches, fetch.trt_cl_pairs())
    matches.sort(key=lambda m: m.start)
    bjk, futbol = split(matches)
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"besiktas-{suffix}.ics").write_bytes(
        build_calendar("Beşiktaş", [(m, True) for m in bjk], wl.alerts_minutes).to_ical())
    (out_dir / f"futbol-{suffix}.ics").write_bytes(
        build_calendar("Futbol", [(m, is_selected(m, wl)) for m in futbol], wl.alerts_minutes).to_ical())
    log.info("yazıldı: %d Beşiktaş, %d futbol", len(bjk), len(futbol))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        run(Path("docs"), "watchlist.yml", os.environ.get("ICS_SUFFIX", "x"))
    except Exception as e:
        log.error("üretim başarısız, eski dosyalar korunuyor: %s", e)
        sys.exit(1)
```

- [ ] **Step 4: PASS, commit**

Run: `.venv/Scripts/pytest -v` → tümü geçer
```bash
git add src/generate.py tests/test_generate.py && git commit -m "feat: generate giriş noktası"
```

---

### Task 8: Gerçek API ile ilk deneme (kullanıcı adımı gerekir)

**Files:** yok (yalnızca çalıştırma)

- [ ] **Step 1: Kullanıcıdan API key al** — api-sports.io ücretsiz hesap. Bu adım kullanıcı tarafından yapılır; key sohbete yapıştırılmaz, doğrudan GitHub Secret'a ve lokal ortam değişkenine kullanıcı girer.

- [ ] **Step 2: Lokal çalıştır**

```powershell
$env:API_FOOTBALL_KEY="..." ; $env:ICS_SUFFIX="deneme"; .venv\Scripts\python -m src.generate
```
Beklenen: `docs/besiktas-deneme.ics` ve `docs/futbol-deneme.ics` oluşur, log satırında maç sayıları > 0.

- [ ] **Step 3: Doğrula** — `docs/besiktas-deneme.ics` içinde `Beşiktaş` geçen etkinlikler ve VALARM'lar var; SL sezon fikstürü tam mı (34 hafta × 9 = 306 maç civarı)?

Sezon boş dönerse (ücretsiz plan kısıtı): `config.SEASON` ve `errors` alanına bak; spec'teki yedek kaynak planına geç, kullanıcıya bildir.

- [ ] **Step 4:** Deneme dosyalarını sil (`docs/*-deneme.ics`), commit yok.

---

### Task 9: GitHub Actions workflow

**Files:**
- Create: `.github/workflows/build.yml`

- [ ] **Step 1: Yaz**

```yaml
name: build-ics
on:
  schedule:
    - cron: "0 3,9,14,18 * * *"   # UTC → TR 06,12,17,21
  push:
    branches: [main]
    paths: [watchlist.yml, "src/**"]
  workflow_dispatch:
permissions:
  contents: write
concurrency: build-ics
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -r requirements.txt
      - run: python -m pytest -q
      - run: python -m src.generate
        env:
          API_FOOTBALL_KEY: ${{ secrets.API_FOOTBALL_KEY }}
          ICS_SUFFIX: ${{ secrets.ICS_SUFFIX }}
      - name: commit
        run: |
          git config user.name "futbol-bot"
          git config user.email "bot@users.noreply.github.com"
          git add docs/*.ics
          git diff --cached --quiet || git commit -m "chore: ics güncelle $(date -u +%F_%H:%M)"
          git push
```

- [ ] **Step 2: Commit**

```bash
git add .github && git commit -m "ci: cron ile ics üretimi"
```

---

### Task 10: README + repo oluşturma + Pages

**Files:**
- Create: `README.md`, `docs/.nojekyll`

- [ ] **Step 1: README.md** — spec'teki "Kurulum (kullanıcı adımları)" bölümünü ve watchlist örneğini kopyala; abonelik URL'lerini `https://parsiyel.github.io/futbol-takvim/besiktas-<EK>.ics` biçiminde yaz.

- [ ] **Step 2: `docs/.nojekyll`** boş dosya (Pages'in `_`'li dosyaları yoksaymaması için, zararsız).

- [ ] **Step 3: Repo oluştur ve push**

```bash
cd D:/AI/Projeler/futbol-takvim
gh repo create parsiyel/futbol-takvim --private --source=. --push
```

- [ ] **Step 4: Secrets** — `ICS_SUFFIX` için rastgele 4-6 karakter üret (`python -c "import secrets;print(secrets.token_hex(3))"`), `gh secret set ICS_SUFFIX` ile ekle. `API_FOOTBALL_KEY`'i **kullanıcı** girer (`gh secret set API_FOOTBALL_KEY` ya da web arayüzü).

- [ ] **Step 5: Pages** — Settings → Pages → Deploy from branch → `main` / `/docs`. (`gh api -X POST repos/parsiyel/futbol-takvim/pages -f "source[branch]=main" -f "source[path]=/docs"` da olur.) Not: private repoda Pages, GitHub Free'de **çalışmaz** → repo **public** olmalı ya da Pro hesap. Kullanıcıya sor; public ise `ICS_SUFFIX` sadece URL gizliliği sağlar, watchlist herkese görünür (hassas değil).

- [ ] **Step 6: Workflow'u elle tetikle** — `gh workflow run build-ics`; bitince `docs/*.ics` commit'i gelmiş mi kontrol et. Pages URL'sini tarayıcıda aç, ICS indiğini gör.

- [ ] **Step 7: iPhone aboneliği** — kullanıcı: Ayarlar → Takvim → Hesaplar → Hesap Ekle → Diğer → Abone Olunan Takvim Ekle → URL; "Uyarıları Kaldır" **kapalı**. İki takvim için iki kez.

- [ ] **Step 8: Commit + push**

```bash
git add README.md docs/.nojekyll && git commit -m "docs: README ve Pages" && git push
```

---

## Self-review

- **Spec kapsamı:** iki takvim ✔ (T7), kurallar+liste ✔ (T4), kanal+TRT ✔ (T6/T7), skor ✔ (T3/T5), hata → exit 1 eski dosya korunur ✔ (T7 `__main__`), cron 4×/gün + watchlist push ✔ (T9), Pages+abonelik ✔ (T10), TRCUP sadece Beşiktaş takvimi ✔ (`FUTBOL_LEAGUES`).
- **Açık nokta:** private repo + Pages Free planda çalışmaz — T10 adım 5'te kullanıcıya soruluyor.
- **Tip tutarlılığı:** `Match(id, league, home, away, start, round, finished, score, channel)` sırası tüm testlerde aynı; `is_team`, `is_selected`, `Watchlist.load`, `build_calendar(name, items, alerts)`, `fetch_league(lid, key)`, `trt_cl_pairs()`, `assign_channels`, `split`, `run(out_dir, watchlist_path, suffix)` tutarlı.
