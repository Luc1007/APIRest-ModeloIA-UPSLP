from fastapi import HTTPException, APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
import pandas as pd
from typing import List
from model import cargar_modelo, hacer_prediccion
from pydantic import BaseModel, Field
import binascii
import pickle
import re

from database import SessionLocal
from models_sql import ModeloML

router = APIRouter()

modelo, mensaje_carga = cargar_modelo()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def convertir_entrada(entrada_str: str) -> List[float]:
    try:
        # Utilizar una expresión regular para extraer los números de la cadena
        numeros = re.findall(r"[-+]?\d*\.\d+|\d+", entrada_str)
        
        # Convertir los números extraídos a punto flotante
        entrada_lista = [float(num) for num in numeros]
        
        if len(entrada_lista) < 2:
            raise ValueError("La entrada debe contener al menos dos valores numéricos.")
        
        print(entrada_lista)
        return entrada_lista
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Error al convertir la entrada: {str(e)}")

def leer_datos_desde_excel(ruta_archivo):
    if not os.path.exists(ruta_archivo):
        raise HTTPException(status_code=400, detail="El archivo de Excel no existe.")
    
    df = pd.read_excel(ruta_archivo)
    # Suponiendo que los datos están en la primera columna
    datos_entrada = df.iloc[:, 0].tolist()
    return datos_entrada

@router.post("/predict/{modelo_id}")
async def get_prediction(modelo_id: int, archivo: UploadFile = File(None), tipo_archivo: str = "excel", db: Session = Depends(get_db)):
    # Buscar el modelo en la base de datos por ID
    db_modelo = db.query(ModeloML).filter(ModeloML.id == modelo_id).first()
    if not db_modelo:
        raise HTTPException(status_code=404, detail="Modelo no encontrado")
    
    # Mostrar el nombre del modelo obtenido de la base de datos
    print(f"Nombre del modelo cargado: {db_modelo.nombre_archivo}")
    
    # Deserializar el modelo binario
    try:
        modelo_binario = binascii.unhexlify(db_modelo.modelo_binario)
        modelo = pickle.loads(modelo_binario)
    except (binascii.Error, pickle.UnpicklingError) as e:
        raise HTTPException(status_code=500, detail=f"Error deserializando el modelo: {str(e)}")

    # Convertir la entrada
    entrada_lista = []
    if archivo:
        print("Archivo recibido")
        if tipo_archivo == "txt":
            contenido = (await archivo.read()).decode("utf-8")
            entrada_lista = convertir_entrada(contenido)
        elif tipo_archivo == "excel":
            df = pd.read_excel(archivo.file, header=None)
            entrada_lista = df.iloc[0].tolist()
            print("Datos extraídos del archivo Excel:", entrada_lista)
        else:
            raise HTTPException(status_code=400, detail="Tipo de archivo no soportado.")

    # Validar la entrada
    if len(entrada_lista) < 2:
        raise HTTPException(status_code=400, detail="La lista de características debe contener más de un elemento.")

   # Leer los índices de las características seleccionadas desde el archivo
    with open('indices_caracteristicas_seleccionadas.txt', 'r') as f:
        indices_caracteristicas_seleccionadas = [int(line.strip()) for line in f]

    # Filtrar la entrada utilizando los índices seleccionados
    try:
        entrada_filtrada = [entrada_lista[i] for i in indices_caracteristicas_seleccionadas]
    except IndexError:
        raise HTTPException(status_code=400, detail="Los datos de entrada no tienen suficientes características.")

    print("entrada filtrada: ", entrada_filtrada)
    # Realizar la predicción utilizando la entrada filtrada
    try:
        prediccion, mensaje_prediccion = hacer_prediccion(modelo, entrada_filtrada)
        return {"prediccion": prediccion, "mensaje": mensaje_prediccion}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

