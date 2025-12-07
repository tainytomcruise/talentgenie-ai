from app_modular import app
from models import db, User

with app.app_context():
    print("--- USERS (Specific) ---")
    users = User.query.filter(User.user_id.in_([161, 163])).all()
    for u in users:
        print(f"ID: {u.user_id}, Name: {u.name}, Email: {u.email}, Role: {u.role}")
