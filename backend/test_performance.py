import requests
import json
from flask_jwt_extended import create_access_token
from app_modular import app

BASE_URL = 'http://localhost:5001/api'

def get_token(user_id, role='Employee'):
    with app.app_context():
        token = create_access_token(identity=str(user_id), additional_claims={'role': role})
        return token

def test_performance():
    # Use emp_id 62 (User 167)
    emp_id = 62
    user_id = 167
    token = get_token(user_id)
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    print(f"--- Testing Performance API for Emp {emp_id} ---")
    
    # 1. Add Score 80
    print("\n1. Adding Score 80...")
    payload1 = {
        'emp_id': emp_id,
        'score': 80,
        'type': 'Module',
        'comment': 'Completed Module 1'
    }
    resp1 = requests.post(f'{BASE_URL}/performance/log', json=payload1, headers=headers)
    print(f"Status: {resp1.status_code}")
    print(f"Response: {resp1.text}")
    
    # 2. Add Score 100
    print("\n2. Adding Score 100...")
    payload2 = {
        'emp_id': emp_id,
        'score': 100,
        'type': 'HR_Manual',
        'comment': 'Excellent presentation'
    }
    resp2 = requests.post(f'{BASE_URL}/performance/log', json=payload2, headers=headers)
    print(f"Status: {resp2.status_code}")
    print(f"Response: {resp2.text}")
    
    # 3. Get Summary (Should be 90)
    print("\n3. Fetching Summary...")
    resp3 = requests.get(f'{BASE_URL}/performance/summary/{emp_id}', headers=headers)
    print(f"Status: {resp3.status_code}")
    print(f"Response: {resp3.text}")
    
    data = resp3.json()
    if data.get('average_score') == 90.0:
        print("\nSUCCESS: Average score is 90.0")
    else:
        print(f"\nFAILURE: Expected 90.0, got {data.get('average_score')}")

if __name__ == '__main__':
    test_performance()
