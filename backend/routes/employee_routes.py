from flask import request
import json
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Employee, User, Department, db, EmployeeBirthday, EmployeePerformance
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func

class EmployeeListResource(Resource):
    @jwt_required()
    def get(self):
        try:
            # Fetch all employees with their associated user and department data
            employees = Employee.query.join(User).outerjoin(Department).all()
            
            employee_list = []
            for emp in employees:
                emp_data = emp.to_dict()
                # Add user-specific fields that might not be in to_dict() or ensure they are present
                emp_data['name'] = emp.user.name
                emp_data['email'] = emp.user.email
                emp_data['department'] = emp.department.name if emp.department else 'Unassigned'
                
                # Add leave stats (mock or calculated)
                # Calculate total approved leave days
                approved_leaves = [req.number_of_days or 0 for req in emp.leave_requests if req.status == 'Approved']
                emp_data['leaves_taken'] = sum(approved_leaves)
                
                # Calculate aggregated performance score
                performance_records = EmployeePerformance.query.filter_by(emp_id=emp.emp_id).all()
                if performance_records:
                    total_score = sum(record.score for record in performance_records)
                    emp_data['performance_score'] = round(total_score, 1)
                else:
                    emp_data['performance_score'] = None
                
                employee_list.append(emp_data)

            return {"employees": employee_list}, 200

        except Exception as e:
            return {"message": "Unexpected error occurred", "error": str(e)}, 500


class PendingEmployeesResource(Resource):
    @jwt_required()
    def get(self):
        try:
            # Fetch users with role 'Employee' (case-insensitive) and is_active=False
            pending_users = User.query.filter(func.lower(User.role) == 'employee', User.is_active == False).all()
            
            pending_list = []
            for user in pending_users:
                pending_list.append({
                    "user_id": user.user_id,
                    "name": user.name,
                    "email": user.email,
                    "created_at": user.created_at.isoformat() if user.created_at else None
                })
            
            return {"pending_employees": pending_list}, 200
        except Exception as e:
            return {"message": "Error fetching pending employees", "error": str(e)}, 500


class ApproveEmployeeResource(Resource):
    @jwt_required()
    def post(self):
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            
            if not user_id:
                return {"message": "User ID is required"}, 400
            
            user = User.query.get(user_id)
            if not user:
                return {"message": "User not found"}, 404
            
            # Update User status
            user.is_active = True
            
            # Update Employee details
            employee = Employee.query.filter_by(user_id=user_id).first()
            if not employee:
                # Create new Employee record if it doesn't exist
                from datetime import datetime
                employee = Employee(
                    user_id=user_id,
                    hire_date=datetime.utcnow().date()
                )
                db.session.add(employee)
            
            # Update Employee details
            employee.dept_id = data.get('dept_id')
            employee.job_title = data.get('job_title')
            employee.salary = data.get('salary')
            employee.manager_id = data.get('manager_id')
            
            skills_data = data.get('skills', [])
            if isinstance(skills_data, list):
                employee.skills = json.dumps(skills_data)
            else:
                employee.skills = skills_data
            
            db.session.commit()
            
            return {"message": f"Employee {user.name} approved and activated successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return {"message": "Error approving employee", "error": str(e)}, 500


class UpdatePersonalDetailsResource(Resource):
    @jwt_required()
    def get(self):
        try:
            current_user_id = get_jwt_identity()
            employee = Employee.query.filter_by(user_id=current_user_id).first()
            if not employee:
                return {"message": "Employee profile not found"}, 404
            
            # Check for birthday record
            birthday_record = EmployeeBirthday.query.filter_by(emp_id=employee.emp_id).first()
            
            return {
                "dob": birthday_record.birth_date.isoformat() if birthday_record else None,
                "skills": employee.get_skills() or []
            }, 200
        except Exception as e:
            print(f"DEBUG: Error in GET personal-details: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"message": "Error fetching personal details", "error": str(e)}, 500

    @jwt_required()
    def put(self):
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json()
            
            employee = Employee.query.filter_by(user_id=current_user_id).first()
            if not employee:
                return {"message": "Employee profile not found"}, 404
            
            # Handle Skills Update
            if 'skills' in data:
                skills_list = data.get('skills')
                if isinstance(skills_list, list):
                    employee.set_skills(skills_list)
                    db.session.commit()
                    return {"message": "Skills updated successfully", "skills": skills_list}, 200
                else:
                    return {"message": "Skills must be a list"}, 400

            # Check if DOB is already set in EmployeeBirthday table
            existing_record = EmployeeBirthday.query.filter_by(emp_id=employee.emp_id).first()
            if existing_record:
                return {"message": "Date of Birth cannot be modified once set. Contact HR for changes."}, 403
            
            dob_str = data.get('dob') # Expected format: YYYY-MM-DD
            if dob_str:
                from datetime import datetime
                try:
                    dob_date = datetime.strptime(dob_str, '%Y-%m-%d').date()
                    
                    # Create new record
                    new_birthday = EmployeeBirthday(
                        emp_id=employee.emp_id,
                        birth_date=dob_date
                    )
                    db.session.add(new_birthday)
                    db.session.commit()
                    
                    return {"message": "Personal details updated successfully"}, 200
                except ValueError:
                    return {"message": "Invalid date format. Use YYYY-MM-DD"}, 400
            
            return {"message": "No changes made"}, 200
        except Exception as e:
            print(f"DEBUG: Error in PUT personal-details: {str(e)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return {"message": "Error updating personal details", "error": str(e)}, 500
