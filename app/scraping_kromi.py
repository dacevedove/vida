# scraping_kromi.py

import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse
import time

def normalizar_url(url):
    """
    Normaliza la URL proporcionada para facilitar comparaciones.

    Args:
    url (str): La URL a normalizar.

    Returns:
    str: URL normalizada.
    """
    parsed_url = urlparse(url)
    dominio = parsed_url.netloc
    if dominio.startswith("www."):
        dominio = dominio[4:]
    return f"{parsed_url.scheme}://{dominio}{parsed_url.path}"

def extraer_precio_kromi(driver, titulo_kromi, url_kromi):
    """
    Extrae el precio de un producto desde la página web 'Kromi' utilizando Selenium.

    Args:
    driver (webdriver): Instancia del navegador controlada por Selenium.
    titulo_kromi (str): Título del producto en Kromi para realizar la búsqueda.
    url_kromi (str): URL del producto en la página web de Kromi.

    Returns:
    float: El precio del producto si es exitosamente extraído, de lo contrario None.
    """
    try:
        # Asumimos que el driver ya está en la página de Kromi
        caja_busqueda = driver.find_element(By.NAME, "des")
        caja_busqueda.clear()  # Limpiar la caja de búsqueda
        caja_busqueda.send_keys(titulo_kromi)
        time.sleep(5)
        enlace_producto = driver.find_element(By.CSS_SELECTOR, "#textItemId a")
        enlace_producto.click()

        # Comprobación de URL
        url_actual = driver.current_url
        if normalizar_url(url_actual) != normalizar_url(url_kromi):
            print(f"URL actual no coincide con url_kromi: {url_actual} != {url_kromi}")
            return None
        
        time.sleep(4)
        span_precio = driver.find_element(By.CLASS_NAME, "tag_precio_producto")
        precio_texto = span_precio.text.strip().replace(',', '').replace('$', '')
        precio = float(precio_texto)
        print(f"Precio extraído de Kromi: {precio}")
        return precio
    except Exception as e:
        print(f"Error al extraer el precio de {titulo_kromi}: {e}")
        return None
