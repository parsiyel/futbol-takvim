# futbol-takvim

Süper Lig, Premier League ve Şampiyonlar Ligi maçlarını iPhone Takvim'ine
düşüren, Beşiktaş ve seçili maçlara alarm koyan `.ics` üreticisi.

- `besiktas-<EK>.ics` — Beşiktaş'ın tüm maçları (lig, Avrupa, elle girilenler), hepsi alarmlı
- `futbol-<EK>.ics` — SL + PL + ŞL/AL/Konferans, Beşiktaş maçları hariç; yalnızca
  `watchlist.yml` kurallarına uyan maçlar alarmlı (başlıkta 🔔)

Kaynaklar: Süper Lig → **tff.org** (resmi, saatler güncel), diğerleri →
fixturedownload.com feed'leri.

Yayın kanalı etkinliğin "konum" alanında: `TOD`, `tabii`, `TRT 1`.

## Kurulum

1. Repo Secrets: `ICS_SUFFIX` (rastgele kısa ek, URL gizliliği için). API key gerekmez.
2. Settings → Pages → Deploy from branch → `main` / `/docs`.
3. Actions → `build-ics` → Run workflow. `docs/*.ics` oluşur.
4. iPhone: Ayarlar → Takvim → Hesaplar → Hesap Ekle → Diğer → **Abone Olunan
   Takvim Ekle** → URL:
   - `https://parsiyel.github.io/futbol-takvim/besiktas-<EK>.ics`
   - `https://parsiyel.github.io/futbol-takvim/futbol-<EK>.ics`

   **"Uyarıları Kaldır" kapalı** olmalı, yoksa alarmlar gelmez.
   Ayarlar → Takvim → Hesaplar → Yeni Verileri Al → "Her saat" önerilir.

## watchlist.yml

```yaml
besiktas_alerts:        # Beşiktaş takvimi: üç alarm
  morning: "11:00"      # maç günü sabah (TR); maç bundan önceyse atlanır
  minutes: [60, 0]      # 60 dk önce + maç anında

include:                # Futbol takvimine girecek maçlar; lig listede yoksa hepsi girer
  PL: [Hull, Arsenal, Chelsea, Liverpool, Man City, Man Utd, Spurs]

teams: []               # bu takımların tüm maçları alarmlı
matches:                # tek maç, sıra önemsiz
  - "Arsenal-Manchester City"
rules:
  sl_derbies: true      # SL: 4 büyük birbirleriyle
  pl_big6: true         # PL: Big 6 birbirleriyle
  eu_from_qf: true      # ŞL/AL/Konferans: çeyrek final ve sonrası
  eu_tr_teams: true     # Avrupa'da Türk takımları
  eu_trt: true          # TRT 1'de yayınlanan maç
alerts_minutes: [60, 15]

# Feed'lerde olmayan maçlar (Avrupa eleme/play-off turları). Saat TR. Hepsi alarmlı.
manual:
  - date: "2026-08-20 20:00"
    home: Beşiktaş
    away: Kauno Žalgiris
    note: "Avrupa Ligi Play-off, ilk maç"
    channel: TRT 1
```

Feed'ler yalnızca ana aşamaları içerir (ŞL/AL/Konferans lig aşaması + eleme
sonrası). **Eleme ve play-off turları hiçbir feed'de yok** → `manual:` ile gir.

Kısaltmalar çalışır: `man city`, `man utd`, `spurs`, `bjk`, `fb`, `gs`, `ts`.
Dosyayı GitHub uygulamasından düzenleyip push edince takvim ~2 dk içinde yenilenir.

## Çalışma

GitHub Actions günde 4 kez (TR 06/12/17/21) + `watchlist.yml` değişince.
Feed başarısız olursa eski `.ics` dosyaları korunur, Actions e-posta atar.
Şampiyonlar Ligi feed'i (`champions-league-2026`) kura çekimine kadar yok; gelince
otomatik dahil olur. TRT 1 etiketi yalnızca maç günü düşer (TRT sitesi ileri
tarihli yayın akışı vermiyor). Sezon değişince `src/config.py` → `SEASON`.

## Lokal

```bash
python -m venv .venv && .venv/Scripts/pip install -r requirements.txt
.venv/Scripts/pytest
ICS_SUFFIX=deneme python -m src.generate
```
