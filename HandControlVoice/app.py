# app.py
from flask import Flask, render_template, Response
import cv2
import config
from hand_engine import HandEngine
from controller import ActionController
from visualizer import HUDVisualizer

app = Flask(__name__)

# Modülleri başlatıyoruz
engine = HandEngine()
controller = ActionController()
viz = HUDVisualizer()

def generate_frames():
    cap = cv2.VideoCapture(0)
    # Performans için çözünürlüğü web'e uygun tutalım
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            # 1. Görüntü İşleme (Aynı main.py mantığı)
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = engine.process_frame(img_rgb)

            if results.multi_hand_landmarks:
                for hand_lms in results.multi_hand_landmarks:
                    # MediaPipe Çizimi
                    engine.mp_draw.draw_landmarks(frame, hand_lms, engine.mp_hands.HAND_CONNECTIONS)
                    
                    # Analiz ve Aksiyon
                    up = engine.get_finger_status(hand_lms)
                    action_msg = controller.perform_actions(up, hand_lms, w, h, hand_lms.landmark[9].x)

                    # HUD Görselleştirme (Web ekranında görünecek olanlar)
                    frame = viz.draw_action_hud(frame, action_msg)
                    
                    if up == [0, 1, 0, 0, 0]: # Ses Barı
                        frame = viz.draw_volume_gauge(frame, controller.accumulated_angle)
                    
                    if up == [0, 0, 0, 0, 1]: # Scroll Takibi
                        frame = viz.draw_scroll_hud(frame, hand_lms, h, w)

            # 2. Görüntüyü Web Formatına (JPEG) Çevirme
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            # 3. Stream olarak gönder
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    """Ana sayfa (HTML dosyasını yükler)"""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Kamera görüntüsünün aktığı kanal"""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # Local olarak test etmek istersen:
    app.run(debug=True)