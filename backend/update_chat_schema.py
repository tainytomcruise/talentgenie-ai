
from app_modular import app
from models import db
from sqlalchemy import text

def update_schema():
    with app.app_context():
        try:
            # Add type column
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE chat_messages ADD COLUMN type VARCHAR(50) DEFAULT 'text'"))
                conn.execute(text("ALTER TABLE chat_messages ADD COLUMN data TEXT"))
                conn.commit()
            print("Schema updated successfully")
        except Exception as e:
            print(f"Error updating schema: {e}")

if __name__ == "__main__":
    update_schema()
