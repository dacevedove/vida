# scraping.py

# Importaciones de los módulos específicos de scraping
from .scraping_vida import extraer_precio_vida
from .scraping_kalea import extraer_precio_kalea
from .scraping_kromi import extraer_precio_kromi
from .scraping_tuzonamarket import extraer_precio_tuzonamarket

from .models import Producto, Categoria, HistorialPrecio
from datetime import datetime, timedelta


def guardar_historial_precio(session, producto_id, precio, fuente, factor=1.0):
    try:
        # Multiplicar el precio por el factor
        precio_ajustado = precio * factor
        # Verificar si ya existe un registro similar reciente
        existe = session.query(HistorialPrecio).filter(
            HistorialPrecio.producto_id == producto_id,
            HistorialPrecio.precio == precio_ajustado,
            HistorialPrecio.fuente == fuente,
            HistorialPrecio.fecha_extraccion > (datetime.now() - timedelta(minutes=5))  # Ejemplo: 5 minutos
        ).first()

        if not existe:
            historial = HistorialPrecio(producto_id=producto_id, precio=precio_ajustado, fecha_extraccion=datetime.now(), fuente=fuente)
            session.add(historial)
            session.commit()
            print(f"Guardado: Producto {producto_id}, Precio {precio}, Fuente {fuente}")
        else:
            print(f"Registro duplicado no guardado: Producto {producto_id}, Precio {precio}, Fuente {fuente}")
    except Exception as e:
        print(f"Error al guardar el precio: {e}")