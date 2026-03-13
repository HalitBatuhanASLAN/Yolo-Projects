import gradio as gr
import cv2
from ultralytics import YOLO

model = YOLO('best.pt')

def photo_alaysis(photo):
    results = model.predict(photo, conf = 0.5)
    selected_frame = results[0].plot()
    return cv2.cvtColor(selected_frame, cv2.COLOR_BGR2RGB)

def video_alaysis(video):
    output_video_path = "output_video.mp4"

    cam = cv2.VideoCapture(video)
    fps = int(cam.get(cv2.CAP_PROP_FPS))
    width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    storage = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    while cam.isOpened():
        ret, frame = cam.read()

        if not ret:
            break

        results = model.predict(frame, conf= 0.5, verbose=False)
        selected_frame = results[0].plot()
        storage.write(selected_frame)
    
    cam.release()
    storage.release()

    return output_video_path

# 4. SEKME (TAB) TABANLI MODERN WEB ARAYÜZÜ
with gr.Blocks(theme=gr.themes.Default()) as arayuz:
    gr.Markdown("# 👷‍♂️ Otonom İş Güvenliği Denetmeni")
    gr.Markdown("Şantiyedeki işçileri analiz eden yapay zeka. Lütfen yapmak istediğiniz analizi seçin:")
    
    # --- BİRİNCİ SEKME: FOTOĞRAF ---
    with gr.Tab("📷 Fotoğraf Analizi"):
        with gr.Row():
            foto_girdi = gr.Image(type="numpy", label="Şantiye Fotoğrafı Yükle")
            foto_cikti = gr.Image(type="numpy", label="Denetim Raporu")
        foto_buton = gr.Button("Fotoğrafı Analiz Et", variant="primary")
        foto_buton.click(fn=photo_alaysis, inputs=foto_girdi, outputs=foto_cikti)
        
    # --- İKİNCİ SEKME: VİDEO ---
    with gr.Tab("🎥 Video Analizi"):
        gr.Markdown("⚠️ **Dikkat:** Ücretsiz bulut sunucusunda (CPU) videonun işlenmesi süresi videonun uzunluğuna göre birkaç dakika sürebilir. Sistemin gücünü test etmek için 5-10 saniyelik kısa videolar yüklemeniz önerilir.")
        with gr.Row():
            video_girdi = gr.Video(label="Şantiye Videosu Yükle")
            video_cikti = gr.Video(label="İşlenmiş Video")
        video_buton = gr.Button("Videoyu Analiz Et", variant="primary")
        video_buton.click(fn=video_alaysis, inputs=video_girdi, outputs=video_cikti)

# 5. Sunucuyu Başlat
if __name__ == "__main__":
    arayuz.launch()