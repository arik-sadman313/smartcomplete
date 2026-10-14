# SmartComplete — yatay üç öneri ve modern Fcitx5 teması

## Kapsam / tasarım

Gönderilen fotoğraftaki dar, dikey beşli liste yerine yatay, en fazla üç aday sunulur. İngilizce tahmin motoru ve uygulanmış Ctrl/Alt düzeltmesi korunur. Metin, sonraki kelime ve emoji aynı liste oluşturucusunu kullanır. Eski yapılandırma sekiz aday istese bile hem görünen hem klavyeyle erişilen liste üçle sınırlanır; daha az sonuç varsa boş seçenek eklenmez.

İlk aday belirgin seçilidir; ↑/↓ gezinme ve döngü sonunda vurgulanan adayla kabul edilen aday eşleşir. Tab/Enter ve tıklama ile kabul korunur. Yeni sol/sağ kısayolları eklenmedi. Escape, noktalama, otomatik düzeltme ve AI davranışları bu yamada yeniden tasarlanmadı. Türkçe desteği eklenmedi.

Tema: açık/koyu yüzey, yaklaşık 10 px yuvarlak köşeler, hafif gölge, 12 px yatay metin payı, Sans 12 punto, mavi seçim vurgusu. Bulanıklık veya Windows'a özgü pencere efekti gerektirmez. Tema ve yazı tipi **Fcitx5 Classic UI genelinde** etkili olur; diğer giriş yöntemleri ve menüler de bu görünümü kullanabilir. Portal/KDE gibi başka bir aday penceresi sağlayıcısı aktifse Classic UI teması görünmeyebilir.

`preview.png` tasarım önizlemesidir; çalışan uygulama ekran görüntüsü değildir. Gerçek ölçüler uygulama, DPI ve Fcitx5 tarafından belirlenir.

## Dosyalar

- `compact-ui.patch`: kaynak ve gerçek Fcitx5 motor testi değişiklikleri.
- `tray-icon.patch`: motorun ikon adını mevcut `Icon=linuxcomplete` kaydıyla eşleştirir; SVG ve CMake kurulum kuralı ekler. Tray menüsündeki SmartComplete satırı ve SmartComplete aktifken tepsi simgesi bu adı kullanır.
- `icons/hicolor/`: özgün mavi metin/tamamlama oku ikonu; SVG ve 16/22/24/32/48/64 px PNG sürümleri. Harici ikon/font kullanılmadı. Assetler SmartComplete'in MIT lisansıyla dağıtılabilir.
- `validate_icons.py`: SVG güvenlik/yapı ve PNG boyut kontrolleri.
- `tray-icon-preview.png`: büyütülmüş ikon önizlemesi.
- `base.sha256`: Ctrl/Alt yamasının uygulanmış olduğu başlangıç dosyaları. Bilinmeyen değişikliklerin üzerine yazılmasını engeller.
- `themes/smartcomplete-modern-light/`, `themes/smartcomplete-modern-dark/`: tema yapılandırması, PNG görseller ve SVG kaynakları.
- `validate_themes.py`: görüntü referansları, dokuz parçalı ölçekleme sınırları ve renk kontrastı kontrolleri.
- `install.sh`: kullanıcı açıkça çalıştırırsa yedekleme, yama, test, derleme, kurulum, yeniden başlatma ve süreç yükleme kontrolü.

## Kurulumdan önce salt okunur kontroller

Aşağıdaki komutlar SmartComplete deposuna veya Fcitx5 ayarlarına yazmaz:

```bash
bash <<'BASH'
set -Eeuo pipefail
cd /home/ekrem/smartcomplete
BUNDLE=/home/ekrem/wrong/reports/smartcomplete-modern-ui
sha256sum --check "$BUNDLE/base.sha256"
git apply --check "$BUNDLE/compact-ui.patch"
git apply --check "$BUNDLE/tray-icon.patch"
python3 "$BUNDLE/validate_themes.py"
python3 "$BUNDLE/validate_icons.py"
bash -n "$BUNDLE/install.sh"
BASH
```

