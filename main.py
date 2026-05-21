from fastapi import FastAPI, UploadFile, File
from database import engine, Base
from database import SessionLocal
from models import Cliente, RankingVendedor
import models
import pandas as pd
from excel_cleaner import limpiar_ranking_vendedores
from sqlalchemy import func

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

@app.post("/guardar-ranking-vendedores")
async def guardar_ranking_vendedores(file: UploadFile = File(...)):
    df = limpiar_ranking_vendedores(file.file)

    db = SessionLocal()

    registros_guardados = 0

    for _, row in df.iterrows():
        vendedor = RankingVendedor(
            vendedor=str(row.get("Vendedor", "")),
            cartera=float(row.get("Cartera", 0) or 0),
            activacion=float(row.get("Activación", 0) or 0),
            facturas_bs=float(row.get("Facturas", 0) or 0),
            pedidos_fact=float(row.get("Ped. Fact.", 0) or 0),
            notas=float(row.get("Notas", 0) or 0),
            total=float(row.get("Total", 0) or 0),
            drop_size_neto=float(row.get("Drop Size Div. Neto", 0) or 0),
            drop_size_cajas=float(row.get("Drop Size Cajas", 0) or 0),
        )
        db.add(vendedor)
        registros_guardados += 1

    db.commit()
    db.close()

    return {
        "mensaje": "Ranking guardado correctamente",
        "registros_guardados": registros_guardados
    }

@app.get("/dashboard-general")
def dashboard_general():
    db = SessionLocal()

    total_vendedores = db.query(RankingVendedor).count()

    facturacion_total = db.query(
        func.sum(RankingVendedor.total)
    ).scalar()

    activacion_promedio = db.query(
        func.avg(RankingVendedor.activacion)
    ).scalar()

    cartera_promedio = db.query(
        func.avg(RankingVendedor.cartera)
    ).scalar()

    drop_size_promedio = db.query(
        func.avg(RankingVendedor.drop_size_cajas)
    ).scalar()

    top_vendedor = db.query(
        RankingVendedor
    ).order_by(
        RankingVendedor.total.desc()
    ).first()

    db.close()

    return {
        "total_vendedores": total_vendedores,
        "facturacion_total": round(facturacion_total or 0, 2),
        "activacion_promedio": round(activacion_promedio or 0, 2),
        "cartera_promedio": round(cartera_promedio or 0, 2),
        "drop_size_promedio": round(drop_size_promedio or 0, 2),
        "top_vendedor": top_vendedor.vendedor if top_vendedor else "N/A"
    }
