import json
import os
from ttf_opensans import opensans

config_path = os.path.join('/var/www/feuerwehr-webapp', 'config.json')

with open(config_path, 'r', encoding='utf-8') as config_file:
    config = json.load(config_file)

FAHRZEUGE = config.get('FAHRZEUGE', [])
WEITERE_KRAEFTE = config.get('WEITERE_KRAEFTE', [])
DROHNE_CALENDAR = config.get('DROHNE_CALENDAR')
ROOM_CALENDAR = config.get('ROOM_CALENDAR')
FOOTER_TEXT = config.get('FOOTER_TEXT')

# OpenSans Schriftartenpfade
font_Headline_path = opensans(font_weight=600).path
font_Einsatzstichwort_path = opensans(font_weight=400).path