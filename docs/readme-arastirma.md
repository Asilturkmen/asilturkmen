# GitHub Profil README'si — Araştırma Raporu

**Tarih:** 22 Ekim 2026 · **Hazırlayan:** Claude (Fable 5.1); üç paralel araştırma kolunun (teknik sınırlar, örnekler, araçlar) birleşimi · **Amaç:** github.com/Asilturkmen profiline giren kişiye "vay be" dedirtecek, klişe olmayan bir README için sağlam zemin.

Doğrulama yöntemi: GitHub Markdown API'ye deneme HTML'i gönderilip neyin budandığı ölçüldü; canlı profil sayfalarının HTML/CSS'i indirilip incelendi; 35+ popüler profil README'si tarandı; örnek repoların ham README/SVG/workflow dosyaları okundu; araçların son push tarihi ve hosted servislerin HTTP durumu kontrol edildi. "Doğrulanmadı" yazan her şey okunmadı/ölçülmedi demektir, uydurma değil.

---

## 0. Kısa özet

1. **GitHub README'de CSS ve JavaScript yok.** Görsel gücün tek gerçek aracı, **repoda duran, elle ya da kodla üretilmiş animasyonlu SVG** (SMIL `<animate>` veya SVG içi CSS `@keyframes`). SVG içinde hover, tıklama, script ve dış font çalışmaz; font ya base64 gömülür ya da yazı path'e çevrilir.
2. **"Vay be" etkisini araç değil dört şey yaratıyor:** (a) tek elden, tutarlı bir görsel dil; (b) gerçek veri + anlatı (sayı değil metafor); (c) canlı hissi (bugünün tarihi, zamana/ortama tepki); (d) ziyaretçinin dokunabildiği bir şey. İstatistik kartı bunların hiçbirini vermiyor; haklıydın.
3. **2026 profil klişesi tam olarak mevcut README:** capsule-render dalga + readme-typing-svg + `for-the-badge` rozet duvarı + `const asil = {...}` + ziyaretçi sayacı + "Thanks for visiting 🚀". Yenisinde hiçbiri olmayacak.
4. **Hazır bir Claude skill'i / plugin'i / MCP'si yok.** İşe yarayan zincir: Python `drawsvg` (SMIL), `fontTools`/`opentype.js` (yazı → path), `svgo` (güvenli ayarla), `<picture>` ile tema + mobil + hareket-azaltma varyantları. Claude bunları doğrudan kullanabilir; skill gerekmiyor.
5. **En taze fikirler 0–15 yıldızlı, 2026 tarihli repolarda;** topluluk listelerine girmemiş. Yani "henüz kimsenin görmediği" alan geniş.
6. **Önerim: "Constellation" konsepti** (bkz. §6). Sitenin parçacık-ağı dilini README'ye taşıyan tek bir elle yazılmış SVG hero (adın Satoshi'den path'e çevrilmiş; yüzün ya da bir sahne, parçacık ağından örülmüş; SMIL ile nefes alan ışık), altında sitenin içerik JSON'undan **otomatik üretilen** tutarlı proje kartları ve bugünün tarihini taşıyan bir "şu an" satırı. Faz 2'de Kıbrıs saatine/havasına tepki veren sahne; Faz 3'te isteğe bağlı oynanabilir öğe.

---

## 1. Oyun alanı: GitHub neyi render ediyor, neyi budiyor

### 1.1 HTML ve Markdown

| Öğe | Durum | Not |
|---|---|---|
| `align`, `width`, `height`, `valign` (img/table/td/p/div/h1) | ✅ | Elimizdeki tek "CSS". `height` verince GitHub oranı koruyan `max-height` ekliyor. |
| `style`, `class`, `id` (özel), `data-*`, `hidden`, `loading` | ❌ | Hepsi budanıyor. `id`/`name` çapaları `user-content-` öneki alır ama `#id` linkleri çalışır. |
| `<details>` / `<summary>` (+`open`) | ✅ | Akordeon bölümler. İçine kod bloğu konabilir. |
| `<picture>` + `<source media srcset>` | ✅ | Resmî (Changelog 2022-05). GitHub `<themed-picture>` ile sarıyor. Tema, mobil ve reduced-motion varyantlarının tek güvenilir yolu. |
| `<table>` (iç içe dahil), `td width/colspan/rowspan` | ✅ | Çok sütunlu yerleşimin tek yolu. **Mobilde sarmaz, yatay kaydırır.** |
| `<img align="right">` ile metin sarma | ✅ | GitHub otomatik 20px padding ekliyor. |
| `<a href><img></a>` | ✅ | Tıklanabilir görsel. Sarmadığın her görseli GitHub kendisi `<a target=_blank>` ile sarar. |
| `<kbd> <sup> <sub> <samp> <ins> <del> <mark> <ruby> <dl> <br> <hr>` | ✅ | |
| `<center> <font> <marquee> <small> <abbr> <u> <figure>` | ❌ | Etiket silinir, metin kalır. |
| `<video> <audio> <iframe> <script> <style> inline <svg> <canvas>` | ❌ | Elle yazılanlar tamamen silinir. |
| HTML yorumları `<!-- -->` | ✅ | Çıktıdan silinir; güvenli not alanı / Action işaretçisi. |
| Mermaid | ✅ | mermaid 12.2; flowchart, sequence, gitGraph, timeline, mindmap, pie, sankey, xychart, radar, treemap vb. **Temayı izliyor** (koyu temada `dark`). Koyu temada açık dolgulu düğümlerde kontrast sorunu bildirilmiş. |
| LaTeX math, Alerts (`> [!NOTE]`), dipnot, görev listesi, emoji | ✅ | Repo README'de canlı doğrulandı; profil README'si aynı pipeline (profilde canlı örnek bulunmadı). |
| Renk çipleri `` `#0969DA` `` | ❌ | Yalnız issue/PR/discussion. |
| Video (yüklenmiş .mp4/.mov, `user-attachments` bare URL) | ⚠️ | Oynatıcıya dönüşür ama **`controls+muted`, autoplay/loop yok**; Free'de 10 MB; dış host yok. Profilde canlı örnek yok. Sinematik otomatik hareket istiyorsan video değil SVG. |

### 1.2 Görseller, camo ve SVG

