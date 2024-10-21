import requests
import pandas as pd
from calendar import monthrange
import asyncio
import aiohttp
from tqdm import tqdm

def skyID(city, token):
    """
    Busca el skyId de una ciudad utilizando la API Sky Scrapper.
    
    Parámetros:
    city (str): Nombre de la ciudad para la cual se desea buscar el skyId.
    token (str): Token de autenticación para acceder a la API.

    Retorna:
    tuple: Un par que contiene el skyId de la ciudad y la respuesta completa en formato JSON.
    """
    url = "https://sky-scrapper.p.rapidapi.com/api/v1/flights/searchAirport"
    headers = {
        'x-rapidapi-key': token,
        'x-rapidapi-host': "sky-scrapper.p.rapidapi.com"
    }
    querystring = {"query": city, "locale": "es-ES"}
    response = requests.get(url, headers=headers, params=querystring)
    city_json = response.json()
    id = city_json["data"][0]["skyId"]
    return id, city_json

async def get_data(token, session, origin_data, destination_data, depart_date, return_date, adult_n, children_n):
    """
    Realiza una búsqueda de vuelos entre dos destinos utilizando la API Sky Scrapper de forma asíncrona.
    
    Parámetros:
    token (str): Token de autenticación para acceder a la API.
    session (aiohttp.ClientSession): Sesión HTTP asíncrona.
    origin_data (tuple): Tupla que contiene el skyId y el JSON de la ciudad de origen.
    destination_data (tuple): Tupla que contiene el skyId y el JSON de la ciudad de destino.
    depart_date (str): Fecha de salida en formato 'YYYY-MM-DD'.
    return_date (str): Fecha de regreso en formato 'YYYY-MM-DD'.
    adult_n (int): Número de adultos para el vuelo.
    children_n (int): Número de niños para el vuelo.
    
    Retorna:
    dict: La respuesta de la API en formato JSON, que incluye información sobre los vuelos disponibles.
    """
    url = "https://sky-scrapper.p.rapidapi.com/api/v2/flights/searchFlights"
    origin_ID, origin_json = origin_data
    dest_ID, dest_json = destination_data
    querystring = {
        "originSkyId": origin_ID,
        "destinationSkyId": dest_ID,
        "originEntityId": origin_json["data"][0]["entityId"],
        "destinationEntityId": dest_json["data"][0]["entityId"],
        "date": depart_date,
        "returnDate": return_date,
        "adults": adult_n,
        "childrens": children_n,
        "sortBy": "best",
        "currency": "EUR",
        "market": "es-ES",
        "countryCode": "ES"
    }

    headers = {
        "x-rapidapi-key": token,
        "x-rapidapi-host": "sky-scrapper.p.rapidapi.com"
    }

    async with session.get(url, headers=headers, params=querystring) as response:
        result = await response.json()
    
    if "data" not in result:
        print(f"Error en la respuesta para {depart_date} a {return_date}: {result}")  # Registro de la respuesta
        return None  # O retorna un DataFrame vacío si prefieres
        
    return result

