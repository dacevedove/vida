from flask import Blueprint, request, render_template, redirect, url_for
from .models import Producto, Categoria, HistorialPrecio
from sqlalchemy.orm import joinedload
from .database import Session
from . import scraping  # Importación centralizada de las funciones de scraping
from .scraping import guardar_historial_precio


# Importaciones de selenium para la actuzalicion de precios
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import random
import time
from threading import Thread

bp = Blueprint('bp', __name__)

@bp.route('/')
def inicio():
    session = Session()

    ultimo_registro_vida = session.query(HistorialPrecio).filter_by(fuente='vida').order_by(HistorialPrecio.fecha_extraccion.desc()).first()
    ultimo_timestamp_vida = ultimo_registro_vida.fecha_extraccion if ultimo_registro_vida else None

    if ultimo_timestamp_vida:
        ultimo_timestamp_formateado = ultimo_timestamp_vida.strftime('%d/%m/%Y %I:%M%p').lower()
    else:
        ultimo_timestamp_formateado = None

    categoria_filtro = request.args.get('categoria_id')

    if categoria_filtro:
        productos = session.query(Producto).filter(Producto.categoria_id == categoria_filtro).all()
    else:
        productos = session.query(Producto).all()

    categorias = session.query(Categoria).all()

    productos_precios = []
    for producto in productos:
        # Obtener el último precio para cada fuente
        ultimo_precio_vida = session.query(HistorialPrecio).filter_by(producto_id=producto.id, fuente='vida').order_by(HistorialPrecio.fecha_extraccion.desc()).first()
        ultimo_precio_kalea = session.query(HistorialPrecio).filter_by(producto_id=producto.id, fuente='kalea').order_by(HistorialPrecio.fecha_extraccion.desc()).first()
        ultimo_precio_kromi = session.query(HistorialPrecio).filter_by(producto_id=producto.id, fuente='kromi').order_by(HistorialPrecio.fecha_extraccion.desc()).first()
        ultimo_precio_tuzonamarket = session.query(HistorialPrecio).filter_by(producto_id=producto.id, fuente='tuzonamarket').order_by(HistorialPrecio.fecha_extraccion.desc()).first()

        # Formatear las diferencias de precio
        def formatear_diferencia(precio, precio_vida):
            if precio is not None and precio_vida is not None:
                diferencia = precio - precio_vida
                clase_dif = "dif positiva" if diferencia > 0 else "dif negativa" if diferencia < 0 else ""
                return f"<span class='{clase_dif}'>{'%.2f' % diferencia}</span>" if diferencia != 0 else ''
            return ''

        # Formatear los precios y las diferencias
        precio_vida = ultimo_precio_vida.precio if ultimo_precio_vida else 'No disponible'
        precio_kalea = f"{ultimo_precio_kalea.precio if ultimo_precio_kalea else 'No disponible'} {formatear_diferencia(ultimo_precio_kalea.precio if ultimo_precio_kalea else None, ultimo_precio_vida.precio if ultimo_precio_vida else None)}"
        precio_kromi = f"{ultimo_precio_kromi.precio if ultimo_precio_kromi else 'No disponible'} {formatear_diferencia(ultimo_precio_kromi.precio if ultimo_precio_kromi else None, ultimo_precio_vida.precio if ultimo_precio_vida else None)}"
        precio_tuzonamarket = f"{ultimo_precio_tuzonamarket.precio if ultimo_precio_tuzonamarket else 'No disponible'} {formatear_diferencia(ultimo_precio_tuzonamarket.precio if ultimo_precio_tuzonamarket else None, ultimo_precio_vida.precio if ultimo_precio_vida else None)}"

        # Agregar al arreglo de productos_precios
        productos_precios.append({
            'producto': producto.nombre,
            'categoria': producto.categoria.nombre if producto.categoria else 'Sin categoría',
            'precio_vida': precio_vida,
            'precio_kalea': precio_kalea,
            'precio_kromi': precio_kromi,
            'precio_tuzonamarket': precio_tuzonamarket
        })

    session.close()
    return render_template('inicio.html', productos_precios=productos_precios, categorias=categorias, ultimo_timestamp_vida=ultimo_timestamp_formateado)




