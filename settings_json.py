import json

settings_json = json.dumps([
    {
        'type': 'numeric',
        'title': 'Font size',
        'desc': 'Change font size',
        'section': 'Game Settings',
        'key': 'font_size',
    },
    {
        'type': 'options',
        'title': 'Change font name',
        'desc': 'Select a font of your choosing.',
        'section': 'Game Settings',
        'key': 'font_name',
        'options': ['Eurostile.ttf', 'Sackers-Gothic-Std-Light.ttf']
    },
    {
        'type': 'options',
        'title': 'Change volume',
        'desc': 'Change volume.',
        'section': 'Game Settings',
        'key': 'volume',
        'options': ['0', '0.2', '0.4', '0.6', '0.8', '0.9', '1']
    },

])
