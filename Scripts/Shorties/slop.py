'''
This file is just to try things out.
'''
import json
import pprint
from Scripts.Modules.Feed import feed
from pathlib import Path

MODEL = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Scripts/Modules/Analyzers/Models/pips_by_pattern')
JSON_PATH = Path(MODEL, 'notes.json')

categories = None

with open(JSON_PATH, 'r') as f:
    categories = json.load(f)

pprint.pprint(categories)