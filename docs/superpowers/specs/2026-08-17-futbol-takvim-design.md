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

- **Repo:** GitHub `futbol-takvim` (private). GitHub Pages `docs/` klasöründen
  yayınlar; iPhone `https://<user>.github.io/futbol-takvim/<dosya>.ics` adresine
  abone olur. Dosya adlarına tahmin edilemez bir ek eklenir (ör.
  `futbol-a8f3.ics`) — Pages public olduğundan basit gizlilik.
- **Çalışma:** GitHub Actions cron günde 4 kez (TR 06:00, 12:00, 17:00, 21:00)
  + `watchlist.yml` push'unda + elle tetikleme. Üretilen `.ics` değiştiyse
  bot commit atar.
- **Dil/kütüphane:** Python 3.12, `requests`, `icalendar`, `pyyaml`.
- **Sırlar:** `API_FOOTBALL_KEY` GitHub Secret.

## Veri kaynağı

API-Football (api-sports.io) ücretsiz plan, 100 istek/gün. Kullanılan uç:
`GET /fixtures?league={id}&season={yıl}` — lig başına tek istek, sezonun tüm
fikstürü. Günde 4 çalışma × 4 lig = 16 istek.

Lig ID'leri (API-Football): Süper Lig 203, Premier League 39, Şampiyonlar Ligi 2,
Türkiye Kupası 206. Sezon: `2026`.

Risk: ücretsiz planın mevcut sezonu kapsadığı ilk çalışmada doğrulanacak;
kapsamıyorsa yedek football-data.org (SL hariç) + TFF kazıma değerlendirilir.

### Kanal bilgisi

API'de yok, kural ile eklenir:

| Lig | Kanal |
|---|---|
| Süper Lig | TOD |
| Premier League | TOD |
| Şampiyonlar Ligi | tabii; TRT'nin haftalık maçı ise `TRT 1` |
| Türkiye Kupası | A Spor / TOD (best-effort) |

TRT maçı: `https://www.trt1.com.tr/yayin-akisi` günlük sayfasından "Şampiyonlar
Ligi" içeren satırların saat + takım adı eşleşmesi. Eşleşme bulunamazsa sessizce
tabii yazılır; kazıma hatası çalışmayı durdurmaz.

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
