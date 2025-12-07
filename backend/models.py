"""
SQLAlchemy Models for HR Assistant Application
Defines all database tables and relationships
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

import json

class User(db.Model):
    """
    User model for authentication and authorization
    Supports multiple roles: Admin, HR Manager, Employee, Applicant, Manager, Executive
    """
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='Employee')  # Admin, HR Manager, Employee, Applicant, Manager, Executive
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = db.relationship('Employee', backref='user', uselist=False, cascade='all, delete-orphan')
    applicant = db.relationship('Applicant', backref='user', uselist=False, cascade='all, delete-orphan')
    ai_interactions = db.relationship('AIInteractionLog', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'emp_id': self.employee.emp_id if self.employee else None,
            'job_title': self.employee.job_title if self.employee else None
        }
    
    def __repr__(self):
        return f'<User {self.email} - {self.role}>'


class Department(db.Model):
    """Department model for organizational structure"""
    __tablename__ = 'departments'
    
    dept_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    employees = db.relationship('Employee', backref='department', lazy='dynamic')
    jobs = db.relationship('Job', backref='department', lazy='dynamic')
    
    def to_dict(self):
        """Convert department to dictionary"""
        return {
            'dept_id': self.dept_id,
            'name': self.name,
            'description': self.description,
            'employee_count': self.employees.count()
        }
    
    def __repr__(self):
        return f'<Department {self.name}>'


class Employee(db.Model):
    """Employee model with profile and skills"""
    __tablename__ = 'employees'
    
    emp_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False, unique=True)
    dept_id = db.Column(db.Integer, db.ForeignKey('departments.dept_id'))
    job_title = db.Column(db.String(100))
    salary = db.Column(db.Float)
    skills = db.Column(db.Text)  # JSON string of skills array
    hire_date = db.Column(db.Date)
    manager_id = db.Column(db.Integer, db.ForeignKey('employees.emp_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    leave_requests = db.relationship(
        'LeaveRequest',
        backref='employee',
        lazy='dynamic',
        cascade='all, delete-orphan',
        foreign_keys='LeaveRequest.emp_id'
    )

    approvals = db.relationship(
        'LeaveRequest',
        backref='approver',
        lazy='dynamic',
        foreign_keys='LeaveRequest.approved_by'
    )

    trainings = db.relationship(
        'EmployeeTraining',
        backref='employee',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    subordinates = db.relationship(
        'Employee',
        backref=db.backref('manager', remote_side=[emp_id])
    )
    
    def get_skills(self):
        """Parse skills from JSON string"""
        if self.skills:
            try:
                return json.loads(self.skills)
            except:
                return []
        return []
    
    def set_skills(self, skills_list):
        """Set skills as JSON string"""
        self.skills = json.dumps(skills_list)
    
    def to_dict(self):
        """Convert employee to dictionary"""
        return {
            'emp_id': self.emp_id,
            'user_id': self.user_id,
            'name': self.user.name if self.user else None,
            'email': self.user.email if self.user else None,
            'dept_id': self.dept_id,
            'department': self.department.name if self.department else None,
            'job_title': self.job_title,
            'salary': self.salary,
            'skills': self.get_skills(),
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'manager_id': self.manager_id
        }
    
    def __repr__(self):
        return f'<Employee {self.emp_id} - {self.job_title}>'


class Job(db.Model):
    """Job posting model for recruitment"""
    __tablename__ = 'jobs'
    
    job_id = db.Column(db.Integer, primary_key=True)
    dept_id = db.Column(db.Integer, db.ForeignKey('departments.dept_id'))
    title = db.Column(db.String(200), nullable=False)
    jd_text = db.Column(db.Text)  # Job description
    requirements = db.Column(db.Text)  # JSON string of requirements
    status = db.Column(db.String(50), default='Open')  # Open, Closed, On Hold
    location = db.Column(db.String(100))
    employment_type = db.Column(db.String(50))  # Full-time, Part-time, Contract
    salary_range = db.Column(db.String(100))
    input_data = db.Column(db.Text)  # JSON string of full input payload
    quantity = db.Column(db.Integer, default=1)
    posted_date = db.Column(db.DateTime, default=datetime.utcnow)
    closing_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    applicants = db.relationship('Applicant', backref='job', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_requirements(self):
        """Parse requirements from JSON string"""
        if self.requirements:
            try:
                return json.loads(self.requirements)
            except:
                return []
        return []
    
    def set_requirements(self, req_list):
        """Set requirements as JSON string"""
        self.requirements = json.dumps(req_list)
    
    def to_dict(self):
        """Convert job to dictionary"""
        return {
            'job_id': self.job_id,
            'dept_id': self.dept_id,
            'department': self.department.name if self.department else None,
            'title': self.title,
            'jd_text': self.jd_text,
            'requirements': self.get_requirements(),
            'status': self.status,
            'location': self.location,
            'employment_type': self.employment_type,
            'location': self.location,
            'employment_type': self.employment_type,
            'salary_range': self.salary_range,
            'quantity': self.quantity,
            'input_data': json.loads(self.input_data) if self.input_data else None,
            'posted_date': self.posted_date.isoformat() if self.posted_date else None,
            'closing_date': self.closing_date.isoformat() if self.closing_date else None,
            'applicant_count': self.applicants.count()
        }
    
    def __repr__(self):
        return f'<Job {self.title} - {self.status}>'


class Applicant(db.Model):
    """Applicant model for job applications"""
    __tablename__ = 'applicants'
    
    applicant_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.job_id'), nullable=False)
    status = db.Column(db.String(50), default='Applied')  # Applied, Screening, Interview, Rejected, Offered, Hired
    score = db.Column(db.Float, default=0.0)  # AI Suitability Score
    q_and_a_scores = db.Column(db.Text)  # JSON string of manual interview scores
    interview_questions = db.Column(db.Text)  # JSON string of generated questions
    feedback = db.Column(db.Text)
    applied_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    resume = db.relationship('Resume', backref='applicant', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert applicant to dictionary"""
        return {
            'applicant_id': self.applicant_id,
            'user_id': self.user_id,
            'name': self.user.name if self.user else None,
            'email': self.user.email if self.user else None,
            'job_id': self.job_id,
            'job_title': self.job.title if self.job else None,
            'status': self.status,
            'score': self.score,
            'feedback': self.feedback,
            'applied_date': self.applied_date.isoformat() if self.applied_date else None,
            'has_resume': self.resume is not None,
            'has_interview_questions': self.interview_questions is not None,
            'q_and_a_scores': json.loads(self.q_and_a_scores) if self.q_and_a_scores else []
        }
    
    def __repr__(self):
        return f'<Applicant {self.applicant_id} - {self.status}>'


