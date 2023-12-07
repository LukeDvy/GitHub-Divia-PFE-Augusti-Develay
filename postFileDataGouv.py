import requests
from datetime import datetime, timedelta

API = 'https://www.data.gouv.fr/api/1'
API_KEY = 'eyJhbGciOiJIUzUxMiJ9.eyJ1c2VyIjoiNjU2OWQ0N2I1ZGI0ZjdlM2Y3MzI1ZDM0IiwidGltZSI6MTcwMTk0MjA5Mi44ODYyNzM5fQ.EQdaM9K577gPRSboH22ThQRBexlF9Y_z5-4h1yiuspQV93mIJW3szDX1wtxdEiYrTQtD9TADLRKRcHwbrVnBBg'
DATASET = '6569d5e36408e968a823feb4'
HEADERS = {
    'X-API-KEY': API_KEY,
}


def api_url(path):
    return f"{API}{path}"


# selection fichier de la veille
selected_file = f"/root/SaveAllDay/Trip_By_Day/{datetime.now().date() - timedelta(days=1)}.csv"

# appel API POST file
url = api_url('/datasets/{}/upload/'.format(DATASET))
response = requests.post(url, files={
    'file': open(selected_file, 'rb'), # remplacer par le fichier à uploader
}, headers=HEADERS)
