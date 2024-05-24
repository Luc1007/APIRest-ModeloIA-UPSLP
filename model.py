import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import joblib  # Se ha actualizado la forma de importar joblib
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import io
import pickle


# Función para cargar datos desde un archivo ARFF
def cargar_arff_a_dataframe(contenido_archivo):
    contenido = contenido_archivo.splitlines()

    indice_inicio_datos = 0
    nombres_columnas = []
    for indice, linea in enumerate(contenido):
        if '@DATA' in linea:
            indice_inicio_datos = indice + 1
            break
        if '@ATTRIBUTE' in linea:
            nombre_columna = linea.split()[1]
            nombres_columnas.append(nombre_columna)

    # Convertir el contenido en un DataFrame
    data = pd.read_csv(io.StringIO('\n'.join(contenido[indice_inicio_datos:])), header=None, delimiter=",")
    data.columns = nombres_columnas
    print(data.head())  # Imprime las primeras cinco filas
    print(data.tail())  # Imprime las últimas cinco filas
    return data

def correlacion_pearson(data, columna_objetivo, n=10):
    correlaciones = data.corr(method='pearson')[columna_objetivo].abs().sort_values(ascending=False)
    top_n = correlaciones[1:n+1].index.tolist()
    return top_n


def correlacion_spearman(data, columna_objetivo, n=10):
    correlaciones = data.corr(method='spearman')[columna_objetivo].abs().sort_values(ascending=False)
    top_n = correlaciones[1:n+1].index.tolist()
    return top_n

def importancia_caracteristicas_arbol_decision(data, columna_objetivo, n=10):
    X = data.drop(columns=[columna_objetivo])
    y = data[columna_objetivo]

    # Escalando las características
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    modelo = RandomForestRegressor()
    modelo.fit(X_scaled, y)

    importancias = modelo.feature_importances_
    indices = np.argsort(importancias)[::-1]
    top_n_indices = indices[:n]
    top_n_nombres = [X.columns[i] for i in top_n_indices]

    return top_n_nombres

# Función para obtener las características más correlacionadas
def n_mas_correlacionadas(data, n):
    target = data.columns[-1]
    correlacion = data.corr()
    correlaciones_con_target = correlacion[target].abs()
    correlaciones_con_target = correlaciones_con_target.drop(target)
    correlaciones_importantes = correlaciones_con_target.sort_values(ascending=False).head(n)
    return correlaciones_importantes.index.tolist()

# Función para entrenar y evaluar modelos
def entrenar_evaluar_modelos(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    modelos = {
        'Random Forest': RandomForestRegressor(n_estimators=100),
        'KNN': KNeighborsRegressor(n_neighbors=5),
        'MLP': MLPRegressor(hidden_layer_sizes=(100,), max_iter=600, alpha=0.001, solver='adam', verbose=10, random_state=1),
        'Ridge': Ridge(alpha=1.0, fit_intercept=True, max_iter=600, tol=0.001, solver='auto'),
        'XGBoost': xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100)
    }

    resultados = {}

    for nombre, modelo in modelos.items():
        modelo.fit(X_train, y_train)
        y_pred = modelo.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = modelo.score(X_test, y_test)
        resultados[nombre] = (mse, mae, r2)

    return resultados, modelos

# Función para seleccionar y serializar el mejor modelo
def seleccionar_y_serializar_mejor_modelo(resultados, modelos):
    mejor_score = float('inf')
    mejor_modelo = None

    for nombre, metricas in resultados.items():
        mse, mae, r2 = metricas
        score_promedio = np.mean([mse, mae, 1-r2])
        if score_promedio < mejor_score:
            mejor_score = score_promedio
            mejor_modelo = nombre

    modelo_serializado = pickle.dumps(modelos[mejor_modelo])
    joblib.dump(modelos[mejor_modelo], f'{mejor_modelo}_modelo.pkl')
    return mejor_modelo


def cargar_modelo(nombre_archivo='modelo_entrenado.pkl'):
    """
    Carga el modelo entrenado desde el disco.
    """
    try:
        modelo = joblib.load(nombre_archivo)
        return modelo, "Modelo cargado con exito"
    except FileNotFoundError:
        raise FileNotFoundError("El archivo del modelo no fue encontrado.")
    except Exception as e:
        raise Exception(f"Error al cargar el modelo: {e}")


def hacer_prediccion(modelo, datos_entrada):
    """
    Realiza una predicción utilizando el modelo cargado y datos de entrada específicos.
    """
    # Filtrar las características de la entrada
    datos_entrada_filtrada_array = np.array(datos_entrada).reshape(1, -1)
    
    # Imprimir información sobre el modelo utilizado
    print(f"Predicción utilizando el modelo: {modelo.__class__.__name__}")
    
    # Imprimir el número de características que el modelo espera recibir
    if hasattr(modelo, 'n_features_in_'):
        print(f"El modelo espera {modelo.n_features_in_} características.")
    else:
        print("El número de características esperadas no está disponible en el modelo.")
    
    # Imprimir la forma de los datos de entrada filtrados
    print(datos_entrada_filtrada_array.shape)
    
    # Realizar la predicción. El resultado es un array de NumPy.
    try:
        prediccion = modelo.predict(datos_entrada_filtrada_array)
    except Exception as e:
        print(f"Error realizando la predicción: {str(e)}")
        return None, "Error realizando la predicción"
    
    # Convertir el array de NumPy a una lista de Python para asegurar la compatibilidad de serialización.
    prediccion_lista = prediccion.tolist()
    
    # Imprimir la predicción realizada
    print(f"Predicción realizada: {prediccion_lista}")
    
    return prediccion_lista, "Predicción realizada con éxito"




