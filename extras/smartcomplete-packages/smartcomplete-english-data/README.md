# SmartComplete — İngilizce veri genişletme yaması

**Yalnız paket hazırlandı. Gerçek depo, kurulu veriler ve çalışan Fcitx5 değiştirilmedi.**

## İnceleme sonucu

- Sözlükte `reschedule`, `onboarding`, `authentication` gibi güncel iş/teknoloji kelimeleri eksikti.
- `screenshot`, `workflow`, `accessibility` gibi mevcut kelimelerin sıklık kaydı yoktu. Sözlük yükleyicisi bunlara 1 puan veriyor; mevcut aday filtreleri bunları eleyebiliyor. Bu nedenle yalnız sözlük boyutunu artırmak yeterli değil.
- `data/rules/en_grammar_pair_rules.txt` içinde doğal `responsible for` kalıbı **-301** puanla cezalandırılıyordu; yamada **250** yapıldı.
- Önek tamamlaması gramer puanlarından yararlanıyor; sonraki kelime yolu ise ağırlıklı olarak bigram ve cümle devamı verilerini kullanıyor. Bu yüzden iki veri türü de genişletildi; algoritma değiştirilmedi.

## Kapsam ve değişiklikler

| Veri | Değişiklik |
|---|---|
| Sözlük | 23 yeni kelime |
| Sıklık/öncelik tablosu | 45 yeni kayıt: yeni kelimeler ve önceden puansız olan 22 kelime |
| Kelime çiftleri | 8 yeni bigram |
| Cümle devamları | 9 yeni kalıp |
| Gramer çiftleri | 6 yeni kural + `responsible for` düzeltmesi |
| Üç kelimeli gramer | 8 yeni kural |
| Test | Kaynak veriyle çalışan, 95 assertion içeren bir yeni CTest testi |

Puanlar, mevcut ölçeğe uygun **elle seçilmiş önceliklerdir**; ölçülmüş korpus kullanım sıklığı değildir. Mevcut frekans kayıtları değiştirilmedi. Yeni anahtarlar eklemeden önce tekrar kontrolü yapıldı; mevcut eski tekrarları temizleyen veya dosyaları topluca yeniden biçimlendiren bir değişiklik yoktur.

### Kullanıcıya yansıyan örnekler

- `resch` → `reschedule`
- `onbo` → `onboarding`
- `authent` → `authentication`
- `screensh` → `screenshot`
- `reprod` → `reproducible`
- `can we ` → `reschedule the meeting`
- `thanks for ` → `your feedback`
- `to reproduce ` → `the issue`

Bu örnekler yeni testte ilk üç aday arasında doğrulandı; her bağlamda daima birinci oldukları iddia edilmiyor. `how are` → `you doing`, `looking forward` → `to hearing`, `please let` → `me know` kontrolleri de korundu.

Türkçe, AI, tahmin motoru kodu, arayüz, Ctrl/Alt davranışı ve kullanıcı öğrenme dosyaları değiştirilmedi. Eklenen İngilizce satırlar bu görevde elle yazıldı; dış korpus veya yeni bağımlılık kullanılmadı.

## Paket

- `english-data.patch`: altı veri dosyası, `CMakeLists.txt` ve yeni `tests/english_data_regression.cpp`.
- `additions.json`: eklenen kelimeler, puanlar ve kalıpların tam dökümü.
- `base.sha256`: incelenen başlangıç dosyalarının kimliği; bilgi/karşılaştırma amaçlıdır.

Yama modern arayüz/ikon yamalarından ayrıdır. Üç yamanın aynı kaynak kopyasında birlikte uygulanması, derlenmesi ve test edilmesi doğrulandı.

**Kurulum sırası notu:** Modern arayüz paketinin `install.sh` betiği tam kaynak hashleriyle korumalıdır. O paketi de kuracaksan önce arayüz/ikon kurulumunu yap, sonra bu İngilizce yamasını uygula. İngilizce yaması `CMakeLists.txt` dosyasını değiştirdiği için eski arayüz kurulum betiğinin başlangıç hash kontrolü sonrasında haklı olarak durur; bu kontrolü kaldırma. Kaynak yamalarının kendileri birbiriyle uyumludur.

## Çalıştırılmış doğrulamalar

Bütün işlemler mevcut çalışma alanındaki geçici kopyalarda yapıldı:

