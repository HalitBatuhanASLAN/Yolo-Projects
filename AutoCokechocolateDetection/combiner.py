import os
import shutil
import yaml

# --- AYARLAR ---
veri_seti_1 = "dataset1_kola"
veri_seti_2 = "dataset2_chocolate"
ana_hedef_klasor = "Otonom_Kasa_Master"

def yaml_oku(dosya_yolu):
    with open(dosya_yolu, 'r', encoding='utf-8') as f:
        veri = yaml.safe_load(f)
    # Roboflow liste veya sözlük verebilir, bunu standart listeye çeviriyoruz
    siniflar = veri.get('names', [])
    if isinstance(siniflar, dict):
        siniflar = list(siniflar.values())
    return siniflar

def etiketleri_kaydir_ve_kopyala(kaynak_klasor, hedef_klasor, offset=0):
    os.makedirs(hedef_klasor, exist_ok=True)
    if not os.path.exists(kaynak_klasor): return

    for dosya in os.listdir(kaynak_klasor):
        if not dosya.endswith('.txt'): continue
        
        kaynak_dosya = os.path.join(kaynak_klasor, dosya)
        hedef_dosya = os.path.join(hedef_klasor, dosya)
        
        with open(kaynak_dosya, 'r') as f:
            satirlar = f.readlines()
            
        with open(hedef_dosya, 'w') as f:
            for satir in satirlar:
                parcalar = satir.strip().split()
                if len(parcalar) > 0:
                    # İŞTE MÜHENDİSLİK DOKUNUŞU: Sınıf ID'sini offset kadar büyütüyoruz
                    yeni_id = int(parcalar[0]) + offset
                    yeni_satir = f"{yeni_id} " + " ".join(parcalar[1:]) + "\n"
                    f.write(yeni_satir)

def resimleri_kopyala(kaynak_klasor, hedef_klasor):
    os.makedirs(hedef_klasor, exist_ok=True)
    if not os.path.exists(kaynak_klasor): return
    for dosya in os.listdir(kaynak_klasor):
        if dosya.lower().endswith(('.png', '.jpg', '.jpeg')):
            shutil.copy(os.path.join(kaynak_klasor, dosya), os.path.join(hedef_klasor, dosya))

print("⚙️ Veri Setleri Birleştiriliyor, lütfen bekleyin...")

# 1. Sınıfları Öğren ve Ofset (Kaydırma) Değerini Bul
siniflar_1 = yaml_oku(os.path.join(veri_seti_1, 'data.yaml'))
siniflar_2 = yaml_oku(os.path.join(veri_seti_2, 'data.yaml'))
offset = len(siniflar_1) # Kola setinde 1 sınıf varsa, çikolata setindeki 0'lar 1 olacak.

# 2. İşlem Döngüsü (train, valid, test klasörleri için)
klasor_tipleri = ['train', 'valid', 'test']

for tip in klasor_tipleri:
    # Veri Seti 1'i Hedefe Kopyala (Değişiklik yapmadan)
    resimleri_kopyala(os.path.join(veri_seti_1, tip, 'images'), os.path.join(ana_hedef_klasor, tip, 'images'))
    etiketleri_kaydir_ve_kopyala(os.path.join(veri_seti_1, tip, 'labels'), os.path.join(ana_hedef_klasor, tip, 'labels'), offset=0)
    
    # Veri Seti 2'yi Hedefe Kopyala (Etiketleri KAYDIRARAK)
    resimleri_kopyala(os.path.join(veri_seti_2, tip, 'images'), os.path.join(ana_hedef_klasor, tip, 'images'))
    etiketleri_kaydir_ve_kopyala(os.path.join(veri_seti_2, tip, 'labels'), os.path.join(ana_hedef_klasor, tip, 'labels'), offset=offset)

# 3. Yeni Ortak data.yaml Dosyasını Yarat
yeni_siniflar = siniflar_1 + siniflar_2
yeni_yaml_icerigi = {
    'train': '../train/images',
    'val': '../valid/images',
    'test': '../test/images',
    'nc': len(yeni_siniflar),
    'names': yeni_siniflar
}

with open(os.path.join(ana_hedef_klasor, 'data.yaml'), 'w', encoding='utf-8') as f:
    yaml.dump(yeni_yaml_icerigi, f, sort_keys=False)

print(f"✅ Başarılı! Birleştirilmiş yeni veri setiniz '{ana_hedef_klasor}' klasöründe hazır.")
print(f"Ortak Sınıflarınız: {yeni_siniflar}")