from sqlalchemy import Column, Integer, String, Float, Boolean
from database import Base

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String)
    nombre = Column(String)
    direccion = Column(String)
    telefono = Column(String)
    latitud = Column(Float)
    longitud = Column(Float)
    activo = Column(Boolean, default=True)
