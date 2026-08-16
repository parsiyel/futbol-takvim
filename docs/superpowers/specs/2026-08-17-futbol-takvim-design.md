# futbol-takvim — Tasarım

Tarih: 2026-08-17

## Amaç

Süper Lig, Premier League ve Şampiyonlar Ligi maçlarını iPhone Takvim'inde
haftalık program olarak görmek; Beşiktaş maçları ve seçilen "büyük" maçlar için
otomatik alarm almak. Yayın kanalı (TOD / TRT / tabii) etkinlikte görünsün.

Kullanıcı: Beşiktaş taraftarı, TOD aboneliği var, TRT'deki Avrupa maçlarını da
izliyor. Bakım yükü minimum olmalı.

## Kapsam

Dahil:
- Süper Lig (tamamı) — kanal: TOD
- Premier League (tamamı) — kanal: TOD
- Şampiyonlar Ligi (tamamı) — kanal: tabii; TRT'nin haftalık açık maçı best-effort işaretlenir
- Türkiye Kupası — yalnızca Beşiktaş maçları
- Ertelenen/saati değişen maçların otomatik güncellenmesi
- Biten maçların açıklamasına skor yazılması

Dahil değil (bilerek): canlı skor bildirimi, web arayüzü, push bildirim,
milli takım, diğer ligler.

## Mimari

```
API-Football ──► generate.py ──► docs/besiktas.ics ──► GitHub Pages ──► iPhone Takvim (abone)
TRT yayın akışı ─┘   ▲           docs/futbol.ics
                     │
              watchlist.yml
```

- **Repo:** GitHub `parsiyel/futbol-takvim` (private). GitHub Pages `docs/` klasöründen
  yayınlar; iPhone `https://parsiyel.github.io/futbol-takvim/<dosya>.ics` adresine
  abone olur. Dosya adlarına tahmin edilemez bir ek eklenir (ör.
  `futbol-a8f3.ics`) — Pages public olduğundan basit gizlilik.
- **Çalışma:** GitHub Actions cron günde 4 kez (TR 06:00, 12:00, 17:00, 21:00)
  + `watchlist.yml` push'unda + elle tetikleme. Üretilen `.ics` değiştiyse
  bot commit atar.
- **Dil/kütüphane:** Python 3.12, `requests`, `icalendar`, `pyyaml`.
- **Sırlar:** `API_FOOTBALL_KEY` GitHub Secret.

## Veri kaynağı

**Güncelleme 2026-08-17:** API-Football ücretsiz planı mevcut sezonu vermiyor
("Free plans do not have access to this season, try from 2022 to 2024"). ESPN'in
açık API'si datacenter IP'lerini (GitHub Actions dahil) 403 ile engelliyor,
TheSportsDB ücretsiz key sezon başına 5 maçla sınırlı. Seçilen kaynak:

**fixturedownload.com JSON feed** — key yok, `GET /feed/json/<slug>` sezonun tüm
fikstürünü skorlarla verir. Slug'lar: `super-lig-2026` (306 maç), `epl-2026`
(380 maç), `champions-league-2026` (kura çekimine kadar 404 → **opsiyonel**,
yoksa uyarı verip atlanır). Alanlar: `MatchNumber`, `RoundNumber`, `DateUtc`,
`HomeTeam`, `AwayTeam`, `HomeTeamScore`, `AwayTeamScore`. Bitmiş maç = skorlar
dolu. UID: `{lig}-{MatchNumber}@futbol-takvim`.

Takım adları kısa (`Man City`, `Man Utd`, `Spurs`); `PL_BIG6` ve `ALIASES` buna
göre. ŞL tur numaraları: 1-8 lig aşaması, 9-10 play-off, 11-12 son 16, 13-14
çeyrek, 15-16 yarı, 17 final; `cl_from_qf` = tur ≥ 13.

**Türkiye Kupası kapsamdan çıkarıldı** — ücretsiz kaynak yok.

**Güncelleme 2 (2026-08-17 akşam):** fixturedownload Süper Lig saatlerini geç
güncelliyor (TFF 8 Ağustos'ta açıkladığı 2-3. hafta saatleri 9 gün sonra hâlâ
placeholder). Süper Lig için birincil kaynak **TFF resmi sitesi** oldu:
`https://www.tff.org/Default.aspx?pageID=198&hafta={1..34}` — hafta başına bir
sayfa, `lblTarih`/`lblSaat`/`Label4`(ev)/`Label1`(dep)/`Label5-6`(skor)/`macId`.
Saat boşsa 00:00 TR placeholder. Takım adları sponsor/A.Ş./FK temizlenip Türkçe
title-case (`tff_team_name`). UID `SL-{macId}`. tff.org ara sertifika
göndermediği için bu istekte `verify=False`. TFF okunamazsa fixturedownload
feed'ine düşülür (UID'ler farklı olduğundan geçici olarak takvim yenilenir).

Avrupa Ligi (`europa-league-2026`) ve Konferans Ligi (`conference-league-2026`)
opsiyonel feed olarak eklendi. Feed'lerde eleme/play-off turları yok →
`watchlist.yml` `manual:` girdileri (tarih TR saati, ev, dep, not, kanal) her
zaman alarmlı olarak Beşiktaş takvimine girer. Kural adları `eu_from_qf`,
`eu_tr_teams`, `eu_trt` (üç Avrupa kupası). Konferans çeyrek final = tur 11.

Beşiktaş maçları yalnızca `besiktas.ics`'te; `futbol.ics` geri kalanı içerir
(çift kayıt olmasın).

### Kanal bilgisi

API'de yok, kural ile eklenir:

