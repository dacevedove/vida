# scraping_tuzonamarket.py

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def extraer_precio_tuzonamarket(url):
    """
    Extrae el precio de un producto desde la página web 'TuZonaMarket' utilizando Selenium.

    Args:
    url (str): URL del producto en la página web de TuZonaMarket.

    Returns:
    float: El precio del producto si es exitosamente extraído, de lo contrario None.
    """
    chrome_options = Options()
    #chrome_options.add_argument("--headless")  # Comentar esta línea si deseas ver el navegador
    chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        driver.get(url)
        time.sleep(4)  # Esperar a que la página se cargue completamente

        span_precio = driver.find_element(By.CLASS_NAME, "d-block.prec-vent.ng-star-inserted")
        precio_texto = span_precio.text.strip().replace(',', '.').replace('$', '')
        precio = float(precio_texto)
        print(f"Precio extraído: {precio}")
        return precio
    except Exception as e:
        print(f"Error al extraer el precio de {url}: {e}")
    finally:
        driver.quit()
    return None