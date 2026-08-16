from datetime import datetime, timezone
from src.model import Match
from src.ics import build_calendar

def m(**kw):
    base = dict(id=7, league="SL", home="Beşiktaş", away="Galatasaray",
                start=datetime(2026, 9, 1, 17, 0, tzinfo=timezone.utc),
                round=4, finished=False, score=None, channel="TOD")
    base.update(kw); return Match(**base)

def test_event_fields():
    cal = build_calendar("Futbol", [(m(), True)], alerts=[60, 15])
    text = cal.to_ical().decode()
    assert "X-WR-CALNAME:Futbol" in text
    assert "UID:SL-7@futbol-takvim" in text
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

def test_cl_round_labels():
    text = build_calendar("F", [(m(league="CL", round=13, channel="tabii"), False)], alerts=[]).to_ical().decode()
    assert "Şampiyonlar Ligi · Çeyrek Final · tabii" in text
    text = build_calendar("F", [(m(league="CL", round=3, channel="tabii"), False)], alerts=[]).to_ical().decode()
    assert "Lig Aşaması 3. Hafta" in text
