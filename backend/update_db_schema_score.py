from app_modular import app, db
from sqlalchemy import text

with app.app_context():
    try:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE applicants ADD COLUMN score FLOAT DEFAULT 0.0"))
            conn.commit()
        print("Successfully added 'score' column to 'applicants' table.")
    except Exception as e:
        print(f"Error updating schema: {e}")
