import logging, re
import requests
from src import config
from src.model import normalize

log = logging.getLogger(__name__)
UA = {"User-Agent": "Mozilla/5.0 (futbol-takvim)"}

class FetchError(Exception): ...

def fetch_feed(league: str) -> list[dict] | None:
    """fixturedownload feed'i. required=False lig 404 verirse None döner; diğer hatalar FetchError."""
    cfg = config.FEEDS[league]
    r = requests.get(f"{config.FEED_BASE}/{cfg['slug']}", headers=UA, timeout=30)
    if r.status_code == 404 and not cfg["required"]:
        log.warning("%s feed'i henüz yok (%s)", league, cfg["slug"])
        return None
    if r.status_code != 200:
        raise FetchError(f"{league}: HTTP {r.status_code}")
    data = r.json()
    if not data:
        raise FetchError(f"{league}: boş feed")
    return data

# TRT 1 yayın akışı sayfası EPG'yi gömülü JSON olarak taşır:
#   "title":"Fenerbahçe - Lyon | UEFA Şampiyonlar Ligi Play Off Maçı"
# Sayfa yalnızca bugünü ve geçmiş haftayı içerir; ileri tarih yok.
TRT_URL = "https://www.trt1.com.tr/yayin-akisi"
_TRT_RE = re.compile(r'"title":"([^"|]+?)\s*[-–]\s*([^"|]+?)\s*\|[^"]*ampiyonlar Ligi[^"]*"', re.I)

def parse_trt_html(html: str) -> list[tuple[str, str]]:
    return [(normalize(a), normalize(b)) for a, b in _TRT_RE.findall(html)]

def trt_cl_pairs() -> set[tuple[str, str]]:
    """TRT 1 yayın akışındaki ŞL maçlarının (ev, dep) normalize çiftleri. Hata → boş küme."""
    try:
        r = requests.get(TRT_URL, timeout=20, headers=UA)
        r.raise_for_status()
        return set(parse_trt_html(r.text))
    except Exception as e:      # kazıma best-effort
        log.warning("TRT yayın akışı okunamadı: %s", e)
        return set()
