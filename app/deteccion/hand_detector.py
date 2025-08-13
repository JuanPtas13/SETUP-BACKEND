import cv2
import mediapipe as mp


class HandDetector:
    def __init__(self, max_hands=2, confidence_threshold=0.5):
        self.max_hands = max_hands
        self.confidence_threshold = confidence_threshold
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=self.max_hands,
            min_detection_confidence=self.confidence_threshold,
            min_tracking_confidence=self.confidence_threshold
        )
        self.mp_draw = mp.solutions.drawing_utils  # Para dibujar puntos

    def detect_hands_in_frame(self, frame):
        # Convierte BGR a RGB
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Procesa la imagen para detectar manos
        results = self.hands.process(image_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Dibuja los puntos y conexiones en la imagen original
                self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
            return results.multi_hand_landmarks
        return None

    def __del__(self):
        self.hands.close()