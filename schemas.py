from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import base64

class ModeloMLCreate(BaseModel):
    nombre_archivo: str = Field(..., min_length=1, max_length=255)
    descripcion: Optional[str] = Field(None, max_length=500)
    ruta_archivo: str


class ModeloMLShow(BaseModel):
    id: int
    nombre_archivo: str
    descripcion: Optional[str] = None
    tipo_modelo: Optional[str] = None
    fecha_creacion: datetime
    metricas: Optional[str] = None
    # No incluimos el campo modelo_binario para no enviar datos binarios grandes en la respuesta

class ModeloMLShow(BaseModel):
    id: int
    nombre_archivo: str
    descripcion: Optional[str] = None
    fecha_creacion: datetime

    class Config:
        orm_mode = True
        
class ModeloMLUpdate(BaseModel):
    nombre_archivo: Optional[str] = Field(None, description="Nombre del archivo del modelo")
    descripcion: Optional[str] = Field(None, description="Descripción del modelo")
    # No incluimos modelo_binario aquí, asumiendo que la actualización del binario se manejará de manera diferente
    class Config:
        from_attributes = True
