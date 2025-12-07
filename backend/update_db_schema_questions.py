from app_modular import app
from models import db
from sqlalchemy import text

with app.app_context():
    try:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE applicants ADD COLUMN interview_questions TEXT"))
            conn.commit()
        print("Successfully added interview_questions column to applicants table")
    except Exception as e:
        print(f"Error (column might already exist): {e}")