class Resume(db.Model):
    """Resume model for storing and parsing applicant resumes"""
    __tablename__ = 'resumes'
    
    resume_id = db.Column(db.Integer, primary_key=True)
    applicant_id = db.Column(db.Integer, db.ForeignKey('applicants.applicant_id'), nullable=False, unique=True)
    file_url = db.Column(db.String(500))  # Path to uploaded file
    parsed_text = db.Column(db.Text)  # Full extracted text
    extracted_skills = db.Column(db.Text)  # JSON string of extracted skills
    extracted_experience = db.Column(db.Text)  # JSON string of experience details
    contact_info = db.Column(db.Text)  # JSON string of contact details
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_skills(self):
        """Parse skills from JSON string"""
        if self.extracted_skills:
            try:
                return json.loads(self.extracted_skills)
            except:
                return []
        return []
    
    def set_skills(self, skills_list):
        """Set skills as JSON string"""
        self.extracted_skills = json.dumps(skills_list)
    
    def get_experience(self):
        """Parse experience from JSON string"""
        if self.extracted_experience:
            try:
                return json.loads(self.extracted_experience)
            except:
                return {}
        return {}
    
    def set_experience(self, exp_dict):
        """Set experience as JSON string"""
        self.extracted_experience = json.dumps(exp_dict)
    
    def get_contact_info(self):
        """Parse contact info from JSON string"""
        if self.contact_info:
            try:
                return json.loads(self.contact_info)
            except:
                return {}
        return {}
    
    def set_contact_info(self, contact_dict):
        """Set contact info as JSON string"""
        self.contact_info = json.dumps(contact_dict)
    
    def to_dict(self):
        """Convert resume to dictionary"""
        return {
            'resume_id': self.resume_id,
            'applicant_id': self.applicant_id,
            'file_url': self.file_url,
            'extracted_skills': self.get_skills(),
            'extracted_experience': self.get_experience(),
            'contact_info': self.get_contact_info(),
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }
    
    def __repr__(self):
        return f'<Resume {self.resume_id} for Applicant {self.applicant_id}>'


