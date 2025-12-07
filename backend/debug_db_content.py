from app_modular import app
from models import User, Employee, EmployeeTraining, Training, db

with app.app_context():
    print("\n=== USERS ===")
    users = User.query.all()
    for u in users:
        print(f"ID: {u.user_id}, Name: {u.name}, Email: {u.email}, Role: {u.role}")

    print("\n=== EMPLOYEES ===")
    employees = Employee.query.all()
    for e in employees:
        print(f"Emp ID: {e.emp_id}, User ID: {e.user_id}, Name: {e.user.name}")

    print("\n=== TRAININGS ===")
    trainings = Training.query.all()
    for t in trainings:
        print(f"ID: {t.training_id}, Title: {t.title}")

    print("\n=== EMPLOYEE TRAININGS ===")
    emp_trainings = EmployeeTraining.query.all()
    for et in emp_trainings:
        print(f"ID: {et.id}, Emp ID: {et.emp_id}, Training ID: {et.training_id}, Status: {et.status}")
