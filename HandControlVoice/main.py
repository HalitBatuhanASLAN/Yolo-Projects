import cv2
import config
import time
from hand_engine import HandEngine
from controller import ActionController
from visualizer import HUDVisualizer

def main():
    # 1. Başlatmalar
    cap = cv2.VideoCapture(0)
    # Daha yüksek çözünürlük görsel şölenin kalitesini artırır
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    engine = HandEngine()
    controller = ActionController()
    viz = HUDVisualizer()

    print("--- SİSTEM GÖRSEL ŞÖLEN MODUNDA BAŞLATILDI ---")
    print("Çıkış yapmak için görüntü penceresindeyken 'q' tuşuna basın.")

    while cap.isOpened():
        success, img = cap.read()
        if not success:
            print("Kamera akışı kesildi.")
            break
        
        # Görüntü Ön İşleme
        img = cv2.flip(img, 1) # Aynalama (Selfie modu)
        h, w, _ = img.shape
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # MediaPipe Analizi
        results = engine.process_frame(img_rgb)

        if results.multi_hand_landmarks:
            for idx, hand_lms in enumerate(results.multi_hand_landmarks):
                # A. El İskeletini Çiz (Neon Tasarım)
                engine.mp_draw.draw_landmarks(
                    img, 
                    hand_lms, 
                    engine.mp_hands.HAND_CONNECTIONS,
                    engine.mp_draw.DrawingSpec(color=config.COLOR_CYAN, thickness=2, circle_radius=3),
                    engine.mp_draw.DrawingSpec(color=config.COLOR_WHITE, thickness=2)
                )
                
                # B. Parmak ve Aksiyon Analizi
                up = engine.get_finger_status(hand_lms)
                center_x = hand_lms.landmark[9].x
                action_msg = controller.perform_actions(up, hand_lms, w, h, center_x)

                # --- C. DİNAMİK GÖRSEL ŞÖLEN (HUD) ---

                # 1. Üst Aksiyon Paneli (Glassmorphism & Swipe Okları)
                img = viz.draw_action_hud(img, action_msg)
                
                # 2. Ses Seviyesi Göstergesi (Sağ taraftaki dikey Gauge)
                # Sadece ses modundaysak (Tek işaret parmağı) göster
                if up == [0, 1, 0, 0, 0]:
                    img = viz.draw_volume_gauge(img, controller.accumulated_angle)
                
                # 3. Akıllı Scroll Takibi (Serçe parmak yanındaki oklar)
                if up == [0, 0, 0, 0, 1]:
                    img = viz.draw_scroll_hud(img, hand_lms, h, w)
                
                # 4. Wolf (Kurt) Efekti (Parmak uçlarında crosshair/parlama)
                # Kurt işareti: İşaret ve Serçe açık, Orta ve Yüzük kapalı
                is_wolf = up[1] == 1 and up[4] == 1 and up[2] == 0 and up[3] == 0
                if is_wolf:
                    img = viz.draw_wolf_effect(img, hand_lms, w, h)
                
                # 5. Sistem Kilitleme Uyarısı (Kilitlenirken ekran flaşı)
                if action_msg == "SYSTEM LOCKED":
                    img = viz.draw_lock_warning(img)

        # Final Görüntüyü Ekrana Ver
        cv2.imshow("Hand Control Master Sci-Fi HUD", img)
        
        # 'q' ile güvenli çıkış
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Kaynakları serbest bırak
    cap.release()
    cv2.destroyAllWindows()
    print("Sistem kapatıldı. İyi günler!")

if __name__ == "__main__":
    main()

'''
.\venv\Scripts\activate
'''