- Dış görseller **camo** proxy'sinden geçer (`camo.githubusercontent.com/<hmac>/<hex>`); hex, query string dahil URL'nin tamamıdır → `?v=2` eklemek yeni önbellek anahtarı demektir (cache-busting fiilen çalışır). Camo, origin'in `Cache-Control`'unu aynen geçirir; başlık yoksa varsayılan **1 yıl**. Son çare: `curl -X PURGE <camo-url>`.
- **Relative path (`./assets/x.svg`) profilde çalışır** ve camo'ya girmez (anuraghazra/codeSTACKr profillerinde canlı doğrulandı). `*.githubusercontent.com` de camo'ya girmez. → Her şeyi kendi repomuzda tutmak hem hızlı hem güvenli.
- **`<img>` içindeki SVG = SVG2 "secure animated mode":** SMIL ✅, SVG içi `<style>` + `@keyframes` ✅, `<script>` ❌, dış font/görsel ❌ (data URI ile gömülü ✅), `:hover` / tıklama / SVG içi `<a>` ❌, `<foreignObject>` ⚠️ (tarayıcıya göre değişken; gerek yok, kullanma). Camo'dan dönen SVG'nin CSP'si: `default-src 'none'; img-src data:; style-src 'unsafe-inline'`.
- Tarayıcı tuzakları (topluluk raporları): Safari/iOS'ta img-SVG içindeki **CSS animasyonları bazen başlamıyor → SMIL tercih et**; Firefox'ta SVG içine base64 gömülü **raster** görsellerin animasyonu çalışmıyor (`github/markup#1864`, "not planned"). Yani piksel-art sprite tekniği Firefox'ta riskli; vektör SMIL her yerde çalışıyor.
- **GIF:** oynar, ama GitHub `<animated-image>` oynatıcısıyla sarar ve kullanıcı Ayarlar → Accessibility → Motion'dan **otomatik oynatmayı kapatabilir** (varsayılan: sistemin reduce-motion ayarını izler). 10 MB sınırı. → Ana animasyon için GIF'e güvenme; SVG kullan. Animasyonlu WebP/APNG: tarayıcı oynatır, GitHub'a özgü doğrulama yapılamadı.
- Boyut: camo açık kaynak varsayılanı 5 MB (GitHub prod değeri doğrulanmadı). Pratik hedef: SVG ≤ ~300 KB, GIF ≤ 2–3 MB.

### 1.3 Tema

- `<picture>` + `<source media="(prefers-color-scheme: dark)">` → resmî, güvenilir yol.
- `#gh-dark-mode-only` / `#gh-light-mode-only` hâlâ CSS'te var ama **`href`e bakıyor, `src`ye değil**: dış (camo'lu) görselde yalnız `src`ye eklersen çalışmaz; görseli `<a href="...#gh-dark-mode-only">` ile sararsan çalışır. Repo içi görselde GitHub'ın otomatik sarmalayıcısı fragment'ı taşıdığı için çalışır.
- SVG içinde `@media (prefers-color-scheme)`: tarayıcı/OS şemasına göre değerlenir, **GitHub'ın elle seçilmiş temasına göre değil** → kullanıcı GitHub'da koyu tema seçip OS'u açıkta tutuyorsa uyumsuzluk. Güvenli yol: iki ayrı dosya + `<picture>`.
- `prefers-reduced-motion`: `<picture>` seviyesinde `<source media="(prefers-reduced-motion: reduce)" srcset="hero-still.svg">` çalışıyor (skulitom profilinde kullanımda); SVG içinde çalışıp çalışmadığı konusunda raporlar çelişiyor → `<picture>` yolunu kullan.

### 1.4 Profil sayfası ölçüleri (canlı HTML/CSS'ten)

