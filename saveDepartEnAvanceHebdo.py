import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import os
import pytz

nom_GTFS = "GTFS_2023_11_07"

# Chargement des fichiers GTFS dans des df
routes = pd.read_csv(f"{nom_GTFS}/routes.txt", delimiter=",")

fichiers_csv = os.listdir("/root/SaveAllDay/Trip_By_Day")
for fichier_csv in fichiers_csv:
    # garde que la date du nom du fichier
    date_str = fichier_csv.split(".")[0].replace("-", "_")
    # nouveau nom dataframe
    nom_dataframe = f"datas_{date_str}"
    # création d'un dataframe par fichier csv
    globals()[nom_dataframe] = pd.read_csv(
        os.path.join("/root/SaveAllDay/Trip_By_Day", fichier_csv), delimiter=","
    )

original_timezone = pytz.timezone("UTC")
cet_timezone = pytz.timezone("CET")

dataframes_list = []
for i in range(1, 8):  # Commencer depuis hier, jusqu'à 1 semaine passée
    date = datetime.now() - timedelta(days=i)
    date_str = date.strftime("%Y_%m_%d")
    nom_dataframe = f"datas_{date_str}"
    try:
        df_jour = globals()[
            nom_dataframe
        ]  # Code pour récupérer le DataFrame du jour date
        dataframes_list.append(df_jour)
    except:
        print(f"Fichier csv non disponible pour la date suivante : {date_str}")

df_7lastday = pd.concat(dataframes_list, ignore_index=True)

class TripParJour:
    def __init__(self, data, date):
        self.data = data
        self.date = date


def routeParTripParJour(data_in):
    date = str(
        (
            original_timezone.localize(
                datetime.fromtimestamp(data_in["departure_time"].iloc[0])
            )
        ).astimezone(cet_timezone)
    )[:10]
    trips = pd.read_csv(f"{nom_GTFS}/trips.txt", delimiter=",")
    trips = trips.drop(columns="direction_id")
    result = pd.merge(data_in, trips, on="trip_id", how="inner")
    result = pd.merge(result, routes, on="route_id", how="inner")
    result = result.drop(
        columns=[
            "stop_id",
            "direction_id",
            "service_id",
            "shape_id",
            "trip_headsign",
            "trip_short_name",
            "agency_id",
            "route_short_name",
            "departure_time",
        ]
    )

    for index, row in result.iterrows():
        result.loc[index, "arrival_time"] = (
            original_timezone.localize(datetime.fromtimestamp(row["arrival_time"]))
        ).astimezone(cet_timezone)

    result["arrival_time"] = pd.to_datetime(result["arrival_time"])

    result["arrival_time"] = result["arrival_time"].dt.hour
    print(result["arrival_time"])
    for index, row in result.iterrows():
        if int(row["arrival_time"]) < 7:
            result.loc[index, "periode_journee"] = "La Nuit"
        elif int(row["arrival_time"]) >= 7 & int(row["arrival_time"]) < 12:
            result.loc[index, "periode_journee"] = "Le Matin"
        elif int(row["arrival_time"]) >= 12 & int(row["arrival_time"]) < 18:
            result.loc[index, "periode_journee"] = "L'Après Midi"
        else:
            result.loc[index, "periode_journee"] = "Le Soir"

    # columns restantes : [trip_id,arrival_delay,departure_delay,route_id,route_long_name]
    result = result.rename(columns={"arrival_delay": "arrival_delay_mean"})
    result = result.rename(columns={"departure_delay": "departure_delay_mean"})
    result["arrival_delay_min"] = result["arrival_delay_mean"]
    result["departure_delay_min"] = result["departure_delay_mean"]
    result["arrival_delay_max"] = result["arrival_delay_mean"]
    result["departure_delay_max"] = result["departure_delay_mean"]

    agg_funcs = {
        "trip_id": "count",
        "arrival_delay_mean": "mean",
        "arrival_delay_min": "min",
        "arrival_delay_max": "max",
        "departure_delay_mean": "mean",
        "departure_delay_min": "min",
        "departure_delay_max": "max",
        "route_long_name": "first",
        "route_type": "first",
    }

    # utilisation de  la méthode .groupby() pour regrouper par "route_id" et appliquer les opérations spécifiée, et selon la période de la journée
    result = (
        result.groupby(["route_id", "periode_journee"]).agg(agg_funcs).reset_index()
    )
    result = result.rename(columns={"trip_id": "trip_id_count"})

    # traduction de la colonne route_type de int à string : 0=Tram, 3=Bus
    result["route_type"] = result["route_type"].astype(str)
    for index, row in result.iterrows():
        if str(row["route_type"]) == "3":
            result.loc[index, "route_type"] = "Bus"
        if str(row["route_type"]) == "0":
            result.loc[index, "route_type"] = "Tramway"

    print(result)
    result.to_csv("SauvegardeHebdomadaire/departEnAvanceHebdo.csv", sep=",", index=False)
    return TripParJour(result, date)


routeParTripParJour(df_7lastday)