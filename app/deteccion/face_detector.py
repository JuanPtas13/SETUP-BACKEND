import cv2
import mediapipe as mp

class FaceDetector:
    def __init__(self, min_detection_confidence=0.3):
        self.mp_face = mp.solutions.face_detection
        self.detector = self.mp_face.FaceDetection(model_selection=0,  # 0=caras cercanas, 1=caras lejanas
                                                   min_detection_confidence=min_detection_confidence)

    def detectar_rostros(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resultados = self.detector.process(rgb)
        return resultados

    def dibujar_rostros(self, frame, resultados):
        if resultados.detections:
            for detection in resultados.detections:
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, _ = frame.shape
                x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                             int(bboxC.width * iw), int(bboxC.height * ih)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        return frame
    
