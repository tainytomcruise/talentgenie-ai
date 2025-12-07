import requests
import json
from flask_jwt_extended import create_access_token
from app_modular import app, db
from models import EmployeeLearningPath, EmployeeTraining, EmployeePerformance, Training

BASE_URL = 'http://localhost:5001/api'

def get_token(user_id, role='Employee'):
    with app.app_context():
        token = create_access_token(identity=str(user_id), additional_claims={'role': role})
        return token

def test_auto_logging():
    # Use emp_id 62 (User 167)
    emp_id = 62
    user_id = 167
    token = get_token(user_id)
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    print(f"--- Testing Auto-Logging for Emp {emp_id} ---")
    
    # 1. Create a dummy learning path if not exists
    with app.app_context():
        # Ensure dummy training exists
        if not Training.query.get(1):
            db.session.add(Training(id=1, title="Test Training", duration_hours=1))
            db.session.commit()

        path = EmployeeLearningPath.query.filter_by(emp_id=emp_id).first()
        if not path:
            print("Creating dummy learning path...")
            path = EmployeeLearningPath(emp_id=emp_id, current_role="Test", career_goal="Test", progress=1.0)
            path.set_path_data({'learning_path': {'modules': [{'title': 'Mod 1', 'completed': False}, {'title': 'Mod 2', 'completed': False}]}})
            db.session.add(path)
            db.session.commit()
        
        path_id = path.id
        current_progress = int(path.progress) if path.progress else 1
        print(f"Current Progress: {current_progress}")
        
    # 2. Complete Module matching progress
    # module_index should be current_progress - 1
    module_index = current_progress - 1
    print(f"\n1. Completing Module {module_index} (Progress {current_progress})...")
    
    payload1 = {
        'path_id': path_id,
        'module_index': module_index,
        'completed': True
    }
    resp1 = requests.patch(f'{BASE_URL}/learning/path/module', json=payload1, headers=headers)
    print(f"Status: {resp1.status_code}")
    
    # Verify log
    with app.app_context():
        log = EmployeePerformance.query.filter_by(emp_id=emp_id, type="Module Completion").order_by(EmployeePerformance.created_at.desc()).first()
        if log and log.score == 100:
            print("SUCCESS: Module completion logged correctly.")
        else:
            print("FAILURE: Module completion NOT logged.")

    # 3. Create dummy training
    with app.app_context():
        training = EmployeeTraining.query.filter_by(emp_id=emp_id, training_id=1).first()
        if not training:
            training = EmployeeTraining(emp_id=emp_id, training_id=1, status="In Progress")
            db.session.add(training)
            db.session.commit()
        training_id = training.id

    # 4. Complete Training -> Should log "Employee Training complete"
    print(f"\n2. Completing Training {training_id}...")
    payload2 = {
        'training_id': training_id,
        'status': 'Completed'
    }
    resp2 = requests.patch(f'{BASE_URL}/learning/training/status', json=payload2, headers=headers)
    print(f"Status: {resp2.status_code}")

    # Verify log
    with app.app_context():
        log = EmployeePerformance.query.filter_by(emp_id=emp_id, type="Employee Training complete").order_by(EmployeePerformance.created_at.desc()).first()
        if log and log.score == 100:
            print("SUCCESS: Training completion logged correctly.")
        else:
            print("FAILURE: Training completion NOT logged.")

if __name__ == '__main__':
    test_auto_logging()
