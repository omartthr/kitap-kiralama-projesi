from flask import Flask, request, jsonify, render_template, session, redirect
import boto3
import uuid
import dotenv
import os
from dotenv import load_dotenv

# .env dosyasındaki verileri yükle
# Dosya adın 'key.env' olduğu için bunu belirtmeliyiz
load_dotenv("key.env") 

# Değişkenleri dosyadan çek
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# 3. Flask uygulamasını BURADA tanımla (Hata buradaydı)
app = Flask(__name__)
app.secret_key = 'gizli-anahtar'

dynamodb = boto3.resource('dynamodb',aws_access_key_id = AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name='eu-north-1')

kitaplar_tablosu = dynamodb.Table('kitaplar')
kullanicilar_tablosu = dynamodb.Table('kullanicilar')



@app.route("/index.html")
def ana_sayfa():
    return render_template("index.html")
@app.route('/')
def index():
    return render_template('giris.html')
@app.route('/kitap-ekle', methods=['POST'])
def kitap_ekle():
    veri = request.get_json()
    kitap_id = str(uuid.uuid4())
    veri['kitap_id'] = kitap_id

    mevcut_kitaplar = kitaplar_tablosu.scan().get('Items', [])
    veri['sira'] = len(mevcut_kitaplar) + 1

    veri.setdefault('sube', 'Genel')  # Şube girilmezse genel
    veri.setdefault('durum', 'mevcut')  # 'mevcut' ya da 'mevcut degil'

    kitaplar_tablosu.put_item(Item=veri)
    return jsonify({'durum': 'eklendi', 'kitap_id': kitap_id})


@app.route('/api/kayit', methods=['POST'])
def kayit():
    veri = request.get_json()
    email = veri.get("email")
    isim = veri.get("isim")
    sifre = veri.get("sifre")
    tip = veri.get("tip", "kullanici")  # default: kullanıcı
    kullanici_id = str(uuid.uuid4())

    # Zaten var mı kontrolü
    response = kullanicilar_tablosu.get_item(Key={"email": email})
    if 'Item' in response:
        return jsonify({"hata": "Bu e-posta ile kayıtlı kullanıcı var."}), 400

    kullanicilar_tablosu.put_item(Item={
        "email": email,
        "isim": isim,
        "sifre": sifre,
        "tip": tip,
        "kullanici_id": kullanici_id
    })

    session["email"] = email
    session["tip"] = tip
    return jsonify({"durum": "ok"})


@app.route('/api/giris', methods=['POST'])
def giris():
    veri = request.get_json()
    email = veri.get("email")
    sifre = veri.get("sifre")
    tip = veri.get("tip")

    response = kullanicilar_tablosu.get_item(Key={"email": email})
    kullanici = response.get("Item")

    if not kullanici or kullanici["sifre"] != sifre or kullanici["tip"] != tip:
        return jsonify({"hata": "Geçersiz giriş bilgileri"}), 401

    session["email"] = email
    session["tip"] = tip
    return jsonify({"durum": "ok"})
@app.route('/kitap-sayisi', methods=['GET'])
def kitap_sayisi():
    response = kitaplar_tablosu.scan(Select='COUNT')
    return jsonify({'toplam': response.get('Count', 0)})

@app.route('/api/kitaplar')
def kitaplari_getir():
    response = kitaplar_tablosu.scan()
    kitaplar = response.get("Items", [])
    return jsonify(kitaplar)

@app.route('/api/kategori-kitaplar')
def kategoriye_gore_kitaplar():
    kategori = request.args.get('kategori', '').lower().strip()
    if not kategori:
        return jsonify({"error": "Kategori gerekli"}), 400

    response = kitaplar_tablosu.scan()
    kitaplar = response.get("Items", [])

    filtrelenmis = [
        kitap for kitap in kitaplar
        if kitap.get("kategori", "").lower() == kategori
    ]

    return jsonify(filtrelenmis)


@app.route("/kategori.html")
def kategori_sayfasi():
    return render_template("kategori.html")


@app.route("/kitap.html")
def kitap_sayfasi():
    return render_template("kitap.html")

@app.route("/giris.html")
def giris_sayfasi():
    return render_template("giris.html")


@app.route("/kitaplarim.html")
def kitaplarim():
    return render_template("kitaplarim.html")


@app.route('/api/kitap-ara')
def kitap_ara():
    sorgu = request.args.get("q", "").lower().strip()
    if not sorgu:
        return jsonify({"error": "Arama terimi gerekli"}), 400

    response = kitaplar_tablosu.scan()
    kitaplar = response.get("Items", [])

    eslesenler = [
        kitap for kitap in kitaplar
        if sorgu in kitap.get("isim", "").lower() or sorgu in kitap.get("yazar", "").lower()
    ]

    return jsonify(eslesenler)

@app.route('/api/kirala', methods=['POST'])
def kitap_kirala():
    if 'email' not in session:
        
        return jsonify({"error": "Oturum bulunamadı"}), 401

    veri = request.get_json()
    kitap_id = veri.get("kitap_id")
    email = session['email']

    if not kitap_id:
        return jsonify({"error": "Kitap ID gerekli"}), 400
    
