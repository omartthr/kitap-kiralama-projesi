📚 Kitap Kiralama ve Yönetim Sistemi
Bu proje, Python Flask ve AWS DynamoDB kullanılarak geliştirilmiş, bulut tabanlı bir kütüphane yönetim sistemidir. Kullanıcıların kitapları görüntülemesine, sisteme yeni kitaplar eklemesine ve kiralama süreçlerini yönetmesine olanak tanır.

🛠 Kullanılan Teknolojiler
Backend: Python Flask

Veritabanı: AWS DynamoDB (NoSQL)

Frontend: HTML5, CSS3, Jinja2

Bulut Entegrasyonu: Boto3 SDK

Güvenlik: .env ile Çevre Değişkenleri Yönetimi

🚀 Özellikler
Dinamik Kitap Listeleme: DynamoDB üzerindeki kitap verilerinin gerçek zamanlı görüntülenmesi.

Kitap Ekleme Sistemi: test.py veya web arayüzü üzerinden JSON formatında veri girişi.

Güvenli Kimlik Doğrulama: Flask Session yönetimi ile kullanıcı girişi.

Bulut Tabanlı Yapı: Verilerin yerel yerine AWS üzerinde güvenli bir şekilde saklanması.

📁 Proje Yapısı
.
├── static/          # CSS ve Görsel dosyaları
├── templates/       # HTML şablonları (index, giris, kitap vb.)
├── main.py          # Flask uygulama sunucusu ve AWS bağlantısı
├── test.py          # API/Veritabanı test scripti
├── .gitignore       # Hassas verilerin gizlenmesi (key.env)
└── key.env          # AWS kimlik bilgileri (Yerelde tutulur)

🔧 Kurulum ve Çalıştırma
1- Gerekli kütüphaneleri yükleyin:
pip install flask boto3 python-dotenv requests
2- AWS Anahtarlarınızı Tanımlayın:
key.env dosyası oluşturun ve şu formatta doldurun:
AWS_ACCESS_KEY_ID=YOUR_KEY
AWS_SECRET_ACCESS_KEY=YOUR_SECRET
AWS_DEFAULT_REGION=eu-north-1
3- Uygulamayı başlatın:
python main.py

🎓 Akademik Not

Bu çalışma, Ankara Üniversitesi bünyesindeki yazılım geliştirme projelerim kapsamında, bulut bilişim ve NoSQL veritabanı mimarilerini deneyimlemek amacıyla geliştirilmiştir.
