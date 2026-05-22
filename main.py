from fastapi import FastAPI, UploadFile, File
from database import engine, Base
from database import SessionLocal
from models import Cliente, RankingVendedor
import models
import pandas as pd
from excel_cleaner import limpiar_ranking_vendedores
from sqlalchemy import func

Base.metadata.create_all(bind=engine)

from sqlalchemy import text
from database import SessionLocal

db = SessionLocal()

try:
    db.execute(text("DROP TABLE ranking_vendedores"))
    db.commit()
    print("TABLA ELIMINADA")
except Exception as e:
    print(e)

db.close()

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
async def guardar_ranking_vendedores(
    empresa: str,
    file: UploadFile = File(...)
):
    db = SessionLocal()

    df = limpiar_ranking_vendedores(file.file)

    registros = 0

    for _, row in df.iterrows():
        vendedor = str(row.get("Vendedor", ""))

        cartera = float(row.get("Cartera", 0) or 0)
        activacion = float(row.get("Activación", 0) or 0)

        facturas_bs = float(row.get("Facturas", 0) or 0)
        pedidos_fact = float(row.get("Ped. Fact.", 0) or 0)

        notas = float(row.get("Notas", 0) or 0)
        total = float(row.get("Total", 0) or 0)

        drop_size_neto = float(row.get("Drop Size Div. Neto", 0) or 0)
        drop_size_cajas = float(row.get("Drop Size Cajas", 0) or 0)

        nuevo = RankingVendedor(
            empresa=empresa,
            vendedor=vendedor,
            cartera=cartera,
            activacion=activacion,
            facturas_bs=facturas_bs,
            pedidos_fact=pedidos_fact,
            notas=notas,
            total=total,
            drop_size_neto=drop_size_neto,
            drop_size_cajas=drop_size_cajas
        )

        db.add(nuevo)
        registros += 1

    db.commit()
    db.close()

    return {
        "mensaje": "Datos guardados correctamente",
        "empresa": empresa,
        "registros_guardados": registros
    }

@app.get("/dashboard-general")
def dashboard_general():
    db = SessionLocal()

    vendedores = db.query(RankingVendedor).all()

    total_vendedores = len(vendedores)

    facturacion_total = sum(v.total or 0 for v in vendedores)

    activacion_promedio = round(
        sum(v.activacion or 0 for v in vendedores) / total_vendedores,
        2
    ) if total_vendedores > 0 else 0

    cartera_promedio = round(
        sum(v.cartera or 0 for v in vendedores) / total_vendedores,
        2
    ) if total_vendedores > 0 else 0

    drop_size_promedio = round(
        sum(v.drop_size_cajas or 0 for v in vendedores) / total_vendedores,
        2
    ) if total_vendedores > 0 else 0

    top_vendedor = max(
        vendedores,
        key=lambda x: x.total or 0
    ).vendedor if vendedores else "N/A"

    empresas = {}

    for v in vendedores:
        if v.empresa not in empresas:
            empresas[v.empresa] = {
                "empresa": v.empresa,
                "facturacion": 0,
                "vendedores": 0,
                "top_vendedor": "",
                "mejor_total": 0
            }

        empresas[v.empresa]["facturacion"] += v.total or 0
        empresas[v.empresa]["vendedores"] += 1

        if (v.total or 0) > empresas[v.empresa]["mejor_total"]:
            empresas[v.empresa]["mejor_total"] = v.total or 0
            empresas[v.empresa]["top_vendedor"] = v.vendedor

    db.close()

    return {
        "total_vendedores": total_vendedores,
        "facturacion_total": facturacion_total,
        "activacion_promedio": activacion_promedio,
        "cartera_promedio": cartera_promedio,
        "drop_size_promedio": drop_size_promedio,
        "top_vendedor_global": top_vendedor,
        "empresas": list(empresas.values())
    }
