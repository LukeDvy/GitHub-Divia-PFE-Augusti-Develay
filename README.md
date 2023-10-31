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

### Exemple fichier GTFS-RT vide :
```json
{
  "entity": [
    {
      "id": "",
      "trip_update": {
        "stop_time_update": [
          {
            "arrival": {
              "delay": 0,
              "time": ""
            },
            "departure": {
              "delay": 0,
              "time": ""
            },
            "stop_id": ""
          }
        ],
        "timestamp": "",
        "trip": {
          "direction_id": 0,
          "route_id": "",
          "schedule_relationship": "",
          "trip_id": ""
        },
        "vehicle": {
          "id": "",
          "label": ""
        }
      }
    }
  ]
}
```

## Création d'un fichier CSV par jour
Le script python `SaveAllDay.py` permet de générer un fichier CSV par jour avec les colonnes suivantes : `trip_id`, `stop_id`, `direction_id`, `arrival_delay`, `arrival_time`, `departure_delay`, `departure_time`.

Les fichiers sont indépendants chaques jours et sont nommé de la manère suivante : `AAAA-MM-JJ.csv`. Ils sont remplis au fur et à mesure de la journée en requêttant l'adresse permettant l'accès aux données GTFS-RT. Le requêtage est automatisé sur un serveur distant, en lançant toutes les minutes le script grâce à un crontab :
```bash
  $ * * * * *       /usr/bin/python3 /root/SaveAllDay/SaveAllDay.py
```

Le script supprimes les doublons potentielles sur les colonnes : `trip_id`, `stop_id`, `direction_id`, permettant de ne pas avoir des informations en doubles.

Pour récupérer les fichiers CSV du serveur distant à son envirronement local on utilise la commande suivante depuis l'envirronement local :
```bash
  $ scp -r pfe-divia:/root/SaveAllDay/Trip_By_Day .
```
Le préfixe <kbd>-r</kbd> permet de copier le répertoire complet à l'emplacement du serveur distant suivie, et de le coller à l'emplacement sur son envirronement local, ici <kbd>.</kbd>, qui signifie de le coller dans son emplecement actuel.