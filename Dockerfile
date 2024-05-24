# Usar una imagen oficial de Python como imagen base
FROM python:3.12.2-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar el archivo de requerimientos al contenedor
COPY . /app

# Instalar virtualenv
#RUN pip install virtualenv

# Crear un entorno virtual en el contenedor
#RUN virtualenv venv

# Activar el entorno virtual
#ENV VIRTUAL_ENV=/app/venv
#ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Instalar las dependencias en el entorno virtual
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT uvicorn --host 0.0.0.0 main:app

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--reload"]
