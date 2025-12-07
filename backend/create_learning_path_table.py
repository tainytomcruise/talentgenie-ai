from app_modular import app, db
from models import EmployeeLearningPath

with app.app_context():
    db.create_all()
    print("Database tables created (including EmployeeLearningPath if missing).")
