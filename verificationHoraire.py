import pandas as pd
import datetime
import numpy as np

# Chargement des fichiers GTFS dans des df
stops = pd.read_csv("GTFS/stops.txt", delimiter=",")
routes = pd.read_csv("GTFS/routes.txt", delimiter=",")
datas = pd.read_csv("Trip_By_Day/2023-10-26.csv", delimiter=",")
stop_times = pd.read_csv("GTFS/stop_times.txt", delimiter=",")


def recupRouteId(tripId: str):
    trips = pd.read_csv("GTFS/trips.txt", delimiter=",")
    result = pd.merge(datas, stops, on="stop_id", how="inner")
    trips = trips.drop(columns="direction_id")
    result = pd.merge(result, trips, on="trip_id", how="inner")
    result = pd.merge(result, routes, on="route_id", how="inner")

    result = result[result["trip_id"].astype(str) == str(tripId)]
    print("Trajet " + str(result["route_id"].loc[1]))


def miseEnForme(routeId: str, tripId: str, directionId: int):
    trips = pd.read_csv("GTFS/trips.txt", delimiter=",")
    result = pd.merge(datas, stops, on="stop_id", how="inner")
    trips = trips.drop(columns="direction_id")
    result = pd.merge(result, trips, on="trip_id", how="inner")
    result = pd.merge(result, routes, on="route_id", how="inner")

    # rename colonne pour ne pas avoir de collisions avec les colonnes d'heures prévues
    result = result.rename(columns={'arrival_time': 'arrival_time_reel'})
    result = result.rename(columns={'departure_time': 'departure_time_reel'})

    result = result[result["route_id"].astype(str) == str(routeId)]

    result = result[result["trip_id"].astype(str) == str(tripId)]

    result = result[result["direction_id"] == directionId]

    # Ajout des colonnes "arrival_time" et "departure_time", afin de comparer les horaires réélles et prévues
    result = pd.merge(result, stop_times, on=["trip_id", "stop_id"], how="inner")

    columns_to_display = [
        "trip_id",
        "stop_id",
        "stop_name",
        "route_long_name",
        "direction_id",
        "arrival_delay",
        "arrival_time_reel",
        "departure_delay",
        "departure_time_reel",
    ]
    for index, row in result.iterrows():
        result.loc[index, "arrival_time_reel"] = datetime.datetime.fromtimestamp(
            row["arrival_time_reel"]
        )
        result.loc[index, "departure_time_reel"] = datetime.datetime.fromtimestamp(
            row["departure_time_reel"]
        )
    print("Trajet " + str(result["route_long_name"].loc[1]))
    result = result.sort_values(by="departure_time_reel")
    result = result.drop_duplicates(subset=["trip_id", "stop_id"], keep="last")
    for index, row in result.iterrows():
        print(
            "départ à           "
            + str(row["departure_time_reel"])
            + "     normalement prévue à "
            + str(row["departure_time"])
            + "          de l'arrêt "
            + str(row["stop_name"])
        )


# recupRouteId("10-L3-1-1-141100")
miseEnForme("4-L3", "10-L3-1-1-141100", 1)