| Lig | Kanal |
|---|---|
| Süper Lig | TOD |
| Premier League | TOD |
| Şampiyonlar Ligi | tabii; TRT'nin haftalık maçı ise `TRT 1` |
| Türkiye Kupası | A Spor / TOD (best-effort) |

TRT maçı: `https://www.trt1.com.tr/yayin-akisi` sayfasındaki gömülü EPG JSON'unda
`"title":"Ev - Dep | UEFA Şampiyonlar Ligi ..."` kalıbı. **Sayfa yalnızca bugünü
ve geçmiş haftayı verir**, ileri tarih yok — dolayısıyla TRT etiketi ancak maç
günü çalışmalarda (06/12/17) düşer. Takım adı eşleşmesi toleranslı (ilk kelimenin
ilk 5 harfi: "bayern munih" ≈ "bayern munchen"). Eşleşme yoksa tabii yazılır;
kazıma hatası çalışmayı durdurmaz. Türkiye Kupası satırı geçersiz (kapsam dışı).

## Çıktı: iki takvim

### `besiktas-<ek>.ics`
Beşiktaş'ın tüm maçları (SL, Kupa, Avrupa). Her etkinlikte alarm var.

### `futbol-<ek>.ics`
SL + PL + ŞL tüm maçlar (Beşiktaş maçları burada da var; iki takvimde aynı UID
kullanılır, iOS iki takvimde ayrı gösterir — kullanıcı istemezse birini kapatır).
Alarm yalnızca **seçili** maçlarda.

### Etkinlik biçimi
- `SUMMARY`: `⚽ Beşiktaş – Galatasaray` (seçili maçlarda başa `🔔` eklenir)
- `DTSTART/DTEND`: maç saati, süre 2 saat, `Europe/Istanbul`
- `LOCATION`: kanal (`TOD`, `TRT 1`, `tabii`)
- `DESCRIPTION`: `Süper Lig · 3. Hafta · TOD` ; maç bitince `Skor: 2-1`
- `UID`: `af-{fixture_id}@futbol-takvim` — sabit, güncellemeler aynı etkinliği değiştirir
- `VALARM`: `alerts_minutes` listesindeki her değer için bir `DISPLAY` alarm
- Takvim başlığı (`X-WR-CALNAME`): `Beşiktaş` / `Futbol`; `REFRESH-INTERVAL` 1 saat

## Seçim kuralları (`watchlist.yml`)

```yaml
teams:                 # bu takımların tüm maçları alarmlı
  - Beşiktaş
matches: []            # tek maç: "Arsenal-Manchester City" (sıra önemsiz)
rules:
  sl_derbies: true     # SL: Beşiktaş/Fenerbahçe/Galatasaray/Trabzonspor birbirleriyle
  pl_big6: true        # PL: Arsenal, Chelsea, Liverpool, Man City, Man Utd, Tottenham birbirleriyle
  cl_from_qf: true     # ŞL: çeyrek final ve sonrası hepsi
  cl_tr_teams: true    # ŞL: Türk takımlarının maçları
  cl_trt: true         # ŞL: TRT'de yayınlanan maç
alerts_minutes: [60, 15]
```

Bir maç şu durumlardan biri sağlanırsa "seçili": takımı `teams`'te, eşleşmesi
`matches`'ta, veya açık bir kurala uyuyor. Takım adı eşleşmesi aksansız ve
küçük harfe indirgenmiş alt-dize (`besiktas`, `man city` gibi kısaltmalar için
küçük bir alias tablosu).

## Hata yönetimi

- Herhangi bir lig için API isteği başarısız ya da boş dönerse script `exit 1`,
  hiçbir `.ics` yazılmaz, eski dosyalar yerinde kalır. Actions e-posta ile
  haber verir. (Kısmi güncelleme yok — basitlik tercih edildi.)
- TRT kazıma hatası: uyarı logu, çalışma devam eder.
- Sezon değişimi: `config.py`'de `SEASON` elle güncellenir (yılda bir).

## Test

- `tests/test_rules.py`: kural motoru — derbi, big6, teams, matches, alias
  eşleşmesi, çeyrek final tespiti.
- `tests/test_ics.py`: örnek fikstür JSON'dan üretilen `.ics`'in UID/alarm/
  kanal/başlık alanları; biten maçta skor.
- API çağrıları kayıtlı JSON fixture'larla mock'lanır; gerçek API testte
  çağrılmaz.

## Kurulum (kullanıcı adımları)

1. api-sports.io ücretsiz hesap → API key → repo Secret `API_FOOTBALL_KEY`.
2. Repo Settings → Pages → branch `main`, klasör `/docs`.
3. Actions'ı elle bir kez çalıştır, `docs/*.ics` oluşsun.
4. iPhone: Ayarlar → Takvim → Hesaplar → Hesap Ekle → Diğer → Abone Olunan Takvim
   Ekle → URL. **"Uyarıları Kaldır" kapalı** olmalı (yoksa alarmlar gelmez).
   İki takvim için iki kez.
5. `watchlist.yml`'ı GitHub iOS uygulamasından düzenle; push sonrası ~2 dk içinde
   `.ics` yenilenir, iPhone bir sonraki yenilemede alır (abonelik yenileme
   sıklığı ayarlardan "Her saat" yapılabilir).

## Repo yapısı

```
futbol-takvim/
  .github/workflows/build.yml
  src/config.py        # lig ID'leri, sezon, kanal tablosu, alias'lar
  src/fetch.py         # API-Football + TRT kazıma
  src/rules.py         # watchlist kuralları
  src/ics.py           # takvim üretimi
  src/generate.py      # giriş noktası
  tests/
  watchlist.yml
  docs/                # Pages: *.ics
  requirements.txt
  README.md
```
