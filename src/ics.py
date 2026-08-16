from datetime import timedelta
from zoneinfo import ZoneInfo
from icalendar import Calendar, Event, Alarm
from src import config
from src.model import Match

TZ = ZoneInfo("Europe/Istanbul")

def _round_label(m: Match) -> str:
    if m.league == "CL":
        return config.CL_ROUND_LABELS.get(m.round, f"Lig Aşaması {m.round}. Hafta")
    return f"{m.round}. Hafta"

def build_calendar(name: str, items: list[tuple[Match, bool]], alerts: list[int]) -> Calendar:
    cal = Calendar()
    cal.add("prodid", "-//futbol-takvim//TR")
    cal.add("version", "2.0")
    cal.add("X-WR-CALNAME", name)
    cal.add("X-WR-TIMEZONE", "Europe/Istanbul")
    cal.add("REFRESH-INTERVAL;VALUE=DURATION", "PT1H")
    for m, selected in items:
        ev = Event()
        ev.add("uid", m.uid)
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