- Sayfa `container-xl` (max 1280px); sol sidebar (avatar) ≥1012px'te 296px; README kutusu 24px padding.
- **README içerik genişliği:** ≥1280px ekranda **~846px**; 1100px'te ~666px; 900px'te ~530px; **390px telefonda ~308px**.
- Profil README metni **14px** (`f5` sınıfı; repo README'de 16px). Görseller ve tablolar buna göre küçük tasarlanmalı.
- Mobilde (<768px) tek sütun: avatar üstte, README altta; tablolar yatay kaydırır.
- Profil sayfasında "Outline"/TOC yok; README kutusu "Pinned" repolardan önce gelir (en fazla 6 pinned, 2 sütun).

### 1.5 2025–2026 Changelog

Profil README'sini doğrudan etkileyen yeni bir özellik yok. Yakın: `gh --attach` ile medya yükleme (2026-09), PR "Files changed"de markdown/SVG zengin önizleme (2025-07).

---

## 2. İnsanlar ne yapmış — en iyi örnekler ve mekanizmaları

Filtre: yalnız istatistik kartıyla "etkileyici" görünen profiller listede yok.

### 2.1 Oynanabilir / etkileşimli README'ler

Mekanizma hep aynı: önceden doldurulmuş `issues/new?title=...` linki → `on: issues: opened` workflow → script README'yi yeniden yazar, issue'yu kapatır. Tamamen GitHub içi, dış bağımlılık yok.

| Profil | Ne var | Durum (2026-10-22) | Yeniden üretim |
|---|---|---|---|
| [timburgan](https://github.com/timburgan) | Herkese açık topluluk satrancı; tahta tablo içinde PNG kareler, geçerli hamle linkleri; `concurrency` ile yarış koşulu çözümü (Ruby + octokit) | **Aktif**, bugün issue kapatılmış, 45 bin+ hamle, 1.186★ | 6–12 saat |
| [JonathanGin52](https://github.com/JonathanGin52) | Connect Four; bota karşı da oynanıyor; 20 bin hamle / 2.189 oyuncu | Aktif (dün), 253★ | 6–10 saat |
| [rossjrw](https://github.com/rossjrw) | 5.000 yıllık **Royal Game of Ur**; takımlar, zar, oyun günlüğü `<details>` içinde, tahta SVG | Aktif (bugün), 206★ | 15–25 saat |
| [benjaminsampica](https://github.com/benjaminsampica) | "Roll for initiative": sınıf seç → zar at; dağılım tablosu | Aktif, 81★ | **2–3 saat** (en ucuz etkileşim) |
| [agonyz](https://github.com/agonyz) | Mayın tarlası + skor tablosu; ayrıca readme-blackjack | Aktif, 5★ | 6–10 saat |
| [joelbaldapan](https://github.com/joelbaldapan) | 2048; tahta SVG, ok tuşu linkleri, top 5 | 2026-09, 2★ | 4–8 saat |
| [aryan02420](https://github.com/aryan02420) | Wordle (`<details>` içinde); oyun durumu README'deki HTML yorumunda saklı | 2026-07, doğrulanmadı | 6–10 saat |
| [0-draft/shogi](https://github.com/0-draft/shogi) | Shogi; 81 linkli taş; seçili taş için ikinci görsel seti (CSS yasak diye) — [dev.to yazısı](https://dev.to/kanywst/lets-play-shogi-i-turned-my-github-profile-readme-into-a-playable-board-333c) | Aktif, az oynanıyor | 10–15 saat |
| [kylepls](https://github.com/kylepls) | **Sıfır backend** tic-tac-toe: 138 KB Markdown, her tahta durumu bir `<a name>` bölümü, hücreler `#çapa` linki | Statik, bozulmaz, 87★ | 2–3 saat (üretici script) |
| [JessicaLim8](https://github.com/JessicaLim8) → [trinib](https://github.com/trinib) | Topluluk kelime bulutu: "Add a word" issue → yeni PNG | trinib aktif (511★) | 3–5 saat |
| [DoubleGremlin181](https://github.com/DoubleGremlin181) | Oylamalı tic-tac-toe (hücre = oy, saat başı en çok oy oynanır) | linkly.link'e bağımlı, 3 aydır hareket yok | — |
| [HFO4](https://github.com/HFO4) | README'den Pokémon (Game Boy) oynatma; kendi emülatör sunucusu | **Sunucu ölü** | — |

Bulunamayanlar: "ortak hikâye / sonraki cümleyi sen yaz" README'si; issue+Actions tabanlı Pokémon. Bu boşluklar §6'da.

### 2.2 Kendini güncelleyen README'ler

| Profil | Ne var | Mekanizma | Durum |
|---|---|---|---|
| [simonw](https://github.com/simonw) | 3 sütun: son sürümler / blog / TIL; hepsi **bugün tarihli** ([yazısı](https://simonwillison.net/2020/Jul/10/self-updating-profile-readme/)) | Python + GraphQL + RSS; `<!-- x starts -->` işaretçileri arası yeniden yazılır | Aktif, 448★ |
| [tw93](https://github.com/tw93) | Aynı kalıbın tasarımlı hâli | Aynı | Aktif, 254★ |
| [prsdx/YourTomo](https://github.com/prsdx/YourTomo) | **Profil evcil hayvanı**: piksel kedi; günün saatine göre selam, gündüz/gece gökyüzü **senin yerel saatine göre**, 3+ günlük streak'te kamp ateşi, CI düşünce "overheat", 00–06 uyuyor | TS, deterministik, 6 saatte bir cron, `<picture>` | Aktif (bugün), 14★ |
| [yuki4266/living-scene](https://github.com/yuki4266/living-scene) | **Hava + saat senkronlu SMIL banner** (6 hava × gece/gündüz), mevsimlik altlık; Open-Meteo (anahtar yok), saf Python, ~3 saatte bir, değişince commit | Action + commit (camo sorununu aşar) | Aktif, 3★ (yazar profili 31★) |
| [SandeepKomal/Git3D-Universe](https://github.com/SandeepKomal/Git3D-Universe) | Saat başı çalışıp 06–18 `daylight`, gece `aurora` teması | Node, GraphQL | Aktif, 3★ |
| [thmsgbrt](https://github.com/thmsgbrt) | Günün saatine göre selam, Stockholm hava + gün doğumu/batımı, Instagram fotoğrafları | Node + Mustache + OpenWeatherMap + **Puppeteer kazıma** | **Durmuş** (Mart 2025; kazıma kırılmış), 541★ — ders: kazımaya dayanma |
| [natemoo-re](https://github.com/natemoo-re) / [novatorem](https://github.com/novatorem) | Spotify "now playing" | Kendi serverless uç → SVG | Aktif ama Spotify 2026 Dev Mode kısıtları (Premium şartı, 5 kullanıcı; kısmen doğrulanmadı) |
| [andyruwruw](https://github.com/andyruwruw) | Müzik çubukları şarkının energy/danceability'sine göre renkleniyor | Kendi API (React → SVG) | **Statiğe çevrilmiş** (2023) — dış servis yorgunluğu |
| [swyxio](https://github.com/swyxio) | Gerçek "son takipçiler" avatar şeridi | Action → avatar URL'leri | Aktif, 147★ |

### 2.3 Elle yapılmış animasyonlu SVG (en "tasarımcı" örnekler)

| Profil | Ne var | Nasıl | Durum |
|---|---|---|---|
| [brenocq](https://github.com/brenocq) | **Tamamen SVG profil:** animasyonlu isim, "about" satırlarında küçük animasyonlu ikonlar, **her proje için üretilmiş animasyonlu repo kartı** (SVG içinde `prefers-color-scheme`) — [HN](https://news.ycombinator.com/item?id=43504961) | Python scriptleri (`animated_text`, `icons`, `project_cards`), günlük Action, orphan dala push | Aktif, 7★ (az yıldız, en tutarlı dil) |
| [skulitom](https://github.com/skulitom) | **Piksel-art sahne** (ay ışığında kaynayan şişe, buhar), 72 karelik sprite; **mobil ve reduced-motion sürümleri `<picture>` ile**; proje linkleri de animasyonlu SVG butonlar — [dev.to (Eki 2026)](https://dev.to/rivskiy_skulitom_af400ad1/how-to-put-crisp-animated-pixel-art-in-a-github-profile-readme-1cpd) | Sprite PNG base64 SVG içinde, CSS `step-end` | Aktif, 0★ |
| [AVIVASHISHTA29](https://github.com/AVIVASHISHTA29) | Terminal: `whoami` → **satır satır beliren ASCII portre** (123 `<animate>`), neofetch kartı, hücre hücre açılan ısı haritası — [yazısı (Tem 2026)](https://avivashishta.com/blog/build-animated-github-profile-readme.html) | Python (OpenCV → parlaklık rampası → SMIL) | Aktif, 78★ |
| [yoshi389111](https://github.com/yoshi389111) | "HELLO" harfleri tuş vuruşu gibi çarpıyor; kendi aracı [power-hello](https://github.com/yoshi389111/power-hello) | CLI → SMIL | Aktif |
| [Andrew6rant](https://github.com/Andrew6rant) | README tek SVG: ASCII portre + neofetch; **"Uptime: 22 yıl 5 ay"** = yaş | GraphQL, light/dark iki SVG | Güncelleme durmuş (Mart 2025), 975★ |
| [jh3y](https://github.com/jh3y) | Yalnız dönen bir mücevher SVG'si (8 KB) ve link | Elle SVG + CSS | Aktif, 85★ — "az ama kusursuz" |
| [kanywst](https://github.com/kanywst) | Tek animasyonlu "kt" logosu (721 bayt) | Elle | Aktif |
| [lennystepn-hue/attract-mode](https://github.com/lennystepn-hue/attract-mode) | **Arcade kabini profili**: player card, loadout, "select your game" proje kabinleri; elle yapılmış 5×7 bitmap font; "her sayı gerçek, her gece yeniden çizilir" | Node stdlib, nightly | 2026, 0★ |
| [OthmanAdi/commit-fm](https://github.com/OthmanAdi/commit-fm) | "Now playing" ama Spotify değil **repoların**: 7 retro skin (split-flap pano, Winamp, VU metre, vinil…); AI ajanı yayına not bırakabiliyor | Node stdlib | 2026, 0★ |

Gözlem: etkileyici SVG'lerin **hemen hepsi kodla üretilmiş** (Python/TS), Figma/SVGator değil. Çizilen imza (`stroke-dashoffset`) animasyonlu bir profil örneği **bulunamadı** — teknik çalışıyor, alan boş.

### 2.4 Terminal / neofetch / ASCII

Andrew6rant (referans), AVIVASHISHTA29 (animasyonlu), [orangekame3/ghfetch](https://github.com/orangekame3/ghfetch) (Go CLI → GIF), [GitAscii](https://gitascii.com) (hosted, avatarı ASCII'ye çevirir; servis bağımlılığı). Hareket eklenmezse 2026'da düz duruyor.

### 2.5 README'yi mini site gibi kuranlar

- brenocq: otomatik üretilen proje kartları, 2×N grid.
- skulitom: iki sütunlu `<table>`, her proje için SVG kart, mobil/reduced-motion varyantları (bunların üçünü birden yapan tek profil).
- [DenverCoder1](https://github.com/DenverCoder1): thumbnail'li **SVG YouTube kartları** kendi Action'ıyla; 7 `<details>` bölümü.
- simonw/tw93: `<table><td valign=top width=33%>` çok sütun.
- [wildanniam/GitHub-Profile-Console](https://github.com/wildanniam/GitHub-Profile-Console) (63★): şeffaf portre PNG → animasyonlu ASCII hero, desktop/mobil × dark/light, PROMPT.md ile Claude Code'a kişiselleştirtme, hash'li dosya adıyla cache kırma. Şablon hissi var ama mühendisliği öğretici.

### 2.6 2024–2026 yeni fikirler

| Proje | Fikir | Durum |
|---|---|---|
| [flycran/github-gravity](https://github.com/flycran/github-gravity) | Katkı kareleri yerçekimiyle düşüp **özel metne (adına) çarpıyor**; yörüngeler SVG'ye gömülü | 2026-07, 4★ |
| [egorthinks/git-bonsai](https://github.com/egorthinks/git-bonsai) | Hesap geçmişinden deterministik piksel-bonsai (SVG + rüzgâr GIF), mevsim seçimi | 2026-07, 18★ |
| [0xharkirat/dither-portrait](https://github.com/0xharkirat/dither-portrait) | Fotoğraftan 1-bit Floyd–Steinberg dither'lı **animasyonlu SVG portre** (grain dalgalanır, yüz sabit; dark/light; reduced-motion'da durur) | 2026-07, 2★ |
| [kimjusnu/readme_portrait](https://github.com/kimjusnu/readme_portrait) | Renkli ASCII portre, satırlar SMIL clip-rect ile "yazılır" | 2026, 2★ |
| [kiaquila/comet-contribution-graph](https://github.com/kiaquila/comet-contribution-graph) | Yıl 7 halka hâlinde "güneş", kuyruklu yıldız en verimli günlerden geçiyor; SMIL | 2026-10, 12★ |
| [Dasmat13/git-world-action](https://github.com/Dasmat13/git-world-action) | "GitWorld": repolar şehir, commit'ler bina, issue'lar canavar, PR'lar boss — [dev.to](https://dev.to/dasmat13/i-built-gitworld-engine-a-github-action-that-turns-your-contributions-into-an-animated-city-302) | 2026-10, 5★ |
| [abozanona/pacman-contribution-graph](https://github.com/abozanona/pacman-contribution-graph) | Pac-Man katkı grafiğini yiyor; profilinde Breakout, Galaga, Puzzle Bobble varyantları | 221★ |
| [yoshi389111/github-profile-3d-contrib](https://github.com/yoshi389111/github-profile-3d-contrib) | İzometrik 3D katkı takvimi | 1.784★ (yaygınlaşıyor) |
| [7csc/github-readme-3d-canvas](https://github.com/7csc/github-readme-3d-canvas) | three.js sahnesini headless Chrome'da render edip GIF/APNG commit | 2026-10, 0★ |
| [profile-readme/local-time-profile-clock](https://github.com/profile-readme/local-time-profile-clock) | Script'siz tıkır tıkır saat (sunucu o anki saati çizer, basamaklar CSS ile kayar) | Demo sunucu "her an kapanabilir" |
| Mermaid | GitHub `gitGraph`, `timeline`, `mindmap` render ediyor ama **yaratıcı kullanan tek profil bulunamadı** | boş alan |

Katkı grafiği oyunları (yılan → pacman → breakout → Game of Life → kuyruklu yıldız → şehir) türü doygun; aynı veriye yeni metafor bulmak gerekiyor.

---

## 3. "Vay be" etkisinin anatomisi (örneklere dayanarak)

1. **Ziyaretçi bir şey yapabiliyor ve README değişiyor.** timburgan'da 45 bin, JonathanGin52'de 20 bin hamle: etkileşim = paylaşılma. Oyun karmaşık olmak zorunda değil (benjaminsampica'nın zarı 3 saatlik iş, 81★).
2. **Gerçek veri + anlatı.** YourTomo'nun kedisi CI düşünce "overheat" oluyor; Andrew6rant yaşını "Uptime" yazıyor; GitWorld issue'ları canavar yapıyor. Sayı aynı sayı; **metafor** vay dedirtiyor. Stat kartı bunun tam tersi: veri var, anlatı yok.
3. **Canlı hissi: tarih damgası ve zamana tepki.** "2026-10-22" gören ziyaretçi güveniyor; YourTomo/living-scene gündüz-gece; skulitom mobil/reduced-motion → "bu beni fark etti" hissi. (Durunca hemen belli oluyor: thmsgbrt ve Andrew6rant Mart 2025'te takılı kalmış, ters etki.)
4. **Tek dilde, tek elden tasarım.** brenocq, skulitom, attract-mode, commit-fm: her kart aynı palet/font/hareket dili; **hiçbirinde rozet yığını yok**. Vay etkisi "çok şey" değil, "tutarlı şey".
5. **Hareket SVG'nin içinde, GitHub'ın dışında değil.** Kalıcı olanların hepsi repoya commit'lenmiş SMIL/CSS SVG; dış servise bağlı olanlar (HFO4, andyruwruw, thmsgbrt) ya öldü ya statikleşti. **Kalıcılık = etkileyicilik.**
6. **Kendi aracını yazıp "nasıl çalışıyor" linki koymak** profilin yıldız kaynağı (simonw, joelbaldapan, AVIVASHISHTA29; Andrew6rant 451 fork).
7. **Terminal estetiği + kişisel veri** hâlâ işliyor çünkü geliştirici kimliğiyle örtüşüyor; ama hareket eklenmezse düz.
8. **Az ama kusursuz** da bir strateji: jh3y'nin tek mücevheri, kanywst'in 721 baytlık logosu.

---

## 4. Araçlar

Puan = özgün, klişe olmayan tasarım için uygunluk (1–5).

### 4.1 Hosted SVG üreticileri (neden kullanmıyoruz)

| Araç | Durum | Puan | Not |
|---|---|---|---|
| [capsule-render](https://github.com/kyechan99/capsule-render) | Aktif, 1.845★, Vercel | 2 | Mevcut README'deki dalga. Font gömmüyor (sistem fontuna düşer), "best-effort" servis, en klişe öğe. |
| [readme-typing-svg](https://github.com/DenverCoder1/readme-typing-svg) | Aktif, 9.456★ | 2 | Google Fonts'u base64 gömüyor (tek iyi tarafı); "typing header" 2026'da klişe. Kendi SMIL typewriter'ımız daha özgün. |
| [svg-banners](https://github.com/Akshay090/svg-banners) | 2020'den beri bakımsız | 1 | Yalnız kaynak okumak için. |
| [github-profile-header-generator](https://github.com/leviarista/github-profile-header-generator) | Aktif, 1.364★ | 2 | Statik PNG, şablon görünümlü. |
| [terminal-identity](https://github.com/doyoon530/terminal-identity), [terminal-shields](https://github.com/seuthootDev/terminal-shields), [ProfileKit](https://github.com/heznpc/ProfileKit) | 2026, çok yeni, hosted | 3 | Az kullanılmış ama Vercel bağımlılığı; hazır kart estetiği. |
| Dalga/blob üreticileri: haikei.app, getwaves.io, blobmaker.app, fffuel.co | Canlı | 3 | Yalnız hammadde (statik şekil → sonra elle animasyon). |
| [vivus-instant](https://maxwellito.github.io/vivus-instant/), svgartista.net | Canlı | 3 | Logo/imza "çizdirme" (stroke) animasyonu için JS'siz hızlı yol. |

Ortak risk: Vercel/Heroku uçları tek nokta arıza + hız sınırı + camo önbelleği. **Gösterilecek şeyi Action ile kendi repomuzda üretmek** her durumda daha sağlam.

### 4.2 GitHub Actions ile üreten araçlar (yaratıcı olanlar)

| Araç | Ne yapar | Durum | Puan |
|---|---|---|---|
| [living-scene](https://github.com/yuki4266/living-scene) | Hava + saat senkronlu SMIL banner; Open-Meteo (anahtar yok); template repo | 2026, 3★ | **5** — "günün saatine göre sahne" talebinin en temiz çözümü |
| [dither-portrait](https://github.com/0xharkirat/dither-portrait) | Fotoğraftan animasyonlu 1-bit SVG portre; dark/light; Action/CLI | 2026, 2★ | **5** — kişiye özel ve zarif |
| [github-gravity](https://github.com/flycran/github-gravity) | Katkı kareleri adına çarpıyor (fizik) | 2026, 4★ | 4 |
| [git-bonsai](https://github.com/egorthinks/git-bonsai) | Deterministik piksel-bonsai | 2026, 18★ | 4 |
| [readme_portrait](https://github.com/kimjusnu/readme_portrait) | Renkli ASCII portre, SMIL yazım | 2026, 2★ | 4 |
| [YourTomo](https://github.com/prsdx/github-pet) | Aktiviteye tepki veren piksel kedi | Aktif, 14★ | 3 (Tamagotchi türü) |
| [blog-post-workflow](https://github.com/gautamkrishnar/blog-post-workflow) | RSS → README liste | 3.450★, AGPL | 3 (metin; ya da 20 satırlık kendi Action'ımız) |
| [vinilo](https://github.com/icortesb/vinilo) | Spotify'ı kendi Action'ında statik SVG'ye çevirir (token üçüncü tarafa gitmez) | 2026-09 | 3 (Spotify kısıtları baki) |
| [Platane/snk](https://github.com/Platane/snk) | Yılan | 6.149★ | 1 — klişe |
| [lowlighter/metrics](https://github.com/lowlighter/metrics) | Dev eklenti seti | v3 dondurulmuş gibi; skyline kaynağı kapalı, tweets deprecated, music/16personalities kırılgan | 2 — görünümü hemen tanınır; isocalendar/rss dışında kullanma |
| Spectrewolf8/isometric-contributions, github-candles, daily-badge, huantt/weather-forecast | Niş | 2026 | 2–3 |

### 4.3 Rozet ve ikon

- [shields.io](https://github.com/badges/shields): `style=flat-square`, `labelColor` ile tek nötr palet, `logo=data:image/svg+xml;base64,…` ile **özel logo** (not: `logoColor` yalnız simple-icons logolarında). 5 gün önbellek. Puan 3: **en fazla 3–6 anlamlı rozet** ya da hiç.
- [simple-icons](https://github.com/simple-icons/simple-icons) (CC0, 26 bin★): kendi SVG'mize gömmek için hammadde. Puan 4.
- [devicon](https://github.com/devicons/devicon): `plain` monokrom varyantlar kendi SVG içinde şık. Puan 3.
- [skill-icons](https://github.com/tandpfun/skill-icons), [markdown-badges](https://github.com/Ileriayo/markdown-badges) duvarı, forthebadge: Puan 1, **klişe**.

### 4.4 Elle/kodla animasyonlu SVG zinciri (asıl ayrışma burada)

**Kodla üretim**
- [cduck/drawsvg](https://github.com/cduck/drawsvg) (Python, SMIL `Animate/AnimateMotion/AnimateTransform`; aktif) — **5/5, ana araç**.
- `svgwrite` arşivlendi (kullanma); alternatif düz şablon/f-string ya da [svg.py](https://github.com/orsinium-labs/svg.py).
- **Yazı → path:** Python `fontTools` `SVGPathPen` (aktif, 5★) veya [opentype.js](https://github.com/opentypejs/opentype.js) `font.getPath().toSVG()`; mevcut SVG'deki `<text>`'i toplu çevirmek için [svg-text-to-path](https://github.com/paulzi/svg-text-to-path). → **Satoshi 900 ile yazılmış adın path'e çevrilir, font gömmeye gerek kalmaz, her tarayıcıda birebir aynı görünür.**
- Teknik örnekleri: stroke-dasharray çizim (vivus-instant), typewriter SMIL (readme_portrait'in clip-rect `<animate>` + `keyTimes`'ı), morph (`animate d`), dither dalgası (dither-portrait), fizik yörünge (github-gravity).

**Font gömme (path'e çevirmek istemezsek)**
- `pyftsubset Font.woff2 --text="…" --flavor=woff2` → 20–40 karakter ≈ 5–15 KB → `<style>@font-face{src:url(data:font/woff2;base64,…)}</style>`.
- Lisans: OFL fontlarını belgeye gömmek serbest (OFL SSS §1.12), lisans metni zorunlu değil. **Satoshi** ITF Free Font License ile (site zaten self-host ediyor; gömme izni fontshare lisansında teyit edilmeli — path'e çevirmek bu soruyu tamamen ortadan kaldırır).

**Tasarım araçları (gerekirse)**
- [Glaxnimate](https://glaxnimate.mattbas.org) (açık kaynak, **SMIL export**) — 4/5. LottieFiles VS Code eklentisi 2026-05'ten beri SMIL export veriyor (kapsamı doğrulanmadı) — 3/5. SVGator: animasyon export yalnız ücretli planda ve morph/motion-path JS ister — 3/5. Figma: animasyonlu SVG export yok, yalnız statik hazırlık — 2/5. Jitter/Linearity: video/GIF, SVG yok.

**Optimizasyon**
- [svgo](https://github.com/svg/svgo) varsayılan preset animasyonu bozar. Güvenli config: `preset-default` + `cleanupIds:false, removeHiddenElems:false, mergePaths:false, convertShapeToPath:false, removeUnknownsAndDefaults:false, inlineStyles:false, minifyStyles:false, collapseGroups:false, removeUselessStrokeAndFill:false`. Hedef ≤300 KB. Chrome + Firefox + Safari + gerçek README'de test.

### 4.5 GIF / video / terminal kaydı

- [charmbracelet/vhs](https://github.com/charmbracelet/vhs) (`.tape` DSL → GIF/MP4/WebM, deterministik, CI'da çalışır) — 5/5.
- asciinema → animasyonlu **SVG**: [svg-term-cli](https://github.com/marionebl/svg-term-cli) (CSS, JS yok) veya [termsvg](https://github.com/MrMarble/termsvg) — 4/5. asciinema + [agg](https://github.com/asciinema/agg) → GIF — 4/5.
- Ekran kaydı → GIF: [gifski](https://github.com/ImageOptim/gifski) (en iyi kalite) veya ffmpeg `palettegen/paletteuse`. WebP/APNG GIF'in %30–60'ı ama GitHub'da doğrulanmadı; önce test.

---

## 5. Claude skill / plugin / MCP durumu

**Sonuç: "özel animasyonlu profil SVG'si" üreten hazır bir skill, plugin ya da MCP yok.** Bulunanlar:

| Kaynak | Ne var | Değerlendirme |
|---|---|---|
| [boffti/github-profile-readme](https://github.com/boffti/github-profile-readme) (skill) | Görüşme → 9 arketip (Minimalist, Visual Showcase, Self-Updating, Persona, Interactive…) → taslak; "tam olarak bir arketip", "substance over decoration" gibi iyi kurallar | 3/5 — yapı/ton kararı için okunabilir; önerdiği widget'lar klasik (stats/typing/capsule), **özel SVG üretmeyi öğretmiyor** |
| [stark-ai-de/agent-skills → animated-readme-logo](https://github.com/stark-ai-de/agent-skills) | audit/create/animate; SVG doğrulayıcı script'ler; motion'ı GIF kare kare üretiyor | 2/5 — çoğunlukla süreç sarmalayıcısı, SMIL/CSS yazmıyor |
| livlign/claude-skills → repo-visuals | Hero görsel: GIF/PNG/animasyonlu SVG (elle CSS/SMIL) | 3/5 — en işe yarar olanı ama proje README'si odaklı; **Snyk "Critical"** uyarısı (npm/Chromium indirme, `git push`) → kurmadan kodunu oku |
| ClaudSkills "github-readme-maker", svg-animation-builder (GSAP) | Jenerik / JS tabanlı | 1–2/5 — README'de JS çalışmaz |
| [anthropics/skills](https://github.com/anthropics/skills), claude-plugins-official, awesome-claude-code, awesome-claude-skills | README/SVG-animasyon skill'i yok; dolaylı: `frontend-design` (özgün görsel karar baskısı), `algorithmic-art` (p5.js → kareleri GIF'e almak gerekir), `slack-gif-creator` | — |
| MCP: profilekit-mcp, Logoloom, icon-generator | Statik SVG/ikon ya da hosted kart URL'si; animasyon MCP'si yok | 1–2/5 |
| README üreten web araçları (rahuldkjain generator 24 bin★, GPRM, profileme.dev, profilinator, readme.so) | Hepsi aynı kalıbı üretir | 1/5 — **klişe fabrikası** |

**Pratik sonuç:** Claude + drawsvg/fontTools + bu rapordaki kurallar yeterli. İstersen §1 ve §4.4'ü yerel bir `SKILL.md`'ye dönüştürüp ileride de kullanırız; ama bu iş için gerekli değil.

---

## 6. Biz ne yapabiliriz — Asil'e özel

### 6.1 Elimizdeki malzeme

- **Marka dili (asilturkmen.com):** zemin `#04091a`, elektrik mavisi **parçacık-ağı** (noktalar + ince çizgiler, ışıyan düğümler) video hero, Satoshi 900 başlık (beyaz → buz mavisi gradyan), Inter gövde, soğuk gri-mavi metin tonları (`#afc6d9`, `#8095b9`). Sinematik, karanlık, sakin.
- **İçerik tek kaynak:** `AsilPortfolio/content/site.json` + `content/projects/*.json` (EN/TR; yönetim panelinden yayınlanıyor). 7 proje: NedirBeo (canlı, topluluk sözlüğü), Wipeout (Unity LAN parkur, **etkinlikte 50+ oyuncu**), HesAppcım, Test2Drive, Not Takip (Playwright + Telegram), TokenStudies, Yayla Yemek Evi.
- **Görseller:** `AsilPortfolio/public/media/projects/<slug>/` (her projenin ekran görüntüleri), `public/media/hero/cinema*.mp4|webp`, `public/profile.jpg`, `public/fonts/satoshi-900.woff2`.
- **Kimlik:** Yazılım Mühendisliği öğrencisi (DAÜ), Kuzey Kıbrıs; web + mobil + oyun; TR/EN.

### 6.2 Konseptler

**A. "Constellation" — önerim (çekirdek)**
- **Hero:** elle yazılmış tek SVG (`assets/hero.svg`, dark; `hero-light.svg`; `hero-mobile.svg`; `hero-still.svg`). Sahne: sitenin parçacık ağı, ama README için yeniden çizilmiş — 80–150 düğüm, ince çizgiler, SMIL ile **nefes alan** ışıma (düğümler sırayla parlıyor, bir ışık darbesi ağ boyunca geziyor). Ortada **"Asil Türkmen"** Satoshi 900'den path'e çevrilmiş, üzerinden bir kez geçen ışık süpürmesi; altında tek satır rol. Her şey vektör → Firefox base64 tuzağına girmiyor, Safari için SMIL.
- **Portre seçeneği (ayrışma noktası):** `profile.jpg`'den **parçacık-ağı portre**: fotoğrafın parlaklık haritasından örneklenmiş noktalar, yakın noktalar arası çizgiler; ağ önce dağınık, SMIL ile yüze toplanıyor (veya hafifçe dalgalanıyor). Sitenin hero diliyle aynı malzeme, ama **kimsede olmayan** bir şey. dither-portrait'in zarafeti, kendi dilimizde.
- **Projeler:** brenocq kalıbı — her proje için **aynı dilde SVG kart** (ekran görüntüsü + ad + tek cümle + teknoloji noktaları), `<a href>` ile tıklanabilir, 2 sütun `<table>` (mobilde kaydırma kabul edilebilir; ya da tek sütun). Kartlar **Action ile `site.json`'dan üretilir** → site panelinden proje yayınlayınca README de güncellenir (gerçek "self-updating", sahte dinamiklik değil).
- **"Şu an" satırı:** `Last updated 2026-10-22 · building X · last commit: "…"` — Action günlük yazar. Canlılık sinyali.
- **Bağlantılar:** rozet değil, SVG içinde çizilmiş 3–4 küçük ikon (site, LinkedIn, e-posta) ya da düz metin linkleri.
- **Tahmini iş:** 12–20 saat. **Risk:** yok (her şey repoda; dış servis yok). Bakım: Action `GITHUB_TOKEN` ile çalışır.

**B. "Yaşayan sahne" — Faz 2**
- Hero, **Kıbrıs yerel saatine ve havasına** göre 4–6 varyant arasında geçer (gece: ağ yıldız alanına dönüşür, bir pencere ışığı; gündüz: daha parlak; yağmur: ince çizgiler düşer). living-scene mekanizması: Open-Meteo (anahtarsız) + 3 saatte bir cron + değişince commit. Ziyaretçi "Lefkoşa'da şu an gece, muhtemelen uyuyor" hissini alır.
- **Tahmini iş:** +6–10 saat. **Risk:** düşük (Open-Meteo ücretsiz; kırılsa varsayılan sahne kalır).

**C. "Oynanabilir" — Faz 3 (isteğe bağlı)**
- Wipeout'u yapmış biri için README'de oyun doğal. Satranç/2048 dolu; özgün seçenek: **ortak parkur** — küçük bir izometrik pist, ziyaretçiler issue linkiyle (sağ/sol/zıpla) karakteri ilerletir, Action pisti SVG olarak yeniden çizer, en uzağa götürenler "leaderboard"da (gerçek GitHub kullanıcı adları). Alternatif, çok ucuz: benjaminsampica tarzı tek tık etkileşim (ör. "bugünkü ziyaretçi sayacı" değil, "bir yıldız yak": her tık ağa bir düğüm ekler, ağ zamanla ziyaretçilerle büyür — **ziyaretçinin kendisi görselin parçası olur**).
- **Tahmini iş:** 4–6 saat ("yıldız yak") / 15–25 saat (parkur). **Risk:** issue spam'i (rate limit + yalnız başlık formatı eşleşenleri işlemek yeterli).

**D. Ek bölümler (A'nın içine girebilir)**
- **Mermaid `gitGraph` ile "yolculuk":** dallar = okul/işler/projeler, merge'ler = yayınlar, tag'ler = yıllar; tema otomatik. Kimse yapmamış, 1–2 saat, sıfır bağımlılık. Koyu temada kontrast testi şart.
- **Kısa, insan sesiyle yazılmış "hakkımda":** 3 cümle; `const asil` yok, emoji yağmuru yok.
- **`<details>` ile ikinci katman:** Türkçe özet, CV linkleri (`public/cv/cveng.pdf`, `cvtr.pdf` sitede zaten var).

### 6.3 Önerilen plan

| Faz | İçerik | Süre | Çıktı |
|---|---|---|---|
| 0 | Konsept seçimi: yapısal olarak farklı 2–3 yerleşimi ASCII önizlemeyle sunup birini öneririm; sen seçersin | 0,5 saat | karar |
| 1 | Hero SVG (dark/light/mobile/still), isim path'i, parçacık ağı + SMIL; Chrome/Firefox/Safari + gerçek profilde ekran görüntüsüyle kontrol | 6–10 saat | `assets/hero*.svg` |
| 2 | Proje kartı üretici (Python, `site.json` → SVG), 7 kart, Action (günlük + manuel tetik) | 4–6 saat | `scripts/`, `.github/workflows/` |
| 3 | README iskeleti: hero, hakkımda, projeler, "şu an", bağlantılar; tema/mobil testleri | 2–4 saat | `README.md` |
| 4 (ops.) | Yaşayan sahne (saat/hava) | 6–10 saat | varyant SVG'ler + Action |
| 5 (ops.) | Etkileşim ("yıldız yak" ya da parkur) | 4–25 saat | issue workflow |

### 6.4 Kalite çıtası (her fazda)

- 846px masaüstü **ve** 308px telefon genişliğinde okunur; metin 14px'e göre ölçek.
- Dark + light (`<picture>`), hareket azaltma için `hero-still.svg`.
- SVG ≤ 300 KB, GIF yok (ana hareket için), dış servis yok, relative path.
- svgo güvenli config; üç tarayıcıda SMIL testi; GitHub'da gerçek render ekran görüntüsü.
- "Son güncelleme" tarihi görünür; Action kırılırsa README bozulmaz (son başarılı çıktı kalır).
- Rozet duvarı, typing header, dalga banner, ziyaretçi sayacı, stat kartı, yılan: **yok**.

---

## 7. Kaçınılacaklar (2026 klişe listesi)

- capsule-render dalga + readme-typing-svg + Platane/snk + skill-icons satırı + `for-the-badge` duvarı (mevcut README'nin iskeleti).
- `const me = {...}` kod bloğu biyografi; "Thanks for visiting 🚀"; emoji başlıklı 8 bölüm.
- Hazır profil üreticileri ve "readme-maker" türü ince skill'ler.
- Vercel/Heroku/onrender üzerindeki üçüncü-taraf dinamik SVG uçları (best-effort, hız sınırı, camo önbelleği).
- Spotify "now playing" (2026 Dev Mode kısıtları; kırılınca boş kutu kalır).
- lowlighter/metrics görünümü; skyline (kaynak kapalı), tweets (deprecated), kazımaya dayalı eklentiler.
- Rastgele joke/quote, zodiac, ziyaretçi sayacı.
- SVGator JS animator, GSAP/svg.js çıktıları, Lottie JSON'u doğrudan (README'de JS yok).
- svgo varsayılan preset'i animasyonlu SVG'de (`cleanupIds`, `removeHiddenElems` animasyonu kırar).
- Bakımsızlar: svg-banners (2020), termtosvg/svgwrite (arşiv), markscribe, Haiku Animator.

---

## 8. Doğrulanamayanlar / açık sorular

- GitHub camo'nun gerçek boyut sınırı; animasyonlu WebP/APNG'nin README'de oynayıp oynamadığı.
- SVG içi `prefers-color-scheme` ve `prefers-reduced-motion`'ın GitHub `<img>` bağlamındaki davranışı (çözüm: `<picture>`; test edilecek).
- Video gömmenin **profil** README'sinde çalıştığı (repo README'de çalışıyor).
- Alerts/math'ın profil README'sinde canlı örneği (aynı pipeline, çalışması bekleniyor).
- Spotify refresh-token 6 ay kuralı; LottieFiles SMIL export kapsamı; `<foreignObject>` tarayıcı davranışı.
- Satoshi'nin (ITF Free Font License) SVG'ye gömülme izni — path'e çevirirsek sorun kalmaz.
- Küçük repoların yıldız sayıları (API kotası nedeniyle bir kısmı sayfadan okundu).

---

## 9. Başlıca kaynaklar

- GitHub Docs: [About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes), [Managing your profile README](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-github-profile/customizing-your-profile/managing-your-profile-readme), [About anonymized URLs (camo)](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-anonymized-urls), [Attaching files](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/attaching-files), [Creating diagrams](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams), [Accessibility settings](https://docs.github.com/en/account-and-profile/how-tos/account-settings/managing-accessibility-settings)
- Changelog: [Themed images `<picture>` (2022-05)](https://github.blog/changelog/2022-05-19-specify-theme-context-for-images-in-markdown-beta/), [`#gh-dark-mode-only` (2021-11)](https://github.blog/changelog/2021-11-24-specify-theme-context-for-images-in-markdown/), [Autoplay animated images option (2022-05)](https://github.blog/changelog/2022-05-19-option-to-prevent-animated-images-from-playing-automatically/), [Alerts (2023-12)](https://github.blog/changelog/2023-12-14-new-markdown-extension-alerts-provide-distinctive-styling-for-significant-content/), [Video uploads (2021-05)](https://github.blog/changelog/2021-05-13-video-uploads-now-generally-available/)
- Sanitasyon: [github/markup](https://github.com/github/markup#readme), [html-pipeline SanitizationFilter](https://github.com/gjtorikian/html-pipeline/blob/main/lib/html_pipeline/sanitization_filter.rb) (üretim listesi birebir aynı değil; rapor ölçüme dayanıyor)
- SVG-as-image: [SVG2 secure animated mode](https://www.w3.org/TR/SVG2/conform.html#secure-animated-mode), [MDN SVG as an image](https://developer.mozilla.org/en-US/docs/Web/SVG/Guides/SVG_as_an_image), [markup#1864 (Firefox base64 animasyon)](https://github.com/github/markup/issues/1864)
- Listeler: [awesome-github-profile-readme](https://github.com/abhisheknaiidu/awesome-github-profile-readme), [beautify-github-profile](https://github.com/rzashakeri/beautify-github-profile), [readme-games topic](https://github.com/topics/readme-games)
- Yazılar: [simonw self-updating README](https://simonwillison.net/2020/Jul/10/self-updating-profile-readme/), [AVIVASHISHTA29 (Tem 2026)](https://avivashishta.com/blog/build-animated-github-profile-readme.html), [skulitom piksel-art (Eki 2026)](https://dev.to/rivskiy_skulitom_af400ad1/how-to-put-crisp-animated-pixel-art-in-a-github-profile-readme-1cpd), [brenocq HN (Mar 2025)](https://news.ycombinator.com/item?id=43504961), [Top 10 hacks 2026 (dev.to)](https://dev.to/igorcbraz/top-10-hacks-to-make-your-github-readme-actually-interesting-in-2026-3i3h)
