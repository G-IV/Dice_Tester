import sqlite3

DATABASE_PATH = 'die_tester_results.db'

def delete_database():
    """
        Deletes the database file.  This can be used to reset the database and start fresh with new test results.
    """
    import os
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)
        print("Database deleted successfully.")
    else:
        print("Database file does not exist.")

def initialize_database():
    """
        Initializes the database and creates the necessary table if it doesn't already exist.  The table will include columns for the ID, timestamp, motor position, dice result, and any errors that may occur during testing.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_results (
            id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            motor_position REAL NOT NULL,
            dice_result INTEGER NOT NULL,
            confidence FLOAT NOT NULL,
            PRIMARY KEY (timestamp, id)
        )
    ''')
    conn.commit()
    conn.close()

def drop_table(db_path, table_name='test_results'):
    """
        Function to drop the specified table from the database.  This can be used to reset the test results and start fresh with new results without having to delete the entire database.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    conn.commit()
    conn.close()
    print("Table '{}' dropped successfully.".format(table_name))

def get_table_columns(db_path, table_name='test_results'):
    """
    Function to retrieve column names from a specified table in the database.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns_info = cursor.fetchall()
    
    column_names = [col[1] for col in columns_info]
    
    conn.close()
    print("Column names in table '{}': {}".format(table_name, column_names))
    return column_names

def clear_table(db_path, table_name='test_results'):
    """
        Function to clear all data from the specified table in the database.  This can be used to reset the test results and start fresh with new results without having to delete the entire database or drop the table.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {table_name}")
    conn.commit()
    conn.close()
    print("Table '{}' cleared successfully.".format(table_name))

def read_results_from_db(db_path):
    """
        Function to read the results of the dice tests from the database and return them as a list of dictionaries, where each dictionary represents a single test result with keys for the motor position, the result of the dice roll, and any errors that may have occurred during testing.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT motor_position, dice_result, confidence FROM test_results")
    rows = cursor.fetchall()
    
    results = []
    print("{} results found in the database.".format(len(rows)))
    print("[")
    for row in rows:
        print(row)
        result = {
            "motor_position": row[0],
            "dice_result": row[1],
            "confidence": row[2]
        }
        # print("  {}".format(result))
        results.append(result)
    
    conn.close()
    print("]")
    return results
# initialize_database()
# get_table_columns(DATABASE_PATH)
# clear_table(DATABASE_PATH)
# delete_database()
# drop_table(DATABASE_PATH)
read_results_from_db(DATABASE_PATH)
