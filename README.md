# Ok.ru Proxy Player

OK.ru videolarını farklı görüntü kalitelerinde oynatmak için geliştirilmiş, FastAPI ve Video.js tabanlı hafif bir video oynatıcı.

## Özellikler

- OK.ru üzerinden video bilgilerinin alınması
- Mevcut görüntü kaliteleri arasında geçiş
- Video akışını proxy üzerinden aktarma
- HTTP Range desteği ile videoda ileri ve geri sarma
- Kalite değiştirirken oynatma konumunu koruma
- Mobil uyumlu arayüz
- Tek Python dosyasıyla çalışma

## Gereksinimler

- Python 3.9 veya üzeri
- İnternet bağlantısı
- Erişilebilir bir OK.ru video bağlantısı

## Kurulum

Depoyu bilgisayarına indir:

```bash
git clone https://github.com/onuronion/akis-player.git
cd akis-player
```

Gerekli kütüphaneleri yükle:

```bash
pip install -r requirements.txt
```

## Kullanım

Uygulamayı başlat:

```bash
python main.py
```

İstendiğinde OK.ru videoembed bağlantısını gir:

```text
https://ok.ru/videoembed/VIDEO_ID
```

Video bilgileri alındıktan sonra tarayıcıdan şu adresi aç:

http://localhost:8000

Mevcut görüntü kalitelerinden birini seçerek videoyu oynatabilir ve kaliteyi değiştirebilirsin.

## API Uç Noktaları

| Adres | Açıklama |
|---|---|
| `/` | Video oynatıcı arayüzü |
| `/api/info` | Video bilgileri ve mevcut kaliteler |
| `/video.mp4?quality=sd` | Seçilen kalitedeki video akışı |

Desteklenen kalite adları, OK.ru tarafından döndürülen verilere bağlıdır. `mobile`, `lowest`, `low`, `sd`, `hd` ve `full` yaygın örneklerdir.

## Sınırlamalar

- OK.ru sayfa yapısındaki değişiklikler metadata alımını bozabilir.
- Bazı videolar oturum açmayı gerektirebilir veya erişime kapalı olabilir.
- Video.js harici bir CDN üzerinden yüklenir.
- Video bilgileri ve bağlantıları bellekte tutulur; uygulama yeniden başlatıldığında silinir.
- Kimlik doğrulama ve erişim denetimi varsayılan olarak bulunmaz. İnternete açık bir sunucuda ek güvenlik önlemleri alınmalıdır.

## Sorumluluk Reddi

Ok.ru Proxy Player, eğitim ve geliştirme amacıyla hazırlanmıştır. Yalnızca erişim hakkına sahip olduğun videolar için kullan. İlgili telif haklarına ve OK.ru kullanım koşullarına uymak kullanıcının sorumluluğundadır.
