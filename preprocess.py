import numpy as np
import pandas as pd
from sklearn.metrics import r2_score
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from math import radians, cos, sin, asin, sqrt
from sklearn.preprocessing import MinMaxScaler


def year_month_extract(df, col):
    df[col + "_year"] = df[col].dt.year
    df[col + "_month"] = df[col].dt.month
    df[col + "_day"] = df[col].dt.day

    return year_month_extract

def duration_minutes(df): 
    df["Duration"] = df["Duration"].str.replace("h", "*60").str.replace(' ','+').str.replace("m","*1").apply(eval)

    return df 

def dep_arrival_extract(df, col):
    df[col + "_hour"] = df[col].dt.hour
    df[col + "_minute"] = df[col].dt.minute
    return dep_arrival_extract

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

def haversine_dist(lon1, lat1, lon2, lat2):

    lat1 = np.radians(lat1)
    lat2 = np.radians(lat2)
    lon1 = np.radians(lon1)
    lon2 = np.radians(lon2)

    # Haversine formula 
    dlat = lat2 - lat1
    dlon = lon2 - lon1 
    a = np.sin(dlat / 2.0)** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2

    c = 2 * np.arcsin(np.sqrt(a))

    r = 6371 # radius of earth in km

    distance = c * r

    return distance

def add_distance(df):
    df["flight_distance"] = haversine_dist(df["Source_Lon"], 
    df["Source_Lat"], 
    df["Destination_Lon"], df["Destination_Lat"])

    df.drop(["Source_Lat", "Source_Lon", "Destination_Lat", "Destination_Lon"], axis = 1, inplace=True)
    return df

def x_var(df):
    df = df.loc[:, ['Duration', 'stop', 'month', 'day', 'dep_hr', 'dep_min',
       'arr_hr', 'arr_min', 'flight_distance', 'Airline_Air India',
       'Airline_GoAir', 'Airline_IndiGo', 'Airline_Jet Airways',
       'Airline_Jet Airways Business', 'Airline_Multiple carriers',
       'Airline_Multiple carriers Premium economy', 'Airline_SpiceJet',
       'Airline_Trujet', 'Airline_Vistara', 'Airline_Vistara Premium economy',
       'Source_Chennai', 'Source_Kolkata', 'Source_Mumbai', 'Source_New Delhi',
       'Destination_Cochin', 'Destination_Hyderabad', 'Destination_Kolkata',
       'Destination_New Delhi']]

    return df

def y_var(df):
    df = df["Price"]

    return df


def preprocess_data(df):

    df["Date_of_Journey"] = pd.to_datetime(df["Date_of_Journey"])

    year_month_extract(df, "Date_of_Journey")

    df = df.dropna()
    df = df.reset_index(drop = True)
    df.drop(["Date_of_Journey", "Route", "Additional_Info"], axis = 1, inplace=True)

    duration_minutes(df)

    df["Dep_Time"] = pd.to_datetime(df["Dep_Time"])
    df["Arrival_Time"] = pd.to_datetime(df["Arrival_Time"])

    df.replace({"non-stop": 0, "1 stop": 1, "2 stops": 2, "3 stops": 3, "4 stops": 4}, 
    inplace = True)

    dep_arrival_extract(df, "Dep_Time")
    dep_arrival_extract(df, "Arrival_Time")

    df.drop(["Dep_Time", "Arrival_Time"], axis = 1, inplace = True)

    df.rename(columns = {'Total_Stops':'stop','Date_of_Journey_month':'month', 
                     'Date_of_Journey_day':'day', "Dep_Time_hour": "dep_hr", 
                     "Dep_Time_minute":"dep_min", "Arrival_Time_hour":"arr_hr", 
                     "Arrival_Time_minute":"arr_min"}, inplace = True)

    df = df.replace("Delhi", "New Delhi")
    df = df.replace("Banglore", "Bengaluru")

    geo_extraction(df, "Source", "Destination")

    df.drop(["Source_Airport", "Destination_Airport"], axis = 1, inplace = True)

    add_distance(df)

    dummy_year = pd.get_dummies(df["Airline"], prefix="Airline", drop_first= True)
    dummy_month = pd.get_dummies(df["Source"], prefix="Source", drop_first= True)
    dummy_crime_type = pd.get_dummies(df["Destination"], prefix="Destination", 
    drop_first= True)

    df = pd.concat([df, dummy_year, dummy_month, dummy_crime_type], axis=1)

    df.drop(["Airline", "Source", "Destination", "Date_of_Journey_year"], axis = 1, inplace = True)

    df.to_csv("test_cleaned.csv", index=False)























