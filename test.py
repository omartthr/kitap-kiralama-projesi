import requests

# Veritabanına kitap eklemeyi test etmeye yarıyor
# main çalışırken ekle

isim = input("Kitap adı: ")
yazar = input("Yazar: ")
aciklama = input("Açıklama: ")
sube = input("Şube: ")
durum = input("Durum: ")
kategori = input("Kategori: ")
gorsel_url = input("Görsel URL: ")

veri = {
    "isim": isim,
    "yazar": yazar,
    "aciklama": aciklama,
    "sube": sube,
    "durum": durum,
    "kategori": kategori,
    "gorsel_url": gorsel_url
}

res = requests.post("http://127.0.0.1:5000/kitap-ekle", json=veri)
print(res.json())