async def extract_flight_info(flights_json):
    """
    Extrae información relevante de los itinerarios de vuelos desde los datos proporcionados por la API.

    Parámetros:
    flights_json (dict): JSON que contiene la información de vuelos devuelta por la API Sky Scrapper.

    Retorna:
    pandas.DataFrame: Un DataFrame con la información extraída, incluyendo destino, precio, duración, hora de salida y llegada,
                      número de escalas, y aerolíneas tanto para el vuelo de ida como para el de vuelta.
    """
    itineraries = flights_json["data"]["itineraries"]
    flight_info = {
        "destination": [],
        "price": [],
        "carrier_go": [],
        "duration_go": [],
        "departure_go": [],
        "arrival_go": [],
        "stops_go": [],
        "carrier_back": [],
        "duration_back": [],
        "departure_back": [],
        "arrival_back": [],
        "stops_back": []
    }

    for iti in itineraries:
        # Ida
        price = iti["price"]["raw"]
        destination = iti["legs"][0]["destination"]["name"]
        duration_go = iti["legs"][0]["durationInMinutes"]
        departure_go = iti["legs"][0]["departure"]
        arrival_go = iti["legs"][0]["arrival"]
        stops_go = iti["legs"][0]["stopCount"]
        carrier_go = iti["legs"][0]["carriers"]["marketing"][0]["name"]

        flight_info["price"].append(price)
        flight_info["destination"].append(destination)
        flight_info["duration_go"].append(duration_go)
        flight_info["departure_go"].append(departure_go)
        flight_info["arrival_go"].append(arrival_go)
        flight_info["stops_go"].append(stops_go)
        flight_info["carrier_go"].append(carrier_go)

        # Vuelta
        duration_back = iti["legs"][1]["durationInMinutes"]
        departure_back = iti["legs"][1]["departure"]
        arrival_back = iti["legs"][1]["arrival"]
        stops_back = iti["legs"][1]["stopCount"]
        carrier_back = iti["legs"][1]["carriers"]["marketing"][0]["name"]

        flight_info["duration_back"].append(duration_back)
        flight_info["departure_back"].append(departure_back)
        flight_info["arrival_back"].append(arrival_back)
        flight_info["stops_back"].append(stops_back)
        flight_info["carrier_back"].append(carrier_back)

    return pd.DataFrame(flight_info)

async def all_month_flights(token, session, origin_data, destination_data, months, adult_n, children_n):
    """
    Busca vuelos para un conjunto de meses entre un origen y varios destinos utilizando la API Sky Scrapper.

    Parámetros:
    token (str): Token de autenticación para acceder a la API.
    session (aiohttp.ClientSession): Sesión HTTP asíncrona.
    origin_data (tuple): Tupla que contiene el skyId y el JSON de la ciudad de origen.
    destination_data (tuple): Tupla que contiene el skyId y el JSON de la ciudad de destino.
    months (list): Lista de meses (como enteros) para los cuales se buscarán vuelos.
    adult_n (int): Número de adultos para el vuelo.
    children_n (int): Número de niños para el vuelo.
    
    Retorna:
    pandas.DataFrame: Un DataFrame que contiene información sobre los vuelos encontrados en los meses especificados.
    """
    df_list = []
    for month in months:
        for day in tqdm(range(10, monthrange(2025, month)[1] + 1)):
            depart_date = f'2025-{month:02}-{day-9:02}'
            return_date = f'2025-{month:02}-{day:02}'
            flight_json = await get_data(token, session, origin_data, destination_data, depart_date, return_date, adult_n, children_n)
            flight_info = await extract_flight_info(flight_json)
            df_list.append(flight_info)
    
    return pd.concat(df_list, ignore_index=True)

async def main(token, origin_data, destinations_data, adult_n, children_n):
    """
    Función principal que coordina la búsqueda de vuelos para múltiples destinos y compila los resultados en un DataFrame.

    Parámetros:
    token (str): Token de autenticación para acceder a la API.
    origin_data (tuple): Tupla que contiene el skyId y el JSON de la ciudad de origen.
    destinations_data (list): Lista de tuplas, cada una conteniendo el skyId y el JSON de una ciudad de destino.
    adult_n (int): Número de adultos para el vuelo.
    children_n (int): Número de niños para el vuelo.

    Retorna:
    pandas.DataFrame: Un DataFrame que contiene información sobre todos los vuelos encontrados para los destinos especificados.
    """
    og_data = origin_data
    months = [7, 8]
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for d_data in destinations_data:
            task = all_month_flights(token, session, og_data, d_data, months, adult_n, children_n)
            tasks.append(task)
        
        df_list = await asyncio.gather(*tasks)

    final_df = pd.concat(df_list, ignore_index=True)
    return final_df
