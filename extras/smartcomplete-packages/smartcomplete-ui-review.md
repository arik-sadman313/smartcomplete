# SmartComplete — arayüz ve öneri deneyimi incelemesi

İncelenen proje: `/home/ekrem/smartcomplete/`
Tarih: 2026-10-14

## Sonuç
Windows 11'in kompakt, yatay kelime önerisi yaklaşımına benzer bir deneyim mevcut Fcitx5 mimarisinin üstünde hedeflenebilir. İlk tercih ayrı bir pencere sistemi yazmak değil, mevcut aday listesinin yerleşimini ve Fcitx5 temasını iyileştirmek olmalı. Kesin görünüm, kullanılan Fcitx5 arayüzüne ve masaüstüne bağlıdır; birebir Windows efekti garantisi verilmez.

## Kanıt sınırı
Bu rapor kaynak incelemesine dayanır. Uygulama çalıştırılmadı, ekran görüntüsü incelenmedi, derleme/test yapılmadı. Görünür kontrast, ölçeklendirme, gerçek gecikme ve uygulamalar arası uyum doğrulanmadı. Ürün kodu veya sistem ayarları değiştirilmedi. Görsel kalite puanı verilmedi.

## Öncelikli bulgular ve öneriler

### 1. Öneri alanı: kompakt yatay şerit
`src/engine/engine.cpp:393–410`: hem sonraki kelime hem önek önerisi listeleri dikey yerleşim ipucu ve sabit beşlik sayfa kullanıyor.

Öneri: varsayılan üç görünür aday; yapılandırılabilir üç/beş seçeneği; yatay yerleşim; belirgin seçili aday. Yerleşim değişince klavye gezinmesi de uyarlanmalı; mevcut yukarı/aşağı akışı `engine.cpp:163–180` içinde. Sol/sağ tuşları metin imlecinden koşulsuz alınmamalı, önce açık bir aday-gezinme modu tasarlanmalı.

Görsel hedef: 13–14 px okunaklı yazı, 8–12 px iç boşluk, 8–10 px köşe yarıçapı, sade kenarlık, hafif gölge, açık/koyu tema. Bunlar önerilen başlangıç değerleridir; ölçülmüş mevcut değerler değildir. Fcitx5 tema değişikliklerinin diğer giriş yöntemlerini etkileyebileceği hesaba katılmalı.

### 2. Öneri kabulü kullanıcı kontrolünde olmalı
`src/engine/engine.cpp:128–146,184–216`: seçim yoksa Tab/Enter ilk adayı kabul ediyor; noktalama yardımcısı da ilk adayı kullanabiliyor. Escape tamponu temizliyor.

Öneri: Tab öneriyi kabul etsin; Enter açık seçim yoksa kullanıcının yazdığını korusun ve normal uygulama davranışı açıkça tanımlansın. Noktalama, açık seçim olmadan kelime değiştirmesin. Escape yalnızca öneriyi kapatsın, yazılmış metni kaybetmesin. Bunlar çalışma zamanı tekrar üretimi yapılmamış, kaynakla doğrulanan davranış tasarımı bulgularıdır.

### 3. Türkçe için tema değişikliği yeterli değil
`src/engine/engine.cpp:428–434`: harf yakalama yalnızca A–Z/a–z aralığında. `src/predictor/predictor.cpp`, `preferred_language()`: her zaman English dönüyor. Veri dosyaları İngilizce odaklı. `src/predictor/ngram.cpp`, `to_lower()`: yalnızca ASCII büyük harfleri dönüştürüyor.

Öneri: Unicode giriş, Türkçe I/ı ve İ/i eşlemesi, Türkçe sözlük ve kelime sıklığı, Türkçe bağlam verisi. `gel`, `geliyor`, `geleceğim` gibi ekli biçimler için ilk aşamada sıklık tabanlı veri kullanılabilir; morfolojik çözümleyici ancak kalite ölçümü ihtiyacı gösterirse eklenmeli. Sadece `languages` alanını değiştirmek Türkçe desteği sağlamaz.

