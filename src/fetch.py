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
