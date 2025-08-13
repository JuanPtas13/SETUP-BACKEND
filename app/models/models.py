
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Text
from sqlalchemy.orm import relationship
from app.database import Base



# Modelo de Usuario
class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100))
    correo = Column(String(100))

# Modelo de Emocion
class Emocion(Base):
    __tablename__ = 'emociones'
    id = Column(Integer, primary_key=True, index=True)
    nombre_emocion = Column(String(50))

# Modelo de Captura
class Captura(Base):
    __tablename__ = 'capturas'
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    emocion_id = Column(Integer, ForeignKey('emociones.id'))
    puntos = Column(Text)
    fecha = Column(TIMESTAMP, default=TIMESTAMP)

    usuario = relationship('Usuario', back_populates="capturas")
    emocion = relationship('Emocion', back_populates="capturas")
