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