@bp.route('/productos')
def listar_productos():
    session = Session()
    categoria_id = request.args.get('categoria_id')
    query = session.query(Producto).options(joinedload(Producto.categoria))

    if categoria_id:
        productos = query.filter(Producto.categoria_id == categoria_id).all()
    else:
        productos = query.all()

    categorias = session.query(Categoria).all()
    session.close()
    return render_template('listar_productos.html', productos=productos, categorias=categorias)



@bp.route('/producto/nuevo', methods=['GET', 'POST'])
def nuevo_producto():
    session = Session()
    categorias = session.query(Categoria).all()  # Necesario para el dropdown de categorías
    producto = None
    if request.method == 'POST':
        nuevo_producto = Producto(
            nombre=request.form['nombre'],
            categoria_id=request.form['categoria_id'],
            titulo_kalea=request.form.get('titulo_kalea', ''),
            url_kalea=request.form.get('url_kalea', ''),
            factor_kalea=scraping.convertir_a_float(request.form.get('factor_kalea', '1.0')),
            titulo_kromi=request.form.get('titulo_kromi', ''),
            url_kromi=request.form.get('url_kromi', ''),
            factor_kromi=scraping.convertir_a_float(request.form.get('factor_kromi', '1.0')),
            titulo_tuzonamarket=request.form.get('titulo_tuzonamarket', ''),
            url_tuzonamarket=request.form.get('url_tuzonamarket', ''),
            factor_tuzonamarket=scraping.convertir_a_float(request.form.get('factor_tuzonamarket', '1.0')),
            titulo_vida=request.form.get('titulo_vida', ''),
            url_vida=request.form.get('url_vida', ''),
            factor_vida=scraping.convertir_a_float(request.form.get('factor_vida', '1.0'))
        )
        session.add(nuevo_producto)
        session.commit()
        session.close()
        return redirect(url_for('bp.listar_productos'))

    session.close()
    return render_template('nuevo_producto.html', categorias=categorias, producto=producto)



