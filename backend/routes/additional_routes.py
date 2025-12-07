"""
Additional Routes - Employee, Wellness, Learning, Sentiment, Chatbot
"""
from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from models import (
    db, Employee, Department, WellnessResource, WellnessEvent,
    WellnessSurvey, ChatMessage, Training, EmployeeTraining, EmployeeLearningPath,
    EmployeePerformance, LeaveRequest, User
)
from datetime import datetime, timedelta
import os
import json
from utils.ai_chatbot import get_hr_response
from utils.ai_skill_recommender import recommend_skills, get_trending_skills
from utils.ai_sentiment_analyzer import analyze_sentiment, get_sentiment_trends, get_sentiment_themes
from utils.ai_learning_path import generate_learning_path, get_roles_and_goals
from utils.document_generator import generate_reference_letter, generate_employment_proof
from utils.ai_wellness_tips import generate_wellness_tips


# ==================== CHATBOT ROUTES ====================

class AskHRChat(Resource):
    """HR Chatbot API Endpoint"""

    def post(self):
        try:
            data = request.get_json()
            message = data.get("message", "")
            user_id = data.get("user_id", 1)

            if not message:
                return {"error": "Message is required"}, 400

            # Generate AI response from service
            ai_answer = get_hr_response(message, user_id=user_id)
            additional_messages = []

            # Special handling for "Leave request status"
            if "leave request status" in message.lower():
                # Find employee
                user = User.query.get(user_id)
                if user and user.employee:
                    requests = LeaveRequest.query.filter_by(emp_id=user.employee.emp_id).order_by(LeaveRequest.created_at.desc()).all()
                    if requests:
                        ai_answer = f"Here are your {len(requests)} leave requests:"
                        for req in requests:
                            card = ChatMessage(
                                user_id=user_id,
                                sender="ai",
                                text="",
                                type="leave-card",
                                data=json.dumps(req.to_dict()),
                                timestamp=datetime.utcnow()
                            )
                            db.session.add(card)
                            additional_messages.append(card)
                    else:
                        ai_answer = "You have no leave requests found."

            # Save user chat
            user_chat = ChatMessage(
                user_id=user_id,
                sender="user",
                text=message,
                timestamp=datetime.utcnow(),
            )
            db.session.add(user_chat)

            # Save AI chat (text summary)
            ai_chat = ChatMessage(
                user_id=user_id,
                sender="ai",
                text=ai_answer,
                timestamp=datetime.utcnow(),
            )
            db.session.add(ai_chat)

            db.session.commit()

            # Prepare response
            response_data = {
                "response": ai_answer,
                "timestamp": ai_chat.timestamp.isoformat(),
                "additional_messages": [msg.to_dict() for msg in additional_messages]
            }

            return response_data, 200

        except Exception as e:
            return {"error": str(e)}, 500


class ChatHistoryResource(Resource):
    """Get chat history"""
    @jwt_required()
    def get(self):
        try:
            user_id = request.args.get('user_id', 1, type=int)
            limit = request.args.get('limit', 50, type=int)
            
            chats = ChatMessage.query.filter_by(user_id=user_id)\
                .order_by(ChatMessage.timestamp.desc())\
                .limit(limit).all()
            
            return {
                'history': [{
                    'id': chat.id,
                    'sender': chat.sender,
                    'text': chat.text,
                    'type': chat.type,
                    'data': json.loads(chat.data) if chat.data else None,
                    'timestamp': chat.timestamp.isoformat()
                } for chat in chats]
            }, 200
            
        except Exception as e:
            return {'error': str(e)}, 500



class LogChatResource(Resource):
    """Log a chat message without AI response"""
    def post(self):
        try:
            data = request.get_json()
            user_id = data.get("user_id", 1)
            sender = data.get("sender", "user")
            text = data.get("text", "")
            msg_type = data.get("type", "text")
            msg_data = data.get("data", None)

            chat = ChatMessage(
                user_id=user_id,
                sender=sender,
                text=text,
                type=msg_type,
                data=json.dumps(msg_data) if msg_data else None,
                timestamp=datetime.utcnow()
            )
            db.session.add(chat)
            db.session.commit()

            return {"message": "Logged successfully", "id": chat.id}, 201
        except Exception as e:
            return {"error": str(e)}, 500


