
from app_modular import app
from models import User, Employee, LeaveRequest, db
from datetime import date

def debug_leave():
    with app.app_context():
        try:
            print("Finding an employee...")
            employee = Employee.query.first()
            if not employee:
                print("No employee found.")
                return

            print(f"Found employee: {employee.emp_id}")
            
            # Create a dummy leave request
            lr = LeaveRequest(
                emp_id=employee.emp_id,
                leave_type="Test",
                start_date=date.today(),
                end_date=date.today(),
                reason="Debug test"
            )
            
            db.session.add(lr)
            db.session.commit()
            print(f"Created LeaveRequest: {lr.leave_id}")
            
            # Try to access relationships
            print(f"Accessing lr.employee: {lr.employee}")
            if lr.employee:
                print(f"Accessing lr.employee.user: {lr.employee.user}")
            
            # Try to_dict
            print("Calling to_dict()...")
            data = lr.to_dict()
            print("to_dict success:")
            print(data)
            
            # Clean up
            db.session.delete(lr)
            db.session.commit()
            print("Cleaned up.")
            
        except Exception as e:
            print("\n!!! ERROR OCCURRED !!!")
            print(str(e))
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_leave()