Hash kontrolü başarısızsa onu atlama: mevcut kaynaklar değişmiş veya Ctrl/Alt düzeltmesi farklı uygulanmış olabilir. Yeniden yama üretmek gerekir. Paket, bilinen mevcut değişiklikleri içerdiğinden temiz Git ağacı şartı koymaz; bunun yerine üç kritik dosyanın tam içeriğini kontrol eder.

## Güvenli kurulum komutu

**Açık yazılarını kaydet.** Kendi grafik oturumunun terminalinde, normal kullanıcı olarak çalıştır. Script kendi gereken adımında sudo sorar; `sudo bash ...` kullanma. Dosyayı doğrudan çalıştırmak yerine `bash` ile çağır:

```bash
bash /home/ekrem/wrong/reports/smartcomplete-modern-ui/install.sh \
  /home/ekrem/smartcomplete light
```

Koyu görünüm için son argümanı `dark` yap. İki tema birlikte kurulur, seçilen tema sabit kullanılır; otomatik açık/koyu algılama kapalıdır. Var olan aynı isimli tema dizinleri varsa script üzerlerine yazmaz, durur.

Scriptin sırası:
1. Araçları, grafik oturumunu, tek çalışan Fcitx5 sürecini, kaynak hashlerini ve yamanın uygulanabilirliğini kontrol eder.
2. `$XDG_STATE_HOME/smartcomplete/modern-ui-backup.*` (varsayılan `~/.local/state/smartcomplete/`) altında eski kaynak dosyalarını ve kurulu eklentiyi yedekler.
3. Sırayla arayüz ve tray ikon yamalarını uygular; Release derleme, odaklı regresyon testi ve tüm CTest testlerini çalıştırır.
4. Başarılıysa sudo yetkisini kontrol eder, Fcitx5'i nazikçe kapatır. Kapanış eski ayarları yazabileceği için Classic UI yapılandırmasını **kapanıştan sonra** yedekler.
5. Yalnızca değişen eklentiyi atomik dosya değiştirme ile kurar; proje `install.sh` betiğini çalıştırmaz, profil/ortam/sözlük ayarlarını sıfırlamaz.
6. Kullanıcı temalarını ve `~/.local/share/icons/hicolor` altına SVG/PNG ikonlarını kurar (XDG_DATA_HOME varsa onu kullanır). Mevcut aynı isimli ikonların üzerine yazmaz. Classic UI dosyasında tema/yazı/yerleşim anahtarlarını ve `PreferTextIcon=False` ayarını günceller; ilgisiz satırları korur. Bu tercih diğer Fcitx5 yöntemlerinde de metin yerine ikonu tercih ettirir.
7. Fcitx5'i başlatır, SmartComplete'i seçer ve etkinleştirir. Yeni PID, etkinlik durumu, seçili yöntem ve bellekte yüklü `linuxcomplete.so` kontrol edilir.

`set -Eeuo pipefail` ile herhangi bir başarısız kontrol sonraki adımları durdurur. Kontrollerin bekleme süreleri sınırlıdır. **Otomatik geri alma yoktur:** hata yama uygulandıktan sonra oluşursa kaynak yamalı kalabilir; kapanıştan sonra oluşursa Fcitx5 durmuş kalabilir. Hata çıktısındaki yedek yolunu sakla ve betiği körlemesine tekrar çalıştırma.

## Geri dönüş

İki yama kurulduysa önce `tray-icon.patch` için `git apply --reverse --check` çalıştır; başarılıysa `git apply --reverse` ile yalnız ikon yamasını geri al. Sonra arayüz yamasını geri almadan önce:

```bash
cd /home/ekrem/smartcomplete
git apply --reverse --check /home/ekrem/wrong/reports/smartcomplete-modern-ui/compact-ui.patch
```

Bu kontrol başarılıysa aynı komutta `--check` yerine yalnız `--reverse` ile yamayı geri alabilirsin. Bu işlem önceki Ctrl/Alt düzeltmesini kaldırmaz.