class LeaveRequest(db.Model):
    """Leave request model for employee leave management"""
    __tablename__ = 'leave_requests'
    
    leave_id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.Integer, db.ForeignKey('employees.emp_id'), nullable=False)
    leave_type = db.Column(db.String(50))  # Sick, Vacation, Personal, etc.
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.Text)
    status = db.Column(db.String(50), default='Pending')  # Pending, Approved, Rejected
    number_of_days = db.Column(db.Float)
    approved_by = db.Column(db.Integer, db.ForeignKey('employees.emp_id'))
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert leave request to dictionary"""
        return {
            'leave_id': self.leave_id,
            'emp_id': self.emp_id,
            'employee_name': self.employee.user.name if self.employee and hasattr(self.employee, 'user') and self.employee.user else 'Unknown',
            'leave_type': self.leave_type,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'number_of_days': self.number_of_days,
            'reason': self.reason,
            'status': self.status,
            'approved_by': self.approved_by,
            'approver_name': self.approver.user.name if self.approver and hasattr(self.approver, 'user') and self.approver.user else None,
            'comments': self.comments,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<LeaveRequest {self.leave_id} - {self.status}>'


class Training(db.Model):
    """Training catalog model"""
    __tablename__ = 'trainings'
    
    training_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))  # Technical, Soft Skills, Leadership, etc.
    description = db.Column(db.Text)
    duration_hours = db.Column(db.Integer)
    instructor = db.Column(db.String(100))
    max_participants = db.Column(db.Integer)
    skills_covered = db.Column(db.Text)  # JSON string of skills
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    enrollments = db.relationship('EmployeeTraining', backref='training', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_skills_covered(self):
        """Parse skills from JSON string"""
        if self.skills_covered:
            try:
                return json.loads(self.skills_covered)
            except:
                return []
        return []
    
    def set_skills_covered(self, skills_list):
        """Set skills as JSON string"""
        self.skills_covered = json.dumps(skills_list)
    
    def to_dict(self):
        """Convert training to dictionary"""
        return {
            'training_id': self.training_id,
            'title': self.title,
            'category': self.category,
            'description': self.description,
            'duration_hours': self.duration_hours,
            'instructor': self.instructor,
            'max_participants': self.max_participants,
            'skills_covered': self.get_skills_covered(),
            'enrolled_count': self.enrollments.count()
        }
    
    def __repr__(self):
        return f'<Training {self.title}>'


class EmployeeTraining(db.Model):
    """Many-to-many relationship between Employee and Training"""
    __tablename__ = 'employee_trainings'
    
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.Integer, db.ForeignKey('employees.emp_id'), nullable=False)
    training_id = db.Column(db.Integer, db.ForeignKey('trainings.training_id'), nullable=False)
    status = db.Column(db.String(50), default='Enrolled')  # Enrolled, In Progress, Completed, Dropped
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)
    completion_date = db.Column(db.DateTime)
    score = db.Column(db.Float)
    certificate_url = db.Column(db.String(500))
    
    # Unique constraint to prevent duplicate enrollments
    __table_args__ = (db.UniqueConstraint('emp_id', 'training_id', name='unique_employee_training'),)
    
    def to_dict(self):
        """Convert employee training to dictionary"""
        return {
            'id': self.id,
            'emp_id': self.emp_id,
            'employee_name': self.employee.user.name if self.employee and self.employee.user else None,
            'training_id': self.training_id,
            'training_title': self.training.title if self.training else None,
            'status': self.status,
            'enrollment_date': self.enrollment_date.isoformat() if self.enrollment_date else None,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'score': self.score,
            'certificate_url': self.certificate_url
        }
    
    def __repr__(self):
        return f'<EmployeeTraining Emp:{self.emp_id} Training:{self.training_id}>'


class Policy(db.Model):
    """HR Policy documents for chatbot knowledge base"""
    __tablename__ = 'policies'
    
    policy_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))  # Leave, Benefits, Code of Conduct, etc.
    content = db.Column(db.Text, nullable=False)
    version = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert policy to dictionary"""
        return {
            'policy_id': self.policy_id,
            'title': self.title,
            'category': self.category,
            'content': self.content,
            'version': self.version,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Policy {self.title}>'


class AIInteractionLog(db.Model):
    """Log of all AI interactions for analytics and improvement"""
    __tablename__ = 'ai_interaction_logs'
    
    interaction_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    interaction_type = db.Column(db.String(50))  # chatbot, resume_parse, jd_generate, skill_recommend
    query = db.Column(db.Text)
    response = db.Column(db.Text)
    context = db.Column(db.Text)  # JSON string of additional context
    confidence_score = db.Column(db.Float)
    feedback_rating = db.Column(db.Integer)  # 1-5 rating from user
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def get_context(self):
        """Parse context from JSON string"""
        if self.context:
            try:
                return json.loads(self.context)
            except:
                return {}
        return {}
    
    def set_context(self, context_dict):
        """Set context as JSON string"""
        self.context = json.dumps(context_dict)
    
    def to_dict(self):
        """Convert AI interaction to dictionary"""
        return {
            'interaction_id': self.interaction_id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else None,
            'interaction_type': self.interaction_type,
            'query': self.query,
            'response': self.response,
            'context': self.get_context(),
            'confidence_score': self.confidence_score,
            'feedback_rating': self.feedback_rating,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    def __repr__(self):
        return f'<AIInteractionLog {self.interaction_id} - {self.interaction_type}>'


class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    sender = db.Column(db.String(50))  # 'user' or 'ai' or 'assistant'
    text = db.Column(db.Text)
    type = db.Column(db.String(50), default='text') # 'text', 'leave-form', 'leave-card'
    data = db.Column(db.Text) # JSON string for structured data
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "sender": self.sender,
            "text": self.text,
            "type": self.type,
            "data": json.loads(self.data) if self.data else None,
            "timestamp": self.timestamp.isoformat()
        }


class WellnessResource(db.Model):
    """Wellness resources for employees"""
    __tablename__ = 'wellness_resources'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    color = db.Column(db.String(50))
    action_label = db.Column(db.String(100))
    link = db.Column(db.String(500))
    resource_type = db.Column(db.String(50))  # 'employee' or 'hr'
    category = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'icon': self.icon,
            'color': self.color,
            'action_label': self.action_label,
            'link': self.link,
            'type': self.category,
            'category': self.category
        }


