"""
Script to add HR user to database
Email: hr@gmail.com
Password: 1234
"""
from app_modular import app, db
from models import User

def add_hr_user():
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(email='hr@gmail.com').first()
        
        if existing_user:
            print(f"❌ User with email 'hr@gmail.com' already exists!")
            print(f"   User ID: {existing_user.user_id}")
            print(f"   Name: {existing_user.name}")
            print(f"   Role: {existing_user.role}")
            return
        
        # Create new HR user
        hr_user = User(
            name='HR Manager',
            email='hr@gmail.com',
            role='hr'
        )
        hr_user.set_password('1234')
        
        db.session.add(hr_user)
        db.session.commit()
        
        print("✅ HR user created successfully!")
        print(f"   Email: hr@gmail.com")
        print(f"   Password: 1234")
        print(f"   Role: hr")
        print(f"   User ID: {hr_user.user_id}")

if __name__ == '__main__':
    add_hr_user()
