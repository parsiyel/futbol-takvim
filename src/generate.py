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

def run(out_dir, watchlist_path: str, suffix: str) -> None:
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
        run(Path("docs"), "watchlist.yml", os.environ.get("ICS_SUFFIX") or "x")
    except Exception as e:
        log.error("üretim başarısız, eski dosyalar korunuyor: %s", e)
        sys.exit(1)
