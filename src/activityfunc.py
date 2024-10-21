import pandas as pd
import numpy as np
import concurrent.futures
import janus
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

import janus

def get_info_page(queue):
    """
    Extrae información de actividades desde una página web utilizando Selenium.

    Args:
        queue (janus.Queue): Cola que contiene las URLs de las páginas a scrapear.

    Returns:
        pd.DataFrame: Un DataFrame que contiene los nombres, precios, enlaces y descripciones de las actividades.
    """
    names_list = []
    prices_list = []
    links_list = []
    desc_list = []

    chrome_options = Options()
    chrome_options.add_argument("--headless=old")  # Ejecución sin interfaz gráfica
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    df_page = pd.DataFrame()
    
    while True:
        try:
            url = queue.sync_q.get() # Obtenemos los links de la cola, generados en la función de link_queue.
            if url is None: # Como es una función que aplicaremos con futuros, ponemos una condición para que deje de ejecutarse si no quedan más links.
                break
            driver = webdriver.Chrome(options=chrome_options)
            print(f"Fetching URL: {url}")
            time.sleep(0.5)
            driver.get(url)

            try:
                consent_button = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="didomi-notice-disagree-button"]/span')) # Rechazamos cookies
                )
                consent_button.click()
            except:
                pass
                # print(f"Consent button not found") # Esto porque hay casos en los que se abre pestaña nueva en el driver y no se necesita rechazar cookies
            time.sleep(0.5)

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") # Scroll para cargar contenido
            time.sleep(0.5)

            urls_html = driver.find_element(By.XPATH, '//*[@id="activities-container"]').get_attribute("innerHTML") # Extraer HTML para luego hacer sopa

            link_soup = BeautifulSoup(urls_html, "html.parser") # sopa, así evitamos tener que usar selenium
            activities = link_soup.findAll("div", class_='o-search-list__item') # El cuadro donde están los items
            for activity in activities: # El método de extracción de links es diferente al resto porque el tag de algunas actividades son diferentes (posiblemente patrocinados)
                try:
                    link = activity.find("a", class_='ga-trackEvent-element _activity-link').get('href')
                    links_list.append("https://www.civitatis.com" + link)
                except Exception as e:
                    # print(f"Error link: {e}")
                    links_list.append(np.nan)

            # print(f"Links: {links_list}")

            # Para el resto de info es el mismo método
            names = link_soup.findAll("h2", class_="comfort-card__title")
            names_list.extend([name.text.strip() for name in names])
            # print(f"Names: {names_list}")

            prices = link_soup.findAll("span", "comfort-card__price__text")
            prices_list.extend([price.text for price in prices])
            # print(f"Prices: {prices_list}")

            descs = link_soup.findAll("div", class_='comfort-card__text l-list-card__text')
            desc_list.extend([desc.text.strip() for desc in descs])
            # print(f"Descriptions: {desc_list}")
            # driver.quit()
            queue.sync_q.task_done() # Aquí indicamos que la tarea que había en cola se ha finalizado, pasando a la siguiente
        except Exception as e:
            print(f"Error scraping {url}: {e}")
        
    df_page = pd.DataFrame({'Nombre': names_list, 'Precio': prices_list, 'Link': links_list, 'Descripcion': desc_list})
            
    return df_page

def link_queue(queue, base_url, pages):
    """
    Añade URLs a una cola para el scraping.

    Args:
        queue (janus.Queue): Cola donde se almacenarán las URLs.
        base_url (str): URL base a la que se le añadirán los parámetros de la página.
        pages (int): Número de páginas que se desea scrapear.
    """
    for page in range(1, pages + 1):
        url = base_url + f"&page={page}"
        # print(f'Added {url} to queue')
        queue.sync_q.put(url) # Añadimos las urls a la cola
    queue.sync_q.put(None)  # Añadimos un None que indica el final de la cola de urls

def main(destinations):
    """
    Función principal que coordina el scraping de múltiples URLs.

    Args:
        destinations (list): Lista de destinos para los que se generarán URLs.

    Returns:
        pd.DataFrame: Un DataFrame combinado que contiene la información de todas las actividades extraídas.
    """
    queue = janus.Queue() # En el main generamos la cola que vamos a usar 
    day_in = 1
    year = 2025
    base_urls = []
    for month in range(7,9):
        for day_in in [1,15]:
            date_in = f"{year}-{month}-{day_in:02}"  # Y M D
            date_out = f"{year}-{month}-{day_in + 14}"  # Y M D
            base_urls.extend([f'https://www.civitatis.com/es/{loc}/?fromDate={date_in}&toDate={date_out}' for loc in destinations]) # URLs base para cada loc
    # print(base_urls)
    total_pages = 2 # Número de páginas que vamos a scrapear por localización

    max_w = 10
    results = [] 
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_w) as executor: # Esto es para procesos paralelos
        futures = [] # Los objetos de futuro que vamos generando

        for url in base_urls: # Añadimos a la cola todas las urls donde queremos extraer info
            link_queue(queue, url, total_pages)

        for _ in base_urls: # Guión bajo porque solo usamos el for como iteración limitada, no se usan los elementos
            future = executor.submit(get_info_page, queue) # Ejecutamos paralelamente la función para los elementos de la cola
            futures.append(future) # Añadimos el futuro generado a la lista de futuros


    for future in futures:
        result_df = future.result()
        results.append(result_df)
 
    final_df = pd.concat(results, ignore_index=True) 
    # print(final_df)
    return final_df


def clean_price(df):
    """
    Limpia la columna de precios de un DataFrame y la convierte a tipo float.

    Args:
        df (pd.DataFrame): DataFrame que contiene la columna 'Precio'.

    Returns:
        pd.Series: Serie de precios limpiados y convertidos a tipo float.
    """
    new_precio = df["Precio"].str.replace(".", "").str.replace(",", ".").str.replace(" €", "").replace("¡Gratis!", "0")
    return new_precio.apply(float)