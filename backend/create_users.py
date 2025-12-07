"""
Create default users for testing
"""
from app_modular import app, db
from models import User

def create_default_users():
    with app.app_context():
        # Check if users already exist
        hr_user = User.query.filter_by(email='hr@company.com').first()
        emp_user = User.query.filter_by(email='employee@company.com').first()
        
        if not hr_user:
            hr_user = User(
                name='HR Manager',
                email='hr@company.com',
                role='hr'
            )
            hr_user.set_password('password123')
            db.session.add(hr_user)
            print("✓ Created HR user: hr@company.com")
        else:
            print("✓ HR user already exists")
        
        if not emp_user:
            emp_user = User(
                name='John Employee',
                email='employee@company.com',
                role='employee'
            )
            emp_user.set_password('password123')
            db.session.add(emp_user)
            print("✓ Created Employee user: employee@company.com")
        else:
            print("✓ Employee user already exists")
        
        db.session.commit()
        print("\n✅ Default users ready!")
        print("   HR: hr@company.com / password123")
        print("   Employee: employee@company.com / password123")

if __name__ == '__main__':
    create_default_users()
