# Usar una imagen oficial de Python como imagen base
FROM python:3.12.2-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar los archivos de requerimientos al contenedor
COPY requirements.txt .

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el contenido de la aplicación al contenedor
COPY . .

# Exponer el puerto en el que se ejecutará la aplicación FastAPI
EXPOSE 80

# Instalación y configuración de PostgreSQL
# Utilizar una imagen base de PostgreSQL
FROM postgres:13

# Variables de entorno para PostgreSQL
ENV POSTGRES_USER=admin
ENV POSTGRES_PASSWORD=1234
ENV POSTGRES_DB=db_modelos

# Copiar el script SQL de inicialización al contenedor
COPY init.sql /docker-entrypoint-initdb.d/

# Puertos expuestos por el contenedor de PostgreSQL
EXPOSE 5432

# CMD para iniciar tanto PostgreSQL como la aplicación FastAPI
CMD ["bash", "-c", "service postgresql start && uvicorn main:app --host 0.0.0.0 --port 80"]


