#Esta clase prepara una conexión reutilizable entre la API y la bse de datos

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import DATABASE_URL

#Configuración para comunicación con MySQL
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

#Sesión para consultas
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)