import cv2
import numpy as np
import config

class HUDVisualizer:
    def __init__(self):
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        
    def draw_glass_rect(self, img, pt1, pt2, color, alpha=0.5):
        """Modern, yarı şeffaf bir yüzey oluşturur."""
        overlay = img.copy()
        cv2.rectangle(overlay, pt1, pt2, color, cv2.FILLED)
        return cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)

    def draw_action_hud(self, img, action_msg):
        """Ekranın üst kısmına profesyonel bir aksiyon bildirim paneli çizer."""
        if action_msg:
            h, w, _ = img.shape
            # Cam Panel
            img = self.draw_glass_rect(img, (w//2 - 200, 20), (w//2 + 200, 80), config.COLOR_BLACK, 0.7)
            # Kenarlık çizgisi (Neon efekti için ince)
            cv2.rectangle(img, (w//2 - 200, 20), (w//2 + 200, 80), config.COLOR_CYAN, 1)
            
            # Aksiyon Metni
            text_size = cv2.getTextSize(action_msg, self.font, 0.8, 2)[0]
            text_x = (w - text_size[0]) // 2
            cv2.putText(img, action_msg, (text_x, 60), self.font, 0.8, config.COLOR_WHITE, 2)
            
            # Swipe Okları (Eğer mesajda NEXT veya PREV varsa)
            if "NEXT" in action_msg:
                cv2.putText(img, ">>>", (w//2 + 210, 60), self.font, 1, config.COLOR_GREEN, 3)
            elif "PREV" in action_msg:
                cv2.putText(img, "<<<", (w//2 - 280, 60), self.font, 1, config.COLOR_RED, 3)
                
        return img

    def draw_volume_gauge(self, img, angle):
        """Ses modu için sağ tarafa dikey, şık bir gösterge."""
        h, w, _ = img.shape
        x, y, bw, bh = w - 60, h // 2 - 100, 25, 200
        
        # Arka plan barı
        img = self.draw_glass_rect(img, (x, y), (x + bw, y + bh), config.COLOR_BLACK, 0.5)
        
        # Doluluk seviyesi (Hassasiyeti görselleştiriyoruz)
        fill = int(np.interp(abs(angle), [0, 15], [0, bh]))
        color = config.COLOR_GREEN if angle > 0 else config.COLOR_RED
        
        # Dinamik dolan bar
        cv2.rectangle(img, (x, y + bh - fill), (x + bw, y + bh), color, cv2.FILLED)
        cv2.putText(img, "VOL", (x - 10, y - 20), self.font, 0.6, config.COLOR_WHITE, 1)
        return img

    def draw_scroll_hud(self, img, hand_lms, h, w):
        """Scroll yaparken parmağın yanında yukarı/aşağı okları gösterir."""
        # Serçe parmak ucu
        tip = hand_lms.landmark[20]
        cx, cy = int(tip.x * w), int(tip.y * h)
        
        # Parmağın etrafına takip halkası
        cv2.circle(img, (cx, cy), 15, config.COLOR_CYAN, 2)
        
        # Yukarı/Aşağı ok sembolleri
        cv2.line(img, (cx, cy - 30), (cx, cy - 50), config.COLOR_GREEN, 2) # Yukarı ok
        cv2.line(img, (cx, cy + 30), (cx, cy + 50), config.COLOR_RED, 2)   # Aşağı ok
        return img

    def draw_wolf_effect(self, img, hand_lms, w, h):
        """Kurt işareti yapıldığında ekrana 'Focus' efekti verir."""
        # İşaret ve Serçe parmak uçları (4, 8, 20)
        for idx in [8, 20]:
            cx, cy = int(hand_lms.landmark[idx].x * w), int(hand_lms.landmark[idx].y * h)
            # Hedefleme dairesi
            cv2.circle(img, (cx, cy), 25, config.COLOR_RED, 1)
            cv2.line(img, (cx-35, cy), (cx+35, cy), config.COLOR_RED, 1)
            cv2.line(img, (cx, cy-35), (cx, cy+35), config.COLOR_RED, 1)
        return img

    def draw_lock_warning(self, img):
        """Sistem kilitlenirken tam ekran bir uyarı flaşı."""
        h, w, _ = img.shape
        # Ekranın etrafına kırmızı kalın bir çerçeve
        cv2.rectangle(img, (0, 0), (w, h), config.COLOR_RED, 20)
        cv2.putText(img, "LOCKING SYSTEM...", (w//2-150, h//2), self.font, 1.2, config.COLOR_WHITE, 3)
        return img