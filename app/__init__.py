# app/__init__.py
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
import os

def create_app():
    app = Flask(__name__, template_folder=os.path.abspath('templates'))
    # Resto de tu configuración de Flask...


    # Configura la base de datos
    DATABASE_URL = "sqlite:///mi_app.db"
    engine = create_engine(DATABASE_URL)
    Base.metadata.bind = engine

    # Crea las tablas si no existen
    Base.metadata.create_all(engine)

    # Configura la sesión de SQLAlchemy
    Session = sessionmaker(bind=engine)
    app.session = Session

    # Registra el Blueprint
    from .routes import bp
    app.register_blueprint(bp)

    return app
