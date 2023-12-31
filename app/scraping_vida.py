# scraping_vida.py

import requests
from bs4 import BeautifulSoup

def extraer_precio_vida(url):
    """
    Extrae el precio de un producto desde la página web 'vida'.
    
    Args:
    url (str): URL del producto en la página web 'vida'.

    Returns:
    float: El precio del producto si es exitosamente extraído, de lo contrario None.
    """
    try:
        respuesta = requests.get(url)
        if respuesta.status_code == 200:
            soup = BeautifulSoup(respuesta.text, 'html.parser')
            span_precio = soup.find('span', class_='price-data')
            if span_precio and span_precio.text:
                precio_texto = span_precio.text.strip().replace(',', '').replace('$', '')
                return float(precio_texto)
    except Exception as e:
        print(f"Error al extraer el precio de {url}: {e}")
    return None