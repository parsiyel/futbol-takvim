SEASON = 2026
FEED_BASE = "https://fixturedownload.com/feed/json"

# fixturedownload slug'ları. required=False olan lig yoksa (404) atlanır —
# ŞL fikstürü kura çekimine kadar yayınlanmıyor.
FEEDS = {
    "SL": {"slug": f"super-lig-{SEASON}", "required": True},
    "PL": {"slug": f"epl-{SEASON}", "required": True},
    "CL": {"slug": f"champions-league-{SEASON}", "required": False},
}
LEAGUE_NAMES = {"SL": "Süper Lig", "PL": "Premier League", "CL": "Şampiyonlar Ligi"}
CHANNELS = {"SL": "TOD", "PL": "TOD", "CL": "tabii"}
TRT_CHANNEL = "TRT 1"

# Feed'deki takım adları kısa (Man City, Man Utd, Spurs); normalize edilmiş halleri
SL_BIG4 = {"besiktas", "fenerbahce", "galatasaray", "trabzonspor"}
PL_BIG6 = {"arsenal", "chelsea", "liverpool", "man city", "man utd", "spurs"}
TR_TEAMS = SL_BIG4 | {"basaksehir", "samsunspor", "eyupspor", "goztepe", "kasimpasa", "konyaspor", "rizespor", "antalyaspor", "kayserispor", "alanyaspor", "gaziantep", "sivasspor", "kocaelispor", "genclerbirligi", "karagumruk", "corum"}

# kullanıcı yazımı -> feed adı (normalize edilmiş)
ALIASES = {"manchester city": "man city", "manchester united": "man utd", "man united": "man utd",
           "tottenham": "spurs", "bjk": "besiktas", "fb": "fenerbahce", "gs": "galatasaray", "ts": "trabzonspor"}

# ŞL tur numaraları (fixturedownload): 1-8 lig aşaması, 9-10 play-off, 11-12 son 16, 13-14 çeyrek, 15-16 yarı, 17 final
CL_ROUND_LABELS = {9: "Play-off", 10: "Play-off", 11: "Son 16", 12: "Son 16", 13: "Çeyrek Final", 14: "Çeyrek Final",
                   15: "Yarı Final", 16: "Yarı Final", 17: "Final"}
CL_QF_ROUND = 13
