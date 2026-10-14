# SmartComplete — sol/sağ ok düzeltmesi ve konum incelemesi

## Sol/sağ seçim düzeltmesi

`horizontal-arrows.patch`, mevcut modern arayüz/ikon/İngilizce veri sürümünün üzerine hazırlanmıştır. Öneri listesi açıkken Sağ/Aşağı ok bir sonraki, Sol/Yukarı ok önceki adayı seçer. İlk/son aday arasında döngü korunur. Listede aday yokken sol/sağ tuşları mevcut uygulama yoluna bırakılır. Ctrl/Alt kısayolları ve Shift ile yazım değiştirilmez.

Gerçek Fcitx5 motoruyla çalışan regresyon testleri önek, sonraki kelime ve emoji listelerinde sol/sağ/yukarı/aşağı gezinmeyi, vurgulanan adayın Tab/Enter ile kabulünü, Ctrl/Alt+sol/sağ geçişini ve boş listeyi kapsar.

- Eski kod: yeni testte 140 assertion başarısız; sorun tekrar üretildi.
- Yamalı geçici kopya: derleme başarılı; **13/13 CTest testi geçti**.
- Yama geçici kopyaya uygulandı ve test edilen kaynakla aynı olduğu karşılaştırıldı.
- Kurulum betiği için `bash -n` kontrolü yapıldı; canlı kurulum çalıştırılmadı.
- Kurulum öncesinde Fcitx5'in kapalı olması artık kabul edilir; başarılı kurulum sonunda başlatılır. Birden fazla süreç veya gerçek `pgrep` hatası hâlâ işlemi durdurur. `python3 installer_preflight_regression.py -v`: dört ön kontrol senaryosu geçti.
- Gerçek SmartComplete deposu ve çalışan eklenti değiştirilmedi.

## Menü neden altta?

Çalışan Hyprland: **0.56.2**, commit `efb50993780079460b0cbed1363e2166a2de1d9f`. Fcitx5 tanılamasında Edge giriş bağlamları `wayland_v2` olarak görünüyor.

Bu yolda Fcitx5 `getInputPopupSurface()` ile yüzeyi oluşturuyor; konumu Hyprland hesaplıyor. Çalışan sürümün `CInputPopup` konum kodu, menü ekranın alt sınırını aşmıyorsa imleç dikdörtgeninin altını; aşıyorsa üstünü seçiyor. Hesap ekranın tam sınırına göre yapılıyor; fotoğraftaki dock alanı bu hesapta ayrıca çıkarılmıyor.

Bu nedenle tema dosyasına hayali bir `Position=Above` anahtarı eklenmedi ve üst konum düzelmiş gibi gösterilmedi. **Bu paket konumu değiştirmez.** Önce üstü tercih ettirmek bu Wayland yolunda ayrı bir Hyprland düzeyi değişiklik gerektirir. Pencere yöneticisini otomatik olarak yamalamak/yeniden derlemek bu düzeltmeye dahil edilmedi.

İncelenen kaynaklar:
- https://github.com/fcitx/fcitx5/blob/5.1.23/src/ui/classic/waylandinputwindow.cpp
- https://github.com/hyprwm/Hyprland/blob/efb50993780079460b0cbed1363e2166a2de1d9f/src/managers/input/InputMethodPopup.cpp

## Sol/sağ düzeltmesini kurmak

Açık yazılarını kaydet; Fcitx5 yeniden başlatılacak. Normal kullanıcı olarak:

```bash
bash /home/ekrem/wrong/reports/smartcomplete-arrows/install.sh
```

Betik kaynak hashlerini ve yamayı kontrol eder; mevcut kaynakları/eklentiyi `~/.local/state/smartcomplete/arrows-backup.*` altında yedekler (XDG_STATE_HOME varsa onu kullanır). Yamayı uygular, derler ve testleri çalıştırır. Başarılıysa yalnız eklenti dosyasını atomik olarak değiştirir; sözlük, tema veya profil dosyalarını yeniden kurmaz. Fcitx5'i yeniden başlatıp yeni PID, giriş yöntemi, etkin durum ve yüklenen eklenti yolunu kontrol eder.

Herhangi bir hata sonraki adımları durdurur. Önceki adımlar otomatik geri alınmaz; yedek yolunu sakla. Kaynaklar değiştiyse hash kontrolünü atlama. Canlı menü görünümü ve fiziksel klavye etkileşimi burada test edilmedi.
