from google.transit import gtfs_realtime_pb2
import urllib.request
import urllib
from firstScriptGTFS import affichageToutesLignesByDate
from datetime import datetime
import pandas as pd

feed = gtfs_realtime_pb2.FeedMessage()
response = urllib.request.urlopen('https://proxy.transport.data.gouv.fr/resource/divia-dijon-gtfs-rt-trip-update')
feed.ParseFromString(response.read())

#fonction renvoyant la section JSON donnant les informations sur les horaires en fonction de l'id du trip à un arrêt précis
def findStopById(target_trip_id:str,target_stop_id:str):
    for entity in feed.entity:
        if entity.HasField('trip_update'):
            if entity.trip_update.trip.trip_id == target_trip_id: #recherche de la section comportant l'id du trip souhaité
                for stop_time_update in entity.trip_update.stop_time_update:
                    if stop_time_update.stop_id == target_stop_id: #recherche de la sous-section comportant l'id de l'arrêt souhaité
                        print("Arrêt trouvé pour le trip_id recherché:")
                        print(stop_time_update)
                        return stop_time_update

#fonction renvoyant la section JSON donnant les informations sur les horaires en fonction de l'id du trip à un arrêt précis. Retourne le retard moyen
def findTripByStopId(target_stop_id:str):
    average_delay=0
    countStop=0
    countTotal=0
    #récupération du nom de la ligne
    listeTrip=affichageToutesLignesByDate('20231207')
    for index, row in listeTrip.iterrows():
        if str(row['stop_id'])==target_stop_id:
            print("Trajet en "+str(row['route_type'])+" sur la ligne "+str(row['route_long_name'])+" à l'arrêt "+str(row['stop_name']))
            print("Arrêt trouvé pour le trip_id recherché:")
    for entity in feed.entity:
        if entity.HasField('trip_update'):
            for stop_time_update in entity.trip_update.stop_time_update:
                if stop_time_update.stop_id == target_stop_id: #recherche de la sous-section comportant l'id de l'arrêt souhaité
                    if str(stop_time_update.schedule_relationship) == "0": #0=SCHEDULED, 1=SKIPPED
                        average_delay=average_delay+int(stop_time_update.arrival.delay)
                        countStop=countStop+1
                    countTotal+=1
                    #print(stop_time_update)
                    print("Numéro trip : "+entity.trip_update.trip.trip_id)
    print(str(countTotal-countStop)+" arrêts annulés sur "+str(countTotal)+" arrêts programmés")
    return "Delai moyen de "+str(average_delay/countStop)+" secondes"

# Convertir le timestamp en une date réelle
#date_reelle = datetime.utcfromtimestamp(_date)

findStopById("29-T2-14-1-100357","4-1459")
print(findTripByStopId("4-1459"))