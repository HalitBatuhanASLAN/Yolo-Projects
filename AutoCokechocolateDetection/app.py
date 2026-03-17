import gradio as gr
import cv2
from ultralytics import YOLO
import os

# 1. İş Güvenliği Uzmanımızı (YOLO Modelini) Yüklüyoruz
# Model dosyasının adını ve yolunu gerektiği gibi güncelleyin
model_path = 'best.pt' # Örneğin, Space'e yüklediğiniz model dosyasının adı
if os.path.exists(model_path):
    model = YOLO(model_path)
else:
    # Model dosyası bulunamazsa hata vermemesi için varsayılan bir model yüklüyoruz (test amaçlı)
    print(f"Uyarı: {model_path} bulunamadı, varsayılan yolov8n.pt yükleniyor.")
    model = YOLO('yolov8n.pt')

# 2. FOTOĞRAF ANALİZ FONKSİYONU
def foto_analiz(img):
    if img is None:
        return None
    # Güven eşiğini (conf) ihtiyaca göre ayarlayabilirsiniz
    sonuclar = model.predict(source=img, conf=0.40)
    # YOLO'nun çizdiği (baret/yelek işaretli) fotoğrafı alıyoruz
    cizilmis_foto = sonuclar[0].plot()
    # Web için renk formatını düzeltiyoruz (BGR'den RGB'ye)
    cizilmis_foto_rgb = cv2.cvtColor(cizilmis_foto, cv2.COLOR_BGR2RGB)
    return cizilmis_foto_rgb

# 3. VİDEO ANALİZ FONKSİYONU (Kare kare işleme ve kaydetme)
def video_analiz(video_path):
    if video_path is None:
        return None
        
    cikis_video_adi = "islenmis_video.mp4"
    
    # Video dosyasını açma
    kamera = cv2.VideoCapture(video_path)
    
    # Orijinal videonun özelliklerini alma
    fps = int(kamera.get(cv2.CAP_PROP_FPS))
    genislik = int(kamera.get(cv2.CAP_PROP_FRAME_WIDTH))
    yukseklik = int(kamera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Çıktı videosu için kaydedici (VideoWriter) oluşturma
    # 'mp4v' codec'i web tarayıcılarında iyi çalışır
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    kaydedici = cv2.VideoWriter(cikis_video_adi, fourcc, fps, (genislik, yukseklik))
    
    # Videoyu kare kare işleme döngüsü
    while kamera.isOpened():
        ret, frame = kamera.read()
        if not ret:
            break # Video bittiğinde döngüden çık
            
        # YOLO ile mevcut kareyi analiz et (verbose=False logları temiz tutar)
        # Hız kazanmak için kare boyutunu düşürmeyi düşünebilirsiniz (imgsz=320 gibi)
        sonuclar = model.predict(source=frame, conf=0.40, verbose=False)
        
        # Tespit sonuçlarını kare üzerine çiz
        cizilmis_kare = sonuclar[0].plot()
        
        # İşlenmiş kareyi çıktı videosuna yaz
        kaydedici.write(cizilmis_kare)
        
    # Kaynakları serbest bırakma
    kamera.release()
    kaydedici.release()
    
    # İşlenmiş videonun dosya yolunu Gradio'ya geri gönder
    return cikis_video_adi

# 4. SEKME (TAB) TABANLI MODERN WEB ARAYÜZÜ (gr.Blocks kullanarak)
# gr.themes.Soft() ile şık ve yumuşak bir tema seçiyoruz
with gr.Blocks(theme=gr.themes.Soft()) as arayuz:
    gr.Markdown("# 👷‍♂️ Otonom İş Güvenliği Denetmeni (Fotoğraf ve Video Analizi)")
    gr.Markdown("""
    Bu yapay zeka uygulaması, şantiye veya fabrika gibi endüstriyel ortamlarda iş güvenliği kurallarına uyumu denetler. 
    Lütfen analiz yapmak istediğiniz dosya türünü (Fotoğraf veya Video) sekmelerden seçin.
    
    Aşağıdaki sınıfları tespit edebilir:
    - **helmet** (baret takan) / **no helmet** (baret takmayan)
    - **vest** (yelek takan) / **no vest** (yelek takmayan)
    - **person** (insan)
    """)
    
    # --- BİRİNCİ SEKME: FOTOĞRAF ---
    with gr.Tab("📷 Fotoğraf Analizi"):
        gr.Markdown("Lütfen analiz etmek istediğiniz şantiye fotoğrafını yükleyin veya kameranızla çekin.")
        with gr.Row():
            # sources=["upload", "webcam"] hem dosya yükleme hem de anlık çekim sunar
            foto_girdi = gr.Image(sources=["upload", "webcam"], type="numpy", label="Şantiye Fotoğrafı")
            foto_cikti = gr.Image(type="numpy", label="Analiz Sonucu")
        foto_buton = gr.Button("Fotoğrafı Analiz Et", variant="primary")
        # Buton tıklanınca foto_analiz fonksiyonunu çalıştır
        foto_buton.click(fn=foto_analiz, inputs=foto_girdi, outputs=foto_cikti)
        
    # --- İKİNCİ SEKME: VİDEO ---
    with gr.Tab("🎥 Video Analizi"):
        gr.Markdown("Lütfen analiz etmek istediğiniz kısa şantiye videosunu yükleyin.")
        gr.Warning("⚠️ **Önemli Uyarı:** Ücretsiz bulut sunucularında (CPU) video işleme işlemi, videonun uzunluğuna ve kalitesine bağlı olarak birkaç dakika sürebilir. Testleriniz için 5-10 saniyelik kısa videolar yüklemeniz önerilir.")
        with gr.Row():
            video_girdi = gr.Video(label="Şantiye Videosu")
            video_cikti = gr.Video(label="İşlenmiş Video")
        video_buton = gr.Button("Videoyu Analiz Et", variant="primary")
        # Buton tıklanınca video_analiz fonksiyonunu çalıştır
        video_buton.click(fn=video_analiz, inputs=video_girdi, outputs=video_cikti)

# 5. Sunucuyu Başlat (local_files=True, Space'de yerel dosyaları kullanmak için önemli)
if __name__ == "__main__":
    # share=True yerel testler için genel bir bağlantı oluşturur
    # Space'e yüklerken launch() parametresiz bırakılabilir
    arayuz.launch()