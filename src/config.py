SEASON = 2026
FEED_BASE = "https://fixturedownload.com/feed/json"

# fixturedownload slug'ları. required=False olan lig yoksa (404) atlanır —
# ŞL fikstürü kura çekimine kadar yayınlanmıyor.
FEEDS = {
    "SL": {"slug": f"super-lig-{SEASON}", "required": True},
    "PL": {"slug": f"epl-{SEASON}", "required": True},
    "CL": {"slug": f"champions-league-{SEASON}", "required": False},
    "EL": {"slug": f"europa-league-{SEASON}", "required": False},
    "UECL": {"slug": f"conference-league-{SEASON}", "required": False},
}
# Feed'lerde eleme turları yok; onlar watchlist.yml `manual:` ile elle girilir (league="MANUAL").
LEAGUE_NAMES = {"SL": "Süper Lig", "PL": "Premier League", "CL": "Şampiyonlar Ligi",
                "EL": "Avrupa Ligi", "UECL": "Konferans Ligi", "MANUAL": ""}
CHANNELS = {"SL": "TOD", "PL": "TOD", "CL": "tabii", "EL": "tabii", "UECL": "tabii", "MANUAL": ""}
EUROPE = {"CL", "EL", "UECL"}
TRT_CHANNEL = "TRT 1"

# Feed'deki takım adları kısa (Man City, Man Utd, Spurs); normalize edilmiş halleri
SL_BIG4 = {"besiktas", "fenerbahce", "galatasaray", "trabzonspor"}
PL_BIG6 = {"arsenal", "chelsea", "liverpool", "man city", "man utd", "spurs"}
TR_TEAMS = SL_BIG4 | {"basaksehir", "samsunspor", "eyupspor", "goztepe", "kasimpasa", "konyaspor", "rizespor", "antalyaspor", "kayserispor", "alanyaspor", "gaziantep", "sivasspor", "kocaelispor", "genclerbirligi", "karagumruk", "corum"}

# kullanıcı yazımı -> feed adı (normalize edilmiş)
ALIASES = {"manchester city": "man city", "manchester united": "man utd", "man united": "man utd",
           "tottenham": "spurs", "bjk": "besiktas", "fb": "fenerbahce", "gs": "galatasaray", "ts": "trabzonspor"}

# Avrupa kupaları tur numaraları (fixturedownload). ŞL/AL: 1-8 lig aşaması, 9-10 play-off, 11-12 son 16,
# 13-14 çeyrek, 15-16 yarı, 17 final. Konferans: 1-6 lig aşaması, sonrası aynı sırayla.
def _ko_labels(first_ko: int) -> dict[int, str]:
    names = ["Play-off", "Play-off", "Son 16", "Son 16", "Çeyrek Final", "Çeyrek Final", "Yarı Final", "Yarı Final", "Final"]
    return {first_ko + i: n for i, n in enumerate(names)}
ROUND_LABELS = {"CL": _ko_labels(9), "EL": _ko_labels(9), "UECL": _ko_labels(7)}
QF_ROUND = {"CL": 13, "EL": 13, "UECL": 11}
