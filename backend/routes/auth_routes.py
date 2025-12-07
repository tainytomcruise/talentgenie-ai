from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from models import User, Employee, db
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime


class LoginResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            email = data.get("email").lower() if data.get("email") else None
            password = data.get("password")
            role = data.get("role")  # 'hr' or 'employee'

            if not all([email, password, role]):
                return {"message": "All credentials (email, password, role) are required"}, 400

            # Find user by email first (case-insensitive)
            user = User.query.filter(func.lower(User.email) == email.lower()).first()
            if not user:
                return {"message": "User not found"}, 404

            # Check if role matches (case-insensitive)
            if user.role.lower() != role.lower():
                return {"message": f"Role mismatch. User is registered as {user.role}"}, 403

            if not check_password_hash(user.password_hash, password):
                return {"message": "Invalid credentials"}, 401
            
            # Only enforce is_active check for employees as per requirement
            if user.role.lower() == 'employee' and not user.is_active:
                return {"message": "Contact HR to activate your account"}, 403

            token = create_access_token(identity=str(user.user_id), additional_claims={"email": user.email,"role": user.role })


            return {
                "message": "Logged in successfully",
                "token": token,
                "user": user.to_dict()
            }, 200

        except SQLAlchemyError as e:
            return {"message": "Database error occurred", "error": str(e)}, 500
        except Exception as e:
            return {"message": "Unexpected error occurred", "error": str(e)}, 500


class RegisterResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            fullname = data.get("fullname")
            email = data.get("email").lower() if data.get("email") else None
            password = data.get("password")
            role = data.get("role", "employee")  # default to employee

            if not all([fullname, email, password]):
                return {"message": "All fields are required"}, 400

            user = User.query.filter(func.lower(User.email) == email.lower()).first()
            if user:
                return {"message": "User already exists"}, 409

            # Create user
            # Default is_active to False for employees, True for others (or as per requirement)
            is_active = False if role.lower() == 'employee' else True
            new_user = User(name=fullname, email=email, role=role, is_active=is_active)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.flush()  # Get user_id before commit

            # If role is employee, create Employee record
            if role.lower() == 'employee':
                from models import Employee
                new_employee = Employee(
                    user_id=new_user.user_id,
                    job_title=data.get("job_title", "Employee"),
                    dept_id=data.get("dept_id"),  # Optional department
                    hire_date=datetime.utcnow().date()
                )
                db.session.add(new_employee)

            db.session.commit()

            return {"message": "User registered successfully", "user": new_user.to_dict()}, 201

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"message": "Database error occurred", "error": str(e)}, 500
        except Exception as e:
            db.session.rollback()
            return {"message": "Unexpected error occurred", "error": str(e)}, 500


class CurrentUserResource(Resource):
    @jwt_required()
    def get(self):
        try:
            user_id = int(get_jwt_identity())  # identity is a string
            user = User.query.get(user_id)


            if not user:
                return {"message": "User not found"}, 404

            return {"user": user.to_dict()}, 200

        except SQLAlchemyError as e:
            return {"message": "Database error occurred", "error": str(e)}, 500
        except Exception as e:
            return {"message": "Unexpected error occurred", "error": str(e)}, 500
