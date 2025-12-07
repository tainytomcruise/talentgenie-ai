import sqlite3

def add_quantity_column():
    db_path = 'talentgenie.db'
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("PRAGMA table_info(jobs)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'quantity' not in columns:
            print("Adding quantity column to jobs table...")
            cursor.execute("ALTER TABLE jobs ADD COLUMN quantity INTEGER DEFAULT 1")
            conn.commit()
            print("Column quantity added successfully.")
        else:
            print("Column quantity already exists.")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    add_quantity_column()
