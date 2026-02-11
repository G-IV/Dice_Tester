from Scripts.Modules.Data import database
from pathlib import Path

DATABASE_PATH = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Database/dice.db')

db = database.DatabaseManager(db_path=DATABASE_PATH)

db.clear_all_data()
# print(data.get_dice_data(5))