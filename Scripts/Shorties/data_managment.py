from Scripts.Modules import data
from pathlib import Path

DATABASE_PATH = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Database/dice.db')

db = data.DatabaseManager(db_path=DATABASE_PATH)

db.clear_all_data()
# print(data.get_dice_data(5))