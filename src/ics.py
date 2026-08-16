from datetime import timedelta, timezone
from zoneinfo import ZoneInfo
from icalendar import Calendar, Event, Alarm
from src import config
from src.model import Match

TZ = ZoneInfo("Europe/Istanbul")

def _round_label(m: Match) -> str:
    if m.league in config.EUROPE:
        return config.ROUND_LABELS[m.league].get(m.round, f"Lig Aşaması {m.round}. Hafta")
    return f"{m.round}. Hafta"

def _description(m: Match) -> str:
    if m.league == "MANUAL":
        return f"{m.note} · {m.channel}" if m.note else m.channel
    return f"{config.LEAGUE_NAMES[m.league]} · {_round_label(m)} · {m.channel}"

def _alarm(title: str, trigger) -> Alarm:
    a = Alarm()
    a.add("action", "DISPLAY")
    a.add("description", title)
    if isinstance(trigger, timedelta):
        a.add("trigger", trigger)
    else:                                   # mutlak zaman (UTC) — RFC 5545 VALUE=DATE-TIME ister
        a.add("trigger", trigger, parameters={"VALUE": "DATE-TIME"})
    return a

def build_calendar(name: str, items: list[tuple[Match, bool]], alerts: list[int],
                   morning: str | None = None) -> Calendar:
    """alerts: maçtan N dakika önce. morning: "HH:MM" (TR) — maç günü sabah alarmı, maç saatinden önceyse eklenir."""
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
        desc = _description(m)
        if m.finished and m.score:
            desc += f"\nSkor: {m.score}"
        if m.league != "MANUAL" and start.hour == 0 and start.minute == 0:   # feed placeholder: saat açıklanmamış
            desc += "\n⚠️ Saat henüz kesinleşmedi"
        ev.add("description", desc)
        if selected:
            for mins in alerts:
                ev.add_component(_alarm(title, timedelta(minutes=-mins)))
            if morning:
                hh, mm = (int(x) for x in morning.split(":"))
                at = start.replace(hour=hh, minute=mm, second=0)
                if at < start:
                    ev.add_component(_alarm(f"Bugün maç var: {title}", at.astimezone(timezone.utc)))
        cal.add_component(ev)
    return cal