1. Yeni `linuxcomplete_english_data_regression` testi **eski veriyle 95 kontrolden 36'sında başarısız** oldu. Eksik kelimeler/kalıplar ve yanlış gramer cezası gözlendi.
2. Aynı test yamalı veriyle **95 kontrol, 0 hata** verdi.
3. `rules_tool.py --rules-dir ... validate`: yamadan önce ve sonra başarılı.
4. `cmake --build ... -j4`: eklenti ve testler başarılı derlendi.
5. `ctest --test-dir ... --output-on-failure`: **13/13 test başarılı**.
6. Modern arayüz ve tray ikon yamaları da eklenince derleme ve **13/13 test tekrar başarılı**.
7. `git apply --check` ve geçici kopyaya gerçek uygulama başarılı; veri/test çıktıları test edilen kopyayla karşılaştırıldı.

Yeni test doğrudan kaynak `data/` dizinini yükler. Her tahmin senaryosu ayrı geçici HOME kullanır; öğrenilmiş kelimeler senaryolar arasında taşınmaz, AI kapalıdır. Büyük harfli önek, boş önek, kısa önek, bilinmeyen önek ve aday sayısı sınırı kontrol edilir. Gramer kontrolleri gerçek kural endekslerini sorgular; `i have attach` ve `can we rescheduled` gibi yanlış çekimlerin pozitif desteklenmemesi de kontrol edilir.

## Arayüz + ikon + İngilizce veriyi birlikte kurmak

Ek kurulum isteği için `install-all.sh` hazırlandı. Normal kullanıcı olarak, grafik oturumunun terminalinden çalıştırılır:

```bash
bash /home/ekrem/wrong/reports/smartcomplete-english-data/install-all.sh \
  /home/ekrem/smartcomplete light
```

`dark` argümanı koyu tema seçer. Açık metinlerini önce kaydet: bu akış önce modern arayüz/ikon paketini, ardından İngilizce veriyi kurar; Fcitx5 iki aşamada yeniden başlatılır. Kaynak/veri yedekleri kullanıcı state dizininde tutulur. Veri aşaması yalnız altı veri dosyasını günceller; profil, tema ve öğrenilmiş kelimeleri ezmez. Kullanıcı sözlüğü override'ı varsa yanlış veri yoluna kurmamak için durur.

**Bu betik gerçek sistemde çalıştırılmadı.** `bash -n` kontrolü geçti; uyguladığı üç yamanın tam sırası geçici kopyada uygulandı ve dosyalar test edilmiş birleşik kopyayla aynı çıktı. Sudo, kurulum ve yeniden başlatma adımları canlı olarak denenmedi.

Betik mevcut incelenmiş başlangıç durumunu bekler; daha önce modern paket kurulmuşsa hash/tema kontrolleri nedeniyle durabilir. Bu kontrolleri atlama, çıktıyı incele. Herhangi bir hata sonraki adımları durdurur; daha önce başarıyla uygulanmış aşamalar otomatik geri alınmaz. Kapanıştan sonraki hata Fcitx5'i durmuş bırakabilir. Çıktıdaki iki ayrı yedek yolunu sakla.

## Sonradan yalnız İngilizce yamayı uygulama ve test komutları

Bu komutlar burada gerçek depoda **çalıştırılmadı**. Uygulamak istediğinde terminalde kullanabilirsin; herhangi bir başarısızlık sonraki adımları durdurur:

```bash
bash <<'BASH'
set -Eeuo pipefail
cd /home/ekrem/smartcomplete
PATCH=/home/ekrem/wrong/reports/smartcomplete-english-data/english-data.patch
git apply --check "$PATCH"
git apply "$PATCH"
git diff --check
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr
cmake --build build --parallel 4
ctest --test-dir build -R '^linuxcomplete_english_data_regression$' --no-tests=error --output-on-failure
ctest --test-dir build --no-tests=error --output-on-failure
BASH
```

Bu blok kaynakları yamalar ve test eder; çalışan uygulamaya veri kurulumu yapmaz. Test başarısızlığında uygulanmış yama otomatik geri alınmaz. Kurulum ayrıca planlanmalıdır; motor `~/.local/share/linuxcomplete/dict` varsa kullanıcı veri yolunu, yoksa kurulu sistem veri yolunu kullanır. Yanlış veri kopyasını güncellemek canlı önerileri değiştirmeyebilir.

## Sınırlar

Canlı yazı alanında öneri kalitesi, kullanıcıya özel öğrenmeyle etkileşim ve geniş bir bağımsız İngilizce değerlendirme kümesi ölçülmedi. 95 kontrol, seçilmiş kullanım örneklerini doğrular; genel İngilizce doğruluğu veya yüzde olarak kalite artışı iddiası değildir. Mevcut binlerce gramer kaydı bütünüyle dilbilimsel denetimden geçirilmedi.
