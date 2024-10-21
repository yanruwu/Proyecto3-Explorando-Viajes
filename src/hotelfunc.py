import numpy as np
import pandas as pd
from tqdm import tqdm
from calendar import monthrange
import aiohttp
import asyncio
import random as rand
import os
import requests

def get_location_ids(destinations, api_key):
    """
    Obtiene los IDs de los destinos a partir de la API de Booking.com.

    Args:
        destinations (list): Lista de nombres de destinos a buscar.
        api_key (str): La clave de API para autenticar las solicitudes.

    Returns:
        list: Lista de IDs de destinos obtenidos de la API.
    """
    url_loc = "https://booking-com.p.rapidapi.com/v1/hotels/locations"
    
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "booking-com.p.rapidapi.com"
    }
    
    loc_ids = []
    
    for loc in destinations:
        querystring = {"locale": "es", "name": loc}
        response = requests.get(url_loc, headers=headers, params=querystring)
        
        if response.status_code == 200:
            loc_ids.append(response.json()[0]["dest_id"])
        else:
            print(f"Error al obtener ID para {loc}: {response.status_code}")
    
    return loc_ids

def extract_hotel_info(hotel_data):
    """
    Extrae información relevante de los datos de hoteles.

    Args:
        hotel_data (list): Lista de diccionarios con datos de hoteles.

    Returns:
        pd.DataFrame: DataFrame con la información extraída de los hoteles, incluyendo nombre, precio,
                      calificación, distancia del centro, tipo de alojamiento y ciudad.
    """
    result = dict(hotel_name=[], price=[], rating=[], distance_from_center=[], acc_type=[], city=[])

    for hotel in hotel_data:
        hotel_name = hotel.get("hotel_name", np.nan)
        price = hotel.get("min_total_price", np.nan)
        rating = hotel.get("review_score", np.nan)
        distance_from_center = hotel.get("distance_to_cc", np.nan)
        acc_type = hotel.get("accommodation_type_name", np.nan)
        city = hotel.get("city_trans", np.nan)

        result["hotel_name"].append(hotel_name)
        result["price"].append(price)
        result["rating"].append(rating)
        result["distance_from_center"].append(distance_from_center)
        result["acc_type"].append(acc_type)
        result["city"].append(city)

    df_hotel = pd.DataFrame(result)
    return df_hotel

async def extract_hotel_info_loc(session, loc_id, children_ages, adult_n, room_n, trip_duration, year, token):
    """
    Realiza una búsqueda de hoteles en una ubicación específica y extrae la información relevante.

    Args:
        session (aiohttp.ClientSession): Sesión HTTP asíncrona para realizar las solicitudes.
        loc_id (str): ID del destino para la búsqueda de hoteles.
        children_ages (str): Edades de los niños como una cadena separada por comas.
        adult_n (int): Número de adultos en la búsqueda.
        room_n (int): Número de habitaciones en la búsqueda.
        trip_duration (int): Duración del viaje en días.
        year (int): Año en el que se realizará el viaje.
        token (str): La clave de API para autenticar las solicitudes.

    Returns:
        list: Lista de DataFrames con la información de hoteles para cada día de la búsqueda.
    """
    url = "https://booking-com.p.rapidapi.com/v1/hotels/search"
    headers = {
        "x-rapidapi-key": token,
        "x-rapidapi-host": "booking-com.p.rapidapi.com"
    }

    list_df_hotel = []
    page = 1

    for month in tqdm(range(7, 9)):
        day_in = 1
        day_out = day_in + trip_duration - 1

        while day_out <= monthrange(year, month)[1]:
            date_in = pd.to_datetime(f"{year}-{month}-{day_in}").date()
            date_out = pd.to_datetime(f"{year}-{month}-{day_out}").date()

            querystring = {
                "children_ages": children_ages,
                "page_number": page,
                "adults_number": adult_n,
                "children_number": len(children_ages.split(',')),
                "room_number": room_n,
                "include_adjacency": "true",
                "units": "metric",
                "categories_filter_ids": "class::3,class::4,class::5",
                "checkout_date": str(date_out),
                "dest_id": loc_id,
                "filter_by_currency": "EUR",
                "dest_type": "city",
                "checkin_date": str(date_in),
                "order_by": "popularity",
                "locale": "en-gb"
            }

            async with session.get(url, headers=headers, params=querystring) as response:
                if response.status == 200:
                    data = await response.json()
                    hotel_info = extract_hotel_info(data["result"])

                    dias = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]

                    hotel_info["date_in"] = date_in
                    hotel_info["date_out"] = date_out
                    hotel_info["day_in"] = dias[date_in.weekday()-1]
                    hotel_info["day_out"] = dias[date_out.weekday()-1]

                    list_df_hotel.append(hotel_info)
                else:
                    print(response.status)
            day_in += 1
            day_out = day_in + trip_duration - 1
    return list_df_hotel

async def main(loc_ids, token):
    """
    Función principal para coordinar la búsqueda de hoteles en múltiples ubicaciones.

    Args:
        loc_ids (list): Lista de IDs de destinos para buscar hoteles.
        token (str): La clave de API para autenticar las solicitudes.

    Returns:
        list: Lista de DataFrames con información de hoteles para todas las ubicaciones.
    """
    children_n = 1
    children_ages = ",".join(rand.choices([str(a) for a in range(1, 11)], k=children_n))
    adult_n = 2
    room_n = 1
    trip_duration = 10
    year = 2025 

    async with aiohttp.ClientSession() as session:
        tasks = []
        for loc_id in tqdm(loc_ids):
            task = extract_hotel_info_loc(session, loc_id, children_ages, adult_n, room_n, trip_duration, year, token)
            tasks.append(task)
        results = await asyncio.gather(*tasks)

        final_df = [item for sublist in results for item in sublist]

        return final_df