# 🔐 Tekrar kiralamayı engelle
    kullanici = kullanicilar_tablosu.get_item(Key={'email': email}).get("Item")
    kitaplarim = kullanici.get("kitaplarim", [])
    if kitap_id in kitaplarim:
        return jsonify({"error": "Bu kitap zaten sizin tarafınızdan kiralandı."}), 400

    kitap_response = kitaplar_tablosu.get_item(Key={'kitap_id': kitap_id})
    kitap = kitap_response.get('Item')
    
    if not kitap:
        return jsonify({"error": "Kitap bulunamadı"}), 404

    if kitap.get("durum", "").lower() != "mevcut":
        return jsonify({"error": "Kitap zaten kiralanmış"}), 400

    # Kitap durumunu güncelle
    kitaplar_tablosu.update_item(
        Key={'kitap_id': kitap_id},
        UpdateExpression="SET durum = :yeni_durum",
        ExpressionAttributeValues={':yeni_durum': 'Mevcut Değil'}
    )

    # Kullanıcıya kitap ID'sini ekle
    kullanicilar_tablosu.update_item(
        Key={'email': email},
        UpdateExpression="SET kitaplarim = list_append(if_not_exists(kitaplarim, :empty_list), :kitap)",
        ExpressionAttributeValues={
            ':kitap': [kitap_id],
            ':empty_list': []
        }
    )

    return jsonify({"durum": "kiralandı"})

@app.route('/api/kullanicinin-kitaplari')
def kullanici_kitaplari():
    if 'email' not in session:
        return jsonify({"error": "Giriş yapılmamış"}), 401

    email = session['email']
    sonuc = kullanicilar_tablosu.get_item(Key={'email': email})
    kullanici = sonuc.get("Item")

    if not kullanici:
        return jsonify([])

    kitap_id_listesi = list(set(kullanici.get("kitaplarim", [])))

    kitaplar = []

    for kitap_id in kitap_id_listesi:
        if isinstance(kitap_id, dict) and 'S' in kitap_id:
            kitap_id = kitap_id['S']  # DynamoDB'nin nested formatı için
        kitap = kitaplar_tablosu.get_item(Key={'kitap_id': kitap_id})
        if 'Item' in kitap:
            kitaplar.append(kitap['Item'])

    return jsonify(kitaplar)
@app.route('/api/onerilen-kitaplar')
def onerilen_kitaplar():
    query = request.args.get("q", "").lower().strip()
    if not query:
        return jsonify([])

    response = kitaplar_tablosu.scan()
    kitaplar = response.get("Items", [])

    # Basit öneri: isim ya da yazar içinde query geçen kitaplar
    eslesen = [
        kitap for kitap in kitaplar
        if query in kitap.get("isim", "").lower() or query in kitap.get("yazar", "").lower()
    ]

    # Farklı kitapları öner (query eşleşmeyen)
    digerler = [
        kitap for kitap in kitaplar
        if kitap not in eslesen and (
            any(word in kitap.get("isim", "").lower() for word in query.split()) or
            kitap.get("kategori", "").lower() in ["roman", "bilim", "tarih"]
        )
    ]

    return jsonify(digerler[:5])  # İlk 5 öneri dön


@app.route('/api/kirala-iptal', methods=['POST'])
def kiralamayi_iptal_et():
    if 'email' not in session:
        return jsonify({"error": "Oturum yok"}), 401

    veri = request.get_json()
    kitap_id = veri.get("kitap_id")
    email = session["email"]

    # Kullanıcı bilgilerini al
    sonuc = kullanicilar_tablosu.get_item(Key={'email': email})
    kullanici = sonuc.get("Item")

    if not kullanici:
        return jsonify({"error": "Kullanıcı bulunamadı"}), 404

    kitaplarim = kullanici.get("kitaplarim", [])
    try:
        index = kitaplarim.index(kitap_id)
    except ValueError:
        return jsonify({"error": "Kitap zaten çıkarılmış"}), 400

    # Kitap kullanıcı listesinden çıkarılır
    kullanicilar_tablosu.update_item(
        Key={'email': email},
        UpdateExpression=f"REMOVE kitaplarim[{index}]"
    )

    # Kitap tekrar "mevcut" olarak güncellenir
    kitaplar_tablosu.update_item(
        Key={'kitap_id': kitap_id},
        UpdateExpression="SET durum = :durum",
        ExpressionAttributeValues={":durum": "mevcut"}
    )

    return jsonify({"durum": "iptal edildi"})


@app.route("/api/kitap")
def kitap_detay():
    kitap_id = request.args.get('id')
    if not kitap_id:
        return jsonify({'error': 'ID girilmedi'}), 400

    response = kitaplar_tablosu.get_item(Key={'kitap_id': kitap_id})

    if 'Item' in response:
        return jsonify(response['Item'])
    else:
        return jsonify({'error': 'Kitap bulunamadı'}), 404

    # onceki = kitaplar_dict.get(sira - 1)
    # sonraki = kitaplar_dict.get(sira + 1)

    # return jsonify({
    #     'kitap': kitap,
    #     'onceki': onceki['isim'] if onceki else "Yok",
    #     'sonraki': sonraki['isim'] if sonraki else "Yok"
    # })

if __name__ == '__main__':
    app.run(debug=True)