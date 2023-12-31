# scraping_kalea.py

import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

def extraer_precio_kalea(driver, url):
    """
    Extrae el precio de un producto desde la página web 'Kalea' utilizando Selenium.

    Args:
    driver (webdriver): Instancia del navegador controlada por Selenium.
    url (str): URL del producto en la página web de Kalea.

    Returns:
    float: El precio del producto si es exitosamente extraído, de lo contrario None.
    """
    try:
        driver.get(url)
        time.sleep(4)  # Esperar a que la página del producto se cargue completamente

        p_precio = driver.find_element(By.CSS_SELECTOR, "p.price.content-text span")
        precio_texto = re.findall(r'\$\s*([\d,]+\.\d+)', p_precio.text.strip())

        if precio_texto:
            precio = precio_texto[0].replace(',', '').strip()
            precio = float(precio)
            print(f"Precio extraído de Kalea: {precio}")  # Impresión de depuración
            return precio
        else:
            print(f"No se pudo extraer el precio de {url}")
            return None
    except Exception as e:
        print(f"Error al extraer el precio de {url}: {e}")
        return None