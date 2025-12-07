import sqlite3

def add_column():
    db_path = 'talentgenie.db'
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("PRAGMA table_info(jobs)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'input_data' not in columns:
            print("Adding input_data column to jobs table...")
            cursor.execute("ALTER TABLE jobs ADD COLUMN input_data TEXT")
            conn.commit()
            print("Column added successfully.")
        else:
            print("Column input_data already exists.")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    add_column()
