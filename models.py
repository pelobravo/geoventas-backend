from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from database import Base
from datetime import datetime

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String)
    nombre = Column(String)
    direccion = Column(String)
    telefono = Column(String)
    latitud = Column(Float)
    longitud = Column(Float)
    vendedor = Column(String)
    frecuencia = Column(String)
    empresa = Column(String)
    activo = Column(Boolean, default=True)


class RankingVendedor(Base):
    __tablename__ = "ranking_vendedores"

    id = Column(Integer, primary_key=True, index=True)

    vendedor = Column(String)
    cartera = Column(Float)
    activacion = Column(Float)

    facturas_bs = Column(Float)
    pedidos_fact = Column(Float)

    notas = Column(Float)
    total = Column(Float)

    drop_size_neto = Column(Float)
    drop_size_cajas = Column(Float)

    fecha_carga = Column(DateTime, default=datetime.utcnow)
