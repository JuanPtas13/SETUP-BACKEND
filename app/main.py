from fastapi import FastAPI, Depends, HTTPException, Response, UploadFile, File,WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
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
from app.services.video_prosesing import VideoProcessingService  # Ruta corregida

app = FastAPI()

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

# Inicializar servicios globalmente
hand_detector = HandDetector()
video_service = VideoProcessingService()

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

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
        # Recibir frame como base64
        data = await websocket.receive_text()
        # Quitar el prefijo "data:image/jpeg;base64," si existe
        if data.startswith("data:image"):
            data = data.split(",")[1]

        # Convertir base64 a np.array
        img_bytes = base64.b64decode(data)
        npimg = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

        if frame is not None:
            # Detectar manos
            hands = detector.detect_hands_in_frame(frame)

            # Convertir el resultado a un formato JSON serializable
            serialized_hands = []
            if isinstance(hands, list):  # Verificar si hands es una lista
                for hand in hands:  # Iterar sobre cada mano detectada
                    if hasattr(hand, 'landmark'):  # Verificar si el objeto tiene el atributo 'landmark'
                        hand_landmarks = []
                        for landmark in hand.landmark:
                            hand_landmarks.append({
                                'x': landmark.x,
                                'y': landmark.y,
                                'z': landmark.z
                            })
                        serialized_hands.append(hand_landmarks)

            # Retornar landmarks al cliente
            await websocket.send_json({"manos": serialized_hands})

 
# -------------------- CORS --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