class WellnessEvent(db.Model):
    """Wellness events and workshops"""
    __tablename__ = 'wellness_events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    max_participants = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'date': self.date.strftime('%b %d, %Y at %I:%M %p') if self.date else None,
            'location': self.location,
            'max_participants': self.max_participants
        }


class WellnessSurvey(db.Model):
    """Wellness and engagement surveys"""
    __tablename__ = 'wellness_surveys'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    deadline = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), default='Active')  # Active, Closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'deadline': self.deadline.strftime('%b %d, %Y') if self.deadline else None,
            'status': self.status
        }


class EmployeeBirthday(db.Model):
    """Employee birthdays for tracking"""
    __tablename__ = 'employee_birthdays'
    
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.Integer, db.ForeignKey('employees.emp_id'), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    employee = db.relationship('Employee', backref='birthday_info')
    
    def to_dict(self):
        age = (datetime.utcnow().date() - self.birth_date).days // 365 if self.birth_date else None
        return {
            'id': self.id,
            'emp_id': self.emp_id,
            'name': self.employee.user.name if self.employee and self.employee.user else "Unknown",
            'age': age,
            'date': self.birth_date.strftime('%b %d, %Y') if self.birth_date else None
        }


class EmployeeLearningPath(db.Model):
    """Persisted learning path for employees"""
    __tablename__ = 'employee_learning_paths'
    
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.Integer, db.ForeignKey('employees.emp_id'), nullable=False)
    current_role = db.Column(db.String(100))
    career_goal = db.Column(db.String(100))
    path_data = db.Column(db.Text) # JSON string of the entire path including module status
    progress = db.Column(db.Float, default=1.0) # Using Float column but storing 1.0, 2.0 etc for backward compatibility or just logic change
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_path_data(self):
        if self.path_data:
            try:
                return json.loads(self.path_data)
            except:
                return {}
        return {}

    def set_path_data(self, data):
        self.path_data = json.dumps(data)

    def to_dict(self):
        return {
            'id': self.id,
            'emp_id': self.emp_id,
            'current_role': self.current_role,
            'career_goal': self.career_goal,
            'learning_path': self.get_path_data(),
            'progress': self.progress,
            'created_at': self.created_at.isoformat()
        }


class EmployeePerformance(db.Model):
    """
    Append-only log of employee performance scores.
    Used to calculate average performance.
    """
    __tablename__ = 'employee_performance'

    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.Integer, db.ForeignKey('employees.emp_id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(50), nullable=False) # 'Module', 'HR_Manual'
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'emp_id': self.emp_id,
            'score': self.score,
            'type': self.type,
            'comment': self.comment,
            'created_at': self.created_at.isoformat()
        }
