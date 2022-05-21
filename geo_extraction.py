import numpy as np
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

def geo_extraction(df, col1 = "Source", col2 = "Destination"):

    """"
    This function get the coordinates for the airports based on the city efficiently
    (using minimal calls from geopy API based only on unique cities instead of iterating 
    over all the cities ) 
    """

    src = list(df[col1].unique())
    des = list(df[col2].unique())

    cities = []

    for i in src, des:
      cities.append(i)
    cities = list(set(np.ravel(cities)))

    airport_name = []

    for city in cities:
        airport_name.append(city + " International Airport")

    airports_dict = dict(zip(cities, airport_name))

    airport_src = []
    airport_des = []

    for i, j in zip(df[col1], df[col2]):
        for k, v in airports_dict.items():
            if i == k:
                airport_src.append(v)
            if j == k:
                airport_des.append(v)

    df[col1 + "_Airport"] = airport_src
    df[col2 + "_Airport"] = airport_des

    geolocator = Nominatim(user_agent="my-flight-fare")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    lat = []
    lon = []

    for airport in airport_name:
        location = geolocator.geocode(airport)
        lat.append(location.latitude)
        lon.append(location.longitude)

    geo = tuple(zip(lat, lon))

    airport_geo = dict(zip(airport_name, geo))

    src_geo = []
    des_geo = []

    for src_airport, des_airport in zip(df[col1 + "_Airport"], df[col2 + "_Airport"]):
        for k, v in airport_geo.items():
            if src_airport == k:
                src_geo.append(v)
            if des_airport == k:
                des_geo.append(v)

    df[[col1 + '_Lat', col1 + '_Lon']] = pd.DataFrame(src_geo, index=df.index)
    df[[col2 + '_Lat', col2 + '_Lon']] = pd.DataFrame(des_geo, index=df.index)

    return df 