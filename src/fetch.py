import logging, re
import requests, urllib3
from src import config
from src.model import normalize

log = logging.getLogger(__name__)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)   # sadece TFF için verify=False
UA ={"User-Agent": "Mozilla/5.0 (futbol-takvim)"}

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

TFF_URL = "https://www.tff.org/Default.aspx?pageID=198&hafta={week}"
TFF_WEEKS = 34

def fetch_tff() -> list["Match"]:
    """Süper Lig'i TFF resmi sitesinden hafta hafta çeker (saatler fixturedownload'dan önce burada güncellenir)."""
    from src.model import parse_tff_week
    matches = []
    for week in range(1, TFF_WEEKS + 1):
        # tff.org ara sertifikayı göndermiyor → Python doğrulaması düşüyor. Veri açık/hassas değil.
        r = requests.get(TFF_URL.format(week=week), headers=UA, timeout=30, verify=False)
        r.raise_for_status()
        wk = parse_tff_week(r.text, week)
        if not wk:
            raise FetchError(f"TFF hafta {week}: maç bulunamadı (sayfa yapısı değişmiş olabilir)")
        matches += wk
    return matches

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
