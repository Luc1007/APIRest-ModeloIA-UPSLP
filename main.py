from fastapi import FastAPI, HTTPException, Query
from typing import List
from pydantic import BaseModel, Field
import numpy as np
import db_endpoints
import ml_endpoints


app = FastAPI()

app.include_router(db_endpoints.router)
app.include_router(ml_endpoints.router)

@app.get("/")
async def read_root():
    return {"message": "Bienvenido a mi API FastAPI"}  # Mensaje de bienvenidos




