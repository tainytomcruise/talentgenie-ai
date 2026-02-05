"""
Main Flask Application - Modular Structure
AI-Powered HR Management System
"""
import os
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_restful import Api
from models import db
from datetime import timedelta

# Import auth routes
from routes.auth_routes import LoginResource, RegisterResource, CurrentUserResource

# Import analytics routes
from routes.analytics_routes import (
    AnalyticsSummary, AbsenteeismTrends, RetentionRisk,
    TrainingCompletion, DepartmentAnalytics, AnalyticsOverview,
    RecruitmentAnalytics, TrainingAnalytics
)

# Import recruitment routes
from routes.recruitment_routes import (
    ResumeUpload, ResumeParseAdvanced, CandidateJobMatcher,
    InterviewQuestionGenerator, GenerateJobPosting,
    GeneratePolicyDocument, PolicyLocations, WritingTones,
    JobListResource, PostJob, FinalizeJob, UpdateJobStatus,
    JobDetailResource, JobApplicants, PolicyList, SaveApplicantScores,
    HireRejectApplicantResource
)

# Import remaining routes from additional_routes
from routes.additional_routes import (
    AskHRChat, EmployeeDashboardSummary,
    EmpWellnessResources, EmpWellnessEvents, EmpWellnessRegister,
    HRWellnessResources, HRAbsenceAlerts, HRMilestones, HRAwards, HRBirthdays, HRSurveys,
    LearningPathGenerator, LearningProgress, ModuleCompletion, LearningRolesAndGoals,
    TrainingStatusUpdate, GetLearningPath, UpdateLearningPathModule,
    SentimentAnalyzer, SentimentTrend, SentimentThemes,
    WellnessResources, WellnessTips, WellnessEvents, WellnessEventRegistration,
    SkillRecommendations, TrendingSkills,
    GenerateReferenceLetterRoute, GenerateEmploymentProof,
    ChatHistoryResource, PerformanceLog, PerformanceSummary, CheckRatingEligibility,
    LeaveRequestResource, HRLeaveRequestsResource, LeaveRequestActionResource, EmployeeLeaveStatusResource,
    LogChatResource, AddEmployeeResource, TrainingListResource, AssignManagerTrainingResource
)

# Import employee routes
from routes.employee_routes import EmployeeListResource, PendingEmployeesResource, ApproveEmployeeResource, UpdatePersonalDetailsResource

# Initialize Flask app
app = Flask(__name__)
CORS(app)
api = Api(app)

# Configuration
database_url = os.environ.get("DATABASE_URL")

database_url = os.environ.get("DATABASE_URL")

if not database_url:
    raise ValueError("DATABASE_URL is not set. Check Render environment variables.")

# Fix Render format
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# # Fix for Render postgres:// vs postgresql://
# if database_url and database_url.startswith("postgres://"):
#     database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get("JWT_SECRET_KEY", "dev-secret-key")
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)  # 7 days expiration
app.config['UPLOAD_FOLDER'] = 'uploads'

# Initialize extensions
try:
    with app.app_context():
        db.create_all()
except Exception as e:
    print("Database initialization failed:", e)






# ==================== REGISTER ROUTES ====================


@app.route("/debug-user/<email>")
def debug_user(email):
    from models import User
    user = User.query.filter_by(email=email).first()

    if not user:
        return {"error": "User not found"}

    return {
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active
    }


# Authentication routes
api.add_resource(LoginResource, '/api/auth/login')
api.add_resource(RegisterResource, '/api/auth/register')
api.add_resource(CurrentUserResource, '/api/auth/me')

# Analytics routes
api.add_resource(AnalyticsSummary, '/api/analytics/summary')
api.add_resource(AbsenteeismTrends, '/api/analytics/absenteeism-trends')
api.add_resource(RetentionRisk, '/api/analytics/retention-risk')
api.add_resource(TrainingCompletion, '/api/analytics/training-completion')
api.add_resource(DepartmentAnalytics, '/api/analytics/departments')
api.add_resource(AnalyticsOverview, '/api/analytics/overview')
api.add_resource(RecruitmentAnalytics, '/api/analytics/recruitment')
api.add_resource(TrainingAnalytics, '/api/analytics/training')

