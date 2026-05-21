from fastapi import FastAPI, UploadFile, File
from database import engine, Base
from database import SessionLocal
from models import Cliente
import models
import pandas as pd
from excel_cleaner import limpiar_ranking_vendedores

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

@app.post("/importar-clientes")
async def importar_clientes(file: UploadFile = File(...)):
    df = pd.read_excel(file.file)

    db = SessionLocal()

    for _, row in df.iterrows():
        cliente = Cliente(
            codigo=str(row.get("codigo", "")),
            nombre=str(row.get("nombre", "")),
            direccion=str(row.get("direccion", "")),
            telefono=str(row.get("telefono", "")),
            vendedor=str(row.get("vendedor", "")),
            frecuencia=str(row.get("frecuencia", "")),
            empresa=str(row.get("empresa", "")),
            latitud=0,
            longitud=0
        )
        db.add(cliente)

    db.commit()
    db.close()

    return {
        "mensaje": "Clientes importados correctamente",
        "cantidad": len(df)
    }

@app.post("/ranking-vendedores")
async def ranking_vendedores(file: UploadFile = File(...)):
    df = limpiar_ranking_vendedores(file.file)

    return {
        "columnas": list(df.columns),
        "filas": len(df),
        "preview": df.head().to_dict(orient="records")
    }
