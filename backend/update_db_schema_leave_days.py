from app_modular import app, db
from sqlalchemy import text

def update_schema():
    with app.app_context():
        # Add number_of_days column to leave_requests table
        try:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE leave_requests ADD COLUMN number_of_days FLOAT"))
                conn.commit()
            print("Successfully added number_of_days column to leave_requests table")
        except Exception as e:
            print(f"Error adding column (might already exist): {e}")

if __name__ == "__main__":
    update_schema()
