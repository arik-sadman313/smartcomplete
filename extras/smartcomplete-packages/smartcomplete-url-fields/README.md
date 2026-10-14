# SmartComplete — adres/URL alanlarında önerileri kapatma

`url-fields.patch`, Fcitx5'in `CapabilityFlag::Url` işaretini kullanır. URL olarak bildirilen bir alanda tuşlar SmartComplete tarafından kabul edilmez/filtrelenmez; doğrudan uygulamaya geçer. Öneri, otomatik düzeltme ve URL metninin SmartComplete üzerinden öğrenilmesi engellenir. Tarayıcının kendisine ait geçmiş/adres önerileri değişmez.

Bütün tarayıcıyı engellemez: aynı tarayıcıdaki normal metin kutusunda kelime önerileri çalışmaya devam eder. URL alanına geçildikten sonra eski listeden tıklanan adayın yazılması da engellenir. Önceki alana ait bekleyen SmartComplete kompozisyonu yeni URL alanına aktarılmaz; tampon ve bağlam temizlenir.

Kontroller tuş olayında ve aday kabulünde uygulanır. Alan türü değiştiği anda, hiç yeni tuş/aday olayı olmadan pencerenin anında gizlenmesi ayrıca doğrulanmadı. Tarayıcı/Wayland yolu URL işaretini bildirmiyorsa motor adres çubuğunu normal metin alanından ayıramaz; bu durumda canlı capability tanılaması gerekir. URL gibi görünen metinleri tahminle engelleyen bir kural eklenmedi.

## Doğrulama

- Gerçek Fcitx5 InputContext ve KeyEvent nesneleriyle, test istemcisinin alan tipi URL/normal arasında değiştirilerek test edildi.
- Edge/Chromium/Firefox program adlarında URL alanı tuş geçişi, noktalama, boşluk, Tab/Enter, ok tuşları, eski adaya tıklama ve normal alana dönüş kontrol edildi. Bunlar canlı tarayıcı testleri değil, motor regresyonlarıdır.
- Eski kodda yeni regresyonlar **93 assertion hatası** üretti.
- Yamalı geçici kopyada derleme ve **13/13 CTest testi başarılı**.
- Kurulum ön kontrolü: Fcitx5 kapalı/açık/çoklu süreç/sorgu hatası için **4/4 test başarılı**.
- `bash -n install.sh` başarılı. Yama uygulaması ve test edilen kaynakla byte karşılaştırması başarılı.
- Gerçek depo, kurulu eklenti, profil ve çalışan oturum değiştirilmedi. Canlı adres çubuğu doğrulaması yapılmadı.

## Kurulum

Önce açık yazılarını kaydet. Normal kullanıcı olarak, grafik oturumundaki terminalde:

```bash
bash /home/ekrem/wrong/reports/smartcomplete-url-fields/install.sh
```

Betik kaynak hashlerini kontrol eder, kaynak/eklentiyi kullanıcı state dizinine yedekler, yamayı uygular, derler ve test eder. Testler başarılıysa yalnız eklentiyi kurup Fcitx5'i yeniden başlatır; kapalıysa başlatır. Tema, sözlük ve profil dosyalarını yeniden kurmaz.

Bir kontrol başarısızsa devam etmez; önceki işlemleri otomatik geri almaz. Hash kontrolünü atlama. Kaynaklar farklıysa yama mevcut sürüme göre yeniden hazırlanmalıdır. Başarı sonrası aynı tarayıcıda adres çubuğu ile normal mesaj alanını ayrı ayrı denemek gerekir.

Bu paket önceki sol/sağ ok, Ctrl/Alt, modern arayüz ve İngilizce veri değişikliklerini korur. Popup konumunu veya tray ikonunu değiştirmez.
