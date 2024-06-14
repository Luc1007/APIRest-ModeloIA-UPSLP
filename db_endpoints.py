from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Depends
from typing import Optional
from sqlalchemy.orm import Session
from models_sql import ModeloML
from schemas import ModeloMLCreate, ModeloMLShow, ModeloMLUpdate
from database import SessionLocal
import pickle
import binascii
import os
from model import *
router = APIRouter()

modelo_guardado, mensaje_carga = cargar_modelo()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def entrenar_y_seleccionar_modelo(
        nombre_archivo: str, 
        ruta_archivo: str,
        descripcion: Optional[str], 
        archivo: UploadFile = File(None),
        db: Session = Depends(get_db)):
    try:
        # Verificar que el archivo ha sido cargado
        if not archivo:
            raise HTTPException(status_code=400, detail="No se ha cargado ningún archivo")

        # Leer el archivo en memoria
        try:
            contenido = await archivo.read()
            contenido_decodificado = contenido.decode('utf-8')
            data = cargar_arff_a_dataframe(contenido_decodificado)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error al leer el archivo: {str(e)}")

        # Verificar que el DataFrame no está vacío
        if data.empty:
            raise HTTPException(status_code=400, detail="El archivo no contiene datos")
        
        # Determinar las características más correlacionadas
        #features_seleccionadas = n_mas_correlacionadas(data, n=10)
        target = data.columns[-1]
        n = 200
        top_pearson = correlacion_pearson(data, target, n)

        # Guardar los índices de las características seleccionadas
        indices_caracteristicas_seleccionadas = [data.columns.get_loc(col) for col in top_pearson]
        with open('indices_caracteristicas_seleccionadas.txt', 'w') as f:
            for indice in indices_caracteristicas_seleccionadas:
                f.write("%d\n" % indice)

        top_spearman = correlacion_spearman(data, target, n)
        top_arboles = importancia_caracteristicas_arbol_decision(data, target, n)
        if data.columns[-1] not in top_pearson:
            top_pearson.append(data.columns[-1])
        # Preparar los datos para entrenamiento
        X = data[top_pearson].iloc[:, :-1]
        y = data[top_pearson].iloc[:, -1]
        
        # Entrenar y evaluar modelos
        resultados, modelos = entrenar_evaluar_modelos(X, y)
        
        # Seleccionar y serializar el mejor modelo
        mejor_modelo_nombre = seleccionar_y_serializar_mejor_modelo(resultados, modelos)
        
        # Serializar el modelo seleccionado utilizando pickle
        modelo_serializado = pickle.dumps(modelos[mejor_modelo_nombre])
        modelo_binario = binascii.hexlify(modelo_serializado)
        
        # Crear el objeto de modelo para la base de datos
        descripcion_final = f'Modelo entrenado: {mejor_modelo_nombre}'
        if descripcion:
            descripcion_final += f' - {descripcion}'

        # Crear el objeto de modelo para la base de datos
        db_modelo = ModeloML(
            nombre_archivo= nombre_archivo + ' -  ' + ruta_archivo.split('/')[-1],
            descripcion=descripcion_final,
            tipo_modelo=mejor_modelo_nombre,
            metricas=resultados[mejor_modelo_nombre],
            ruta_archivo=ruta_archivo,
            modelo_binario=modelo_binario
        )
        
        # Guardar el modelo en la base de datos
        db.add(db_modelo)
        db.commit()
        db.refresh(db_modelo)
        
        # Retornar el ID del modelo guardado
        return {"id_modelo": db_modelo.id}
    
    except FileNotFoundError:
        raise HTTPException(status_code=400, detail="El archivo especificado no fue encontrado")
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="El archivo está vacío o tiene un formato incorrecto")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/modelos/create")
async def create_modelo(nombre_archivo: str, ruta_archivo: str, descripcion: Optional[str] = None,  archivo: UploadFile = File(None), db: Session = Depends(get_db)):
    return await entrenar_y_seleccionar_modelo(nombre_archivo, ruta_archivo, descripcion, archivo, db)

@router.patch("/modelos/update/{modelo_id}", response_model=ModeloMLShow)
def update_modelo(modelo_id: int, modelo: ModeloMLUpdate, db: Session = Depends(get_db)):
    try:
        db_modelo = db.query(ModeloML).filter(ModeloML.id == modelo_id).first()
        if not db_modelo:
            raise HTTPException(status_code=404, detail="Modelo no encontrado")
        
        modelo_data = modelo.dict(exclude_unset=True)
        for key, value in modelo_data.items():
            setattr(db_modelo, key, value)

        db.commit()
        db.refresh(db_modelo)
        return db_modelo
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/delete_modelos/{modelo_id}", status_code=200)
def delete_modelo(modelo_id: int, db: Session = Depends(get_db)):
    db_modelo = db.query(ModeloML).filter(ModeloML.id == modelo_id).first()
    if not db_modelo:
        raise HTTPException(status_code=404, detail="Modelo no encontrado")
    db.delete(db_modelo)
    db.commit()
    return {"message": "Modelo eliminado con éxito"}

