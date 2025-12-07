
from app_modular import app
from models import User, db
from sqlalchemy import func

def debug_login():
    with app.app_context():
        try:
            print("Attempting to query user...")
            # Simulate the query from LoginResource
            email = "john.doe@example.com" # Replace with a known user email if needed, or just query first
            user = User.query.first()
            
            if user:
                print(f"User found: {user.email}")
                print("Attempting to convert to dict...")
                user_dict = user.to_dict()
                print("User dict created successfully:")
                print(user_dict)
            else:
                print("No users found in DB.")
                
        except Exception as e:
            print("\n!!! ERROR OCCURRED !!!")
            print(str(e))
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_login()
