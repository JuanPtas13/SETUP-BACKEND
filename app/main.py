from fastapi import FastAPI, Depends, HTTPException, Response, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import logging
import numpy as np
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from os import getcwd, path
import base64
import cv2

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

@app.post("/frame")
async def process_frame(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        npimg = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

        # Procesar frame con el servicio de video
        result = video_service.process_frame(frame)

        return JSONResponse(content={"status": "ok", "result": result})
    except Exception as e:
        logger.error(f"Error procesando frame: {e}")
        return JSONResponse(content={"status": "error", "error": str(e)})

# -------------------- CORS --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