Çalışan sürümü geri almak için Fcitx5 kapalıyken yedekteki `linuxcomplete.so` dosyasını `/usr/lib/fcitx5/linuxcomplete.so` konumuna geri kur ve `classicui.conf` dosyasını `config-path.txt` içindeki konuma geri koy. Yedekte `classicui-was-absent` varsa önceki durum yapılandırma dosyasının bulunmamasıydı. Yeni tema dosyaları seçili olmadığında etkisizdir; silmek zorunlu değildir. Sonra normal kullanıcı olarak `fcitx5 -d` ile başlat. Sonradan başka değişiklikler yaptıysan önce mevcut dosyaları ayrıca yedekle.

## Çalıştırılmış doğrulamalar

Tüm derleme/testler mevcut çalışma alanındaki geçici kaynak kopyalarında çalıştırıldı; gerçek SmartComplete deposu değiştirilmedi.

- Son regresyon testleri eski motorda: 70 başarısız assertion, CTest başarısız. Dikey liste, sınırlandırılmamış aday sayısı ve imleç davranışı farkları yakalandı.
- Yamalı kopyada `cmake --build ... -j4`: başarılı, eklenti ve testler derlendi.
- `ctest --test-dir ... --output-on-failure`: **12/12 başarılı**.
- Prefix, sonraki kelime ve emoji: yatay yerleşim; üç aday; gizli sayfa olmaması; başlangıç vurgusu; ↑/↓ döngüsü; Tab/Enter kabulü; adayın `select()` yolu; boş sonuç.
- Mevcut gerçek-motor Ctrl/Alt ve Shift regresyonları da aynı test çalışmasında geçti.
- Yama taze kopyaya uygulandı; üretilen dosyalar derlenmiş/test edilmiş dosyalarla byte düzeyinde karşılaştırıldı.
- `validate_themes.py`: iki temada görsel referansları ve dilimleme sınırları geçerli. Renklerden hesaplanan normal/seçili metin kontrastı açık: 14.75 / 6.49; koyu: 13.55 / 9.10.
- SVG dosyaları `rsvg-convert` ile PNG'ye çevrildi. Bu, Fcitx5'in canlı yerleşim doğrulaması değildir.
- `bash -n install.sh`: başarılı. Yapılandırma düzenleme bölümü, var olan/olmayan örnek dosyalarda çalıştırıldı; ilgisiz ayarlar korundu.

İkon eklemesinin doğrulaması: motorun `listInputMethods()` ikon adı testi eski kodda başarısız, yeni kodda başarılı. İkon ve yatay arayüz yamaları birlikte derlendi; **12/12 CTest testi tekrar geçti**. CMake kurulumu yalnız geçici `DESTDIR` dizinine yapıldı, hicolor SVG dosyasının kurulduğu doğrulandı. Gerçek `fcitx::IconTheme` araması geçici kurulumda `linuxcomplete` ikonunu 16/22/24/32/48/64 boyutlarının hepsinde buldu. Kullanıcı sistemine ikon kurulmadı. Yeni `PreferTextIcon=False` güncellemesi örnek yapılandırmada test edildi.

**Doğrulanmayanlar:** kurulum scriptinin gerçek sisteme uygulanması, canlı Fcitx5 tema yüklemesi/görünümü, farklı DPI/ekran kenarı/çok uzun aday yerleşimi ve fiziksel fare tıklaması. Oturuma dokunmamak için bunlar çalıştırılmadı. Kontrast hesapları tüm arayüzün erişilebilirlik sertifikası değildir.

Kurulumdan sonra bir grafik metin alanında `hel`, `hello ` ve `:s` ile önerileri; ↑/↓, Tab/Enter, Ctrl/Alt ve Shift ile etkileşimi kontrol et. Terminaller uygulamanın mevcut engelleme listesinde yer alır.

Tema anahtarları için incelenen Fcitx5 5.1.23 kaynakları:
- https://github.com/fcitx/fcitx5/blob/5.1.23/src/ui/classic/theme.h
- https://github.com/fcitx/fcitx5/blob/5.1.23/src/ui/classic/classicui.h