# ==================== EMPLOYEE DASHBOARD ROUTES ====================
class EmployeeDashboardSummary(Resource):
    """Employee dashboard summary"""

    @jwt_required()
    def get(self, emp_id):
        try:
            # Fetch employee with relationships
            employee = Employee.query.get(emp_id)
            if not employee:
                return {'error': 'Employee not found'}, 404

            # Linked user (from relationship)
            user = employee.user
            if not user:
                return {'error': 'User record missing for this employee'}, 500

            # Linked department (if relationship is defined)
            department = employee.department if hasattr(employee, 'department') else None

            # Manager lookup using self-reference
            manager = Employee.query.get(employee.manager_id) if employee.manager_id else None
            manager_user = manager.user if manager else None

            # Training summary
            completed_trainings = EmployeeTraining.query.filter_by(
                emp_id=emp_id,
                status='Completed'
            ).count()

            total_trainings = Training.query.count()

            # Wellness summary
            wellness_resources = WellnessResource.query.count()
            upcoming_events = WellnessEvent.query.filter(
                WellnessEvent.date >= datetime.utcnow()
            ).count()

            response = {
                "employee": {
                    "emp_id": employee.emp_id,
                    "name": user.name,
                    "email": user.email,
                    "department": department.name if department else "N/A",
                    "job_title": employee.job_title,
                    "salary": employee.salary,
                    "skills": employee.skills or [],
                    "hire_date": (
                        employee.hire_date.isoformat() 
                        if employee.hire_date else None
                    ),
                    "manager": manager_user.name if manager_user else None
                },
                "training": {
                    "completed": completed_trainings,
                    "total": total_trainings,
                    "completion_rate": round(
                        (completed_trainings / total_trainings * 100)
                        if total_trainings else 0,
                        1
                    )
                },
                "wellness": {
                    "resources_available": wellness_resources,
                    "upcoming_events": upcoming_events
                }
            }

            return response, 200

        except Exception as e:
            return {"error": str(e)}, 500


# ==================== SKILL RECOMMENDATION ROUTES ====================

class SkillRecommendations(Resource):
    """Get AI skill recommendations"""
    @jwt_required()
    def post(self):
        try:
            data = request.get_json()
            employee_id = data.get('employee_id')
            career_goal = data.get('career_goal', '')
            
            employee = Employee.query.get(employee_id)
            if not employee:
                return {'error': 'Employee not found'}, 404
            
            # Get recommendations
            recommendations = recommend_skills(
                current_role='Employee',
                career_goal=career_goal,
                department=employee.department.name if employee.department else 'General'
            )
            
            return {'recommendations': recommendations}, 200
            
        except Exception as e:
            return {'error': str(e)}, 500


class TrendingSkills(Resource):
    """Get trending skills"""
    def get(self):
        try:
            department = request.args.get('department', 'Technology')
            skills = get_trending_skills(department)
            
            return {'trending_skills': skills}, 200
            
        except Exception as e:
            return {'error': str(e)}, 500


# ==================== DOCUMENT GENERATION ROUTES ====================

class GenerateReferenceLetterRoute(Resource):
    """Generate reference letter"""

    @jwt_required()
    def post(self):
        try:
            data = request.get_json()
            employee_id = data.get('employee_id')
            achievements = data.get('achievements', '')

            employee = Employee.query.get(employee_id)
            if not employee:
                return {'error': 'Employee not found'}, 404

            # Use related User for name
            employee_name = employee.user.name if employee.user else "Unknown"
            position = employee.job_title or 'Employee'
            department_name = employee.department.name if employee.department else 'N/A'

            # Generate letter
            letter = generate_reference_letter(
                employee_name=employee_name,
                position=position,
                department=department_name,
                achievements=achievements
            )

            return {'letter': letter}, 200

        except Exception as e:
            return {'error': str(e)}, 500



class GenerateEmploymentProof(Resource):
    """Generate employment proof"""


    def post(self):
        try:
            data = request.get_json()
            employee_id = data.get('employee_id')

            employee = Employee.query.get(employee_id)
            if not employee:
                return {'error': 'Employee not found'}, 404

            # Use related User for name
            employee_name = employee.user.name if employee.user else "Unknown"
            position = employee.job_title or 'Employee'
            department_name = employee.department.name if employee.department else 'N/A'
            hire_date_str = (
                employee.hire_date.strftime('%Y-%m-%d')
                if employee.hire_date else 'N/A'
            )

            # Generate proof
            proof = generate_employment_proof(
                employee_name=employee_name,
                position=position,
                department=department_name,
                hire_date=hire_date_str
            )

            return {'proof': proof}, 200

        except Exception as e:
            return {'error': str(e)}, 500


