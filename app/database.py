from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

# Configuración de la URL de la base de datos
DATABASE_URL = "sqlite:///mi_app.db"  # Cambia esto por tu URL de base de datos

# Creación del motor de base de datos
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Vinculación del motor con los modelos
Base.metadata.bind = engine

# Creación de las tablas en la base de datos
Base.metadata.create_all(engine)

# Creación de una fábrica de sesiones
Session = sessionmaker(bind=engine)
