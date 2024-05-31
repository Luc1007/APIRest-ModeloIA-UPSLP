#!/bin/bash

# Activar el entorno virtual si es necesario
source /path/to/venv/bin/activate

pip install -r requirements.txt
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
