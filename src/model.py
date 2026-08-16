import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass
class Match:
    id: int              # feed MatchNumber (lig içinde benzersiz)
    league: str          # "SL" | "PL" | "CL"
    home: str
    away: str
    start: datetime      # tz-aware (UTC)
    round: int
    finished: bool
    score: str | None
    channel: str = ""    # generate.py doldurur

    @property
    def home_n(self) -> str: return normalize(self.home)
    @property
    def away_n(self) -> str: return normalize(self.away)
    @property
    def uid(self) -> str: return f"{self.league}-{self.id}@futbol-takvim"

def normalize(name: str) -> str:
    s = name.replace("ı", "i").replace("I", "i")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower().strip()

def parse_feed(items: list[dict], league: str) -> list[Match]:
    """fixturedownload.com JSON feed -> Match listesi."""
    out = []
    for it in items:
        hs, as_ = it.get("HomeTeamScore"), it.get("AwayTeamScore")
        finished = hs is not None and as_ is not None
        start = datetime.strptime(it["DateUtc"], "%Y-%m-%d %H:%M:%SZ").replace(tzinfo=timezone.utc)
        out.append(Match(
            id=int(it["MatchNumber"]), league=league,
            home=it["HomeTeam"], away=it["AwayTeam"],
            start=start, round=int(it["RoundNumber"]),
            finished=finished, score=f"{hs}-{as_}" if finished else None,
        ))
    return out
