# GitHub-Divia-PFE-Augusti-Develay
 Répertoire GitHub du Projet de fin d'étude sur l'analyse de données du réseau Divia à Dijon.

## GTFS Description des fichiers
### agency.txt
`agency_id`, `agency_name`, `agency_url`, `agency_timezone`
Description de l'agence

### calendar_dates.txt
`service_id`, `date`, `exception_type`
Liste de tous les services avec la date associée, fichier en lien avec calendar.txt et trips.txt

### calendar.txt
`service_id`, `monday`, `tuesday`, `wednesday`, `thursday`, `friday`, `saturday`, `sunday`, `start_date`, `end_date`
Détail du calendrier en fonction du `service_id` associé à calendar.txt

### routes.txt
`route_id`, `agency_id`, `route_short_name`, `route_long_name`, `route_type`
Détail des routes associés à `route_id` lié au fichier  trips.txt

### shapes.txt
Différents points géographiques permettant de créer le réseau sur une carte

### stop_times.txt
`trip_id`, `arrival_time`, `departure_time`, `stop_id`, `stop_sequence`, `pickup_type`, `drop_off_type`
Données statiques sur les prévisions des horaires de chaques trips, associés à `trip_id` lié au fichier trips.txt

### trips.txt
`route_id`, `service_id`, `shape_id`, `trip_id`, `trip_headsign`, `trip_short_name`, `direction_id`
Fichier permettant de lier plusieurs fichiers (calendar_dates.txt, stop_times.txt, calendar.txt), rendant le tout comme une base de données. Et, donnant des informations précises sur un trip en particulier (`direction_id` : sens de circulation)

### stop_name.txt
`stop_id`,`stop_name`
Fichier réalisé hors récupération sur les serveurs du gouvernement. Réalisé à partir d'un [fichier sur GitHub](https://github.com/Tsuna77/TransportDijon/blob/2ead8e6db3906e459aeb1fdb04e0a748ffaa755f/app/src/main/java/fr/tsuna/transportdijon/MyDB.java#L48), et après avoir réalisé du post-traitement à l'aide de la bibliothèque Pandas sur Python.

## GTFS-RT Description des fichiers
Accès aux données en temps réel à l'adresse suivante : `https://proxy.transport.data.gouv.fr/resource/divia-dijon-gtfs-rt-trip-update`. Les données sont collectées en Protobuf et traduites en format JSON.
Première requête simple commentée dans le fichier [firstRealTime.py](https://github.com/LukeDvy/GitHub-Divia-PFE-Augusti-Develay/blob/main/firstRealTime.py), le nom de la fonction est `findStopById(target_trip_id:str,target_stop_id:str)`.