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
    channel: str = ""    # generate.py doldurur (MANUAL: yaml'dan)
    note: str = ""       # MANUAL: serbest açıklama ("Avrupa Ligi 3. Eleme Turu")

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

def parse_manual(items: list[dict]) -> list[Match]:
    """watchlist.yml `manual:` girdileri. Saat Türkiye saati (Europe/Istanbul).
    {date: "2026-08-20 21:00", home: Beşiktaş, away: X, note: "...", channel: "tabii"}"""
    from zoneinfo import ZoneInfo
    tz = ZoneInfo("Europe/Istanbul")
    out = []
    for i, it in enumerate(items, start=1):
        start = datetime.strptime(str(it["date"]), "%Y-%m-%d %H:%M").replace(tzinfo=tz).astimezone(timezone.utc)
        out.append(Match(id=i, league="MANUAL", home=it["home"], away=it["away"], start=start,
                         round=0, finished=False, score=None,
                         channel=str(it.get("channel", "")), note=str(it.get("note", ""))))
    return out

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