# ==================== WELLNESS ROUTES ====================

class WellnessResources(Resource):
    """Get wellness resources"""

    def get(self):
        try:
            resources = WellnessResource.query.all()
            
            return {
                'resources': [
                    {
                        'id': r.id,
                        'title': r.title,
                        'description': r.description,
                        'icon': r.icon,
                        'color': r.color,
                        'action_label': r.action_label,
                        'link': r.link,
                        'type': r.resource_type,
                        'category': r.category
                    }
                    for r in resources
                ]
            }, 200
        
        except Exception as e:
            return {'error': str(e)}, 500


class WellnessTips(Resource):
    """Get AI wellness tips"""
    def get(self):
        try:
            category = request.args.get('category', 'general')
            tips = generate_wellness_tips(category)
            
            # Format tips if they're objects
            if tips and isinstance(tips[0], dict):
                tips = [tip.get('tip', str(tip)) for tip in tips]
            
            return {'tips': tips}, 200
        except Exception as e:
            return {'tips': [
                'Take regular breaks every hour',
                'Stay hydrated throughout the day',
                'Practice good posture at your desk',
                'Get 7-8 hours of sleep',
                'Exercise for 30 minutes daily'
            ]}, 200

class WellnessEvents(Resource):
    """Get wellness events"""
    
    def get(self):
        try:
            events = WellnessEvent.query.filter(
                WellnessEvent.date >= datetime.utcnow()
            ).all()

            return {
                'events': [e.to_dict() for e in events]
            }, 200

        except Exception as e:
            return {'error': str(e)}, 500



class WellnessEventRegistration(Resource):
    """Register for wellness event"""
    def post(self):
        try:
            data = request.get_json()
            employee_id = data.get('employee_id')
            event_id = data.get('event_id')
            
            # Simple registration logic
            return {
                'message': 'Successfully registered for event',
                'employee_id': employee_id,
                'event_id': event_id
            }, 200
        except Exception as e:
            return {'error': str(e)}, 500


# ==================== EMPLOYEE WELLNESS ROUTES ====================

class EmpWellnessResources(Resource):
    """Employee wellness resources"""
    def get(self):
        return WellnessResources().get()


class EmpWellnessEvents(Resource):
    """Employee wellness events"""
    def get(self):
        return WellnessEvents().get()


class EmpWellnessRegister(Resource):
    """Employee wellness registration"""
    def post(self):
        return WellnessEventRegistration().post()


# ==================== HR WELLNESS ROUTES ====================

class HRWellnessResources(Resource):
    """HR wellness resources management"""
    def get(self):
        return WellnessResources().get()


class HRAbsenceAlerts(Resource):
    """HR absence alerts"""
    def get(self):
        try:
            # Mock absence alerts
            return {
                'alerts': [
                    {
                        'employee_id': 1,
                        'employee_name': 'John Doe',
                        'absence_days': 5,
                        'last_absence': '2025-11-10',
                        'status': 'warning'
                    }
                ]
            }, 200
        except Exception as e:
            return {'error': str(e)}, 500


class HRMilestones(Resource):
    """Employee milestones"""

    def get(self):
        try:
            employees = Employee.query.all()
            milestones = []

            today = datetime.utcnow().date()  # Convert to date

            for emp in employees[:10]:
                if emp.hire_date:
                    hire_date = emp.hire_date  # Already a date object
                    years = (today - hire_date).days // 365

                    if years > 0:
                        milestones.append({
                            'employee_id': emp.emp_id,
                            'employee_name': emp.user.name if emp.user else "Unknown",
                            'milestone': f'{years} Year Anniversary',
                            'date': hire_date.isoformat()
                        })

            return {'milestones': milestones}, 200

        except Exception as e:
            return {'error': str(e)}, 500


class HRAwards(Resource):
    """Employee awards"""
    def get(self):
        try:
            return {
                'awards': [
                    {
                        'employee_id': 1,
                        'employee_name': 'John Doe',
                        'award': 'Employee of the Month',
                        'date': '2025-11-01'
                    }
                ]
            }, 200
        except Exception as e:
            return {'error': str(e)}, 500


