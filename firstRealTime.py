from google.transit import gtfs_realtime_pb2
import urllib.request
import urllib

feed = gtfs_realtime_pb2.FeedMessage()
response = urllib.request.urlopen('https://proxy.transport.data.gouv.fr/resource/divia-dijon-gtfs-rt-trip-update')
feed.ParseFromString(response.read())
for entity in feed.entity:
  if entity.HasField('trip_update'):
    print(entity.trip_update)