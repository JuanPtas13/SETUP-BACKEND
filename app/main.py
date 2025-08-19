from fastapi import FastAPI, Depends, HTTPException, Response, UploadFile, File,WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger
import logging
import numpy as np
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from os import getcwd, path
import base64
import cv2
import os
# Import internos
from app.deteccion.hand_detector import HandDetector
from app.database import engine, SessionLocal
from app.models.models import Base
from app.services.video_prosesing import VideoProcessingService  
from app.deteccion.face_detector import FaceDetector

app = FastAPI()

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

# Inicializar servicios globalmente
hand_detector = HandDetector()
face_detector = FaceDetector()
video_service = VideoProcessingService()

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Logs de debugging para troubleshooting
logging.basicConfig(level=logging.DEBUG)

# -------------------- Rutas --------------------

@app.get("/")
def root():
    logger.info("Se accedió a la raíz") 
    return {"mensaje": "Backend funcionando"}

@app.get("/health")
def health():
    logger.info("Se accedió a Health")
    return {"status": "ok"}

# Dependencia para la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/db")
def check_database_connection(db: Session = Depends(get_db)):
    logger.info("Se accedió a la base de datos")
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "mensaje": "Conexión a base de datos exitosa"
        }
    except Exception as e:
        return {
            "status": "error",
            "mensaje": f"Fallo en la conexión: {str(e)}"
        }

@app.get("/camara")
def abrir_camara():
    logger.info("Se accedió a la camara")
    file_path = os.path.join(os.path.dirname(__file__), "..", "client", "index.html")
    return FileResponse(file_path)
   
detector = HandDetector()


# Servir HTML
             
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        if data.startswith("data:image"):
            data = data.split(",")[1]

        img_bytes = base64.b64decode(data)
        npimg = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

        if frame is not None:
                # --- Detección de Manos ---
            hands = hand_detector.detect_hands_in_frame(frame)
            serialized_hands = []
            if isinstance(hands, list):
                for hand in hands:
                    if hasattr(hand, 'landmark'):
                        hand_landmarks = []
                        for landmark in hand.landmark:
                            hand_landmarks.append({
                                'x': landmark.x,
                                'y': landmark.y,
                                'z': landmark.z
                            })
                        serialized_hands.append(hand_landmarks)

                # --- Detección de Caras ---
            face_results = face_detector.detectar_rostros(frame)
            serialized_faces = []
            if face_results.detections:
                for detection in face_results.detections:
                    bboxC = detection.location_data.relative_bounding_box
                    ih, iw, _ = frame.shape
                    x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                                    int(bboxC.width * iw), int(bboxC.height * ih)
                    serialized_faces.append({
                            'xmin': x,
                            'ymin': y,
                            'width': w,
                            'height': h,
                            'score': detection.score[0] # El score de confianza
                        })
                    # Opcional: dibujar los rostros en el frame antes de enviarlo de vuelta si quisieras visualizarlos en el servidor
                    # frame = face_detector.dibujar_rostros(frame, face_results)


                # Retornar landmarks de manos y datos de caras al cliente
            await websocket.send_json({
                "manos": serialized_hands,
                "cara": serialized_faces # Añadir los datos de la cara aquí
            })
    

 
# -------------------- CORS --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
