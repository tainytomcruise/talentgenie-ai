from app_modular import app
from models import db, EmployeeLearningPath, Employee

with app.app_context():
    emp_id = 62
    print(f"Checking paths for emp_id: {emp_id}")
    paths = EmployeeLearningPath.query.filter_by(emp_id=emp_id).all()
    print(f"Found {len(paths)} paths for emp_id {emp_id}")
    
    all_paths = EmployeeLearningPath.query.all()
    print(f"Total paths in DB: {len(all_paths)}")
    emp = Employee.query.get(emp_id)
    if emp and emp.user:
        print(f"User Email: {emp.user.email}")
        print(f"User ID: {emp.user.user_id}")
    else:
        print("User not found for this employee")
