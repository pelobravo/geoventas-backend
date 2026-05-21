from fastapi import FastAPI, UploadFile, File
from database import engine, Base
import models
import pandas as pd

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def home():
    return {"mensaje": "GeoVentas funcionando 🚀"}

@app.get("/clientes")
def clientes():
    return {"modulo": "clientes activo"}

@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    # Leer el archivo CSV subido
    df = pd.read_csv(file.file)
    
    # Ejemplo: mostrar las primeras filas
    datos = df.head().to_dict(orient="records")
    
    return {
        "mensaje": "Archivo CSV procesado correctamente",
        "filas": len(df),
        "columnas": list(df.columns),
        "vista_previa": datos
    }

@app.post("/upload-excel")
async def upload_excel(file: UploadFile = File(...)):
    df = pd.read_excel(file.file)
    
    return {
        "columnas": list(df.columns),
        "filas": len(df)
    }
