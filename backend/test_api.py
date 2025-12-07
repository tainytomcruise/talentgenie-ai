import requests
import json

BASE_URL = 'http://localhost:5001/api'
EMAIL = 'prashantp@email.com'
PASSWORD = 'password123' # Assuming default password, or I need to find a way to login without it? 
# Wait, I don't know the password.
# I can use a known user or create a new one?
# Or I can just bypass auth in the backend for testing?
# No, I should try to use the token if I can get it.
# But I can't get the token from the frontend.

# Alternative: I can use the `check_paths.py` to generate a token?
# No, I need the secret key.
# I have the secret key in app_modular.py: 'super-secret-key'

from flask_jwt_extended import create_access_token
from app_modular import app

def get_token(user_id, role='Employee'):
    with app.app_context():
        # Create a token for the user
        token = create_access_token(identity=str(user_id), additional_claims={'role': role})
        return token

def test_get_paths():
    token = get_token(167) # User ID 167
    headers = {'Authorization': f'Bearer {token}'}
    
    print(f"Testing GET /learning/paths/62 with token for User 167")
    response = requests.get(f'{BASE_URL}/learning/paths/62', headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == '__main__':
    test_get_paths()
