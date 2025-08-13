from app.deteccion.hand_detector import HandDetector

class VideoProcessingService:
    def __init__(self):
        self.hand_detector = HandDetector()

    def process_frame(self, frame):
        hands = self.hand_detector.detect_hands_in_frame(frame)
        return frame, hands  # Devuelves la imagen procesada y los datos