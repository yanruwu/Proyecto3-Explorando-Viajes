# Explorando Viajes con APIs y Web Scraping: Diseñando las Vacaciones Perfectas ✈️🌍

## Descripción del Proyecto
Este proyecto tiene como objetivo diseñar propuestas de vacaciones ideales utilizando la recopilación de datos de vuelos, alojamiento y actividades en varias ciudades. Se emplean APIs y web scraping para obtener información actualizada sobre opciones de vuelo y hoteles, facilitando así la creación de itinerarios personalizados para diferentes tipos de clientes. En este caso, se ha escogido como cliente ficticio a una familia de 4 miembros. 👨‍👩‍👧‍👦

### Progreso del Proyecto:

- **Recopilación de datos**: Se han utilizado las APIs de [Sky Scraper](https://rapidapi.com/sky-scraper/api/sky-scrapper) y [Booking.com](https://rapidapi.com/booking-com/api/booking-com) para obtener información sobre vuelos y alojamientos. En particular, se han recopilado los datos de vuelos a Budapest y Milán, así como información sobre alojamientos disponibles en ambos destinos. 🏨✈️

- **Análisis exploratorio de datos (EDA)**: A través de la implementación de notebooks en Jupyter, se ha llevado a cabo un análisis detallado de los datos recopilados. Esto incluye la identificación de patrones en los precios de los vuelos, la comparación de costos de alojamiento y la evaluación de la calidad y cantidad de actividades disponibles. 📊

- **Funcionalidades del código**:
  - Se ha desarrollado una serie de funciones en archivos Python (`activityfunc.py`, `flightfunc.py`, `hotelfunc.py`) que permiten la extracción y procesamiento de datos relacionados con actividades, vuelos y hoteles, facilitando el análisis de manera modular y eficiente. 🧑‍💻
  - Se han implementado funcionalidades asincrónicas utilizando `aiohttp` para optimizar las solicitudes a las APIs, lo que mejora la eficiencia del proceso de recopilación de datos. ⚡
  - Optimización de Procesos Asíncronos: Para mejorar la eficiencia en la recopilación de datos, se implementaron técnicas de programación asíncrona utilizando `asyncio`. Además, se utilizó `concurrent.futures.ThreadPoolExecutor` para realizar solicitudes en paralelo, permitiendo así un procesamiento más rápido de las consultas a la API. También se empleó `Janus` para facilitar la comunicación entre el código asíncrono y las operaciones de subproceso, garantizando que la recolección de datos se llevara a cabo de manera fluida y efectiva. 🔄

- **Visualización y comparativa de costos**: Se ha creado un análisis que permite visualizar la diferencia de precios entre vuelos y alojamientos en ambos destinos. También se ha destacado que Budapest ofrece, en general, opciones de alojamiento más económicas y mejor puntuación en comparación con Milán. 💰📈

## Estructura del Proyecto

```
├── datos                          # Carpeta que contiene los archivos de datos recopilados
│   ├── accommodation_budapest.csv  # Datos de alojamiento en Budapest
│   ├── accommodation_milan.csv     # Datos de alojamiento en Milán
│   ├── buda_flights.csv            # Información sobre vuelos hacia Budapest
│   ├── mila_flights.csv            # Información sobre vuelos hacia Milán
│   ├── budapest_act.csv            # Datos sobre actividades en Budapest
│   └── milan_act.csv               # Datos sobre actividades en Milán
├── notebooks                       # Carpeta que contiene los notebooks Jupyter para análisis
│   ├── activities.ipynb            # Análisis de las actividades disponibles en los destinos
│   ├── flights.ipynb               # Análisis de los datos de vuelos
│   ├── hotels.ipynb                # Análisis de los datos de alojamiento
│   └── EDA.ipynb                   # Notebook de Análisis Exploratorio de Datos (EDA) 
├── src                             # Carpeta que contiene los scripts fuente del proyecto
│   ├── activityfunc.py             # Funciones para manejar datos de actividades
│   ├── flightfunc.py               # Funciones para manejar datos de vuelos
│   └── hotelfunc.py                # Funciones para manejar datos de hoteles
├── environment.yml                 # Archivo de configuración para gestionar dependencias del entorno
└── README.md                       # Archivo README que describe el proyecto y su uso
```



## Instalación y Requisitos

Para configurar el entorno de desarrollo y asegurarte de que todas las dependencias necesarias estén instaladas, sigue estos pasos:

### Requisitos

- Python 3.7 o superior 🐍
- [Anaconda](https://www.anaconda.com/products/distribution) o [Miniconda](https://docs.conda.io/en/latest/miniconda.html) (opcional, pero recomendado)

### Paquetes Necesarios

El proyecto utiliza los siguientes paquetes:

- [`pandas`](https://pandas.pydata.org/pandas-docs/stable/): Para la manipulación y análisis de datos.
- [`numpy`](https://numpy.org/doc/stable/): Para operaciones numéricas y manejo de arrays.
- [`aiohttp`](https://docs.aiohttp.org/en/stable/): Para realizar solicitudes HTTP de manera asíncrona.
- [`requests`](https://docs.python-requests.org/en/latest/): Para realizar solicitudes HTTP sencillas.
- [`tqdm`](https://tqdm.github.io/): Para mostrar barras de progreso en loops.
- [`jupyter`](https://jupyter.org/documentation): Para ejecutar notebooks y análisis interactivos.
- [`matplotlib`](https://matplotlib.org/stable/users/index.html): Para la visualización de datos.
- [`seaborn`](https://seaborn.pydata.org/): Para visualización estadística de datos.

### Instalación

1. **Clona el repositorio:**

   ```bash
   git clone https://github.com/yanruwu/Proyecto3-Explorando-Viajes
   cd Proyecto3-Explorando-Viajes
2. **Crea un entorno virtual:**

    Para crear el entorno de Conda, usa el siguiente comando:
    ```bash
    conda env create -f environment.yml
    ```
    O si prefieres usar venv:
    ```bash
    python -m venv venv
    source venv/bin/activate  # En macOS/Linux
    venv\Scripts\activate     # En Windows
    ```
## Conclusiones
A partir del análisis realizado, se han obtenido varias conclusiones clave que pueden guiar la elección del destino y la planificación de las vacaciones para la familia:

- **Costos de Vuelos**: Los vuelos hacia Budapest resultan ser significativamente más caros que hacia Milán, con una diferencia promedio de 400 €. Esto sugiere que, dependiendo del presupuesto, Milán podría ser la opción más asequible para el viaje. 💸

- **Días y Meses de Compra**: Para ambos destinos, se ha observado que los viernes son los días menos favorables para comprar billetes de avión. En cuanto a los meses, se recomienda evitar julio para Budapest y agosto para Milán, ya que los precios suelen ser más altos en esos períodos. 📅

- **Alojamiento**: En general, Budapest ofrece opciones de alojamiento más económicas y con mejores calificaciones en comparación con Milán. Esto puede resultar ventajoso para una familia que busca maximizar su experiencia sin exceder su presupuesto. 🏡

- **Días para Reservar Alojamiento**: Los miércoles son los peores días para reservar alojamiento en Milán, mientras que los jueves son menos favorables en Budapest. Sin embargo, el precio de los alojamientos en Budapest suele ser más bajo, con una diferencia que puede alcanzar los 400 €. 🗓️

- **Calidad de Alojamiento**: Los alojamientos en Budapest no solo son más baratos, sino que también presentan una puntuación y ubicación superior en comparación con los de Milán, lo que puede influir en la satisfacción general de la familia. ⭐

- **Actividades**: Aunque Milán cuenta con una mayor cantidad de actividades disponibles, Budapest se destaca por ofrecer una mayor proporción de actividades gratuitas, lo que podría ser un factor importante para las familias que buscan entretenimiento sin costos adicionales. 🎉

En resumen, tanto Budapest como Milán presentan opciones interesantes y atractivas para unas vacaciones familiares. Sin embargo, Budapest se perfila como la alternativa más económica y con mejor calidad de alojamiento, lo que lo convierte en un destino muy adecuado para esta familia. 🌟


## 🔄 Próximos Pasos 
- Aumentar los datos recogidos en el ámbito de las actividades.
- Aumentar el rango de búsqueda e implementar un ajuste más intuitivo de los parámetros de las queries.
- Implementar una interfaz de selección.

Gran parte de ello dependería de las llamadas limitadas a las APIs, por lo que sería interesante implementar una gran parte vía scraping. 🔍

## 🤝 Contribuciones
Las contribuciones son bienvenidas. Si deseas mejorar el proyecto, por favor abre un pull request o una issue.