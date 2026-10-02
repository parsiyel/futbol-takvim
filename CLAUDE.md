# CLAUDE.md — futbol-takvim

Süper Lig, Premier League ve UEFA kupası maçlarını iPhone Takvim'e abone olunabilir `.ics` olarak üretir; Beşiktaş maçlarına ve `watchlist.yml` kurallarına uyan maçlara alarm koyar. Kurulum, `watchlist.yml` biçimi ve çalışma ayrıntısı [`README.md`](./README.md) içinde.

## Önce bil

- **Üretim GitHub Actions'ta koşar** (`.github/workflows/build.yml`): zamanlanmış olarak ve `watchlist.yml`, `src/**` ya da workflow dosyası değişince. `futbol-bot` `docs/*.ics` dosyalarını `main`'e commit'ler; yerel `main` bu yüzden çoğu zaman geridedir.
- **Bu yollara dokunan push yayındır:** workflow testleri koşar, `.ics` dosyalarını yeniden üretir ve takvim yenilenir.
- **Yayın GitHub Pages'tedir** (`main` / `/docs`). `docs/` altındaki her dosya sitede sunulur.
- **`docs/*.ics` çıktıdır**, elle düzenlenmez; bot üzerine yazar.
- Dosya adındaki ek `ICS_SUFFIX` secret'ından gelir. API anahtarı gerekmez.

## Yapı

- `src/` — `config.py` (sezon, feed'ler, takım adları), `fetch.py`, `model.py`, `rules.py` (watchlist kuralları), `ics.py`, `generate.py` (giriş: `python -m src.generate`)
- `tests/` — pytest; `tests/fixtures/` kayıtlı kaynak örnekleri
- `watchlist.yml` — alarm kuralları ve elle girilen maçlar
- `docs/` — yayınlanan `.ics` dosyaları; `docs/superpowers/` tasarım ve plan

## Kurallar

1. Doğrulama: `.venv/Scripts/pytest` yeşil olmalı. Workflow da üretimden önce testleri koşar; test kırmızıysa takvim güncellenmez.
2. Sezon değişince `src/config.py` → `SEASON`.
3. Türkçe yaz; kod tanımlayıcıları İngilizce.

## Proje haritası

Bu repo `yigit-hub` ağacının bir parçasıdır: https://github.com/parsiyel/yigit-hub (`PROJECTS.md`).
İlişkili projeler: yok (bağımsız kişisel araç).

## Çalışma döngüsü

Süreklilik oturum geçmişinde değil, bu repoda ve GitHub'da durur. Her makinede aynı döngü:

**Oturum başında**

1. `git pull --ff-only` (bot arada commit atmıştır)
2. `gh issue list --state open` ile açık işleri oku. `ready-for-agent` etiketliler doğrudan yapılabilir.
3. Varsa `CONTEXT.md` ve çalışılacak alana dokunan `docs/adr/` kayıtlarını oku.

**İş bitince**

1. İlgili issue'yu kapat (`gh issue close <n> --comment "ne yapıldı"`); bitmediyse nerede kalındığını issue'ya yorum olarak yaz.
2. Ortaya çıkan yeni işler için issue aç.
3. Karar üç koşulu birden sağlıyorsa (geri dönüşü zor, bağlamsız şaşırtıcı, gerçek ödünleşim) `docs/adr/NNNN-baslik.md` yaz. Sağlamıyorsa yazma.
4. Yeni ya da netleşen terim varsa `CONTEXT.md`'yi güncelle.
5. Commit ve push. Push edilmemiş iş diğer makinede yoktur.

## Agent skills

### Issue tracker

Issue'lar GitHub Issues'da yaşar (`parsiyel/futbol-takvim`, `gh` CLI). Bkz. `docs/agents/issue-tracker.md`.

### Triage labels

5 kanonik rol varsayılan string'leriyle kullanılır (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). Bkz. `docs/agents/triage-labels.md`.

### Domain docs

Single-context: repo kökünde `CONTEXT.md` ve `docs/adr/`. Bkz. `docs/agents/domain.md`.
