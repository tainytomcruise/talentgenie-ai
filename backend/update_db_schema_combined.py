import sqlite3
import os

def update_schema():
    # Path to the database file in the instance directory
    db_path = os.path.join('instance', 'talentgenie.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check existing columns
        cursor.execute("PRAGMA table_info(jobs)")
        columns = [info[1] for info in cursor.fetchall()]
        print(f"Existing columns: {columns}")
        
        # Add input_data column
        if 'input_data' not in columns:
            print("Adding input_data column...")
            cursor.execute("ALTER TABLE jobs ADD COLUMN input_data TEXT")
            print("Column input_data added.")
        else:
            print("Column input_data already exists.")
            
        # Add quantity column
        if 'quantity' not in columns:
            print("Adding quantity column...")
            cursor.execute("ALTER TABLE jobs ADD COLUMN quantity INTEGER DEFAULT 1")
            print("Column quantity added.")
        else:
            print("Column quantity already exists.")
            
        conn.commit()
        conn.close()
        print("Schema update complete.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_schema()
