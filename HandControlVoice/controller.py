import pyautogui
import time
import math
import ctypes 
from collections import deque
import config
from overlay_manager import overlay # Yeni OSD sistemimiz

class ActionController:
    def __init__(self):
        # Hareket takibi için kuyruklar
        self.pts = deque(maxlen=config.PTS_LEN)
        self.track_pts = deque(maxlen=config.TRACK_PTS_LEN)
        self.tab_pts = deque(maxlen=config.TAB_PTS_LEN)
        self.alt_tab_pts = deque(maxlen=10)
        
        # Durum değişkenleri
        self.last_action_time = 0
        self.accumulated_angle = 0
        self.prev_angle = None
        self.prev_y = None 

    def perform_actions(self, up, hand_lms, w, h, center_x):
        current_time = time.time()
        
        # --- JEST TANIMLARI ---
        is_wolf = up[1] == 1 and up[4] == 1 and up[2] == 0 and up[3] == 0
        is_tab_mode = up[0] == 1 and up[1] == 1 and up[2] == 1 and up[3] == 0 and up[4] == 0
        is_alt_tab_mode = up == [0, 1, 1, 1, 1]
        is_track_mode = up == [1, 1, 1, 1, 1]
        is_volume_mode = up == [0, 1, 0, 0, 0]
        is_scroll_mode = up == [0, 0, 0, 0, 1]
        is_lock_mode = up == [1, 0, 0, 0, 1]

        # --- AKSİYONLAR VE OSD BİLDİRİMLERİ ---

        # 1. WINDOWS LOCK (Baş + Serçe)
        if is_lock_mode:
            if current_time - self.last_action_time > config.COOLDOWN:
                overlay.show_message("🔒 SYSTEM LOCKED", duration=2.0)
                ctypes.windll.user32.LockWorkStation()
                self.last_action_time = current_time
                return "SYSTEM LOCKED"

        # 2. SMART SCROLL (Serçe) - OSD gerekmez, akışkan olmalı
        elif is_scroll_mode:
            current_y = hand_lms.landmark[20].y 
            if self.prev_y is not None:
                dy = current_y - self.prev_y 
                if abs(dy) > 0.005:
                    scroll_amount = int(-dy * 1000 * config.SCROLL_SENSITIVITY / 10)
                    pyautogui.scroll(scroll_amount)
            self.prev_y = current_y
            return "SCROLLING"

        # 3. MEDIA TOGGLE (Kurt)
        elif is_wolf:
            if current_time - self.last_action_time > config.COOLDOWN:
                pyautogui.press("playpause")
                overlay.show_message("🐺 MEDIA PLAY/PAUSE", duration=1.5)
                self.last_action_time = current_time
                return "MEDIA TOGGLE"

        # 4. TAB SWIPE (Üçlü Tabanca)
        elif is_tab_mode:
            self.tab_pts.append(center_x)
            if len(self.tab_pts) == 10 and current_time - self.last_action_time > config.COOLDOWN:
                diff_x = self.tab_pts[-1] - self.tab_pts[0]
                if diff_x > config.SWIPE_THRESHOLD:
                    pyautogui.hotkey('ctrl', 'tab')
                    overlay.show_message("📑 NEXT TAB")
                    self.last_action_time = current_time
                    self.tab_pts.clear(); return "TAB NEXT"
                elif diff_x < -config.SWIPE_THRESHOLD:
                    pyautogui.hotkey('ctrl', 'shift', 'tab')
                    overlay.show_message("📑 PREV TAB")
                    self.last_action_time = current_time
                    self.tab_pts.clear(); return "TAB PREV"

        # 5. ALT+TAB (Dörtlü Pençe)
        elif is_alt_tab_mode:
            self.alt_tab_pts.append(center_x)
            if len(self.alt_tab_pts) == 10 and current_time - self.last_action_time > config.COOLDOWN:
                diff_x = self.alt_tab_pts[-1] - self.alt_tab_pts[0]
                if diff_x > config.SWIPE_THRESHOLD:
                    pyautogui.hotkey('alt', 'tab')
                    overlay.show_message("🪟 SWITCH APP")
                    self.last_action_time = current_time
                    self.alt_tab_pts.clear(); return "APP NEXT"
                elif diff_x < -config.SWIPE_THRESHOLD:
                    pyautogui.hotkey('alt', 'shift', 'tab')
                    overlay.show_message("🪟 SWITCH APP")
                    self.last_action_time = current_time
                    self.alt_tab_pts.clear(); return "APP PREV"

        # 6. TRACK SWIPE (Tam Avuç)
        elif is_track_mode:
            self.track_pts.append(center_x)
            if len(self.track_pts) == 10 and current_time - self.last_action_time > config.COOLDOWN:
                diff_x = self.track_pts[-1] - self.track_pts[0]
                if diff_x > config.SWIPE_THRESHOLD:
                    pyautogui.press("nexttrack")
                    overlay.show_message("🎵 NEXT TRACK")
                    self.last_action_time = current_time
                    self.track_pts.clear(); return "TRACK NEXT"
                elif diff_x < -config.SWIPE_THRESHOLD:
                    pyautogui.press("prevtrack")
                    overlay.show_message("🎵 PREV TRACK")
                    self.last_action_time = current_time
                    self.track_pts.clear(); return "TRACK PREV"

        # 7. VOLUME (Tek İşaret)
        elif is_volume_mode:
            cx, cy = int(hand_lms.landmark[8].x * w), int(hand_lms.landmark[8].y * h)
            self.pts.append((cx, cy))
            if len(self.pts) > 10:
                x_avg = sum([p[0] for p in self.pts]) / len(self.pts)
                y_avg = sum([p[1] for p in self.pts]) / len(self.pts)
                
                # Açı hesaplama:
                # $current\_angle = \arctan2(cy - y\_avg, cx - x\_avg)$
                current_angle = math.degrees(math.atan2(cy - y_avg, cx - x_avg))
                
                if self.prev_angle is not None:
                    diff = current_angle - self.prev_angle
                    if diff > 180: diff -= 360
                    if diff < -180: diff += 360
                    self.accumulated_angle += diff
                    
                    if self.accumulated_angle > config.ANGLE_THRESHOLD:
                        pyautogui.press("volumeup")
                        # Ses modunda OSD sürekli çıkmasın diye küçük bir kontrol eklenebilir
                        self.accumulated_angle = 0
                    elif self.accumulated_angle < -config.ANGLE_THRESHOLD:
                        pyautogui.press("volumedown")
                        self.accumulated_angle = 0
                self.prev_angle = current_angle
            return "VOLUME MODE"
        
        else:
            self.pts.clear(); self.track_pts.clear()
            self.tab_pts.clear(); self.alt_tab_pts.clear()
            self.prev_angle = None; self.accumulated_angle = 0
            self.prev_y = None
            
        return None