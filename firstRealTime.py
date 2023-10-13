from google.transit import gtfs_realtime_pb2
import urllib.request
import urllib

feed = gtfs_realtime_pb2.FeedMessage()
response = urllib.request.urlopen('https://proxy.transport.data.gouv.fr/resource/divia-dijon-gtfs-rt-trip-update')
feed.ParseFromString(response.read())

def findStopById(target_trip_id:str,target_stop_id:str):
    for entity in feed.entity:
        if entity.HasField('trip_update'):
            if entity.trip_update.trip.trip_id == target_trip_id:
                for stop_time_update in entity.trip_update.stop_time_update:
                    if stop_time_update.stop_id == target_stop_id:
                        print("Arrêt trouvé pour le trip_id recherché:")
                        print(stop_time_update)
                        return stop_time_update

findStopById("29-T2-14-1-100357","4-1459")