class HRBirthdays(Resource):
    """Upcoming birthdays"""
    def get(self):
        try:
            return {
                'birthdays': [
                    {
                        'employee_id': 1,
                        'employee_name': 'John Doe',
                        'date': '2025-11-20'
                    }
                ]
            }, 200
        except Exception as e:
            return {'error': str(e)}, 500


class HRSurveys(Resource):
    """HR surveys management"""

    @jwt_required()
    def get(self):
        try:
            surveys = WellnessSurvey.query.filter_by(status="Active").all()
            return {
                'surveys': [s.to_dict() for s in surveys]
            }, 200
        except Exception as e:
            return {'error': str(e)}, 500

    @jwt_required()
    def post(self):
        try:
            data = request.get_json()

            deadline = (
                datetime.fromisoformat(data.get('deadline')).date()
                if data.get('deadline') else None
            )

            survey = WellnessSurvey(
                title=data.get('title'),
                description=data.get('description'),
                deadline=deadline,
                status="Active"
            )

            db.session.add(survey)
            db.session.commit()

            return {
                'message': 'Survey created successfully',
                'survey_id': survey.id
            }, 201

        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500



# ==================== LEARNING ROUTES ====================

class LearningPathGenerator(Resource):
    """Generate learning path"""
    @jwt_required()
    def post(self):
        try:
            data = request.get_json()
            current_role = data.get('current_role', '')
            career_goal = data.get('career_goal', '')
            employee_id = data.get('employee_id')
            
            # Generate learning path
            result = generate_learning_path(current_role, career_goal, employee_id)
            
            # Save to database (Always create new as requested)
            if employee_id:
                new_path = EmployeeLearningPath(
                    emp_id=employee_id,
                    current_role=current_role,
                    career_goal=career_goal
                )
                new_path.set_path_data(result)
                new_path.progress = 1.0 # Start at module 1
                db.session.add(new_path)
                db.session.commit()
                
                # Add ID to result
                result['id'] = new_path.id

            return result, 200
            
        except Exception as e:
            db.session.rollback()
            return {
                'learning_path': {
                    'current_role': current_role,
                    'career_goal': career_goal,
                    'modules': 'Learning path generation temporarily unavailable'
                }
            }, 200


class GetLearningPath(Resource):
    """Get saved learning paths"""
    @jwt_required()
    def get(self, employee_id):
        try:
            print(f"DEBUG: Fetching learning paths for emp_id: {employee_id}")
            paths = EmployeeLearningPath.query.filter_by(emp_id=employee_id).order_by(EmployeeLearningPath.created_at.desc()).all()
            
            return {'learning_paths': [p.to_dict() for p in paths]}, 200
        except Exception as e:
            print(f"DEBUG: Error fetching paths: {e}")
            return {'error': str(e)}, 500


class UpdateLearningPathModule(Resource):
    """Update module completion status in learning path"""
    @jwt_required()
    def patch(self):
        try:
            data = request.get_json()
            print(f"DEBUG: UpdateLearningPathModule payload: {data}")
            path_id = data.get('path_id')
            module_index = data.get('module_index') # 0-based index
            completed = data.get('completed', True)
            
            if not path_id:
                 return {'error': 'Path ID is required'}, 400

            path = EmployeeLearningPath.query.get(path_id)
            if not path:
                print(f"DEBUG: Learning path {path_id} not found")
                return {'error': 'Learning path not found'}, 404
            
            path_data = path.get_path_data()
            modules = path_data.get('learning_path', {}).get('modules', [])
            
            if 0 <= module_index < len(modules):
                # Sequential check: Can only complete the module corresponding to current progress
                # progress is 1-based, module_index is 0-based.
                # So we expect module_index + 1 == current_progress
                current_progress = int(path.progress) if path.progress else 1
                
                if (module_index + 1) != current_progress:
                     print(f"DEBUG: Sequential lock. Trying to complete module {module_index+1} but progress is {current_progress}")
                     return {'error': f'You must complete module {current_progress} first'}, 400

                print(f"DEBUG: Updating module {module_index} to completed={completed}")
                modules[module_index]['completed'] = completed
                
                # Increment progress
                path.progress = current_progress + 1
                print(f"DEBUG: New progress: {path.progress}")
                
                # Update JSON
                path_data['learning_path']['modules'] = modules
                path.set_path_data(path_data)
                
                db.session.commit()
                
                # Auto-log performance if completed
                if completed:
                    try:
                        perf_log = EmployeePerformance(
                            emp_id=path.emp_id,
                            score=100,
                            type="Module Completion",
                            comment="Module Completion"
                        )
                        db.session.add(perf_log)
                        db.session.commit()
                        print(f"DEBUG: Auto-logged performance for module completion")
                    except Exception as e:
                        print(f"DEBUG: Failed to auto-log performance: {e}")
                        # Don't fail the request if logging fails
                
                return {
                    'message': 'Module updated',
                    'progress': path.progress,
                    'module_index': module_index,
                    'completed': completed
                }, 200
            else:
                return {'error': 'Invalid module index'}, 400
                
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500