### 4. Ayar dosyası ile gerçek davranış örtüşmeli
`config/linuxcomplete.conf` içinde `languages`, `trigger_key`, `accept_key`, `dismiss_key` bulunuyor; `src/engine/engine_config.cpp` içindeki yükleyici bu alanları okumuyor. Motor tuşları doğrudan kontrol ediyor.

Öneri: bu alanları gerçek davranışa bağlamak veya desteklenmeyen ayarları açıkça belirtmek. Sonrasında küçük bir ayar ekranı: dil, üç/beş aday, yazı boyutu/tema, otomatik düzeltme, öğrenme, uygulama istisnaları. Bu depoda bağımsız ayar arayüzü kaynakları görülmedi; dış masaüstü entegrasyonu ayrıca incelenmeli.

### 5. Yapay zekâ yazmayı bekletmemeli
`src/predictor/ai_reranker.cpp`, `rerank()`: önbellek kaçırıldığında `request_ranking()` senkron çağrılıyor; `exec_curl()` çocuk süreci bekliyor. Motor tahmin çağrılarını tuş olayından yapıyor. AI varsayılan olarak kapalı.

Öneri: önce yerel sonuçları göster; isteğe bağlı AI sıralamasını arka planda çalıştır; eski bağlama ait cevabı at; kullanıcı seçim yaparken listeyi yeniden sıralama. Gerçek gecikme ölçülmedi; burada belirtilen risk senkron çağrı yoluna dayanıyor.

### 6. Kaliteyi daha fazla adayla değil, doğru ilk üç adayla ölç
Öneri: gerçek kullanım örneklerinden ayrı değerlendirme kümesi oluştur; ilk 1/3 isabet oranı, kabul oranı, gereksiz düzeltme oranı ve p95 öneri gecikmesini ölç. Türkçe ve İngilizceyi ayrı raporla. Yerel öneri için p95 <50 ms başlangıç hedefi olarak değerlendirilebilir; mevcut performans iddiası değildir. Kişisel öğrenme verisinin silinmesi ve AI'ya bağlam gönderiminin açık onayı ürün tasarımına dahil edilmeli.

## Önerilen görünüm

```text
Yazılan: mer
╭────────────────────────────────────╮
│ [merhaba]   merak   meraklı         │
╰────────────────────────────────────╯
```

Bu yalnızca konsepttir; mevcut Türkçe desteğini veya uygulanmış bir arayüzü temsil etmez. Birincil seçeneğin arka planı belirgin, diğer seçeneklerin hit alanı yeterli olmalı. Uzun kelime/cümle önerileri paneli kontrolsüz genişletmemeli. Satır içi hayalet metin ikinci aşamada, yalnızca gerçek önek tamamlamasında ve uygulama uyumu doğrulanarak ele alınmalı; mevcut kod `engine.cpp:371–375` içinde altı çizili tamamlamayı preedit'e ekliyor.

## Uygulama sırası ve kabul kontrolleri
1. Fcitx5 yatay üç aday prototipi ve tema. Açık/koyu, yüksek DPI, ekran kenarı, uzun aday, tıklama ve klavye seçimi kontrolü.
2. Enter/Escape/noktalama davranışının güvenli hale getirilmesi. Seçili/seçili olmayan aday, boş liste, sonraki kelime ve emoji için regresyon testleri.
3. Türkçe Unicode ve dil verisi. `ş, ğ, ı, İ, ö, ü, ç`, büyük/küçük harf ve ekli kelime testleri.
4. Ölçümlere göre sıralama iyileştirmesi; gerekirse asenkron AI. Eski cevapların atılması ve odak değişimi testleri.

İlk aşamada yeni bir Qt/GTK overlay uygulaması önerilmiyor. Özel pencere, Wayland konumlandırma/odak ve uygulama uyumu yükünü artırır. Mevcut Fcitx5 yolunun görsel sınırları çalışan prototiple görülmeden bu maliyet alınmamalı.
