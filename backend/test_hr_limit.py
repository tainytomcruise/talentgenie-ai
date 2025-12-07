import requests
import datetime
import random
import string

BASE_URL = "http://127.0.0.1:5001/api"

def get_auth_token():
    # Register a random user
    rand_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    email = f"hr_{rand_suffix}@example.com"
    password = "password123"
    
    print(f"Registering user: {email}")
    reg_payload = {
        "email": email,
        "password": password,
        "fullname": "Test HR",
        "role": "HR"
    }
    try:
        requests.post(f"{BASE_URL}/auth/register", json=reg_payload)
    except:
        pass # Ignore if fails (maybe already exists)

    # Login
    print("Logging in...")
    login_payload = {
        "email": email,
        "password": password,
        "role": "HR"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
    if response.status_code == 200:
        return response.json().get('token')
    else:
        print(f"Login failed: {response.text}")
        return None

def test_hr_rating_limit():
    token = get_auth_token()
    if not token:
        print("Failed to get auth token. Exiting.")
        return
        
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\nTesting HR Rating Limit...")
    
    # 1. Log first rating
    print("\n1. Logging first rating...")
    payload1 = {
        "emp_id": 1,
        "score": 85,
        "type": "HR_Manual",
        "comment": "First rating"
    }
    try:
        response1 = requests.post(f"{BASE_URL}/performance/log", json=payload1, headers=headers)
        print(f"Response 1: {response1.status_code} - {response1.json()}")
    except Exception as e:
        print(f"Request failed: {e}")
        if 'response1' in locals():
            print(f"Raw response: {response1.text}")
        return

    # 2. Log second rating (should fail)
    print("\n2. Logging second rating (should fail)...")
    payload2 = {
        "emp_id": 1,
        "score": 90,
        "type": "HR_Manual",
        "comment": "Second rating"
    }
    try:
        response2 = requests.post(f"{BASE_URL}/performance/log", json=payload2, headers=headers)
        print(f"Response 2: {response2.status_code} - {response2.json()}")
        
        if response2.status_code == 400 and "already rated" in response2.json().get('error', ''):
            print("\nSUCCESS: Daily limit enforced correctly.")
        elif response2.status_code == 201:
             print("\nFAILURE: Second rating was allowed.")
        else:
            print(f"\nUNEXPECTED: {response2.status_code}")
            
    except Exception as e:
        print(f"Request failed: {e}")

    # 3. Check eligibility endpoint (should return False)
    print("\n3. Checking eligibility endpoint (should be False)...")
    try:
        response3 = requests.get(f"{BASE_URL}/performance/can-rate/1", headers=headers)
        print(f"Response 3: {response3.status_code} - {response3.json()}")
        
        if response3.status_code == 200 and response3.json().get('can_rate') is False:
             print("\nSUCCESS: Eligibility check returned False as expected.")
        else:
             print("\nFAILURE: Eligibility check returned True or failed.")
             
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_hr_rating_limit()