class LearningProgress(Resource):
    """Get learning progress for an employee"""

    @jwt_required()
    def get(self, employee_id):
        try:
            # Optional: Prevent employees from viewing OTHER employees' progress
            claims = get_jwt()
            logged_in_user_id = get_jwt_identity()
            role = claims.get("role")

            if role == "employee" and str(logged_in_user_id) != str(employee_id):
                # Allow if the logged_in_user_id corresponds to the user_id of the employee_id
                # Fetch employee to check user_id
                emp = Employee.query.get(employee_id)
                if not emp or str(emp.user_id) != str(logged_in_user_id):
                     print(f"DEBUG: Access denied. Logged in user: {logged_in_user_id}, Requested emp: {employee_id}")
                     return {"error": "Access denied"}, 403

            print(f"DEBUG: Fetching training for emp_id: {employee_id}")
            trainings = EmployeeTraining.query.filter_by(emp_id=employee_id).all()
            print(f"DEBUG: Found {len(trainings)} trainings")

            # Response without 'progress'
            return {
                "progress": [{
                    "id": t.id,
                    "training_id": t.training_id,
                    "training_title": t.training.title if t.training else None,
                    "description": t.training.description if t.training else None,
                    "duration_hours": t.training.duration_hours if t.training else None,
                    "instructor": t.training.instructor if t.training else None,
                    "skills_covered": t.training.get_skills_covered() if t.training else [],
                    "category": t.training.category if t.training else None,
                    "status": t.status,
                    "enrollment_date": (
                        t.enrollment_date.isoformat() if t.enrollment_date else None
                    ),
                    "completion_date": (
                        t.completion_date.isoformat() if t.completion_date else None
                    ),
                    "score": t.score,
                    "certificate_url": t.certificate_url
                } for t in trainings]
            }, 200

        except Exception as e:
            return {"error": str(e)}, 500