# Recruitment routes
api.add_resource(ResumeUpload, '/api/recruitment/upload')
api.add_resource(ResumeParseAdvanced, '/api/recruitment/parse')
api.add_resource(CandidateJobMatcher, '/api/recruitment/match')
api.add_resource(InterviewQuestionGenerator, '/api/recruitment/questions')
api.add_resource(GenerateJobPosting, '/api/policy/generate/job')
api.add_resource(GeneratePolicyDocument, '/api/policy/generate/document')
api.add_resource(PolicyList, '/api/policies')
api.add_resource(PolicyLocations, '/api/policy/locations')
api.add_resource(WritingTones, '/api/policy/tones')
api.add_resource(JobListResource, '/api/jobs')
api.add_resource(JobDetailResource, '/api/jobs/<int:job_id>')
api.add_resource(PostJob, '/api/jobs/<int:job_id>/post')
api.add_resource(FinalizeJob, '/api/jobs/<int:job_id>/finalize')
api.add_resource(UpdateJobStatus, '/api/jobs/<int:job_id>/status')
api.add_resource(JobApplicants, '/api/jobs/<int:job_id>/applicants')
api.add_resource(SaveApplicantScores, '/api/applicants/<int:applicant_id>/scores')
api.add_resource(HireRejectApplicantResource, '/api/applicants/<int:applicant_id>/status')

# HR Chatbot
api.add_resource(AskHRChat, '/api/askhr/chat')
api.add_resource(ChatHistoryResource, '/api/chat/history')
api.add_resource(LogChatResource, '/api/chat/log')

# Employee Dashboard
api.add_resource(EmployeeDashboardSummary, '/api/employee/dashboard/summary/<int:emp_id>')

# Employee Wellness
api.add_resource(EmpWellnessResources, '/api/empwellness/resources')
api.add_resource(EmpWellnessEvents, '/api/empwellness/events')
api.add_resource(EmpWellnessRegister, '/api/empwellness/register')

# HR Wellness
api.add_resource(HRWellnessResources, '/api/hr/wellness/resources')
api.add_resource(HRAbsenceAlerts, '/api/hr/wellness/alerts')
api.add_resource(HRMilestones, '/api/hr/wellness/milestones')
api.add_resource(HRAwards, '/api/hr/wellness/awards')
api.add_resource(HRBirthdays, '/api/hr/wellness/birthdays')
api.add_resource(HRSurveys, '/api/hr/wellness/surveys')

# Learning routes
api.add_resource(LearningPathGenerator, '/api/learning/generate-path')
api.add_resource(LearningProgress, '/api/learning/progress/<int:employee_id>')
api.add_resource(ModuleCompletion, '/api/learning/module/complete')
api.add_resource(LearningRolesAndGoals, '/api/learning/roles-goals')
api.add_resource(TrainingStatusUpdate, '/api/learning/training/status')
api.add_resource(GetLearningPath, '/api/learning/paths/<int:employee_id>')
api.add_resource(UpdateLearningPathModule, '/api/learning/path/module')
api.add_resource(TrainingListResource, '/api/trainings')
api.add_resource(AssignManagerTrainingResource, '/api/employees/assign')

# Sentiment analysis routes
api.add_resource(SentimentAnalyzer, '/api/sentiment/analyze')
api.add_resource(SentimentTrend, '/api/sentiment/trend')
api.add_resource(SentimentThemes, '/api/sentiment/themes')

# Wellness routes
api.add_resource(WellnessResources, '/api/wellness/resources')
api.add_resource(WellnessTips, '/api/wellness/tips')
api.add_resource(WellnessEvents, '/api/wellness/events')
api.add_resource(WellnessEventRegistration, '/api/wellness/events/register')

# Skill recommendation routes
api.add_resource(SkillRecommendations, '/api/employee/ai_skill_recommendations')
api.add_resource(TrendingSkills, '/api/skills/trending')

# Document generation routes
api.add_resource(GenerateReferenceLetterRoute, '/api/employee/document_request/reference')
api.add_resource(GenerateEmploymentProof, '/api/employee/document_request/employment_proof')

# Performance routes
api.add_resource(PerformanceLog, '/api/performance/log')
api.add_resource(PerformanceSummary, '/api/performance/summary/<int:emp_id>')
api.add_resource(CheckRatingEligibility, '/api/performance/can-rate/<int:emp_id>')

# Employee Management routes
api.add_resource(EmployeeListResource, '/api/employees')
api.add_resource(AddEmployeeResource, '/api/employees/add')
api.add_resource(PendingEmployeesResource, '/api/employees/pending')
api.add_resource(ApproveEmployeeResource, '/api/employees/approve')
api.add_resource(UpdatePersonalDetailsResource, '/api/employee/personal-details')

# Leave Request routes
api.add_resource(LeaveRequestResource, '/api/leave/request')
api.add_resource(HRLeaveRequestsResource, '/api/hr/leave/requests')
api.add_resource(LeaveRequestActionResource, '/api/hr/leave/action')
api.add_resource(EmployeeLeaveStatusResource, '/api/employee/leave/status')

# Serve uploaded files
from flask import send_from_directory


@app.route('/api/uploads/<path:filename>')
def serve_uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ==================== RUN APPLICATION ====================

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get("RENDER") is None)