@bp.route('/producto/editar/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    session = Session()
    producto = session.query(Producto).get(id)
    categorias = session.query(Categoria).all()

    if request.method == 'POST':
        producto.nombre = request.form['nombre']
        producto.categoria_id = request.form['categoria_id']
        producto.titulo_kalea = request.form['titulo_kalea']
        producto.url_kalea = request.form['url_kalea']
        producto.factor_kalea = scraping.convertir_a_float(request.form.get('factor_kalea', '1.0'))
        producto.titulo_kromi = request.form['titulo_kromi']
        producto.url_kromi = request.form['url_kromi']
        producto.factor_kromi = scraping.convertir_a_float(request.form.get('factor_kromi', '1.0'))
        producto.titulo_tuzonamarket = request.form['titulo_tuzonamarket']
        producto.url_tuzonamarket = request.form['url_tuzonamarket']
        producto.factor_tuzonamarket = scraping.convertir_a_float(request.form.get('factor_tuzonamarket', '1.0'))
        producto.titulo_vida = request.form['titulo_vida']
        producto.url_vida = request.form['url_vida']
        producto.factor_vida = scraping.convertir_a_float(request.form.get('factor_vida', '1.0'))

        session.commit()
        session.close()
        return redirect(url_for('bp.listar_productos'))

    session.close()
    return render_template('editar_producto.html', producto=producto, categorias=categorias)



@bp.route('/producto/eliminar/<int:id>', methods=['GET'])
def eliminar_producto(id):
    session = Session()
    producto = session.query(Producto).get(id)

    if producto:
        session.delete(producto)
        session.commit()

    session.close()
    return redirect(url_for('bp.listar_productos'))



@bp.route('/categorias')
def listar_categorias():
    session = Session()
    categorias = session.query(Categoria).all()
    session.close()
    return render_template('listar_categorias.html', categorias=categorias)



@bp.route('/categoria/nueva', methods=['GET', 'POST'])
def nueva_categoria():
    session = Session()
    
    if request.method == 'POST':
        nombre_categoria = request.form['nombre']
        nueva_categoria = Categoria(nombre=nombre_categoria)
        session.add(nueva_categoria)
        session.commit()
        session.close()
        return redirect(url_for('bp.listar_categorias'))

    session.close()
    return render_template('nueva_categoria.html')



@bp.route('/categoria/eliminar/<int:id>', methods=['GET'])
def eliminar_categoria(id):
    session = Session()
    categoria = session.query(Categoria).get(id)

    if categoria:
        session.delete(categoria)
        session.commit()

    session.close()
    return redirect(url_for('bp.listar_categorias'))



@bp.route('/actualizar_precios_vida')
def actualizar_precios_vida():
    session = Session()
    productos = session.query(Producto).all()
    random.shuffle(productos)

    for producto in productos:
        if producto.url_vida:
            precio = scraping.extraer_precio_vida(producto.url_vida)
            if precio is not None:
                guardar_historial_precio(session, producto.id, precio, "vida")

    session.close()
    return "Precios de 'Vida' actualizados"



@bp.route('/actualizar_precios_kalea')
def actualizar_precios_kalea():
    session = Session()
    productos = session.query(Producto).all()
    random.shuffle(productos)

    # Configuración del WebDriver de Selenium
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # Cargar la URL base primero para poder acceder al almacenamiento local
    driver.get("https://kaleamarket.com")
    time.sleep(1)  # Esperar a que la página cargue
    # Establecer el valor en el almacenamiento local
    driver.execute_script("localStorage.setItem('store-location', JSON.stringify({\"id\":\"pfvswBTKMD0JMgHsvEEv\",\"name\":\"Valles de Camoruco\"}));")
    
    for producto in productos:
        if producto.url_kalea:
            precio = scraping.extraer_precio_kalea(driver, producto.url_kalea)
            if precio is not None:
                guardar_historial_precio(session, producto.id, precio, "kalea")

    driver.quit()
    session.close()
    return "Precios de 'Kalea' actualizados"



@bp.route('/actualizar_precios_tuzonamarket')
def actualizar_precios_tuzonamarket():
    session = Session()
    productos = session.query(Producto).all()
    random.shuffle(productos)

    for producto in productos:
        if producto.url_tuzonamarket:
            precio = scraping.extraer_precio_tuzonamarket(producto.url_tuzonamarket)
            if precio is not None:
                guardar_historial_precio(session, producto.id, precio, "tuzonamarket")

    session.close()
    return "Precios de 'TuZonaMarket' actualizados"



@bp.route('/actualizar_precios_kromi')
def actualizar_precios_kromi():
    session = Session()
    productos = session.query(Producto).all()
    random.shuffle(productos)

    # Configuración del WebDriver de Selenium
    chrome_options = Options()
    #chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Navega a la página principal de Kromi para iniciar la sesión
    driver.get("https://kromionline.com")
    # Añade aquí cualquier configuración adicional necesaria para Kromi
    time.sleep(4)
    
    for producto in productos:
        if producto.url_kromi:
            precio = scraping.extraer_precio_kromi(driver, producto.titulo_kromi, producto.url_kromi)
            if precio is not None:
                guardar_historial_precio(session, producto.id, precio, "kromi")
            else:
                print(f"El precio para {producto.url_kromi} no se pudo extraer o guardar.")
    
    driver.quit()
    session.close()
    return "Precios de 'Kromi' actualizados"

@bp.route('/actualizar_producto/<int:id>')
def actualizar_producto(id):
    session = Session()
    producto = session.query(Producto).get(id)

    if not producto:
        session.close()
        return f"No se encontró el producto con ID {id}", 404

    # Actualizar precio para Vida
    if producto.url_vida:
        precio_vida = scraping.extraer_precio_vida(producto.url_vida)
        if precio_vida is not None:
            guardar_historial_precio(session, id, precio_vida * producto.factor_vida, "vida")

    # Actualizar precio para Kalea
    if producto.url_kalea:
        chrome_options = Options()
        #chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get("https://kaleamarket.com")
        time.sleep(1)
        driver.execute_script("localStorage.setItem('store-location', JSON.stringify({\"id\":\"pfvswBTKMD0JMgHsvEEv\",\"name\":\"Valles de Camoruco\"}));")
        precio_kalea = scraping.extraer_precio_kalea(driver, producto.url_kalea)
        if precio_kalea is not None:
            guardar_historial_precio(session, id, precio_kalea * producto.factor_kalea, "kalea")
        driver.quit()

    # Actualizar precio para Kromi
    if producto.url_kromi:
        chrome_options = Options()
        #chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get("https://kromionline.com")
        time.sleep(4)
        precio_kromi = scraping.extraer_precio_kromi(driver, producto.titulo_kromi, producto.url_kromi)
        if precio_kromi is not None:
            guardar_historial_precio(session, id, precio_kromi * producto.factor_kromi, "kromi")
        driver.quit()

    # Actualizar precio para TuZonaMarket
    if producto.url_tuzonamarket:
        precio_tuzonamarket = scraping.extraer_precio_tuzonamarket(producto.url_tuzonamarket)
        if precio_tuzonamarket is not None:
            guardar_historial_precio(session, id, precio_tuzonamarket * producto.factor_tuzonamarket, "tuzonamarket")

    session.close()
    return f"Precios actualizados para el producto con ID {id}"


def actualizar_precios_background():
    global status
    session = Session()
    productos = session.query(Producto).all()

    # Actualizar precios para TuZonaMarket
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    for producto in productos:
        if producto.url_vida:
            precio_vida = scraping.extraer_precio_vida(producto.url_vida)
            if precio_vida is not None:
                guardar_historial_precio(session, producto.id, precio_vida, "vida", producto.factor_vida)
    driver.quit()

    # Actualizar precios para Kalea
    # Configuración inicial de Selenium para Kalea
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get("https://kaleamarket.com")
    time.sleep(1)
    driver.execute_script("localStorage.setItem('store-location', JSON.stringify({\"id\":\"pfvswBTKMD0JMgHsvEEv\",\"name\":\"Valles de Camoruco\"}));")

    for producto in productos:
        if producto.url_kalea:
            precio_kalea = scraping.extraer_precio_kalea(driver, producto.url_kalea)
            if precio_kalea is not None:
                guardar_historial_precio(session, producto.id, precio_kalea, "kalea", producto.factor_kalea)
    driver.quit()

    # Actualizar precios para Kromi
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get("https://kromionline.com")
    time.sleep(4)

    for producto in productos:
        if producto.url_kromi:
            precio_kromi = scraping.extraer_precio_kromi(driver, producto.titulo_kromi, producto.url_kromi)
            if precio_kromi is not None:
                guardar_historial_precio(session, producto.id, precio_kromi, "kromi", producto.factor_kromi)
    driver.quit()

    # Actualizar precios para TuZonaMarket
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    for producto in productos:
        if producto.url_tuzonamarket:
            precio_tuzonamarket = scraping.extraer_precio_tuzonamarket(producto.url_tuzonamarket)
            if precio_tuzonamarket is not None:
                guardar_historial_precio(session, producto.id, precio_tuzonamarket, "tuzonamarket", producto.factor_tuzonamarket)
    driver.quit()
    
    session.close()
    return "Precios actualizados para todos los productos"

@bp.route('/estado_actualizacion')
def estado_actualizacion():
    global status
    return jsonify(status)

status = {"processed": 0, "total": 0, "running": False}

@bp.route('/actualizar_precios')
def actualizar_precios():
    global status
    if not status["running"]:
        status["running"] = True
        status["processed"] = 0
        # Obtener el número total de productos a procesar
        session = Session()
        total_products = session.query(Producto).count()
        session.close()
        status["total"] = total_products

        # Iniciar la actualización en un hilo de fondo
        thread = Thread(target=actualizar_precios_background)
        thread.start()

    return render_template('actualizando_precios.html')