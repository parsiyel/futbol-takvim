SEASON = 2026
API_BASE = "https://v3.football.api-sports.io"

# Lig id'leri: Süper Lig, Premier League, Şampiyonlar Ligi, Türkiye Kupası
LEAGUES = {203: "SL", 39: "PL", 2: "CL", 206: "TRCUP"}
LEAGUE_NAMES = {"SL": "Süper Lig", "PL": "Premier League", "CL": "Şampiyonlar Ligi", "TRCUP": "Türkiye Kupası"}
CHANNELS = {"SL": "TOD", "PL": "TOD", "CL": "tabii", "TRCUP": "A Spor"}
TRT_CHANNEL = "TRT 1"
FUTBOL_LEAGUES = {"SL", "PL", "CL"}

SL_BIG4 = {"besiktas", "fenerbahce", "galatasaray", "trabzonspor"}
PL_BIG6 = {"arsenal", "chelsea", "liverpool", "manchester city", "manchester united", "tottenham"}
TR_TEAMS = SL_BIG4 | {"basaksehir", "samsunspor", "eyupspor", "goztepe", "kasimpasa", "konyaspor", "rizespor", "antalyaspor", "kayserispor", "alanyaspor", "gaziantep", "sivasspor", "kocaelispor", "genclerbirligi", "karagumruk"}

ALIASES = {"man city": "manchester city", "man utd": "manchester united", "man united": "manchester united", "spurs": "tottenham", "bjk": "besiktas", "fb": "fenerbahce", "gs": "galatasaray", "ts": "trabzonspor"}

CL_KO_ROUNDS = ("Quarter-finals", "Semi-finals", "Final")
