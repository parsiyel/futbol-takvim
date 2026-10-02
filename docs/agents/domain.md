# Domain Docs

Engineering skill'leri kod tabanını keşfederken bu repo'nun domain dokümantasyonunu nasıl tüketmeli.

## Keşfe başlamadan önce oku

- Repo kökündeki **`CONTEXT.md`**
- **`docs/adr/`**: çalışacağın alana dokunan ADR'leri oku.

Bu dosyalar yoksa **sessizce devam et**. Yokluklarını bildirme, baştan oluşturmayı önerme. `/domain-modeling` skill'i (`/grill-with-docs` ve `/improve-codebase-architecture` üzerinden) terimler veya kararlar gerçekten netleştiğinde bunları tembel şekilde oluşturur.

## Dosya yapısı

Single-context repo:

```
/
├── CONTEXT.md
├── docs/adr/
│   ├── 0001-ornek-karar.md
│   └── 0002-baska-karar.md
└── src/
```

## Sözlükteki kelime dağarcığını kullan

Çıktın bir domain kavramını adlandırıyorsa (issue başlığı, refactor önerisi, hipotez, test adı), terimi `CONTEXT.md`'de tanımlandığı gibi kullan. Sözlüğün açıkça kaçındığı eş anlamlılara kayma.

İhtiyacın olan kavram sözlükte yoksa bu bir sinyaldir: ya projenin kullanmadığı bir dil uyduruyorsun (yeniden düşün) ya da gerçek bir boşluk var (`/domain-modeling` için not et).

## ADR çelişkilerini işaretle

Çıktın mevcut bir ADR ile çelişiyorsa sessizce geçersiz kılma, açıkça belirt:

> _ADR-0007 ile çelişiyor, ama yeniden açmaya değer çünkü…_

## ADR ne zaman yazılır

Yalnızca üçü birden doğruysa: **geri dönüşü zor**, **bağlamsız okununca şaşırtıcı**, **gerçek bir ödünleşimin sonucu**. İlerleme kaydı ADR değildir; "nerede kaldık" bilgisi issue'larda durur.
