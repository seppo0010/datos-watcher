import urllib
from datetime import datetime, timedelta
from dateutil import parser
import json
import requests
import os

TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
BASE_URL = 'https://datos.gob.ar/'
now = datetime.now()

url = f'{BASE_URL}api/3/action/recently_changed_packages_activity_list'
data = requests.get(url).raise_for_status().json()

changes = []
for activity in data['result']:
    d = parser.parse(activity['timestamp'])
    if now - d < timedelta(days=1):
        changes.append(activity)

def format_change(change):
    activity_type = {
        'changed package': 'Paquete cambiado',
        'new package': 'Paquete agregado',
        'deleted package': 'Paquete borrado',
    }.get(change['activity_type'], change['activity_type'])

    return f'{activity_type}: {change["data"]["package"]["title"]}\n{BASE_URL}dataset/{change["data"]["package"]["name"]}'

message = '\n'.join(format_change(change) for change in changes)
print(f'Cambios del último día:\n{message}')
for change in changes:
    message = urllib.parse.quote(format_change(change))
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    requests.get(url).raise_for_status()
