from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func


Base = declarative_base()

class Categoria(Base):
    __tablename__ = 'categorias'
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)

    # Relación inversa (opcional pero útil en consultas bidireccionales)
    productos = relationship('Producto', back_populates='categoria')

    def __repr__(self):
        return f"<Categoria(nombre='{self.nombre}')>"

class Producto(Base):
    __tablename__ = 'productos'
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    categoria_id = Column(Integer, ForeignKey('categorias.id'), nullable=False)
    titulo_kalea = Column(String)
    url_kalea = Column(String)
    factor_kalea = Column(Float)
    titulo_kromi = Column(String)
    url_kromi = Column(String)
    factor_kromi = Column(Float)
    titulo_tuzonamarket = Column(String)
    url_tuzonamarket = Column(String)
    factor_tuzonamarket = Column(Float)
    titulo_vida = Column(String)
    url_vida = Column(String)
    factor_vida = Column(Float)

    # Establecer la relación con la categoría
    categoria = relationship('Categoria', back_populates='productos')
    # Establecer la relación del precio
    historial_precios = relationship("HistorialPrecio", back_populates="producto")

    def __repr__(self):
        return f"<Producto(nombre='{self.nombre}', categoria_id={self.categoria_id})>"
    

class HistorialPrecio(Base):
    __tablename__ = 'historial_precios'
    id = Column(Integer, primary_key=True)
    producto_id = Column(Integer, ForeignKey('productos.id'))
    precio = Column(Float)
    fecha_extraccion = Column(DateTime)
    fuente = Column(String)

    producto = relationship("Producto", back_populates="historial_precios")
