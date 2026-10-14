# SmartComplete — tekrar eden yazı ve üstte açılma

## 1. Metin tekrarı: iki doğrulanmış hata

`preedit-fix.patch` iki ayrı sorunu giderir:

1. `commit_candidate()` normal kelime ve emoji kabulünden sonra predictor tamponunu temizliyordu, fakat Fcitx5'in panel preedit'i, istemciye gönderilen preedit ve aday listesi kalıyordu. Genel tuş geçişi yolunda da aynı eksik temizlik vardı. Var olan `clear_state()` çağrısı bu üç yolu artık birlikte temizler.
2. Satır içi tamamlama her öneriyi son ek sanıyordu. `dont` → `don't` düzeltmesinde `best.substr(4)` son `t` harfini tekrar ekleyerek `dontt` görüntüsü üretiyordu. Artık yalnız gerçekten önekten devam eden kelimelerde hayalet metin eklenir; apostrof/kelime içi düzeltme aday listesinde kalır.

Regresyon istemcisi artık `updatePreeditImpl()` bildirimini kaydediyor. Böylece yalnız motor tamponu değil, uygulamaya gösterilen geçici yazının da silindiği doğrulanıyor. `i dont` + Tab akışında sonuç `i don't`; preedit boş. Sonraki `t` yalnız yeni preedit olur. Normal `he` tamamlaması çalışmaya devam eder.

Doğrulama:
- İlk eski kod tekrar üretiminde 24 preedit/liste temizliği assertion'ı başarısız oldu.
- Temizlik düzeltmesinden sonra eklenen apostrof senaryosu ayrı olarak başarısız oldu; önek kontrolüyle geçti.
- Son kodda derleme ve **13/13 CTest testi başarılı**.
- Tab, Enter, tıklama, normal kelime/emoji/sonraki kelime, noktalama ve genel tuş geçişi kontrol edildi. Önceki URL, Ctrl/Alt, Shift ve yön tuşu testleri de geçti.
- Kurulum ön kontrolü **4/4**; `bash -n install.sh` başarılı.

### Bu düzeltmeyi kurmak

Açık yazılarını kaydet; normal kullanıcı terminalinde:

```bash
bash /home/ekrem/wrong/reports/smartcomplete-preedit/install.sh
```

Betik mevcut kaynak hashlerini kontrol eder, kaynak/eklentiyi yedekler, derler/test eder; başarılıysa yalnız SmartComplete eklentisini kurar ve Fcitx5'i yeniden başlatır. Hata olursa durur; otomatik geri alma yapmaz. **Gerçek depoya veya sisteme burada uygulanmadı.**

## 2. Üstte açılma: ayrı, isteğe bağlı Hyprland yaması

`hyprland-prefer-above.patch`, **Hyprland 0.56.2, commit efb50993780079460b0cbed1363e2166a2de1d9f** için hazırlanmıştır. SmartComplete deposuna değil, o sürümün Hyprland kaynak ağacına yöneliktir.

- Önce imlecin üstünü tercih eder.
- Üstte yer yoksa ve altta sığıyorsa altta gösterir.
- İki tarafta da sığmıyorsa üst ekran kenarına hizalar. Menü ekranın kendisinden büyükse taşma kaçınılmazdır; bu yama yeniden boyutlandırmaz.
- Yatay konum hesabı değiştirilmez.

**Etki yalnız SmartComplete ile sınırlı değildir:** aynı Hyprland IM popup yolunu kullanan diğer giriş yöntemleri de etkilenir. Bu nedenle normal `install.sh` bu yamayı uygulamaz, Hyprland derlemez veya değiştirmez.

`test_hyprland_geometry.py` verilen Hyprland kaynak dosyasından gerçek Y-konumlandırma bloğunu çıkarıp küçük C++ koordinat nesneleriyle derler. Orijinal kaynakta 9 vakanın 7'si üst-öncelikli beklentiye uymadı; yamalı blokta **9/9 geçti**. Testler orta/alt/üst sınır, tam sınırda sığma, negatif monitör koordinatı, pencere ofseti, kesirli değerler ve aşırı büyük popup durumlarını kapsar.

```bash
python3 /home/ekrem/wrong/reports/smartcomplete-preedit/test_hyprland_geometry.py \
  /path/to/Hyprland/src/managers/input/InputMethodPopup.cpp
```

Bu geometri testi **tam Hyprland derlemesi veya canlı compositor testi değildir**. Yama sabitlenmiş sürümün kaynak kopyasına başarıyla uygulandı; Hyprland'ın bütünü derlenmedi, paketlenmedi ve kurulmadı. Kullanımdaki pencere yöneticisini değiştirmeden önce paketleme, geri dönüş ve ayrı oturum testi gerekir. Uyumlu olmayan sürüme zorla uygulanmamalıdır.

Kaynak: https://github.com/hyprwm/Hyprland/blob/efb50993780079460b0cbed1363e2166a2de1d9f/src/managers/input/InputMethodPopup.cpp

## Sınırlar

Gerçek sosyal ağ yazı alanında canlı deneme yapılmadı. Bu paket kanıtlanan iki metin hatasını ve üst-öncelikli yerleşim için ayrı bir kaynak yamasını içerir; uygulamanın bütün olası hatalarının bittiği iddia edilmez. Testler ve kaynak kopyaları mevcut çalışma alanında tutuldu; gerçek SmartComplete/Hyprland kurulumu değiştirilmedi.
