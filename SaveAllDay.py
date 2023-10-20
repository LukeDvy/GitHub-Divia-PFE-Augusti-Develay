from google.transit import gtfs_realtime_pb2
import urllib.request
import urllib
from firstScriptGTFS import affichageToutesLignesByDate
from datetime import datetime, date
import pandas as pd
import csv
import os
import time


def SaveAllStopByDay():
    # lecture du GTFS-RT
    feed = gtfs_realtime_pb2.FeedMessage()
    response = urllib.request.urlopen(
        "https://proxy.transport.data.gouv.fr/resource/divia-dijon-gtfs-rt-trip-update"
    )
    feed.ParseFromString(response.read())

    nomFichier = f"Trip_By_Day/{str(date.today())}.csv"
    newFichier = os.path.isfile(nomFichier)

    with open(nomFichier, "a", newline="") as fichier:
        writer = csv.writer(fichier, delimiter=",")

        # si nouveau fichier
        if not newFichier:
            writer.writerow(
                [
                    "trip_id",
                    "stop_id",
                    "direction_id",
                    "arrival_delay",
                    "arrival_time",
                    "departure_delay",
                    "departure_time",
                ]
            )

        # listeTrip=affichageToutesLignesByDate('20231207')
        trip_id = ""
        stop_id = ""
        direction_id = ""
        arrival_delay = ""
        arrival_time = ""
        departure_delay = ""
        departure_time = ""
        for entity in feed.entity:
            if entity.HasField("trip_update"):
                for id_trip in entity.trip_update.stop_time_update:
                    trip_id = str(entity.trip_update.trip.trip_id)
                    stop_id = str(id_trip.stop_id)
                    direction_id = str(entity.trip_update.trip.direction_id)
                    arrival_delay = str(id_trip.arrival.delay)
                    arrival_time = str(id_trip.arrival.time)
                    departure_delay = str(id_trip.departure.delay)
                    departure_time = str(id_trip.departure.time)

                    # creation ligne
                    nouvelle_ligne = [
                        trip_id,
                        stop_id,
                        direction_id,
                        arrival_delay,
                        arrival_time,
                        departure_delay,
                        departure_time,
                    ]
                    # Ajouter la nouvelle ligne de données
                    writer.writerows([nouvelle_ligne])

        # suppression des doublons sur les colonnes 'trip_id' et 'stop_id'
        df = pd.read_csv(nomFichier, delimiter=",")
        df = df.drop_duplicates(subset=["trip_id", "stop_id"], keep="last")
        df.to_csv(nomFichier, sep=",", index=False)

    return "good"


# appel de la fonction et écriture dans le fichier CSV toutes les 60 secondes
SaveAllStopByDay()

