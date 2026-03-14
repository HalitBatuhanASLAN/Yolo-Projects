# hand_engine.py
import mediapipe as mp
import config

class HandEngine:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            max_num_hands=config.MAX_NUM_HANDS,
            min_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE
        )

    def get_finger_status(self, hand_lms):
        fingers = []
        # 0: Baş Parmak
        if abs(hand_lms.landmark[4].x - hand_lms.landmark[3].x) > 0.05:
            fingers.append(1)
        else:
            fingers.append(0)
            
        # 1:İşaret, 2:Orta, 3:Yüzük, 4:Serçe
        for tip, pip in zip([8, 12, 16, 20], [6, 10, 14, 18]):
            if hand_lms.landmark[tip].y < hand_lms.landmark[pip].y:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers

    def process_frame(self, img_rgb):
        return self.hands.process(img_rgb)