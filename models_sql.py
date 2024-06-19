# app/models.py

from sqlalchemy import Column, Integer, String, Text, DateTime, BINARY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class ModeloML(Base):
    __tablename__ = 'modelos_ml'

    id = Column(Integer, primary_key=True)
    nombre_archivo = Column(String(255), nullable=False)
    descripcion = Column(Text)
    tipo_modelo = Column(String(100))
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    metricas = Column(Text)
    modelo_binario = Column(BINARY)

