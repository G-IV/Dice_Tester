'''
This script will handle creating, managing, and storing data to sqlite3 database. 
'''

import sqlite3

DATABASE_PATH = '/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Database/dice.db'

def initialize_database():
    '''Initialize the database and create necessary tables if they don't exist.
    
    id: This should be applied to each tested dice
    timestamp: When the test was conducted
    motor position: in case we want to analyze results based on motor position
    dice result: the number on the top face of the dice
    image: path to the image captured when the dice came to a stop
    
    The primary key is a combination of timestamp and id to ensure uniqueness.
    '''
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_results (
            id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            motor_position REAL NOT NULL,
            dice_result INTEGER NOT NULL,
            image TEXT NOT NULL,
            PRIMARY KEY (timestamp, id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized and tables created if they didn't exist.")

def get_next_id():
    """
        Get the most recent id for a given dice, then return that id incremented by 1 for a new dice.  This will allow us to keep track of multiple dice and their results in the database, and allows users to not have to manually input an ID for each dice that is tested.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT MAX(id) FROM test_results')
    result = cursor.fetchone()
    conn.close()
    if result[0] is not None:
        return result[0] + 1
    else:
        return 1
    
def log_test_result(id, timestamp, motor_position, dice_result, img_path):
    """
        Logs the results of each test to the database, including the motor position, the result of the dice roll, and any errors that may occur during testing.  The timestamp is automatically generated when the entry is created.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    print(f"Logging test result to database: ID={id}, Timestamp={timestamp}, Motor Position={motor_position}, Dice Result={dice_result}, Confidence={img_path}")
    cursor.execute('''
        INSERT INTO test_results (timestamp, id, motor_position, dice_result, image)
        VALUES (?, ?, ?, ?, ?)
    ''', (timestamp, id, motor_position, dice_result, img_path))
    conn.commit()
    conn.close()

def get_dice_data(id):
    """
    Retrieve all test results for a specific dice ID from the database.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM test_results WHERE id = ?', (id,))
    results = cursor.fetchall()
    conn.close()
    return results

def clear_all_data():
    """
    Clear all data from the test_results table in the database.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM test_results')
    conn.commit()
    conn.close()
    print("All data cleared from the database.")

def clear_all_data_for_id(id):
    """
    Clear all data for a specific dice ID from the test_results table in the database.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM test_results WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    print(f"All data cleared for dice ID {id} from the database.")