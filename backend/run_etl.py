import sqlite3
import os
from etl.load_from_excel import main as run_etl_main

# --- Paths ---
# The backend directory, where this script is located
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
# The project root, which is one level above the 'backend' folder
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
# The final database path
DB_PATH = os.path.join(PROJECT_ROOT, 'strategic_shield.db')
# The schema file path
SCHEMA_PATH = os.path.join(PROJECT_ROOT, 'db', 'schema.sql')

def initialize_database():
    """
    Initializes the database by deleting the old DB file and creating a new one from the schema.
    """
    print(f"Initializing database at {DB_PATH}...")
    
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("Removed old database file.")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        with open(SCHEMA_PATH, 'r') as f:
            schema_sql = f.read()
        
        cursor.executescript(schema_sql)
        print("Database schema created successfully.")
    except FileNotFoundError:
        print(f"ERROR: Could not find the schema file at {SCHEMA_PATH}")
        raise
    finally:
        conn.commit()
        conn.close()

def main():
    """
    Main function to orchestrate the ETL process.
    """
    initialize_database()
    run_etl_main()

if __name__ == "__main__":
    main() 