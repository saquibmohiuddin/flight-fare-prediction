import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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

    dummy_year = pd.get_dummies(df["Airline"], prefix="Airline", drop_first= True)
    dummy_month = pd.get_dummies(df["Source"], prefix="Source", drop_first= True)
    dummy_crime_type = pd.get_dummies(df["Destination"], prefix="Destination", 
    drop_first= True)

    df = pd.concat([df, dummy_year, dummy_month, dummy_crime_type], axis=1)

    df.drop(["Airline", "Source", "Destination", "Date_of_Journey_year"], axis = 1, inplace = True)

    














