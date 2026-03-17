import gradio as gr
import cv2
from ultralytics import YOLO
import os

# 1. Kasiyer Yapay Zekamızı Yüklüyoruz
model_path = 'best.pt' # Hugging Face'e yüklediğin modelin adı buysa dokunma
if os.path.exists(model_path):
    model = YOLO(model_path)
else:
    model = YOLO('yolov8n.pt')

# 2. FOTOĞRAF ANALİZ FONKSİYONU
def foto_analiz(img):
    if img is None: return None
    sonuclar = model.predict(source=img, conf=0.40)
    cizilmis_foto = sonuclar[0].plot()
    return cv2.cvtColor(cizilmis_foto, cv2.COLOR_BGR2RGB)

# 3. VİDEO ANALİZ FONKSİYONU
def video_analiz(video_path):
    if video_path is None: return None
    cikis_video_adi = "islenmis_video.mp4"
    kamera = cv2.VideoCapture(video_path)
    fps = int(kamera.get(cv2.CAP_PROP_FPS))
    genislik = int(kamera.get(cv2.CAP_PROP_FRAME_WIDTH))
    yukseklik = int(kamera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    kaydedici = cv2.VideoWriter(cikis_video_adi, fourcc, fps, (genislik, yukseklik))
    
    while kamera.isOpened():
        ret, frame = kamera.read()
        if not ret: break
        sonuclar = model.predict(source=frame, conf=0.40, verbose=False)
        kaydedici.write(sonuclar[0].plot())
        
    kamera.release()
    kaydedici.release()
    return cikis_video_adi

# 4. MODERN WEB ARAYÜZÜ (OTONOM KASA)
with gr.Blocks(theme=gr.themes.Soft()) as arayuz:
    gr.Markdown("# 🛒 Yapay Zeka Otonom Kasa (Smart Retail AI)")
    gr.Markdown("""
    Amazon Go benzeri otonom mağaza asistanı. Kasaya koyduğunuz ürünleri saniyeler içinde tanır.
    
    **📋 Tanıyabildiği Ürünler Listesi:**
    * **İçecekler:** 🥤 Coca-Cola, Sprite, Doble Cola, Doble Cola Naranja
    * **Atıştırmalıklar:** 🍫 KitKat, Snickers, Mars, Cadbury
    """)
    
    with gr.Tab("📷 Fotoğraf & Webcam Analizi"):
        with gr.Row():
            foto_girdi = gr.Image(sources=["upload", "webcam"], type="numpy", label="Ürünü Göster / Fotoğraf Yükle")
            foto_cikti = gr.Image(type="numpy", label="Kasa Ekranı (Tespit Edilenler)")
        foto_buton = gr.Button("Ürünleri Okut 🧾", variant="primary")
        foto_buton.click(fn=foto_analiz, inputs=foto_girdi, outputs=foto_cikti)
        
    with gr.Tab("🎥 Video Analizi"):
        gr.Warning("⚠️ Kısa videolar (5-10 saniye) yüklemeniz tavsiye edilir.")
        with gr.Row():
            video_girdi = gr.Video(label="Kasa Bandı Videosu Yükle")
            video_cikti = gr.Video(label="İşlenmiş Kasa Videosu")
        video_buton = gr.Button("Videoyu Analiz Et", variant="primary")
        video_buton.click(fn=video_analiz, inputs=video_girdi, outputs=video_cikti)

if __name__ == "__main__":
    arayuz.launch()