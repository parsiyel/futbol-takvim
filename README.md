# futbol-takvim

Süper Lig, Premier League ve Şampiyonlar Ligi maçlarını iPhone Takvim'ine
düşüren, Beşiktaş ve seçili maçlara alarm koyan `.ics` üreticisi.

- `besiktas-<EK>.ics` — Beşiktaş'ın tüm maçları, hepsi alarmlı
- `futbol-<EK>.ics` — SL + PL + ŞL tamamı; yalnızca `watchlist.yml` kurallarına
  uyan maçlar alarmlı (başlıkta 🔔)

Yayın kanalı etkinliğin "konum" alanında: `TOD`, `tabii`, `TRT 1`.

## Kurulum

1. Repo Secrets: `ICS_SUFFIX` (rastgele kısa ek, URL gizliliği için). API key gerekmez —
   veri [fixturedownload.com](https://fixturedownload.com) feed'inden gelir.
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
teams:                  # bu takımların tüm maçları alarmlı
  - Beşiktaş
matches:                # tek maç, sıra önemsiz
  - "Arsenal-Manchester City"
rules:
  sl_derbies: true      # SL: 4 büyük birbirleriyle
  pl_big6: true         # PL: Big 6 birbirleriyle
  cl_from_qf: true      # ŞL: çeyrek final ve sonrası
  cl_tr_teams: true     # ŞL: Türk takımları
  cl_trt: true          # ŞL: TRT'de yayınlanan maç
alerts_minutes: [60, 15]
```

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
