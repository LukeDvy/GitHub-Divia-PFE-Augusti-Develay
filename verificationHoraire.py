import pandas as pd
import datetime

# Chargement des fichiers GTFS dans des df
stops = pd.read_csv("GTFS/stops.txt", delimiter=",")
trips = pd.read_csv("GTFS/trips.txt", delimiter=",")
routes = pd.read_csv("GTFS/routes.txt", delimiter=",")

datas = pd.read_csv("Trip_By_Day/2023-10-26.csv", delimiter=",")

def miseEnForme(routeId: str):
    result = pd.merge(datas, stops, on="stop_id", how="inner")
    result = pd.merge(result, trips, on="trip_id", how="inner")
    result = pd.merge(result, routes, on="route_id", how="inner")

    result = result[
        result["route_id"].astype(str) == str(routeId)
    ]
    columns_to_display = [
        "trip_id",
        "stop_id",
        "stop_name",
        "route_long_name",
        "direction_id",
        "arrival_delay",
        "arrival_time",
        "departure_delay",
        "departure_time",
    ]
    for index, row in result.iterrows():
            result.loc[index, "departure_time"] = datetime.datetime.fromtimestamp(row["departure_time"])
    print("Trajet "
            + str(result["route_long_name"].loc[1])
        )
    result=result.sort_values(by="departure_time")
    result=result.drop_duplicates()
    for index, row in result.iterrows():
        print(
            "à l'arrêt "
            + str(row["stop_name"])
            + " départ à  "
            + str(row["departure_time"])
        )

miseEnForme("4-L3")