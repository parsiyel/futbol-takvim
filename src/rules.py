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
    manual: list[dict] = field(default_factory=list)
    include: dict[str, list[str]] = field(default_factory=dict)   # lig -> takvime girecek takımlar (yoksa hepsi)
    besiktas_alerts: dict = field(default_factory=lambda: {"minutes": [60, 0], "morning": "11:00"})

    @classmethod
    def load(cls, path) -> "Watchlist":
        d = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        return cls(teams=d.get("teams") or [], matches=d.get("matches") or [],
                   rules=d.get("rules") or {}, alerts_minutes=d.get("alerts_minutes") or [60, 15],
                   manual=d.get("manual") or [], include=d.get("include") or {},
                   besiktas_alerts=d.get("besiktas_alerts") or {"minutes": [60, 0], "morning": "11:00"})

def is_included(match: Match, wl: Watchlist) -> bool:
    """Ligde `include` listesi varsa yalnızca o takımların maçları takvime girer."""
    teams = wl.include.get(match.league)
    return not teams or any(is_team(match, t) for t in teams)

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
    if match.league == "MANUAL":          # elle girilen maç her zaman alarmlı
        return True
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
    if match.league in config.EUROPE:     # ŞL / Avrupa Ligi / Konferans Ligi
        if r.get("eu_from_qf") and match.round >= config.QF_ROUND[match.league]:
            return True
        if r.get("eu_tr_teams") and any(_has(match, t) for t in config.TR_TEAMS):
            return True
        if r.get("eu_trt") and match.channel == config.TRT_CHANNEL:
            return True
    return False
