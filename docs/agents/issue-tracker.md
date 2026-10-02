# Issue tracker: GitHub

Bu repo'nun issue'ları ve spec'leri GitHub Issues'da yaşar (`parsiyel/futbol-takvim`). Tüm operasyonlar için `gh` CLI kullanılır.

## Konvansiyonlar

- **Issue oluştur**: `gh issue create --title "..." --body "..."`. Çok satırlı body için heredoc kullan.
- **Issue oku**: `gh issue view <number> --comments` (label'larla birlikte).
- **Issue listele**: `gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'` — `--label` ve `--state` filtreleriyle.
- **Yorum yap**: `gh issue comment <number> --body "..."`
- **Label ekle/çıkar**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **Kapat**: `gh issue close <number> --comment "..."`

Repo otomatik olarak `git remote -v`'den çıkarılır — `gh` clone içinde çalışırken bunu kendisi yapar.

## Triage yüzeyi olarak pull request'ler

**PRs as a request surface: no.** _(Bu repo dışarıdan gelen PR'ları özellik isteği olarak ele alıyorsa `yes` yap; `/triage` bu bayrağı okur.)_

## Bir skill "issue tracker'a publish et" derse

GitHub issue oluştur.

## Bir skill "ilgili ticket'ı çek" derse

`gh issue view <number> --comments` çalıştır.

## Wayfinding operasyonları

`/wayfinder` tarafından kullanılır. **Harita** tek bir issue'dur; **alt** issue'lar ticket'lardır.

- **Harita**: `wayfinder:map` label'lı tek issue; gövdesinde Notlar / Şimdiye kadarki kararlar / Sis bölümleri. `gh issue create --label wayfinder:map`.
- **Alt ticket**: haritaya GitHub sub-issue olarak bağlı issue (`gh api` sub-issues endpoint'i). Sub-issue kapalıysa: haritanın gövdesindeki görev listesine ekle ve alt issue'nun başına `Part of #<harita>` yaz. Label: `wayfinder:<tip>` (`research`/`prototype`/`grilling`/`task`).
- **Engelleme**: GitHub'ın yerel issue bağımlılıkları (`gh api --method POST repos/<owner>/<repo>/issues/<alt>/dependencies/blocked_by -F issue_id=<engelleyenin-db-id'si>`). Yoksa alt issue'nun başına `Blocked by: #<n>` satırı.
- **Sıradaki iş**: haritanın açık alt issue'larından, açık engelleyicisi ve atanmış kişisi olmayan ilki.
- **Sahiplen**: `gh issue edit <n> --add-assignee @me`.
- **Çöz**: `gh issue comment <n> --body "<cevap>"`, sonra `gh issue close <n>`, sonra haritanın "Şimdiye kadarki kararlar" bölümüne bağlam işaretçisi ekle.
