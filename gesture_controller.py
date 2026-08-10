import cv2
import pygame
import math

try:
    import mediapipe as mp
    HAS_MEDIAPIPE = True
except ImportError:
    HAS_MEDIAPIPE = False

class HandController:
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        
        self.hand_detected = False
        self.target_y = screen_height // 2
        self.is_pinching = False
        self.cap = None

        if HAS_MEDIAPIPE and hasattr(mp, 'solutions'):
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.cap = None
        else:
            self.hands = None

    def update(self):
        if not self.cap or not self.hands:
            self.hand_detected = False
            return

        success, frame = self.cap.read()
        if not success:
            self.hand_detected = False
            return

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            self.hand_detected = True
            hand = results.multi_hand_landmarks[0]
            
            index_tip = hand.landmark[8]
            self.target_y = int(index_tip.y * self.height)

            thumb_tip = hand.landmark[4]
            dist = math.hypot(
                (index_tip.x - thumb_tip.x) * self.width,
                (index_tip.y - thumb_tip.y) * self.height
            )
            self.is_pinching = dist < 40
        else:
            self.hand_detected = False

    def draw_preview(self, surface, x=15, y=15):
        status_color = (0, 255, 120) if self.hand_detected else (255, 60, 80)
        pygame.draw.rect(surface, (20, 20, 30), (x, y, 140, 35), border_radius=6)
        pygame.draw.circle(surface, status_color, (x + 18, y + 17), 6)
        
        font = pygame.font.SysFont("Consolas", 12, bold=True)
        txt = "GESTURE: ON" if self.hand_detected else "NO HAND"
        lbl = font.render(txt, True, (255, 255, 255))
        surface.blit(lbl, (x + 32, y + 10))

    def release(self):
        if self.cap:
            self.cap.release()