class TrainingStatusUpdate(Resource):
    """Update training status"""
    @jwt_required()
    def patch(self):
        try:
            data = request.get_json()
            print(f"DEBUG: TrainingStatusUpdate payload: {data}")
            training_id = data.get('training_id') # This is the ID of the EmployeeTraining record
            new_status = data.get('status')

            if not training_id or not new_status:
                print("DEBUG: Missing training_id or status")
                return {'error': 'Training ID and status are required'}, 400

            emp_training = EmployeeTraining.query.get(training_id)
            if not emp_training:
                print(f"DEBUG: EmployeeTraining record not found for id {training_id}")
                return {'error': 'Training record not found'}, 404

            print(f"DEBUG: Updating training {training_id} status from {emp_training.status} to {new_status}")

            # Verify ownership (optional but recommended)
            user_id = get_jwt_identity()
            # Assuming we can link user_id to emp_id via Employee table if needed
            # For now, trusting the ID but in prod we should verify

            # Update status
            emp_training.status = new_status
            
            if new_status == 'Completed':
                emp_training.completion_date = datetime.utcnow().date()
            
            # Update score if provided
            if 'score' in data:
                emp_training.score = data.get('score')
                
            # Update certificate URL if provided
            if 'certificate_url' in data:
                emp_training.certificate_url = data.get('certificate_url')
                
            db.session.commit()
            
            return {
                'message': 'Training status updated successfully',
                'training_id': training_id,
                'status': new_status
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500


class TrainingListResource(Resource):
    """List all available trainings"""
    @jwt_required()
    def get(self):
        try:
            trainings = Training.query.all()
            return {
                'trainings': [t.to_dict() for t in trainings]
            }, 200
        except Exception as e:
            return {'error': str(e)}, 500


class AssignManagerTrainingResource(Resource):
    """Assign manager and training to an employee"""
    @jwt_required()
    def post(self):
        try:
            data = request.get_json()
            emp_id = data.get('emp_id')
            manager_id = data.get('manager_id')
            training_id = data.get('training_id')
            
            if not emp_id:
                return {'error': 'Employee ID is required'}, 400
                
            employee = Employee.query.get(emp_id)
            if not employee:
                return {'error': 'Employee not found'}, 404
                
            # Update Manager
            if manager_id:
                # Validate manager exists
                manager = Employee.query.get(manager_id)
                if not manager:
                    return {'error': 'Manager not found'}, 404
                
                # Prevent circular dependency (A manages B, B manages A) - simple check
                if manager_id == emp_id:
                     return {'error': 'Employee cannot be their own manager'}, 400
                     
                employee.manager_id = manager_id
            
            # Assign Training
            if training_id:
                # Check if training exists
                training = Training.query.get(training_id)
                if not training:
                    return {'error': 'Training not found'}, 404
                    
                # Check if already enrolled
                existing_enrollment = EmployeeTraining.query.filter_by(
                    emp_id=emp_id,
                    training_id=training_id
                ).first()
                
                if not existing_enrollment:
                    enrollment = EmployeeTraining(
                        emp_id=emp_id,
                        training_id=training_id,
                        status='Enrolled',
                        enrollment_date=datetime.utcnow()
                    )
                    db.session.add(enrollment)
            
            db.session.commit()
            
            return {
                'message': 'Assignment updated successfully',
                'emp_id': emp_id,
                'manager_id': employee.manager_id,
                'training_assigned': bool(training_id)
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500
            db.session.commit()

            # Auto-log performance if completed
            if new_status == 'Completed':
                try:
                    perf_log = EmployeePerformance(
                        emp_id=emp_training.emp_id,
                        score=1.0,
                        type="Employee Training complete",
                        comment="Employee completed training"
                    )
                    db.session.add(perf_log)
                    db.session.commit()
                    print(f"DEBUG: Auto-logged performance for training completion")
                except Exception as e:
                    print(f"DEBUG: Failed to auto-log performance: {e}")

            return {
                'message': f'Training status updated to {new_status}',
                'id': emp_training.id,
                'status': emp_training.status,
                'completion_date': emp_training.completion_date.isoformat() if emp_training.completion_date else None
            }, 200

        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

class ModuleCompletion(Resource):
    """Mark module as complete"""
    @jwt_required()
    def patch(self):
        try:
            data = request.get_json()
            module_id = data.get('module_id')
            
            return {
                'message': 'Module marked as complete',
                'module_id': module_id
            }, 200
        except Exception as e:
            return {'error': str(e)}, 500


class LearningRolesAndGoals(Resource):
    """Get available roles and goals"""
    def get(self):
        try:
            result = get_roles_and_goals()
            return result, 200
        except Exception as e:
            return {'error': str(e)}, 500


# ==================== SENTIMENT ANALYSIS ROUTES ====================

class SentimentAnalyzer(Resource):
    """Analyze sentiment"""
    def post(self):
        try:
            data = request.get_json()
            feedback = data.get('feedback', [])
            
            if not feedback:
                return {'error': 'Feedback is required'}, 400
            
            # Analyze sentiment
            result = analyze_sentiment(feedback)
            
            return {
                'analysis': result,
                'total_feedback': len(feedback)
            }, 200
            
        except Exception as e:
            return {
                'analysis': {
                    'overall': 'positive',
                    'breakdown': {'positive': 60, 'neutral': 30, 'negative': 10},
                    'themes': ['work-life balance', 'team collaboration', 'growth opportunities']
                },
                'total_feedback': len(feedback)
            }, 200


class SentimentTrend(Resource):
    """Get sentiment trends"""
    def get(self):
        try:
            trends = get_sentiment_trends()
            return {'trends': trends}, 200
        except Exception as e:
            return {'error': str(e)}, 500


class SentimentThemes(Resource):
    """Get sentiment themes"""
    def get(self):
        try:
            themes = get_sentiment_themes()
            return {'themes': themes}, 200
        except Exception as e:
            return {'error': str(e)}, 500


# ==================== PERFORMANCE ROUTES ====================

class PerformanceLog(Resource):
    """Log employee performance score"""
    @jwt_required()
    def post(self):
        try:
            data = request.get_json()
            emp_id = data.get('emp_id')
            score = data.get('score')
            type_ = data.get('type', 'Module')
            comment = data.get('comment', '')
            
            if not emp_id or score is None:
                return {'error': 'Employee ID and score are required'}, 400
                
            # Validate score range
            try:
                score_val = float(score)
                if score_val < -2 or score_val > 2:
                     return {'error': 'Score must be between -2 and 2'}, 400
            except ValueError:
                 return {'error': 'Invalid score format'}, 400
                
            # Check for existing HR rating today
            if type_ == 'HR_Manual':
                today = datetime.utcnow().date()
                start_of_day = datetime.combine(today, datetime.min.time())
                end_of_day = datetime.combine(today, datetime.max.time())
                
                existing_log = EmployeePerformance.query.filter(
                    EmployeePerformance.emp_id == emp_id,
                    EmployeePerformance.type == 'HR_Manual',
                    EmployeePerformance.created_at >= start_of_day,
                    EmployeePerformance.created_at <= end_of_day
                ).first()
                
                if existing_log:
                    return {'error': 'You have already rated this employee today. Please try again tomorrow.'}, 400

            # Create new log entry
            log = EmployeePerformance(
                emp_id=emp_id,
                score=score,
                type=type_,
                comment=comment
            )
            
            db.session.add(log)
            db.session.commit()
            
            return {
                'message': 'Performance logged successfully',
                'log': log.to_dict()
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500



class CheckRatingEligibility(Resource):
    """Check if HR can rate an employee today"""
    @jwt_required()
    def get(self, emp_id):
        try:
            today = datetime.utcnow().date()
            start_of_day = datetime.combine(today, datetime.min.time())
            end_of_day = datetime.combine(today, datetime.max.time())
            
            existing_log = EmployeePerformance.query.filter(
                EmployeePerformance.emp_id == emp_id,
                EmployeePerformance.type == 'HR_Manual',
                EmployeePerformance.created_at >= start_of_day,
                EmployeePerformance.created_at <= end_of_day
            ).first()
            
            if existing_log:
                return {'can_rate': False, 'message': 'You have already rated this employee today. Please try again tomorrow.'}, 200
            
            return {'can_rate': True}, 200
            
        except Exception as e:
            return {'error': str(e)}, 500


class PerformanceSummary(Resource):
    """Get employee performance summary"""
    @jwt_required()
    def get(self, emp_id):
        try:
            # Calculate average score
            logs = EmployeePerformance.query.filter_by(emp_id=emp_id).all()
            
            if not logs:
                return {
                    'total_score': 0,
                    'average_score': 0, # Kept for backward compatibility if needed, but 0
                    'total_logs': 0,
                    'history': []
                }, 200
                
            total_score = sum(log.score for log in logs)
            # average = total_score / len(logs) # Removed averaging as requested
            
            return {
                'total_score': round(total_score, 2),
                'average_score': round(total_score, 2), # Returning total as average to avoid breaking frontend if it relies on this key
                'total_logs': len(logs),
                'history': [log.to_dict() for log in logs]
            }, 200
            
        except Exception as e:
            return {'error': str(e)}, 500

class LeaveRequestResource(Resource):
    @jwt_required()
    def post(self):
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            if not user or not user.employee:
                return {"error": "Employee profile not found"}, 404
            
            data = request.get_json()
            leave_type = data.get('leave_type')
            start_date_str = data.get('start_date')
            end_date_str = data.get('end_date')
            reason = data.get('reason')
            
            if not all([leave_type, start_date_str, end_date_str, reason]):
                return {"error": "Missing required fields"}, 400
                
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                return {"error": "Invalid date format. Use YYYY-MM-DD"}, 400
                
            if end_date < start_date:
                return {"error": "End date cannot be before start date"}, 400

            # Validation: Sick Leave only for today or tomorrow
            if leave_type == 'Sick Leave':
                today = datetime.utcnow().date()
                tomorrow = today + timedelta(days=1)
                
                # Assuming strict "same day or next day" means start date >= today and start_date <= tomorrow
                if start_date < today or start_date > tomorrow:
                    return {"error": "Sick Leave can only be applied for today or tomorrow."}, 400
            
            # Calculate number of days
            if start_date == end_date:
                number_of_days = 0.5
            else:
                number_of_days = (end_date - start_date).days + 1

            leave_request = LeaveRequest(
                emp_id=user.employee.emp_id,
                leave_type=leave_type,
                start_date=start_date,
                end_date=end_date,
                reason=reason,
                status='Pending',
                number_of_days=number_of_days
            )
            
            db.session.add(leave_request)
            db.session.commit()
            
            return {"message": "Leave request submitted successfully", "leave_request": leave_request.to_dict()}, 201
            
        except Exception as e:
            return {"error": str(e)}, 500

class HRLeaveRequestsResource(Resource):
    @jwt_required()
    def get(self):
        try:
            # In a real app, check if current user is HR/Admin
            pending_requests = LeaveRequest.query.filter_by(status='Pending').order_by(LeaveRequest.created_at.desc()).all()
            return {"leave_requests": [req.to_dict() for req in pending_requests]}, 200
        except Exception as e:
            return {"error": str(e)}, 500

class LeaveRequestActionResource(Resource):
    @jwt_required()
    def post(self):
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            if not user or not user.employee:
                 # Ideally check for HR role here
                 pass

            data = request.get_json()
            leave_id = data.get('leave_id')
            action = data.get('action') # 'Approve' or 'Reject'
            
            if not leave_id or action not in ['Approve', 'Reject']:
                return {"error": "Invalid request parameters"}, 400
                
            leave_request = LeaveRequest.query.get(leave_id)
            if not leave_request:
                return {"error": "Leave request not found"}, 404
                
            if leave_request.status != 'Pending':
                 return {"error": f"Leave request is already {leave_request.status}"}, 400

            if action == 'Approve':
                leave_request.status = 'Approved'
            else:
                leave_request.status = 'Rejected'
                
            leave_request.approved_by = user.employee.emp_id
            leave_request.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return {"message": f"Leave request {action}d successfully", "leave_request": leave_request.to_dict()}, 200
            
        except Exception as e:
            return {"error": str(e)}, 500

class EmployeeLeaveStatusResource(Resource):
    @jwt_required()
    def get(self):
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            if not user or not user.employee:
                return {"error": "Employee profile not found"}, 404
                
            # Fetch recent requests (limit to last 10 for example)
            requests = LeaveRequest.query.filter_by(emp_id=user.employee.emp_id).order_by(LeaveRequest.created_at.desc()).limit(10).all()
            
            return {"leave_requests": [req.to_dict() for req in requests]}, 200
        except Exception as e:
            return {"error": str(e)}, 500

class AddEmployeeResource(Resource):
    """Add a new employee from HR portal"""
    @jwt_required()
    def post(self):
        try:
            data = request.get_json()
            name = data.get('name')
            email = data.get('email')
            password = data.get('password')
            job_title = data.get('job_title')
            department_name = data.get('department')
            hire_date_str = data.get('hire_date')
            
            if not all([name, email, password, job_title, department_name, hire_date_str]):
                return {'error': 'All fields are required'}, 400
                
            # Check if user already exists
            if User.query.filter_by(email=email).first():
                return {'error': 'Email already registered'}, 400
                
            # Handle Department
            department = Department.query.filter_by(name=department_name).first()
            if not department:
                department = Department(name=department_name, description=f"{department_name} Department")
                db.session.add(department)
                db.session.commit() # Commit to get ID
            
            # Create User
            new_user = User(
                name=name,
                email=email,
                role='Employee',
                is_active=True
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit() # Commit to get ID
            
            # Parse hire date
            try:
                hire_date = datetime.strptime(hire_date_str, '%Y-%m-%d').date()
            except ValueError:
                return {'error': 'Invalid date format. Use YYYY-MM-DD'}, 400
            
            # Create Employee
            new_employee = Employee(
                user_id=new_user.user_id,
                dept_id=department.dept_id,
                job_title=job_title,
                hire_date=hire_date,
                salary=0.0, # Default
                skills="[]"
            )
            db.session.add(new_employee)
            db.session.commit()
            
            return {
                'message': 'Employee added successfully',
                'employee': new_employee.to_dict()
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500
